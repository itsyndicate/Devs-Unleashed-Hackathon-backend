from game.game_logic.fight import Fight
from game.game_logic.actions import FightAction, HitFightAction, DefaultAction
from game.game_logic.constants import ACTION_KICK, ACTION_PUNCH


def map_action(account_id: str, action: str, fight: Fight | None = None) -> FightAction:
    if fight is None:
        return DefaultAction()
    if action in [ACTION_KICK, ACTION_PUNCH]:
        if account_id == fight.player1.account_id:
            return HitFightAction(fight.player1, fight.player2)
        elif account_id == fight.player2.account_id:
            return HitFightAction(fight.player2, fight.player1)
        else:
            raise ValueError('Account id is not in fight')
    return DefaultAction()
