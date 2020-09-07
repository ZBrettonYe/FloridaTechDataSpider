import json
from dataclasses import dataclass

from util import dataclassToJson


@dataclass
class Tag:
    code: str
    name: str

    def __lt__(self, t):
        return self.code < t.code


# https://catalog.fit.edu/content.php?catoid=9&navoid=367
presetTags = [
    ['CC', 'Cross-cultural'],
    ['CL', 'Computer Literacy Requirement'],
    ['COM', 'Communication Elective'],
    ['HON', 'Honors Sections'],
    ['HU', 'Humanities Elective'],
    ['LA', 'Liberal Arts Elective'],
    ['Q', 'Scholarly Inquiry Requirement'],
    ['SS', 'Social Science Elective']
]

if __name__ == '__main__':
    tags = [
        Tag(code=presetTag[0], name=presetTag[1])
        for presetTag in presetTags
    ]

    dataclassToJson(Tag, tags, 'tag')
