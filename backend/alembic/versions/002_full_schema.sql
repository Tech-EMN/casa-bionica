CREATE TABLE IF NOT EXISTS homes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL,
    address VARCHAR(256),
    elderly_name VARCHAR(128) NOT NULL,
    timezone VARCHAR(64) DEFAULT 'America/Sao_Paulo',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL,
    phone VARCHAR(32),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_homes (
    user_id UUID REFERENCES users(id),
    home_id UUID REFERENCES homes(id),
    role VARCHAR(32) NOT NULL DEFAULT 'caregiver'
        CHECK (role IN ('elderly', 'caregiver', 'admin')),
    PRIMARY KEY (user_id, home_id)
);
CREATE TABLE IF NOT EXISTS passages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    home_id UUID NOT NULL REFERENCES homes(id),
    name VARCHAR(128) NOT NULL,
    passage_type VARCHAR(16) NOT NULL DEFAULT 'room'
        CHECK (passage_type IN ('room', 'entrance')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passage_id UUID REFERENCES passages(id),
    home_id UUID NOT NULL REFERENCES homes(id),
    sensor_id VARCHAR(64) NOT NULL UNIQUE,
    status VARCHAR(32) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'low_battery', 'offline')),
    installed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_devices_home ON devices(home_id);

CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES devices(id),
    direction VARCHAR(16) NOT NULL CHECK (direction IN ('entry', 'exit')),
    distance_mm INTEGER NOT NULL CHECK (distance_mm >= 0 AND distance_mm <= 4000),
    event_timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_events_device_ts ON events(device_id, event_timestamp);
CREATE UNIQUE INDEX IF NOT EXISTS idx_events_dedup ON events(device_id, event_timestamp);
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    home_id UUID NOT NULL REFERENCES homes(id),
    name VARCHAR(128) NOT NULL,
    phone VARCHAR(32) NOT NULL,
    relationship VARCHAR(64),
    priority INTEGER NOT NULL DEFAULT 1 CHECK (priority BETWEEN 1 AND 3),
    escalation_timeout_minutes INTEGER NOT NULL DEFAULT 15,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    home_id UUID NOT NULL REFERENCES homes(id),
    device_id UUID REFERENCES devices(id),
    status VARCHAR(32) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','notified','acknowledged','resolved','escalated_external')),
    current_duration_seconds DOUBLE PRECISION NOT NULL,
    threshold_seconds DOUBLE PRECISION NOT NULL,
    baseline_mean_seconds DOUBLE PRECISION NOT NULL,
    message TEXT,
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_alerts_home ON alerts(home_id);

CREATE TABLE IF NOT EXISTS escalation_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID NOT NULL REFERENCES alerts(id),
    contact_id UUID REFERENCES emergency_contacts(id),
    escalation_level INTEGER NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','notified','acknowledged','failed','escalated')),
    notified_at TIMESTAMPTZ,
    responded_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_esc_alert ON escalation_log(alert_id);
