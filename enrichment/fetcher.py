import httpx
from bs4 import BeautifulSoup


def fetch_page(url: str) -> str:
    response = httpx.get(
        url,
        timeout=10,
        follow_redirects=True,
        headers={
            "User-Agent": "event-lead-qualification/1.0"
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    for element in soup([
        "script",
        "style",
        "nav",
        "footer"
    ]):
        element.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return text[:12000]