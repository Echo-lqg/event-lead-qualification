from enrichment.fetcher import build_company_sources
from enrichment.extractor import extract_company_profile


company_name = "NVIDIA"

sources = build_company_sources(
    "https://www.nvidia.com"
)

profile = extract_company_profile(
    company_name=company_name,
    sources=sources
)

print(profile)