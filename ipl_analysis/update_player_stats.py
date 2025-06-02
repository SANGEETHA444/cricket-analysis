from pymongo import MongoClient
import pandas as pd
import sys

print("Updating player statistics...")

# MongoDB client
client = MongoClient('mongodb://localhost:27017/')
db = client['ipl_analysis']

try:
    # Get all deliveries from database
    deliveries_data = list(db.delivery.find({}, {'_id': 0}))
    deliveries_df = pd.DataFrame(deliveries_data)
    
    print(f"Total deliveries: {len(deliveries_df)}")
    
    # Batting stats
    batting_stats = deliveries_df.groupby('batsman').agg({
        'batsman_runs': 'sum',
        'match_id': 'nunique'
    }).reset_index()
    
    # Bowling stats
    bowling_stats = deliveries_df[deliveries_df['dismissal_kind'] != 'run out'].groupby('bowler').agg({
        'player_dismissed': 'count',
        'match_id': 'nunique'
    }).reset_index()
    
    # Merge stats and calculate averages
    stats_df = pd.merge(batting_stats, bowling_stats, left_on='batsman', right_on='bowler', how='outer')
    stats_df = stats_df.fillna(0)
    
    # Convert string values to numeric
    stats_df['batsman_runs'] = pd.to_numeric(stats_df['batsman_runs'], errors='coerce')
    stats_df['match_id_x'] = pd.to_numeric(stats_df['match_id_x'], errors='coerce')
    
    # Calculate averages and strike rates
    stats_df['batting_average'] = stats_df['batsman_runs'] / stats_df['match_id_x']
    stats_df['strike_rate'] = (stats_df['batsman_runs'] / stats_df['match_id_x']) * 100
    
    # Update or create player stats
    for idx, row in stats_df.iterrows():
        try:
            player_name = str(row['batsman']) if pd.notna(row['batsman']) else 'Unknown Player'
            
            # Handle NaN values and large integers
            def safe_convert(value, default=0):
                try:
                    if pd.isna(value):
                        return default
                    num = float(value)  # Convert to float first
                    if num > 9223372036854775807:  # MongoDB int64 max
                        return int(9223372036854775807)
                    if num < -9223372036854775808:  # MongoDB int64 min
                        return int(-9223372036854775808)
                    return int(num)
                except (ValueError, TypeError):
                    return default

            try:
                # Check if player exists
                player = db.playerstats.find_one({'player_name': player_name})
                if player:
                    # Update existing player stats
                    db.playerstats.update_one(
                        {'player_name': player_name},
                        {'$set': {
                            'total_matches': safe_convert(row['match_id_x']),
                            'total_runs': safe_convert(row['batsman_runs']),
                            'total_wickets': safe_convert(row['player_dismissed']),
                            'batting_average': float(row['batting_average']) if not pd.isna(row['batting_average']) else 0.0,
                            'strike_rate': float(row['strike_rate']) if not pd.isna(row['strike_rate']) else 0.0
                        }}
                    )
                else:
                    # Create new player stats
                    db.playerstats.insert_one({
                        'player_name': player_name,
                        'total_matches': safe_convert(row['match_id_x']),
                        'total_runs': safe_convert(row['batsman_runs']),
                        'total_wickets': safe_convert(row['player_dismissed']),
                        'batting_average': float(row['batting_average']) if not pd.isna(row['batting_average']) else 0.0,
                        'strike_rate': float(row['strike_rate']) if not pd.isna(row['strike_rate']) else 0.0,
                        'highest_score': 0,
                        'best_bowling': "",
                        'player_type': 'Batsman' if safe_convert(row['player_dismissed']) == 0 else 'Bowler'
                    })
            except Exception as e:
                print(f"Error saving player stats for {player_name}: {str(e)}")
                
            if idx % 100 == 0:
                print(f"Processed {idx + 1} player stats")
                
        except Exception as e:
            print(f"Error saving player stats for {row['batsman']}: {str(e)}")
            continue
    
    print("Player statistics updated successfully!")
    
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)
