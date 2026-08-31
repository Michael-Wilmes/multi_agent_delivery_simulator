from app.maps.presets import create_map1,create_map2
from app.maps.random_map import RandomGraphMapFactory
from app.domain.graph import NodeKind
def check(g,w,h):
 assert (g.width,g.height)==(w,h);walk=g.walkable_positions();assert len(g.reachable_from(walk[0]))==len(walk);assert len(g.positions_of_kind(NodeKind.DEPOT))>=2;assert len(g.positions_of_kind(NodeKind.TARGET))>=3
def test_maps():check(create_map1(),10,10);check(create_map2(),10,10);check(RandomGraphMapFactory(42).create(),20,20)
