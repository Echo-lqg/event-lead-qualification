from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI()

class ClassificationResult(BaseModel):
    event: Literal[ #表示 event 只能是这四个值之一。
        "RAISE",
        "Siganl Week",
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

Company:
{company}

Description:
{description}

Rules:
- Choose RAISE only if AI is central to the company's primary business.
- Choose Signal Week only if blockchain, crypto, Web3, or digital assets are central.
- Choose MACHINA when the company primarily develops robotics, physical AI,
  autonomous machines, or embodied AI.
- Otherwise choose Other.
- relevance_score must be an integer from 1 to 10.
- reason must be short and clear.
"""

