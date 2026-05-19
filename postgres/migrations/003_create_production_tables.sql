CREATE TABLE IF NOT EXISTS production.gemeenten (
    id SERIAL PRIMARY KEY,
    id_master int(11) NOT NULL
)

CREATE TABLE IF NOT EXISTS production.wijken (
    id SERIAL PRIMARY KEY,
    id_master int(11) NOT NULL
)

CREATE TABLE IF NOT EXISTS production.buurten (
    id SERIAL PRIMARY KEY,
    id_master int(11) NOT NULL
)