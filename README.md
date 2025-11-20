# 🥇 Humblebrag Dashboard

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

---
*Disclaimer: This project is open-source and not affiliated with Strava.*
