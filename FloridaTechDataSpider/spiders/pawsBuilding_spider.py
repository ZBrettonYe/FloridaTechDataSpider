import json
from typing import Dict, List, Optional

import scrapy


class PawsBuildingSpider(scrapy.Spider):
    name = 'pawsBuilding'
    allowed_domains = ['nssb-p.adm.fit.edu']

    def start_requests(self):
        courses: list = json.load(open('course.json', 'r'))
        sections: list = json.load(open('_pawsSection.raw.json', 'r'))

        for course in courses:
            subject: str = course['subject']
            courseNumber: int = course['course']
            semesterId: int = course['semesterId']
            year: int = course['year']
            sectionIds: list = course['sectionIds']

            termIn = f'{year}{["01", "05", "08"][semesterId]}'
            pawsUrl = f'https://nssb-p.adm.fit.edu/prod/bwckctlg.p_disp_listcrse?term_in={termIn}&subj_in={subject}&crse_in={courseNumber}&schd_in='

            yield scrapy.Request(
                pawsUrl,
                callback=self.parseBuilding,
                cb_kwargs={
                    'sections': [sections[index] for index in sectionIds],
                    'course': course
                }
            )

    def parseBuilding(self, response: scrapy.http.TextResponse, sections: List[dict], course: dict):
        # print(response.url)

        tableData = response.xpath('''
            //table[@class="datadisplaytable" and @summary="This layout table is used to present the sections found"]
            //td[@class="dddefault"]
            /table[@class="datadisplaytable" and @summary="This table lists the scheduled meeting times and assigned instructors for this class.."]
        ''')
        # print(tableData)

        # Using the reverse & pop method
        tableData.reverse()

        titles = response.xpath('''
            //table[@class="datadisplaytable" and @summary="This layout table is used to present the sections found"]
            //th[@class="ddtitle" and @scope="colgroup"]
            /a
            /text()
        ''').getall()
        # print(titles)

        # Some titles have '-' in them, so it's only possible to count backwards to get crn
        # For example:
        # 'Spc Topics in Chem Engr 1 - TOPIC: Biomaterials - 26537 - CHE 4591 - 01'
        # 'Flight 4 CP-AMEL - 26920 - AVF 2102 - 29
        # 'Flt Instructor-Airplane - 53802 - AVF 3001 - 05'
        # 'Human Fact in Man-Mach Systems - 80507 - AHF 5101 - 01'
        crns = [
            int(title.split('-')[-3].strip())
            for title in titles
        ]
        # print(crns)

        # Abort operation if some sections do not have table
        if len(tableData) != len(crns):
            print(f'Warning: {course["subject"]} {course["course"]} skipped because some sections do not have schedule table. Expected {len(crns)} tables, got {len(tableData)}.')
            return

        for crn in crns:
            locations: list = tableData.pop().xpath('''
                ./tr[position()>1]
                /td[@class="dddefault" and position()=4]
                /text()
            ''').getall()

            # Find places of the section
            # The order showed on the page may be different from the order in the data file
            places = None
            for section in sections:
                if section['crn'] == crn:
                    places: list = section['places']
                    break

            # Skip if there is no places
            if places is None:
                continue

            # Enumerate place and location to find matches
            for place in places:
                buildingCode: str = place[0]
                room: Optional[str] = place[1]

                if room is None:
                    continue

                yielded = False
                for location in locations:
                    if not location.endswith(room):
                        continue

                    if len(room) != 0:
                        buildingName = location[:-len(room)].strip()
                    else:
                        buildingName = location

                    yield {
                        'code': buildingCode,
                        'name': buildingName
                    }
                    yielded = True
                    break

                if not yielded:
                    print(f'Warning: {crn} did not yield because {locations} and {places} do not match.')
