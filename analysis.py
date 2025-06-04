import csv
import statistics
from dataclasses import dataclass

from scoring import Scoring

import matplotlib.pyplot as plt


class AvgMedian:
    def __init__(self, name, with_ai, without):
        self.mean_with_ai = statistics.mean(with_ai)
        self.mean_without = statistics.mean(without)
        self.median_with_ai = statistics.median(with_ai)
        self.median_without = statistics.median(without)

    def __str__(self):
        return (
                f'       With AI vs. Without\n' +
                f'Mean   = {self.mean_with_ai:>5.02f}     {self.mean_without:.02f}\n' +
                f'Median = {self.median_with_ai:>5.02f}     {self.median_without:.02f}'
        )


def scoring_report(with_ai: Scoring, without: Scoring):
    print(f'With AI: {len(with_ai)}')
    print(f'Without: {len(without)}')

    print('\nOriginalitet')
    am = AvgMedian(
        name='Originalitet',
        with_ai=[s.original for s in with_ai],
        without=[s.original for s in without],
    )
    print(am)

    print('\nGjennomførbarhet')
    am = AvgMedian(
        name='Gjennomførbarhet',
        with_ai=[s.plausible for s in with_ai],
        without=[s.plausible for s in without],
    )
    print(am)

    print('\nPotensiell effekt')
    am = AvgMedian(
        name='Potensiell effekt',
        with_ai=[s.effective for s in with_ai],
        without=[s.effective for s in without],
    )
    print(am)

    # print('\nTotal, gjennomsnitt')
    # am = AvgMedian(
    #     name='Total, gjennomsnitt',
    #     with_ai=[s.total() for s in with_ai],
    #     without=[s.total() for s in without],
    # )
    # print(am)
    #
    # print('\nTotal, 40/30/30')
    # am = AvgMedian(
    #     name='Total, 40/30/30',
    #     with_ai=[s.total_weighted(.4, .3) for s in with_ai],
    #     without=[s.total_weighted(.4, .3) for s in without],
    # )
    # print(am)
    #
    # print('\nTotal, 40/20/40')
    # am = AvgMedian(
    #     name='Total, 40/20/40',
    #     with_ai=[s.total_weighted(.4, .2) for s in with_ai],
    #     without=[s.total_weighted(.4, .2) for s in without],
    # )
    # print(am)

    print('\nTotal, 60/20/20')
    am = AvgMedian(
        name='Total, 60/20/20',
        with_ai=[s.total_weighted(.6, .2) for s in with_ai],
        without=[s.total_weighted(.6, .2) for s in without],
    )
    print(am)


@dataclass
class DataSet:
    label: str
    color: str
    values: list[float]


def bar_plot(
        values_with_ai,
        values_without,
        title,
        ylabel,
        xlabel,
        xticklabels,
        rotation=90,
        figsize=(12, 8),
        bar_width=0.35
):
    plt.figure(figsize=figsize)
    x = list(range(len(values_with_ai)))

    # Create bars
    plt.bar([i - bar_width / 2 for i in x], values_with_ai,
            width=bar_width, label='With AI', color='skyblue')
    plt.bar([i + bar_width / 2 for i in x], values_without,
            width=bar_width, label='Without AI', color='lightcoral')

    # Add labels, title and legend
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x, xticklabels, rotation=rotation)
    plt.legend()
    plt.tight_layout()
    plt.show()
