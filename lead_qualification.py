import pandas as pd
import sqlite3

# =========================================================
# 1. Load qualification data from SQLite
# =========================================================

conn = sqlite3.connect("event_leads.db")

classified_df = pd.read_sql_query("""
SELECT
    c.name AS company,
    c.description,
    c.expected_event,
    c.case_type,
    c.company_size,
    c.industry_fit,
    c.past_event_engagement,
    c.sponsorship_potential,

    cl.predicted_event AS event,
    cl.relevance_score,
    cl.reason,
    cl.correct,

    ls.lead_score,
    ls.priority,
    ls.recommended_action

FROM companies AS c
JOIN classifications AS cl
    ON c.id = cl.company_id
JOIN lead_scores AS ls
    ON c.id = ls.company_id
""", conn)

if classified_df.empty:
    raise ValueError(
        "No lead qualification data found in the database."
    )

# =========================================================
# 2. Classification evaluation
# =========================================================

accuracy = classified_df["correct"].mean()

print("\n===== Classification Evaluation =====")
print("Accuracy:", round(accuracy, 3))


errors = classified_df[
    classified_df["correct"] == 0
].copy()
#.copy() 是为了拿到一张独立的新表，避免后面改 errors 时碰到 pandas 的「视图还是副本」问题。

print("\n===== Classification Errors =====")

print(errors[[
    "company",
    "expected_event",
    "event",
    "reason"
]])


case_summary = classified_df.groupby(
    "case_type"
)["correct"].agg(
    ["count", "mean"]
)
#每类有多少家公司、答对的比例是多少。
#count：这类有几家公司
#mean：这类的准确率（答对家数 ÷ 总数）

print("\n===== Accuracy by Case Type =====")
print(case_summary)

# =========================================================
# 3. Lead qualification analysis
# =========================================================

classified_df = classified_df.sort_values(
    by="lead_score",
    ascending=False #降序 分数最高的公司排第一。
)

print("\n===== Lead Scoring Results =====")
print(classified_df[[
    "company",
    "event",
    "relevance_score",
    "industry_fit",
    "sponsorship_potential",
    "company_size",
    "past_event_engagement",
    "lead_score",
    "priority",
    "recommended_action"
]])

# =========================================================
# 4. Top leads
# =========================================================

# Select the 10 highest-scoring leads
top_10_leads = classified_df.head(10)

print("\n===== Top 10 Leads =====")
print(top_10_leads[[
    "company",
    "event",
    "lead_score",
    "priority"
]])


# Select the top 3 leads for each event
top_leads_by_event = (
    classified_df[
        classified_df["event"] != "Other"
    ]
    .sort_values(
        by="lead_score",
        ascending=False
    )
    .groupby("event")
    .head(3)
)

print("\n===== Top 3 Leads by Event =====")
print(top_leads_by_event[[
    "company",
    "event",
    "lead_score",
    "priority"
]])


# Select all high-priority leads
priority_leads = classified_df[
    classified_df["priority"] == "High"
].copy()

print("\n===== High Priority Leads =====")
print(priority_leads[[
    "company",
    "event",
    "lead_score",
    "priority",
    "recommended_action"
]])


# =========================================================
# 5. Business summaries
# =========================================================

# Summarize leads by event
event_summary = (
    classified_df[
        classified_df["event"] != "Other"
    ]
    .groupby("event")
    .agg(
        company_count=("company", "count"),
        average_lead_score=("lead_score", "mean")
    )
)

event_summary["average_lead_score"] = (
    event_summary["average_lead_score"]
    .round(1)
)

print("\n===== Event Summary =====")
print(event_summary)


# Summarize lead priority distribution
priority_summary = (
    classified_df["priority"]
    .value_counts()
)

print("\n===== Priority Summary =====")
print(priority_summary)


# =========================================================
# 6. Export analysis results
# =========================================================

classified_df.to_csv(
    "lead_qualification_results.csv",
    index=False
)

top_10_leads.to_csv(
    "top_10_leads.csv",
    index=False
)

top_leads_by_event.to_csv(
    "top_leads_by_event.csv",
    index=False
)

priority_leads.to_csv(
    "priority_leads.csv",
    index=False
)

event_summary.to_csv(
    "event_summary.csv"
)

priority_summary.to_csv(
    "priority_summary.csv"
)

errors.to_csv(
    "classification_errors.csv",
    index=False
)

case_summary.to_csv(
    "lead_qualification_case_summary.csv"
)


# =========================================================
# 7. Close database connection
# =========================================================

conn.close()

print("\n===== Pipeline Complete =====")
print("All output files saved successfully.")