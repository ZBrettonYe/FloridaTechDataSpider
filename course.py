import bisect
import json
import re
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


def bisectStartsWith(ls: list, value: str) -> int:
    if value is None:
        return -1

    index = bisect.bisect_right(ls, value) - 1
    if index != -1 and value.startswith(ls[index]):
        return index

    return -1


if __name__ == '__main__':
    campuses: list = json.load(open('campus.json', 'r'))
    descriptions: list = json.load(open('description.json', 'r'))
    sections: list = json.load(open('_pawsSection.raw.json', 'r'))
    tags: list = json.load(open('tag.json', 'r'))
    titles: list = json.load(open('title.json', 'r'))

    tags = [tag['code'] for tag in tags]

    tagPattern = r'\((?:'
    tagPattern += '|'.join(tags)
    tagPattern += r'|/)+\)'
    # print(tagPattern)
    # \((?:CC|CL|COM|HON|HU|LA|Q|SS|/)+\)
    tagPattern = re.compile(tagPattern, flags=re.IGNORECASE)

    tagCodePattern = r'('
    tagCodePattern += '|'.join(tags)
    tagCodePattern += r')'
    # print(tagCodePattern)
    # (CC|CL|COM|HON|HU|LA|Q|SS)
    tagCodePattern = re.compile(tagCodePattern, flags=re.IGNORECASE)

    # Use dict to ensure courses are unique
    courses = dict()
    for index, section in enumerate(sections):
        course: int = section['course'][1]
        creditHours: list = section['creditHours']
        description: str = section['title'][1]
        location: str = section['location']
        semester: str = section['semester']
        subject: str = section['course'][0]
        title: str = section['title'][0]
        year: int = section['year']

        course = Course(
            subject=subject,
            course=course,
            campusId=bisectIndex(campuses, location),
            semesterId=['spring', 'summer', 'fall'].index(semester),
            year=year
        )

        course: Course
        if str(course) in courses:
            course = courses[str(course)]
        else:
            course.creditHours = creditHours
            course.sectionIds = []
            course.titleId = bisectIndex(titles, title)
            course.descriptionId = bisectStartsWith(descriptions, description)
            course.tagIds = set()
            courses[str(course)] = course

        course.creditHours[0] = min(course.creditHours[0], creditHours[0])
        course.creditHours[1] = max(course.creditHours[1], creditHours[1])

        course.sectionIds.append(index)

        attributeText: str = description[len(descriptions[course.descriptionId]):]
        if attributeText != '':
            tagText = ''.join(tagPattern.findall(attributeText))
            tagIds = [
                tags.index(tagCode.upper())
                for tagCode in tagCodePattern.findall(tagText)
            ]
            course.tagIds.update(tagIds)

    courses = list(courses.values())

    for course in courses:
        course.tagIds = list(course.tagIds)

    dataclassToJson(Course, courses, 'course')
