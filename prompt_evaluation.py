import pandas as pd
from openai import OpenAI

client = OpenAI()

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

def build_prompt_v1(company,description) :
    return f"""
You're an event classification assistant.

Classify a company into exactly one of these events:

{classification_rules}

Company:
{company}

Description:
{description}
Return only the event name.

"""

def build_prompt_v2(company,description) :
    return f"""
You are an event classification assistant.

Your task is to classify a company into exactly one event.

Classification rules:

{classification_rules}

Important rules:
- Choose RAISE only if the company is primarily related to AI.
- Choose Signal Week only if the company is primarily related to blockchain, crypto, Web3, or digital assets.
- Choose MACHINA only if the company is primarily related to robotics, physical AI, autonomous machines, or embodied AI.
- If none clearly applies, choose Other.
- Do not classify based only on vague technology-related wording.
- Use only the company description provided.

Company:
{company}

Description:
{description}

Return exactly one of:
RAISE
Signal Week
MACHINA
Other
"""

def build_prompt_v3(company, description) :
    return f"""

You are an event classification assistant.

Classify the company into exactly one event.

{classification_rules}

Decision rules:

1. Choose MACHINA when the company's primary product is physical robotics,
   autonomous machines, humanoid robots, industrial robots, or embodied AI.

2. Do NOT choose MACHINA for software-only automation such as
   robotic process automation (RPA).

3. Choose Signal Week only when blockchain, crypto, Web3, or digital assets
   are central to the company's business.

4. Do NOT choose Signal Week for general fintech or payment companies
   unless blockchain or crypto is explicitly central.

5. Choose RAISE when AI, machine learning, generative AI, or AI infrastructure
   is central to the company's primary business.

6. If AI is only an additional feature of a broader software or cloud product,
   do not automatically choose RAISE.

7. If a company fits both AI and robotics, prioritize MACHINA when its primary
   product is a physical autonomous or robotic system.

8. If none of the categories clearly fits the company's primary business,
   choose Other.

Use only the provided description.

Company:
{company}

Description:
{description}

Return exactly one of:
RAISE
Signal Week
MACHINA
Other


"""

df = pd.read_csv("companies.csv")

print("\n===== Evaluation Dataset =====")
print(df.head())

print("\n===== Prompt Example =====")
print(
    build_prompt_v3(
        "Anthropic",
        "AI safety and research company"
    )
)

predictions_v1 = {}
predictions_v2 = {}
predictions_v3 = {}

def run_prompt(prompt):

    response = client.responses.create(
        model="gpt-6-astra",
        input=prompt
    )

    return response.output_text.strip()

for _, row in df.iterrows():
    company = row["name"]
    description = row["description"]

    prompt_v1 = build_prompt_v1(
        company,
        description
    )

    prompt_v2 = build_prompt_v2(
        company,
        description
    )

    prompt_v3 = build_prompt_v3(
        company,
        description
    )

    predictions_v1[company] = run_prompt(
        prompt_v1
    )

    predictions_v2[company] = run_prompt(
            prompt_v2
    )

    predictions_v3[company] = run_prompt(
            prompt_v3
    )

    print(
         f"✓ Evaluated {company}"
    )



evaluation = df.copy()
    
evaluation["prediction_v1"] = evaluation["name"].map(predictions_v1)    
evaluation["prediction_v2"] = evaluation["name"].map(predictions_v2)
evaluation["prediction_v3"] = evaluation["name"].map(predictions_v3)


evaluation["v1_correct"] = (
    evaluation["prediction_v1"] == evaluation["expected_event"]
)

evaluation["v2_correct"] = (
    evaluation["prediction_v2"] == evaluation["expected_event"]
)

evaluation["v3_correct"] = (
    evaluation["prediction_v3"] 
    == evaluation["expected_event"]
)

print("\n===== Prompt Accuracy =====")

accuracy_v1 = evaluation["v1_correct"].mean()
accuracy_v2 = evaluation["v2_correct"].mean()
accuracy_v3 = evaluation["v3_correct"].mean()

print("V1 Accuracy:", round(accuracy_v1, 3))
print("V2 Accuracy:", round(accuracy_v2, 3))
print("V3 Accuracy:", round(accuracy_v3, 3))

case_summary = evaluation.groupby("case_type")[
    ["v1_correct","v2_correct", "v3_correct"]
].mean()

print("\n===== Accuracy by Case Type =====")
print(case_summary)

v1_errors =  evaluation[
    evaluation["v1_correct"] == False
].copy()   

v2_errors = evaluation[
    evaluation["v2_correct"] == False
].copy()

v3_errors = evaluation[
    evaluation["v3_correct"] == False
].copy()

print("\n===== V1 Errors =====")
print(v1_errors[[
    "name",
    "expected_event",
    "prediction_v1"
]])


print("\n===== V2 Errors =====")
print(v2_errors[[
    "name",
    "expected_event",
    "prediction_v2"
]])

print("\n===== V3 Errors =====")
print(v3_errors[[
    "name",
    "expected_event",
    "prediction_v3"
]])


fixed_by_v2 = evaluation[
    (evaluation["v1_correct"] == False) &
    (evaluation["v2_correct"] == True)
].copy() 

print("\n===== Fixed by V2 =====")
print(fixed_by_v2[[
    "name",
    "expected_event",
    "prediction_v1",
    "prediction_v2"
]])

fixed_by_v3 = evaluation[
    (evaluation["v2_correct"] == False)
    & (evaluation["v3_correct"] == True)
].copy()

print("\n===== Fixed by V3 =====")
print(fixed_by_v3[[
    "name",
    "expected_event",
    "prediction_v2",
    "prediction_v3"
]])

broken_by_v2 = evaluation[
    (evaluation["v1_correct"] == True)
    & (evaluation["v2_correct"] == False)
].copy()

print("\n===== Broken by V2 =====")
print(broken_by_v2[[
    "name",
    "expected_event",
    "prediction_v1",
    "prediction_v2"
]])

broken_by_v3 = evaluation[
    (evaluation["v2_correct"] == True)
    & (evaluation["v3_correct"] == False)
].copy()

print("\n===== Broken by V3 =====")
print(broken_by_v3[[
    "name",
    "expected_event",
    "prediction_v2",
    "prediction_v3"
]])

summary = {
    "total_cases": len(evaluation),
    "v1_accuracy": accuracy_v1,
    "v2_accuracy": accuracy_v2,
    "v3_accuracy": accuracy_v3,
    "fixed_by_v2": len(fixed_by_v2),
    "broken_by_v2": len(broken_by_v2),
    "fixed_by_v3": len(fixed_by_v3),
    "broken_by_v3": len(broken_by_v3)
}

print("summary :", summary)


fixed_by_v2.to_csv(
    "fixed_by_v2.csv",
    index=False
)

evaluation.to_csv("prompt_evaluation.csv", index=False)
case_summary.to_csv("case_type_summary.csv")

summary_df = pd.DataFrame([summary])
summary_df.to_csv(
    "experiment_summary.csv",
    index=False
)

print("\n===== Prompt Evaluation Complete =====")
print("Evaluation files saved successfully.")


