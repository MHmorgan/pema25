from dataclasses import dataclass
from pathlib import Path
import csv
import statistics

from IPython.utils.timing import clocks

from answers import Answers, Answer
from utils import debug

D_SCORING = Path('data/scoring/')


@dataclass
class Scorings(list):
    def __init__(self, rows):
        super().__init__(sorted(rows, key=lambda row: row.number))

    @classmethod
    def from_csv(cls, rows, answers: Answers):
        return cls([Scoring.from_csv(row, answers) for row in rows])

    @classmethod
    def from_median(cls, lst: list['Scorings']):
        scorings = [
            Scoring.from_median(zipped)
            for zipped in zip(*lst)
        ]
        return cls(scorings)

    def with_ai(self):
        return Scorings([s for s in self if s.answer.used_ai])

    def without_ai(self):
        return Scorings([s for s in self if not s.answer.used_ai])


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

    @classmethod
    def from_median(cls, scorings: tuple['Scoring']):
        answer = scorings[0].answer
        number = scorings[0].number
        for s in scorings[1:]:
            assert s.answer == answer
            assert s.number == number

        original = statistics.median_high([s.original for s in scorings])
        plausible = statistics.median_high([s.plausible for s in scorings])
        effective = statistics.median_high([s.effective for s in scorings])

        return cls(answer, number, original, plausible, effective)

    @classmethod
    def from_answer(cls, answer: Answer, number: int):
        return cls(
            answer=answer,
            number=number,
            original=answer.original,
            plausible=answer.plausible,
            effective=answer.effective,
        )

    def total(self):
        return (self.original + self.plausible + self.effective) / 3

    def total_weighted(self, wo, wp):
        we = 1.0 - wo - wp
        return self.original * wo + self.plausible * wp + self.effective * we


def read_scorings(answers) -> dict[str, Scorings]:
    result = {}

    for file_path in D_SCORING.glob('*.csv'):
        with open(file_path, 'r', encoding='utf-8') as f:
            rd = csv.reader(f, delimiter=';')

            # Skip the header row
            next(rd)

            scorings = Scorings.from_csv(rd, answers)
            result[file_path.stem] = scorings
            debug(f'Read {len(scorings)} scorings from {file_path}')

    return result
