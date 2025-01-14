import os
import time

import pyrootutils
from bs4 import BeautifulSoup

from caldav_sync import CalendarSync
from data import ResearchGroupMeeting, StudentPresentation
from google_sync import GoogleCalendarSync
from schedule_parser import ScheduleParser
from wiki_client import MediaWikiClient

# combines find_root() and set_root() into one method
root = pyrootutils.setup_root(
    search_from=__file__,
    indicator=".project-root",
    project_root_env_var=True,
    dotenv=True,
    pythonpath=True,
    cwd=True,
)


base_url = os.environ.get('WIKI_URL')
page_title = "Schedule_Groupmeetings"

username = os.environ.get('WIKI_USERNAME')
password = os.environ.get('WIKI_PASSWORD')

#Check Internet connection 10 times
for i in range(10):
    response = os.system("ping -c 1 google.com")
    if response == 0:
        break
    else:
        print("No Internet connection")
        time.sleep(1)
print("Internet connection established")


client = MediaWikiClient(base_url, username, password)
client.login()

html_string = client.fetch_page_html(page_title)

parser = ScheduleParser(html_string)
research_meetings = parser.get_research_group_meetings()
student_presentations = parser.get_student_presentations()

print("Research Group Meetings:")
for meeting in research_meetings:
    print(meeting)

print("\nStudent Presentations:")
for presentation in student_presentations:
    print(presentation)

research_meetings = ResearchGroupMeeting.load_data(research_meetings)
student_presentations = StudentPresentation.load_data(student_presentations)

#cal_sync = CalendarSync(
#    os.environ.get('CALDAV_URL'),
#    os.environ.get('CALDAV_USERNAME'),
#    os.environ.get('CALDAV_PASSWORD')
#)
#cal_sync.mirror_meetings_and_presentations(research_meetings, student_presentations)

g_sync = GoogleCalendarSync("client_g.json")
g_cal_id = os.environ.get('GOOGLE_CALENDAR_ID')

events = g_sync.get_calendar_events(g_cal_id)
g_sync.sync_research_group_meetings(g_cal_id, research_meetings)
g_sync.sync_student_presentations(g_cal_id, student_presentations)
pass