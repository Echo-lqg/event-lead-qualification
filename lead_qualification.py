import pandas as pd

df = pd.read_csv("companies.csv")

print("\n===== Input Data Preview =====")
print(df.head())

classification_rules = """
RAISE:
AI, generative AI, machine learning, AI infrastructure, AI startups

Signal Week:
Blockchain, crypto, Web3, digital assets, fintech related to blockchain

MACHINA:
Robotics, physical AI, autonomous machines, industrial AI, embodied AI

Other:
Companies that do not clearly fit any of the categories above.
"""

def build_structured_prompt(company, description):
    return f"""
You are an event classification assistant.

Classify the company into exactly one event.

{classification_rules}

Company:
{company}

Description:
{description}

Return valid JSON with exactly these fields:

company
event
relevance_score
reason

Rules:
- event must be one of:
  RAISE
  Signal Week
  MACHINA
  Other

- relevance_score must be an integer from 1 to 10.
- reason must be short and clear.
- Do not add any text outside the JSON.
"""


for index,row in df.iterrows():
    prompt = build_structured_prompt(
        row["name"], #build_structured_prompt需要两个变量输入
        row["description"]
    )

    #print("====================")
    #print("Company :", row["name"])
    #print(prompt)

#Python list
structured_results = [
    {
    "company": "Anthropic",
    "event": "RAISE",
    "relevance_score": 10,
    "reason": "Anthropic focuses on AI research and AI safety."
    },
    {
    "company": "Binance",
    "event": "Signal Week",
    "relevance_score": 10,
    "reason": "Binance is a cryptocurrency exchange and blockchain ecosystem."
    },
    {
    "company": "Boston Dynamics",
    "event": "MACHINA",
    "relevance_score": 10,
    "reason": "Boston Dynamics develops advanced mobile robots."
    },
    {
    "company": "L'Oreal",
    "event": "Other",
    "relevance_score": 2,
    "reason": "L'Oreal is primarily a beauty and cosmetics company."
    },
    {
    "company": "Tesla",
    "event": "MACHINA",
    "relevance_score": 9,
    "reason": "Tesla develops autonomous driving systems and humanoid robots."
    },
    {
    "company": "Stripe",
    "event": "Other",
    "relevance_score": 3,
    "reason": "Stripe focuses on online payment infrastructure rather than blockchain."
    },
    {
    "company": "NVIDIA",
    "event": "RAISE",
    "relevance_score": 9,
    "reason": "NVIDIA provides accelerated computing infrastructure widely used for AI."
    },
    {
    "company": "UiPath",
    "event": "Other",
    "relevance_score": 4,
    "reason": "UiPath focuses on software-based process automation rather than physical robotics."
    },
    {
    "company": "Coinbase",
    "event": "Signal Week",
    "relevance_score": 10,
    "reason": "Coinbase is a cryptocurrency exchange and digital asset platform."
    },
    {
    "company": "Ledger",
    "event": "Signal Week",
    "relevance_score": 10,
    "reason": "Ledger develops hardware wallets for cryptocurrencies and digital assets."
    },
    {
    "company": "Palantir",
    "event": "RAISE",
    "relevance_score": 8,
    "reason": "Palantir provides data analytics and artificial intelligence platforms."
    },
    {
    "company": "Hugging Face",
    "event": "RAISE",
    "relevance_score": 10,
    "reason": "Hugging Face provides machine learning models, datasets and AI developer tools."
    },
    {
    "company": "Figure AI",
    "event": "MACHINA",
    "relevance_score": 10,
    "reason": "Figure AI develops AI-powered general-purpose humanoid robots."
    },
    {
    "company": "Waymo",
    "event": "MACHINA",
    "relevance_score": 10,
    "reason": "Waymo develops autonomous driving technology and self-driving vehicles."
    },
    {
    "company": "Salesforce",
    "event": "Other",
    "relevance_score": 4,
    "reason": "Salesforce is primarily an enterprise CRM and cloud software company."
    },
    {
    "company": "PayPal",
    "event": "Other",
    "relevance_score": 3,
    "reason": "PayPal focuses on digital payments rather than blockchain or digital assets."
    },
    {
    "company": "Snowflake",
    "event": "RAISE",
    "relevance_score": 7,
    "reason": "Snowflake provides cloud data infrastructure with analytics and AI capabilities."
    },
    {
    "company": "Scale AI",
    "event": "RAISE",
    "relevance_score": 10,
    "reason": "Scale AI provides infrastructure for AI data, evaluation and model development."
    },
    {
    "company": "ABB Robotics",
    "event": "MACHINA",
    "relevance_score": 10,
    "reason": "ABB Robotics develops industrial robots and automation systems."
    },
    {
    "company": "Chainlink",
    "event": "Signal Week",
    "relevance_score": 10,
    "reason": "Chainlink provides decentralized oracle infrastructure for blockchain networks."
    }
]

results_df = pd.DataFrame(structured_results)

print("\n===== Structured LLM Results =====")
print(results_df)

#merge df and results_df

if df["name"].duplicated().any():
    raise ValueError("Duplicate company names found in input data.")

if results_df["company"].duplicated().any():
    raise ValueError("Duplicate company names found in classification results.")

classified_df = df.merge(
    results_df,
    left_on="name",
    right_on="company",
    how="left", #以输入表为准，每家输入公司都保留。如果某家没有分类结果，event 等会是空值；
    validate="one_to_one" #每个 name 只对应一个 company
)

if classified_df["event"].isna().any(): #整一列event
    missing_companies = classified_df.loc[
        classified_df["event"].isna(),
        "name"
    ].tolist()

    raise ValueError(
        f"Missing classification results for: {missing_companies}"
    )
    #刚才用的是 how="left"：输入公司一定会留下。如果 results_df 里没有这家，拼完后 event 就是空的（NaN）。
    #isna()每一行空不空？
    #any()有没有一行是空的？
    #all()是不是每一行都空？

print("\n===== Merged Classification Data =====")
print(classified_df)

classified_df["correct"] = (
    classified_df["expected_event"] ==
    classified_df["event"]
)

classified_df.to_csv(
    "classified_companies.csv",
    index = False
)

# Classification Evaluation

accuracy = classified_df["correct"].mean()

print("\n===== Classification Evaluation =====")
print("Accuracy:", round(accuracy, 3))


errors = classified_df[
    classified_df["correct"] == False
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


errors.to_csv(
    "classification_errors.csv",
    index=False
)

case_summary.to_csv(
    "case_type_summary.csv"
)

# Assign lower confidence to ambiguous or borderline cases.
# Clear cases receive higher confidence because they are easier to classify reliably.

case_confidence_score = {
    "clear_case": 10,
    "multi_domain": 7,
    "borderline_fintech": 6,
    "borderline_ai": 6,
    "borderline_autonomy": 7,
    "keyword_trap": 5 #这种案例容易被关键词误导，所以即使模型给出了分类，我们也不应该过度相信它。
}

classified_df["case_confidence"] = (
    classified_df["case_type"]
    .map(case_confidence_score)
)

if classified_df["case_confidence"].isna().any():
    unknown_case_type = (
        classified_df.loc[
            classified_df["case_confidence"].isna(),
            "case_type"
        ]
        .unique()
        .tolist()
    )
    raise ValueError(
        f"Unknown case_type values: {unknown_case_type}"
    )
#有没有至少一行置信度是空的。有，就说明出现了未知 case_type。
#.loc[..., "case_type"].unique().tolist()
#把这些空置信度对应的 case_type 拿出来，去重后变成列表。
#这样报错时看到的是类型名（例如 "borderline_saas"），不是一堆重复行。

print("\n===== Missing Values Check =====")

scoring_columns = [
    "relevance_score",
    "industry_fit",
    "sponsorship_potential",
    "company_size",
    "past_event_engagement",
    "case_confidence"
]

print(classified_df[scoring_columns].isna().sum())

if classified_df[scoring_columns].isna().any().any():
    missing_rows = classified_df.loc[
        classified_df[scoring_columns].isna().any(axis=1),
        ["name"] + scoring_columns
    ]
    raise ValueError(
        f"Missing scoring inputs:\n{missing_rows.toString(index=False)}"
    )

#第一个 .any()：每一列有没有空值 第二个 .any()：有没有任何一列空 axis=1：按行看，这家公司这 6 列里有没有至少一个空格子
#报错带上 name 和这 6 列，能直接看到是谁、缺哪项

# Weighted lead scoring model:
# relevance_score: 30%
# industry_fit: 25%
# sponsorship_potential: 20%
# company_size: 10%
# past_event_engagement: 10%
# case_confidence: 5%
#
# All input scores are on a 1-10 scale.
# Multiplying by 10 converts the final score to a 0-100 scale.

classified_df["lead_score"] = (
    (
    classified_df["relevance_score"] * 0.30
    + classified_df["industry_fit"] * 0.25
    + classified_df["sponsorship_potential"] * 0.20
    + classified_df["company_size"] * 0.10
    + classified_df["past_event_engagement"] * 0.10
    + classified_df["case_confidence"] * 0.05
    ) * 10
).round(1)

# Convert numerical lead scores into business-friendly priority levels.

def assign_priority(score):
    if score >= 85:
        return "High"
    elif score >= 65:
        return "Medium"
    else:
        return "Low"

classified_df["priority"] = (
    classified_df["lead_score"].apply(assign_priority)
)
#这里apply（）: classified_df["lead_score"]是一个 Series，也就是单独一列。

# Translate lead priority into a suggested business follow-up action.

def recommend_action(row):
    if row["priority"] == "High":
        return "Contact sales / partnership team"
    elif row["priority"] == "Medium":
        return "Add to nurture campaign"
    else:
        return "Low priority / monitor"

classified_df["recommended_action"] = (
    classified_df.apply(
        recommend_action,
        axis = 1
    )
)

#这里的apply()是对整个classified_df执行 而且写了：axis=1 一行一行处理。

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

# Select the 10 highest-scoring leads across all events.

top_10_leads = classified_df.head(10)

print("\n===== Top 10 Leads =====")
print(top_10_leads[[
    "company",
    "event",
    "lead_score",
    "priority"
]])

# Top 3 per event

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

priority_leads.to_csv(
    "priority_leads.csv",
    index=False
)

event_summary = (
    classified_df[
        classified_df["event"] != "Other"
    ] #先滤掉 L'Oreal、Stripe 这类未匹配活动的公司
    .groupby("event")
    .agg(
        company_count=("company","count"),
        average_lead_score=("lead_score","mean")
    )
)
#.agg(
#    新列名=("原列名", "统计方法")
#)
#把 event 相同的公司放在一组 然后aggregate（聚合）。 company_count 每个 event 里面有多少家公司。

event_summary["average_lead_score"] = (
    event_summary["average_lead_score"]
    .round(1)
)

print("\n===== Event Summary =====")
print(event_summary)

event_summary.to_csv(
    "event_summary.csv"
)

priority_summary = (
    classified_df["priority"]
    .value_counts()
)
#value_counts()会自动统计每个不同值出现了几次。

print("\n===== Priority Summary =====")
print(priority_summary)

priority_summary.to_csv(
    "priority_summary.csv"
)

print("\n===== Pipeline Complete =====")
print("All output files saved successfully.")
#很多都是模拟数据。
#所以 README 要明确写：
#Business features are currently simulated for prototyping purposes. In production, these fields would be sourced from CRM, enrichment APIs, historical event data, and company databases.
