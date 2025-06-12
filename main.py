from itertools import permutations

import answers
import analysis
import extra
from scoring import *
from utils import *

info('Reading input data...')
all_answers = answers.read_answers()
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

categorized_answers = answers.categorize(scored_answers, categories)
categorized_with_ai = answers.categorize(scored_with_ai, categories)
categorized_without = answers.categorize(scored_without, categories)
debug(f'Categorized answers: {len(scored_answers)}')
debug(f'With AI: {len(categorized_with_ai)}')
debug(f'Without: {len(categorized_without)}')

categorized_with_ai_grouped = {}
for ans in categorized_with_ai:
    categorized_with_ai_grouped.setdefault(ans.category, []).append(ans)

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
# Other Dimensions
# Analysis of the results based on other dimensions.
# 
# ------------------------------------------------------------------------------

# --------------------------------------
# Category Count
# --------------------------------------

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

# --------------------------------------
# Category Scoring
# --------------------------------------

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

# --------------------------------------
# Number of Ideas
# --------------------------------------

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

# --------------------------------------
# AI usage in experiment
# --------------------------------------

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
