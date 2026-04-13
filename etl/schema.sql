-- PitWall Intelligence — PostgreSQL schema (3NF)
-- Auto-executed on first postgres container start via docker-entrypoint-initdb.d

-- ── Extensions ───────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Drop order (reverse FK dependency) ──────────────────────────────────────
DROP TABLE IF EXISTS bvi_scores       CASCADE;
DROP TABLE IF EXISTS pit_stops        CASCADE;
DROP TABLE IF EXISTS qualifying       CASCADE;
DROP TABLE IF EXISTS results          CASCADE;
DROP TABLE IF EXISTS drivers          CASCADE;
DROP TABLE IF EXISTS constructors     CASCADE;
DROP TABLE IF EXISTS circuits         CASCADE;
DROP TABLE IF EXISTS races            CASCADE;

-- ── circuits ─────────────────────────────────────────────────────────────────
CREATE TABLE circuits (
    circuit_id      INTEGER PRIMARY KEY,
    circuit_ref     VARCHAR(50)  NOT NULL,
    name            VARCHAR(100) NOT NULL,
    location        VARCHAR(100),
    country         VARCHAR(100),
    lat             DOUBLE PRECISION,
    lng             DOUBLE PRECISION,
    alt             INTEGER,
    url             TEXT
);

-- ── races ────────────────────────────────────────────────────────────────────
CREATE TABLE races (
    race_id         INTEGER PRIMARY KEY,
    season          INTEGER      NOT NULL,
    round           INTEGER      NOT NULL,
    circuit_id      INTEGER      REFERENCES circuits(circuit_id),
    name            VARCHAR(100) NOT NULL,
    date            DATE,
    time            TIME,
    url             TEXT
);

-- ── constructors ─────────────────────────────────────────────────────────────
CREATE TABLE constructors (
    constructor_id  INTEGER PRIMARY KEY,
    constructor_ref VARCHAR(50)  NOT NULL,
    name            VARCHAR(100) NOT NULL,
    nationality     VARCHAR(50),
    url             TEXT
);

-- ── drivers ──────────────────────────────────────────────────────────────────
CREATE TABLE drivers (
    driver_id       INTEGER PRIMARY KEY,
    driver_ref      VARCHAR(50)  NOT NULL,
    number          VARCHAR(5),
    code            VARCHAR(3),
    forename        VARCHAR(50)  NOT NULL,
    surname         VARCHAR(50)  NOT NULL,
    dob             DATE,
    nationality     VARCHAR(50),
    url             TEXT
);

-- ── results ──────────────────────────────────────────────────────────────────
CREATE TABLE results (
    result_id       INTEGER PRIMARY KEY,
    race_id         INTEGER      NOT NULL REFERENCES races(race_id),
    driver_id       INTEGER      NOT NULL REFERENCES drivers(driver_id),
    constructor_id  INTEGER      NOT NULL REFERENCES constructors(constructor_id),
    number          VARCHAR(5),
    grid            INTEGER,
    position        INTEGER,
    position_text   VARCHAR(5),
    position_order  INTEGER,
    points          NUMERIC(5,2),
    laps            INTEGER,
    time            VARCHAR(20),
    milliseconds    BIGINT,
    fastest_lap     INTEGER,
    rank            INTEGER,
    fastest_lap_time VARCHAR(20),
    fastest_lap_speed VARCHAR(20),
    status_id       INTEGER
);

CREATE INDEX idx_results_race     ON results(race_id);
CREATE INDEX idx_results_driver   ON results(driver_id);
CREATE INDEX idx_results_constructor ON results(constructor_id);

-- ── qualifying ───────────────────────────────────────────────────────────────
CREATE TABLE qualifying (
    qualify_id      INTEGER PRIMARY KEY,
    race_id         INTEGER      NOT NULL REFERENCES races(race_id),
    driver_id       INTEGER      NOT NULL REFERENCES drivers(driver_id),
    constructor_id  INTEGER      NOT NULL REFERENCES constructors(constructor_id),
    number          INTEGER,
    position        INTEGER,
    q1              VARCHAR(20),
    q2              VARCHAR(20),
    q3              VARCHAR(20)
);

CREATE INDEX idx_qualifying_race   ON qualifying(race_id);
CREATE INDEX idx_qualifying_driver ON qualifying(driver_id);

-- ── pit_stops ────────────────────────────────────────────────────────────────
CREATE TABLE pit_stops (
    stop_id         SERIAL PRIMARY KEY,
    race_id         INTEGER      NOT NULL REFERENCES races(race_id),
    driver_id       INTEGER      NOT NULL REFERENCES drivers(driver_id),
    stop            INTEGER      NOT NULL,
    lap             INTEGER,
    time            TIME,
    duration        VARCHAR(20),
    milliseconds    INTEGER
);

CREATE INDEX idx_pitstops_race   ON pit_stops(race_id);
CREATE INDEX idx_pitstops_driver ON pit_stops(driver_id);

-- ── bvi_scores ───────────────────────────────────────────────────────────────
CREATE TABLE bvi_scores (
    score_id        SERIAL PRIMARY KEY,
    constructor_id  INTEGER      NOT NULL REFERENCES constructors(constructor_id),
    season          INTEGER      NOT NULL,
    -- Raw stats
    total_points    NUMERIC(8,2),
    wins            INTEGER,
    podiums         INTEGER,
    entries         INTEGER,
    dnf_rate        NUMERIC(5,4),
    pts_finish_rate NUMERIC(5,4),
    -- BVI dimension scores (0–100)
    perf_score      NUMERIC(6,2),
    cons_score      NUMERIC(6,2),
    expo_score      NUMERIC(6,2),
    -- Composite
    bvi             NUMERIC(6,2),
    tier            INTEGER CHECK (tier IN (1, 2, 3)),
    computed_at     TIMESTAMPTZ  DEFAULT NOW(),
    UNIQUE (constructor_id, season)
);

CREATE INDEX idx_bvi_season ON bvi_scores(season);
CREATE INDEX idx_bvi_constructor ON bvi_scores(constructor_id);
