from dataclasses import dataclass, field
from app.domain.entities.contractnetmessage import (
    ContractNetMessage,
    MessageType
)
from app.shared.constants import OPEN

@dataclass
class ContractNetManager:
    """Coordinates and records Contract Net communication events."""

    events: list[ContractNetMessage] = field(default_factory=list)
    agents: list = field(default_factory=list, repr=False)

    def register_agent(self, agent) -> None:
        if agent not in self.agents:
            self.agents.append(agent)

    def announce_task(self, task, tick: int, deadline: int) -> None:
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
        self.events.append(announcement)
        for agent in self.agents:
            agent.receive_notification(announcement, task)

    def has_bid(self, task_id: int, agent_id: int) -> bool:
        return any(
            event.type is MessageType.BID
            and event.task_id == task_id
            and event.agent_id == agent_id
            for event in self.events
        )

    def award_ready_tasks(self, tasks, tick: int) -> tuple[ContractNetMessage, ...]:
        outcomes = []
        for task in tasks:
            if task.status != OPEN:
                continue

            announcement = next(
                (
                    event for event in self.events
                    if event.type is MessageType.ANNOUNCE
                    and event.task_id == task.id
                ),
                None,
            )
            if announcement is None:
                continue

            if any(
                event.type is MessageType.NO_BID
                and event.task_id == task.id
                for event in self.events
            ):
                continue

            bids = [
                event for event in self.events
                if event.type is MessageType.BID
                and event.task_id == task.id
            ]
            deadline_reached = announcement.deadline is not None and tick >= announcement.deadline
            if not deadline_reached:
                continue

            if not bids:
                outcomes.append(
                    ContractNetMessage(
                        type=MessageType.NO_BID,
                        tick=tick,
                        task_id=task.id,
                    )
                )
                self.events.append(outcomes[-1])
                continue

            winning_bid = min(bids, key=lambda bid: (bid.cost, bid.agent_id))
            outcomes.extend(self.award_task(task.id, winning_bid.agent_id, tick, task))
        return tuple(outcomes)

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


    def award_task(self, task_id: int, agent_id: int, tick: int, task=None):
        winning_bid = next(
            (
                event for event in self.events
                if event.type is MessageType.BID
                and event.task_id == task_id
                and event.agent_id == agent_id
            ),
            None,
        )
        award = ContractNetMessage(
            type=MessageType.AWARD,
            tick=tick,
            task_id=task_id,
            agent_id=agent_id,
            cost=winning_bid.cost if winning_bid else None,
        )

        self.events.append(award)
        outcomes = [award]

        for agent in self.agents:
            if agent.id == agent_id:
                agent.receive_notification(award, task)
                break
            
        for bid in tuple(self.events):
            if (
                bid.type is MessageType.BID
                and bid.task_id == task_id
                and bid.agent_id != agent_id
            ):
                lost = ContractNetMessage(
                    type=MessageType.BID_LOST,
                    tick=tick,
                    task_id=task_id,
                    agent_id=bid.agent_id,
                    cost=bid.cost,
                )
                self.events.append(lost)
                outcomes.append(lost)
                for agent in self.agents:
                    if agent.id == bid.agent_id:
                        agent.receive_notification(lost, task)
                        break
        return tuple(outcomes)

    def recent_events(self, limit: int = 20) -> tuple[ContractNetMessage, ...]:
        return tuple(self.events[-limit:])
