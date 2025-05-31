from dataclasses import dataclass
from pathlib import Path
import csv

from answers import Answers, Answer
from utils import debug

D_SCORING = Path('data/scoring/')


@dataclass
class Scorings:
    rows: list['Scoring']

    def __init__(self, rows):
        self.rows = sorted(rows, key=lambda row: row.number)

    def __iter__(self):
        return iter(self.rows)

    @classmethod
    def from_csv(cls, rows, answers: Answers):
        return cls([Scoring.from_csv(row, answers) for row in rows])

    def with_ai(self):
        return Scorings([s for s in self.rows if s.answer.used_ai])

    def without_ai(self):
        return Scorings([s for s in self.rows if not s.answer.used_ai])


@dataclass
class Scoring:
    answer: Answer
    number: int
    original: int
    plausible: int
    effective: int

    @classmethod
    def from_csv(cls, row, answers: Answers):
        assert len(row) == 15, f'Expected 15 columns in scoring, got {len(row)}'

        number = int(row[0])
        idea1 = row[1]
        original = int(row[-4])
        plausible = int(row[-3])
        effective = int(row[-2])

        for ans in answers:
            if ans.idea1 == idea1:
                answer = ans
                break
        else:
            raise ValueError(f'Idea {number} not found in answers :: {idea1}')

        return cls(answer, number, original, plausible, effective)


def read_scorings(answers) -> dict[str, Scorings]:
    result = {}

    for file_path in D_SCORING.glob('*.csv'):
        with open(file_path, 'r', encoding='utf-8') as f:
            rd = csv.reader(f, delimiter=';')

            # Skip the header row
            next(rd)

            scorings = Scorings.from_csv(rd, answers)
            result[file_path.stem] = scorings
            debug(f'Read {len(scorings.rows)} scorings from {file_path}')

    return result
