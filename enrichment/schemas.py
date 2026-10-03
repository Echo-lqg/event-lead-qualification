from typing import Literal
from pydantic import BaseModel, Field


class SourceDocument(BaseModel):
    source_id: str

    source_type: Literal[
        "website",
        "wikipedia",
        "wikidata",
        "search"
    ]

    url: str
    fetched_at: str
    content_hash: str
    text: str


class Evidence(BaseModel):
    field: Literal[
        "primary_business",
        "product_type",
        "customer_type",
        "technology_tags",
        "employee_range",
        "public_or_funding",
        "event_presence"
    ]

    source_id: str

    quote: str = Field(
        max_length=300
    )


class CompanyProfile(BaseModel):
    primary_business: str

    product_type: Literal[
        "software",
        "hardware",
        "platform",
        "services",
        "mixed",
        "unknown"
    ]

    customer_type: Literal[
        "b2b_enterprise",
        "developers",
        "mixed",
        "consumers",
        "unknown"
    ]

    technology_tags: list[
        Literal[
            "ai",
            "generative_ai",
            "ml_infrastructure",
            "blockchain",
            "crypto",
            "web3",
            "robotics",
            "autonomous_systems",
            "fintech",
            "payments",
            "cloud",
            "other"
        ]
    ]

    employee_range: Literal[
        "1-50",
        "51-200",
        "201-1000",
        "1001-5000",
        "5001+",
        "unknown"
    ]

    public_or_funding: Literal[
        "public",
        "late_stage",
        "early_stage",
        "unknown"
    ]

    event_presence: Literal[
        "confirmed",
        "not_found",
        "unknown"
    ]

    evidence: list[Evidence]