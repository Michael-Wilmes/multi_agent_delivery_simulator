from dataclasses import dataclass
from enum import StrEnum


class MessageType(StrEnum):
    ANNOUNCE = "ANNOUNCE"
    BID = "BID"
    AWARD = "AWARD"
    BID_LOST = "BID_LOST"


@dataclass(frozen=True)
class ContractNetMessage:
    type: MessageType
    tick: int
    task_id: int
    depot: tuple[int, int] | None = None
    depot_id: int | None = None
    destination: tuple[int, int] | None = None
    destination_id: int | None = None
    deadline: int | None = None
    agent_id: int | None = None
    cost: float | None = None