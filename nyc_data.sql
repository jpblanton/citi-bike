DROP EXTENSION IF EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS timescaledb;
DROP TABLE IF EXISTS "status";

CREATE TABLE "status"(
    time TIMESTAMPTZ NOT NULL,
    station_id INTEGER NOT NULL,
    station_status TEXT NOT NULL,
    bikes_available NUMERIC,
    ebikes_available NUMERIC,
    bikes_disabled NUMERIC,
    docks_available NUMERIC,
    docks_disabled NUMERIC
);
SELECT create_hypertable('status', 'time');
CREATE INDEX ON status (station_id, time desc);
CREATE INDEX ON status (station_status, time desc);

CREATE TABLE IF NOT EXISTS "location"(
    station_id INTEGER NOT NULL,
    neighborhood TEXT,
    longitude NUMERIC,
    latitude NUMERIC
);

CREATE TABLE IF NOT EXISTS "boroughs"(
    neighborhood TEXT NOT NULL,
    borough TEXT
);

CREATE TABLE IF NOT EXISTS "names"(
    station_id INTEGER NOT NULL,
    station_name TEXT,
    station_cap NUMERIC
);
