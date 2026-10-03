from enrichment.fetcher import build_source_document

url = "https://www.nvidia.com"

document = build_source_document(
    url=url,
    source_id="S1"
)

print("Source ID:")
print(document.source_id)

print("\nURL:")
print(document.url)

print("\nFetched at:")
print(document.fetched_at)

print("\nContent hash:")
print(document.content_hash)

print("\nText preview:")
print(document.text[:1000])