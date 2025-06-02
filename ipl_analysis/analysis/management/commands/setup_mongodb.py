from django.core.management.base import BaseCommand
from analysis.models import Match, Delivery, PlayerStats
import pymongo
from django.conf import settings

class Command(BaseCommand):
    help = 'Setup MongoDB collections and indexes'

    def handle(self, *args, **options):
        # Get MongoDB connection
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]

        # Create auth collections if they don't exist
        auth_collections = ['auth_user', 'auth_group', 'auth_permission',
                          'auth_user_groups', 'auth_user_user_permissions',
                          'django_content_type', 'django_session']
        
        for collection in auth_collections:
            if collection not in db.list_collection_names():
                db.create_collection(collection)

        # Create indexes for auth collections
        if 'auth_user' in db.list_collection_names():
            db.auth_user.create_index([('username', pymongo.ASCENDING)], unique=True)
            db.auth_user.create_index([('email', pymongo.ASCENDING)], unique=True)

        if 'django_session' in db.list_collection_names():
            db.django_session.create_index([('expire_date', pymongo.ASCENDING)])

        # Create indexes for Match collection
        if 'matches' not in db.list_collection_names():
            db.create_collection('matches')
        db.matches.create_index([('season', pymongo.ASCENDING)])
        db.matches.create_index([('date', pymongo.ASCENDING)])
        db.matches.create_index([('team1', pymongo.ASCENDING)])
        db.matches.create_index([('team2', pymongo.ASCENDING)])

        # Create indexes for Delivery collection
        if 'deliveries' not in db.list_collection_names():
            db.create_collection('deliveries')
        db.deliveries.create_index([('match_id', pymongo.ASCENDING)])
        db.deliveries.create_index([('batsman', pymongo.ASCENDING)])
        db.deliveries.create_index([('bowler', pymongo.ASCENDING)])
        db.deliveries.create_index([('over', pymongo.ASCENDING)])
        db.deliveries.create_index([('ball', pymongo.ASCENDING)])

        # Create indexes for PlayerStats collection
        if 'analysis_playerstats' not in db.list_collection_names():
            db.create_collection('analysis_playerstats')
        db.analysis_playerstats.create_index([('player_name', pymongo.ASCENDING)])
        db.analysis_playerstats.create_index([('total_runs', pymongo.DESCENDING)])
        db.analysis_playerstats.create_index([('total_wickets', pymongo.DESCENDING)])

        self.stdout.write(self.style.SUCCESS('Successfully setup MongoDB collections and indexes'))
