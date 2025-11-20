import os
import json
import pandas as pd
import time
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
    if obj is None: return 0
    if hasattr(obj, 'magnitude'): return obj.magnitude
    if hasattr(obj, 'num'): return obj.num
    return float(obj)

def update_activities():
    os.makedirs(DATA_DIR, exist_ok=True)
    print("🚀 --- TELJES ADATLETÖLTÉS INDÍTÁSA (HARD RESET) ---")
    
    # 1. LÉPÉS: Töröljük a régi fájlt, hogy biztosan mindent leszedjen
    if os.path.exists(ACTIVITIES_FILE):
        print(f"⚠️  Régi adatbázis törlése: {ACTIVITIES_FILE}")
        os.remove(ACTIVITIES_FILE)
    
    client = get_client()
    new_activities = []
    
    print("⏳ Kapcsolódás a Stravához és adatok letöltése... (Ez eltarthat egy ideig)")
    
    # Nincs 'after' paraméter = az idők kezdetétől töltünk le
    # limit=None = nincs korlát, mindent kérünk
    activity_generator = client.get_activities(limit=None)
    
    count = 0
    try:
        for act in activity_generator:
            try:
                # Egyszerűsített adatkinyerés
                data = {
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
                }
                new_activities.append(data)
                count += 1
                
                # Visszajelzés minden 50. edzésnél a logba
                if count % 50 == 0:
                    print(f"✅ Feldolgozva: {count} edzés... (Legutóbbi: {act.start_date_local.date()})")
                    
            except Exception as inner_e:
                print(f"❌ Hiba egy adott edzésnél ({act.id}): {inner_e}")
                continue
                
    except Exception as e:
        print(f"🔥 KRITIKUS HIBA a letöltés közben: {e}")
        # Ha itt megáll, akkor is mentsük el, amit eddig sikerült
    
    print(f"🏁 Összesen {count} edzés letöltve.")

    if new_activities:
        final_df = pd.DataFrame(new_activities)
        final_df['start_date'] = pd.to_datetime(final_df['start_date'])
        final_df = final_df.sort_values('start_date', ascending=False)
        
        final_df.to_csv(ACTIVITIES_FILE, index=False)
        print(f"💾 Adatok sikeresen mentve ide: {ACTIVITIES_FILE}")
        print(f"📊 Adatbázis mérete: {len(final_df)} sor")
        return final_df
    else:
        print("⚠️ Nem találtam letölthető edzést. Ellenőrizd a Strava fiókodat vagy a jogosultságokat!")
        # Üres fájl létrehozása, hogy ne legyen hiba
        empty = pd.DataFrame(columns=['id', 'name', 'start_date', 'distance_km', 'elevation_m', 'average_speed_kmh', 'pr_count'])
        empty.to_csv(ACTIVITIES_FILE, index=False)
        return empty

def update_leaderboards(df):
    # Ezt most kikapcsoljuk vagy minimalizáljuk, hogy először az alap adatok meglegyenek
    # A leaderboard lekérdezés nagyon lassú és hamar eléri a limitet
    print("⏩ Leaderboard frissítés kihagyása a gyorsabb első futtatás érdekében.")
    
    # Üres JSON létrehozása, hogy ne sírjon az app
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump([], f)

if __name__ == "__main__":
    df = update_activities()
    update_leaderboards(df)
