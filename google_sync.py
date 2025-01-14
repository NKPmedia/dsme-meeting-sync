import os
from datetime import datetime, timedelta
from time import sleep

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarSync:
    def __init__(self, credentials_file):
        self.creds = None

        # Load credentials from file or initiate OAuth flow if not available/expired.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If there are no valid credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for future use.
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('calendar', 'v3', credentials=self.creds)

    def create_event(self, calendar_id, event):
        event_result = self.service.events().insert(calendarId=calendar_id, body=event).execute()
        return event_result

    def update_event(self, calendar_id, event_id, updated_event):
        event_result = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=updated_event).execute()
        return event_result

    def delete_event(self, calendar_id, event_id):
        result = self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return result

    def get_calendar_events(self, calendar_id):
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(
            calendarId=calendar_id,
            maxResults=2500,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return events_result.get('items', [])

    def delete_all_events(self, calendar_id):
        events = self.get_calendar_events(calendar_id)
        for event in events:
            self.delete_event(calendar_id, event['id'])

    def sync_research_group_meetings(self, calendar_id, meetings):
        # Retrieve all existing events
        rgm = [event for event in self.get_calendar_events(calendar_id) if event['summary'].startswith('RGM:')]
        existing_events_keys = {f"RGM{event['summary'].split(': ')[1]}-{event['start']['dateTime'].split('T')[0]}-{event['start']['dateTime'].split('T')[1].split('+')[0]}-{event['end']['dateTime'].split('T')[1].split('+')[0]}": event for event in rgm}

        # Track current meetings for updating/removal purposes
        current_meeting_keys = set()

        for meeting in meetings:
            sleep(0.5)
            event_title = f"RGM: {meeting.speaker}"
            description = f"{meeting.comment}"
            unique_key = f"RGM{meeting.speaker}-{meeting.date}-{meeting.time.start}-{meeting.time.end}"

            start_datetime = datetime.combine(meeting.date, datetime.strptime(meeting.time.start.strftime("%H:%M"), "%H:%M").time()).isoformat()
            end_datetime = (datetime.combine(meeting.date, datetime.strptime(meeting.time.end.strftime("%H:%M"), "%H:%M").time())).isoformat()

            event = {
                'summary': event_title,
                'description': description,
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': 'Europe/Berlin',
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': 'Europe/Berlin',
                },
            }

            current_meeting_keys.add(unique_key)

            if unique_key in existing_events_keys:
                existing_event = existing_events_keys[unique_key]
                # Check if the event needs an update
                if (existing_event['start']['dateTime'] == start_datetime and
                        existing_event['end']['dateTime'] == end_datetime and
                        existing_event['description'] == description):
                    print(f"Meeting '{meeting.speaker}' is already up-to-date.")
                else:
                    # Update existing event
                    self.update_event(calendar_id, existing_event['id'], event)
                    print(f"Updated meeting: {meeting.speaker}")
            else:
                # Create new event
                self.create_event(calendar_id, event)
                print(f"Added meeting: {meeting.speaker}")

        # Remove obsolete events
        for unique_key, event in existing_events_keys.items():
            if unique_key not in current_meeting_keys:
                self.delete_event(calendar_id, event['id'])
                print(f"Removed obsolete meeting: {event['summary']}")

    def sync_student_presentations(self, calendar_id, presentations):
        # Retrieve all existing events
        spp = [event for event in self.get_calendar_events(calendar_id) if event['summary'].startswith('SP:')]
        existing_events_keys = {f"SP{event['summary'].split(': ')[1]}-{event['start']['dateTime'].split('T')[0]}-{event['start']['dateTime'].split('T')[1].split('+')[0]}-{event['end']['dateTime'].split('T')[1].split('+')[0]}": event for event in spp}

        # Track current presentations for updating/removal purposes
        current_presentation_keys = set()

        for presentation in presentations:
            sleep(0.5)
            event_title = f"SP: {presentation.speaker}"
            description = f"Week: {presentation.week}\nSpeaker: {presentation.speaker}\nProject: {presentation.project}\nComment: {presentation.comment}"
            unique_key = f"SP{presentation.speaker}-{presentation.date}-{presentation.time.start}-{presentation.time.end}"

            start_datetime = datetime.combine(presentation.date, datetime.strptime(presentation.time.start.strftime("%H:%M"), "%H:%M").time()).isoformat()
            end_datetime = (datetime.combine(presentation.date, datetime.strptime(presentation.time.end.strftime("%H:%M"), "%H:%M").time())).isoformat()

            event = {
                'summary': event_title,
                'description': description,
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': 'Europe/Berlin',
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': 'Europe/Berlin',
                },
            }

            current_presentation_keys.add(unique_key)

            if unique_key in existing_events_keys:
                existing_event = existing_events_keys[unique_key]
                # Check if the event needs an update
                if (existing_event['start']['dateTime'] == start_datetime and
                        existing_event['end']['dateTime'] == end_datetime and
                        existing_event['description'] == description):
                    print(f"Presentation '{presentation.speaker}' is already up-to-date.")
                else:
                    # Update existing event
                    self.update_event(calendar_id, existing_event['id'], event)
                    print(f"Updated presentation: {presentation.speaker}")
            else:
                # Create new event
                self.create_event(calendar_id, event)
                print(f"Added presentation: {presentation.speaker}")

        # Remove obsolete events
        for unique_key, event in existing_events_keys.items():
            if unique_key not in current_presentation_keys:
                self.delete_event(calendar_id, event['id'])
                print(f"Removed obsolete presentation: {event['summary']}")