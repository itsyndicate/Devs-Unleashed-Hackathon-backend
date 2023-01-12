from django.core.mail import send_mail
from core.models import FightChallenge, FightStatus


def send_fight_call_notification(fight: FightChallenge):
    if not fight.status == FightStatus.WAITING_ACCEPT or not fight.opponent.player.email:
        return

    send_mail(
        subject="New fight challenge",
        message=f"You were challenged to a fight by "
                f"{fight.initiator.player.name or fight.initiator.player.email} "
                f"in project {fight.initiator.project.name or '<b>not accessible</b>'}.",
        html_message=f"You were challenged to a fight by "
                     f"{fight.initiator.player.name or fight.initiator.player.email} "
                     f"in project {fight.initiator.project.name or '<b>not accessible</b>'}.",
        from_email="notification@backend.guard-lite.com",
        recipient_list=[fight.opponent.player.email],
    )
