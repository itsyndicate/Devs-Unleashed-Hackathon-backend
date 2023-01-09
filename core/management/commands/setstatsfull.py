from django.core.management.base import BaseCommand, CommandError
from ._logic import set_stats_full


class Command(BaseCommand):
    help = 'Set all taskogotchies\' stats to 100'

    def handle(self, *args, **options):
        set_stats_full(self.stdout, self.style)

        self.stdout.write(self.style.SUCCESS('Successfully set all stats to 100'))
