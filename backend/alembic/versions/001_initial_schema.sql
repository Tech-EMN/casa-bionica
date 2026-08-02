-- Casa Biônica — Database Schema (Postgres)
-- Executar no SQL Editor do Supabase ou via Management API
-- Data: 02/Ago/2026

-- ── Crossing Events ────────────────────────────────────
CREATE TABLE IF NOT EXISTS crossing_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sensor_id VARCHAR(64) NOT NULL,
    home_id VARCHAR(64) NOT NULL,
    direction VARCHAR(16) NOT NULL CHECK (direction IN ('entry', 'exit')),
    distance_mm INTEGER NOT NULL CHECK (distance_mm >= 0 AND distance_mm <= 4000),
    event_timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_events_sensor
    ON crossing_events (sensor_id);
CREATE INDEX IF NOT EXISTS idx_events_home
    ON crossing_events (home_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp
    ON crossing_events (event_timestamp);
CREATE UNIQUE INDEX IF NOT EXISTS idx_events_dedup
    ON crossing_events (sensor_id, event_timestamp);

-- ── Baselines ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS baselines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sensor_id VARCHAR(64) NOT NULL,
    home_id VARCHAR(64) NOT NULL,
    hour_bucket INTEGER NOT NULL CHECK (hour_bucket >= 0 AND hour_bucket <= 23),
    ewma_mean_seconds DOUBLE PRECISION NOT NULL,
    ewma_std_seconds DOUBLE PRECISION NOT NULL,
    sample_count INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_baselines_sensor_home
    ON baselines (sensor_id, home_id);

COMMENT ON TABLE baselines IS 'EWMA baseline: one row per sensor + hour bucket';

-- ── Alerts ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    home_id VARCHAR(64) NOT NULL,
    sensor_id VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'notified', 'acknowledged', 'resolved')),
    current_duration_seconds DOUBLE PRECISION NOT NULL,
    threshold_seconds DOUBLE PRECISION NOT NULL,
    baseline_mean_seconds DOUBLE PRECISION NOT NULL,
    message TEXT,
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_alerts_home
    ON alerts (home_id);
CREATE INDEX IF NOT EXISTS idx_alerts_sensor
    ON alerts (sensor_id);
CREATE INDEX IF NOT EXISTS idx_alerts_triggered
    ON alerts (triggered_at);

-- ── Row Level Security (optional, para Supabase) ──────
ALTER TABLE crossing_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE baselines ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
