from django.core.management.base import BaseCommand
from mongoengine import connect
from analysis.models import PlayerStats

class Command(BaseCommand):
    help = 'Initialize MongoDB connection and migrate player statistics'

    def handle(self, *args, **options):
        # Connect to MongoDB
        connect(
            db='ipl_analysis',
            host='mongodb://127.0.0.1:27017',
            alias='default'
        )
        
        # Create indexes
        PlayerStats.ensure_indexes()
        self.stdout.write(self.style.SUCCESS('Successfully initialized MongoDB and created indexes'))
