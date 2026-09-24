from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .graph import Position

if TYPE_CHECKING:
    from .deliverytask import DeliveryTask
    from app.domain.services.contractnetmanager import ContractNetManager


@dataclass
class Depot:
    """Represents a package starting point on the simulation map."""

    id: int
    position: Position
    tasks: list["DeliveryTask"] = field(default_factory=list, compare=False, repr=False)
    contract_net_manager: "ContractNetManager | None" = field(
        default=None,
        compare=False,
        repr=False,
    )

    def connect_contract_net_manager(self, manager: "ContractNetManager") -> None:
        self.contract_net_manager = manager

    def add_task(self, task: "DeliveryTask") -> None:
        self.tasks.append(task)

    def submit_task(self, task: "DeliveryTask", tick: int, deadline: int):
        if self.contract_net_manager is None:
            raise RuntimeError("Depot is not connected to a ContractNetManager")
        return self.contract_net_manager.submit_task(task, tick, deadline)

    def remove_task(self, task: "DeliveryTask") -> None:
        for index, stored_task in enumerate(self.tasks):
            if stored_task is task:
                del self.tasks[index]
                return
