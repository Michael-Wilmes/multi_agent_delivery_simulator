from dataclasses import dataclass, field
from enum import Enum
import math
from .contractnetmessage import ContractNetMessage
from .agentdelivery import AgentDelivery
from app.shared.constants import AWAIT_PICKUP, DELIVERED, IDLE, IN_TRANSIT, STRANDED
from .graph import Position
from app.domain.services.routecalculator import ManhattanRouteCalculator
from .contractnetmessage import MessageType


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
                if not math.isfinite(cost):
                    distance = self._delivery_distance(task)
                    maximum_distance = self._maximum_distance()
                    maximum_distance_text = (
                        "unlimited"
                        if math.isinf(maximum_distance)
                        else f"{maximum_distance:.1f}"
                    )
                    self.log_messages.append(
                        f"Not reachable. Distance: {self._delivery_distance(task):.1f}, "
                        f"Energy range: {maximum_distance_text}."
                    )
                    return ContractNetMessage(
                        type=MessageType.NO_BID_RESOURCES,
                        tick=message.tick,
                        task_id=task.id,
                        agent_id=self.id,
                        distance=distance,
                        energy_range=maximum_distance,
                    )
                self.deliveries.append(
                    AgentDelivery(
                        task=task,
                        agent_id=self.id,
                        route=[],
                        cost=cost,
                    )
                )
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

    def pick_task(self, task) -> bool:
        """Pick up an assigned task and transition it to in transit at its depot."""
        if task is None:
            return False
        if task.depot.position != self.position:
            return False
        if task.status != AWAIT_PICKUP or task.assigned_agent_id != self.id:
            return False
        if self.load >= self.capacity:
            return False
        task.status = IN_TRANSIT
        self.load += 1
        return True

    def deliver_task(self, task) -> bool:
        """Mark an owned in-transit task delivered at its destination."""
        if task is None:
            return False
        if task.status != IN_TRANSIT or task.assigned_agent_id != self.id:
            return False
        if task.destination.position != self.position:
            return False
        task.status = DELIVERED
        task.assigned_agent_id = None
        self.load = max(0, self.load - 1)
        self.remove_delivery(task.id)
        return True

    def _is_target_reachable(self, task) -> bool:
        return True

    def clear_notifications(self) -> None:
        self.notifications.clear()

    def mark_stranded(self) -> None:
        """Transition the agent into stranded state when battery is exhausted away from a depot."""
        if self.status == STRANDED:
            return
        self.battery = 0.0
        self.status = STRANDED
        self.current_action = STRANDED

    def move_to(self, position: Position, battery_enabled: bool = True) -> bool:
        """Move to an already-approved position and consume movement energy."""
        if self.status == STRANDED:
            return False

        self.position = position
        if not battery_enabled:
            return False

        self.battery = max(0.0, self.battery - self.battery_cost_per_field)
        return self.battery <= 0

    def calulate_delivery_task_cost(self, task) -> float:
        """Calculates the cost of a delivery task for this agent."""
        distance = self._delivery_distance(task)
        battery_loss = distance * self.battery_cost_per_field

        if self.battery - battery_loss < 0:
            return float("inf")  # Not enough battery to complete the task
        return distance

    def _delivery_distance(self, task) -> float:
        distance_to_depot = self.route_calculator.calculate_distance(
            self.position,
            task.depot.position,
        )
        delivery_distance = self.route_calculator.calculate_distance(
            task.depot.position,
            task.destination.position,
        )
        return float(distance_to_depot + delivery_distance)

    def _maximum_distance(self) -> float:
        if self.battery_cost_per_field == 0:
            return float("inf")
        return self.battery / self.battery_cost_per_field
        