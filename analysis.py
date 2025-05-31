import csv
import statistics

from scoring import Scorings


class AvgMedian:
    def __init__(self, name, with_ai, without):
        self.name = name
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

    def write_csv(self, wr):
        wr.writerow([self.name, 'Mean', self.mean_with_ai, self.mean_without])
        wr.writerow([self.name, 'Median', self.median_with_ai, self.median_without])


def scoring_report(with_ai: Scorings, without: Scorings, file):
    wr = csv.writer(file, delimiter=';')
    wr.writerow(['Name', 'Type', 'With AI', 'Without AI'])

    print(f'With AI: {len(with_ai)}')
    print(f'Without: {len(without)}')

    print('\nOriginalitet')
    am = AvgMedian(
        name='Originalitet',
        with_ai=[s.original for s in with_ai],
        without=[s.original for s in without],
    )
    print(am)
    am.write_csv(wr)

    print('\nGjennomførbarhet')
    am = AvgMedian(
        name='Gjennomførbarhet',
        with_ai=[s.plausible for s in with_ai],
        without=[s.plausible for s in without],
    )
    print(am)
    am.write_csv(wr)

    print('\nPotensiell effekt')
    am = AvgMedian(
        name='Potensiell effekt',
        with_ai=[s.effective for s in with_ai],
        without=[s.effective for s in without],
    )
    print(am)
    am.write_csv(wr)

    print('\nTotal, gjennomsnitt')
    am = AvgMedian(
        name='Total, gjennomsnitt',
        with_ai=[s.total() for s in with_ai],
        without=[s.total() for s in without],
    )
    print(am)
    am.write_csv(wr)

    print('\nTotal, 40/30/30')
    am = AvgMedian(
        name='Total, 40/30/30',
        with_ai=[s.total_weighted(.4, .3) for s in with_ai],
        without=[s.total_weighted(.4, .3) for s in without],
    )
    print(am)
    am.write_csv(wr)

    print('\nTotal, 40/20/40')
    am = AvgMedian(
        name='Total, 40/20/40',
        with_ai=[s.total_weighted(.4, .2) for s in with_ai],
        without=[s.total_weighted(.4, .2) for s in without],
    )
    print(am)
    am.write_csv(wr)

    print('\nTotal, 60/20/20')
    am = AvgMedian(
        name='Total, 60/20/20',
        with_ai=[s.total_weighted(.6, .2) for s in with_ai],
        without=[s.total_weighted(.6, .2) for s in without],
    )
    print(am)
    am.write_csv(wr)

