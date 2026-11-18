from conftest import INIT_SQL, MIGRACAO_TEMAS, ler_seed_temas

NUCLEO = {
    "Fundos de Investimento",
    "Companhias Abertas",
    "Ofertas Públicas",
    "Intermediários",
    "Cadastro de Investidores e PLD/FTP",
    "Suitability",
}


def test_seed_tem_os_32_assuntos(temas_oficiais):
    assert len(temas_oficiais) == 32


def test_prioridades_validas_e_contagem(temas_oficiais):
    prioridades = list(temas_oficiais.values())

    assert set(prioridades) == {"nucleo", "segunda_leva", "fora_do_escopo"}
    assert prioridades.count("nucleo") == 6
    assert prioridades.count("segunda_leva") == 16
    assert prioridades.count("fora_do_escopo") == 10


def test_nucleo_e_o_do_piloto(temas_oficiais):
    nucleo = {nome for nome, prioridade in temas_oficiais.items() if prioridade == "nucleo"}

    assert nucleo == NUCLEO


def test_init_sql_e_migracao_tem_o_mesmo_seed():
    assert ler_seed_temas(INIT_SQL) == ler_seed_temas(MIGRACAO_TEMAS)


def test_init_sql_cria_tabelas_de_temas():
    texto = INIT_SQL.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS temas" in texto
    assert "CREATE TABLE IF NOT EXISTS documento_temas" in texto
