from typing import List, Optional

import scrapy


class EmployeeSpider(scrapy.Spider):
    name = 'employee'
    allowed_domains = ['directory.fit.edu']
    start_urls = ['https://directory.fit.edu/department']

    employeeAttributes = [
        {
            'key': 'name',
            'xpath': 'td[1]/div[@class="name"]/b/text()'
        }, {
            'key': 'title',
            'xpath': 'td[1]/div[@class="title"]/text()'
        }, {
            'key': 'email',
            'xpath': 'td[2]/div[@class="email"]/a/text()'
        }, {
            'key': 'phone',
            'xpath': 'td[2]/div[@class="phone"]/a/text()'
        }, {
            'key': 'building',
            'xpath': 'td[3]/div[@class="building"]/text()'
        }, {
            'key': 'room',
            'xpath': 'td[3]/div[@class="room"]/text()'
        }
    ]

    # Goto each department page
    def parse(self, response: scrapy.http.TextResponse):
        departmentUrls = response.xpath('''
            //div[@class="twelve wide column"]
            /div[@class="ui list"]
            /a[@class="item"]
            /@href
        ''').getall()
        # print(departmentUrls)

        yield from response.follow_all(departmentUrls, callback=self.parseDepartment)

    # Parse employee info on department page
    def parseDepartment(self, response: scrapy.http.TextResponse):
        departmentCode = response.url[
            len('https://directory.fit.edu/department/'):
        ]

        employeeRows = response.xpath('''
            //div[@class="twelve wide column"]
            /table[@class="ui celled table" and position()=2]
            /tr
        ''')

        for employeeRow in employeeRows:
            employee = {
                'departmentCode': departmentCode
            }

            for attribute in self.employeeAttributes:
                key: str = attribute['key']
                xpath: str = attribute['xpath']

                value: Optional[str] = employeeRow.xpath(xpath).get()
                employee[key] = value

            # If room starts with 'Room: ', trim it
            room: Optional[str] = employee['room']
            if room is not None and room.startswith('Room: '):
                employee['room'] = room[len('Room: '):]

            # print(employee)
            yield employee
