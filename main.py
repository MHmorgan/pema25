import answers
import analysis
import extra
from scoring import *
from utils import *

info('Reading input data...')
all_answers = answers.read_answers()
scorings = read_scorings(all_answers)

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

# --------------------------------------
# Median scoring
# --------------------------------------

info('Median scoring')
median = Scoring.from_median(scorings.values())

with open(outdir / 'median-scoring.txt', 'w') as f:
    analysis.scoring_report(
        with_ai=median.with_ai(),
        without=median.without_ai(),
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

with open(outdir / 'self-evaluation.txt', 'w') as f:
    analysis.scoring_report(
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

analysis.bar_plot_compare(
    name='kategori-distribusjon',
    values_with_ai=[with_ai_count.get(cat, 0) for cat in category_names],
    values_without=[without_count.get(cat, 0) for cat in category_names],
    title='Category Distribution: With AI vs Without AI',
    ylabel='Count',
    xlabel='Categories',
    xticklabels=category_names,
)

# --------------------------------------
# Category Scoring
# --------------------------------------

info('Originality distribution')

with_ai_original = {
    category: median.original_mean(answers)
    for category, answers in categorized_with_ai_grouped.items()
}

without_original = {
    category: median.original_mean(answers)
    for category, answers in categorized_without_grouped.items()
}

analysis.scatter_plot(
    name='kategori-originalitet',
    line_values=[
        [with_ai_original.get(cat, None) for cat in category_names],
        [without_original.get(cat, None) for cat in category_names],
    ],
    line_labels=['With AI', 'Without AI'],
    title='Category Originalitet: With AI vs Without AI',
    ylabel='Count',
    xlabel='Categories',
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
# Usage
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
    rotation=30,
)

