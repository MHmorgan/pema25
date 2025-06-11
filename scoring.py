from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
import csv
import statistics

from answers import Answer
from utils import debug

D_SCORING = Path('data/scoring/')


@dataclass
class Scoring(list):
    def __init__(self, rows: Iterable['ScoringEntry']):
        super().__init__(sorted(rows, key=lambda row: row.number))

    @classmethod
    def from_csv(cls, rows, answers: Iterable[Answer]):
        return cls(ScoringEntry.from_csv(row, answers) for row in rows)

    @classmethod
    def from_median(cls, lst: Iterable['Scoring']):
        scoring = [
            ScoringEntry.from_median(zipped)
            for zipped in zip(*lst)
        ]
        return cls(scoring)

    def find(self, number) -> 'ScoringEntry':
        for score in self:
            if score.number == number:
                return score
        raise KeyError(number)

    def with_ai(self) -> 'Scoring':
        return Scoring(s for s in self if s.answer.used_ai)

    def without_ai(self) -> 'Scoring':
        return Scoring(s for s in self if not s.answer.used_ai)

    def answers(self) -> list[Answer]:
        return [s.answer for s in self]

    def original_mean(self, answers: Iterable[Answer]):
        nums = [self.find(ans.number).original for ans in answers]
        return statistics.mean(nums)

    def plausible_mean(self, answers: Iterable[Answer]):
        nums = [self.find(ans.number).plausible for ans in answers]
        return statistics.mean(nums)

    def effective_mean(self, answers: Iterable[Answer]):
        nums = [self.find(ans.number).effective for ans in answers]
        return statistics.mean(nums)


@dataclass
class ScoringEntry:
    answer: Answer
    number: int
    original: int
    plausible: int
    effective: int

    @classmethod
    def from_csv(cls, row, answers: Iterable[Answer]):
        assert len(row) == 15, f'Expected 15 columns in scoring, got {len(row)}'

        number = int(row[0])
        idea1 = row[1]
        original = int(row[-4])
        plausible = int(row[-3])
        effective = int(row[-2])

        for ans in answers:
            if ans.idea1 == idea1:
                answer = ans.numbered(number)
                break
        else:
            raise ValueError(f'Idea {number} not found in answers :: {idea1}')

        return cls(answer, number, original, plausible, effective)

    @classmethod
    def from_median(cls, scoring: tuple['ScoringEntry']):
        answer = scoring[0].answer
        number = scoring[0].number
        for s in scoring[1:]:
            assert s.answer.id == answer.id
            assert s.number == number

        original = statistics.median_high([s.original for s in scoring])
        plausible = statistics.median_high([s.plausible for s in scoring])
        effective = statistics.median_high([s.effective for s in scoring])

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


def read_scorings(answers) -> dict[str, Scoring]:
    result = {}

    for file_path in D_SCORING.glob('*.csv'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                rd = csv.reader(f, delimiter=';')

                # Skip the header row
                next(rd)

                scoring = Scoring.from_csv(rd, answers)
                result[file_path.stem] = scoring
                debug(f'Read {len(scoring)} scorings from {file_path}')
        except Exception as e:
            raise Exception(f'Error parsing {file_path}: {e}') from e

    return result
