from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .graph import Position

if TYPE_CHECKING:
    from .deliverytask import DeliveryTask


@dataclass
class Depot:
    """Represents a package starting point on the simulation map."""

    id: int
    position: Position
    tasks: list["DeliveryTask"] = field(default_factory=list, compare=False, repr=False)

    def add_task(self, task: "DeliveryTask") -> None:
        self.tasks.append(task)

    def remove_task(self, task: "DeliveryTask") -> None:
        for index, stored_task in enumerate(self.tasks):
            if stored_task is task:
                del self.tasks[index]
                return
