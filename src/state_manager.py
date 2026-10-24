from enum import Enum, auto

class GameState(Enum):
    HOME = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class StateManager:
    """Controls high-level game state transitions."""

    def __init__(self, initial_state: GameState = GameState.HOME):
        self._current_state = initial_state
        self._previous_state = initial_state

    @property
    def current_state(self) -> GameState:
        return self._current_state

    @property
    def previous_state(self) -> GameState:
        return self._previous_state

    def change_state(self, new_state: GameState):
        """Switches to new_state and remembers previous_state."""
        if self._current_state != new_state:
            self._previous_state = self._current_state
            self._current_state = new_state
            print(f"[StateManager] State changed: {self._previous_state.name} -> {self._current_state.name}")

    def toggle_pause(self):
        """Toggles between PLAYING and PAUSED."""
        if self._current_state == GameState.PLAYING:
            self.change_state(GameState.PAUSED)
        elif self._current_state == GameState.PAUSED:
            self.change_state(GameState.PLAYING)
