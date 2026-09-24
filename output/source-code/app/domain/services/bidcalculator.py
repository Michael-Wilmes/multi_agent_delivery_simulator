from dataclasses import dataclass, field

from app.domain.entities.contractnetmessage import ContractNetMessage, MessageType
from app.domain.services.awardpolicy import AwardPolicy
from app.shared.constants import OPEN


@dataclass
class BidCalculator:
    """Manages auctions and determines task assignment outcomes."""

    announcements: dict[int, ContractNetMessage] = field(default_factory=dict)
    bids: dict[int, list[ContractNetMessage]] = field(default_factory=dict)
    closed_tasks: set[int] = field(default_factory=set)
    award_policy: AwardPolicy = field(default_factory=AwardPolicy, repr=False)

    def announce_task(self, task, tick: int, deadline: int) -> ContractNetMessage:
        announcement = ContractNetMessage(
            type=MessageType.ANNOUNCE,
            tick=tick,
            task_id=task.id,
            depot=task.depot.position,
            depot_id=task.depot.id,
            destination=task.destination.position,
            destination_id=task.destination.id,
            deadline=deadline,
        )
        self.announcements[task.id] = announcement
        self.bids.setdefault(task.id, [])
        return announcement

    def record_bid(
        self,
        agent_id: int,
        task_id: int,
        cost: float,
        tick: int,
    ) -> ContractNetMessage:
        bid = ContractNetMessage(
            type=MessageType.BID,
            tick=tick,
            task_id=task_id,
            agent_id=agent_id,
            cost=cost,
        )
        self.bids.setdefault(task_id, []).append(bid)
        return bid

    def has_bid(self, task_id: int, agent_id: int) -> bool:
        return any(
            bid.agent_id == agent_id
            for bid in self.bids.get(task_id, [])
        )

    def award_ready_tasks(self, tasks, tick: int) -> tuple[ContractNetMessage, ...]:
        """Close auctions whose registered deadline has been reached."""
        outcomes = []
        for task in tasks:
            if task.status != OPEN or task.id in self.closed_tasks:
                continue

            announcement = self.announcements.get(task.id)
            if announcement is None:
                continue
            if announcement.deadline is None or tick < announcement.deadline:
                continue

            task_bids = self.bids.get(task.id, [])
            decision = self.award_policy.decide(announcement, task_bids, tick)
            if decision is None:
                outcomes.append(
                    ContractNetMessage(
                        type=MessageType.NO_BID,
                        tick=tick,
                        task_id=task.id,
                    )
                )
            else:
                outcomes.append(
                    ContractNetMessage(
                        type=MessageType.AWARD,
                        tick=tick,
                        task_id=task.id,
                        agent_id=decision.agent_id,
                        cost=decision.cost,
                    )
                )
                outcomes.extend(
                    ContractNetMessage(
                        type=MessageType.BID_LOST,
                        tick=tick,
                        task_id=task.id,
                        agent_id=bid.agent_id,
                        cost=bid.cost,
                    )
                    for bid in task_bids
                    if bid.agent_id != decision.agent_id
                )
            self.closed_tasks.add(task.id)
        return tuple(outcomes)

