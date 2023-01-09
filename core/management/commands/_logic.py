from django.db.models import F

from core.models import Taskogotchi


def set_stats_full(stdout, style):
    Taskogotchi.objects.all().update(health=100, strength=100)


def decrease_health(stdout, style, decrease_value=5):
    Taskogotchi.objects.filter(health__gt=0).update(health=F('health') - decrease_value)
