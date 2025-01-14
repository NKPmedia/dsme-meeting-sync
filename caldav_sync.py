from datetime import date, datetime, timedelta
from caldav import DAVClient
from caldav.elements import dav, cdav
import vobject  # Used to parse iCalendar events from the calendar

from data import ResearchGroupMeeting, StudentPresentation


class CalendarSync:
    def __init__(self, url: str, username: str, password: str):
        self.client = DAVClient(url, username=username, password=password)
        self.principal = self.client.principal()
        self.calendars = self.principal.calendars()
        self.calendar = self.calendars[0]  # Assuming the first calendar is the target

    def format_event(self, title: str, start: date, end: date, description: str):
        """Formats the data into a basic iCalendar (VCALENDAR) format for the event."""
        return f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{title}
DTSTART;VALUE=DATE:{start.strftime("%Y%m%d")}
DTEND;VALUE=DATE:{(end + timedelta(days=1)).strftime("%Y%m%d")}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR"""

    def get_existing_events(self):
        """Retrieve existing events on the calendar."""
        events = {}
        for event in self.calendar.events():
            component = vobject.readOne(event.data)
            summary = component.vevent.summary.value
            start = component.vevent.dtstart.value
            end = component.vevent.dtend.value
            description = component.vevent.description.value
            events[summary] = (start, end, description, event)
        return events

    def sync_meeting(self, meeting: ResearchGroupMeeting, existing_events):
        title = f"Research Group Meeting: {meeting.speaker}"
        description = f"Week: {meeting.week}\nSpeaker: {meeting.speaker}\nComment: {meeting.comment}"

        # Check if event already exists and is up to date
        if title in existing_events:
            start, end, existing_description, event = existing_events[title]
            if start == meeting.date and description == existing_description:
                print(f"Meeting {title} already up-to-date.")
                return
            else:
                # Update event
                event.vobject_instance.vevent.dtstart.value = meeting.date
                event.vobject_instance.vevent.dtend.value = meeting.date + timedelta(days=1)
                event.vobject_instance.vevent.description.value = description
                event.save()
                print(f"Updated meeting: {title}")
        else:
            # Add new event
            new_event = self.format_event(title, meeting.date, meeting.date, description)
            self.calendar.add_event(new_event)
            print(f"Added meeting: {title}")

    def sync_presentation(self, presentation: StudentPresentation, existing_events):
        title = f"Student Presentation: {presentation.speaker}"
        description = f"Week: {presentation.week}\nSpeaker: {presentation.speaker}\nProject: {presentation.project}\nComment: {presentation.comment}"

        # Check if event already exists and is up to date
        if title in existing_events:
            start, end, existing_description, event = existing_events[title]
            if start == presentation.date and description == existing_description:
                print(f"Presentation {title} already up-to-date.")
                return
            else:
                # Update event
                event.vobject_instance.vevent.dtstart.value = presentation.date
                event.vobject_instance.vevent.dtend.value = presentation.date + timedelta(days=1)
                event.vobject_instance.vevent.description.value = description
                event.save()
                print(f"Updated presentation: {title}")
        else:
            # Add new event
            new_event = self.format_event(title, presentation.date, presentation.date, description)
            self.calendar.add_event(new_event)
            print(f"Added presentation: {title}")

    def mirror_meetings_and_presentations(self, meetings: list[ResearchGroupMeeting],
                                          presentations: list[StudentPresentation]):
        # Retrieve existing events
        existing_events = self.get_existing_events()

        # Sync all meetings
        for meeting in meetings:
            self.sync_meeting(meeting, existing_events)

        # Sync all presentations
        for presentation in presentations:
            self.sync_presentation(presentation, existing_events)

        # Remove obsolete events
        valid_titles = {f"Research Group Meeting: {m.speaker}" for m in meetings}
        valid_titles.update({f"Student Presentation: {p.speaker}" for p in presentations})

        for title, (_, _, _, event) in existing_events.items():
            if title not in valid_titles:
                event.delete()
                print(f"Removed obsolete event: {title}")