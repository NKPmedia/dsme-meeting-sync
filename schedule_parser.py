from datetime import datetime, timedelta

from bs4 import BeautifulSoup

def _remove_empty_time_entries(presentations):
    return [p for p in presentations if p['time']]

def remove_emtpy_comment_and_speaker_entries(presentations):
    return [p for p in presentations if p['comment'] or p['speaker']]

def remove_emtpy_speaker_entries(presentations):
    return [p for p in presentations if p['speaker']]

def transform_date_string_to_date(presentations):
    for p in presentations:
        p['date'] = datetime.strptime(p['date'], '%d.%m.%Y').date()
    return presentations

def remove_weekly_entry(presentations):
    return [p for p in presentations if p['week']!= 'weekly']

def convert_timeslot_to_start_end(presentations):
    new = []
    for p in presentations:
        #If timeslot does not have a start and end time ( - ) assume 1h duration
        try:
            if '-' in p['time']:
                p['time'] = p['time'].split('-')
                p['time'] = {
                    'start': datetime.strptime(p['time'][0], '%H:%M').time(),
                    'end': datetime.strptime(p['time'][1], '%H:%M').time()
                }
            else:
                p['time'] = {
                    'start': datetime.strptime(p['time'], '%H:%M').time(),
                    'end': (datetime.strptime(p['time'], '%H:%M') + timedelta(hours=1)).time()
                }
            new.append(p)
        except ValueError:
            print(f"Error parsing time: {p['time']}")
    return new

def split_presentation_from_day(presentations_old):
    presentations = []
    for p in presentations_old:
        for i in range(len(p['time'])):
            data = {
                'week': p['week'],
                'date': p['date'],
                'time': p['time'][i],
                'speaker': p['speaker'][i],
                'project': p['project'][i],
            }
            if len(p['comment']) == len(p['time']):
                data['comment'] = p['comment'][i]
            else:
                data['comment'] = str (p['comment'])
            presentations.append(data)
    return presentations

class ScheduleParser:
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def get_raw_research_group_meetings(self):
        research_meetings = []
        research_section = self.soup.find('span', id='DSME_Research_Group_Meetings').find_parent(
            'h2').find_next_sibling('table')

        if research_section:
            rows = research_section.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cols = row.find_all('td')
                meeting_info = {
                    'week': cols[0].text.strip(),
                    'date': cols[1].text.strip(),
                    'time': cols[2].text.strip(),
                    'speaker': cols[3].text.strip(),
                    'comment': cols[4].text.strip()
                }
                research_meetings.append(meeting_info)

        return research_meetings

    def get_raw_student_presentations(self):
        student_presentations = []
        student_section = self.soup.find('span', id='DSME_Students_Meetings').find_parent('h2').find_next_sibling(
            'table')

        if student_section:
            rows = student_section.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cols = row.find_all('td')
                presentation_info = {
                    'week': cols[0].text.strip(),
                    'date': cols[1].text.strip(),
                    'time': [s.strip() for s in cols[2].stripped_strings],
                    'speaker': [s.strip() for s in cols[3].stripped_strings],
                    'project': [p.strip() for p in cols[4].stripped_strings],
                    'comment': [c.strip() for c in cols[5].stripped_strings]
                }
                student_presentations.append(presentation_info)

        return student_presentations

    def get_student_presentations(self):
        student_presentations = self.get_raw_student_presentations()

        student_presentations = _remove_empty_time_entries(student_presentations)
        student_presentations = remove_emtpy_speaker_entries(student_presentations)
        student_presentations = transform_date_string_to_date(student_presentations)
        student_presentations = split_presentation_from_day(student_presentations)
        student_presentations = convert_timeslot_to_start_end(student_presentations)

        return student_presentations


    def get_research_group_meetings(self):
        research_meetings = self.get_raw_research_group_meetings()
        research_meetings = remove_weekly_entry(research_meetings)
        research_meetings = _remove_empty_time_entries(research_meetings)
        research_meetings = remove_emtpy_comment_and_speaker_entries(research_meetings)
        research_meetings = transform_date_string_to_date(research_meetings)
        research_meetings = convert_timeslot_to_start_end(research_meetings)

        return research_meetings