from django.core.management.base import BaseCommand
import pymongo
import csv
from datetime import datetime

class Command(BaseCommand):
    help = 'Import IPL data from CSV files into MongoDB'

    def handle(self, *args, **options):
        try:
            # Connect to MongoDB
            client = pymongo.MongoClient('mongodb://127.0.0.1:27017')
            db = client['ipl_analysis']
            
            print("Importing matches...")
            # Import matches.csv
            with open('matches.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                matches = []
                for row in reader:
                    # Convert numeric fields
                    for key, value in row.items():
                        if value.isdigit():
                            row[key] = int(value)
                        elif value.replace('.', '', 1).isdigit():
                            row[key] = float(value)
                    
                    # Convert date
                    if 'date' in row:
                        try:
                            row['date'] = datetime.strptime(row['date'], '%Y-%m-%d').isoformat()
                        except:
                            pass
                    
                    matches.append(row)
                
                if matches:
                    db.matches.insert_many(matches)
                    print(f"Imported {len(matches)} matches")
                else:
                    print("No matches found in matches.csv")

            print("Importing deliveries...")
            # Import deliveries.csv
            with open('deliveries.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                deliveries = []
                for row in reader:
                    # Convert numeric fields
                    for key, value in row.items():
                        if value.isdigit():
                            row[key] = int(value)
                        elif value.replace('.', '', 1).isdigit():
                            row[key] = float(value)
                    deliveries.append(row)
                
                if deliveries:
                    try:
                        db.deliveries.insert_many(deliveries)
                        print(f"Imported {len(deliveries)} deliveries")
                    except pymongo.errors.BulkWriteError as e:
                        print(f"Error inserting deliveries: {e.details}")
                    except Exception as e:
                        print(f"Error inserting deliveries: {str(e)}")
                else:
                    print("No deliveries found in deliveries.csv")

            print("Creating player statistics...")
            # Create player stats collection
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
            try:
                results = list(db.deliveries.aggregate(pipeline))
                db.player_stats.insert_many(results)
                print(f"Created {len(results)} player stats")
            except Exception as e:
                print(f"Error creating player stats: {str(e)}")
            
            print("Data import completed successfully!")
        except Exception as e:
            print(f"Error during data import: {str(e)}")
            
            # Merge stats and calculate averages
            batting_stats = pd.read_csv('batting_stats.csv')
            bowling_stats = pd.read_csv('bowling_stats.csv')
            
            batting_stats = batting_stats.groupby('batter').agg({
                'batsman_runs': 'sum',
                'match_id': 'nunique'
            }).reset_index()
            
            bowling_stats = bowling_stats.groupby('bowler').agg({
                'player_dismissed': 'count',
                'match_id': 'nunique'
            }).reset_index()
            
            # Merge stats and calculate averages
            stats_df = pd.merge(batting_stats, bowling_stats, left_on='batter', right_on='bowler', how='outer')
            stats_df = stats_df.fillna(0)
            
            # Calculate averages and strike rates
            stats_df['average'] = stats_df['batsman_runs'] / stats_df['match_id_x']
            stats_df['strike_rate'] = (stats_df['batsman_runs'] / stats_df['match_id_x']) * 100
            
            # Save player stats
            for idx, row in stats_df.iterrows():
                try:
                    # Convert batter name to string and handle empty values
                    player_name = str(row['batter']) if pd.notna(row['batter']) else 'Unknown Player'
                    
                    player = PlayerStats(
                        player_name=player_name,
                        total_matches=int(row['match_id_x']),
                        total_runs=int(row['batsman_runs']),
                        total_wickets=int(row['player_dismissed']),
                        batting_average=float(row['average']),
                        strike_rate=float(row['strike_rate']),
                        highest_score=0,  # To be updated later
                        best_bowling=""    # To be updated later
                    )
                    player.save()
                    if idx % 100 == 0:
                        print(f"Processed {idx + 1} player stats")
                except Exception as e:
                    print(f"Error saving player stats for {row['batter']}: {str(e)}")
            
            print("Player statistics generated successfully!")
            
            print("Data import completed successfully!")
            
        except Exception as e:
            print(f"Error during data import: {str(e)}")
