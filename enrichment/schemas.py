from typing import Literal
from pydantic import BaseModel

class SourceDocument(BaseModel):
    source_id: str

    source_type: Literal[
        "website",
        "wikipedia",
        "wikidata",
        "search"       
    ]

    url : str
    fetched_at : str
    content_hash : str
    text : str

    
