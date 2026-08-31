from .presets import create_map1,create_map2
from .random_map import RandomGraphMapFactory
def create_graph_map(c):
    if c.type=='map1':return create_map1()
    if c.type=='map2':return create_map2()
    return RandomGraphMapFactory(c.random_seed).create(c.random_width,c.random_height,c.wall_density,c.depot_count,c.target_count)
