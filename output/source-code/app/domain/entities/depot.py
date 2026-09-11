from dataclasses import dataclass

from .graph import Position


@dataclass(frozen=True)
class Depot:
    """Represents a package starting point on the simulation map."""

    id: int
    position: Position
