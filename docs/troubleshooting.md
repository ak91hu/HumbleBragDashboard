# 🔧 Troubleshooting

### "No data found" Error
If the dashboard says "No data", it means the `activities.csv` file hasn't been generated yet.
* **Fix:** Go to GitHub Actions and manually trigger the **Strava Daily Sync** workflow. Wait for the green checkmark ✅.

### "Unauthorized" or "Missing Permissions"
The bot cannot fetch data.
* **Cause:** Your Refresh Token was generated without the `activity:read_all` scope.
* **Fix:** You must generate a new Refresh Token and ensure you check the "View data about your private activities" box during authorization. Update the GitHub Secret.

### Matplotlib / ImportError
* **Cause:** Missing dependencies on Streamlit Cloud.
* **Fix:** Ensure your `requirements.txt` includes `matplotlib`. (The current version of the app has a fallback to prevent crashing).

### Data isn't updating on the website
* **Cause:** Streamlit aggressive caching.
* **Fix:** In the Streamlit app, click the three dots (top right) > **Clear Cache** > **Rerun**.
