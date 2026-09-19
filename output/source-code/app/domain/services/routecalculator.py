from app.domain.entities.graph import Position


class ManhattanRouteCalculator:
    """Calculates route distances using Manhattan distance."""

    def calculate_distance(self, start: Position, target: Position) -> int:
        # Add the absolute difference of each coordinate; abs() makes the order irrelevant, because of taking the absolute value.
        return sum(abs(current - destination) for current, destination in zip(start, target))