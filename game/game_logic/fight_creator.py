from channels.db import database_sync_to_async
from time import time
from game.game_logic.fight import Fight, FightTimer, FightPlayer
from game.game_logic.constants import FIGHT_DURATION, FIGHT_COUNTDOWN_DURATION
from core.models import FightChallenge


@database_sync_to_async
def create_fight_from_fight_challenge(fight_challenge: FightChallenge) -> Fight:
    start_time = time()
    fight_timer = FightTimer(start_time=start_time, duration=FIGHT_DURATION,
                             countdown_duration=FIGHT_COUNTDOWN_DURATION)
    initiator = FightPlayer(fight_challenge.initiator.player.account_id, fight_challenge.initiator_health,
                            fight_challenge.initiator_strength, fight_challenge.initiator.player.name)
    opponent = FightPlayer(fight_challenge.opponent.player.account_id, fight_challenge.opponent_health,
                           fight_challenge.opponent_strength, fight_challenge.opponent.player.name)
    return Fight(initiator, opponent, fight_timer)
