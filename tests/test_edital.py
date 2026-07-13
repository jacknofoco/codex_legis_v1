from legislacao_editorial.services.edital import EditalAnalyzer


def test_identifica_referencias_explicitas_e_paginas():
    pages = [
        "Direito Constitucional: Constituição Federal. Lei nº 8.112/1990.",
        "Direito Penal: Código Penal e Decreto-Lei nº 2.848/1940. Lei nº 8.112/1990.",
    ]
    references = EditalAnalyzer().analyze_text_pages(pages)
    by_name = {item.reference.casefold(): item for item in references}
    lei = by_name["lei nº 8.112/1990"]
    assert lei.occurrences == 2
    assert lei.pages == (1, 2)
    assert any("código penal" == key for key in by_name)

