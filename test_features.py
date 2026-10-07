from enrichment.fetcher import build_company_sources
from enrichment.extractor import extract_company_profile
from enrichment.verifier import (
    verify_profile_evidence,
    calculate_grounded_ratio,
    calculate_enrichment_confidence
)
from enrichment.features import (
    calculate_company_size,
    calculate_customer_fit,
    calculate_sponsorship_potential
)


company_name = "NVIDIA"

sources = build_company_sources(
    "https://www.nvidia.com"
)

profile = extract_company_profile(
    company_name=company_name,
    sources=sources
)

verification_results = verify_profile_evidence(
    profile,
    sources
)

grounded_ratio = calculate_grounded_ratio(
    verification_results
)

enrichment_confidence = (
    calculate_enrichment_confidence(
        grounded_ratio
    )
)

company_size = calculate_company_size(
    profile
)

customer_fit = calculate_customer_fit(
    profile
)

sponsorship_potential = (
    calculate_sponsorship_potential(
        profile
    )
)

print("Company profile:")
print(profile)

print("\nCompany size:")
print(company_size)

print("\nCustomer fit:")
print(customer_fit)

print("\nSponsorship potential:")
print(sponsorship_potential)

print("\nEnrichment confidence:")
print(enrichment_confidence)