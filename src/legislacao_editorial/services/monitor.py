from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..collectors import OfficialSourceCollector


@dataclass(frozen=True)
class UpdateResult:
    name: str
    url: str
    previous_hash: str | None
    current_hash: str

    @property
    def changed(self) -> bool:
        return self.previous_hash is not None and self.previous_hash != self.current_hash


class UpdateMonitor:
    def __init__(self, collector: OfficialSourceCollector | None = None) -> None:
        self.collector = collector or OfficialSourceCollector()

    def check(self, config_path: str | Path, baseline_path: str | Path) -> list[UpdateResult]:
        config = json.loads(Path(config_path).read_text(encoding="utf-8"))
        baseline_file = Path(baseline_path)
        baselines = json.loads(baseline_file.read_text(encoding="utf-8")) if baseline_file.exists() else {}
        results = []
        for source in config["sources"]:
            document = self.collector.collect(source["url"], source["name"])
            results.append(UpdateResult(source["name"], document.url, baselines.get(source["id"]),
                                        document.content_hash))
        return results

    @staticmethod
    def write_report(results: list[UpdateResult], path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# Relatório de atualização legislativa", ""]
        for item in results:
            status = "ALTERAÇÃO DETECTADA" if item.changed else ("SEM BASELINE" if item.previous_hash is None else "sem alteração")
            lines.extend([f"## {item.name}", "", f"- Status: **{status}**", f"- Fonte: {item.url}",
                          f"- Hash anterior: `{item.previous_hash or 'não cadastrado'}`",
                          f"- Hash atual: `{item.current_hash}`", ""])
        target.write_text("\n".join(lines), encoding="utf-8")
        return target

