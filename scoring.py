from dataclasses import dataclass
from pathlib import Path
import csv

from answers import Answers
from utils import debug

D_SCORING = Path('data/scoring/')


@dataclass
class Scorings:
    rows: list['Scoring']

    @classmethod
    def from_csv(cls, rows, answers: Answers):
        cls([Scoring.from_csv(row, answers) for row in rows])

    def __iter__(self):
        return iter(self.rows)


@dataclass
class Scoring:
    id: str
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
                id = ans.id
                break
        else:
            raise ValueError(f'Idea {number} not found in answers :: {idea1}')

        return cls(id, original, plausible, effective)


def read_scorings(answers) -> dict[str, Scorings]:
    result = {}

    for file_path in D_SCORING.glob('*.csv'):
        with open(file_path, 'r', encoding='utf-8') as f:
            rd = csv.reader(f, delimiter=';')

            # Skip the header row
            next(rd)

            scorings = Scorings(rd, answers)
            result[file_path.stem] = scorings
            debug(f'Read {len(scorings.rows)} scorings from {file_path}')

    return result
