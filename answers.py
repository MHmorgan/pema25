import csv
from collections.abc import Iterable

import arrow

from extra import CategoryEntry, Categories
from utils import *

F_ANSWERS = Path('data/alle-svar.csv')


def float_no(s):
    try:
        return float(s.replace(',', '.'))
    except ValueError:
        return 0.0


class Answer:
    def __init__(self, row):
        self.row = row

        assert len(row) == 104, f'Expected 104 columns in answers, got {len(row)}'

        self.start_date = arrow.get(row[0], 'M/D/YY H:mm')
        self.end_date = arrow.get(row[1], 'M/D/YY H:mm')
        self.progress_percent = int(row[4])
        self.duration_seconds = int(row[5])
        self.finished = bool(row[6])
        self.recorded_date = arrow.get(row[7], 'M/D/YY H:mm')
        self.id = row[8]

        self.idea1 = row[19] or row[53]
        self.idea2 = row[20] or row[54]
        self.idea3 = row[21] or row[55]
        self.idea4 = row[22] or row[56]
        self.idea5 = row[23] or row[57]

        self.difficulty = row[44] or row[78]

        self.time_brainstorm = float_no(row[26] or row[60])
        self.time_description = float_no(row[32] or row[66])
        self.time_effect = float_no(row[39] or row[73])
        self.time_total = self.time_brainstorm + self.time_description + self.time_effect

        # How they used AI when answering
        self.ans_usages = row[46] or row[79]
        if self.ans_usages:
            self.ans_usages = self.ans_usages.split(',')

        # How much they use AI at work
        self.work_usage = row[83]

        self.ai_use_exploration = row[86]
        self.ai_use_videreutvikling = row[87]
        self.ai_use_search = row[88]

        self.ai_time_saved = row[91]
        self.ai_quality = row[92]
        self.ai_critical = row[93]
        self.ai_knowledge = row[95]
        self.ai_education = row[96]
        self.age = row[97]
        self.experience = row[98]
        self.sex = row[99]
        self.department = row[100]
        self.education_level = row[101]
        self.role = row[102]

        try:
            self.original = int(row[41] or row[75])
            self.plausible = int(row[42] or row[76])
            self.effective = int(row[43] or row[77])
        except ValueError:
            self.original = 0
            self.plausible = 0
            self.effective = 0

        self.used_ai = row[-1] == 'AI'

        self._number = None
        self._category = None
        self._ideas = None

    @property
    def number(self):
        if self._number is None:
            raise ValueError('Number not set for this answer')
        return self._number

    @number.setter
    def number(self, value):
        self._number = value

    def numbered(self, value):
        self._number = value
        return self

    @property
    def category(self):
        if self._category is None:
            raise ValueError('Category not set for this answer')
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    @property
    def ideas(self):
        if self._ideas is None:
            raise ValueError('Ideas not set for this answer')
        return self._ideas

    @ideas.setter
    def ideas(self, value):
        self._ideas = value

    def categorized(self, category: CategoryEntry):
        self._category = category.category
        self._ideas = category.ideas
        return self

    @property
    def ai_knowledge_rated(self):
        rating_map = {
            'Ingen kunnskap': 0,
            'Litt kunnskap': 1,
            'Moderat kunnskap': 2,
            'God kunnskap': 3,
            'Svært god kunnskap': 4
        }
        return rating_map[self.ai_knowledge]

    @property
    def ai_critical_rated(self):
        rating_map = {
            '': 0,
            'I ingen grad': 1,
            'I liten grad': 1,
            'I middels grad': 2,
            'I stor grad': 3,
            'I svært stor grad': 4
        }
        return rating_map[self.ai_critical]

    @property
    def work_usage_rated(self):
        rating_map = {
            '': 0,
            'I ingen grad': 1,
            'I liten grad': 1,
            'I middels grad': 2,
            'I stor grad': 3,
            'I svært stor grad': 4
        }
        return rating_map[self.work_usage]

    ai_use_rating_map = {
        '': 0,
        '1 - ingen grad': 1,
        '2 - liten grad': 2,
        '3 - middels grad': 3,
        '4 - stor grad': 4,
        '5 - Veldig stor grad': 5
    }

    @property
    def ai_use_exploration_rated(self):
        return self.ai_use_rating_map[self.ai_use_exploration]

    @property
    def ai_use_videreutvikling_rated(self):
        return self.ai_use_rating_map[self.ai_use_videreutvikling]

    @property
    def ai_use_search_rated(self):
        return self.ai_use_rating_map[self.ai_use_search]


def categorize(answers: Iterable[Answer], categories: Categories) -> list[Answer]:
    """
    Use the `categories` to categorize all the given answers.

    If an answer isn't categorized, this will fail.
    """
    return [ans.categorized(categories[ans.id]) for ans in answers]


def read_answers() -> list[Answer]:
    """
    Read all answers from the CSV file in the data folder.
    """

    with open(F_ANSWERS, 'r', encoding='utf-8') as f:
        rd = csv.reader(f, delimiter=';')

        # Skip the first two rows
        next(rd)
        next(rd)

        res = [Answer(row) for row in rd]
        debug(f'Read {len(res)} answers from {F_ANSWERS}')
        return res


def distinct(answers: Iterable[Answer], getkey) -> list:
    return list({getkey(ans) for ans in answers})


def experiment_usages(answers: Iterable[Answer]):
    """
    Return pairs of (<category>, <count>) for how the respondents
    used AI when solving the experiment.
    """
    res = {}
    for ans in answers:
        for cat in ans.ans_usages:
            cnt = res.setdefault(cat, 0)
            res[cat] = cnt + 1
    return [(cat, cnt) for cat, cnt in res.items()]
