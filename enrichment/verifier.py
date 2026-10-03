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