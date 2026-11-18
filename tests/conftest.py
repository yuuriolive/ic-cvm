import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
MIGRACAO_TEMAS = RAIZ / "db" / "migrations" / "001_temas.sql"
INIT_SQL = RAIZ / "db" / "init.sql"


def ler_seed_temas(arquivo_sql: Path) -> dict[str, str]:
    """Extrai {nome: prioridade} do INSERT INTO temas de um arquivo SQL."""
    texto = arquivo_sql.read_text(encoding="utf-8")
    insert = texto.split("INSERT INTO temas", 1)[1].split(";", 1)[0]
    return dict(re.findall(r"\('((?:[^']|'')+)',\s*'(\w+)'\)", insert))


@pytest.fixture
def temas_oficiais() -> dict[str, str]:
    return ler_seed_temas(MIGRACAO_TEMAS)
