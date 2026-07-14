from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class SourceDocument:
    name: str
    url: str
    collected_at: datetime
    content_hash: str
    html: str


@dataclass(frozen=True)
class LegalArticle:
    number: str
    heading_path: tuple[str, ...]
    text: str


@dataclass
class LegalDocument:
    source: SourceDocument
    preamble: list[str] = field(default_factory=list)
    articles: list[LegalArticle] = field(default_factory=list)

