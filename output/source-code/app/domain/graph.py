from dataclasses import dataclass, field
from enum import Enum

Position = tuple[int, int]


class NodeKind(str, Enum):
    ROAD = "road"
    WALL = "wall"
    DEPOT = "depot"
    TARGET = "target"


@dataclass
class GraphNode:
    position: Position
    kind: NodeKind = NodeKind.ROAD
    label: str | None = None

    @property
    def walkable(self):
        return self.kind is not NodeKind.WALL


@dataclass
class GraphMap:
    width: int
    height: int
    name: str
    nodes: dict[Position, GraphNode] = field(default_factory=dict)
    adjacency: dict[Position, dict[Position, float]] = field(default_factory=dict)

    def add_node(self, node):
        self.nodes[node.position] = node
        self.adjacency.setdefault(node.position, {})

    def add_undirected_edge(self, a, b, cost=1.0):
        if self.nodes[a].walkable and self.nodes[b].walkable:
            self.adjacency[a][b] = cost
            self.adjacency[b][a] = cost

    def node_at(self, p):
        return self.nodes[p]

    def in_bounds(self, p):
        x, y = p
        return 0 <= x < self.width and 0 <= y < self.height

    def neighbors(self, p):
        return self.adjacency.get(p, {})

    def positions_of_kind(self, k):
        return [p for p, n in self.nodes.items() if n.kind is k]

    def walkable_positions(self):
        return [p for p, n in self.nodes.items() if n.walkable]

    def rebuild_edges(self):
        self.adjacency = {p: {} for p in self.nodes}
        for y in range(self.height):
            for x in range(self.width):
                a = (x, y)
                if not self.nodes[a].walkable:
                    continue
                for b in ((x + 1, y), (x, y + 1)):
                    if b in self.nodes and self.nodes[b].walkable:
                        self.add_undirected_edge(a, b)

    def reachable_from(self, start):
        if start not in self.nodes or not self.nodes[start].walkable:
            return set()
        seen = {start}
        stack = [start]
        while stack:
            for n in self.neighbors(stack.pop()):
                if n not in seen:
                    seen.add(n)
                    stack.append(n)
        return seen
