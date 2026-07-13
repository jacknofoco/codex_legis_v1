from datetime import datetime, timezone

from legislacao_editorial.database import SnapshotRepository
from legislacao_editorial.models import LegalArticle, LegalDocument, SourceDocument


def test_snapshot_nao_duplica_mesmo_hash(tmp_path):
    source = SourceDocument("Lei", "https://www.planalto.gov.br/lei", datetime.now(timezone.utc), "hash", "")
    document = LegalDocument(source, articles=[LegalArticle("1", (), "Art. 1º Texto")])
    repository = SnapshotRepository(tmp_path / "db.sqlite3")
    assert repository.save(document) is True
    assert repository.save(document) is False
    assert repository.latest_hash(source.url) == "hash"

