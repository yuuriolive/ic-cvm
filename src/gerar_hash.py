"""Gera o hash SHA-256 de cada arquivo da camada raw do data lake."""

import hashlib
from pathlib import Path

PASTA_RAW = Path("data_lake/raw")


def calcular_hash(arquivo: Path) -> str:
    """Retorna o hash SHA-256 (hexadecimal) do conteúdo de um arquivo."""
    return hashlib.sha256(arquivo.read_bytes()).hexdigest()


def gerar_hashes(pasta: Path) -> dict[str, str]:
    """Retorna {nome_do_arquivo: sha256} para cada arquivo da pasta, em ordem alfabética.

    Arquivos ocultos (ex.: .gitkeep) e subpastas são ignorados.
    """
    return {
        arquivo.name: calcular_hash(arquivo)
        for arquivo in sorted(pasta.iterdir())
        if arquivo.is_file() and not arquivo.name.startswith(".")
    }


def main() -> None:
    for nome, hash_sha256 in gerar_hashes(PASTA_RAW).items():
        print(f"Arquivo: {nome} | SHA-256: {hash_sha256}")


if __name__ == "__main__":
    main()
