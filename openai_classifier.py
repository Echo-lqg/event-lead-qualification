from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, Field, model_validator

_client = None

def get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client

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

    @model_validator(mode="after")
    def other_requires_low_relevance(self):
        if self.event == "Other" and self.relevance_score > 3:
            raise ValueError(
                "relevance_score must be 3 or lower when event is Other"
            )
        return self

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

Relevance score:

relevance_score measures how relevant the company is to the event you
assigned. It does NOT measure how confident you are in the classification.

- 8-10: the event topic is the company's primary business.
- 5-7: the company fits the event, but the relevant technology is only one
  part of a broader business.
- 2-4: the company has only a marginal connection to the event topics.
- 1: the company has no meaningful connection to any event topic.

If you choose Other, relevance_score must be 3 or lower, because Other means
the company does not fit any of the three events.

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

    response = get_client().responses.parse(
        model="gpt-6-astra",
        input=prompt,
        text_format=ClassificationResult
    )

    result = response.output_parsed
    return result