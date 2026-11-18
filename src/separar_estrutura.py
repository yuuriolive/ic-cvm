"""Separa o texto de uma norma da CVM (.docx) na sua hierarquia normativa.

Lê o .docx direto do XML (biblioteca padrão, sem dependências) e gera um JSON em
data_lake/processed/ com um trecho por dispositivo (capítulo, seção, artigo, parágrafo, inciso,
alínea...). Cada trecho traz o texto e o caminho hierárquico, no formato do campo
``hierarquia_normativa`` da tabela ``chunks_regulatorios``. Exemplo::

    Capítulo III > Art. 3º > § 4º > Inciso II

Regras dos textos consolidados da CVM tratadas aqui:

- Redação revogada vem tachada no .docx e é descartada (só fica a redação vigente).
- Notas de alteração ("Caput com redação dada pela Resolução CVM nº 216...") vêm em parágrafo
  próprio, em negrito e itálico; elas vão para o campo ``notas`` do trecho a que se referem.
- Dispositivo revogado aparece como "II – REVOGADO" e recebe ``revogado: true``.
- O sumário (estilos de índice) e o bloco de assinatura são ignorados.

Uso::

    python src/separar_estrutura.py data_lake/raw/resol044consolid.docx
"""

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from gerar_hash import calcular_hash

PASTA_SAIDA = Path("data_lake/processed")

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Níveis da hierarquia, do mais externo para o mais interno.
NIVEIS = ("anexo", "capitulo", "secao", "subsecao", "artigo", "paragrafo", "inciso", "alinea")
NIVEIS_DE_ABERTURA = {"anexo", "capitulo", "secao", "subsecao", "artigo"}

ESTILO_TITULO = "TtulodaResoluo"
ESTILO_EMENTA = "Ementa"

TRAVESSAO = r"[–—-]"
# Dispositivos incluídos depois: Art. 73-A, Inciso XXIX-A (às vezes com travessão: Art. 70–A).
SUFIXO = r"(?:[-–][A-Z]{1,3})?"

PADROES = (
    (
        "anexo",
        re.compile(r"^(anexo(?:\s+normativo)?|suplemento)\s+([IVXLC]+|[A-Z]|\d+)\b", re.I),
    ),
    (
        "subsecao",
        re.compile(rf"^subse[çc][ãa]o\s+([IVXLC]+{SUFIXO}|[úu]nica)(?=\s|{TRAVESSAO}|$)", re.I),
    ),
    (
        "secao",
        re.compile(rf"^se[çc][ãa]o\s+([IVXLC]+{SUFIXO}|[úu]nica)(?=\s|{TRAVESSAO}|$)", re.I),
    ),
    (
        "capitulo",
        re.compile(rf"^cap[íi]tulo\s+([IVXLC]+{SUFIXO}|[úu]nico)(?=\s|{TRAVESSAO}|$)", re.I),
    ),
    ("artigo", re.compile(rf"^Art\.?\s*(\d+)\s*[º°]?\s*({SUFIXO})\s*\.?(?=\s|$)")),
    ("paragrafo_unico", re.compile(r"^Par[áa]grafo\s+[úu]nico\b", re.I)),
    ("paragrafo", re.compile(rf"^§\s*(\d+)\s*[º°]?\s*({SUFIXO})\s*\.?(?=\s|$)")),
    ("inciso", re.compile(rf"^([IVXLC]+{SUFIXO})\s*{TRAVESSAO}\s*")),
    ("alinea", re.compile(r"^([a-z]{1,2})\)\s*")),
)

PADRAO_NOTA = re.compile(
    r"(reda[çc][ãa]o dada|inclu[íi]d|acrescid|revogad|renumerad|alterad|exclu[íi]d|suprimid)"
    r".{0,80}(Resolu[çc][ãa]o|Instru[çc][ãa]o|Delibera[çc][ãa]o)",
    re.I,
)
PADRAO_REVOGADO = re.compile(r"^\W*revogad[oa]\W*$", re.I)
PADRAO_ASSINATURA = re.compile(r"^Assinado eletronicamente", re.I)
TAMANHO_MAXIMO_NOTA = 400


@dataclass
class Paragrafo:
    """Parágrafo do .docx já sem o texto tachado (redação revogada)."""

    texto: str
    estilo: str = ""
    negrito_italico: bool = False
    tabela: bool = False


def _ligado(elemento: ET.Element | None) -> bool:
    """Indica se uma propriedade de formatação (ex.: <w:strike/>) está ativa."""
    return elemento is not None and elemento.get(f"{W}val") not in ("0", "false")


def _normalizar(texto: str) -> str:
    """Troca espaços especiais por espaço comum e junta espaços repetidos."""
    return re.sub(r"\s+", " ", texto.replace("\xa0", " ")).strip()


def _ler_paragrafo(p: ET.Element) -> Paragrafo:
    estilo_el = p.find(f"{W}pPr/{W}pStyle")
    estilo = estilo_el.get(f"{W}val", "") if estilo_el is not None else ""

    partes = []
    negrito_italico = True
    for run in p.iter(f"{W}r"):
        propriedades = run.find(f"{W}rPr")
        if propriedades is not None and (
            _ligado(propriedades.find(f"{W}strike")) or _ligado(propriedades.find(f"{W}dstrike"))
        ):
            continue  # redação revogada

        texto_run = ""
        for filho in run:
            if filho.tag == f"{W}t":
                texto_run += filho.text or ""
            elif filho.tag in (f"{W}tab", f"{W}br"):
                texto_run += " "
        if texto_run.strip() and not (
            propriedades is not None
            and _ligado(propriedades.find(f"{W}b"))
            and _ligado(propriedades.find(f"{W}i"))
        ):
            negrito_italico = False
        partes.append(texto_run)

    texto = _normalizar("".join(partes))
    return Paragrafo(texto=texto, estilo=estilo, negrito_italico=negrito_italico and bool(texto))


def _ler_tabela(tbl: ET.Element) -> Paragrafo:
    """Achata uma tabela em texto: células separadas por " | " e linhas por quebra de linha."""
    linhas = []
    for tr in tbl.iter(f"{W}tr"):
        celulas = []
        for tc in tr.iter(f"{W}tc"):
            textos = [_ler_paragrafo(p).texto for p in tc.iter(f"{W}p")]
            celulas.append(" ".join(t for t in textos if t))
        if any(celulas):
            linhas.append(" | ".join(celulas))
    return Paragrafo(texto="\n".join(linhas), tabela=True)


def _percorrer(container: ET.Element):
    for elemento in container:
        if elemento.tag == f"{W}p":
            yield _ler_paragrafo(elemento)
        elif elemento.tag == f"{W}tbl":
            yield _ler_tabela(elemento)
        elif elemento.tag == f"{W}sdt":  # controles de conteúdo (ex.: sumário automático)
            conteudo = elemento.find(f"{W}sdtContent")
            if conteudo is not None:
                yield from _percorrer(conteudo)


def ler_paragrafos(caminho_docx: Path) -> list[Paragrafo]:
    """Lê o corpo do .docx, na ordem, descartando parágrafos vazios."""
    with zipfile.ZipFile(caminho_docx) as arquivo:
        raiz = ET.fromstring(arquivo.read("word/document.xml"))
    corpo = raiz.find(f"{W}body")
    if corpo is None:
        return []
    return [p for p in _percorrer(corpo) if p.texto]


PREFIXOS = {"capitulo": "Capítulo", "secao": "Seção", "subsecao": "Subseção"}


def _identificar(texto: str) -> tuple[str, str, int] | None:
    """Retorna (nível, rótulo, posição onde o rótulo termina) ou None."""
    for nome, padrao in PADROES:
        m = padrao.match(texto)
        if not m:
            continue
        if nome == "anexo":
            rotulo = _normalizar(m.group(0))
        elif nome in PREFIXOS:
            numero = m.group(1)
            numero = numero.capitalize() if numero[0] in "úÚuU" else numero.upper()
            rotulo = f"{PREFIXOS[nome]} {numero}"
        elif nome == "artigo":
            rotulo = "Art. " + _numero_ordinal(m.group(1)) + m.group(2)
        elif nome == "paragrafo_unico":
            nome, rotulo = "paragrafo", "Parágrafo único"
        elif nome == "paragrafo":
            rotulo = "§ " + _numero_ordinal(m.group(1)) + m.group(2)
        elif nome == "inciso":
            rotulo = f"Inciso {m.group(1)}"
        else:
            rotulo = f"Alínea {m.group(1)}"
        return nome, rotulo.replace("–", "-"), m.end()
    return None


def classificar(texto: str) -> tuple[str, str] | None:
    """Retorna (nível, rótulo) se o texto abre um dispositivo; senão, None.

    Ex.: "Art. 3º  Cumpre ao Diretor..." -> ("artigo", "Art. 3º").
    """
    identificado = _identificar(texto)
    return identificado[:2] if identificado else None


def _numero_ordinal(numero: str) -> str:
    """Artigos e parágrafos de 1 a 9 levam ordinal (1º); a partir de 10, cardinal (10)."""
    return f"{int(numero)}º" if int(numero) < 10 else str(int(numero))


def eh_nota(paragrafo: Paragrafo) -> bool:
    """Nota de alteração: frase curta, toda em negrito e itálico, citando a norma alteradora."""
    return (
        paragrafo.negrito_italico
        and len(paragrafo.texto) <= TAMANHO_MAXIMO_NOTA
        and PADRAO_NOTA.search(paragrafo.texto) is not None
    )


def separar_estrutura(paragrafos: list[Paragrafo]) -> dict:
    """Agrupa os parágrafos em trechos com caminho hierárquico.

    Retorna {"titulo", "ementa", "trechos"}. Texto sem rótulo próprio (continuação, item de
    anexo, tabela) é anexado ao trecho anterior; antes do primeiro dispositivo vira preâmbulo.
    """
    titulo = ementa = None
    caminho: dict[str, str | None] = dict.fromkeys(NIVEIS)
    trechos: list[dict] = []
    em_assinatura = False

    for paragrafo in paragrafos:
        texto = paragrafo.texto

        if paragrafo.estilo.startswith("ndice") or texto.upper() == "SUMÁRIO":
            continue  # sumário
        if titulo is None and paragrafo.estilo == ESTILO_TITULO:
            titulo = texto
            continue
        if ementa is None and paragrafo.estilo == ESTILO_EMENTA:
            ementa = texto
            continue

        if eh_nota(paragrafo):
            if trechos:
                trechos[-1]["notas"].append(texto)
            continue

        identificado = None if paragrafo.tabela else _identificar(texto)

        if PADRAO_ASSINATURA.match(texto):
            em_assinatura = True
            continue
        if em_assinatura:
            if identificado is None or identificado[0] not in NIVEIS_DE_ABERTURA:
                continue  # nome e cargo de quem assina
            em_assinatura = False

        if identificado is None:
            if trechos:
                trechos[-1]["texto"] += "\n" + texto
            else:
                trechos.append(_novo_trecho("preambulo", None, caminho, texto, False))
            continue

        nivel, rotulo, fim_do_rotulo = identificado
        if _repete_cabecalho_de_anexo(nivel, rotulo, caminho, trechos):
            # ex.: "Anexo C – Resolução..." seguido de "ANEXO C"
            trechos[-1]["texto"] += "\n" + texto
            continue
        caminho[nivel] = rotulo
        for mais_interno in NIVEIS[NIVEIS.index(nivel) + 1 :]:
            caminho[mais_interno] = None
        revogado = PADRAO_REVOGADO.match(texto[fim_do_rotulo:]) is not None
        trechos.append(_novo_trecho(nivel, rotulo, caminho, texto, revogado))

    for ordem, trecho in enumerate(trechos, start=1):
        trecho["ordem"] = ordem
    return {"titulo": titulo, "ementa": ementa, "trechos": trechos}


def _repete_cabecalho_de_anexo(nivel: str, rotulo: str, caminho: dict, trechos: list) -> bool:
    return (
        nivel == "anexo"
        and bool(trechos)
        and trechos[-1]["tipo"] == "anexo"
        and (caminho["anexo"] or "").upper() == rotulo.upper()
    )


def _novo_trecho(tipo: str, rotulo: str | None, caminho: dict, texto: str, revogado: bool) -> dict:
    return {
        "ordem": None,
        "tipo": tipo,
        "rotulo": rotulo,
        "hierarquia_normativa": " > ".join(r for r in caminho.values() if r),
        "caminho": dict(caminho),
        "texto": texto,
        "notas": [],
        "revogado": revogado,
    }


def processar_docx(caminho_docx: Path) -> dict:
    """Lê um .docx de norma e devolve o documento estruturado (pronto para virar JSON)."""
    estrutura = separar_estrutura(ler_paragrafos(caminho_docx))
    return {
        "arquivo_origem": caminho_docx.as_posix(),
        "hash_sha256": calcular_hash(caminho_docx),
        "titulo": estrutura["titulo"],
        "ementa": estrutura["ementa"],
        "total_trechos": len(estrutura["trechos"]),
        "trechos": estrutura["trechos"],
    }


def salvar_json(documento: dict, pasta_saida: Path) -> Path:
    """Grava o documento em <pasta_saida>/<nome_do_docx>.json e devolve o caminho."""
    pasta_saida.mkdir(parents=True, exist_ok=True)
    destino = pasta_saida / (Path(documento["arquivo_origem"]).stem + ".json")
    destino.write_text(json.dumps(documento, ensure_ascii=False, indent=2), encoding="utf-8")
    return destino


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("arquivos", nargs="+", type=Path, help="arquivo(s) .docx da norma")
    parser.add_argument(
        "--saida", type=Path, default=PASTA_SAIDA, help=f"pasta do JSON (padrão: {PASTA_SAIDA})"
    )
    args = parser.parse_args(argv)

    for arquivo in args.arquivos:
        documento = processar_docx(arquivo)
        destino = salvar_json(documento, args.saida)
        print(
            f"{arquivo.as_posix()} -> {destino.as_posix()} ({documento['total_trechos']} trechos)"
        )


if __name__ == "__main__":
    main(sys.argv[1:])
