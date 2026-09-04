from dataclasses import dataclass
from enum import Enum

from app.shared.constants import IDLE, OPEN
from .graph import Position


@dataclass
class DeliveryTask:
    """Represents a package delivery from a depot to a destination."""

    id: int
    depot: Position
    destination: Position
    created_tick: int
    status: str = OPEN
    assigned_agent_id: int | None = None