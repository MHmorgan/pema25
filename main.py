
all_answers = read_answers()

categories = extra.read_categories()
category_names = categories.category_names()

scorings = read_scorings(all_answers)

for scoring in scorings.values():
    scored_answers = [ans for ans in scoring.answers()]
    scored_with_ai = [ans for ans in scoring.with_ai().answers()]
    scored_without = [ans for ans in scoring.without_ai().answers()]
    break
#%% md
# # AI vs. uten AI
# 
# Sammenligning av vurderingskriterier mellom AI og ikke-AI svar.
# 
# - Gjennomsnitt og median.
# - Sensor-vurderinger og selvvurderinger.
#%% md
# ## Median Scoring
#%%
median = Scoring.from_median(scorings.values())
analysis.scoring_report(median.with_ai(), median.without_ai())
#%% md
# ## Self-evaluation
#%%
self_evals = Scoring(
    ScoringEntry.from_answer(ans, ans.number)
    for ans in scored_answers
)
analysis.scoring_report(self_evals.with_ai(), self_evals.without_ai())
#%% md
# # Other Dimensions
# 
# Analysis of the results based on other dimensions.
#%%
categories = extra.read_categories()
category_names = categories.category_names()

categorized_with_ai = categorize(scored_with_ai, categories)
categorized_without = categorize(scored_without, categories)

categorized_with_ai_grouped = {}
for ans in categorized_with_ai:
    categorized_with_ai_grouped.setdefault(ans.category, []).append(ans)

categorized_without_grouped = {}
for ans in categorized_without:
    categorized_without_grouped.setdefault(ans.category, []).append(ans)
#%% md
# ## Category Count
#%%
with_ai_count = {k: len(g) for k, g in categorized_with_ai_grouped.items()}
without_count = {k: len(g) for k, g in categorized_without_grouped.items()}

analysis.bar_plot(
    values_with_ai=[with_ai_count.get(cat, 0) for cat in category_names],
    values_without=[without_count.get(cat, 0) for cat in category_names],
    title='Category Distribution: With AI vs Without AI',
    ylabel='Count',
    xlabel='Categories',
    xticklabels=category_names,
)
#%% md
# # Category Scoring
#%%
with_ai_original = {
    category: median.original_mean(answers)
    for category, answers in categorized_with_ai_grouped.items()
}

without_original = {
    category: median.original_mean(answers)
    for category, answers in categorized_without_grouped.items()
}

analysis.scatter_plot(
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

#%% md
# ## Number of Ideas
#%%
cnt_with_ai = 0
for ans in categorized_with_ai:
    cnt_with_ai = cnt_with_ai + ans.ideas

avg_with_ai = statistics.mean(ans.ideas for ans in categorized_with_ai)

cnt_without = 0
for ans in categorized_without:
    cnt_without = cnt_without + ans.ideas

avg_without = statistics.mean(ans.ideas for ans in categorized_without)

print(f'    With AI   Without')
print(f'Total    {cnt_with_ai:>2}   {cnt_without}')
print(f'Average  {avg_with_ai:>2}   {avg_without:.3}')
