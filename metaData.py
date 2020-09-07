import json
import os
from datetime import datetime
from typing import List

fileNames = [
    'building.min.json',
    'campus.min.json',
    'course3.min.json',
    'courseAttribute.min.json',
    'department.min.json',
    'description.min.json',
    'employee.min.json',
    'level.min.json',
    'note.min.json',
    'prerequisite.min.json',
    'requirement.min.json',
    'restriction.min.json',
    'scheduleType.min.json',
    'section.min.json',
    'session.min.json',
    'subject.min.json',
    'tag.min.json',
    'title.min.json'
]


if __name__ == '__main__':
    # Collect file sizes
    fileSizes = {}
    for fileName in fileNames:
        size = os.path.getsize(fileName)
        fileSizes[fileName] = size

    # Collect years from sections
    years = [-1, -1, -1]
    sections: List[dict] = json.load(open('section.json', 'r'))
    for section in sections:
        year: int = section['year']
        semesterId: int = section['semesterId']

        if years[semesterId] == -1:
            years[semesterId] = year

        # Exit when all 3 years has been collected
        if -1 not in years:
            break

    metaData = {
        'fileSizes': fileSizes,
        'timestamp': datetime.now().timestamp(),
        'years': years
    }

    json.dump(metaData, open('metaData.json', 'w'), indent=4)
    json.dump(metaData, open('metaData.min.json', 'w'), separators=(',', ':'))
