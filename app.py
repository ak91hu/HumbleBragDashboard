import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Humblebrag Dashboard", layout="wide", page_icon="🔥", initial_sidebar_state="expanded")

@st.cache_data
def load_data():
    if not os.path.exists('data/activities.csv'): return pd.DataFrame()
    df = pd.read_csv('data/activities.csv')
    if df.empty: return pd.DataFrame()

    num_cols = ['distance_km', 'elevation_m', 'average_speed_kmh', 'pr_count', 'moving_time_min', 'kudos', 'kilojoules']
    for col in num_cols:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'type' in df.columns:
        df['type'] = df['type'].astype(str).str.replace(r'root=', '', regex=False).str.strip()
        df['type'] = df['type'].apply(lambda x: x.split('=')[-1].replace('>', '') if '=' in x else x)

    # Időzóna javítás (tz-naive)
    df['start_date'] = pd.to_datetime(df['start_date'], utc=True).dt.tz_localize(None)
    
    df['year'] = df['start_date'].dt.year
    df['month_name'] = df['start_date'].dt.month_name()
    df['week'] = df['start_date'].dt.isocalendar().week
    df['day_of_year'] = df['start_date'].dt.dayofyear
    df['day_name'] = df['start_date'].dt.day_name()
    df['day_of_week'] = df['start_date'].dt.dayofweek 
    df['hour'] = df['start_date'].dt.hour
    
    if 'kilojoules' not in df.columns: df['kilojoules'] = 0
    def estimate_calories(row):
        if row['kilojoules'] > 0: return row['kilojoules']
        if row['type'] == 'Run': return row['distance_km'] * 75
        if row['type'] == 'Ride': return row['distance_km'] * 25
        return row['distance_km'] * 40
    
    df['calories'] = df.apply(estimate_calories, axis=1)
    df = df.sort_values('start_date')
    df['cumulative_km'] = df.groupby('year')['distance_km'].cumsum()
    
    return df

def calculate_streaks(df):
    if df.empty: return 0, 0
    dates = df['start_date'].dt.date.sort_values().unique()
    if len(dates) < 2: return 1, 1
    current_streak = 1
    max_streak = 1
    prev = dates[0]
    for d in dates[1:]:
        if (d - prev).days == 1:
            current_streak += 1
        else:
            max_streak = max(max_streak, current_streak)
            current_streak = 1
        prev = d
    return max(max_streak, current_streak), current_streak

df = load_data()

if df.empty:
    st.error("Nincs adat. Ellenőrizd a GitHub Actiont.")
    st.stop()

st.sidebar.title("🔍 Szűrők")
years = sorted(df['year'].unique(), reverse=True)
sel_years = st.sidebar.multiselect("Évek", years, default=years) 
st.sidebar.divider()
types = sorted(df['type'].unique())
sel_types = st.sidebar.multiselect("Mozgásforma", types, default=types)

if not sel_years: sel_years = years
if not sel_types: sel_types = types

filtered = df[df['year'].isin(sel_years) & df['type'].isin(sel_types)]

st.title(f"📊 Humblebrag Dashboard {min(sel_years)}-{max(sel_years)}")
k1, k2, k3, k4, k5 = st.columns(5)
max_streak, cur_streak = calculate_streaks(filtered)

k1.metric("Össz Táv", f"{filtered['distance_km'].sum():,.0f} km".replace(",", " "))
k2.metric("Össz Szint", f"{filtered['elevation_m'].sum():,.0f} m".replace(",", " "))
k3.metric("Kalória", f"{filtered['calories'].sum():,.0f} kcal".replace(",", " "))
k4.metric("Aktív Napok", f"{filtered['start_date'].dt.date.nunique()} nap")
k5.metric("Max Széria", f"{max_streak} nap")

st.divider()

# Fülek definiálása (Az első az új Napló)
t_log, t1, t2, t3, t4, t5 = st.tabs(["📋 Napló", "📈 Trendek", "🏔️ Kihívások", "📅 Heatmap", "🏆 Rekordok", "🗺️ Időbeli"])

# --- ÚJ SZEKCIÓ: UTOLSÓ 10 AKTIVITÁS ---
with t_log:
    st.subheader("Legutóbbi 10 aktivitás")
    
    # Adatok előkészítése: sorrend megfordítása (legújabb felül) és top 10
    last_10 = filtered.sort_values('start_date', ascending=False).head(10).copy()
    
    # Strava link generálása
    last_10['link'] = "https://www.strava.com/activities/" + last_10['id'].astype(str)
    
    # Oszlopok átnevezése a szép megjelenítéshez
    display_cols = {
        'start_date': 'Dátum',
        'name': 'Név',
        'type': 'Típus',
        'distance_km': 'Táv (km)',
        'elevation_m': 'Szint (m)',
        'moving_time_min': 'Idő (perc)',
        'average_speed_kmh': 'Tempó (km/h)',
        'kudos': 'Kudos',
        'link': 'Link'
    }
    
    # Csak a szükséges oszlopok
    display_df = last_10[display_cols.keys()].rename(columns=display_cols)
    
    st.dataframe(
        display_df,
        column_config={
            "Link": st.column_config.LinkColumn("Strava", display_text="Megnyitás"),
            "Dátum": st.column_config.DatetimeColumn(format="YYYY.MM.DD HH:mm"),
            "Táv (km)": st.column_config.NumberColumn(format="%.1f km"),
            "Szint (m)": st.column_config.NumberColumn(format="%d m"),
            "Tempó (km/h)": st.column_config.NumberColumn(format="%.1f km/h"),
            "Idő (perc)": st.column_config.NumberColumn(format="%d p"),
        },
        use_container_width=True,
        hide_index=True
    )

with t1:
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_cum = px.line(filtered, x='day_of_year', y='cumulative_km', color='year', title="Kumulatív KM verseny",
                          color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig_cum, use_container_width=True)
    with c2:
        yearly = filtered.groupby('year').agg({'distance_km': 'sum', 'elevation_m': 'sum', 'calories': 'sum'}).reset_index()
        st.write("Éves összesítő:")
        st.dataframe(yearly.style.format("{:.0f}").background_gradient(cmap="Blues"), use_container_width=True, hide_index=True)

with t2:
    st.subheader("🏔️ Hegymászó Kihívás")
    total_elev = filtered['elevation_m'].sum()
    kekesteto = 1014
    everest = 8848
    
    c1, c2 = st.columns(2)
    with c1:
        k_count = total_elev / kekesteto
        st.write(f"🇭🇺 **Kékes-tető (1014m)**")
        st.progress(min(1.0, (total_elev % kekesteto) / kekesteto))
        st.caption(f"{k_count:.1f}x másztad meg eddig!")

    with c2:
        e_count = total_elev / everest
        st.write(f"🗻 **Mount Everest (8848m)**")
        st.progress(min(1.0, (total_elev % everest) / everest))
        st.caption(f"{e_count:.2f}x másztad meg eddig!")

    st.divider()
    st.subheader("🍔 Gasztró Konverzió")
    total_cal = filtered['calories'].sum()
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("🍕 Pizza", f"{total_cal / 285:,.0f} szelet")
    g2.metric("🍺 Sör", f"{total_cal / 215:,.0f} korsó")
    g3.metric("🍔 Burger", f"{total_cal / 550:,.0f} db")
    g4.metric("🍩 Fánk", f"{total_cal / 250:,.0f} db")

with t3:
    st.subheader("📅 Aktivitási Heatmap (GitHub Stílus)")
    for year in sorted(filtered['year'].unique(), reverse=True):
        st.markdown(f"### {year}")
        df_year = filtered[filtered['year'] == year].copy()
        if df_year.empty: continue
        
        full_range = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31')
        daily_data = df_year.set_index('start_date')['distance_km'].resample('D').sum().reindex(full_range, fill_value=0).to_frame()
        
        daily_data['week'] = daily_data.index.isocalendar().week
        daily_data['day_of_week'] = daily_data.index.dayofweek
        
        heatmap_data = daily_data.pivot_table(index='day_of_week', columns='week', values='distance_km', fill_value=0)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        fig_cal = px.imshow(
            heatmap_data,
            labels=dict(x="Hét", y="Nap", color="Km"),
            y=days,
            color_continuous_scale=[(0, "#ebedf0"), (0.01, "#9be9a8"), (0.5, "#30a14e"), (1, "#216e39")],
            aspect="equal"
        )
        fig_cal.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis={'showgrid': False, 'zeroline': False},
            yaxis={'showgrid': False, 'zeroline': False},
            height=250
        )
        st.plotly_chart(fig_cal, use_container_width=True)

with t4:
    c1, c2, c3, c4 = st.columns(4)
    if not filtered.empty:
        c1.metric("Leghosszabb", f"{filtered['distance_km'].max():.1f} km")
        c2.metric("Legtöbb Szint", f"{filtered['elevation_m'].max():.0f} m")
        c3.metric("Leggyorsabb", f"{filtered[filtered['distance_km']>5]['average_speed_kmh'].max():.1f} km/h")
        c4.metric("Legtöbb Kudos", f"{filtered['kudos'].max()}")

        st.subheader("Top 10 Edzés")
        top10 = filtered.nlargest(10, 'distance_km')[['start_date', 'name', 'type', 'distance_km', 'elevation_m', 'average_speed_kmh']]
        st.dataframe(top10, use_container_width=True)

with t5:
    c1, c2 = st.columns(2)
    with c1:
        day_counts = filtered['day_name'].value_counts()
        fig_pie = px.pie(values=day_counts.values, names=day_counts.index, title="Melyik napon edzel?")
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        fig_hour = px.bar(filtered['hour'].value_counts().sort_index(), title="Edzés kezdés (óra)")
        st.plotly_chart(fig_hour, use_container_width=True)
