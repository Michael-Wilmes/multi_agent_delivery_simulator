from dataclasses import dataclass, field
from app.domain.entities.contractnetmessage import ContractNetMessage, MessageType
from app.domain.services.bidcalculator import BidCalculator

@dataclass
class ContractNetManager:
    """Coordinates and records Contract Net communication events."""

    events: list[ContractNetMessage] = field(default_factory=list)
    agents: list = field(default_factory=list, repr=False)
    bid_calculator: BidCalculator = field(default_factory=BidCalculator, repr=False)

    def register_agent(self, agent) -> None:
        if agent not in self.agents:
            self.agents.append(agent)

    def submit_task(
        self,
        task,
        tick: int,
        deadline: int,
    ) -> tuple[ContractNetMessage, ...]:
        announcement = self.bid_calculator.announce_task(task, tick, deadline)
        self.events.append(announcement)
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
                agent.receive_notification(message, task)
                return

    def recent_events(self, limit: int = 20) -> tuple[ContractNetMessage, ...]:
        return tuple(self.events[-limit:])
