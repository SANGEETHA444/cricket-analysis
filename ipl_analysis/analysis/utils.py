import csv
import pymongo
from datetime import datetime

def import_csv_to_mongodb(collection_name, csv_file_path):
    """
    Import CSV data into MongoDB collection
    """
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://127.0.0.1:27017')
        db = client['ipl_analysis']
        collection = db[collection_name]
        
        # Read and process CSV
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            documents = []
            
            # Process each row
            for row in reader:
                # Convert numeric fields
                for key, value in row.items():
                    if value.isdigit():
                        row[key] = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        row[key] = float(value)
                
                # Convert date fields if present
                if 'date' in row:
                    try:
                        row['date'] = datetime.strptime(row['date'], '%Y-%m-%d').isoformat()
                    except:
                        pass
                
                documents.append(row)
        
        # Insert documents
        if documents:
            collection.insert_many(documents)
            print(f"Successfully imported {len(documents)} documents into {collection_name}")
        else:
            print(f"No documents found in {csv_file_path}")
            
    except Exception as e:
        print(f"Error importing {collection_name}: {str(e)}")
        raise

def import_all_data():
    """
    Import all CSV files into MongoDB
    """
    try:
        # Import deliveries.csv
        print("Importing deliveries...")
        import_csv_to_mongodb('deliveries', 'deliveries.csv')
        
        # Import matches.csv
        print("Importing matches...")
        import_csv_to_mongodb('matches', 'matches.csv')
        
        # Create player stats collection from deliveries
        print("Creating player stats...")
        client = pymongo.MongoClient('mongodb://127.0.0.1:27017')
        db = client['ipl_analysis']
        
        # Aggregate player statistics
        pipeline = [
            {
                "$group": {
                    "_id": "$batsman",
                    "total_runs": {"$sum": "$batsman_runs"},
                    "matches_played": {"$addToSet": "$match_id"},
                    "seasons_played": {"$addToSet": "$season"},
                    "batting_average": {"$avg": "$batsman_runs"}
                }
            },
            {
                "$project": {
                    "player_name": "$_id",
                    "total_runs": 1,
                    "matches_played": {"$size": "$matches_played"},
                    "seasons_played": {"$size": "$seasons_played"},
                    "batting_average": 1,
                    "_id": 0
                }
            }
        ]
        
        # Run aggregation and insert results
        results = list(db.deliveries.aggregate(pipeline))
        db.player_stats.insert_many(results)
        print(f"Created {len(results)} player stats")
        
        print("Data import completed successfully!")
        
    except Exception as e:
        print(f"Error in import_all_data: {str(e)}")
        raise
