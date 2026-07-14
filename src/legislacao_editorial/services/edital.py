from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader


REFERENCE_PATTERNS = (
    re.compile(r"\bConstitui[cç][aã]o(?:\s+Federal|\s+da\s+Rep[uú]blica)?\b", re.IGNORECASE),
    re.compile(r"\b(?:Lei|Decreto(?:-Lei)?|Lei Complementar|Emenda Constitucional)\s+"
               r"(?:Federal\s+|Estadual\s+)?n?[ºo°.]?\s*[\d.]+(?:/\d{2,4})?\b", re.IGNORECASE),
    re.compile(r"\bC[oó]digo\s+(?:Penal|Civil|de Processo Penal|de Processo Civil|Tribut[aá]rio Nacional)\b",
               re.IGNORECASE),
)


@dataclass(frozen=True)
class LegalReference:
    reference: str
    occurrences: int
    pages: tuple[int, ...]


class EditalAnalyzer:
    """Extrai referências normativas explícitas; não inventa diplomas implícitos."""

    def extract_pages(self, pdf_path: str | Path) -> list[str]:
        reader = PdfReader(str(pdf_path))
        return [(page.extract_text() or "") for page in reader.pages]

    def analyze_text_pages(self, pages: list[str]) -> list[LegalReference]:
        found: dict[str, dict[str, object]] = {}
        for page_number, text in enumerate(pages, start=1):
            normalized = re.sub(r"\s+", " ", text)
            for pattern in REFERENCE_PATTERNS:
                for match in pattern.finditer(normalized):
                    label = re.sub(r"\s+", " ", match.group(0)).strip(" ,;:.")
                    key = label.casefold()
                    record = found.setdefault(key, {"label": label, "count": 0, "pages": set()})
                    record["count"] = int(record["count"]) + 1
                    cast_pages = record["pages"]
                    assert isinstance(cast_pages, set)
                    cast_pages.add(page_number)
        return [
            LegalReference(str(value["label"]), int(value["count"]), tuple(sorted(value["pages"])))
            for value in sorted(found.values(), key=lambda item: str(item["label"]).casefold())
        ]

    def analyze(self, pdf_path: str | Path) -> list[LegalReference]:
        return self.analyze_text_pages(self.extract_pages(pdf_path))

    def export(self, references: list[LegalReference], output_dir: str | Path) -> tuple[Path, Path]:
        directory = Path(output_dir)
        directory.mkdir(parents=True, exist_ok=True)
        json_path = directory / "legislacoes-identificadas.json"
        md_path = directory / "legislacoes-identificadas.md"
        json_path.write_text(json.dumps([asdict(item) for item in references], ensure_ascii=False, indent=2),
                             encoding="utf-8")
        lines = ["# Legislações identificadas no edital", "",
                 "> Resultado automático preliminar. Confirme os itens no conteúdo programático oficial.", ""]
        if references:
            lines.extend(["| Referência | Ocorrências | Páginas |", "|---|---:|---|"])
            lines.extend(f"| {item.reference} | {item.occurrences} | {', '.join(map(str, item.pages))} |"
                         for item in references)
        else:
            lines.append("Nenhuma referência normativa explícita foi encontrada.")
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return json_path, md_path

