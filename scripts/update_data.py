import os
import json
import pandas as pd
from stravalib.client import Client

DATA_DIR = 'data'
ACTIVITIES_FILE = os.path.join(DATA_DIR, 'activities.csv')
LEADERBOARD_FILE = os.path.join(DATA_DIR, 'leaderboards.json')

def get_client():
    client = Client()
    refresh_response = client.refresh_access_token(
        client_id=os.environ['STRAVA_CLIENT_ID'],
        client_secret=os.environ['STRAVA_CLIENT_SECRET'],
        refresh_token=os.environ['STRAVA_REFRESH_TOKEN']
    )
    client.access_token = refresh_response['access_token']
    return client

def get_value(obj):
    if obj is None:
        return 0
    if hasattr(obj, 'magnitude'):
        return obj.magnitude
    if hasattr(obj, 'num'):
        return obj.num
    return float(obj)

def update_activities():
    os.makedirs(DATA_DIR, exist_ok=True)

    client = get_client()
    
    if os.path.exists(ACTIVITIES_FILE):
        existing_df = pd.read_csv(ACTIVITIES_FILE)
        existing_df['start_date'] = pd.to_datetime(existing_df['start_date'])
        last_date = existing_df['start_date'].max()
    else:
        existing_df = pd.DataFrame(columns=[
            'id', 'name', 'start_date', 'distance_km', 'moving_time_min', 
            'elevation_m', 'type', 'average_speed_kmh', 'pr_count', 'kudos'
        ])
        last_date = None

    new_activities = []
    try:
        activities = client.get_activities(after=last_date)
        for act in activities:
            try:
                new_activities.append({
                    'id': act.id,
                    'name': act.name,
                    'start_date': act.start_date_local,
                    'distance_km': get_value(act.distance) / 1000, 
                    'moving_time_min': act.moving_time.seconds / 60,
                    'elevation_m': get_value(act.total_elevation_gain),
                    'type': act.type,
                    'average_speed_kmh': get_value(act.average_speed) * 3.6,
                    'pr_count': act.pr_count,
                    'kudos': act.kudos_count
                })
            except Exception:
                continue
    except Exception:
        pass

    if new_activities:
        new_df = pd.DataFrame(new_activities)
        new_df['start_date'] = pd.to_datetime(new_df['start_date'])
        final_df = pd.concat([existing_df, new_df])
        final_df = final_df.drop_duplicates(subset='id', keep='last')
        final_df = final_df.sort_values('start_date', ascending=False)
    else:
        final_df = existing_df

    final_df.to_csv(ACTIVITIES_FILE, index=False)
    return final_df

def update_leaderboards(df):
    os.makedirs(DATA_DIR, exist_ok=True)
    
    leaderboard_data = []
    
    if not df.empty:
        client = get_client()
        recent_ids = df.head(5)['id'].tolist()
        
        for act_id in recent_ids:
            try:
                detail = client.get_activity(act_id, include_all_efforts=True)
                if detail.segment_efforts:
                    for effort in detail.segment_efforts:
                        rank = effort.kom_rank or effort.pr_rank
                        if rank and rank <= 10:
                            leaderboard_data.append({
                                'segment_name': effort.segment.name,
                                'rank': rank,
                                'date': detail.start_date_local.strftime('%Y-%m-%d'),
                                'time_str': str(effort.elapsed_time)
                            })
            except Exception:
                continue
            
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard_data, f)

if __name__ == "__main__":
    df = update_activities()
    update_leaderboards(df)
