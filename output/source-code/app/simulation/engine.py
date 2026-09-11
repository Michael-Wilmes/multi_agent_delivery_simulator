import random
import csv
from dataclasses import dataclass
from pathlib import Path

from app.domain.agent import Agent, AgentType
from app.domain.contractnetmanager import ContractNetManager
from app.domain.deliverytask import DeliveryTask
from app.domain.graph import NodeKind
from app.shared.constants import CHARGE, DELIVER, IDLE, LOAD_DELIVERY, LOADING, MOVE, PICKUP, SEND_MESSAGE, STRANDED
from app.maps.factory import create_graph_map


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
        self.tick = 0
        self.running = False
        self.agents = []
        self.tasks = []
        self.messages = [f'Karte geladen: {self.graph.name}'] #todo: use from a centralized place
        self.contract_net_manager = ContractNetManager()
        self._next_agent_id = 1
        self._next_task_id = 1
        self.package_creation_kpi = []
        self.kpi_directory = Path(__file__).resolve().parents[2] / 'kpis'
        self.package_creation_kpi_file = self.kpi_directory / 'package_creation.csv'
        self.simulation_kpi_file = self.kpi_directory / 'simulation.csv'
        self._initialize_kpi_files()
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
            battery=float(type_config.batteryCapacity),
            battery_cost_per_field=type_config.batteryCostPerField,
        )
        self._next_agent_id += 1
        self.agents.append(a)
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
        self._next_task_id += 1
        self.tasks.append(t)
        self.package_creation_kpi.append((self.tick, depot.id, t.id))
        self._store_package_creation_kpi(self.tick, depot.id, t.id)
        self.messages.append(
            f'Depot D{depot.id + 1} erzeugt T-{t.id:03d} bei Tick {self.tick}: '
            f'{t.depot.position} -> {t.destination.position}'
        ) #todo: use from a centralized place
        self.contract_net_manager.announce_task(t, self.tick)
        return True

    def _initialize_kpi_files(self):
        self.kpi_directory.mkdir(parents=True, exist_ok=True)
        with self.package_creation_kpi_file.open('w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(('tick', 'depot_id', 'task_id'))
        with self.simulation_kpi_file.open('w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow((
                'tick',
                'total_agents',
                'active_agents',
                'stranded_agents',
                'total_tasks',
                'open_tasks',
                'in_transit_tasks',
                'delivered_tasks',
                'total_load',
                'packages_created',
            ))

    def _store_package_creation_kpi(self, tick, depot_id, task_id):
        with self.package_creation_kpi_file.open('a', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow((tick, depot_id, task_id))

    def _store_simulation_kpi(self):
        task_counts = {
            status: sum(task.status == status for task in self.tasks)
            for status in ('open', 'in_transit', 'delivered')
        }
        stranded_agents = sum(agent.status == STRANDED for agent in self.agents)
        created_this_tick = sum(event[0] == self.tick for event in self.package_creation_kpi)
        row = (
            self.tick,
            len(self.agents),
            len(self.agents) - stranded_agents,
            stranded_agents,
            len(self.tasks),
            task_counts['open'],
            task_counts['in_transit'],
            task_counts['delivered'],
            sum(agent.load for agent in self.agents),
            created_this_tick,
        )
        with self.simulation_kpi_file.open('a', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow(row)

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
                    task.status == 'open' and task.depot.position == a.position
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

        self._store_simulation_kpi()
        self.stop_if_all_agents_stranded()
        self.messages.append(f'Tick {self.tick} ausgeführt') #todo: use from a centralized place

    def choose_random_action(self, agent):
        """Selects a random action for the initial simulation milestone.

        This method is the replaceable action-selection policy. The action methods
        themselves remain part of the simulation after random selection is removed.
        """
        node_kind = self.graph.node_at(agent.position).kind
        if node_kind is NodeKind.DEPOT and agent.load < agent.capacity and any(
            task.status == 'open' and task.depot.position == agent.position
            for task in self.tasks
        ):
            return PICKUP
        if node_kind is NodeKind.TARGET and any(
            task.status == 'in_transit'
            and task.assigned_agent_id == agent.id
            and task.destination.position == agent.position
            for task in self.tasks
        ):
            return DELIVER
        return self.r.choice((MOVE, SEND_MESSAGE))

    def execute_action(self, agent, action, occupied, reserved):
        """Executes an action selected for an agent during the current tick."""
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
        elif action == SEND_MESSAGE:
            self.send_message(agent)

    def send_message(self, agent):
        """Records an agent message; its routing can be extended in milestone 2."""
        self.messages.append(f'Agent {agent.id}: Nachricht gesendet')

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
                            task.status == 'in_transit'
                            and task.assigned_agent_id == agent.id
                            and task.destination.position == p
                            for task in self.tasks
                        )
                    )
                )
            ]
            if not possible:
                break

            occupied.discard(agent.position)
            agent.position = self.r.choice(possible)
            occupied.add(agent.position)
            reserved.add(agent.position)

            if self.config.simulation.battery_enabled:
                agent.battery = max(0.0, agent.battery - agent.battery_cost_per_field)
                if agent.battery <= 0:
                    self.mark_stranded(agent)
                    break

            if self.graph.node_at(agent.position).kind is NodeKind.DEPOT:
                if agent.load < agent.capacity and any(
                    task.status == 'open' and task.depot.position == agent.position
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
        """Stops an agent with an empty battery and leaves it as an obstacle."""
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
            self.messages.append('Keine Bewegungen mehr möglich')
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
                if task.status == 'open' and task.depot.position == agent.position
            ),
            None,
        )
        if task is None:
            self.messages.append(f'Agent {agent.id}: Kein Paket am Depot')
            return

        agent.load += 1
        task.status = 'in_transit'
        task.assigned_agent_id = agent.id
        self.messages.append(f'Agent {agent.id}: T-{task.id:03d} aufgenommen')

    def deliver_task(self, agent):
        if self.graph.node_at(agent.position).kind is not NodeKind.TARGET:
            self.messages.append(f'Agent {agent.id}: Kein Ziel an dieser Position')
            return

        task = next(
            (
                task for task in self.tasks
                if task.status == 'in_transit'
                and task.assigned_agent_id == agent.id
                and task.destination.position == agent.position
            ),
            None,
        )
        if task is None:
            self.messages.append(f'Agent {agent.id}: Keine Zustellung möglich')
            return

        agent.load -= 1
        task.status = 'delivered'
        self.messages.append(f'Agent {agent.id}: T-{task.id:03d} abgeliefert')

    def toggle_running(self):
        if not self.running and self.agents and all(agent.status == STRANDED for agent in self.agents):
            self.messages.append('Simulation kann nicht gestartet werden: Alle Agenten sind gestrandet')
            return
        self.running = not self.running

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
