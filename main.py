from functools import partial
from pprint import pprint, pformat

import answers
import analysis
import extra
from scoring import *
from utils import *

import numpy as np
import pandas as pd
from scipy import stats

info('Reading input data...')
# All answers known to Qualtrics. Includes irrelevant answers.
# At this point the answers is lacking numbers and categories.
all_answers = answers.read_answers()

# All scorings done by the authors and experts.
scorings = read_scorings(all_answers)

debug(f'Scorings: {scorings.keys()}')

# Use first scoring to determine which answers are relevant
for scoring in scorings.values():
    scored_answers = [ans for ans in scoring.answers()]
    scored_with_ai = [ans for ans in scoring.with_ai().answers()]
    scored_without = [ans for ans in scoring.without_ai().answers()]
    break

debug(f'Scored answers: {len(scored_answers)}')

categories = extra.read_categories()
category_names = categories.category_names()
debug(f'Distinct categories: {len(category_names)}')

# All relevant answers, enriched with all necessary data.
categorized_answers = answers.categorize(scored_answers, categories)
categorized_with_ai = answers.categorize(scored_with_ai, categories)
categorized_without = answers.categorize(scored_without, categories)
debug(f'Categorized answers: {len(scored_answers)}')
debug(f'With AI: {len(categorized_with_ai)}')
debug(f'Without: {len(categorized_without)}')

# All relevant AI answers, grouped by category.
categorized_with_ai_grouped = {}
for ans in categorized_with_ai:
    categorized_with_ai_grouped.setdefault(ans.category, []).append(ans)

# All relevant non-AI answers, grouped by category.
categorized_without_grouped = {}
for ans in categorized_without:
    categorized_without_grouped.setdefault(ans.category, []).append(ans)

# ------------------------------------------------------------------------------
#
# AI vs. uten AI
# Sammenligning av vurderingskriterier mellom AI og ikke-AI svar.
#
# ------------------------------------------------------------------------------

author_scorings = [
    scorings['pernille'],
    scorings['trine'],
    scorings['kristoffer'],
    scorings['thomas'],
]
author_scoring_median = Scoring.from_median(author_scorings)
author_scoring_mean = Scoring.from_mean(author_scorings)

expert_scorings = [
    scorings['zia'],
    scorings['monique'],
]
expert_scoring_median = Scoring.from_median(expert_scorings)
expert_scoring_mean = Scoring.from_mean(expert_scorings)

total_scoring = author_scorings + expert_scorings
total_scoring_median = Scoring.from_median(total_scoring)
total_scoring_mean = Scoring.from_mean(total_scoring)

felles_scoring = scorings['felles']

# --------------------------------------
# Median scoring
# --------------------------------------

info('Scoring authors - median')
with open(outdir / 'median-scoring-authors.csv', 'w') as f:
    analysis.scoring_csv(
        with_ai=author_scoring_median.with_ai(),
        without=author_scoring_median.without_ai(),
        fout=f
    )

info('Scoring authors - median')
with open(outdir / 'mean-scoring-authors.csv', 'w') as f:
    analysis.scoring_csv(
        with_ai=author_scoring_mean.with_ai(),
        without=author_scoring_mean.without_ai(),
        fout=f
    )

info('Scoring expert - median')
with open(outdir / 'median-scoring-expert.csv', 'w') as f:
    analysis.scoring_csv(
        with_ai=expert_scoring_median.with_ai(),
        without=expert_scoring_median.without_ai(),
        fout=f
    )

info('Scoring expert - mean')
with open(outdir / 'mean-scoring-expert.csv', 'w') as f:
    analysis.scoring_csv(
        with_ai=expert_scoring_mean.with_ai(),
        without=expert_scoring_mean.without_ai(),
        fout=f
    )

info('Scoring total - median')
with open(outdir / 'median-scoring-total.csv', 'w') as f:
    analysis.scoring_csv(
        with_ai=total_scoring_median.with_ai(),
        without=total_scoring_median.without_ai(),
        fout=f
    )

info('Scoring total - mean')
with open(outdir / 'mean-scoring-total.csv', 'w') as f:
    analysis.scoring_csv(
        with_ai=total_scoring_mean.with_ai(),
        without=total_scoring_mean.without_ai(),
        fout=f
    )

# --------------------------------------
# Self-evaluation
# --------------------------------------

info('Self-evaluation scoring')
self_evals = Scoring(
    ScoringEntry.from_answer(ans, ans.number)
    for ans in scored_answers
)

with open(outdir / 'self-evaluation.csv', 'w') as f:
    analysis.scoring_csv(
        with_ai=self_evals.with_ai(),
        without=self_evals.without_ai(),
        fout=f
    )

# ------------------------------------------------------------------------------
#
# Category Count
# Counting the answers for each category. Plot the distribution.
#
# ------------------------------------------------------------------------------

info('Category distribution')
with_ai_count = {k: len(g) for k, g in categorized_with_ai_grouped.items()}
without_count = {k: len(g) for k, g in categorized_without_grouped.items()}

analysis.bar_plot_compare_ai(
    name='kategori-distribusjon',
    values_with_ai=[with_ai_count.get(cat, 0) for cat in category_names],
    values_without=[without_count.get(cat, 0) for cat in category_names],
    title='Distribusjon kategori: Med KI vs uten KI',
    ylabel='Antall',
    xlabel='Kategorier',
    xticklabels=category_names,
)

# ------------------------------------------------------------------------------
#
# Category Scoring
# Plot the scoring per category, for different scorers.
#
# ------------------------------------------------------------------------------

info('Originality distribution - authors')

with_ai_original = {
    category: author_scoring_mean.original_mean(answers)
    for category, answers in categorized_with_ai_grouped.items()
}

without_original = {
    category: author_scoring_mean.original_mean(answers)
    for category, answers in categorized_without_grouped.items()
}

analysis.scatter_plot(
    name='category-original-authors',
    line_values=[
        [with_ai_original.get(cat, None) for cat in category_names],
        [without_original.get(cat, None) for cat in category_names],
    ],
    line_labels=['Med KI', 'Uten KI'],
    title='Kategori, Originalitet: Med KI vs uten KI (forfattere)',
    ylabel='Antall',
    xlabel='Kategorier',
    xticklabels=category_names,
)

info('Originality distribution - experts')

with_ai_original = {
    category: expert_scoring_mean.original_mean(answers)
    for category, answers in categorized_with_ai_grouped.items()
}

without_original = {
    category: expert_scoring_mean.original_mean(answers)
    for category, answers in categorized_without_grouped.items()
}

analysis.scatter_plot(
    name='category-original-expert',
    line_values=[
        [with_ai_original.get(cat, None) for cat in category_names],
        [without_original.get(cat, None) for cat in category_names],
    ],
    line_labels=['Med KI', 'Uten KI'],
    title='Kategory, Originalitet: Med KI vs uten KI (eksperter)',
    ylabel='Antall',
    xlabel='Kategorier',
    xticklabels=category_names,
)

info('Originality distribution - totals')

with_ai_original = {
    category: total_scoring_mean.original_mean(answers)
    for category, answers in categorized_with_ai_grouped.items()
}

without_original = {
    category: total_scoring_mean.original_mean(answers)
    for category, answers in categorized_without_grouped.items()
}

analysis.scatter_plot(
    name='category-original-total',
    line_values=[
        [with_ai_original.get(cat, None) for cat in category_names],
        [without_original.get(cat, None) for cat in category_names],
    ],
    line_labels=['Med KI', 'Uten KI'],
    title='Kategori, Originalitet: Med KI vs uten KI (totalt)',
    ylabel='Antall',
    xlabel='Kategorier',
    xticklabels=category_names,
)

# ------------------------------------------------------------------------------
#
# Number of Ideas
#
# ------------------------------------------------------------------------------

info('Number of ideas')

cnt_with_ai = 0
for ans in categorized_with_ai:
    cnt_with_ai = cnt_with_ai + ans.ideas

avg_with_ai = statistics.mean(ans.ideas for ans in categorized_with_ai)

cnt_without = 0
for ans in categorized_without:
    cnt_without = cnt_without + ans.ideas

avg_without = statistics.mean(ans.ideas for ans in categorized_without)

with open(outdir / 'number-of-ideas.txt', 'w') as f:
    print(f'    With AI   Without', file=f)
    print(f'Total    {cnt_with_ai:>2}   {cnt_without}', file=f)
    print(f'Average  {avg_with_ai:>2}   {avg_without:.3}', file=f)
    debug(f'Wrote text: {f.name}')

# ------------------------------------------------------------------------------
#
# AI usage in experiment
#
# ------------------------------------------------------------------------------

info('AI usage in experiment')

categories = answers.experiment_usages(scored_answers)

analysis.bar_plot_single(
    name='ai-usage',
    label='Antall svar',
    values=[count for (cat, count) in categories],
    title='Bruk av AI i eksperiment',
    ylabel='Antall svar',
    xlabel='Bruksområde',
    xticklabels=[cat for (cat, count) in categories],
)


# ------------------------------------------------------------------------------
#
# T-Testing
#
# ------------------------------------------------------------------------------

def weighted(score): return score.total_weighted(.6, .2)


def ttest(a, b):
    debug(f'T-test A ({len(a)}): {pformat(a, width=140, compact=True)}')
    debug(f'T-test B ({len(b)}): {pformat(b, width=140, compact=True)}')
    return stats.ttest_ind(a, b)


fmt_num4 = partial(fmt_num, w=4)


# --------------------------------------
# Mean Scoring
# --------------------------------------

def ttest_mean_scoring():
    debug("Authors T-tests")
    authors_weighted = stats.ttest_ind(
        [weighted(score) for score in author_scoring_mean.with_ai()],
        [weighted(score) for score in author_scoring_mean.without_ai()]
    )
    authors_equal = stats.ttest_ind(
        [score.total() for score in author_scoring_mean.with_ai()],
        [score.total() for score in author_scoring_mean.without_ai()]
    )

    debug("Felles T-tests")
    felles_weighted = stats.ttest_ind(
        [weighted(score) for score in felles_scoring.with_ai()],
        [weighted(score) for score in felles_scoring.without_ai()]
    )
    felles_equal = stats.ttest_ind(
        [score.total() for score in felles_scoring.with_ai()],
        [score.total() for score in felles_scoring.without_ai()]
    )

    debug("Experts T-tests")
    experts_weighted = stats.ttest_ind(
        [weighted(score) for score in expert_scoring_mean.with_ai()],
        [weighted(score) for score in expert_scoring_mean.without_ai()]
    )
    experts_equal = stats.ttest_ind(
        [score.total() for score in expert_scoring_mean.with_ai()],
        [score.total() for score in expert_scoring_mean.without_ai()]
    )

    debug("Totals T-tests")
    totals_weighted = stats.ttest_ind(
        [weighted(score) for score in total_scoring_mean.with_ai()],
        [weighted(score) for score in total_scoring_mean.without_ai()]
    )
    totals_equal = stats.ttest_ind(
        [score.total() for score in total_scoring_mean.with_ai()],
        [score.total() for score in total_scoring_mean.without_ai()]
    )

    debug("Self T-tests")
    self_weighted = stats.ttest_ind(
        [weighted(score) for score in self_evals.with_ai()],
        [weighted(score) for score in self_evals.without_ai()]
    )
    self_equal = stats.ttest_ind(
        [score.total() for score in self_evals.with_ai()],
        [score.total() for score in self_evals.without_ai()]
    )

    with open(outdir / 't-testing-scoring.csv', 'w') as f:
        w = csv.writer(f, delimiter=';')

        w.writerow(['', 'Forfattere', 'Eksperter', 'Forfattere og Eksperter', 'Forfattere Felles',
                    'Selvevaluering'])

        w.writerow([
            'Likt Vektet',
            fmt_num4(authors_equal.pvalue),
            fmt_num4(experts_equal.pvalue),
            fmt_num4(totals_equal.pvalue),
            fmt_num4(felles_equal.pvalue),
            fmt_num4(self_equal.pvalue),
        ])

        w.writerow([
            'Vektet 60/20/20',
            fmt_num4(authors_weighted.pvalue),
            fmt_num4(experts_weighted.pvalue),
            fmt_num4(totals_weighted.pvalue),
            fmt_num4(felles_weighted.pvalue),
            fmt_num4(self_weighted.pvalue),
        ])

        debug(f'Wrote CSV: {f.name}')


info("T-testing mean scorings")
ttest_mean_scoring()

# --------------------------------------
# Difficulty Evaluation
# --------------------------------------

fttest = open(outdir / 't-testing.csv', 'w')
wttest = csv.writer(fttest, delimiter=';')
wttest.writerow(['Test', 'P-value'])

rating = {
    'Svært lett': 1,
    'Lett': 2,
    'Middels': 3,
    'Vanskelig': 4,
    'Svært vanskelig': 5,
}


def ttest_difficulty_evaluation():
    res = ttest(
        [rating[ans.difficulty] for ans in categorized_with_ai],
        [rating[ans.difficulty] for ans in categorized_without],
    )
    wttest.writerow(['Difficulty Evaluation', fmt_num4(res.pvalue)])


info("T-testing difficulty evaluation")
ttest_difficulty_evaluation()


# --------------------------------------
# Number of Ideas
# --------------------------------------

def ttest_number_of_ideas():
    res = ttest(
        [ans.ideas for ans in categorized_with_ai],
        [ans.ideas for ans in categorized_without],
    )
    wttest.writerow(['Number of Ideas', fmt_num4(res.pvalue)])


info("T-testing number of ideas")
ttest_number_of_ideas()


# --------------------------------------
# Answer Category
# --------------------------------------

def ttest_answer_category():
    cats = sorted(set(ans.category for ans in categorized_answers))
    res = ttest(
        [cats.index(ans.category) for ans in categorized_with_ai],
        [cats.index(ans.category) for ans in categorized_without],
    )
    wttest.writerow(['Answer Category', fmt_num4(res.pvalue)])


info("T-testing answer category")
ttest_answer_category()


# --------------------------------------
# Time
# --------------------------------------

def ttest_timings():
    debug('T-testing brainstorm time')
    res = ttest(
        sorted(ans.time_brainstorm for ans in categorized_with_ai),
        sorted(ans.time_brainstorm for ans in categorized_without),
    )
    wttest.writerow(['Time Brainstorming', fmt_num4(res.pvalue)])

    debug('T-testing description time')
    res = ttest(
        sorted(ans.time_description for ans in categorized_with_ai),
        sorted(ans.time_description for ans in categorized_without),
    )
    wttest.writerow(['Time Description', fmt_num4(res.pvalue)])

    debug('T-testing effect time')
    res = ttest(
        sorted(ans.time_effect for ans in categorized_with_ai if ans.time_effect < 12000),
        sorted(ans.time_effect for ans in categorized_without),
    )
    wttest.writerow(['Time Effect', fmt_num4(res.pvalue)])

    debug('T-testing total time')
    res = ttest(
        sorted(ans.time_total for ans in categorized_with_ai if ans.time_total < 12000),
        sorted(ans.time_total for ans in categorized_without),
    )
    wttest.writerow(['Time Total', fmt_num4(res.pvalue)])


info("T-testing time")
ttest_timings()


# --------------------------------------
# Originality
# --------------------------------------

def ttest_originality():
    debug('T-testing originality authors')
    res = ttest(
        [score.original for score in author_scoring_mean.with_ai()],
        [score.original for score in author_scoring_mean.without_ai()]
    )
    wttest.writerow(['Originalitet - Forfattere', fmt_num4(res.pvalue)])

    debug('T-testing originality experts')
    res = ttest(
        [score.original for score in expert_scoring_mean.with_ai()],
        [score.original for score in expert_scoring_mean.without_ai()]
    )
    wttest.writerow(['Originalitet - Eksperter', fmt_num4(res.pvalue)])

    debug('T-testing originality total')
    res = ttest(
        [score.original for score in total_scoring_mean.with_ai()],
        [score.original for score in total_scoring_mean.without_ai()]
    )
    wttest.writerow(['Originalitet - Forfattere og eksperter', fmt_num4(res.pvalue)])


info("T-testing originality")
ttest_originality()


# # --------------------------------------
# # Knowledge high/low
# # --------------------------------------
#
# def ttest_knowledge_highlow():
#     ai_scores = total_scoring_mean.with_ai()
#     ai_scores.sort(key=lambda s: s.total())
#     ai_scores.sort(key=lambda s: s.answer.ai_knowledge_rated)
#
#     middle = len(ai_scores) // 2
#     high = [score.total() for score in ai_scores[:middle]]
#     low = [score.total() for score in ai_scores[middle:]]
#     res = ttest(high, low)
#     wttest.writerow(['AI-kunnskap høy vs. lav', fmt_num4(res.pvalue)])
#
#
# info("T-testing knowledge high/low")
# ttest_knowledge_highlow()
#
#
# # --------------------------------------
# # Critical high/low
# # --------------------------------------
#
# def ttest_critical_highlow():
#     ai_scores = total_scoring_mean.with_ai()
#     ai_scores.sort(key=lambda s: s.total())
#     ai_scores.sort(key=lambda s: s.answer.ai_critical_rated)
#
#     middle = len(ai_scores) // 2
#     high = [score.total() for score in ai_scores[:middle]]
#     low = [score.total() for score in ai_scores[middle:]]
#     res = ttest(high, low)
#     wttest.writerow(['AI-kritisk høy vs. lav', fmt_num4(res.pvalue)])
#
#
# info("T-testing critical high/low")
# ttest_critical_highlow()


# --------------------------------------
# Knowledge high med/uten
# --------------------------------------

def ttest_knowledge_highlow():
    with_ai_scores = total_scoring_mean.with_ai()
    with_ai_scores.sort(key=lambda s: s.total())
    with_ai_scores.sort(key=lambda s: s.answer.ai_knowledge_rated)
    with_ai_scores = with_ai_scores[len(with_ai_scores) // 2:]

    without_scores = total_scoring_mean.without_ai()
    without_scores.sort(key=lambda s: s.total())
    without_scores.sort(key=lambda s: s.answer.ai_knowledge_rated)
    without_scores = without_scores[len(without_scores) // 2:]

    res = ttest(
        [score.total() for score in with_ai_scores],
        [score.total() for score in without_scores],
    )
    wttest.writerow(['AI-kunnskap høy, med vs. uten', fmt_num4(res.pvalue)])


info("T-testing knowledge high med/uten")
ttest_knowledge_highlow()


# --------------------------------------
# Critical high med/uten
# --------------------------------------

def ttest_critical_highlow():
    with_ai_scores = total_scoring_mean.with_ai()
    with_ai_scores.sort(key=lambda s: s.total())
    with_ai_scores.sort(key=lambda s: s.answer.ai_critical_rated)
    with_ai_scores = with_ai_scores[len(with_ai_scores) // 2:]

    without_scores = total_scoring_mean.without_ai()
    without_scores.sort(key=lambda s: s.total())
    without_scores.sort(key=lambda s: s.answer.ai_critical_rated)
    without_scores = without_scores[len(without_scores) // 2:]

    res = ttest(
        [score.total() for score in with_ai_scores],
        [score.total() for score in without_scores],
    )
    wttest.writerow(['AI-kritisk høy, med vs. uten', fmt_num4(res.pvalue)])


info("T-testing critical high med/uten")
ttest_critical_highlow()


# --------------------------------------
# Exploration high med/uten
# --------------------------------------

def ttest_knowledge_highlow():
    with_ai_scores = total_scoring_mean.with_ai()
    with_ai_scores.sort(key=lambda s: s.total())
    with_ai_scores.sort(key=lambda s: s.answer.ai_use_exploration_rated)
    with_ai_scores = with_ai_scores[len(with_ai_scores) // 2:]

    without_scores = total_scoring_mean.without_ai()
    without_scores.sort(key=lambda s: s.total())
    without_scores.sort(key=lambda s: s.answer.ai_use_exploration_rated)
    without_scores = without_scores[len(without_scores) // 2:]

    res = ttest(
        [score.total() for score in with_ai_scores],
        [score.total() for score in without_scores],
    )
    wttest.writerow(['AI-utforskning høy, med vs. uten', fmt_num4(res.pvalue)])


info("T-testing exploration high med/uten")
ttest_knowledge_highlow()


# --------------------------------------
# Videreutvikling high med/uten
# --------------------------------------

def ttest_knowledge_highlow():
    with_ai_scores = total_scoring_mean.with_ai()
    with_ai_scores.sort(key=lambda s: s.total())
    with_ai_scores.sort(key=lambda s: s.answer.ai_use_videreutvikling_rated)
    with_ai_scores = with_ai_scores[len(with_ai_scores) // 2:]

    without_scores = total_scoring_mean.without_ai()
    without_scores.sort(key=lambda s: s.total())
    without_scores.sort(key=lambda s: s.answer.ai_use_videreutvikling_rated)
    without_scores = without_scores[len(without_scores) // 2:]

    res = ttest(
        [score.total() for score in with_ai_scores],
        [score.total() for score in without_scores],
    )
    wttest.writerow(['AI-videreutvikling høy, med vs. uten', fmt_num4(res.pvalue)])


info("T-testing videreutvikling high med/uten")
ttest_knowledge_highlow()


# --------------------------------------
# Search high med/uten
# --------------------------------------

def ttest_knowledge_highlow():
    with_ai_scores = total_scoring_mean.with_ai()
    with_ai_scores.sort(key=lambda s: s.total())
    with_ai_scores.sort(key=lambda s: s.answer.ai_use_search_rated)
    with_ai_scores = with_ai_scores[len(with_ai_scores) // 2:]

    without_scores = total_scoring_mean.without_ai()
    without_scores.sort(key=lambda s: s.total())
    without_scores.sort(key=lambda s: s.answer.ai_use_search_rated)
    without_scores = without_scores[len(without_scores) // 2:]

    res = ttest(
        [score.total() for score in with_ai_scores],
        [score.total() for score in without_scores],
    )
    wttest.writerow(['AI-søk høy, med vs. uten', fmt_num4(res.pvalue)])


info("T-testing search high med/uten")
ttest_knowledge_highlow()


# --------------------------------------
# Work usage high med/uten
# --------------------------------------

def ttest_knowledge_highlow():
    with_ai_scores = total_scoring_mean.with_ai()
    with_ai_scores.sort(key=lambda s: s.total())
    with_ai_scores.sort(key=lambda s: s.answer.work_usage_rated)
    with_ai_scores = with_ai_scores[len(with_ai_scores) // 2:]

    without_scores = total_scoring_mean.without_ai()
    without_scores.sort(key=lambda s: s.total())
    without_scores.sort(key=lambda s: s.answer.work_usage_rated)
    without_scores = without_scores[len(without_scores) // 2:]

    res = ttest(
        [score.total() for score in with_ai_scores],
        [score.total() for score in without_scores],
    )
    wttest.writerow(['Bruk på jobb høy, med vs. uten', fmt_num4(res.pvalue)])


info("T-testing work usage high med/uten")
ttest_knowledge_highlow()

# usg = set(ans.work_usage for ans in scored_answers)
# print('Work usage')
# pprint(usg)


# ------------------------------------------------------------------------------
#
# Spearman Tests
#
# ------------------------------------------------------------------------------

# --------------------------------------
# Spearman AI knowledge
# --------------------------------------

def spearman_ai_knowledge():
    data = pd.DataFrame({
        'knowledge': [score.answer.ai_knowledge for score in total_scoring_mean],
        'score': [score.total() for score in total_scoring_mean]
    })

    # Convert ordinal categories to numeric
    rating_map = {
        'Ingen kunnskap': 0,
        'Litt kunnskap': 1,
        'Moderat kunnskap': 2,
        'God kunnskap': 3,
        'Svært god kunnskap': 4
    }
    data['knowledge_num'] = data['knowledge'].map(rating_map)

    # Calculate Spearman correlation
    correlation, p_value = stats.spearmanr(
        data['knowledge_num'],
        data['score']
    )
    print(f"Spearman correlation: {correlation:.3f}")
    print(f"P-value: {p_value:.4f}")


info("Spearman - AI knowledge")
spearman_ai_knowledge()


# --------------------------------------
# Spearman AI critical
# --------------------------------------

def spearman_ai_critical():
    data = pd.DataFrame({
        'eval': [score.answer.ai_critical for score in total_scoring_mean],
        'score': [score.total() for score in total_scoring_mean]
    })

    # Convert ordinal categories to numeric
    rating_map = {
        '': 0,
        'I ingen grad': 1,
        'I liten grad': 1,
        'I middels grad': 2,
        'I stor grad': 3,
        'I svært stor grad': 4
    }
    data['eval_num'] = data['eval'].map(rating_map)

    # Calculate Spearman correlation
    correlation, p_value = stats.spearmanr(
        data['eval_num'],
        data['score']
    )
    print(f"Spearman correlation: {correlation:.3f}")
    print(f"P-value: {p_value:.4f}")


info("Spearman - AI critical")
spearman_ai_critical()
