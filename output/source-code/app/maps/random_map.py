import random

from app.domain.graph import GraphMap, GraphNode, NodeKind


class RandomGraphMapFactory:
    def __init__(self, seed=None):
        self.r = random.Random(seed)

    def create(self, width=20, height=20, wall_density=0.20, depot_count=2, target_count=4):
        g = GraphMap(width, height, "Zufallskarte")

        for y in range(height):
            for x in range(width):
                g.add_node(GraphNode((x, y)))

        desired = int(width * height * wall_density)
        walls = set()
        attempts = 0

        while len(walls) < desired and attempts < desired * 25:
            attempts += 1
            horizontal = self.r.choice([True, False])
            length = self.r.randint(2, min(6, width - 2, height - 2))
            x = self.r.randint(1, width - 2)
            y = self.r.randint(1, height - 2)

            segment = {
                (x + i, y) if horizontal else (x, y + i)
                for i in range(length)
                if 0 < (x + i if horizontal else x) < width - 1
                and 0 < (y if horizontal else y + i) < height - 1
            }
            previous = set(walls)
            walls |= segment

            for n in g.nodes.values():
                n.kind = NodeKind.ROAD
                n.label = None
            for p in walls:
                g.nodes[p].kind = NodeKind.WALL
            g.rebuild_edges()
            roads = g.walkable_positions()
            if not roads or len(g.reachable_from(roads[0])) != len(roads):
                walls = previous

        for n in g.nodes.values():
            n.kind = NodeKind.ROAD
            n.label = None
        for p in walls:
            g.nodes[p].kind = NodeKind.WALL

        g.rebuild_edges()
        free = g.walkable_positions()
        chosen = self.r.sample(free, depot_count + target_count)

        for i, p in enumerate(chosen[:depot_count]):
            g.nodes[p].kind = NodeKind.DEPOT
            g.nodes[p].label = f"D{i}"
        for i, p in enumerate(chosen[depot_count:]):
            g.nodes[p].kind = NodeKind.TARGET
            g.nodes[p].label = f"Z{i}"

        g.rebuild_edges()
        return g
