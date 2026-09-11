from dataclasses import dataclass, field
from app.domain.entities.contractnetmessage import (
    ContractNetMessage,
    MessageType
)

@dataclass
class ContractNetManager:
    """Coordinates and records Contract Net communication events."""

    events: list[ContractNetMessage] = field(default_factory=list)

    def announce_task(self, task, tick: int, deadline: int) -> None:
        self.events.append(
            ContractNetMessage(
                type=MessageType.ANNOUNCE,
                tick=tick,
                task_id=task.id,
                depot=task.depot.position,
                depot_id=task.depot.id,
                destination=task.destination.position,
                destination_id=task.destination.id,
                deadline=deadline,
            )
        )


    def record_bid(self, agent_id: int, task_id: int, cost: float, tick: int) -> None:
        self.events.append(
            ContractNetMessage(
                type=MessageType.BID,
                tick=tick,
                task_id=task_id,
                agent_id=agent_id,
                cost=cost,
            )
        )


    def award_task(self, task_id: int, agent_id: int, tick: int) -> None:
        self.events.append(
            ContractNetMessage(
                type=MessageType.AWARD,
                tick=tick,
                task_id=task_id,
                agent_id=agent_id,
            )
        )

    def recent_events(self, limit: int = 20) -> tuple[ContractNetMessage, ...]:
        return tuple(self.events[-limit:])
