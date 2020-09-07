import bisect
import json
import re
from dataclasses import asdict, astuple, dataclass, field, fields
from typing import Optional
from util import dataclassToJson


@dataclass
class Section:
    campusId: int
    semesterId: int
    year: int

    crn: int
    courseId: int
    section: str

    creditHours: list
    cap: list
    waitListSeats: list

    titleId: int
    noteIds: list
    sessionId: int
    instructorId: int
    syllabus: str
    crossListCourses: list

    schedules: list

    levelId: int
    restrictionIds: list
    # prerequisiteId: int


# https://docs.python.org/3/library/bisect.html#searching-sorted-lists
def bisectIndex(ls: list, value) -> int:
    if value is None:
        return -1

    index = bisect.bisect_left(ls, value)
    if index != len(ls) and ls[index] == value:
        return index

    return -1


def bisectStartsWith(ls: list, value: str) -> int:
    if value is None:
        return -1

    index = bisect.bisect_right(ls, value) - 1
    if index != -1 and value.startswith(ls[index]):
        return index

    return -1


if __name__ == '__main__':
    buildings = [
        b['code']
        for b in json.load(open('building.json', 'r'))
    ]

    campuses: list = json.load(open('campus.json', 'r'))

    courses = [
        f'{c["subject"]:>4}{c["course"]:04}{c["campusId"]:02}{c["semesterId"]}{c["year"]}'
        for c in json.load(open('course2.json', 'r'))
    ]

    descriptions: list = json.load(open('description.json', 'r'))

    employees = [
        e['email']
        for e in json.load(open('employee.json', 'r'))
    ]

    notes: list = json.load(open('note.json', 'r'))
    sessions: list = json.load(open('session.json', 'r'))
    titles: list = json.load(open('title.json', 'r'))
    semesters = ['spring', 'summer', 'fall']
    levels: list = json.load(open('level.json', 'r'))
    restrictions: list = json.load(open('restriction.json', 'r'))
    prerequisites: list = json.load(open('prerequisite.json', 'r'))

    sections: list = json.load(open('_pawsSection.raw.json', 'r'))

    for section in sections:
        location: str = section['location']
        semester: str = section['semester']
        year: int = section['year']
        crn: int = section['crn']
        course: list = section['course']
        # section: str = section['section']
        creditHours: list = section['creditHours']
        title: list = section['title']
        # notes: list = section['notes']
        session: str = section['session']
        days: list = section['days']
        times: list = section['times']
        places: list = section['places']
        instructor: Optional[list] = section['instructor']
        cap: list = section['cap']
        syllabus: str = section['syllabus']
        level: str = section['level']
        waitListSeats: str = section['waitListSeats']
        crossListCourses: list = section['crossListCourses']
        # restrictions: list = section['restrictions']
        prerequisite: str = section['prerequisite']

        section['campusId'] = bisectIndex(campuses, location)

        section['semesterId'] = ['spring', 'summer', 'fall'].index(semester)

        section['courseId'] = bisectIndex(
            courses,
            f'{course[0]:>4}{course[1]:04}{section["campusId"]:02}{section["semesterId"]}{year}'
        )

        section['titleId'] = bisectStartsWith(titles, title[0])

        section['noteIds'] = [
            bisectIndex(notes, note)
            for note in section['notes']
        ]

        section['sessionId'] = bisectIndex(sessions, session)

        if instructor is None:
            section['instructorId'] = -1
        else:
            section['instructorId'] = bisectIndex(employees, instructor[1])

        schedules = []
        for i in range(max([len(days), len(times), len(places)])):
            day: str = days[i] if i < len(days) else None
            time: list = times[i] if i < len(times) else [0, 0]
            place: list = places[i] if i < len(places) else [None, None]

            buildingId = bisectIndex(buildings, place[0])
            if place[0] is not None and buildingId != -1:
                place[0] = buildingId

            schedules.append([
                day,                        # Day string
                time[0], time[1],           # Start time, end time
                place[0], place[1]          # Building id | building code, room string
            ])
        section['schedules'] = schedules

        section['levelId'] = bisectIndex(levels, level)

        section['restrictionIds'] = [
            bisectIndex(restrictions, restriction)
            for restriction in section['restrictions']
        ]

        section['prerequisiteId'] = bisectIndex(prerequisites, prerequisite)

    keys = [f.name for f in fields(Section)]
    sections = [
        Section(**{key: s[key] for key in keys})
        for s in sections
    ]

    dataclassToJson(Section, sections, 'section')
