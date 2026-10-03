from enrichment.fetcher import fetch_page

url = "https://www.nvidia.com"

text = fetch_page(url)

print(text[:3000])