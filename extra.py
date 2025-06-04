import csv
from pathlib import Path

from utils import debug

F_CATEGORIES = Path('data/category.csv')


class Categories(list):
    def __init__(self, rows):
        super().__init__(CategoryEntry(r) for r in rows)

    def __getitem__(self, item) -> 'CategoryEntry':
        for entry in self:
            if entry.id == item:
                return entry
        raise KeyError(item)

    def category_names(self) -> list[str]:
        return sorted({e.category for e in self})


class CategoryEntry:
    id: str
    number: int
    category: str
    ideas: int

    def __init__(self, row):
        self.id = row[0]
        self.number = int(row[1])
        self.category = row[2]
        self.ideas = int(row[3])


def read_categories() -> Categories:
    with open(F_CATEGORIES, 'r', encoding='utf-8') as f:
        rd = csv.reader(f, delimiter=';')

        # Skip the header row
        next(rd)

        res = Categories(rd)
        debug(f'Read {len(res)} categories from {F_CATEGORIES}')
        return res
