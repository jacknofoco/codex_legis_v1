# Sistema Jurídico-Editorial

Aplicação em Python para transformar legislação brasileira de fontes oficiais em material de estudo rastreável. A versão atual reconstrói e operacionaliza o protótipo que antes existia apenas como descrição no repositório.

## O que já funciona

- baixa uma lei por URL oficial HTTPS;
- registra URL final, data/hora e hash SHA-256;
- identifica artigos e o contexto de títulos, capítulos e seções;
- guarda o histórico de coletas em SQLite;
- gera material completo ou seccionado em Markdown e PDF;
- lê PDF de edital e lista referências normativas explícitas em JSON e Markdown;
- verifica quinzenalmente as fontes configuradas e abre uma issue quando o hash diverge da referência;
- executa testes automaticamente no GitHub Actions.

O sistema **não substitui conferência jurídica humana**. A extração de edital é preliminar e não associa automaticamente conteúdos implícitos. Jurisprudência STF/STJ e incidência estatística em provas permanecem no roadmap.

## Instalação no Windows — sem programês

Abra o PowerShell na pasta do projeto e execute:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

Se `py -3.12` não existir, use `python` no primeiro comando. Python 3.11 ou superior é aceito.

## Gerar a Constituição completa

```powershell
legislacao gerar-lei-completa `
  --url "https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm" `
  --nome "Constituição Federal" `
  --arquivo "constituicao-federal" `
  --saida "outputs/constituicao-federal"
```

Serão criados:

```text
outputs/constituicao-federal/
├── constituicao-federal.md
└── constituicao-federal.pdf
```

## Gerar somente um trecho

O filtro procura o texto informado nos títulos, capítulos, seções e dispositivos. Separe alternativas com vírgula ou ponto e vírgula.

```powershell
legislacao gerar-lei-seccionada `
  --url "https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm" `
  --nome "Constituição Federal" `
  --trecho "DA SEGURANÇA PÚBLICA,Art. 144" `
  --arquivo "seguranca-publica" `
  --saida "outputs/seguranca-publica"
```

## Analisar um edital

```powershell
legislacao analisar-edital `
  --pdf "C:\Editais\edital.pdf" `
  --saida "outputs\analise-edital"
```

O comando cria `legislacoes-identificadas.json` e `legislacoes-identificadas.md`, com ocorrências e páginas. Ele identifica apenas referências escritas no edital, evitando inventar leis.

## Monitorar alterações

As fontes ficam em `config/fontes.json`. O arquivo `data/baselines.json` guarda os hashes aprovados. Para cadastrar a primeira referência, rode a verificação, confira a fonte e copie o hash atual para a chave correspondente:

```json
{
  "constituicao-federal": "HASH_CONFERIDO_AQUI"
}
```

Depois execute:

```powershell
legislacao verificar-atualizacoes
```

No GitHub, o workflow **Monitor legislativo** roda nos dias 1 e 15 e também pode ser iniciado manualmente. Uma mudança gera relatório e issue; ela é um alerta para revisão, não prova isolada de alteração legislativa.

## Arquitetura

```text
src/legislacao_editorial/
├── collectors/   # fontes oficiais e política de domínios
├── database/     # snapshots auditáveis em SQLite
├── exporters/    # Markdown e PDF
├── parsers/      # estrutura de diplomas legais
├── services/     # edital e monitoramento
└── cli.py        # comandos de terminal
```

## Roadmap responsável

1. validar o parser com Constituição, Código Penal e leis especiais;
2. mapear tópicos de edital para recortes por artigo, com confirmação humana;
3. integrar pesquisa oficial de jurisprudência do STF/STJ com metadados e links;
4. criar diagramação editorial avançada e DOCX;
5. adicionar incidência por banca somente a partir de uma base de questões licenciada e auditável.

