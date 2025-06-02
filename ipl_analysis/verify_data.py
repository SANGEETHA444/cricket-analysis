import os
import sys
import json
from bson import json_util
from bson.json_util import dumps as bson_dumps

# Add project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ipl_analysis.settings')

# Import Django and models
import django
from analysis.models import PlayerStats

django.setup()

print("Verifying player statistics data...")
print("\nTotal players:", PlayerStats.objects.count())

# Get first player
first_player = PlayerStats.objects.first()
if first_player:
    print("\nFirst player details:")
    # Convert MongoDB object to JSON using bson_dumps
    print(bson_dumps(first_player.to_mongo()))

# Get sample player stats
print("\nSample player stats:")
for player in PlayerStats.objects.limit(2):
    print(bson_dumps(player.to_mongo()))

print("\nData verification complete!")
