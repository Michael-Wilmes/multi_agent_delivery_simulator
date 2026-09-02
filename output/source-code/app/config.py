from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class MapConfig:
    type: str
    random_seed: int | None
    random_width: int
    random_height: int
    wall_density: float
    depot_count: int
    target_count: int


@dataclass(frozen=True)
class SimulationConfig:
    initial_standard_agents: int
    initial_express_agents: int
    auto_tick_ms: int
    battery_enabled: bool


@dataclass(frozen=True)
class WindowConfig:
    width: int
    height: int
    fps: int


@dataclass(frozen=True)
class AppConfig:
    map: MapConfig
    simulation: SimulationConfig
    window: WindowConfig


def load_config(path: Path) -> AppConfig:
    raw = json.loads(path.read_text(encoding="utf-8"))
    m = MapConfig(**raw["map"])

    if m.type not in {"map1", "map2", "random"}:
        raise ValueError("map.type must be map1, map2 or random")
    if not 0 <= m.wall_density <= 0.45:
        raise ValueError("wall_density must be between 0.0 and 0.45")

    return AppConfig(
        m,
        SimulationConfig(**raw["simulation"]),
        WindowConfig(**raw["window"]),
    )
