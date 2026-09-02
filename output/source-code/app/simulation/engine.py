import random
from dataclasses import dataclass

from app.domain.agent import Agent, AgentType
from app.domain.deliverytask import DeliveryTask
from app.domain.graph import NodeKind
from app.maps.factory import create_graph_map


@dataclass(frozen=True)
class SimulationSnapshot:
    tick: int
    graph: object
    agents: tuple
    tasks: tuple
    messages: tuple
    contract_log: tuple
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
        self.messages = [f'Karte geladen: {self.graph.name}']
        self.contract_log = []
        self._next_agent_id = 1
        self._next_task_id = 1

        for _ in range(self.config.simulation.initial_standard_agents):
            self.add_agent(AgentType.STANDARD)
        for _ in range(self.config.simulation.initial_express_agents):
            self.add_agent(AgentType.EXPRESS)

    def free_road_positions(self):
        occupied = {a.position for a in self.agents}
        return [
            p for p, n in self.graph.nodes.items()
            if n.kind is NodeKind.ROAD and p not in occupied
        ]

    def add_agent(self, t):
        free = self.free_road_positions()
        if not free:
            self.messages.append('Kein freies Strassenfeld')
            return False

        speed, capacity = (1, 3) if t is AgentType.STANDARD else (2, 2)
        a = Agent(self._next_agent_id, t, self.r.choice(free), speed, capacity)
        self._next_agent_id += 1
        self.agents.append(a)
        self.messages.append(f'Agent {a.id} ({a.type.value}) bei {a.position}')
        return True

    def add_task(self):
        ds = self.graph.positions_of_kind(NodeKind.DEPOT)
        zs = self.graph.positions_of_kind(NodeKind.TARGET)
        if not ds or not zs:
            self.messages.append('Task nicht moeglich')
            return False

        t = DeliveryTask(self._next_task_id, self.r.choice(ds), self.r.choice(zs), self.tick)
        self._next_task_id += 1
        self.tasks.append(t)
        self.messages.append(f'T-{t.id:03d} erzeugt: {t.depot} -> {t.destination}')
        self.contract_log.append(
            (self.tick, 'CREATED', 'Depot -> Agenten', f'T-{t.id:03d}; Contract-Net folgt in Aufgabe 2')
        )
        return True

    def step(self):
        self.tick += 1
        occupied = {a.position for a in self.agents}
        reserved = set()
        order = list(self.agents)
        self.r.shuffle(order)

        for a in order:
            possible = [
                p for p in self.graph.neighbors(a.position)
                if p not in occupied and p not in reserved
            ]
            if possible:
                occupied.discard(a.position)
                a.position = self.r.choice(possible)
                occupied.add(a.position)
                reserved.add(a.position)

        self.messages.append(f'Tick {self.tick} ausgefuehrt')

    def toggle_running(self):
        self.running = not self.running

    def snapshot(self):
        return SimulationSnapshot(
            self.tick,
            self.graph,
            tuple(self.agents),
            tuple(self.tasks),
            tuple(self.messages[-20:]),
            tuple(self.contract_log[-20:]),
            self.running,
        )
