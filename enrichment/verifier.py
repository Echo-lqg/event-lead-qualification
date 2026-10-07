def normalize_text(text: str) -> str:
    return " ".join(text.split()).lower()

def verify_quote(
    quote: str,
    source_text: str
) -> bool:
    normalized_quote = normalize_text(quote)
    normalized_source = normalize_text(source_text)

    return normalized_quote in normalized_source

from enrichment.schemas import (
    CompanyProfile,
    SourceDocument
)


def verify_profile_evidence(
    profile: CompanyProfile,
    sources: list[SourceDocument]
):
    source_map = {
        source.source_id: source.text
        for source in sources
    }

    results = []

    for evidence in profile.evidence:
        source_text = source_map.get(
            evidence.source_id
        )

        if source_text is None:
            is_valid = False
        else:
            is_valid = verify_quote(
                evidence.quote,
                source_text
            )

        results.append(
            {
                "field": evidence.field,
                "source_id": evidence.source_id,
                "quote": evidence.quote,
                "verified": is_valid
            }
        )

    return results

KEY_FIELDS = {
    "primary_business",
    "product_type",
    "customer_type",
    "technology_tags",
    "employee_range",
    "public_or_funding",
    "event_presence"
}

def calculate_grounded_ratio(
    verification_results: list[dict]
) -> float:

    verified_fields = {
        result["field"]
        for result in verification_results
        if result["verified"]
    }

    grounded_fields = (
        verified_fields & KEY_FIELDS
    )

    return len(grounded_fields) / len(KEY_FIELDS)

def calculate_enrichment_confidence(
    grounded_ratio: float
) -> float:
    return round(
        1 + 9 * grounded_ratio,
        1
    )
