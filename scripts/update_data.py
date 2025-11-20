import os
import json
import pandas as pd
from stravalib.client import Client
from datetime import datetime

DATA_PATH = 'data/activities.csv'
LEADERBOARD_PATH = 'data/leaderboards.json'

def get_client():
    client = Client()
    refresh_response = client.refresh_access_token(
        client_id=os.environ['STRAVA_CLIENT_ID'],
        client_secret=os.environ['STRAVA_CLIENT_SECRET'],
        refresh_token=os.environ['STRAVA_REFRESH_TOKEN']
    )
    client.access_token = refresh_response['access_token']
    return client

def update_activities():
    client = get_client()
    
    if os.path.exists(DATA_PATH):
        existing_df = pd.read_csv(DATA_PATH)
        existing_df['start_date'] = pd.to_datetime(existing_df['start_date'])
        last_date = existing_df['start_date'].max()
    else:
        existing_df = pd.DataFrame()
        last_date = None

    new_activities = []
    for act in client.get_activities(after=last_date):
        new_activities.append({
            'id': act.id,
            'name': act.name,
            'start_date': act.start_date_local,
            'distance_km': act.distance.num / 1000,
            'moving_time_min': act.moving_time.seconds / 60,
            'elevation_m': act.total_elevation_gain.num,
            'type': act.type,
            'average_speed_kmh': act.average_speed.num * 3.6,
            'pr_count': act.pr_count,
            'kudos': act.kudos_count
        })

    if new_activities:
        new_df = pd.DataFrame(new_activities)
        new_df['start_date'] = pd.to_datetime(new_df['start_date'])
        final_df = pd.concat([existing_df, new_df]).drop_duplicates(subset='id').sort_values('start_date', ascending=False)
        final_df.to_csv(DATA_PATH, index=False)
        return final_df
    return existing_df

def update_leaderboards(df):
    if df.empty: return
    
    client = get_client()
    leaderboard_data = []
    
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
        except:
            continue
            
    with open(LEADERBOARD_PATH, 'w') as f:
        json.dump(leaderboard_data, f)

if __name__ == "__main__":
    df = update_activities()
    update_leaderboards(df)
