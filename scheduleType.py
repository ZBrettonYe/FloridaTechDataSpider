import json

from util import listToJson

if __name__ == '__main__':
    courses: list = json.load(open('_pawsCourse.raw.json', 'r'))

    scheduleTypes = set()
    for course in courses:
        scheduleTypes.update(course['scheduleTypes'])

    scheduleTypes = list(scheduleTypes)

    listToJson(scheduleTypes, 'scheduleType')
