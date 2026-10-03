from enrichment.fetcher import build_company_sources
from enrichment.extractor import extract_company_profile
from enrichment.verifier import verify_profile_evidence


company_name = "NVIDIA"

sources = build_company_sources(
    "https://www.nvidia.com"
)

profile = extract_company_profile(
    company_name=company_name,
    sources=sources
)

print(profile)

verification_results = verify_profile_evidence(
    profile,
    sources
)

print("\nVerification results:")

for result in verification_results:
    print(
        result["field"],
        result["source_id"],
        "->",
        result["verified"]
    )