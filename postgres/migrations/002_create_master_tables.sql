CREATE TABLE IF NOT EXISTS production.master_gemeenten (
    id SERIAL PRIMARY KEY,
    id_master int(11) NOT NULL,
    gemeentecode VARCHAR(4) NOT NULL,
    jaar int(4) NOT NULL,
    UNIQUE(gemeentecode, jaar)
);

CREATE TABLE IF NOT EXISTS production.master_wijken (
    id SERIAL PRIMARY KEY,
    id_master int(11) NOT NULL,
    wijkcode VARCHAR(6) NOT NULL,
    gemeentecode VARCHAR(4) NOT NULL,
    jaar int(4) NOT NULL,
    UNIQUE(wijkcode, jaar)
);

CREATE TABLE IF NOT EXISTS production.master_buurten (
    id SERIAL PRIMARY KEY,
    id_master int(11) NOT NULL,
    buurtcode VARCHAR(8) NOT NULL,
    wijkcode VARCHAR(6) NOT NULL,
    gemeentecode VARCHAR(4) NOT NULL,
    jaar int(4) NOT NULL,
    UNIQUE(buurtcode, jaar)
);

