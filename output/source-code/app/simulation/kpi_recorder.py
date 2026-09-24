import csv
from pathlib import Path

from app.domain.entities.contractnetmessage import ContractNetMessage, MessageType
from app.shared.constants import DELIVERED, IN_TRANSIT, OPEN, STRANDED


class KpiRecorder:
    """Collects and persists simulation KPIs in one place."""

    def __init__(self, directory: Path):
        self.directory = directory
        self.package_creation_file = directory / "package_creation.csv"
        self.simulation_file = directory / "simulation.csv"
        self.bid_file = directory / "bidding.csv"
        self._initialize_files()

    def _initialize_files(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        with self.package_creation_file.open("w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(("tick", "depot_id", "task_id"))
        with self.simulation_file.open("w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow((
                "tick",
                "total_agents",
                "active_agents",
                "stranded_agents",
                "total_tasks",
                "open_tasks",
                "in_transit_tasks",
                "delivered_tasks",
                "total_load",
                "packages_created",
            ))
        with self.bid_file.open("w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(("tick", "task_id", "agent_id", "result", "cost"))

    def record_task_created(self, tick, depot_id, task_id):
        with self.package_creation_file.open("a", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow((tick, depot_id, task_id))

    def record_contract_event(self, event: ContractNetMessage):
        result = {
            MessageType.BID: "submitted",
            MessageType.NO_BID_RESOURCES: "no_bid_resources",
            MessageType.AWARD: "won",
            MessageType.BID_LOST: "lost",
            MessageType.NO_BID: "no_bid",
        }.get(event.type)
        if result is None:
            return
        with self.bid_file.open("a", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow((
                event.tick,
                event.task_id,
                event.agent_id,
                result,
                event.cost,
            ))

    def record_simulation_tick(self, tick, agents, tasks, package_creation_kpi):
        task_counts = {
            status: sum(task.status == status for task in tasks)
            for status in (OPEN, IN_TRANSIT, DELIVERED)
        }
        stranded_agents = sum(agent.status == STRANDED for agent in agents)
        row = (
            tick,
            len(agents),
            len(agents) - stranded_agents,
            stranded_agents,
            len(tasks),
            task_counts[OPEN],
            task_counts[IN_TRANSIT],
            task_counts[DELIVERED],
            sum(agent.load for agent in agents),
            sum(event[0] == tick for event in package_creation_kpi),
        )
        with self.simulation_file.open("a", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(row)