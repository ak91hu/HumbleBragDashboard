import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Humblebrag Dashboard", layout="wide", page_icon="🏃", initial_sidebar_state="expanded")

@st.cache_data
def load_data():
    if not os.path.exists('data/activities.csv'): return pd.DataFrame()
    df = pd.read_csv('data/activities.csv')
    if df.empty: return pd.DataFrame()

    num_cols = ['distance_km', 'elevation_m', 'average_speed_kmh', 'pr_count', 'moving_time_min', 'kudos', 'max_heartrate', 'average_heartrate']
    for col in num_cols:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'type' in df.columns:
        df['type'] = df['type'].astype(str).str.replace(r'root=', '', regex=False).str.strip()
        df['type'] = df['type'].apply(lambda x: x.split('=')[-1].replace('>', '') if '=' in x else x)

    df['start_date'] = pd.to_datetime(df['start_date'])
    df['year'] = df['start_date'].dt.year
    df['month_name'] = df['start_date'].dt.month_name()
    df['month'] = df['start_date'].dt.month
    df['week'] = df['start_date'].dt.isocalendar().week
    df['day_of_year'] = df['start_date'].dt.dayofyear
    df['day_name'] = df['start_date'].dt.day_name()
    df['hour'] = df['start_date'].dt.hour
    
    df = df.sort_values('start_date')
    df['cumulative_km'] = df.groupby('year')['distance_km'].cumsum()
    df['cumulative_elev'] = df.groupby('year')['elevation_m'].cumsum()
    
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
k3.metric("Össz Idő", f"{filtered['moving_time_min'].sum()/60:,.0f} óra")
k4.metric("Aktív Napok", f"{filtered['start_date'].dt.date.nunique()} nap")
k5.metric("Széria (Max)", f"{max_streak} nap")

st.divider()

t1, t2, t3, t4, t5 = st.tabs(["📈 Trendek", "📅 Havi Mátrix", "⚡ Intenzitás", "🏆 Rekordok", "🗺️ Időbeli"])

with t1:
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_cum = px.line(filtered, x='day_of_year', y='cumulative_km', color='year', title="Kumulatív KM",
                          color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig_cum, use_container_width=True)
    with c2:
        yearly_stats = filtered.groupby('year').agg({'distance_km': 'sum', 'elevation_m': 'sum', 'id': 'count'}).reset_index()
        yearly_stats.columns = ['Év', 'Km', 'Szint', 'Edzés db']
        yearly_stats['Km/Edzés'] = yearly_stats['Km'] / yearly_stats['Edzés db']
        st.dataframe(yearly_stats.style.format("{:.1f}"), use_container_width=True, hide_index=True)

    daily_vol = filtered.groupby('start_date')['distance_km'].sum().asfreq('D', fill_value=0)
    rolling_avg = daily_vol.rolling(window=30).mean().reset_index()
    fig_roll = px.area(rolling_avg, x='start_date', y='distance_km', title="30 napos mozgóátlag terhelés")
    st.plotly_chart(fig_roll, use_container_width=True)

with t2:
    c1, c2 = st.columns(2)
    with c1:
        monthly = filtered.groupby(['year', 'month'])['distance_km'].sum().reset_index()
        fig_mon = px.bar(monthly, x='month', y='distance_km', color='year', barmode='group', title="Havi Összesítő")
        st.plotly_chart(fig_mon, use_container_width=True)
    with c2:
        weekly = filtered.groupby(['year', 'week'])['distance_km'].sum().reset_index()
        fig_week = px.scatter(weekly, x='week', y='distance_km', color='year', size='distance_km', title="Heti volumen")
        st.plotly_chart(fig_week, use_container_width=True)

    piv = filtered.pivot_table(index='year', columns='month', values='distance_km', aggfunc='sum', fill_value=0)
    st.write("Havi kilométer mátrix:")
    try:
        st.dataframe(piv.style.background_gradient(cmap="Greens", axis=None).format("{:.0f}"), use_container_width=True)
    except ImportError:
        st.dataframe(piv.style.format("{:.0f}"), use_container_width=True)
    except Exception:
        st.dataframe(piv, use_container_width=True)

with t3:
    c1, c2 = st.columns(2)
    with c1:
        fig_dist = px.histogram(filtered, x="distance_km", nbins=40, color="type", marginal="box", title="Távolság eloszlás")
        st.plotly_chart(fig_dist, use_container_width=True)
    with c2:
        fig_bubble = px.scatter(filtered, x="distance_km", y="average_speed_kmh", size="elevation_m", color="type", 
                                title="Teljesítmény Buborékok (Méret = Szint)")
        st.plotly_chart(fig_bubble, use_container_width=True)

    if 'average_heartrate' in filtered.columns and filtered['average_heartrate'].sum() > 0:
        fig_hr = px.scatter(filtered[filtered['average_heartrate'] > 0], x='average_speed_kmh', y='average_heartrate', color='type', title="Pulzus vs Sebesség")
        st.plotly_chart(fig_hr, use_container_width=True)

with t4:
    c1, c2, c3, c4 = st.columns(4)
    if not filtered.empty:
        c1.metric("Leghosszabb", f"{filtered['distance_km'].max():.1f} km")
        c2.metric("Legtöbb Szint", f"{filtered['elevation_m'].max():.0f} m")
        c3.metric("Leggyorsabb", f"{filtered[filtered['distance_km']>5]['average_speed_kmh'].max():.1f} km/h")
        c4.metric("Legtöbb Kudos", f"{filtered['kudos'].max()}")

        st.subheader("Top 10 Edzés (Táv alapján)")
        top10 = filtered.nlargest(10, 'distance_km')[['start_date', 'name', 'type', 'distance_km', 'moving_time_min', 'elevation_m', 'average_speed_kmh']]
        st.dataframe(top10, use_container_width=True)

with t5:
    c1, c2 = st.columns(2)
    with c1:
        day_counts = filtered['day_name'].value_counts()
        fig_pie = px.pie(values=day_counts.values, names=day_counts.index, title="Melyik napon edzel?")
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        fig_hour = px.bar(filtered['hour'].value_counts().sort_index(), title="Edzés kezdés időpontja (óra)")
        st.plotly_chart(fig_hour, use_container_width=True)
