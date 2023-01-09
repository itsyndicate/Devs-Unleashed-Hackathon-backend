from django.core.management.base import BaseCommand, CommandError
from ._logic import decrease_health


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('decrease_value', nargs='?', type=int, default=5)

    def handle(self, *args, **options):
        decrease_health(self.stdout, self.style, options['decrease_value'])
        self.stdout.write(self.style.SUCCESS('Successfully decreased health by %s' % options['decrease_value']))
