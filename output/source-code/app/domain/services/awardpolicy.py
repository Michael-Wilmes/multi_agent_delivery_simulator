from dataclasses import dataclass

from app.domain.entities.contractnetmessage import ContractNetMessage


@dataclass(frozen=True)
class AwardDecision:
    agent_id: int
    cost: float


class AwardPolicy:
    """Selects a winning bid without mutating simulation state."""

    def decide(
        self,
        announcement: ContractNetMessage,
        bids: list[ContractNetMessage],
        tick: int,
    ) -> AwardDecision | None:
        if announcement.deadline is None or tick < announcement.deadline:
            return None
        if not bids:
            return None

        winning_bid = min(bids, key=lambda bid: (bid.cost, bid.agent_id))
        return AwardDecision(
            agent_id=winning_bid.agent_id,
            cost=winning_bid.cost,
        )