import json
import re
from typing import Callable, List, Tuple

import scrapy


def parseLevels(lines: List[str], section: dict) -> None:
    section['level'] = lines.pop()


def parseWaitListSeats(lines: List[str], section: dict) -> None:
    while lines[-1] != 'Waitlist Seats':
        lines.pop()

    seats: [int, int] = []
    lines.pop()
    lines.pop()

    seats.append(int(lines.pop()))
    lines.pop()

    seats.append(int(lines.pop()))
    lines.pop()

    section['waitListSeats'] = seats


def parseCrossListCoruses(lines: List[str], section: dict) -> None:
    courses: List[Tuple[str, int]] = []
    lines.pop()
    lines.pop()

    while lines[-1] != '':
        text = lines.pop()

        course = (text.split(' ')[0], int(text.split(' ')[1]))
        courses.append(course)

        lines.pop()
        lines.pop()

    section['crossListCourses'] = courses


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


def parseRestrictions(lines: List[str], section: dict) -> None:
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

    section['restrictions'] = restrictions


def parsePrerequisites(lines: List[str], section: dict) -> None:
    prerequisite = ''
    lines.pop()  # '\n'

    while lines[-1] != '':
        line = lines.pop()
        prerequisite += f'{line} '

    prerequisite = prerequisite.strip()  # Remove trailing space
    if prerequisite == '':
        prerequisite = None

    section['prerequisite'] = prerequisite


def parseCorequisites(lines: List[str], section: dict) -> None:
    corequisites: List[Tuple[str, int]] = []
    lines.pop()
    lines.pop()

    while lines[-1] != '':
        line = lines.pop()

        course = (line.split()[0], int(line.split()[1]))
        corequisites.append(course)

        lines.pop()
        lines.pop()

    section['corequisites'] = corequisites


class PawsSectionSpider(scrapy.Spider):
    name = 'pawsSection'
    allowed_domains = ['nssb-p.adm.fit.edu']

    sectionAttributes = [
        {
            'key': 'level',
            'parseFn': parseLevels,
            'default': None,
            'header': 'Levels:'
        }, {
            'key': 'waitListSeats',
            'parseFn': parseWaitListSeats,
            'default': [],
            'header': 'Registration Availability'
        }, {
            'key': 'crossListCourses',
            'parseFn': parseCrossListCoruses,
            'default': [],
            'header': 'Cross List Courses:'
        }, {
            'key': 'restrictions',
            'parseFn': parseRestrictions,
            'default': [],
            'header': 'Restrictions:'
        }, {
            'key': 'prerequisite',
            'parseFn': parsePrerequisites,
            'default': None,
            'header': 'Prerequisites:'
        }, {
            'key': 'corequisites',
            'parseFn': parseCorequisites,
            'default': [],
            'header': 'Corequisites:'
        }
    ]

    def start_requests(self):
        # Convertion from semester text to code
        term = {'spring': '01', 'summer': '05', 'fall': '08'}

        sections: list = json.load(open('_section.raw.json', 'r'))
        for section in sections:
            year: int = section['year']
            semester: str = section['semester']
            crn: int = section['crn']

            # Construct URL
            termIn = f'{year}{term[semester]}'
            pawsUrl = f'https://nssb-p.adm.fit.edu/prod/bwckschd.p_disp_detail_sched?term_in={termIn}&crn_in={crn}'
            # print(pawsUrl)

            # Goto each section's PAWS page to collect data
            yield scrapy.Request(
                pawsUrl,
                callback=self.parsePawsSection,
                cb_kwargs={
                    'section': section
                }
            )

    def parsePawsSection(self, response: scrapy.http.Response, section: dict) -> None:
        # print(response.url)

        # Get all lines of texts on the page
        lines: List[str] = response.xpath('''
            //table[@class="datadisplaytable" and @summary="This table is used to present the detailed class information."]
            //td[@class="dddefault"]
            //text()
        ''').getall()

        # Strip all lines
        lines = [
            line.strip()
            for line in lines
        ]

        # Using the 'Reverse & Pop' mechanism to process data
        lines.reverse()

        # Fill section with default data
        section.update({
            attribute['key']: attribute['default']
            for attribute in self.sectionAttributes
        })

        # Process lines
        while lines != []:
            line: str = lines.pop()

            # Skip empty lines
            if line == '':
                continue

            # Try to match the line with one of the attrs
            for attribute in self.sectionAttributes:
                parseFn: Callable[[List[str], dict], None] = attribute['parseFn']
                header: str = attribute['header']

                # Process attr if header matches
                if line == header:
                    parseFn(lines, section)

        # print(section)
        yield section
