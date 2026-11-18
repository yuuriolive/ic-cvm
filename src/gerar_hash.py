"""Gera o hash SHA-256 de cada arquivo da camada raw do data lake.

As normas ficam direto em data_lake/raw/. Dados cadastrais (que não são normas e não entram no
RAG) ficam na subpasta data_lake/raw/dados_cadastrais/ e são listados em um bloco separado.
"""

import hashlib
from pathlib import Path

PASTA_RAW = Path("data_lake/raw")
PASTA_DADOS_CADASTRAIS = PASTA_RAW / "dados_cadastrais"


def calcular_hash(arquivo: Path) -> str:
    """Retorna o hash SHA-256 (hexadecimal) do conteúdo de um arquivo."""
    return hashlib.sha256(arquivo.read_bytes()).hexdigest()


def gerar_hashes(pasta: Path) -> dict[str, str]:
    """Retorna {nome_do_arquivo: sha256} para cada arquivo da pasta, em ordem alfabética.

    Arquivos ocultos (ex.: .gitkeep) e subpastas são ignorados. Pasta inexistente retorna {}.
    """
    if not pasta.is_dir():
        return {}
    return {
        arquivo.name: calcular_hash(arquivo)
        for arquivo in sorted(pasta.iterdir())
        if arquivo.is_file() and not arquivo.name.startswith(".")
    }


def main() -> None:
    blocos = {
        "Normas": PASTA_RAW,
        "Dados cadastrais (fora do RAG)": PASTA_DADOS_CADASTRAIS,
    }
    for titulo, pasta in blocos.items():
        print(f"=== {titulo} ({pasta.as_posix()}) ===")
        for nome, hash_sha256 in gerar_hashes(pasta).items():
            print(f"Arquivo: {nome} | SHA-256: {hash_sha256}")


if __name__ == "__main__":
    main()
