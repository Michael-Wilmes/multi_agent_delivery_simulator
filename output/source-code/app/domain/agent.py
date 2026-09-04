from dataclasses import dataclass
from enum import Enum

from app.shared.constants import IDLE, OPEN, STRANDED
from .graph import Position


class AgentType(str, Enum):
    """Identifies the movement and capacity profile of an agent."""

    STANDARD = "Standard"
    EXPRESS = "Express"


@dataclass
class Agent:
    """Represents a delivery agent and its current simulation state."""

    id: int
    type: AgentType
    position: Position
    speed: int
    capacity: int
    battery: float = 100.0
    battery_cost_per_field: int = 0
    load: int = 0
    status: str = IDLE
    last_action: str = IDLE