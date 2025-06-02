from django.core.management.base import BaseCommand
from pymongo import MongoClient
from django.conf import settings

class Command(BaseCommand):
    help = 'Check MongoDB collections for data'

    def handle(self, *args, **options):
        # Get MongoDB connection
        db_settings = settings.DATABASES['default']
        client = MongoClient(db_settings['CLIENT']['host'])
        db = client[db_settings['NAME']]

        # Check collections
        collections = db.list_collection_names()
        self.stdout.write(self.style.SUCCESS(f'Collections: {collections}'))

        # Check PlayerStats collection
        if 'analysis_playerstats' in collections:
            player_count = db['analysis_playerstats'].count_documents({})
            self.stdout.write(self.style.SUCCESS(f'Total players: {player_count}'))
            sample_player = db['analysis_playerstats'].find_one()
            if sample_player:
                self.stdout.write(self.style.SUCCESS('Sample player stats:'))
                self.stdout.write(self.style.SUCCESS(str(sample_player)))
        else:
            self.stdout.write(self.style.ERROR('PlayerStats collection not found'))

        # Check Matches collection
        if 'matches' in collections:
            match_count = db['matches'].count_documents({})
            self.stdout.write(self.style.SUCCESS(f'Total matches: {match_count}'))
            sample_match = db['matches'].find_one()
            if sample_match:
                self.stdout.write(self.style.SUCCESS('Sample match:'))
                self.stdout.write(self.style.SUCCESS(str(sample_match)))
        else:
            self.stdout.write(self.style.ERROR('Matches collection not found'))

        # Check Deliveries collection
        if 'deliveries' in collections:
            delivery_count = db['deliveries'].count_documents({})
            self.stdout.write(self.style.SUCCESS(f'Total deliveries: {delivery_count}'))
            sample_delivery = db['deliveries'].find_one()
            if sample_delivery:
                self.stdout.write(self.style.SUCCESS('Sample delivery:'))
                self.stdout.write(self.style.SUCCESS(str(sample_delivery)))
        else:
            self.stdout.write(self.style.ERROR('Deliveries collection not found'))
