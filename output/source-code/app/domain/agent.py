from dataclasses import dataclass
from enum import Enum

from app.shared.constants import IDLE, OPEN
from .graph import Position


class AgentType(str, Enum):
    STANDARD = "Standard"
    EXPRESS = "Express"


@dataclass
class Agent:
    id: int
    type: AgentType
    position: Position
    speed: int
    capacity: int
    battery: float = 100.0
    load: int = 0
    status: str = IDLE