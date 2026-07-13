from __future__ import annotations

from pathlib import Path

from ..models import LegalDocument


def export_markdown(document: LegalDocument, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    source = document.source
    lines = [
        f"# {source.name}",
        "",
        f"> Fonte oficial: [{source.url}]({source.url})  ",
        f"> Coleta: {source.collected_at.isoformat()}  ",
        f"> SHA-256: `{source.content_hash}`  ",
        f"> Artigos incluídos: {len(document.articles)}",
        "",
        "## Sumário do recorte",
        "",
    ]
    seen = set()
    for article in document.articles:
        for heading in article.heading_path:
            if heading not in seen:
                lines.append(f"- {heading}")
                seen.add(heading)
    lines.extend(["", "---", ""])

    previous_path: tuple[str, ...] = ()
    for article in document.articles:
        if article.heading_path != previous_path:
            for index, heading in enumerate(article.heading_path, start=2):
                lines.extend([f"{'#' * min(index, 6)} {heading}", ""])
            previous_path = article.heading_path
        lines.extend([f"### Art. {article.number}", "", article.text, ""])
    target.write_text("\n".join(lines), encoding="utf-8")
    return target

