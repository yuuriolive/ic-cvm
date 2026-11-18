import csv

from conftest import RAIZ

MANIFESTO = RAIZ / "data_lake" / "manifesto.csv"

COLUNAS = [
    "assuntos",
    "tipo_norma",
    "numero",
    "ano",
    "ementa_curta",
    "url_pagina",
    "url_pdf",
    "status_vigencia",
    "baixado",
    "caminho_local",
]


def ler_manifesto() -> list[dict[str, str]]:
    with MANIFESTO.open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def test_colunas_do_manifesto():
    with MANIFESTO.open(encoding="utf-8", newline="") as arquivo:
        cabecalho = next(csv.reader(arquivo))

    assert cabecalho == COLUNAS


def test_assuntos_sao_oficiais(temas_oficiais):
    for linha in ler_manifesto():
        for assunto in linha["assuntos"].split("|"):
            assert assunto in temas_oficiais, f"assunto fora da lista oficial: {assunto}"


def test_todo_assunto_do_nucleo_tem_norma(temas_oficiais):
    nucleo = {nome for nome, prioridade in temas_oficiais.items() if prioridade == "nucleo"}
    cobertos = {assunto for linha in ler_manifesto() for assunto in linha["assuntos"].split("|")}

    assert nucleo <= cobertos


def test_campos_bem_formados():
    for linha in ler_manifesto():
        assert linha["numero"].isdigit()
        assert len(linha["ano"]) == 4 and linha["ano"].isdigit()
        assert linha["status_vigencia"] == "VIGENTE"
        assert linha["url_pagina"].startswith("https://conteudo.cvm.gov.br/legislacao/resolucoes/")
        assert linha["url_pdf"].startswith("https://conteudo.cvm.gov.br/") and linha[
            "url_pdf"
        ].endswith(".pdf")


def test_sem_norma_repetida():
    numeros = [(linha["tipo_norma"], linha["numero"]) for linha in ler_manifesto()]

    assert len(numeros) == len(set(numeros))


def test_baixados_existem_no_data_lake():
    for linha in ler_manifesto():
        assert linha["baixado"] in ("s", "n")
        if linha["baixado"] == "s":
            for caminho in linha["caminho_local"].split("|"):
                assert (RAIZ / caminho).is_file(), f"arquivo não encontrado: {caminho}"
        else:
            assert linha["caminho_local"] == ""


def test_baixados_sao_44_80_175():
    baixados = {linha["numero"] for linha in ler_manifesto() if linha["baixado"] == "s"}

    assert baixados == {"44", "80", "175"}
