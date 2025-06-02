from django.core.management.base import BaseCommand
from django.conf import settings
from pymongo import MongoClient

class Command(BaseCommand):
    help = 'Setup MongoDB collections for auth, contenttypes, and sessions'

    def handle(self, *args, **options):
        # Get MongoDB settings from Django settings
        db_settings = settings.DATABASES['default']
        client = MongoClient(db_settings['CLIENT']['host'])
        db = client[db_settings['NAME']]
        
        # Create collections if they don't exist
        collections = [
            'auth_user',
            'auth_group',
            'auth_permission',
            'auth_user_groups',
            'auth_user_user_permissions',
            'django_content_type',
            'django_session'
        ]
        
        for collection in collections:
            if collection not in db.list_collection_names():
                db.create_collection(collection)
                self.stdout.write(self.style.SUCCESS(f'Created collection: {collection}'))
            else:
                self.stdout.write(f'Collection already exists: {collection}')
        
        # Create indexes for auth_user
        if 'auth_user' in db.list_collection_names():
            user_collection = db['auth_user']
            user_collection.create_index([('username', 1)], unique=True)
            user_collection.create_index([('email', 1)], unique=True)
            self.stdout.write(self.style.SUCCESS('Created indexes for auth_user'))
        
        self.stdout.write(self.style.SUCCESS('MongoDB setup completed successfully!'))
