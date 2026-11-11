import hashlib

from gerar_hash import calcular_hash, gerar_hashes

# SHA-256 conhecido da string "abc" (vetor de teste do NIST FIPS 180-2)
HASH_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_calcular_hash_vetor_conhecido(tmp_path):
    arquivo = tmp_path / "abc.txt"
    arquivo.write_bytes(b"abc")

    assert calcular_hash(arquivo) == HASH_ABC


def test_calcular_hash_arquivo_vazio(tmp_path):
    arquivo = tmp_path / "vazio.txt"
    arquivo.write_bytes(b"")

    assert calcular_hash(arquivo) == hashlib.sha256(b"").hexdigest()


def test_conteudos_diferentes_geram_hashes_diferentes(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_bytes(b"resolucao 175")
    b.write_bytes(b"resolucao 176")

    assert calcular_hash(a) != calcular_hash(b)


def test_gerar_hashes_ignora_subpastas_e_ocultos(tmp_path):
    (tmp_path / "b.pdf").write_bytes(b"pdf")
    (tmp_path / "a.csv").write_bytes(b"abc")
    (tmp_path / ".gitkeep").write_bytes(b"")
    (tmp_path / "subpasta").mkdir()

    resultado = gerar_hashes(tmp_path)

    assert list(resultado) == ["a.csv", "b.pdf"]
    assert resultado["a.csv"] == HASH_ABC


def test_gerar_hashes_pasta_vazia(tmp_path):
    assert gerar_hashes(tmp_path) == {}
