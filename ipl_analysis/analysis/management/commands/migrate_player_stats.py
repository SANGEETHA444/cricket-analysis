from django.core.management.base import BaseCommand
from analysis.models import PlayerStats

class Command(BaseCommand):
    help = 'Migrate player statistics data'

    def handle(self, *args, **options):
        # Create indexes
        PlayerStats.ensure_indexes()
        self.stdout.write(self.style.SUCCESS('Successfully created indexes for PlayerStats'))
