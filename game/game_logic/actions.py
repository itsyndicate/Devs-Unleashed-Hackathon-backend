from game.game_logic.fight import Fight, FightTimer, FightPlayer


class FightAction:
    def do_action(self) -> None:
        raise NotImplementedError


class HitFightAction(FightAction):
    def __init__(self, hit_sender: FightPlayer, hit_receiver: FightPlayer):
        self.hit_sender = hit_sender
        self.hit_receiver = hit_receiver

    def do_action(self) -> None:
        self.hit_sender.attack(self.hit_receiver)


class DefaultAction(FightAction):
    def do_action(self) -> None:
        pass
