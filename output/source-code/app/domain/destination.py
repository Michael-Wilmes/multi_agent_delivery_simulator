from dataclasses import dataclass

from .graph import Position


@dataclass(frozen=True)
class Destination:
    """Represents a package delivery destination on the simulation map."""

    id: int
    position: Position
