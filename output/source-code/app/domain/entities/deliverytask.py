from dataclasses import dataclass
from enum import Enum

from app.shared.constants import IDLE, OPEN
from .depot import Depot
from .destination import Destination


@dataclass
class DeliveryTask:
    """Represents a package delivery from a depot to a destination."""

    id: int
    depot: Depot
    destination: Destination
    created_tick: int
    status: str = OPEN
    assigned_agent_id: int | None = None