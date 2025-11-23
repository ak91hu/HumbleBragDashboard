import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Humblebrag Dashboard", layout="wide", page_icon="🔥", initial_sidebar_state="expanded")

TRANSLATIONS = {
    'HU': {
        'sidebar_title': "🔍 Szűrők",
        'lang_sel': "Nyelv / Language",
        'years': "Évek",
        'types': "Mozgásforma",
        'page_title': "📊 Humblebrag Dashboard",
        'kpi_dist': "Össz Táv",
        'kpi_elev': "Össz Szint",
        'kpi_cal': "Kalória",
        'kpi_days': "Aktív Napok",
        'kpi_streak': "Max Széria",
        'tab_log': "📋 Napló",
        'tab_trends': "📈 Trendek",
        'tab_challenges': "🏔️ Kihívások",
        'tab_heatmap': "📅 Heatmap",
        'tab_records': "🏆 Rekordok",
        'tab_time': "🗺️ Időbeli",
        'log_title': "Legutóbbi 10 aktivitás",
        'col_date': "Dátum",
        'col_name': "Név",
        'col_type': "Típus",
        'col_dist': "Táv (km)",
        'col_elev': "Szint (m)",
        'col_time': "Idő (perc)",
        'col_pace': "Tempó (km/h)",
        'open_link': "Megnyitás",
        'chart_cum_title': "Kumulatív KM verseny",
        'table_yearly_title': "Éves összesítő",
        'chal_mountain': "🏔️ Hegymászó Kihívás",
        'chal_gastro': "🍔 Gasztró Konverzió",
        'chal_kekes': "🇭🇺 Kékes-tető (1014m)",
        'chal_everest': "🗻 Mount Everest (8848m)",
        'climbed_msg': "x másztad meg eddig!",
        'pizza': "🍕 Pizza (szelet)",
        'beer': "🍺 Sör (korsó)",
        'burger': "🍔 Burger (db)",
        'donut': "🍩 Fánk (db)",
        'heat_title': "📅 Aktivitási Heatmap (GitHub Stílus)",
        'rec_longest': "Leghosszabb",
        'rec_highest': "Legtöbb Szint",
        'rec_fastest': "Leggyorsabb (5km+)",
        'rec_kudos': "Legtöbb Kudos",
        'rec_top10': "Top 10 Edzés (Táv)",
        'time_pie': "Melyik napon edzel?",
        'time_bar': "Edzés kezdés (óra)",
        'error_nodata': "Nincs adat. Ellenőrizd a GitHub Actiont.",
        'footer': "Made with ❤️ by Akos"
    },
    'EN': {
        'sidebar_title': "🔍 Filters",
        'lang_sel': "Language / Nyelv",
        'years': "Years",
        'types': "Activity Type",
        'page_title': "📊 Humblebrag Dashboard",
        'kpi_dist': "Total Dist",
        'kpi_elev': "Total Elev",
        'kpi_cal': "Calories",
        'kpi_days': "Active Days",
        'kpi_streak': "Max Streak",
        'tab_log': "📋 Log",
        'tab_trends': "📈 Trends",
        'tab_challenges': "🏔️ Challenges",
        'tab_heatmap': "📅 Heatmap",
        'tab_records': "🏆 Records",
        'tab_time': "🗺️ Timing",
        'log_title': "Last 10 Activities",
        'col_date': "Date",
        'col_name': "Name",
        'col_type': "Type",
        'col_dist': "Dist (km)",
        'col_elev': "Elev (m)",
        'col_time': "Time (min)",
        'col_pace': "Pace (km/h)",
        'open_link': "Open",
        'chart_cum_title': "Cumulative KM Race",
        'table_yearly_title': "Yearly Summary",
        'chal_mountain': "🏔️ Climbing Challenge",
        'chal_gastro': "🍔 Gastro Conversion",
        'chal_kekes': "🇭🇺 Kekes Peak (1014m)",
        'chal_everest': "🗻 Mount Everest (8848m)",
        'climbed_msg': "x climbed so far!",
        'pizza': "🍕 Pizza (slice)",
        'beer': "🍺 Beer (pint)",
        'burger': "🍔 Burger (pc)",
        'donut': "🍩 Donut (pc)",
        'heat_title': "📅 Activity Heatmap (GitHub Style)",
        'rec_longest': "Longest",
        'rec_highest': "Highest Elev",
        'rec_fastest': "Fastest (5km+)",
        'rec_kudos': "Most Kudos",
        'rec_top10': "Top 10 Activities (Dist)",
        'time_pie': "Which days are you active?",
        'time_bar': "Start Hour Distribution",
        'error_nodata': "No data found. Check GitHub Actions.",
        'footer': "Made with ❤️ by Akos"
    }
}

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

lang_option = st.sidebar.radio("🌐 Language / Nyelv", ["🇬🇧 English", "🇭🇺 Magyar"])
lang = 'EN' if "English" in lang_option else 'HU'
T = TRANSLATIONS[lang]

if df.empty:
    st.error(T['error_nodata'])
    st.stop()

st.sidebar.title(T['sidebar_title'])
years = sorted(df['year'].unique(), reverse=True)
sel_years = st.sidebar.multiselect(T['years'], years, default=years) 
st.sidebar.divider()
types = sorted(df['type'].unique())
sel_types = st.sidebar.multiselect(T['types'], types, default=types)

if not sel_years: sel_years = years
if not sel_types: sel_types = types

filtered = df[df['year'].isin(sel_years) & df['type'].isin(sel_types)]

st.title(f"{T['page_title']} {min(sel_years)}-{max(sel_years)}")
k1, k2, k3, k4, k5 = st.columns(5)
max_streak, cur_streak = calculate_streaks(filtered)

k1.metric(T['kpi_dist'], f"{filtered['distance_km'].sum():,.0f} km".replace(",", " "))
k2.metric(T['kpi_elev'], f"{filtered['elevation_m'].sum():,.0f} m".replace(",", " "))
k3.metric(T['kpi_cal'], f"{filtered['calories'].sum():,.0f} kcal".replace(",", " "))
k4.metric(T['kpi_days'], f"{filtered['start_date'].dt.date.nunique()}")
k5.metric(T['kpi_streak'], f"{max_streak}")

st.divider()

t_log, t1, t2, t3, t4, t5 = st.tabs([T['tab_log'], T['tab_trends'], T['tab_challenges'], T['tab_heatmap'], T['tab_records'], T['tab_time']])

with t_log:
    st.subheader(T['log_title'])
    last_10 = filtered.sort_values('start_date', ascending=False).head(10).copy()
    last_10['link'] = "https://www.strava.com/activities/" + last_10['id'].astype(str)
    
    display_cols = {
        'start_date': T['col_date'],
        'name': T['col_name'],
        'type': T['col_type'],
        'distance_km': T['col_dist'],
        'elevation_m': T['col_elev'],
        'moving_time_min': T['col_time'],
        'average_speed_kmh': T['col_pace'],
        'link': 'Link'
    }
    display_df = last_10[display_cols.keys()].rename(columns=display_cols)
    
    st.dataframe(
        display_df,
        column_config={
            "Link": st.column_config.LinkColumn("Strava", display_text=T['open_link']),
            T['col_date']: st.column_config.DatetimeColumn(format="YYYY.MM.DD HH:mm"),
            T['col_dist']: st.column_config.NumberColumn(format="%.1f km"),
            T['col_elev']: st.column_config.NumberColumn(format="%d m"),
            T['col_pace']: st.column_config.NumberColumn(format="%.1f km/h"),
            T['col_time']: st.column_config.NumberColumn(format="%d p"),
        },
        use_container_width=True,
        hide_index=True
    )

with t1:
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_cum = px.line(filtered, x='day_of_year', y='cumulative_km', color='year', title=T['chart_cum_title'],
                          color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig_cum, use_container_width=True)
    with c2:
        yearly = filtered.groupby('year').agg({'distance_km': 'sum', 'elevation_m': 'sum', 'calories': 'sum'}).reset_index()
        st.write(T['table_yearly_title'])
        st.dataframe(yearly.style.format("{:.0f}").background_gradient(cmap="Blues"), use_container_width=True, hide_index=True)

with t2:
    st.subheader(T['chal_mountain'])
    total_elev = filtered['elevation_m'].sum()
    kekesteto = 1014
    everest = 8848
    
    c1, c2 = st.columns(2)
    with c1:
        k_count = total_elev / kekesteto
        st.write(f"**{T['chal_kekes']}**")
        st.progress(min(1.0, (total_elev % kekesteto) / kekesteto))
        st.caption(f"{k_count:.1f}{T['climbed_msg']}")

    with c2:
        e_count = total_elev / everest
        st.write(f"**{T['chal_everest']}**")
        st.progress(min(1.0, (total_elev % everest) / everest))
        st.caption(f"{e_count:.2f}{T['climbed_msg']}")

    st.divider()
    st.subheader(T['chal_gastro'])
    total_cal = filtered['calories'].sum()
    g1, g2, g3, g4 = st.columns(4)
    g1.metric(T['pizza'], f"{total_cal / 285:,.0f}")
    g2.metric(T['beer'], f"{total_cal / 215:,.0f}")
    g3.metric(T['burger'], f"{total_cal / 550:,.0f}")
    g4.metric(T['donut'], f"{total_cal / 250:,.0f}")

with t3:
    st.subheader(T['heat_title'])
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
            labels=dict(x="Week", y="Day", color="Km"),
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
        c1.metric(T['rec_longest'], f"{filtered['distance_km'].max():.1f} km")
        c2.metric(T['rec_highest'], f"{filtered['elevation_m'].max():.0f} m")
        c3.metric(T['rec_fastest'], f"{filtered[filtered['distance_km']>5]['average_speed_kmh'].max():.1f} km/h")
        c4.metric(T['rec_kudos'], f"{filtered['kudos'].max()}")

        st.subheader(T['rec_top10'])
        top10 = filtered.nlargest(10, 'distance_km')[['start_date', 'name', 'type', 'distance_km', 'elevation_m', 'average_speed_kmh']]
        st.dataframe(top10, use_container_width=True)

with t5:
    c1, c2 = st.columns(2)
    with c1:
        day_counts = filtered['day_name'].value_counts()
        fig_pie = px.pie(values=day_counts.values, names=day_counts.index, title=T['time_pie'])
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        fig_hour = px.bar(filtered['hour'].value_counts().sort_index(), title=T['time_bar'])
        st.plotly_chart(fig_hour, use_container_width=True)

st.divider()
footer_html = """
<div style="text-align: center; font-size: 14px; color: #666;">
    Made with ❤️ by <a href="https://discordapp.com/users/justakos91" target="_blank" style="text-decoration: none; color: #e25555; font-weight: bold;">Akos</a>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
