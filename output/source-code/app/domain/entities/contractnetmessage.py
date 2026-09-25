from dataclasses import dataclass
from enum import StrEnum


class MessageType(StrEnum):
    ANNOUNCE = "ANNOUNCE"
    BID = "BID"
    AWARD = "AWARD"
    BID_LOST = "BID_LOST"
    NO_BID = "NO_BID"
    NO_BID_RESOURCES = "NO_BID_RESOURCES"
    TASK_OPEN = "TASK_OPEN"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    TASK_AWAIT_PICKUP = "TASK_AWAIT_PICKUP"
    TASK_IN_TRANSIT = "TASK_IN_TRANSIT"
    TASK_DELIVERED = "TASK_DELIVERED"


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
    distance: float | None = None
    energy_range: float | None = None


def describe(message: ContractNetMessage) -> str:
    """Builds the human readable details text shown in the UI log and written to the CSV log."""
    destination = (
        f"Destination Z{message.destination_id + 1}"
        if message.destination_id is not None
        else "destination"
    )
    if message.destination is not None:
        destination += f" {message.destination}"
    if message.type is MessageType.ANNOUNCE:
        depot = f"Depot D{message.depot_id + 1} {message.depot}"
        destination = f"Ziel Z{message.destination_id + 1} {message.destination}"
        details = f"T-{message.task_id:03d}: {depot} -> {destination}"
        return details + f" bis {message.deadline}"
    if message.type is MessageType.BID:
        return f"T-{message.task_id:03d} Agent {message.agent_id} Kosten {message.cost}"
    if message.type is MessageType.AWARD:
        return (
            f"T-{message.task_id:03d} an Agent {message.agent_id}, "
            f"Kosten {message.cost}"
        )
    if message.type is MessageType.BID_LOST:
        return f"T-{message.task_id:03d} verloren, Kosten {message.cost}"
    if message.type is MessageType.NO_BID:
        return f"T-{message.task_id:03d} ohne Gebot"
    if message.type is MessageType.NO_BID_RESOURCES:
        distance = "unknown" if message.distance is None else f"{message.distance:.1f}"
        energy_range = (
            "unlimited"
            if message.energy_range is None
            else f"{message.energy_range:.1f}"
        )
        return (
            f"T-{message.task_id:03d} Agent {message.agent_id}: "
            f"Not reachable. Distance {distance}, "
            f"Energy range {energy_range}."
        )
    if message.type is MessageType.TASK_OPEN:
        return (
            f"T-{message.task_id:03d} open: awaiting bids for {destination}, "
            f"deadline {message.deadline}"
        )
    if message.type is MessageType.TASK_ASSIGNED:
        return (
            f"T-{message.task_id:03d} assigned to Agent {message.agent_id}; "
            f"awaiting pickup for {destination}"
        )
    if message.type is MessageType.TASK_AWAIT_PICKUP:
        return (
            f"T-{message.task_id:03d} AWAIT_PICKUP: waiting at "
            f"{message.depot} for Agent {message.agent_id}"
        )
    if message.type is MessageType.TASK_IN_TRANSIT:
        return (
            f"T-{message.task_id:03d} in delivery to {destination} "
            f"by Agent {message.agent_id}"
        )
    if message.type is MessageType.TASK_DELIVERED:
        return (
            f"T-{message.task_id:03d} delivered at {destination} "
            f"by Agent {message.agent_id}"
        )
    return ""