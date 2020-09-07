import bisect
import json
from dataclasses import asdict, astuple, dataclass, field, fields

from util import dataclassToJson


@dataclass
class Course:
    subject: str
    course: int

    campusId: int
    semesterId: int
    year: int

    creditHours: list = None
    sectionIds: list = None
    titleId: int = None
    descriptionId: int = None
    tagIds: set = None

    # Additional attributes
    lectureHours: int = None
    labHours: int = None

    levelId: int = None
    scheduleTypeIds: list = None
    restrictionIds: list = None
    prerequisiteId: int = None
    courseAttributeIds: list = None

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, c):
        return str(self) == str(c)

    def __lt__(self, c):
        return str(self) < str(c)

    def __str__(self):
        return f'{self.subject:>4}{self.course:04}{self.campusId:02}{self.semesterId}{self.year}'


# https://docs.python.org/3/library/bisect.html#searching-sorted-lists
def bisectIndex(ls: list, value) -> int:
    if value is None:
        return -1

    index = bisect.bisect_left(ls, value)
    if index != len(ls) and ls[index] == value:
        return index

    return -1


if __name__ == '__main__':
    levels: list = json.load(open('level.json', 'r'))
    scheduleTypes: list = json.load(open('scheduleType.json', 'r'))
    restrictions: list = json.load(open('restriction.json', 'r'))
    prerequisites: list = json.load(open('prerequisite.json', 'r'))
    courseAttributes: list = json.load(open('courseAttribute.json', 'r'))

    courses: list = json.load(open('_pawsCourse.raw.json', 'r'))

    for course in courses:
        course['levelId'] = bisectIndex(levels, course['level'])

        course['scheduleTypeIds'] = [
            bisectIndex(scheduleTypes, scheduleType)
            for scheduleType in course['scheduleTypes']
        ]

        course['restrictionIds'] = [
            bisectIndex(restrictions, restriction)
            for restriction in course['restrictions']
        ]

        course['prerequisiteId'] = bisectIndex(prerequisites, course['prerequisite'])

        course['courseAttributeIds'] = [
            bisectIndex(courseAttributes, courseAttribute)
            for courseAttribute in course['courseAttributes']
        ]

    keys = [f.name for f in fields(Course)]
    courses = [
        Course(**{key: c[key] for key in keys})
        for c in courses
    ]

    dataclassToJson(Course, courses, 'course2')
