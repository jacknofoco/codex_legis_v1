# Legislacao Editorial

Projeto inicial em Python e SQLite para transformar legislacao federal oficial em material de estudo organizado.

## Escopo desta primeira versao

- Coletor de leis do Planalto por URL oficial.
- Parser basico de artigos, paragrafos, incisos e alineas.
- Banco SQLite com rastreabilidade de fonte, data de coleta e hash.
- Exportacao Markdown para Obsidian.
- Exportacao PDF simples com fonte sem serifa, preferindo Century Gothic quando disponivel.

Jurisprudencia, incidencia estatistica em provas, analise de edital, DOCX e atualizacao periodica ainda nao foram implementados.

## Instalar

```powershell
python -m pip install -e .
```

## Gerar lei completa

```powershell
python -m legislacao_editorial gerar-lei-completa `
  --url "https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm" `
  --nome "Codigo Penal" `
  --saida "outputs/codigo-penal"
```

## Gerar lei seccionada

O recorte atual filtra por texto encontrado em titulo, capitulo, secao, artigo ou conteudo do dispositivo.

```powershell
python -m legislacao_editorial gerar-lei-seccionada `
  --url "https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm" `
  --nome "Codigo Penal" `
  --trecho "Crimes contra a Administracao Publica" `
  --saida "outputs/codigo-penal-recorte"
```

## Estrutura

```text
src/legislacao_editorial/
  collectors/      coleta em fontes oficiais
  database/        SQLite e historico por hash
  editorial/       configuracao visual inicial
  exporters/       Markdown e PDF
  parsers/         parser de dispositivos legais
  cli.py           comandos de uso
tests/             testes de parser e exportacao
```
