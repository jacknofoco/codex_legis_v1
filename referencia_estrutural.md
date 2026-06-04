# Referencia estrutural observada

Arquivo analisado: `LEGISLACAO-referencia_estrutural.pdf`

Observacoes estruturais aproveitaveis, sem copia de identidade visual ou conteudo autoral:

- Documento longo com paginacao discreta.
- Abertura com identificacao do diploma legal, ato normativo e data/versao de atualizacao.
- Sumario no inicio, antes do corpo normativo.
- Indice de tabelas separado do sumario.
- Organizacao por titulo, capitulo, secao e blocos tematicos.
- Corpo em fonte sem serifa, com hierarquia compacta e alta densidade de leitura.
- Uso de tabelas/quadros para sintese, mas esta primeira versao ainda nao implementa tabelas.
- Fonte predominante observada no PDF: familias sem serifa como Lato e Montserrat; neste projeto, por preferencia do usuario, o PDF tenta usar Century Gothic e recua para Helvetica quando a fonte nao esta disponivel.

Decisoes para a versao inicial:

- Manter capa interna simples com metadados auditaveis.
- Gerar sumario automatico por contexto normativo e artigos.
- Incluir indice de tabelas vazio enquanto o modulo de tabelas nao existir.
- Preservar corpo normativo limpo, com artigos, paragrafos, incisos e alineas.
- Nao implementar jurisprudencia nesta etapa.
