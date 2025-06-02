import pymongo
import json
import csv
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['ipl_analysis']

# Read and import player stats
def import_player_stats():
    print("Importing player stats...")
    try:
        # Create or clear collection
        db.drop_collection('player_stats')
        player_stats = db.create_collection('player_stats')
        
        # Read and insert data
        with open('player_stats.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = [{k: v for k, v in row.items()} for row in reader]
            player_stats.insert_many(data)
            print(f"Inserted {len(data)} player stats")
    except Exception as e:
        print(f"Error importing player stats: {str(e)}")

# Read and import matches
def import_matches():
    print("Importing matches...")
    try:
        # Create or clear collection
        db.drop_collection('matches')
        matches = db.create_collection('matches')
        
        # Read and insert data
        with open('matches.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = [{k: v for k, v in row.items()} for row in reader]
            matches.insert_many(data)
            print(f"Inserted {len(data)} matches")
    except Exception as e:
        print(f"Error importing matches: {str(e)}")

# Read and import deliveries
def import_deliveries():
    print("Importing deliveries...")
    try:
        # Create or clear collection
        db.drop_collection('deliveries')
        deliveries = db.create_collection('deliveries')
        
        # Read and insert data
        with open('deliveries.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = [{k: v for k, v in row.items()} for row in reader]
            deliveries.insert_many(data)
            print(f"Inserted {len(data)} deliveries")
    except Exception as e:
        print(f"Error importing deliveries: {str(e)}")

# Main execution
if __name__ == '__main__':
    print("Starting data import...")
    import_player_stats()
    import_matches()
    import_deliveries()
    print("Data import completed")
