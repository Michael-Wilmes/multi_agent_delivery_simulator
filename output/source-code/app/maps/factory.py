from .presets import create_map1, create_map2
from .random_map import RandomGraphMapFactory



def create_graph_map(config):
    match config.type:
        case "map1":
            return create_map1()
        case "map2":
            return create_map2()
        case _:
            return RandomGraphMapFactory(config.random_seed).create(
                config.random_width,
                config.random_height,
                config.wall_density,
                config.depot_count,
                config.target_count,
            )
