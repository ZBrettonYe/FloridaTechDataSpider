import json
import re
from typing import List, Callable
import scrapy


LECTURE_HOURS_RE = re.compile(
    pattern=r'([\d.]+)\s+Lecture hours',
    flags=re.IGNORECASE
)

LAB_HOURS_RE = re.compile(
    pattern=r'([\d.]+)\s+Lab hours',
    flags=re.IGNORECASE
)


def parseLectureHours(line: str, lines: list, course: dict) -> None:
    try:
        lectureHours = LECTURE_HOURS_RE.search(line).group(1)
        course['lectureHours'] = float(lectureHours)
    except AttributeError:  # 'NoneType' object has no attribute 'group'
        pass


def parseLabHours(line: str, lines: list, course: dict) -> None:
    try:
        labHours = LAB_HOURS_RE.search(line).group(1)
        course['labHours'] = float(labHours)
    except AttributeError:  # 'NoneType' object has no attribute 'group'
        pass


def parseLevels(line: str, lines: list, course: dict) -> None:
    if line == 'Levels:':
        course['level'] = lines.pop()


def parseScheduleTypes(line: str, lines: list, course: dict) -> None:
    if line != 'Schedule Types:':
        return

    scheduleTypes = []

    line: str = lines.pop()
    while line != '':
        parts = line.split(',')
        for part in parts:
            part = part.strip()
            if part != '':
                scheduleTypes.append(part)

        line: str = lines.pop()

    course['scheduleTypes'] = scheduleTypes


# UNINDENT_RESTRICTIONS = [
#     'May not be assigned one of the following Student Attributes:',
#     'May not be enrolled as the following Classifications:',
#     'May not be enrolled in one of the following Campuses:',
#     'May not be enrolled in one of the following Levels:',
#     'May not be enrolled in one of the following Majors:',
#     'Must be assigned one of the following Student Attributes:',
#     'Must be enrolled in one of the following Campuses:',
#     'Must be enrolled in one of the following Classifications:',
#     'Must be enrolled in one of the following Colleges:',
#     'Must be enrolled in one of the following Departments:',
#     'Must be enrolled in one of the following Fields of Study (Major, Minor,  or Concentration):',
#     'Must be enrolled in one of the following Majors:'
# ]


def parseRestrictions(line: str, lines: list, course: dict) -> None:
    if line != 'Restrictions:':
        return

    restrictions = []
    lines.pop()  # '\n'

    while lines[-1] != '':
        line = lines.pop()

        # Some lines in restrictions are not indented
        # See UNINDENT_RESTRICTIONS
        if line.startswith('May not be') or line.startswith('Must be'):
            restrictions.append(line)
        # Others are indented with '\n\xa0 \xa0 \xa0 ', but it's stripped away
        # Here we use a '\t' in place of the monstrosity
        else:
            restrictions.append(f'\t{line}')

    course['restrictions'] = restrictions


def parsePrerequisites(line: str, lines: list, course: dict) -> None:
    if line != 'Prerequisites:':
        return

    prerequisite = ''
    lines.pop()  # '\n'

    while lines[-1] != '':
        line = lines.pop()
        prerequisite += f'{line} '

    prerequisite = prerequisite.strip()  # Remove trailing space
    if prerequisite == '':
        prerequisite = None

    course['prerequisite'] = prerequisite


def parseCourseAttributes(line: str, lines: list, course: dict) -> None:
    if line.strip() != 'Course Attributes:':
        return

    courseAttributes = []

    line: str = lines.pop()
    while line.strip() != '':
        courseAttributes.append(line.strip())
        line: str = lines.pop()

    course['courseAttributes'] = courseAttributes


class PawsCourseSpider(scrapy.Spider):
    name = 'pawsCourse'
    allowed_domains = ['nssb-p.adm.fit.edu']

    courseAttributes = [
        {
            'key': 'lectureHours',
            'parseFn': parseLectureHours,
            'default': None
        }, {
            'key': 'labHours',
            'parseFn': parseLabHours,
            'default': None
        }, {
            'key': 'level',
            'parseFn': parseLevels,
            'default': None
        }, {
            'key': 'scheduleTypes',
            'parseFn': parseScheduleTypes,
            'default': []
        }, {
            'key': 'restrictions',
            'parseFn': parseRestrictions,
            'default': []
        }, {
            'key': 'prerequisite',
            'parseFn': parsePrerequisites,
            'default': None
        }, {
            'key': 'courseAttributes',
            'parseFn': parseCourseAttributes,
            'default': []
        }
    ]

    def start_requests(self):
        courses: list = json.load(open('course.json', 'r'))
        for course in courses:
            subject: str = course['subject']
            courseNumber: int = course['course']
            semesterId: int = course['semesterId']
            year: int = course['year']

            catTermIn = f'{year}{["01", "05", "08"][semesterId]}'
            pawsUrl = f'https://nssb-p.adm.fit.edu/prod/bwckctlg.p_disp_course_detail?cat_term_in={catTermIn}&subj_code_in={subject}&crse_numb_in={courseNumber}'
            # print(pawsUrl)

            yield scrapy.Request(
                pawsUrl,
                callback=self.parsePawsCourse,
                cb_kwargs={
                    'course': course
                },
                dont_filter=True
            )

    def parsePawsCourse(self, response: scrapy.http.TextResponse, course: dict) -> None:
        # print(response.url)

        # Get all lines of texts on the page
        lines: List[str] = response.xpath('''
            //table[@class="datadisplaytable" and @summary="This table lists the course detail for the selected term."]
            //td[@class="ntdefault"]
            //text()
        ''').getall()

        # Strip all lines
        lines = [
            line.strip()
            for line in lines
        ]

        # Using the 'Reverse & Pop' mechanism to process data
        lines.reverse()

        # Fill course with default data
        course.update({
            attribute['key']: attribute['default']
            for attribute in self.courseAttributes
        })

        # Process lines
        while lines != []:
            line: str = lines.pop()

            # Skip empty lines
            if line == '':
                continue

            # Call parse functions on the line
            for attribute in self.courseAttributes:
                key: str = attribute['key']
                parseFn: Callable[[str, List[str], dict], None] = attribute['parseFn']
                default = attribute['default']

                # If the value is still default, call parse function to update the course
                # Parse function will change the course if the line is for the function
                # Otherwise it does nothing
                if course[key] == default:
                    parseFn(line, lines, course)

        # print(course)
        yield course
