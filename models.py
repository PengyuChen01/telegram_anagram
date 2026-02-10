"""Data models for the Anagram game."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum

from config import GAME_DURATION, SCORE_MAP


class GameMode(Enum):
    SOLO = "solo"
    MULTI = "multi"


class GameState(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"


@dataclass
class Player:
    user_id: int
    username: str
    display_name: str
    score: int = 0
    found_words: List[str] = field(default_factory=list)
    current_input: str = ""
    message_id: Optional[int] = None
    last_action: str = ""
    used_positions: Set[int] = field(default_factory=set)
    input_positions: List[int] = field(default_factory=list)
    last_update_time: float = 0.0

    def add_word(self, word):
        word = word.upper()
        if word in self.found_words:
            return 0
        points = SCORE_MAP.get(len(word), 0)
        if points > 0:
            self.found_words.append(word)
            self.score += points
        return points

    def has_found(self, word):
        return word.upper() in self.found_words

    def reset_input(self):
        self.current_input = ""
        self.used_positions.clear()
        self.input_positions.clear()

    def backspace(self):
        """Remove last letter and restore its position."""
        if self.current_input and self.input_positions:
            self.input_positions.pop()
            self.current_input = self.current_input[:-1]
            self.used_positions = set(self.input_positions)

    def add_letter(self, letter, position):
        """Add a letter from a specific position."""
        if len(self.current_input) < 6 and position not in self.used_positions:
            self.current_input += letter.upper()
            self.used_positions.add(position)
            self.input_positions.append(position)

    def restore_position(self, position):
        """Restore a used position (press X to undo)."""
        if position in self.used_positions:
            self.used_positions.discard(position)
            if position in self.input_positions:
                idx = self.input_positions.index(position)
                self.input_positions.pop(idx)
                self.current_input = self.current_input[:idx] + self.current_input[idx+1:]


@dataclass
class GameSession:
    chat_id: int
    mode: GameMode
    letters: List[str] = field(default_factory=list)
    players: Dict[int, Player] = field(default_factory=dict)
    state: GameState = GameState.WAITING
    start_time: float = 0.0
    host_user_id: int = 0
    possible_words: List[str] = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def add_player(self, user_id, username, display_name):
        if user_id not in self.players:
            player = Player(user_id=user_id, username=username, display_name=display_name)
            self.players[user_id] = player
        return self.players[user_id]

    def get_player(self, user_id):
        return self.players.get(user_id)

    def start(self):
        self.state = GameState.PLAYING
        self.start_time = time.time()

    def finish(self):
        self.state = GameState.FINISHED

    @property
    def is_playing(self):
        return self.state == GameState.PLAYING

    @property
    def is_waiting(self):
        return self.state == GameState.WAITING

    @property
    def is_finished(self):
        return self.state == GameState.FINISHED

    @property
    def time_remaining(self):
        if not self.is_playing:
            return 0
        elapsed = time.time() - self.start_time
        remaining = GAME_DURATION - elapsed
        return max(0, int(remaining))

    @property
    def letters_display(self):
        return "  ".join(self.letters)

    def get_rankings(self):
        return sorted(self.players.values(), key=lambda p: p.score, reverse=True)
