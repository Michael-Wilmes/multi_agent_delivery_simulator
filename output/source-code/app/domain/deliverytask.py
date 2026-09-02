from dataclasses import dataclass
from enum import Enum

from app.shared.constants import IDLE, OPEN
from .graph import Position


@dataclass
class DeliveryTask:
    id: int
    depot: Position
    destination: Position
    created_tick: int
    status: str = OPEN