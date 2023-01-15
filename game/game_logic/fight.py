from time import time

from game.game_logic.exceptions import FightEndedException
from game.game_logic.json_serializable import JsonSerializable

STRENGTH_COEFFICIENT = 0.1


class FightTimer(JsonSerializable):
    start_time: float
    duration: int = 30
    countdown_duration: int = 3

    def __init__(self, start_time: float = None, duration: int = 30, countdown_duration: int = 3):
        if start_time is None:
            start_time = time()
        self.start_time = start_time
        self.duration = duration
        self.countdown_duration = countdown_duration

    @property
    def end_time(self) -> float:
        return self.start_time + self.countdown_duration + self.duration

    @property
    def time_left(self) -> float:
        return self.end_time - time()

    @property
    def is_countdown(self) -> bool:
        return time() < self.start_time + self.countdown_duration

    def check_timeout(self) -> bool:
        return time() >= self.end_time

    def to_json(self) -> dict:
        return {
            'start_time': self.start_time,
            'duration': self.duration,
            'countdown_duration': self.countdown_duration,
            'is_countdown': self.is_countdown,
            'end_time': self.end_time,
            'time_left': self.time_left,
        }

    @staticmethod
    def from_json(data: dict):
        return FightTimer(data['start_time'], data['duration'])


class FightPlayer(JsonSerializable):
    account_id: str
    health: int
    strength: int

    def __init__(self, account_id: str, health: int, strength: int):
        self.account_id = account_id
        self.health = health
        self.strength = strength

    def attack(self, opponent: 'FightPlayer') -> None:
        opponent.health -= self.strength * STRENGTH_COEFFICIENT
        if opponent.health < 0:
            opponent.health = 0

    @property
    def is_dead(self) -> bool:
        return self.health <= 0

    @property
    def is_alive(self) -> bool:
        return not self.is_dead

    def to_json(self) -> dict:
        return {
            'account_id': self.account_id,
            'health': self.health,
            'strength': self.strength,
        }

    @staticmethod
    def from_json(data: dict):
        return FightPlayer(
            data['account_id'],
            data['health'],
            data['strength'],
        )


class Fight(JsonSerializable):
    player1: FightPlayer
    player2: FightPlayer
    fight_timer: FightTimer
    _ended: bool = False  # used if fight must be ended before somebody dies or time runs out

    def __init__(self, player1: FightPlayer, player2: FightPlayer, fight_timer: FightTimer):
        self.player1 = player1
        self.player2 = player2
        self.fight_timer = fight_timer

    @property
    def is_ended(self) -> bool:
        if not self._ended:
            return any([self.player1.is_dead, self.player2.is_dead, self.fight_timer.check_timeout()])
        return self._ended

    def attack(self, attacker: FightPlayer, opponent: FightPlayer) -> None:
        if self.is_ended:
            raise FightEndedException('Fight is already ended')
        attacker.attack(opponent)

    def end_fight(self) -> None:
        self._ended = True

    def to_json(self) -> dict:
        return {
            'player1': self.player1.to_json(),
            'player2': self.player2.to_json(),
            'fight_timer': self.fight_timer.to_json(),
            'winner': self.winner,
            'ended': self.is_ended
        }

    @staticmethod
    def from_json(data: dict):
        return Fight(
            FightPlayer.from_json(data['player1']),
            FightPlayer.from_json(data['player2']),
            FightTimer.from_json(data['fight_timer'])
        )

    @property
    def is_draw(self) -> bool:
        return not self.player1.is_dead and not self.player2.is_dead or self.fight_timer.check_timeout()

    @property
    def winner(self) -> FightPlayer | None:
        if self.is_draw or not self.is_ended:
            return None
        if self.player1.is_dead:
            return self.player2
        return self.player1
