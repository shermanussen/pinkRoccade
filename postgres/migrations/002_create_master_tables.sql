CREATE TABLE IF NOT EXISTS production.master_gemeenten (
    id SERIAL PRIMARY KEY,
    id_master int NOT NULL,
    gemeentecode VARCHAR NOT NULL,
    jaar int NOT NULL,
    UNIQUE(gemeentecode, jaar)
);

CREATE TABLE IF NOT EXISTS production.master_wijken (
    id SERIAL PRIMARY KEY,
    id_master int NOT NULL,
    wijkcode VARCHAR NOT NULL,
    jaar int NOT NULL,
    UNIQUE(wijkcode, jaar)
);

CREATE TABLE IF NOT EXISTS production.master_buurten (
    id SERIAL PRIMARY KEY,
    id_master int NOT NULL,
    buurtcode VARCHAR NOT NULL,
    jaar int NOT NULL,
    UNIQUE(buurtcode, jaar)
);