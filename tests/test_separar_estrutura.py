import json
import zipfile
from xml.sax.saxutils import escape

from conftest import RAIZ
from separar_estrutura import classificar, processar_docx, salvar_json

RESOL044 = RAIZ / "data_lake" / "raw" / "resol044consolid.docx"
# SHA-256 do resol044consolid.docx registrado em evidencias.txt
HASH_RESOL044 = "946d5e0f70f92ae95a69eadf1cb8506100bf173b8f76ea4c970fe8f3d17c6903"


def criar_docx(pasta, paragrafos):
    """Cria um .docx mínimo. Cada parágrafo é um texto ou uma lista de runs (texto, formato).

    Formato é um conjunto com "tachado" e/ou "nota" (negrito+itálico); um parágrafo pode ser
    ("estilo", conteudo) para definir o estilo.
    """
    corpo = []
    for paragrafo in paragrafos:
        estilo = ""
        if isinstance(paragrafo, tuple) and len(paragrafo) == 2 and isinstance(paragrafo[1], str):
            estilo, paragrafo = paragrafo
        runs = [(paragrafo, set())] if isinstance(paragrafo, str) else paragrafo
        xml_runs = ""
        for texto, formato in runs:
            propriedades = ""
            if "tachado" in formato:
                propriedades += "<w:strike/>"
            if "nota" in formato:
                propriedades += "<w:b/><w:i/>"
            xml_runs += f'<w:r><w:rPr>{propriedades}</w:rPr><w:t xml:space="preserve">{escape(texto)}</w:t></w:r>'
        ppr = f'<w:pPr><w:pStyle w:val="{estilo}"/></w:pPr>' if estilo else ""
        corpo.append(f"<w:p>{ppr}{xml_runs}</w:p>")

    documento = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{''.join(corpo)}</w:body></w:document>"
    )
    arquivo = pasta / "norma.docx"
    with zipfile.ZipFile(arquivo, "w") as docx:
        docx.writestr("word/document.xml", documento)
    return arquivo


def trechos_de(pasta, paragrafos):
    return processar_docx(criar_docx(pasta, paragrafos))["trechos"]


# ---------- classificar ----------


def test_classificar_reconhece_cada_nivel():
    assert classificar("CAPÍTULO III – DEVERES") == ("capitulo", "Capítulo III")
    assert classificar("Seção II – Constituição") == ("secao", "Seção II")
    assert classificar("Subseção III-A – Taxas") == ("subsecao", "Subseção III-A")
    assert classificar("Art. 1º  Esta Resolução dispõe") == ("artigo", "Art. 1º")
    assert classificar("Art. 10.  O adquirente") == ("artigo", "Art. 10")
    assert classificar("Art. 70–A. Pode ser constituído") == ("artigo", "Art. 70-A")
    assert classificar("§ 4º  A divulgação") == ("paragrafo", "§ 4º")
    assert classificar("§ 10.  As pessoas") == ("paragrafo", "§ 10")
    assert classificar("Parágrafo único.  Na hipótese") == ("paragrafo", "Parágrafo único")
    assert classificar("XXII – pedido de recuperação") == ("inciso", "Inciso XXII")
    assert classificar("b) REVOGADO") == ("alinea", "Alínea b")
    assert classificar("ANEXO NORMATIVO I – FUNDOS") == ("anexo", "ANEXO NORMATIVO I")


def test_classificar_texto_comum_retorna_none():
    assert classificar("O PRESIDENTE DA COMISSÃO DE VALORES MOBILIÁRIOS torna público") is None
    assert classificar("Isso vale para o art. 3º desta Resolução.") is None


# ---------- separar_estrutura (docx sintético) ----------


def test_caminho_hierarquico_completo(tmp_path):
    trechos = trechos_de(
        tmp_path,
        [
            "CAPÍTULO I – ÂMBITO",
            "Seção I – Geral",
            "Art. 1º  Texto do caput:",
            "§ 1º  Texto do parágrafo:",
            "I – texto do inciso:",
            "a) texto da alínea.",
            "Art. 2º  Outro artigo.",
        ],
    )
    caminhos = [t["hierarquia_normativa"] for t in trechos]

    assert caminhos == [
        "Capítulo I",
        "Capítulo I > Seção I",
        "Capítulo I > Seção I > Art. 1º",
        "Capítulo I > Seção I > Art. 1º > § 1º",
        "Capítulo I > Seção I > Art. 1º > § 1º > Inciso I",
        "Capítulo I > Seção I > Art. 1º > § 1º > Inciso I > Alínea a",
        "Capítulo I > Seção I > Art. 2º",
    ]
    assert trechos[4]["caminho"]["inciso"] == "Inciso I"
    assert trechos[6]["caminho"]["paragrafo"] is None
    assert [t["ordem"] for t in trechos] == list(range(1, 8))


def test_novo_capitulo_limpa_secao(tmp_path):
    trechos = trechos_de(
        tmp_path, ["CAPÍTULO I", "Seção I", "Art. 1º  A.", "CAPÍTULO II", "Art. 2º  B."]
    )

    assert trechos[-1]["hierarquia_normativa"] == "Capítulo II > Art. 2º"


def test_texto_tachado_e_descartado(tmp_path):
    trechos = trechos_de(
        tmp_path,
        [
            "CAPÍTULO I",
            [("Art. 9º  Redação antiga.", {"tachado"})],
            "Art. 9º  Redação nova.",
            [("§ 1º  Texto ", set()), ("removido ", {"tachado"}), ("vigente.", set())],
        ],
    )

    artigos = [t for t in trechos if t["tipo"] == "artigo"]
    assert len(artigos) == 1
    assert artigos[0]["texto"] == "Art. 9º Redação nova."
    assert trechos[-1]["texto"] == "§ 1º Texto vigente."


def test_nota_vai_para_o_trecho_anterior(tmp_path):
    nota = "Caput com redação dada pela Resolução CVM nº 216, de 29 de outubro de 2024."
    trechos = trechos_de(tmp_path, ["Art. 9º  Redação nova.", [(nota, {"nota"})]])

    assert len(trechos) == 1
    assert trechos[0]["notas"] == [nota]
    assert nota not in trechos[0]["texto"]


def test_texto_comum_em_negrito_italico_nao_e_nota(tmp_path):
    trechos = trechos_de(tmp_path, ["Art. 1º  Caput.", [("Texto destacado qualquer.", {"nota"})]])

    assert trechos[0]["notas"] == []
    assert "Texto destacado qualquer." in trechos[0]["texto"]


def test_dispositivo_revogado(tmp_path):
    trechos = trechos_de(tmp_path, ["Art. 1º  Caput:", "I – vigente;", "II – REVOGADO"])

    assert [t["revogado"] for t in trechos] == [False, False, True]


def test_continuacao_e_anexada_ao_trecho_anterior(tmp_path):
    trechos = trechos_de(tmp_path, ["Art. 1º  Caput:", "continuação do caput."])

    assert len(trechos) == 1
    assert trechos[0]["texto"] == "Art. 1º Caput:\ncontinuação do caput."


def test_titulo_ementa_preambulo_e_assinatura(tmp_path):
    documento = processar_docx(
        criar_docx(
            tmp_path,
            [
                ("TtulodaResoluo", "Resolução CVM nº 1"),
                ("Ementa", "Dispõe sobre testes."),
                "O PRESIDENTE DA CVM torna público:",
                "Art. 1º  Esta Resolução entra em vigor.",
                "Assinado eletronicamente por",
                "FULANO DE TAL",
                "Presidente",
            ],
        )
    )
    trechos = documento["trechos"]

    assert documento["titulo"] == "Resolução CVM nº 1"
    assert documento["ementa"] == "Dispõe sobre testes."
    assert [t["tipo"] for t in trechos] == ["preambulo", "artigo"]
    assert trechos[0]["hierarquia_normativa"] == ""
    assert "FULANO" not in trechos[-1]["texto"]


def test_salvar_json(tmp_path):
    documento = processar_docx(criar_docx(tmp_path, ["Art. 1º  Ação e informação."]))

    destino = salvar_json(documento, tmp_path / "processed")

    assert destino == tmp_path / "processed" / "norma.json"
    assert json.loads(destino.read_text(encoding="utf-8")) == documento
    assert "informação" in destino.read_text(encoding="utf-8")  # UTF-8 sem escapes \u


# ---------- Resolução CVM 44 (arquivo real do data lake) ----------


def test_resol044_estrutura_geral():
    documento = processar_docx(RESOL044)
    tipos = [t["tipo"] for t in documento["trechos"]]

    assert documento["hash_sha256"] == HASH_RESOL044
    assert documento["titulo"].startswith("Resolução CVM nº 44")
    assert documento["ementa"].startswith("Dispõe sobre a divulgação de informações")
    assert tipos.count("capitulo") == 16
    assert tipos.count("artigo") == 25
    assert tipos[0] == "preambulo"


def test_resol044_art9_sem_redacao_revogada_e_com_notas():
    trechos = processar_docx(RESOL044)["trechos"]
    art9 = [t for t in trechos if t["tipo"] == "artigo" and t["rotulo"] == "Art. 9º"]
    paragrafo1 = next(t for t in trechos if t["hierarquia_normativa"].endswith("Art. 9º > § 1º"))

    assert len(art9) == 1
    assert art9[0]["hierarquia_normativa"] == "Capítulo VI > Art. 9º"
    assert any("Resolução CVM nº 216" in nota for nota in art9[0]["notas"])
    assert paragrafo1["texto"].count("O disposto no caput") == 1


def test_resol044_inciso_dentro_de_paragrafo():
    trechos = processar_docx(RESOL044)["trechos"]
    caminhos = {t["hierarquia_normativa"]: t for t in trechos}

    inciso = caminhos["Capítulo III > Art. 3º > § 4º > Inciso II"]
    assert inciso["texto"].startswith("II – pelo menos 1 (um) portal de notícias")


def test_resol044_termina_sem_assinatura():
    trechos = processar_docx(RESOL044)["trechos"]

    assert trechos[-1]["hierarquia_normativa"] == "Capítulo XVI > Art. 25"
    assert all("Assinado eletronicamente" not in t["texto"] for t in trechos)
