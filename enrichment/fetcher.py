import httpx
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime, timezone

from enrichment.schemas import SourceDocument


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

def build_source_document(
    url : str,
    source_id : str
) ->SourceDocument:

    text = fetch_page(url)

    content_hash = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

    return SourceDocument(
        source_id=source_id,
        source_type="website",
        url=url,
        fetched_at=datetime.now(
            timezone.utc
        ).isoformat(),
        content_hash=content_hash,
        text=text
    )