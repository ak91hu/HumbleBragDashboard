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
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['year'] = df['start_date'].dt.year
    df['day_of_year'] = df['start_date'].dt.dayofyear
    df = df.sort_values('start_date')
    df['cumulative_km'] = df.groupby('year')['distance_km'].cumsum()
    
    lb_data = []
    if os.path.exists('data/leaderboards.json'):
        with open('data/leaderboards.json', 'r') as f:
            lb_data = json.load(f)
            
    return df, lb_data

df, lb_data = load_data()

st.title("🚴 Strava Performance Dashboard")

if df.empty:
    st.warning("Nincs adat. A robot még nem futott le.")
    st.stop()

# Sidebar
st.sidebar.header("Beállítások")
years = sorted(df['year'].unique())
selected_years = st.sidebar.multiselect("Évek összehasonlítása", years, default=years)
filtered_df = df[df['year'].isin(selected_years)]

# KPI
col1, col2, col3, col4 = st.columns(4)
col1.metric("Összes Táv", f"{filtered_df['distance_km'].sum():.0f} km")
col2.metric("Szintemelkedés", f"{filtered_df['elevation_m'].sum():.0f} m")
col3.metric("Edzések száma", len(filtered_df))
col4.metric("PR-ok száma", filtered_df['pr_count'].sum())

# Charts
st.subheader("Éves összehasonlítás (Kumulatív)")
fig_line = px.line(filtered_df, x='day_of_year', y='cumulative_km', color='year', 
                   labels={'cumulative_km': 'Km', 'day_of_year': 'Nap'},
                   color_discrete_sequence=px.colors.qualitative.Bold)
st.plotly_chart(fig_line, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("Távolság eloszlás")
    fig_hist = px.histogram(filtered_df, x="distance_km", nbins=20)
    st.plotly_chart(fig_hist, use_container_width=True)
with c2:
    st.subheader("Sebesség vs Táv")
    fig_scatter = px.scatter(filtered_df, x="distance_km", y="average_speed_kmh", 
                             size="elevation_m", color="year")
    st.plotly_chart(fig_scatter, use_container_width=True)

# Leaderboard
st.subheader("🏆 Legutóbbi Top helyezések")
if lb_data:
    lb_cols = st.columns(3)
    for i, item in enumerate(lb_data[:6]):
        with lb_cols[i % 3]:
            st.success(f"**{item['segment_name']}**\n\n#{item['rank']} helyezés ({item['time_str']})")
else:
    st.info("Nincs top helyezés az utóbbi edzéseken.")
