from datetime import datetime, timezone

from legislacao_editorial.models import SourceDocument
from legislacao_editorial.parsers import LegalHtmlParser


HTML = """
<html><body>
<h2>TÍTULO I</h2><h3>DOS PRINCÍPIOS FUNDAMENTAIS</h3>
<p>Art. 1º A República Federativa do Brasil constitui-se em Estado Democrático de Direito.</p>
<p>Parágrafo único. Todo o poder emana do povo.</p>
<p>Art. 2º São Poderes da União, independentes e harmônicos entre si.</p>
<h2>TÍTULO II</h2><h3>DOS DIREITOS E GARANTIAS FUNDAMENTAIS</h3>
<p>Art. 5º Todos são iguais perante a lei.</p>
</body></html>
"""


def source() -> SourceDocument:
    return SourceDocument("Constituição Federal", "https://www.planalto.gov.br/exemplo",
                          datetime.now(timezone.utc), "abc", HTML)


def test_parser_identifica_artigos_e_contexto():
    document = LegalHtmlParser().parse(source())
    assert [article.number for article in document.articles] == ["1", "2", "5"]
    assert "Parágrafo único" in document.articles[0].text
    assert document.articles[0].heading_path == ("TÍTULO I",)


def test_recorte_por_titulo():
    parser = LegalHtmlParser()
    document = parser.parse(source())
    section = parser.section(document, "TÍTULO II")
    assert [article.number for article in section.articles] == ["5"]


def test_novo_titulo_substitui_hierarquia_anterior():
    parser = LegalHtmlParser()
    document = parser.parse(source())
    assert document.articles[-1].heading_path == ("TÍTULO II",)
