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

def get_safe_value(obj):
    if obj is None: return 0
    if hasattr(obj, 'total_seconds'): return obj.total_seconds()
    if hasattr(obj, 'magnitude'): return obj.magnitude
    if hasattr(obj, 'num'): return obj.num
    if hasattr(obj, 'seconds'): return obj.seconds
    return float(obj)

def update_activities():
    os.makedirs(DATA_DIR, exist_ok=True)
    print("🚀 --- HARD RESET: KEZDŐDIK ---")
    
    if os.path.exists(ACTIVITIES_FILE):
        print(f"⚠️  Régi fájl törlése: {ACTIVITIES_FILE}")
        os.remove(ACTIVITIES_FILE)
    
    client = get_client()
    new_activities = []
    
    print("⏳ Strava adatok letöltése folyamatban...")
    
    activity_generator = client.get_activities(limit=None)
    
    count = 0
    try:
        for act in activity_generator:
            try:
                data = {
                    'id': act.id,
                    'name': act.name,
                    'start_date': act.start_date_local,
                    'distance_km': get_safe_value(act.distance) / 1000, 
                    'moving_time_min': get_safe_value(act.moving_time) / 60,
                    'elevation_m': get_safe_value(act.total_elevation_gain),
                    'type': act.type,
                    'average_speed_kmh': get_safe_value(act.average_speed) * 3.6,
                    'pr_count': act.pr_count,
                    'kudos': act.kudos_count
                }
                new_activities.append(data)
                count += 1
                
                if count % 50 == 0:
                    print(f"✅ Feldolgozva: {count} db...")
                    
            except Exception as inner_e:
                print(f"❌ Hiba ennél az ID-nél ({act.id}): {inner_e}")
                continue
                
    except Exception as e:
        print(f"🔥 FŐ HIBA a letöltés közben: {e}")
    
    print(f"🏁 Összesen {count} edzés letöltve.")

    if new_activities:
        final_df = pd.DataFrame(new_activities)
        final_df['start_date'] = pd.to_datetime(final_df['start_date'])
        final_df = final_df.sort_values('start_date', ascending=False)
        
        final_df.to_csv(ACTIVITIES_FILE, index=False)
        print(f"💾 Mentve. Sorok száma: {len(final_df)}")
        return final_df
    else:
        print("⚠️ Üres válasz vagy hiba. Üres fájl létrehozása.")
        empty = pd.DataFrame(columns=['id', 'name', 'start_date', 'distance_km', 'elevation_m', 'average_speed_kmh', 'pr_count'])
        empty.to_csv(ACTIVITIES_FILE, index=False)
        return empty

def update_leaderboards(df):
    print("⏩ Leaderboard frissítés kihagyva.")
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump([], f)

if __name__ == "__main__":
    df = update_activities()
    update_leaderboards(df)
