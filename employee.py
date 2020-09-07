import bisect
import json
import re
from dataclasses import asdict, astuple, dataclass, fields

from util import dataclassToJson


@dataclass
class Employee:
    name: str
    title: str
    email: str
    phone: str
    buildingId: int
    room: str
    departmentId: int

    def __lt__(self, e) -> bool:
        return self.email < e.email


# https://docs.python.org/3/library/bisect.html#searching-sorted-lists
def bisectIndex(ls: list, value):
    if value is None:
        return -1

    index = bisect.bisect_left(ls, value)
    if index != len(ls) and ls[index] == value:
        return index

    return -1


if __name__ == '__main__':
    buildings = [b['code'] for b in json.load(open('building.json', 'r'))]
    departments = [d['code'] for d in json.load(open('department.json', 'r'))]
    titles: list = json.load(open('title.json', 'r'))
    sections: list = json.load(open('_pawsSection.raw.json', 'r'))

    employees: list = json.load(open('_employee.raw.json', 'r'))

    emails = []
    for employee in employees:
        try:
            buildingText: str = employee['building']
            duplets = re.match(r'(.+) \((\d{3}\w{3})\)', buildingText).groups()
            buildingCode = duplets[1]
        except TypeError:
            buildingCode = None
        employee['buildingId'] = bisectIndex(buildings, buildingCode)

        departmentCode = employee['departmentCode']
        employee['departmentId'] = bisectIndex(departments, departmentCode)

        emails.append(employee['email'])

    emails.sort()

    for section in sections:
        if section['instructor'] is None:
            continue

        name: str = section['instructor'][0]
        email: str = section['instructor'][1]

        if name != '' and bisectIndex(emails, email) == -1:
            employees.append({
                'name': name,
                'title': None,
                'email': email,
                'phone': None,
                'buildingId': None,
                'room': None,
                'departmentId': None
            })
            bisect.insort(emails, email)

    keys = [f.name for f in fields(Employee)]
    employees = [
        Employee(**{key: e[key] for key in keys})
        for e in employees
    ]

    dataclassToJson(Employee, employees, 'employee')

    # employees.sort()
    # values = [list(astuple(e)) for e in employees]

    # json.dump(
    #     [asdict(e) for e in employees],
    #     open('employee.json', 'w'),
    #     indent=4
    # )
    # json.dump(
    #     {'keys': keys, 'values': values},
    #     open('employee.min.json', 'w'),
    #     separators=(',', ':')
    # )
