import re
from typing import Dict, List, Optional, Tuple, Union

import scrapy


def parseCourse(tableData: scrapy.Selector) -> Tuple[str, int]:
    text: str = tableData.xpath('text()').get()
    # Course number is not guaranteed to be 4 digits, for example: '23604 WRI 100'
    doublet = re.match(r'(\w{3,4}) (\d+)', text).groups()
    return (doublet[0], int(doublet[1]))


def parseCreditHours(tableData: scrapy.Selector) -> Tuple[float, float]:
    text: str = tableData.xpath('text()').get()

    # It could be a range, which is formatted like '3-6'
    # Need to use float because there are courses with 0.5 credit hours
    if '-' in text:
        doublet = text.split('-')
        return (float(doublet[0]), float(doublet[1]))
    else:
        return (float(text), float(text))


def parseTitle(tableData: scrapy.Selector) -> Tuple[str, str]:
    # The title contains the actual course title and its description
    return (
        tableData.xpath('span/text()').get().strip(),
        tableData.xpath('span/@data-content').get().strip()
    )


def parseNotes(tableData: scrapy.Selector) -> List[str]:
    # It can have multiple notes, and empty notes are ignored
    return [
        note.strip()
        for note in tableData.xpath('text()').getall()
        if note.strip() != ''
    ]


def parseDays(tableData: scrapy.Selector) -> List[str]:
    # It can have multiple days, and empty days are ignored
    return [
        day.strip()
        for day in tableData.xpath('text()').getall()
        if day.strip() != ''
    ]


def parseTimes(tableData: scrapy.Selector) -> List[Tuple[int, int]]:
    return [
        (
            int(timeRange.split('-')[0]),
            int(timeRange.split('-')[1])
        )
        for timeRange in tableData.xpath('text()').getall()
        if timeRange.strip() != ''
    ]


# [Building Code, Room]
def parsePlaces(tableData: scrapy.Selector) -> List[Tuple[str, str]]:
    places = [
        (
            placePair.strip().split()[0],
            placePair.strip().split()[1]
        )
        for placePair in tableData.xpath('text()').getall()
        if placePair.strip() != ''
    ]

    # Set 'TBA' rooms to None
    places = [
        place if place[1] != 'TBA' else (place[0], None)
        for place in places
    ]

    return places

def parseInstructor(tableData: scrapy.Selector) -> Optional[Tuple[str, str]]:
    # It could be name, empty, or 'TBA'. Only parse when name and email are both present
    try:
        name = tableData.xpath('a/text()').get()
        email = tableData.xpath('a/@href').get()[len('mailto:'):]   # TypeError
        return (name, email)
    except TypeError:  # 'NoneType' object is not subscriptable
        return None


def parseCap(tableData: scrapy.Selector) -> Tuple[int, int]:
    return (
        int(tableData.xpath('strong/text()').get()),
        int(tableData.xpath('text()').get()[len('/'):])
    )


class SectionSpider(scrapy.Spider):
    name = 'section'
    allowed_domains = ['apps.fit.edu']
    start_urls = ['https://apps.fit.edu/schedule']

    # If the attr can be parsed with a single xpath, the xpath is provided
    # Otherwise xpath is None and a parse function is provided
    sectionAttributes = [
        {
            'header': 'CRN',
            'key': 'crn',
            'default': -1,
            'xpath': 'text()',
            'parseFn': None
        }, {
            'header': 'Course',
            'key': 'course',
            'default': ('Unknown', -1),
            'xpath': None,
            'parseFn': parseCourse
        }, {
            'header': 'Section',
            'key': 'section',
            'default': '',
            'xpath': 'text()',
            'parseFn': None
        }, {
            'header': 'Cr',
            'key': 'creditHours',
            'default': (-1, -1),
            'xpath': None,
            'parseFn': parseCreditHours
        }, {
            'header': 'Title',
            'key': 'title',
            'default': 'Unknown',
            'xpath': None,
            'parseFn': parseTitle
        }, {
            'header': 'Notes',
            'key': 'notes',
            'default': [],
            'xpath': None,
            'parseFn': parseNotes
        }, {
            'header': 'Session',
            'key': 'session',
            'default': None,
            'xpath': 'text()',
            'parseFn': None
        }, {
            'header': 'Days',
            'key': 'days',
            'default': [],
            'xpath': None,
            'parseFn': parseDays
        }, {
            'header': 'Times',
            'key': 'times',
            'default': [],
            'xpath': None,
            'parseFn': parseTimes
        }, {
            'header': 'Place',
            'key': 'places',
            'default': [],
            'xpath': None,
            'parseFn': parsePlaces
        }, {
            'header': 'Instructor',
            'key': 'instructor',
            'default': None,
            'xpath': None,
            'parseFn': parseInstructor
        }, {
            'header': 'Cap',
            'key': 'cap',
            'default': (-1, -1),
            'xpath': None,
            'parseFn': parseCap
        }, {
            'header': 'Syllabus',
            'key': 'syllabus',
            'default': None,
            'xpath': 'a/@href',
            'parseFn': None
        }
    ]

    # Goto each campus
    def parse(self, response: scrapy.http.TextResponse):
        # campusUrls will contain 'https://policy.fit.edu/Schedule-of-Classes'
        # This URL is automatically eliminated by self.allowed_domains
        campusUrls = response.xpath('''
            //div[@class="three wide column"]
            /div[@id="sub-nav"]
            /a
            /@href
        ''').getall()
        # print(campusUrls)

        yield from response.follow_all(campusUrls, callback=self.parseCampus)

    # Goto each semester of this campus
    def parseCampus(self, response: scrapy.http.TextResponse):
        semesterUrls = response.xpath('''
            //div[@class="thirteen wide column"]
            /div[@class="ui"]
            /a
            /@href
        ''').getall()
        # print(semesterUrls)

        yield from response.follow_all(semesterUrls, callback=self.parseSemester)

    # Goto the first page of the semester
    def parseSemester(self, response: scrapy.http.TextResponse):
        sectionTableUrls = [f'{response.url}?page=1']
        # print(sectionTableUrls)

        yield from response.follow_all(sectionTableUrls, callback=self.parseSectionTable)

    # Goto other pages of the semester. Duplicated visits are automatically eliminated
    # Parse sections on the page
    def parseSectionTable(self, response: scrapy.http.TextResponse):
        nextPageUrls = response.xpath('''
            //div[@class="thirteen wide column"]
            /div[@class="ui pagination menu"]
            /a
            /@href
        ''').getall()
        # print(nextPageUrls)

        yield from response.follow_all(nextPageUrls, callback=self.parseSectionTable)

        h2Text: str = response.xpath('''
            //div[@class="thirteen wide column"]
            /h2
            /text()
        ''').get()

        # It happends when 'There are currently no available classes for this term.'
        # For example, 'Fort Lee, VA Class Schedule: Summer' in June 2020
        try:
            triplet = re.match(  # AttributeError
                r'(.+) Class Schedule: (spring|summer|fall) (\d{4})',
                h2Text
            ).groups()
        except AttributeError:  # 'NoneType' object has no attribute 'groups'
            return

        location: str = triplet[0]
        semester: str = triplet[1]
        year = int(triplet[2])
        # print(location, semester, year)

        # Semesters and campuses can have different header
        # Summer have 'session'
        # Non-main campus have 'syllabus'
        headers = response.xpath('''
            //table[@class="ui small compact celled table"]
            //th
            /text()
        ''').getall()
        # print(headers)

        # Take out every cell in a flattened array
        sectionData = response.xpath('''
            //table[@class="ui small compact celled table"]
            //td
        ''')

        # Make sure the numbers match, otherwise the operations comes next will break
        assert len(sectionData) % len(headers) == 0

        # Reverse the list so that it pops each item in correct order
        sectionData.reverse()

        # It will be empty when all rows has been parsed
        while sectionData != []:
            section = {
                'location': location,
                'semester': semester,
                'year': year
            }

            for attribute in self.sectionAttributes:
                header: str = attribute['header']
                key: str = attribute['key']
                default = attribute['default']
                xpath: str = attribute['xpath']
                parseFn = attribute['parseFn']

                # Skip parsing if table does not have the attribute
                if header not in headers:
                    section[key] = default
                    continue

                # Take out a cell
                tableData: scrapy.Selector = sectionData.pop()

                # Do parsing
                if xpath is not None:
                    value: str = tableData.xpath(xpath).get(default=default)
                    if isinstance(value, str):
                        value = value.strip()
                        if value == '':
                            value = None
                else:
                    value = parseFn(tableData)

                section[key] = value

            # Postprocessing
            section['crn'] = int(section['crn'])

            # print(section)
            yield section
