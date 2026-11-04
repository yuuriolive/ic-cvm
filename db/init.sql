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