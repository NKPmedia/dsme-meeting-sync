# Group Meeting and Presentation Scheduler

This project syncs research group meetings and student presentations from a MediaWiki-based wiki page to Google Calendar using the Google Calendar API.

## Features

- Fetches and parses meeting schedules from a MediaWiki page.
- Synchronizes events with Google Calendar.

---

## Setup Instructions

### 1. Prerequisites

- Python 3.8+ installed.
- Access to your MediaWiki server credentials.
- Google Cloud project with the Calendar API enabled.
- `client_g.json` file for the Google Calendar API.

---

### 2. Clone and Create and Activate a Virtual Environment and Install Required Packages

```bash
git clone <repository-url>
python -m venv venv
source venv/bin/activate       # On Linux/macOS
venv\Scripts\activate          # On Windows
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory and add the following environment variables:

```
MEDIAWIKI_URL=<your-mediawiki-url>
MEDIAWIKI_USERNAME=<your-mediawiki-username>
MEDIAWIKI_PASSWORD=<your-mediawiki-password>
GOOGLE_CALENDAR_ID=<your-google-calendar-id>
```

### 4. Google Calendar API Setup
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the Google Calendar API.
4. Create OAuth 2.0 credentials.
5. Download the `client_g.json` file and place it in the root directory.

### 5. Run the Application

```bash
python main.py
```