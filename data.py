from datetime import date

class Timeslot:
    def __init__(self, start: str|date, end: str|date):
        self.start = start
        self.end = end
        if isinstance(start, str):
            self.start = date.fromisoformat(start)
        if isinstance(end, str):
            self.end = date.fromisoformat(end)

    def __repr__(self):
        return f"Timeslot(start={self.start}, end={self.end})"

class ResearchGroupMeeting:
    def __init__(self, week, date, time, speaker, comment):
        self.week = week
        self.date = date
        self.time = time
        self.speaker = speaker
        self.comment = comment

    @classmethod
    def from_dict(cls, data):
        return cls(
            week=data['week'],
            date=data['date'],
            time=Timeslot(data['time']['start'], data['time']['end']),
            speaker=data['speaker'],
            comment=data['comment']
        )

    @classmethod
    def load_data(cls, data_list):
        return [cls.from_dict(data) for data in data_list]

    def __repr__(self):
        return f"ResearchGroupMeeting(week={self.week}, date={self.date}, time={self.time}, speaker={self.speaker}, comment={self.comment})"


class StudentPresentation:
    def __init__(self, week, date, time, speaker, project, comment):
        self.week = week
        self.date = date
        self.time = time
        self.speaker = speaker
        self.project = project
        self.comment = comment

    @classmethod
    def from_dict(cls, data):
        return cls(
            week=data['week'],
            date=data['date'],
            time=Timeslot(data['time']['start'], data['time']['end']),
            speaker=data['speaker'],
            project=data['project'],
            comment=data.get('comment', [])
        )

    @classmethod
    def load_data(cls, data_list):
        return [cls.from_dict(data) for data in data_list]

    def __repr__(self):
        return f"StudentPresentation(week={self.week}, date={self.date}, time={self.time}, speaker={self.speaker}, project={self.project}, comment={self.comment})"
