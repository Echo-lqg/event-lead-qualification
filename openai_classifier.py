from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI()

class ClassificationResult(BaseModel):
    event: Literal[ #表示 event 只能是这四个值之一。
        "RAISE",
        "Signal Week",
        "MACHINA",
        "Other"
    ]

    relevance_score: int = Field( #relevance_score 必须是整数 而且只能在 1 到 10 之间
        ge=1,
        le=10
    )

    reason: str

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

def build_prompt(company, description):
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

Rules:
- relevance_score must be an integer from 1 to 10.
- reason must be short and clear.
"""

def classify_company(company, description):
    prompt = build_prompt(
        company,
        description
    )

    response = client.responses.parse(
        model="gpt-6-astra",
        input=prompt,
        text_format=ClassificationResult
    )

    result = response.output_parsed
    return result