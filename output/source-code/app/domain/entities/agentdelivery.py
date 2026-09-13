from dataclasses import dataclass, field
from app.domain.entities.deliverytask import DeliveryTask
from app.domain.entities.graph import Position


@dataclass
class AgentDelivery:
    task: DeliveryTask
    agent_id: int
    route: list[Position]
    current_route_index: int = 0
    cost: float = 0.0