from enrichment.fetcher import build_company_sources

sources = build_company_sources(
    "https://www.nvidia.com/this-page-does-not-exist"
)

for source in sources:
    print("=" * 60)
    print(source.source_id)
    print(source.url)
    print(source.text[:500])