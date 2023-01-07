from core.models import FightStatus, FightChallenge
from rest_framework.exceptions import ValidationError


class FightStatusStateMachine:
    """
    A state machine for the fight status.
    Not a typical state machine, it contains different operations that can be performed with the status
    """
    ACTIONS = ['accept', 'start', 'complete', 'cancel']
    _fight: FightChallenge
    _save: bool

    def __init__(self, fight: FightChallenge, save: bool = True):
        self._fight = fight
        self._save = save

    @staticmethod
    def process_action(action_name: str, fight: FightChallenge, save: bool = True) -> FightChallenge:
        if action_name not in FightStatusStateMachine.ACTIONS:
            raise ValueError(f'Action "{action_name}" is not in {FightStatusStateMachine.ACTIONS}')
        state_machine = FightStatusStateMachine(fight, save)
        action_callable = getattr(state_machine, action_name)
        return action_callable()

    def _check_fight_ended(self, raise_exception: bool = True) -> bool:
        """Check if the fight is over."""
        completed = self._fight.status in [FightStatus.COMPLETED, FightStatus.CANCELED]
        if raise_exception and completed:
            raise ValidationError('The fight is already over.')
        return completed

    def accept(self) -> FightChallenge:
        """Accept the fight challenge."""
        self._check_fight_ended(raise_exception=True)
        if self._fight.status == FightStatus.WAITING_ACCEPT:
            self._fight.status = FightStatus.ACCEPTED
            if self._save:
                self._fight.save()
            return self._fight
        raise ValidationError('The fight is not in WAITING_ACCEPT status, so can\'t accept it.')

    def start(self) -> FightChallenge:
        """Start the fight."""
        self._check_fight_ended(raise_exception=True)
        if self._fight.status == FightStatus.ACCEPTED:
            self._fight.status = FightStatus.PENDING
            if self._save:
                self._fight.save()
            return self._fight
        raise ValidationError('The fight is not in ACCEPTED status, so can\'t start it.')

    def complete(self) -> FightChallenge:
        """
        Complete the fight.
        If winner is None, the fight is a draw. Otherwise, the winner is the player profile.
        """
        self._check_fight_ended(raise_exception=True)
        if self._fight.status == FightStatus.PENDING:
            self._fight.status = FightStatus.COMPLETED
            if self._save:
                self._fight.save()
            return self._fight
        raise ValidationError('The fight is not in PROGRESS status, so can\'t complete it.')

    def cancel(self) -> FightChallenge:
        """Cancel the fight."""
        self._check_fight_ended(raise_exception=True)
        self._fight.status = FightStatus.CANCELED
        if self._save:
            self._fight.save()
        return self._fight
