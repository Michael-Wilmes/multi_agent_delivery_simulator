from dataclasses import dataclass, field


ContractEvent = tuple[int, str, str, str]


@dataclass
class ContractNetManager:
    """Coordinates and records Contract Net communication events."""

    events: list[ContractEvent] = field(default_factory=list)

    def record(self, tick: int, phase: str, sender: str, details: str):
        self.events.append((tick, phase, sender, details))

    def announce_task(self, task, tick: int):
        """Announce a newly created task to the Contract Net participants."""
        self.record(
            tick,
            'CREATED',
            f'Depot D{task.depot.id + 1}',
            f'T-{task.id:03d} -> {task.destination.position}',
        )

    def recent_events(self, limit: int = 20) -> tuple[ContractEvent, ...]:
        return tuple(self.events[-limit:])
