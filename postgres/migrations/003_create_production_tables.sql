CREATE TABLE IF NOT EXISTS production.gemeenten (
    id SERIAL PRIMARY KEY,
    id_master int NULL,
    gemeentecode varchar NOT NULL,
    jaar int NOT NULL,
    UNIQUE (gemeentecode, jaar)
);

CREATE TABLE IF NOT EXISTS production.wijken (
    id SERIAL PRIMARY KEY,
    id_master int NULL,
    wijkcode varchar NOT NULL,
    jaar int NOT NULL,
    UNIQUE (wijkcode, jaar)
);

CREATE TABLE IF NOT EXISTS production.buurten (
    id SERIAL PRIMARY KEY,
    id_master int NULL,
    buurtcode varchar NOT NULL,
    jaar int NOT NULL,
    UNIQUE (buurtcode, jaar)
);