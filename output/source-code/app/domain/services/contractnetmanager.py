from dataclasses import dataclass, field

from app.domain.entities.contractnetmessage import ContractNetMessage, MessageType
from app.domain.services.bidcalculator import BidCalculator
from app.shared.constants import (
    AWAIT_PICKUP,
    BUSY,
    DELIVERED,
    IDLE,
    IN_TRANSIT,
    LOADING,
    NO_BID,
    OPEN,
    STRANDED,
    UNANNOUNCED,
)

@dataclass
class ContractNetManager:
    """Coordinates and records Contract Net communication events."""

    events: list[ContractNetMessage] = field(default_factory=list)
    agents: list = field(default_factory=list, repr=False)
    bid_calculator: BidCalculator = field(default_factory=BidCalculator, repr=False)

    def register_agent(self, agent) -> None:
        if agent not in self.agents:
            self.agents.append(agent)
        agent.connect_contract_net_manager(self)

    def record_agent_status(
        self,
        agent_id: int,
        status: str,
        tick: int,
    ) -> ContractNetMessage:
        message_type = {
            IDLE: MessageType.AGENT_IDLE,
            BUSY: MessageType.AGENT_BUSY,
            LOADING: MessageType.AGENT_LOADING,
            STRANDED: MessageType.AGENT_OUT_OF_ORDER,
        }.get(status)
        if message_type is None:
            raise ValueError(f"Unsupported agent status: {status}")
        event = ContractNetMessage(
            type=message_type,
            tick=tick,
            agent_id=agent_id,
        )
        self.events.append(event)
        return event

    def record_agent_activity(
        self,
        message_type: MessageType,
        agent_id: int,
        task_id: int,
        tick: int,
        position: tuple[int, int] | None = None,
    ) -> ContractNetMessage:
        event = ContractNetMessage(
            type=message_type,
            tick=tick,
            agent_id=agent_id,
            task_id=task_id,
            position=position,
        )
        self.events.append(event)
        return event

    def submit_task(
        self,
        task,
        tick: int,
        deadline: int,
    ) -> tuple[ContractNetMessage, ...]:
        if task.status != UNANNOUNCED:
            raise ValueError("Only unannounced tasks can be announced")
        announcement = self.bid_calculator.announce_task(task, tick, deadline)
        self.events.append(announcement)
        task.status = OPEN
        self.events.append(
            ContractNetMessage(
                type=MessageType.TASK_OPEN,
                tick=tick,
                task_id=task.id,
                depot_id=task.depot.id,
                destination=task.destination.position,
                destination_id=task.destination.id,
                deadline=deadline,
            )
        )
        resource_events = []
        for agent in self.agents:
            response = agent.receive_notification(announcement, task)
            if response is not None:
                self.events.append(response)
                resource_events.append(response)
        return tuple(resource_events)

    def has_bid(self, task_id: int, agent_id: int) -> bool:
        return self.bid_calculator.has_bid(task_id, agent_id)

    def award_ready_tasks(self, tasks, tick: int) -> tuple[ContractNetMessage, ...]:
        outcomes = self.bid_calculator.award_ready_tasks(tasks, tick)
        for outcome in outcomes:
            self.events.append(outcome)
            self._notify_agent(outcome, tasks)
        return tuple(outcomes)

    def record_bid(self, agent_id: int, task_id: int, cost: float, tick: int):
        bid = self.bid_calculator.record_bid(agent_id, task_id, cost, tick)
        self.events.append(bid)
        return bid

    def _notify_agent(self, message, tasks):
        if message.agent_id is None:
            return
        task = next((task for task in tasks if task.id == message.task_id), None)
        if task is None:
            return
        for agent in self.agents:
            if agent.id == message.agent_id:
                if message.type is MessageType.AUCTION_AWARD:
                    task.status = AWAIT_PICKUP
                    task.assigned_agent_id = agent.id
                    agent.set_status(BUSY, message.tick)
                    self.events.append(
                        ContractNetMessage(
                            type=MessageType.TASK_ASSIGNED,
                            tick=message.tick,
                            task_id=task.id,
                            agent_id=agent.id,
                            depot_id=task.depot.id,
                            destination=task.destination.position,
                            destination_id=task.destination.id,
                        )
                    )
                    self.events.append(
                        ContractNetMessage(
                            type=MessageType.TASK_AWAIT_PICKUP,
                            tick=message.tick,
                            task_id=task.id,
                            agent_id=agent.id,
                            depot=task.depot.position,
                            depot_id=task.depot.id,
                            destination=task.destination.position,
                            destination_id=task.destination.id,
                        )
                    )
                agent.receive_notification(message, task)
                return

    def assign_task_to_agent(self, agent, task, tick: int | None = None) -> bool:
        if task is None or task.depot.position != agent.position:
            return False
        if task.status not in {OPEN, AWAIT_PICKUP}:
            return False
        if agent.load >= agent.capacity:
            return False
        if task.status == OPEN:
            task.status = AWAIT_PICKUP
            task.assigned_agent_id = agent.id
            agent.set_status(BUSY, tick if tick is not None else 0)
            self.events.append(
                ContractNetMessage(
                    type=MessageType.TASK_ASSIGNED,
                    tick=tick if tick is not None else 0,
                    task_id=task.id,
                    agent_id=agent.id,
                    depot_id=task.depot.id,
                    destination=task.destination.position,
                    destination_id=task.destination.id,
                )
            )
            self.events.append(
                ContractNetMessage(
                    type=MessageType.TASK_AWAIT_PICKUP,
                    tick=tick if tick is not None else 0,
                    task_id=task.id,
                    agent_id=agent.id,
                    depot=task.depot.position,
                    depot_id=task.depot.id,
                    destination=task.destination.position,
                    destination_id=task.destination.id,
                )
            )
        elif task.assigned_agent_id != agent.id:
            return False
        return True

    def start_task_for_agent(self, agent, task, tick: int | None = None) -> bool:
        if task is None or task.assigned_agent_id != agent.id:
            return False
        if task.status != IN_TRANSIT:
            return False
        self.events.append(
            ContractNetMessage(
                type=MessageType.TASK_IN_TRANSIT,
                tick=tick if tick is not None else 0,
                task_id=task.id,
                agent_id=agent.id,
                depot_id=task.depot.id,
                destination=task.destination.position,
                destination_id=task.destination.id,
            )
        )
        return True

    def deliver_task_for_agent(self, agent, task, tick: int | None = None) -> bool:
        if task is None or task.status != DELIVERED:
            return False
        self.events.append(
            ContractNetMessage(
                type=MessageType.TASK_DELIVERED,
                tick=tick if tick is not None else 0,
                task_id=task.id,
                agent_id=agent.id,
                depot_id=task.depot.id,
                destination=task.destination.position,
                destination_id=task.destination.id,
            )
        )
        return True

    def close_task(self, task, status: str, tick: int | None = None) -> bool:
        if task is None:
            return False
        task.status = status
        task.assigned_agent_id = None
        return True

    def recent_events(self, limit: int = 20) -> tuple[ContractNetMessage, ...]:
        return tuple(self.events[-limit:])
