from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pymongo
from django.conf import settings
from plotly.express import bar as px
from analysis.models import Match, Delivery, PlayerStats
import json
import pandas as pd
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

# MongoDB connection function
def get_mongodb_connection():
    try:
        print("Attempting MongoDB connection...")
        # Using a more robust connection string with timeout
        client = pymongo.MongoClient(
            'mongodb://127.0.0.1:27017',
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            socketTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        
        # Test connection
        try:
            client.server_info()  # Forces a connection
            print("MongoDB connection successful")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")
            raise
            
        db = client['ipl_analysis']
        
        # Test if database exists
        if 'ipl_analysis' not in client.list_database_names():
            print("Database 'ipl_analysis' does not exist")
            raise Exception("Database 'ipl_analysis' does not exist")
            
        # Test if any collections exist
        collections = db.list_collection_names()
        if not collections:
            print("No collections found in database")
            raise Exception("No collections found in database")
            
        print(f"Available collections: {collections}")
        return db
    except Exception as e:
        print(f"MongoDB connection error: {str(e)}")
        raise

def index(request):
    try:
        # Get MongoDB connection
        db = get_mongodb_connection()
        
        # Get all collections
        collections = db.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Check sample data in each collection
        collection_data = {}
        for collection_name in collections:
            try:
                sample = list(db[collection_name].find().limit(1))
                collection_data[collection_name] = {
                    'count': db[collection_name].count_documents({}),
                    'sample': sample[0] if sample else None
                }
            except Exception as e:
                collection_data[collection_name] = {'error': str(e)}
        
        return render(request, 'base.html', {
            'collections': collections,
            'connection_status': 'MongoDB connection successful'
        })
    except Exception as e:
        return render(request, 'base.html', {
            'error': str(e),
            'connection_status': 'MongoDB connection failed'
        })

def test_mongodb(request):
    try:
        # Get MongoDB connection
        db = get_mongodb_connection()
        
        # Get all collections
        collections = db.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Check sample data in each collection
        collection_data = {}
        for collection_name in collections:
            try:
                sample = list(db[collection_name].find().limit(1))
                if sample:
                    # Convert ObjectId to string for JSON serialization
                    sample[0]['_id'] = str(sample[0]['_id'])
                collection_data[collection_name] = {
                    'count': db[collection_name].count_documents({}),
                    'sample': sample[0] if sample else None
                }
            except Exception as e:
                collection_data[collection_name] = {'error': str(e)}
        
        return JsonResponse({
            'status': 'success',
            'collections': collections,
            'collection_data': collection_data,
            'message': 'MongoDB connection successful'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def search_player(request):
    if request.method == 'POST':
        try:
            # Get MongoDB connection
            db = get_mongodb_connection()
            
            # Get player name from request
            player_name = request.POST.get('player_name', '').strip()
            if not player_name:
                return JsonResponse({'error': 'Player name is required'}, status=400)

            print(f"Searching for player: {player_name}")
            
            # Search for player stats in both possible collections
            collections = ['playerstats', 'analysis_playerstats']
            player_stats = None
            
            for collection in collections:
                if collection in db.list_collection_names():
                    print(f"Searching in {collection} collection")
                    player_stats = db[collection].find_one({
                        'player_name': {'$regex': f".*{player_name}.*", '$options': 'i'}
                    })
                    if player_stats:
                        print(f"Found player stats: {player_stats}")
                        break

            if not player_stats:
                print(f"Player not found in any collection. Available collections: {db.list_collection_names()}")
                return JsonResponse({'error': 'Player not found'}, status=404)

            # Convert MongoDB document to dict and handle ObjectIds
            player_stats_dict = {}
            for key, value in player_stats.items():
                if key == '_id':
                    player_stats_dict[key] = str(value)
                elif isinstance(value, dict):
                    # Recursively handle nested dictionaries
                    player_stats_dict[key] = {
                        k: str(v) if k == '_id' else v
                        for k, v in value.items()
                    }
                else:
                    player_stats_dict[key] = value

            # Get deliveries for this player
            deliveries = list(db.deliveries.find({
                'batter': {'$regex': f".*{player_name}.*", '$options': 'i'}
            }))
            
            print(f"Found {len(deliveries)} deliveries for {player_name}")
            
            # Calculate total runs and dismissals
            total_runs = 0
            dismissals = 0
            
            for delivery in deliveries:
                runs = int(delivery.get('batsman_runs', 0))
                total_runs += runs
                
                # Check for dismissals
                if delivery.get('player_dismissed', '').lower() == player_name.lower():
                    dismissals += 1
            
            print(f"Total runs calculated: {total_runs}")
            print(f"Total dismissals: {dismissals}")
            
            # Calculate batting average
            batting_average = total_runs / dismissals if dismissals > 0 else 0
            print(f"Batting average: {batting_average}")
            
            # Calculate strike rate
            balls_faced = len(deliveries)
            strike_rate = (total_runs / balls_faced) * 100 if balls_faced > 0 else 0
            print(f"Strike rate: {strike_rate}")
            
            # Update player stats with calculated values
            player_stats_dict['total_runs'] = total_runs
            player_stats_dict['batting_average'] = round(batting_average, 2)
            player_stats_dict['strike_rate'] = round(strike_rate, 2)
            player_stats_dict['balls_faced'] = balls_faced
            
            # Get runs by season
            runs_by_season = get_runs_by_season(player_name)
            print(f"Runs by season data: {runs_by_season}")
            
            # Get wickets by season
            wickets_by_season = get_wickets_by_season(player_name)
            print(f"Wickets by season data: {wickets_by_season}")

            # Ensure data is in the correct format for charts
            runs_data = [{'season': item['season'], 'runs': item['runs']} for item in runs_by_season]
            wickets_data = [{'season': item['season'], 'wickets': item['wickets']} for item in wickets_by_season]
            
            print(f"Final runs data: {runs_data}")
            print(f"Final wickets data: {wickets_data}")

            return JsonResponse({
                'player_stats': player_stats_dict,
                'runs_by_season': runs_data,
                'wickets_by_season': wickets_data
            })
        except Exception as e:
            print(f"Error in search_player: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_runs_by_season(player_name):
    try:
        # Get MongoDB connection
        db = get_mongodb_connection()
        
        # Get deliveries collection
        deliveries = db.deliveries.find({
            'batter': {'$regex': f".*{player_name}.*", '$options': 'i'}
        })
        
        # Group by season and sum runs
        runs_by_season = {}
        
        # First get all unique seasons
        seasons = set()
        for delivery in deliveries:
            season = delivery.get('season', '')
            if season:
                seasons.add(season)
        
        # Initialize all seasons with 0 runs
        for season in seasons:
            runs_by_season[season] = 0
        
        # Now calculate runs for each season
        for delivery in deliveries:
            season = delivery.get('season', '')
            runs = int(delivery.get('batsman_runs', 0))
            
            if season in runs_by_season:
                runs_by_season[season] += runs
            
        # Convert to list of dicts for plotting
        result = []
        for season, runs in runs_by_season.items():
            result.append({
                'season': season,
                'runs': runs
            })
        
        # Sort by season
        result.sort(key=lambda x: x['season'])
        
        # Create a Plotly chart
        if result:
            df = pd.DataFrame(result)
            fig = px.bar(df, 
                        x='season', 
                        y='runs',
                        title=f'Runs by Season for {player_name}',
                        labels={'season': 'Season', 'runs': 'Runs'},
                        color_discrete_sequence=['#FF69B4'])  # Pink for runs
            
            # Add hover information
            fig.update_traces(hovertemplate='Season: %{x}<br>Runs: %{y}')
            
            # Add grid lines
            fig.update_layout(
                yaxis=dict(
                    gridcolor='rgba(150, 150, 150, 0.2)',
                    zerolinecolor='rgba(150, 150, 150, 0.2)'
                ),
                xaxis=dict(
                    gridcolor='rgba(150, 150, 150, 0.2)'
                ),
                # Add margins and padding
                margin=dict(l=50, r=50, t=80, b=50),
                # Add title font size
                title_font_size=16,
                # Add axis labels font size
                xaxis_title_font_size=12,
                yaxis_title_font_size=12
            )
            
            # Return the chart as JSON
            return json.loads(fig.to_json())
        
        return []
    except Exception as e:
        print(f"Error getting runs by season: {str(e)}")
        return []

def get_wickets_by_season(player_name):
    try:
        # Get MongoDB connection
        db = get_mongodb_connection()
        
        # Get deliveries collection
        deliveries = db.deliveries.find({
            'bowler': {'$regex': f".*{player_name}.*", '$options': 'i'},
            'dismissal_kind': {'$ne': 'run out'}  # Exclude run outs
        })
        
        # Group by season and count wickets
        wickets_by_season = {}
        
        # First get all unique seasons
        seasons = set()
        for delivery in deliveries:
            season = delivery.get('season', '')
            if season:
                seasons.add(season)
        
        # Initialize all seasons with 0 wickets
        for season in seasons:
            wickets_by_season[season] = 0
        
        # Now count wickets for each season
        for delivery in deliveries:
            season = delivery.get('season', '')
            if season in wickets_by_season:
                wickets_by_season[season] += 1
            
        # Convert to list of dicts for plotting
        result = []
        for season, wickets in wickets_by_season.items():
            result.append({
                'season': season,
                'wickets': wickets
            })
        
        # Sort by season
        result.sort(key=lambda x: x['season'])
        
        # Create a Plotly chart
        if result:
            df = pd.DataFrame(result)
            fig = px.bar(df, 
                        x='season', 
                        y='wickets',
                        title=f'Wickets by Season for {player_name}',
                        labels={'season': 'Season', 'wickets': 'Wickets'},
                        color_discrete_sequence=['#00BFFF'])  # Light blue for wickets
            
            # Add hover information
            fig.update_traces(hovertemplate='Season: %{x}<br>Wickets: %{y}')
            
            # Add grid lines
            fig.update_layout(
                yaxis=dict(
                    gridcolor='rgba(150, 150, 150, 0.2)',
                    zerolinecolor='rgba(150, 150, 150, 0.2)'
                ),
                xaxis=dict(
                    gridcolor='rgba(150, 150, 150, 0.2)'
                ),
                # Add margins and padding
                margin=dict(l=50, r=50, t=80, b=50),
                # Add title font size
                title_font_size=16,
                # Add axis labels font size
                xaxis_title_font_size=12,
                yaxis_title_font_size=12
            )
            
            # Return the chart as JSON
            return json.loads(fig.to_json())
        
        return []
    except Exception as e:
        print(f"Error getting wickets by season: {str(e)}")
        return []
