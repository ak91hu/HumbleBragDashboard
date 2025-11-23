# ⚙️ Installation & Setup

This dashboard runs serverless using **Streamlit Cloud** and **GitHub Actions**. You do not need to pay for hosting.

## Prerequisites
1. A **GitHub** account.
2. A **Strava** account.
3. A **Streamlit Cloud** account.

---

## Step 1: Fork the Repository
Click the **Fork** button on the [GitHub Repository](https://github.com/ak91hu/HumblebragDashboard) to create your own copy.

---

## Step 2: Get Strava API Keys
This is the tricky part, but you only do it once.

1. Log in to [Strava API Settings](https://www.strava.com/settings/api).
2. Create an Application:
    * **Name:** `HumblebragDashboard`
    * **Category:** `Visualizer`
    * **Website:** `http://localhost`
    * **Authorization Callback Domain:** `localhost`
3. Copy your `Client ID` and `Client Secret`.

!!! warning "Crucial Step: The Refresh Token"
    You cannot use the standard Access Token. You need a **Refresh Token** with `activity:read_all` permissions.
    
    1. Paste your Client ID into this URL and open it in your browser:
       `https://www.strava.com/oauth/authorize?client_id=[YOUR_CLIENT_ID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all`
    2. Click **Authorize**.
    3. Look at the URL in your browser. It will look like: `http://localhost/exchange_token?state=&code=c40c...&scope=...`
    4. Copy the code after `code=`.
    5. Exchange this code for a token using cURL or a Python script (see `get_token.py` in the repo/issues).

---

## Step 3: Configure GitHub Secrets
1. Go to your forked repository on GitHub.
2. Navigate to **Settings** > **Secrets and variables** > **Actions**.
3. Add the following **Repository Secrets**:

| Secret Name | Value |
| :--- | :--- |
| `STRAVA_CLIENT_ID` | Your numeric Client ID |
| `STRAVA_CLIENT_SECRET` | Your alphanumeric Client Secret |
| `STRAVA_REFRESH_TOKEN` | The long token string starting with `r...` |

---

## Step 4: Deploy to Streamlit
1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Click **New App**.
3. Select your forked repository.
4. Main file path: `app.py`.
5. Click **Deploy**.

## Step 5: First Data Sync
1. Go to the **Actions** tab in your GitHub Repo.
2. Select **Strava Daily Sync**.
3. Click **Run workflow**.

Your dashboard will now update automatically every day at 06:00 UTC!
