from dataclasses import dataclass, field
from enum import Enum
import math
from typing import TYPE_CHECKING
from .contractnetmessage import ContractNetMessage
from .agentdelivery import AgentDelivery
from app.shared.constants import (
    AWAIT_PICKUP,
    CHARGE,
    DELIVER,
    DELIVERED,
    IDLE,
    IN_TRANSIT,
    LOAD_DELIVERY,
    LOADING,
    MOVE,
    MOVING_TO_DROPOFF,
    MOVING_TO_PICKUP,
    OPEN,
    PICKUP,
    STRANDED,
)
from .graph import Position
from app.domain.services.routecalculator import ManhattanRouteCalculator
from .contractnetmessage import MessageType

if TYPE_CHECKING:
    from app.domain.services.contractnetmanager import ContractNetManager


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
    contract_net_manager: "ContractNetManager | None" = field(
        default=None,
        repr=False,
        compare=False,
    )
    route_calculator: ManhattanRouteCalculator = field(
        default_factory=ManhattanRouteCalculator,
        repr=False,
    )
    battery_capacity: float = 100.0

    def receive_notification(self, message: ContractNetMessage, task=None) -> None:
        self.notifications.append(message)
        if task is None:
            return

        if message.type is MessageType.AUCTION_ANNOUNCE:
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
                        type=MessageType.AGENT_NO_BID,
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
        elif message.type is MessageType.AUCTION_BID_LOST:
            self.remove_delivery(task.id)
            self.log_messages.append(f"Remove Task {task.id}, BID LOST")

    def submit_pending_bids(self, tick: int) -> None:
        manager = self.contract_net_manager
        if manager is None:
            return

        announced_task_ids = {
            notification.task_id
            for notification in self.notifications
            if notification.type is MessageType.AUCTION_ANNOUNCE
        }
        for delivery in self.deliveries:
            task = delivery.task
            if (
                task.id not in announced_task_ids
                or task.status != OPEN
                or manager.has_bid(task.id, self.id)
            ):
                continue
            manager.record_bid(self.id, task.id, delivery.cost, tick)

    def choose_action(self) -> str:
        if self.status == STRANDED:
            return STRANDED
        if self.status == LOADING:
            return self.current_action

        assigned_tasks = [
            delivery.task
            for delivery in self.deliveries
            if delivery.task.assigned_agent_id == self.id
            and delivery.task.status in {AWAIT_PICKUP, IN_TRANSIT}
        ]
        if not assigned_tasks:
            return IDLE
        if any(
            task.status == AWAIT_PICKUP
            and task.depot.position == self.position
            and self.load < self.capacity
            for task in assigned_tasks
        ):
            return PICKUP
        if any(
            task.status == IN_TRANSIT
            and task.destination.position == self.position
            for task in assigned_tasks
        ):
            return DELIVER
        return MOVE

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

    def pick_up_task(self, tick: int):
        manager = self.contract_net_manager
        if manager is None or self.load >= self.capacity:
            return None

        task = next(
            (
                delivery.task
                for delivery in self.deliveries
                if delivery.task.status == AWAIT_PICKUP
                and delivery.task.assigned_agent_id == self.id
                and delivery.task.depot.position == self.position
            ),
            None,
        )
        if task is None or not self.pick_task(task):
            return None
        if not manager.start_task_for_agent(self, task, tick):
            return None

        manager.record_agent_activity(
            MessageType.AGENT_PICK_OFF,
            self.id,
            task.id,
            tick,
            self.position,
        )
        self.set_status(LOADING, tick)
        self.current_action = LOAD_DELIVERY
        return task

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

    def deliver_assigned_task(self, tick: int):
        manager = self.contract_net_manager
        if manager is None:
            return None

        task = next(
            (
                delivery.task
                for delivery in self.deliveries
                if delivery.task.status == IN_TRANSIT
                and delivery.task.assigned_agent_id == self.id
                and delivery.task.destination.position == self.position
            ),
            None,
        )
        if task is None or not self.deliver_task(task):
            return None
        if not manager.deliver_task_for_agent(self, task, tick):
            return None

        manager.record_agent_activity(
            MessageType.AGENT_DROP_OFF,
            self.id,
            task.id,
            tick,
            self.position,
        )
        self.set_status(self._task_activity_status(), tick)
        return task

    def _is_target_reachable(self, task) -> bool:
        return True

    def clear_notifications(self) -> None:
        self.notifications.clear()

    def connect_contract_net_manager(self, manager: "ContractNetManager") -> None:
        self.contract_net_manager = manager

    def set_status(self, status: str, tick: int = 0) -> bool:
        if self.status == status:
            return False
        self.status = status
        if self.contract_net_manager is not None:
            self.contract_net_manager.record_agent_status(self.id, status, tick)
        return True

    def mark_stranded(self, tick: int = 0) -> None:
        """Transition the agent into stranded state when battery is exhausted away from a depot."""
        if self.status == STRANDED:
            return
        self.battery = 0.0
        self.set_status(STRANDED, tick)
        self.current_action = STRANDED

    def move_to(
        self,
        position: Position,
        battery_enabled: bool = True,
        tick: int = 0,
    ) -> bool:
        """Move to an already-approved position and consume movement energy."""
        if self.status == STRANDED:
            return False

        self.position = position
        if not battery_enabled:
            return False

        self.battery = max(0.0, self.battery - self.battery_cost_per_field)
        if self.battery <= 0:
            self.mark_stranded(tick)
        return self.battery <= 0

    def start_charging(self, charging_duration_ticks: int, tick: int) -> bool:
        if self.status == STRANDED or self.battery >= self.battery_capacity:
            return False
        self.set_status(LOADING, tick)
        self.charging_ticks_remaining = max(1, charging_duration_ticks)
        self.current_action = CHARGE
        self._record_charge(tick)
        return True

    def advance_loading(self, tick: int) -> None:
        if self.current_action == CHARGE:
            self._record_charge(tick)
            if self.charging_ticks_remaining > 1:
                self.charging_ticks_remaining -= 1
                return

        self.battery = self.battery_capacity
        self.charging_ticks_remaining = 0
        self.set_status(self._task_activity_status(), tick)
        self.current_action = CHARGE

    def _task_activity_status(self) -> str:
        assigned_tasks = [
            delivery.task
            for delivery in self.deliveries
            if delivery.task.assigned_agent_id == self.id
            and delivery.task.status in {AWAIT_PICKUP, IN_TRANSIT}
        ]
        if not assigned_tasks:
            return IDLE
        if assigned_tasks[0].status == AWAIT_PICKUP:
            return MOVING_TO_PICKUP
        return MOVING_TO_DROPOFF

    def _record_charge(self, tick: int) -> None:
        if self.contract_net_manager is not None:
            self.contract_net_manager.record_agent_activity(
                MessageType.AGENT_CHARGE,
                self.id,
                None,
                tick,
                self.position,
            )

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
        