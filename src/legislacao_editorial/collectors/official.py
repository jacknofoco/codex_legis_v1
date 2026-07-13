from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from ..models import SourceDocument


class UnsupportedSourceError(ValueError):
    pass


class OfficialSourceCollector:
    """Baixa HTML somente de fontes governamentais previamente autorizadas."""

    DEFAULT_ALLOWED_DOMAINS = (
        "planalto.gov.br",
        "camara.leg.br",
        "senado.leg.br",
        "stf.jus.br",
        "stj.jus.br",
    )

    def __init__(self, allowed_domains: tuple[str, ...] | None = None) -> None:
        self.allowed_domains = allowed_domains or self.DEFAULT_ALLOWED_DOMAINS

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https":
            raise UnsupportedSourceError("A fonte deve usar HTTPS.")
        if not any(host == domain or host.endswith(f".{domain}") for domain in self.allowed_domains):
            raise UnsupportedSourceError(f"Dominio nao autorizado como fonte oficial: {host}")

    def collect(self, url: str, name: str, timeout: float = 40.0) -> SourceDocument:
        self._validate_url(url)
        headers = {
            "User-Agent": "LegislacaoEditorial/0.2 (+auditoria de fontes publicas)",
            "Accept": "text/html,application/xhtml+xml",
        }
        with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
            response = client.get(url)
            response.raise_for_status()
            html = response.text
        digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
        return SourceDocument(
            name=name,
            url=str(response.url),
            collected_at=datetime.now(timezone.utc),
            content_hash=digest,
            html=html,
        )

