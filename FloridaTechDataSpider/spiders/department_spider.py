import scrapy


class DepartmentSpider(scrapy.Spider):
    name = 'department'
    allowed_domains = ['directory.fit.edu']
    start_urls = ['https://directory.fit.edu/department']

    departmentAttributes = [
        {
            'header': 'Phone',
            'xpath': 'a/text()',
            'key': 'phone'
        }, {
            'header': 'Fax',
            'xpath': 'text()',
            'key': 'fax'
        }, {
            'header': 'Email',
            'xpath': 'a/text()',
            'key': 'email'
        }, {
            'header': 'Website',
            'xpath': 'a/text()',
            'key': 'website'
        }, {
            'header': 'Primary Location',
            'xpath': 'text()',
            'key': 'primaryLocation'
        }
    ]

    def parse(self, response: scrapy.http.TextResponse):
        departmentUrls = response.xpath('''
            //div[@class="twelve wide column"]
            /div[@class="ui list"]
            /a[@class="item"]
            /@href
        ''').getall()
        # print(departmentUrls)

        yield from response.follow_all(departmentUrls, callback=self.parseDepartment)

    def parseDepartment(self, response: scrapy.http.TextResponse):
        # print(response.url)

        # It's not guaranteed all fields are present on the page
        headers = response.xpath('''
            //div[@class="twelve wide column"]
            /table[@class="ui celled table" and position()=1]
            //th
            /text()
        ''').getall()
        # print(headers)

        tdTags = response.xpath('''
            //div[@class="twelve wide column"]
            /table[@class="ui celled table" and position()=1]
            //td
        ''')
        # print(data)

        name: str = response.xpath('''
            //div[@class="twelve wide column"]
            /h2
            /text()
        ''').get()

        department = {
            'name': name,
            'code': response.url[len('https://directory.fit.edu/department/'):]
        }

        for attribute in self.departmentAttributes:
            header: str = attribute['header']
            xpath: str = attribute['xpath']
            key: str = attribute['key']

            # If we don't see the header, set field to default value
            if header not in headers:
                department[key] = None
                continue

            # Otherwise extract the string
            index = headers.index(header)
            value = tdTags[index].xpath(xpath).get()
            department[key] = value

        # print(department)
        yield department
