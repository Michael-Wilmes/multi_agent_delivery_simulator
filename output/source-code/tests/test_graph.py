from app.config import load_config
from app.domain.graph import NodeKind
from app.maps.presets import create_map1, create_map2, graph_from_ascii
from app.maps.random_map import RandomGraphMapFactory
from app.simulation.engine import SimulationEngine


def check(g, w, h):
    assert (g.width, g.height) == (w, h)
    walk = g.walkable_positions()
    assert len(g.reachable_from(walk[0])) == len(walk)
    assert len(g.positions_of_kind(NodeKind.DEPOT)) >= 2
    assert len(g.positions_of_kind(NodeKind.TARGET)) >= 3


def test_ascii_space_is_road():
    g = graph_from_ascii(['. # ', 'D Z '], 'space-map')
    assert g.nodes[(0, 0)].kind is NodeKind.ROAD
    assert g.nodes[(2, 0)].kind is NodeKind.ROAD
    assert g.nodes[(0, 1)].kind is NodeKind.DEPOT
    assert g.nodes[(2, 1)].kind is NodeKind.TARGET


def test_engine_starts_with_configured_agents():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)
    assert len(engine.agents) == config.simulation.initial_standard_agents + config.simulation.initial_express_agents
    assert all(engine.graph.neighbors(agent.position) for agent in engine.agents)


def test_agents_stay_within_map_bounds_after_steps():
    config = load_config(__import__('pathlib').Path('config/app.json'))
    engine = SimulationEngine(config)

    for _ in range(100):
        engine.step()
        assert all(engine.graph.in_bounds(agent.position) for agent in engine.agents)


def test_maps():
    maps = [create_map1(), create_map2(), RandomGraphMapFactory(42).create()]
    for graph in maps:
        check(graph, 10 if graph.name != 'Zufallskarte' else 20, 10 if graph.name != 'Zufallskarte' else 20)
        special_positions = graph.positions_of_kind(NodeKind.DEPOT) + graph.positions_of_kind(NodeKind.TARGET)
        assert all(graph.neighbors(position) for position in special_positions)
