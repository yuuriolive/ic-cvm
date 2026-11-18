CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documentos_regulatorios (
    id SERIAL PRIMARY KEY,
    orgao VARCHAR(10) NOT NULL,
    tipo_norma VARCHAR(50) NOT NULL,
    numero_norma VARCHAR(50) NOT NULL,
    status_vigencia VARCHAR(20) DEFAULT 'VIGENTE',
    hash_sha256 VARCHAR(64) UNIQUE NOT NULL,
    caminho_arquivo TEXT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chunks_regulatorios (
    id SERIAL PRIMARY KEY,
    documento_id INT REFERENCES documentos_regulatorios(id) ON DELETE CASCADE,
    hierarquia_normativa TEXT,
    texto_chunk TEXT NOT NULL,
    embedding vector(1024)
);

-- Taxonomia de temas (assuntos oficiais da CVM).
-- Mantenha este bloco idêntico ao de db/migrations/001_temas.sql
-- (tests/test_temas_sql.py verifica que os dois seeds são iguais).

CREATE TABLE IF NOT EXISTS temas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) UNIQUE NOT NULL,
    prioridade VARCHAR(20) NOT NULL
        CHECK (prioridade IN ('nucleo', 'segunda_leva', 'fora_do_escopo'))
);

-- Uma norma pode estar em mais de um assunto no portal da CVM (ex.: Resolução CVM 232).
CREATE TABLE IF NOT EXISTS documento_temas (
    documento_id INT NOT NULL REFERENCES documentos_regulatorios(id) ON DELETE CASCADE,
    tema_id INT NOT NULL REFERENCES temas(id) ON DELETE CASCADE,
    PRIMARY KEY (documento_id, tema_id)
);

CREATE INDEX IF NOT EXISTS idx_documento_temas_tema ON documento_temas (tema_id);

-- Seed: os 32 assuntos oficiais da "Lista de Assuntos" do portal da CVM (ver docs/topicos.md).
INSERT INTO temas (nome, prioridade) VALUES
    ('Administradores de Carteiras de Valores Mobiliários', 'segunda_leva'),
    ('Agências de Classificação de Risco de Crédito', 'segunda_leva'),
    ('Agentes Fiduciários', 'segunda_leva'),
    ('Analistas de Valores Mobiliários', 'segunda_leva'),
    ('Assessores de Investimento', 'segunda_leva'),
    ('Atos expedidos pela CVM', 'fora_do_escopo'),
    ('Auditores Independentes', 'segunda_leva'),
    ('BDR', 'segunda_leva'),
    ('Cadastro de Investidores e PLD/FTP', 'nucleo'),
    ('Cadastro de Participantes Regulados', 'fora_do_escopo'),
    ('Clubes de Investimento', 'segunda_leva'),
    ('Companhias Abertas', 'nucleo'),
    ('Companhias Securitizadoras', 'segunda_leva'),
    ('Consultores de Valores Mobiliários', 'segunda_leva'),
    ('Fundos de Investimento', 'nucleo'),
    ('Identidade Visual Institucional', 'fora_do_escopo'),
    ('Infraestrutura do Mercado', 'segunda_leva'),
    ('Intermediários', 'nucleo'),
    ('Investidores Não Residentes', 'segunda_leva'),
    ('Mercados Organizados', 'segunda_leva'),
    ('Normas Contábeis', 'segunda_leva'),
    ('Ofertas Públicas', 'nucleo'),
    ('Ouvidoria', 'fora_do_escopo'),
    ('Portabilidade', 'segunda_leva'),
    ('Regimento Interno', 'fora_do_escopo'),
    ('Ritos Processuais', 'fora_do_escopo'),
    ('Sandbox Regulatório', 'segunda_leva'),
    ('Sistema Integrado de Gestão de Riscos da CVM', 'fora_do_escopo'),
    ('Sistemas de Gestão Institucional da CVM', 'fora_do_escopo'),
    ('Sociedades beneficiárias de recursos oriundos de incentivos fiscais (Cias. Incentivadas)', 'fora_do_escopo'),
    ('Suitability', 'nucleo'),
    ('Taxas, Débitos e Restituições', 'fora_do_escopo')
ON CONFLICT (nome) DO NOTHING;
