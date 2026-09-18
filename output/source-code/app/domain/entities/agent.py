from dataclasses import dataclass, field
from enum import Enum
from .contractnetmessage import ContractNetMessage
from .agentdelivery import AgentDelivery
from app.shared.constants import AWAIT_PICKUP, DELIVERED, IDLE, IN_TRANSIT
from .graph import Position
from app.domain.services.routecalculator import ManhattanRouteCalculator


class AgentType(str, Enum):
    STANDARD = "Standard"
    EXPRESS = "Express"


@dataclass
class Agent:
    """Represents a delivery agent and its current simulation state."""

    id: int
    type: AgentType
    position: Position
    speed: int
    capacity: int
    task_capacity: int
    battery: float = 100.0
    battery_cost_per_field: int = 0
    load: int = 0
    status: str = IDLE
    current_action: str = IDLE
    charging_ticks_remaining: int = 0
    notifications: list[ContractNetMessage] = field(default_factory=list, repr=False)
    deliveries: list[AgentDelivery] = field(default_factory=list, repr=False)
    log_messages: list[str] = field(default_factory=list, repr=False)
    route_calculator: ManhattanRouteCalculator = field(
        default_factory=ManhattanRouteCalculator,
        repr=False,
    )

    def receive_notification(self, message: ContractNetMessage, task=None) -> None:
        self.notifications.append(message)
        if task is None:
            return

        if message.type.value == "ANNOUNCE":
            if self.has_task_capacity() and self._is_target_reachable(task):
                cost = self.calulate_delivery_task_cost(task)
                self.deliveries.append(
                    AgentDelivery(
                        task=task,
                        agent_id=self.id,
                        route=[],
                        cost=cost,
                    )
                )
        elif message.type.value == "AWARD":
            self.mark_task_await_pickup(task)
        elif message.type.value == "BID_LOST":
            self.remove_delivery(task.id)
            self.log_messages.append(f"Remove Task {task.id}, BID LOST")

    def has_task_capacity(self, reserved_tasks: int = 0) -> bool:
        return len(self.deliveries) + reserved_tasks < self.task_capacity

    def remove_delivery(self, task_id: int) -> None:
        self.deliveries[:] = [
            delivery for delivery in self.deliveries
            if delivery.task.id != task_id
        ]

    def mark_task_in_transit(self, task) -> None:
        task.status = IN_TRANSIT
        task.assigned_agent_id = self.id

    def mark_task_await_pickup(self, task) -> None:
        task.status = AWAIT_PICKUP
        task.assigned_agent_id = self.id

    def mark_task_delivered(self, task) -> None:
        task.status = DELIVERED
        self.remove_delivery(task.id)

    def _is_target_reachable(self, task) -> bool:
        return True

    def clear_notifications(self) -> None:
        self.notifications.clear()

    def calulate_delivery_task_cost(self, task) -> float:
        """Calculates the cost of a delivery task for this agent."""
        distance_to_depot = self.route_calculator.calculate_distance(
            self.position,
            task.depot.position,
        )
        delivery_distance = self.route_calculator.calculate_distance(
            task.depot.position,
            task.destination.position,
        )

        battery_loss = (distance_to_depot + delivery_distance) * self.battery_cost_per_field

        if self.battery - battery_loss < 0:
            return float("inf")  # Not enough battery to complete the task
        return float(distance_to_depot + delivery_distance)
        