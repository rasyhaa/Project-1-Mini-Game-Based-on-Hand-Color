import config

class LaneManager:
    """Manages the 3 fixed lanes, their screen coordinates, and transition validity."""

    def __init__(self, lane_centers=None):
        if lane_centers is None:
            self.lane_centers = list(config.LANE_CENTERS)
        else:
            self.lane_centers = list(lane_centers)
        self.total_lanes = len(self.lane_centers)

    def get_lane_center(self, lane_idx: int) -> int:
        """Returns the horizontal center coordinate (x) for the given lane index."""
        clamped = self.clamp_lane(lane_idx)
        return self.lane_centers[clamped]

    def is_valid_lane(self, lane_idx: int) -> bool:
        """Checks if a lane index is within valid bounds [0, 2]."""
        return 0 <= lane_idx < self.total_lanes

    def clamp_lane(self, lane_idx: int) -> int:
        """Restricts lane index strictly within [0, total_lanes - 1]."""
        return max(0, min(self.total_lanes - 1, int(lane_idx)))

    def can_transition(self, from_lane: int, to_lane: int) -> bool:
        """
        Validates transition rules between lanes:
        - From Lane 0 (Left): can only move to Lane 1 (Center)
        - From Lane 1 (Center): can move to Lane 0 (Left) or Lane 2 (Right)
        - From Lane 2 (Right): can only move to Lane 1 (Center)
        - Same lane is always valid (no transition required)
        """
        if not self.is_valid_lane(from_lane) or not self.is_valid_lane(to_lane):
            return False

        if from_lane == to_lane:
            return True

        # Exactly 1 lane step allowed per atomic transition
        return abs(to_lane - from_lane) == 1

    def next_step_toward(self, current_lane: int, target_lane: int) -> int:
        """
        Determines the next sequential lane to reach target_lane safely.
        For example:
        - If at lane 0 and hand calls for lane 2, next valid step is lane 1.
        - If at lane 2 and hand calls for lane 0, next valid step is lane 1.
        """
        target = self.clamp_lane(target_lane)
        current = self.clamp_lane(current_lane)

        if target > current:
            return current + 1
        elif target < current:
            return current - 1
        return current
