from collections.abc import Iterable
from pathlib import Path
import csv

import arrow

from extra import CategoryEntry, Categories
from utils import *

F_ANSWERS = Path('data/alle-svar.csv')


class Answers:
    def __init__(self, rows):
        self.answers = [Answer(row) for row in rows]

    def __iter__(self):
        return iter(self.answers)

    def __len__(self):
        return len(self.answers)


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

        try:
            self.original = int(row[41] or row[75])
            self.plausible = int(row[42] or row[76])
            self.effective = int(row[43] or row[77])
        except ValueError:
            self.original = 0
            self.plausible = 0
            self.effective = 0

        self.used_ai = row[-1] == 'AI'


class AnswerNumbered(Answer):
    def __init__(self, row, number):
        super().__init__(row)
        self.number = number


class AnswerCategorized(Answer):
    def __init__(self, row, cat: CategoryEntry):
        super().__init__(row)
        self.number = cat.number
        self.category = cat.category
        self.ideas = cat.ideas


def categorize(
        answers: Iterable[Answer],
        categories: Categories,
) -> list[AnswerCategorized]:
    return [
        AnswerCategorized(ans.row, categories[ans.id])
        for ans in answers
    ]


def read_answers() -> Answers:
    with open(F_ANSWERS, 'r', encoding='utf-8') as f:
        rd = csv.reader(f, delimiter=';')

        # Skip the first two rows
        next(rd)
        next(rd)

        res = Answers(rd)
        debug(f'Read {len(res.answers)} answers from {F_ANSWERS}')
        return res
