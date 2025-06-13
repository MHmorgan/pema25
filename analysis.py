import csv
import statistics
import sys
from dataclasses import dataclass
from functools import partial
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np

from scoring import Scoring
from utils import *


class AvgMedian:
    def __init__(self, desc, with_ai, without):
        self.desc = desc
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

    def rows(self):
        return [
            [self.desc, 'Gjennomsnitt', fmt_num(self.mean_with_ai), fmt_num(self.mean_without)],
            [self.desc, 'Median', fmt_num(self.median_with_ai), fmt_num(self.median_without)],
        ]


def scoring_csv(with_ai: Scoring, without: Scoring, fout=sys.stdout):
    w = csv.writer(fout, delimiter=';')
    w.writerow(['Beskrivelse', 'Type', 'Med KI', 'Uten KI'])

    rows = AvgMedian(
        desc='Originalitet',
        with_ai=[s.original for s in with_ai],
        without=[s.original for s in without],
    ).rows()
    w.writerows(rows)

    rows = AvgMedian(
        desc='Gjennomførbarhet',
        with_ai=[s.plausible for s in with_ai],
        without=[s.plausible for s in without],
    ).rows()
    w.writerows(rows)

    rows = AvgMedian(
        desc='Potensiell effekt',
        with_ai=[s.effective for s in with_ai],
        without=[s.effective for s in without],
    ).rows()
    w.writerows(rows)

    rows = AvgMedian(
        desc='Total, gjennomsnitt',
        with_ai=[s.total() for s in with_ai],
        without=[s.total() for s in without],
    ).rows()
    w.writerows(rows)

    rows = AvgMedian(
        desc='Total, 60/20/20',
        with_ai=[s.total_weighted(.6, .2) for s in with_ai],
        without=[s.total_weighted(.6, .2) for s in without],
    ).rows()
    w.writerows(rows)

    rows = AvgMedian(
        desc='Total, 50/25/25',
        with_ai=[s.total_weighted(.5, .25) for s in with_ai],
        without=[s.total_weighted(.5, .25) for s in without],
    ).rows()
    w.writerows(rows)

    rows = AvgMedian(
        desc='Total, 50/20/30',
        with_ai=[s.total_weighted(.5, .2) for s in with_ai],
        without=[s.total_weighted(.5, .2) for s in without],
    ).rows()
    w.writerows(rows)

    rows = AvgMedian(
        desc='Total, 40/30/30',
        with_ai=[s.total_weighted(.4, .3) for s in with_ai],
        without=[s.total_weighted(.4, .3) for s in without],
    ).rows()
    w.writerows(rows)

    rows = AvgMedian(
        desc='Total, 40/20/40',
        with_ai=[s.total_weighted(.4, .2) for s in with_ai],
        without=[s.total_weighted(.4, .2) for s in without],
    ).rows()
    w.writerows(rows)


def scoring_report(with_ai: Scoring, without: Scoring, fout=sys.stdout):
    show = partial(print, file=fout)

    show('\nOriginalitet')
    am = AvgMedian(
        desc='Originalitet',
        with_ai=[s.original for s in with_ai],
        without=[s.original for s in without],
    )
    show(am)

    show('\nGjennomførbarhet')
    am = AvgMedian(
        desc='Gjennomførbarhet',
        with_ai=[s.plausible for s in with_ai],
        without=[s.plausible for s in without],
    )
    show(am)

    show('\nPotensiell effekt')
    am = AvgMedian(
        desc='Potensiell effekt',
        with_ai=[s.effective for s in with_ai],
        without=[s.effective for s in without],
    )
    show(am)

    # show('\nTotal, gjennomsnitt')
    # am = AvgMedian(
    #     name='Total, gjennomsnitt',
    #     with_ai=[s.total() for s in with_ai],
    #     without=[s.total() for s in without],
    # )
    # show(am)
    #
    # show('\nTotal, 40/30/30')
    # am = AvgMedian(
    #     name='Total, 40/30/30',
    #     with_ai=[s.total_weighted(.4, .3) for s in with_ai],
    #     without=[s.total_weighted(.4, .3) for s in without],
    # )
    # show(am)
    #
    # show('\nTotal, 40/20/40')
    # am = AvgMedian(
    #     name='Total, 40/20/40',
    #     with_ai=[s.total_weighted(.4, .2) for s in with_ai],
    #     without=[s.total_weighted(.4, .2) for s in without],
    # )
    # show(am)

    show('\nTotal, 60/20/20')
    am = AvgMedian(
        desc='Total, 60/20/20',
        with_ai=[s.total_weighted(.6, .2) for s in with_ai],
        without=[s.total_weighted(.6, .2) for s in without],
    )
    show(am)


@dataclass
class DataSet:
    label: str
    color: str
    values: list[float]


def bar_plot_single(
        name,
        values,
        label,
        title,
        ylabel,
        xlabel,
        xticklabels,
        rotation=90,
        figsize=(12, 8),
        bar_width=0.35
):
    plt.figure(figsize=figsize)
    x = list(range(len(values)))

    # Grid lines
    plt.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5)

    # Create bars
    plt.bar([i for i in x], values, width=bar_width, label=label)

    # Add labels, title and legend
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x, xticklabels, rotation=rotation)
    plt.legend()
    plt.tight_layout()

    # Write to file
    fout = outdir / f'{name}.png'
    plt.savefig(fout)
    debug(f'Wrote graph: {name}')


def bar_plot_compare_ai(
        name,
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
    plt.bar([i - bar_width / 2 for i in x], values_with_ai, width=bar_width, label='With AI')
    plt.bar([i + bar_width / 2 for i in x], values_without, width=bar_width, label='Without AI')

    # Add labels, title and legend
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x, xticklabels, rotation=rotation)
    plt.legend()
    plt.tight_layout()

    # Write to file
    fout = outdir / f'{name}.png'
    plt.savefig(fout)
    debug(f'Wrote graph: {name}')


def bar_plot_multiple(
        name,
        data_dict,
        title,
        ylabel,
        xlabel,
        xticklabels,
        rotation=90,
        figsize=(12, 8),
        bar_width=None
):
    """
    Create a bar plot with a variable number of bar groups.

    Parameters:
    -----------
    name : str
        Name for the output file
    data_dict : dict
        Dictionary where keys are labels and values are lists of data points
        Example: {'With AI': [1, 2, 3], 'Without AI': [0.5, 1.5, 2.5]}
    title : str
        Plot title
    ylabel : str
        Y-axis label
    xlabel : str
        X-axis label
    xticklabels : list
        Labels for x-axis ticks
    rotation : int, optional
        Rotation angle for x-axis labels (default: 90)
    figsize : tuple, optional
        Figure size (width, height) in inches (default: (12, 8))
    bar_width : float, optional
        Width of each bar. If None, automatically calculated based on number of groups
    """
    plt.figure(figsize=figsize)

    pprint(data_dict)

    # Get the number of groups and data points
    num_groups = len(data_dict)
    num_points = len(next(iter(data_dict.values())))

    # Calculate bar width if not provided
    if bar_width is None:
        bar_width = 0.8 / num_groups

    # Calculate positions for each group
    x = np.arange(num_points)

    # Calculate offset positions for each bar group
    offsets = np.linspace(-(num_groups - 1) / 2, (num_groups - 1) / 2, num_groups) * bar_width

    # Create bars for each data series
    for i, (label, values) in enumerate(data_dict.items()):
        plt.bar(x + offsets[i], values, width=bar_width, label=label)

    # Add labels, title and legend
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x, xticklabels, rotation=rotation)
    plt.legend()
    plt.tight_layout()

    # Write to file
    fout = outdir / f'{name}.png'
    plt.savefig(fout)
    debug(f'Wrote graph: {name}')


def line_plot(
        name,
        line_values,
        line_labels,
        title,
        ylabel,
        xlabel,
        xticklabels,
        rotation=90,
        figsize=(12, 8),
        marker_size=8
):
    plt.figure(figsize=figsize)

    # Create lines
    for (line, label) in zip(line_values, line_labels):
        x = list(range(len(line)))
        plt.plot(x, line, 'o-', label=label, markersize=marker_size)

    # Add labels, title and legend
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x, xticklabels, rotation=rotation)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Write to file
    fout = outdir / f'{name}.png'
    plt.savefig(fout)
    debug(f'Wrote graph: {name}')


def scatter_plot(
        name,
        line_values,
        line_labels,
        title,
        ylabel,
        xlabel,
        xticklabels,
        rotation=90,
        figsize=(12, 8),
        marker_size=8
):
    plt.figure(figsize=figsize)
    x = list(range(len(line_values[0])))

    # Create scatter plots for each line
    markers = ['o', 's', '^', 'D', 'v']

    for i, values in enumerate(line_values):
        marker = markers[i % len(markers)]
        label = line_labels[i] if i < len(line_labels) else f'Series {i + 1}'
        plt.scatter(x, values, label=label, s=marker_size * 10, marker=marker, alpha=0.7)

    # Add labels, title and legend
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x, xticklabels, rotation=rotation)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()

    # Write to file
    fout = outdir / f'{name}.png'
    plt.savefig(fout)
    debug(f'Wrote graph: {name}')
