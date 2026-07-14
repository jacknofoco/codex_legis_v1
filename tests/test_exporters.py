from datetime import datetime, timezone

from legislacao_editorial.exporters import export_markdown, export_pdf
from legislacao_editorial.models import LegalArticle, LegalDocument, SourceDocument


def test_exporta_markdown_e_pdf(tmp_path):
    source = SourceDocument("Constituição Federal", "https://www.planalto.gov.br/constituicao",
                            datetime.now(timezone.utc), "hash", "")
    document = LegalDocument(source, articles=[LegalArticle("1", ("TÍTULO I",), "Art. 1º Texto")])
    markdown = export_markdown(document, tmp_path / "lei.md")
    pdf = export_pdf(document, tmp_path / "lei.pdf")
    assert markdown.read_text(encoding="utf-8").startswith("# Constituição Federal")
    assert pdf.read_bytes().startswith(b"%PDF")

