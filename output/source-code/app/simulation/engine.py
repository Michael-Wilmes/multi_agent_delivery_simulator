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
                self.mark_stranded(a)
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
            next_position = self.r.choice(possible)
            occupied.discard(previous_position)
            battery_empty = agent.move_to(
                next_position,
                self.config.simulation.battery_enabled,
            )
            occupied.add(agent.position)
            reserved.add(agent.position)

            if battery_empty:
                self.mark_stranded(agent)
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

    def start_charging(self, agent):
        """Starts a configured charging phase without charging in this tick."""
        agent.status = LOADING
        agent.charging_ticks_remaining = max(1, self.config.battery.chargingDurationTicks)
        agent.current_action = CHARGE

    def mark_stranded(self, agent):
        """Freezes an agent with an empty battery and leaves it as an obstacle."""
        if agent.status == STRANDED:
            return
        agent.battery = 0.0
        agent.status = STRANDED
        agent.current_action = STRANDED
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

        if agent.load >= agent.capacity:
            self.messages.append(f'Agent {agent.id}: Kapazität erreicht')
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

        agent.load += 1
        agent.mark_task_in_transit(task)
        task.depot.remove_task(task)
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

        agent.load -= 1
        agent.mark_task_delivered(task)
        self.messages.append(f'Agent {agent.id}: T-{task.id:03d} abgeliefert')

    def toggle_running(self):
        if not self.running and self.agents and all(agent.status == STRANDED for agent in self.agents):
            self.messages.append('Simulation kann nicht gestartet werden: Alle Agenten sind gestrandet')
            return
        self.running = not self.running

    def mark_no_bid(self, task_id):
        """Closes a task that received no bid by its deadline and drops it from the open queue."""
        task = next((task for task in self.tasks if task.id == task_id), None)
        if task is None:
            return
        task.status = NO_BID
        task.depot.remove_task(task)
        self.messages.append(f'T-{task.id:03d}: Kein Gebot erhalten, Auftrag geschlossen')

    def snapshot(self):
        return SimulationSnapshot(
            self.tick,
            self.graph,
            tuple(self.agents),
            tuple(self.tasks),
            tuple(self.messages[-20:]),
            self.contract_net_manager.recent_events(),
            tuple(self.package_creation_kpi),
            self.running,
        )
