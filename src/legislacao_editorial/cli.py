from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .collectors import OfficialSourceCollector
from .database import SnapshotRepository
from .exporters import export_markdown, export_pdf
from .parsers import LegalHtmlParser
from .services import EditalAnalyzer, UpdateMonitor


def _generate(args: argparse.Namespace, section: str | None = None) -> int:
    source = OfficialSourceCollector().collect(args.url, args.nome)
    parser = LegalHtmlParser()
    document = parser.parse(source)
    if section:
        document = parser.section(document, section)
    output = Path(args.saida)
    output.mkdir(parents=True, exist_ok=True)
    SnapshotRepository(args.banco).save(document)
    stem = args.arquivo or "material"
    markdown = export_markdown(document, output / f"{stem}.md")
    pdf = export_pdf(document, output / f"{stem}.pdf")
    print(f"OK: {len(document.articles)} artigos | {markdown} | {pdf}")
    return 0


def _analyze_edital(args: argparse.Namespace) -> int:
    analyzer = EditalAnalyzer()
    references = analyzer.analyze(args.pdf)
    json_path, md_path = analyzer.export(references, args.saida)
    print(f"OK: {len(references)} referências | {json_path} | {md_path}")
    return 0


def _check_updates(args: argparse.Namespace) -> int:
    monitor = UpdateMonitor()
    results = monitor.check(args.config, args.baseline)
    report = monitor.write_report(results, args.relatorio)
    changed = [item for item in results if item.changed]
    missing = [item for item in results if item.previous_hash is None]
    print(f"Relatório: {report} | alterações: {len(changed)} | sem baseline: {len(missing)}")
    return 2 if changed or missing else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="legislacao", description="Sistema jurídico-editorial auditável")
    parser.add_argument("--banco", default="data/legislacao.sqlite3", help="Banco local de snapshots")
    commands = parser.add_subparsers(dest="command", required=True)

    complete = commands.add_parser("gerar-lei-completa", help="Gera Markdown e PDF de uma fonte oficial")
    complete.add_argument("--url", required=True)
    complete.add_argument("--nome", required=True)
    complete.add_argument("--saida", required=True)
    complete.add_argument("--arquivo")
    complete.set_defaults(handler=lambda args: _generate(args))

    sectioned = commands.add_parser("gerar-lei-seccionada", help="Gera apenas dispositivos do trecho informado")
    sectioned.add_argument("--url", required=True)
    sectioned.add_argument("--nome", required=True)
    sectioned.add_argument("--trecho", required=True)
    sectioned.add_argument("--saida", required=True)
    sectioned.add_argument("--arquivo")
    sectioned.set_defaults(handler=lambda args: _generate(args, args.trecho))

    edital = commands.add_parser("analisar-edital", help="Extrai referências normativas explícitas de um PDF")
    edital.add_argument("--pdf", required=True)
    edital.add_argument("--saida", required=True)
    edital.set_defaults(handler=_analyze_edital)

    updates = commands.add_parser("verificar-atualizacoes", help="Compara fontes com hashes de referência")
    updates.add_argument("--config", default="config/fontes.json")
    updates.add_argument("--baseline", default="data/baselines.json")
    updates.add_argument("--relatorio", default="updates/report.md")
    updates.set_defaults(handler=_check_updates)
    return parser


def main(argv: list[str] | None = None) -> None:
    try:
        args = build_parser().parse_args(argv)
        raise SystemExit(args.handler(args))
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as error:
        print(f"ERRO: {error}", file=sys.stderr)
        raise SystemExit(1)
