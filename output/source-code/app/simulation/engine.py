import random
from dataclasses import dataclass
from pathlib import Path

from app.domain.entities.agent import Agent, AgentType
from app.domain.entities.contractnetmessage import MessageType
from app.domain.services.contractnetmanager import ContractNetManager
from app.domain.entities.deliverytask import DeliveryTask
from app.domain.entities.graph import NodeKind
from app.shared.constants import AWAIT_PICKUP, CHARGE, DELIVER, IDLE, IN_TRANSIT, LOAD_DELIVERY, LOADING, MOVE, NO_BID, OPEN, PICKUP, STRANDED, SUBMIT_BID
from app.maps.factory import create_graph_map
from app.config import validate_map_size, validate_depot_count
from app.simulation.kpi_recorder import KpiRecorder


@dataclass(frozen=True)
class SimulationSnapshot:
    tick: int
    graph: object
    agents: tuple
    tasks: tuple
    messages: tuple
    contract_log: tuple
    package_creation_kpi: tuple
    running: bool


class SimulationEngine:
    def __init__(self, config):
        self.config = config
        self.r = random.Random()
        self.reset()

    def reset(self):
        self.graph = create_graph_map(self.config.map)
        validate_map_size(self.graph.width, self.graph.height)
        validate_depot_count(len(self.graph.depots))
        self.tick = 0
        self.running = False
        self.agents = []
        self.tasks = []
        self.messages = [f'Karte geladen: {self.graph.name}'] #todo: use from a centralized place
        self.contract_net_manager = ContractNetManager()
        for depot in self.graph.depots:
            depot.connect_contract_net_manager(self.contract_net_manager)
        self._next_agent_id = 1
        self._next_task_id = 1
        self.package_creation_kpi = []
        self.kpi_directory = Path(__file__).resolve().parents[2] / 'kpis'
        self.kpi_recorder = KpiRecorder(self.kpi_directory)
        self._all_stranded_message_sent = False
        self._logged_contract_events = 0

        for _ in range(self.config.simulation.initial_standard_agents):
            self.add_agent(AgentType.STANDARD)
        for _ in range(self.config.simulation.initial_express_agents):
            self.add_agent(AgentType.EXPRESS)

    def free_road_positions(self):
        occupied = {a.position for a in self.agents}
        return [
            p for p, n in self.graph.nodes.items()
            if n.kind is NodeKind.ROAD
            and self.graph.neighbors(p)
            and p not in occupied
        ]

    def add_agent(self, t):
        free = self.free_road_positions()
        if not free:
            self.messages.append('Kein freies Strassenfeld')# todo: use from a centralized place
            return False

        type_config = (
            self.config.agentTypes.standard
            if t is AgentType.STANDARD
            else self.config.agentTypes.express
        )
        a = Agent(
            self._next_agent_id,
            t,
            self.r.choice(free),
            type_config.speed,
            type_config.capacity,
            type_config.taskCapacity,
            battery=float(type_config.batteryCapacity),
            battery_cost_per_field=type_config.batteryCostPerField,
        )
        self._next_agent_id += 1
        self.agents.append(a)
        self.contract_net_manager.register_agent(a)
        self.messages.append(f'Agent {a.id} ({a.type.value}) bei {a.position}')
        return True

    def add_task(self):
        depots = self.graph.depots
        destinations = self.graph.destinations
        if not depots or not destinations:
            self.messages.append('Task nicht moeglich') #todo: use from a centralized place
            return False

        depot = self.r.choice(depots)
        destination = self.r.choice(destinations)
        t = DeliveryTask(self._next_task_id, depot, destination, self.tick)
        deadline = self.tick + self.r.randint(2, 10)
        self._next_task_id += 1
        self.tasks.append(t)
        depot.add_task(t)
        self.package_creation_kpi.append((self.tick, depot.id, t.id))
        self.kpi_recorder.record_task_created(self.tick, depot.id, t.id)
        self.messages.append(
            f'Depot D{depot.id + 1} erzeugt T-{t.id:03d} bei Tick {self.tick}: '
            f'{t.depot.position} -> {t.destination.position}, Deadline: Tick {deadline}'
        ) #todo: use from a centralized place
        for event in depot.submit_task(t, self.tick, deadline):
            self.kpi_recorder.record_contract_event(event)
        self._flush_contract_log()
        return True

    def step(self):
        if self.all_agents_stranded():
            self.stop_if_all_agents_stranded()
            return

        self.tick += 1
        occupied = {a.position for a in self.agents}
        reserved = set()
        order = list(self.agents)
        self.r.shuffle(order)

        for a in order:
            if a.status == STRANDED:
                a.current_action = STRANDED
                continue

            # Bieten ist ein Kommunikationsschritt: jeder Agent gibt es unabhaengig
            # von seiner physischen Aktion im selben Tick ab, nicht nacheinander.
            self.submit_pending_bids(a)

            if a.status == LOADING:
                if a.charging_ticks_remaining > 1:
                    a.charging_ticks_remaining -= 1
                    a.current_action = CHARGE
                    continue

                battery_config = (
                    self.config.agentTypes.standard
                    if a.type is AgentType.STANDARD
                    else self.config.agentTypes.express
                )
                a.battery = float(battery_config.batteryCapacity)
                a.charging_ticks_remaining = 0
                a.status = IDLE
                a.current_action = CHARGE
                continue

            if self.config.simulation.battery_enabled and a.battery <= 0:
                if self.graph.node_at(a.position).kind is not NodeKind.DEPOT:
                    a.mark_stranded()
                continue

            if self.graph.node_at(a.position).kind is NodeKind.DEPOT:
                battery_config = (
                    self.config.agentTypes.standard
                    if a.type is AgentType.STANDARD
                    else self.config.agentTypes.express
                )
                if a.load < a.capacity and any(
                    self._task_available_for_agent(task, a)
                    for task in self.tasks
                ):
                    self.pick_up_task(a)
                    a.status = LOADING
                    a.current_action = LOAD_DELIVERY
                    continue
                if a.battery < battery_config.batteryCapacity:
                    self.start_charging(a)
                    continue

            # Meilenstein 1: In Meilenstein 2 durch die geplante Agentenaktion ersetzen.
            action = self.choose_random_action(a)
            self.execute_action(a, action, occupied, reserved)

        if self.tick % 5 == 0:
            self.add_task()

        for outcome in self.contract_net_manager.award_ready_tasks(self.tasks, self.tick):
            if outcome.type is MessageType.NO_BID:
                self.mark_no_bid(outcome.task_id)
            self.kpi_recorder.record_contract_event(outcome)
        self.kpi_recorder.record_simulation_tick(
            self.tick,
            self.agents,
            self.tasks,
            self.package_creation_kpi,
        )
        self.stop_if_all_agents_stranded()
        self.messages.append(f'Tick {self.tick} ausgeführt') #todo: use from a centralized place
        self._flush_contract_log()

    def choose_random_action(self, agent):
        """Selects a random action for the initial simulation milestone.

        This method is the replaceable action-selection policy. The action methods
        themselves remain part of the simulation after random selection is removed.
        """
        if agent.status == STRANDED:
            return STRANDED

        node_kind = self.graph.node_at(agent.position).kind
        if node_kind is NodeKind.DEPOT and agent.load < agent.capacity and any(
            self._task_available_for_agent(task, agent)
            for task in self.tasks
        ):
            return PICKUP
        if node_kind is NodeKind.TARGET and any(
            task.status == IN_TRANSIT
            and task.assigned_agent_id == agent.id
            and task.destination.position == agent.position
            for task in self.tasks
        ):
            return DELIVER
        return MOVE

    def execute_action(self, agent, action, occupied, reserved):
        """Executes an action selected for an agent during the current tick."""
        if agent.status == STRANDED:
            agent.current_action = STRANDED
            return

        if action == DELIVER and self.graph.node_at(agent.position).kind is not NodeKind.TARGET:
            return

        agent.current_action = action
        if action == MOVE:
            if agent.status == LOADING:
                return
            self.move_agent(agent, occupied, reserved)
        elif action == PICKUP:
            self.pick_up_task(agent)
        elif action == DELIVER:
            self.deliver_task(agent)

    def submit_pending_bids(self, agent):
        """Submits bids for every notified, still-open task the agent hasn't bid on yet.

        Runs for every agent every tick so all eligible agents can bid on the same
        tick an announcement arrives, instead of one agent per tick in turn.
        """
        pending_tasks = [
            task for task in self.tasks
            if any(
                notification.type is MessageType.ANNOUNCE
                and notification.task_id == task.id
                for notification in agent.notifications
            )
            and task.status == OPEN
            and not self.contract_net_manager.has_bid(task.id, agent.id)
            and any(delivery.task.id == task.id for delivery in agent.deliveries)
        ]
        for task in pending_tasks:
            delivery = next(
                delivery for delivery in agent.deliveries
                if delivery.task.id == task.id
            )
            bid = self.contract_net_manager.record_bid(
                agent.id,
                task.id,
                delivery.cost,
                self.tick,
            )
            self.kpi_recorder.record_contract_event(bid)
            self.messages.append(
                f'Agent {agent.id}: Gebot für T-{task.id:03d} abgegeben ({delivery.cost:.1f})'
            )

    def move_agent(self, agent, occupied, reserved):
        if agent.status == STRANDED:
            return

        assigned_task = next(
            (
                task for task in self.tasks
                if task.assigned_agent_id == agent.id
                and task.status in {AWAIT_PICKUP, IN_TRANSIT}
            ),
            None,
        )
        target = None
        distances = {}
        if assigned_task is not None:
            target = (
                assigned_task.depot.position
                if assigned_task.status == AWAIT_PICKUP
                else assigned_task.destination.position
            )
            distances = self._distances_from(target)

        for _ in range(agent.speed):
            possible = [
                p for p in self.graph.neighbors(agent.position)
                if (
                    self.graph.in_bounds(p)
                    and p not in occupied
                    and p not in reserved
                    and (
                        self.graph.node_at(p).kind is not NodeKind.TARGET
                        or any(
                            task.status == IN_TRANSIT
                            and task.assigned_agent_id == agent.id
                            and task.destination.position == p
                            for task in self.tasks
                        )
                    )
                )
            ]
            if not possible:
                break

            previous_position = agent.position
            route_steps = [p for p in possible if p in distances]
            if target is not None and route_steps:
                best_distance = min(distances[p] for p in route_steps)
                next_position = self.r.choice(
                    [p for p in route_steps if distances[p] == best_distance]
                )
            else:
                next_position = self.r.choice(possible)
            occupied.discard(previous_position)
            battery_empty = agent.move_to(
                next_position,
                self.config.simulation.battery_enabled,
            )
            occupied.add(agent.position)
            reserved.add(agent.position)

            if battery_empty:
                if self.graph.node_at(agent.position).kind is not NodeKind.DEPOT:
                    agent.mark_stranded()
                break

            if self.graph.node_at(agent.position).kind is NodeKind.DEPOT:
                if agent.load < agent.capacity and any(
                    self._task_available_for_agent(task, agent)
                    for task in self.tasks
                ):
                    self.pick_up_task(agent)
                    agent.status = LOADING
                    agent.current_action = LOAD_DELIVERY
                else:
                    self.start_charging(agent)
                break

            if self.graph.node_at(agent.position).kind is NodeKind.TARGET:
                break

    def _distances_from(self, target):
        if target not in self.graph.nodes or not self.graph.node_at(target).walkable:
            return {}

        distances = {target: 0}
        positions = [target]
        for position in positions:
            for neighbor in self.graph.neighbors(position):
                if neighbor not in distances:
                    distances[neighbor] = distances[position] + 1
                    positions.append(neighbor)
        return distances

    def start_charging(self, agent):
        """Starts a configured charging phase without charging in this tick."""
        agent.status = LOADING
        agent.charging_ticks_remaining = max(1, self.config.battery.chargingDurationTicks)
        agent.current_action = CHARGE

    def mark_stranded(self, agent):
        """Compatibility wrapper: an agent itself owns the stranded transition."""
        agent.mark_stranded()
        self.messages.append(f'Agent {agent.id}: Batterie leer, Agent gestrandet')

    def all_agents_stranded(self):
        return bool(self.agents) and all(agent.status == STRANDED for agent in self.agents)

    def stop_if_all_agents_stranded(self):
        if self.all_agents_stranded() and not self._all_stranded_message_sent:
            self.running = False
            self.messages.append('Stopped. Agents out of battery')
            self._all_stranded_message_sent = True

    def pick_up_task(self, agent):
        if self.graph.node_at(agent.position).kind is not NodeKind.DEPOT:
            self.messages.append(f'Agent {agent.id}: Kein Depot an dieser Position')
            return

        task = next(
            (
                task for task in self.tasks
                if self._task_available_for_agent(task, agent)
            ),
            None,
        )
        if task is None:
            self.messages.append(f'Agent {agent.id}: Kein Paket am Depot')
            return

        if not agent.pick_task(task):
            self.messages.append(f'Agent {agent.id}: Kapazität erreicht')
            return

        if not self.contract_net_manager.start_task_for_agent(agent, task, self.tick):
            self.messages.append(f'Agent {agent.id}: Aufgabe konnte nicht gestartet werden')
            return

        self.messages.append(f'Agent {agent.id}: T-{task.id:03d} aufgenommen')

    def _task_available_for_agent(self, task, agent):
        return (
            task.depot.position == agent.position
            and task.status == AWAIT_PICKUP
            and task.assigned_agent_id == agent.id
        )

    def deliver_task(self, agent):
        if self.graph.node_at(agent.position).kind is not NodeKind.TARGET:
            self.messages.append(f'Agent {agent.id}: Kein Ziel an dieser Position')
            return

        task = next(
            (
                task for task in self.tasks
                if task.status == IN_TRANSIT
                and task.assigned_agent_id == agent.id
                and task.destination.position == agent.position
            ),
            None,
        )
        if task is None:
            self.messages.append(f'Agent {agent.id}: Keine Zustellung möglich')
            return

        if not agent.deliver_task(task):
            self.messages.append(f'Agent {agent.id}: Zustellung konnte nicht abgeschlossen werden')
            return

        if not self.contract_net_manager.deliver_task_for_agent(agent, task, self.tick):
            self.messages.append(f'Agent {agent.id}: Zustellung konnte nicht abgeschlossen werden')
            return

        self.messages.append(f'Agent {agent.id}: T-{task.id:03d} abgeliefert')

    def toggle_running(self):
        if not self.running and self.agents and all(agent.status == STRANDED for agent in self.agents):
            self.messages.append('Simulation kann nicht gestartet werden: Alle Agenten sind gestrandet')
            return
        self.running = not self.running

    def mark_no_bid(self, task_id):
        """Closes a task that received no bid by its deadline without deleting its lifecycle record."""
        task = next((task for task in self.tasks if task.id == task_id), None)
        if task is None:
            return
        self.contract_net_manager.close_task(task, NO_BID, self.tick)
        self.messages.append(f'T-{task.id:03d}: Kein Gebot erhalten, Auftrag geschlossen')

    def _flush_contract_log(self):
        """Writes every contract-net event not yet logged, mirroring the UI's contract-net log 1:1."""
        events = self.contract_net_manager.events
        for event in events[self._logged_contract_events:]:
            self.kpi_recorder.record_contract_log(event)
        self._logged_contract_events = len(events)

    def snapshot(self):
        return SimulationSnapshot(
            self.tick,
            self.graph,
            tuple(self.agents),
            tuple(self.tasks),
            tuple(self.messages[-20:]),
            tuple(self.contract_net_manager.events),
            tuple(self.package_creation_kpi),
            self.running,
        )
