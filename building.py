import json
import re
from dataclasses import asdict, astuple, dataclass, fields

from util import dataclassToJson
from typing import List

@dataclass(order=True)
class Building:
    code: str
    name: str


if __name__ == '__main__':
    departments: list = json.load(open('_department.raw.json', 'r'))
    employees: list = json.load(open('_employee.raw.json', 'r'))
    pawsBuildings: list = json.load(open('_pawsBuilding.raw.json', 'r'))

    buildingTexts = set()

    for department in departments:
        building: str = department['primaryLocation']
        if building is not None:
            buildingTexts.add(building)

    for employee in employees:
        building: str = employee['building']
        if building is not None:
            buildingTexts.add(building)

    for pawsBuilding in pawsBuildings:
        buildingTexts.add(f'{pawsBuilding["name"]} ({pawsBuilding["code"]})')

    buildings = []

    for buildingText in buildingTexts:
        try:
            duplets = re.match(r'(.+) \((\d{3}\w{3})\)', buildingText).groups()
            buildings.append(Building(name=duplets[0], code=duplets[1]))
        except AttributeError:
            pass

    dataclassToJson(Building, buildings, 'building')
