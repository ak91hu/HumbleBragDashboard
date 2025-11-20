import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Strava Analytics", layout="wide", page_icon="🏃")

@st.cache_data
def load_data():
    if not os.path.exists('data/activities.csv'):
        return pd.DataFrame(), []
        
    df = pd.read_csv('data/activities.csv')

    if df.empty:
        return pd.DataFrame(), []

    df['distance_km'] = pd.to_numeric(df['distance_km'], errors='coerce').fillna(0)
    df['elevation_m'] = pd.to_numeric(df['elevation_m'], errors='coerce').fillna(0)
    df['average_speed_kmh'] = pd.to_numeric(df['average_speed_kmh'], errors='coerce').fillna(0)
    df['pr_count'] = pd.to_numeric(df['pr_count'], errors='coerce').fillna(0)

    df['start_date'] = pd.to_datetime(df['start_date'])
    df['year'] = df['start_date'].dt.year
    df['day_of_year'] = df['start_date'].dt.dayofyear
    df = df.sort_values('start_date')
    
    df['cumulative_km'] = df.groupby('year')['distance_km'].cumsum()
    
    lb_data = []
    if os.path.exists('data/leaderboards.json'):
        try:
            with open('data/leaderboards.json', 'r') as f:
                lb_data = json.load(f)
        except:
            lb_data = []
            
    return df, lb_data

df, lb_data = load_data()

st.title("🚴 Strava Performance Dashboard")

if df.empty:
    st.warning("Az adatbázis létrejött, de még üres. Fuss egy kört, vagy várj a következő szinkronizálásra!")
    st.stop()

st.sidebar.header("Beállítások")
years = sorted(df['year'].unique())
selected_years = st.sidebar.multiselect("Évek összehasonlítása", years, default=years)

if not selected_years:
    filtered_df = df
else:
    filtered_df = df[df['year'].isin(selected_years)]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Összes Táv", f"{filtered_df['distance_km'].sum():.0f} km")
col2.metric("Szintemelkedés", f"{filtered_df['elevation_m'].sum():.0f} m")
col3.metric("Edzések száma", len(filtered_df))
col4.metric("PR-ok száma", int(filtered_df['pr_count'].sum()))

st.subheader("Éves összehasonlítás (Kumulatív)")
if not filtered_df.empty:
    fig_line = px.line(filtered_df, x='day_of_year', y='cumulative_km', color='year', 
                       labels={'cumulative_km': 'Km', 'day_of_year': 'Nap', 'year': 'Év'},
                       color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig_line, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("Távolság eloszlás")
    if not filtered_df.empty:
        fig_hist = px.histogram(filtered_df, x="distance_km", nbins=20)
        st.plotly_chart(fig_hist, use_container_width=True)
with c2:
    st.subheader("Sebesség vs Táv")
    if not filtered_df.empty:
        fig_scatter = px.scatter(filtered_df, x="distance_km", y="average_speed_kmh", 
                                 size="elevation_m", color="year")
        st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("🏆 Legutóbbi Top Helyezések")
if lb_data:
    lb_cols = st.columns(3)
    for i, item in enumerate(lb_data[:6]):
        with lb_cols[i % 3]:
            st.success(f"**{item['segment_name']}**\n\n#{item['rank']} helyezés ({item['time_str']})")
else:
    st.info("Nincs top helyezés az utóbbi edzéseken.")
