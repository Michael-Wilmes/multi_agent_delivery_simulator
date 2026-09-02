from app.domain.graph import GraphMap, GraphNode, NodeKind

MAP_1 = [
    '...###..Z.',
    'D..#Z#.##.',
    '.#.#.#.....',
    '.#....##..',
    '.####.....',
    '....#.##..',
    '.##.#....Z',
    '.#...#.##.',
    '...#.#....',
    '.Z.#...#D.',
]

MAP_2 = [
    '.Z.###....',
    'D..#.#.#Z.',
    '.#. #.#.#..',
    '.#.....#..',
    '.#####.#..',
    '.....#.#..',
    '.###.#....',
    '.#Z#.###..',
    '...#.....D',
    '....Z.##..',
]


def graph_from_ascii(lines, name):
    g = GraphMap(len(lines[0]), len(lines), name)
    kinds = {
        ' ': NodeKind.ROAD,
        '.': NodeKind.ROAD,
        '#': NodeKind.WALL,
        'D': NodeKind.DEPOT,
        'Z': NodeKind.TARGET,
    }
    count = {'D': 0, 'Z': 0}

    for y, row in enumerate(lines):
        for x, s in enumerate(row):
            label = None
            if s in count:
                label = f'{s}{count[s]}'
                count[s] += 1
            g.add_node(GraphNode((x, y), kinds.get(s, NodeKind.ROAD), label))

    g.rebuild_edges()
    return g


def create_map1():
    return graph_from_ascii(MAP_1, 'Karte 1: Flaschenhals')


def create_map2():
    return graph_from_ascii(MAP_2, 'Karte 2: Zwei Viertel')
