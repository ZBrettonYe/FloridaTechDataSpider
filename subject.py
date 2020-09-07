import json
from dataclasses import asdict, astuple, dataclass, fields
from typing import List

from util import dataclassToJson

presetSubjects = [
    ['ASC', 'Academic Support Center'],
    ['AEE', 'Aerospace Engineering'],
    ['AVF', 'Aviation Flight'],
    ['AHF', 'Aviation Human Factors'],
    ['AVM', 'Aviation Management'],
    ['AVS', 'Aviation Science'],
    ['AVT', 'Aviation Technology'],
    ['BEH', 'Behavior Analysis'],
    ['BCM', 'Biochemistry'],
    ['BIO', 'Biology'],
    ['BME', 'Biomedical Engineering'],
    ['BUS', 'Business'],
    ['CHE', 'Chemical Engineering'],
    ['CHM', 'Chemistry'],
    ['CVE', 'Civil Engineering'],
    ['COM', 'Communication'],
    ['CIS', 'Computer Information Systems'],
    ['CSE', 'Computer Sciences'],
    ['CON', 'Construction'],
    ['CWE', 'Cooperative Education'],
    ['EDS', 'Education'],
    ['ECE', 'Electrical & Computer Engineer'],
    ['ENM', 'Engineering Management'],
    ['EPE', 'Engineering Protrack Co-op Edu'],
    ['ESL', 'English as a Second Language'],
    ['ENS', 'Environmental Sciences'],
    ['FYE', 'First Year Experience'],
    ['FTE', 'Flight Test Engineering'],
    ['PSF', 'Forensic Psychology'],
    ['HON', 'Honors'],
    ['HCD', 'Human-Centered Design'],
    ['HUM', 'Humanities'],
    ['CYB', 'Info Assurance & Cybersecurity'],
    ['ISC', 'Interdisciplinary Science'],
    ['LNG', 'Languages & Linguistics'],
    ['MGT', 'Management'],
    ['MAR', 'Marine Biology'],
    ['MTH', 'Mathematics'],
    ['MEE', 'Mechanical Engineering'],
    ['MET', 'Meteorology'],
    ['MSC', 'Military Science'],
    ['MUS', 'Music'],
    ['OCE', 'Ocean Engineering'],
    ['OCN', 'Oceanography'],
    ['ORP', 'Operations Research'],
    ['PED', 'Physical Education'],
    ['PHY', 'Physics'],
    ['PSY', 'Psychology'],
    ['SOC', 'Sociology'],
    ['SWE', 'Software Engineering'],
    ['SPS', 'Space Sciences'],
    ['SPC', 'Space Systems'],
    ['SUS', 'Sustainability'],
    ['SYS', 'Systems Engineering'],
    ['WRI', 'Writing'],
]


@dataclass
class Subject:
    code: str
    name: str
    courseIdStart: int
    courseIdEnd: int

    def __lt__(self, s) -> bool:
        return self.code < s.code


if __name__ == '__main__':
    courses: List[dict] = json.load(open('course2.json', 'r'))

    subjects = dict()
    for presetSubject in presetSubjects:
        subjects[presetSubject[0]] = {
            'name': presetSubject[1],
            'courseIds': []
        }

    for index, course in enumerate(courses):
        subject: str = course['subject']

        # Add course to subject if the subject exists
        if subject in subjects:
            subjects[subject]['courseIds'].append(index)
            continue

        # Otherwise create a new subject
        subjects[subject] = {
            'name': subject,
            'courseIds': [index]
        }

    subjects2 = []
    for code, subject in subjects.items():
        subject['code'] = code

        courseIds: List[int] = subject['courseIds']
        courseIds.sort()

        # Coruse IDs are expected to be consecutive, so we can extract the range of it
        expectedCourseIds: List[int] = list(range(courseIds[0], courseIds[-1] + 1))

        if courseIds == expectedCourseIds:
            subject['courseIdStart'] = courseIds[0]
            subject['courseIdEnd'] = courseIds[-1] + 1
        else:
            raise ValueError(f'Course IDs for subject {code} is not consecutive. Expected {expectedCourseIds}, got {courseIds}.')

        subjects2.append(subject)

    subjects = subjects2
    # print(subjects)

    keys = [f.name for f in fields(Subject)]
    subjects = [
        Subject(**{key: s[key] for key in keys})
        for s in subjects
    ]

    dataclassToJson(Subject, subjects, 'subject')
