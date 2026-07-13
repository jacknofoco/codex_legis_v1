from __future__ import annotations

import re

from bs4 import BeautifulSoup

from ..models import LegalArticle, LegalDocument, SourceDocument


ARTICLE_RE = re.compile(r"^Art\.\s*(\d+[A-Za-z]?(?:[-–][A-Za-z])?)(?:\s*[ºo°.]*)\b", re.IGNORECASE)
HEADING_RE = re.compile(
    r"^(T[IÍ]TULO|CAP[IÍ]TULO|SE[CÇ][AÃ]O|SUBSE[CÇ][AÃ]O|LIVRO|PARTE|ATO DAS DISPOSI[CÇ][OÕ]ES)",
    re.IGNORECASE,
)


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


class LegalHtmlParser:
    """Parser tolerante ao HTML historico e pouco uniforme de portais oficiais."""

    def parse(self, source: SourceDocument) -> LegalDocument:
        soup = BeautifulSoup(source.html, "html.parser")
        for tag in soup(["script", "style", "noscript", "nav", "footer"]):
            tag.decompose()

        lines = [_clean(text) for text in soup.stripped_strings]
        lines = [line for line in lines if line]
        document = LegalDocument(source=source)
        heading_levels: dict[int, str] = {}
        current_number: str | None = None
        current_lines: list[str] = []
        current_path: tuple[str, ...] = ()

        def flush() -> None:
            nonlocal current_number, current_lines, current_path
            if current_number and current_lines:
                document.articles.append(
                    LegalArticle(current_number, current_path, "\n".join(current_lines))
                )
            current_number = None
            current_lines = []

        for line in lines:
            if HEADING_RE.match(line) and len(line) <= 180:
                flush()
                level = HEADING_RE.match(line).group(1).upper()
                level_order = {"PARTE": 0, "LIVRO": 1, "TÍTULO": 2, "TITULO": 2,
                               "CAPÍTULO": 3, "CAPITULO": 3, "SEÇÃO": 4, "SECAO": 4,
                               "SUBSEÇÃO": 5, "SUBSECAO": 5}
                rank = level_order.get(level, 0)
                heading_levels = {key: value for key, value in heading_levels.items() if key < rank}
                heading_levels[rank] = line
                continue

            article = ARTICLE_RE.match(line)
            if article:
                flush()
                current_number = article.group(1)
                current_path = tuple(value for _, value in sorted(heading_levels.items()))
                current_lines = [line]
            elif current_number:
                current_lines.append(line)
            elif len(document.preamble) < 80:
                document.preamble.append(line)

        flush()
        if not document.articles:
            raise ValueError("Nenhum artigo foi identificado na pagina oficial.")
        return document

    def section(self, document: LegalDocument, query: str) -> LegalDocument:
        terms = [term.casefold() for term in re.split(r"\s*[,;]\s*", query) if term.strip()]
        selected = []
        for article in document.articles:
            haystack = " ".join((*article.heading_path, article.text)).casefold()
            if any(term in haystack for term in terms):
                selected.append(article)
        if not selected:
            raise ValueError(f"O trecho '{query}' nao foi localizado no diploma.")
        return LegalDocument(source=document.source, preamble=document.preamble, articles=selected)
