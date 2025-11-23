# 🥇 Humblebrag Dashboard

[![Documentation Status](https://readthedocs.org/projects/humblebragdashboard/badge/?version=latest)](https://humblebragdashboard.readthedocs.io/en/latest/?badge=latest)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Build Status](https://github.com/ak91hu/HumbleBragDashboard/actions/workflows/daily_update.yml/badge.svg)

A fully automated, interactive analytics dashboard for Strava data. It visualizes year-over-year progression, tracks gamified challenges and mathematically proves that I earned that extra slice of pizza.

## 🚀 Key Features

### 📊 Deep Analytics
* **Year-over-Year Comparison:** Cumulative distance charts to track annual progress.
* **GitHub-Style Heatmap:** A calendar grid showing daily activity intensity.
* **Detailed Trends:** Rolling averages, weekly volume, and heart rate zones.
* **Activity Log:** A filterable list of recent activities with direct links to Strava.

### 🏔️ Gamification & "Humblebrags"
* **Gastro Conversion:** Converts burned calories into slices of **Pizza** 🍕, **Beers** 🍺, and **Burgers** 🍔.
* **Elevation Challenges:** Visual progress bars tracking ascent against **Mount Everest** and **Kékes-tető**.
* **Streaks:** Tracks the longest consecutive days of activity.

### 🤖 Zero-Maintenance Automation
* **Serverless:** Runs entirely on GitHub infrastructure.
* **Daily Updates:** A background bot fetches new data every morning.
* **Incremental Sync:** Only downloads new activities to respect API limits.

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **Data & Viz:** Pandas, Plotly Express
* **Integration:** Strava API (`stravalib`)
* **Automation:** GitHub Actions (Cron Job)

## ⚙️ How It Works
1. A **GitHub Action** wakes up daily to fetch new activities from Strava using a refresh token.
2. The data is processed, cleaned, and saved to a CSV file within the repository.
3. The **Streamlit Cloud** app detects the change and updates the dashboard instantly.

## ♻️ How to Run with YOUR Data
Want this dashboard for yourself? **Fork this repository** and follow these steps:

1. **Get Strava API Keys:**
   - Go to [Strava API Settings](https://www.strava.com/settings/api).
   - Create an app (use `localhost` as the "Authorization Callback Domain").
   - Copy your `Client ID` and `Client Secret`.

2. **Generate a Refresh Token:**
   - You need a token with `activity:read_all` permission (crucial!).
   - Use a helper script or Postman to exchange your Client ID/Secret for a **Refresh Token**.

3. **Set GitHub Secrets:**
   - Go to your forked repo **Settings** -> **Secrets and variables** -> **Actions**.
   - Add these 3 repository secrets:
     - `STRAVA_CLIENT_ID`
     - `STRAVA_CLIENT_SECRET`
     - `STRAVA_REFRESH_TOKEN`

4. **Deploy:**
   - Go to [Streamlit Cloud](https://share.streamlit.io/).
   - Connect your GitHub account and select your forked repository.
   - Click **Deploy**.

5. **Trigger Data Sync:**
   - Go to the **Actions** tab in your GitHub repo.
   - Select "Strava Daily Sync" and click **Run workflow**.
   - Once finished, refresh your Streamlit app to see your stats!

---
*Disclaimer: This project is open-source and not affiliated with Strava. The software is provided "as is", without warranty of any kind. Use it at your own risk. The author is not responsible for any data loss, API rate limits, or issues with your Strava account.*
