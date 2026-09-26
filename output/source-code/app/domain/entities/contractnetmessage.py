from dataclasses import dataclass
from enum import StrEnum


class MessageType(StrEnum):
    AUCTION_ANNOUNCE = "AUCTION_ANNOUNCE"
    AUCTION_BID = "AUCTION_BID"
    AUCTION_AWARD = "AUCTION_AWARD"
    AUCTION_BID_LOST = "AUCTION_BID_LOST"
    AUCTION_NO_BID = "AUCTION_NO_BID"
    TASK_OPEN = "TASK_OPEN"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    TASK_AWAIT_PICKUP = "TASK_AWAIT_PICKUP"
    TASK_IN_TRANSIT = "TASK_IN_TRANSIT"
    TASK_DELIVERED = "TASK_DELIVERED"
    AGENT_NO_BID = "AGENT_NO_BID"
    AGENT_IDLE = "AGENT_IDLE"
    AGENT_MOVING_TO_PICKUP = "AGENT_MOVING_TO_PICKUP"
    AGENT_MOVING_TO_DROPOFF = "AGENT_MOVING_TO_DROPOFF"
    AGENT_WAIT = "AGENT_WAIT"
    AGENT_LOADING = "AGENT_LOADING"
    AGENT_CHARGE = "AGENT_CHARGE"
    AGENT_OUT_OF_ORDER = "AGENT_OUT_OF_ORDER"
    AGENT_MOVING_PICK_UP = "AGENT_MOVING_PICK_UP"
    AGENT_PICK_OFF = "AGENT_PICK_OFF"
    AGENT_MOVING_DROPOFF = "AGENT_MOVING_DROPOFF"
    AGENT_DROP_OFF = "AGENT_DROP_OFF"


@dataclass(frozen=True)
class ContractNetMessage:
    type: MessageType
    tick: int
    task_id: int | None = None
    depot: tuple[int, int] | None = None
    depot_id: int | None = None
    destination: tuple[int, int] | None = None
    destination_id: int | None = None
    deadline: int | None = None
    agent_id: int | None = None
    cost: float | None = None
    distance: float | None = None
    energy_range: float | None = None
    position: tuple[int, int] | None = None


def describe(message: ContractNetMessage) -> str:
    """Builds the human readable details text shown in the UI log and written to the CSV log."""

    match message.type:
        case MessageType.AGENT_IDLE:
            return f"Agent {message.agent_id} is idle"
        case MessageType.AGENT_MOVING_TO_PICKUP:
            return f"Agent {message.agent_id} is moving to pickup"
        case MessageType.AGENT_MOVING_TO_DROPOFF:
            return f"Agent {message.agent_id} is moving to dropoff"
        case MessageType.AGENT_WAIT:
            return f"Agent {message.agent_id} is waiting"
        case MessageType.AGENT_LOADING:
            return f"Agent {message.agent_id} is loading"
        case MessageType.AGENT_CHARGE:
            return f"Agent {message.agent_id} is charging at {message.position}"
        case MessageType.AGENT_OUT_OF_ORDER:
            return f"Agent {message.agent_id} is out of order"
        case MessageType.AGENT_MOVING_PICK_UP:
            return (
                f"Agent {message.agent_id} moved to {message.position} "
                f"while heading to pickup for T-{message.task_id:03d}"
            )
        case MessageType.AGENT_PICK_OFF:
            return f"Agent {message.agent_id} picked up T-{message.task_id:03d}"
        case MessageType.AGENT_MOVING_DROPOFF:
            return (
                f"Agent {message.agent_id} moved to {message.position} "
                f"while heading to dropoff for T-{message.task_id:03d}"
            )
        case MessageType.AGENT_DROP_OFF:
            return f"Agent {message.agent_id} dropped off T-{message.task_id:03d}"
        case MessageType.AUCTION_ANNOUNCE:
            depot = f"Depot D{message.depot_id + 1} {message.depot}"
            destination = f"Ziel Z{message.destination_id + 1} {message.destination}"
            return f"T-{message.task_id:03d}: {depot} -> {destination} bis {message.deadline}"
        case MessageType.AUCTION_BID:
            return f"T-{message.task_id:03d} Agent {message.agent_id} Kosten {message.cost}"
        case MessageType.AUCTION_AWARD:
            return (
                f"T-{message.task_id:03d} an Agent {message.agent_id}, "
                f"Kosten {message.cost}"
            )
        case MessageType.AUCTION_BID_LOST:
            return f"T-{message.task_id:03d} verloren, Kosten {message.cost}"
        case MessageType.AUCTION_NO_BID:
            return f"T-{message.task_id:03d} ohne Gebot"
        case MessageType.AGENT_NO_BID:
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
        case MessageType.TASK_OPEN:
            destination = _describe_destination(message)
            return (
                f"T-{message.task_id:03d} open: awaiting bids for {destination}, "
                f"deadline {message.deadline}"
            )
        case MessageType.TASK_ASSIGNED:
            destination = _describe_destination(message)
            return (
                f"T-{message.task_id:03d} assigned to agent {message.agent_id}; "
                f"awaiting pickup for {destination}"
            )
        case MessageType.TASK_AWAIT_PICKUP:
            destination = _describe_destination(message)
            return (
                f"T-{message.task_id:03d} AWAIT_PICKUP: waiting at "
                f"{message.depot} for Agent {message.agent_id}"
            )
        case MessageType.TASK_IN_TRANSIT:
            destination = _describe_destination(message)
            return (
                f"T-{message.task_id:03d} in delivery to {destination} "
                f"by Agent {message.agent_id}"
            )
        case MessageType.TASK_DELIVERED:
            destination = _describe_destination(message)
            return (
                f"T-{message.task_id:03d} delivered at {destination} "
                f"by Agent {message.agent_id}"
            )
        case _:
            return ""


def _describe_destination(message: ContractNetMessage) -> str:
    destination = (
        f"Destination Z{message.destination_id + 1}"
        if message.destination_id is not None
        else "destination"
    )
    if message.destination is not None:
        destination += f" {message.destination}"
    return destination