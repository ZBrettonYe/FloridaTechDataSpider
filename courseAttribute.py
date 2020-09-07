import json
from util import listToJson

if __name__ == '__main__':
    courses: list = json.load(open('_pawsCourse.raw.json', 'r'))

    courseAttributes = set()
    for course in courses:
        courseAttributes.update(course['courseAttributes'])

    courseAttributes = list(courseAttributes)

    listToJson(courseAttributes, 'courseAttribute')
