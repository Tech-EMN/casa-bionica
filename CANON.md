# CASA BIÔNICA — CANON (PRJ-033)

> **Fonte canônica de integração.** Valores aqui prevalecem sobre qualquer outro documento.
> **Atualizado:** 02/Ago/2026 — Daedalus (AG01)
> **⚠️ SEGREDOS:** Chaves e senhas NÃO estão neste arquivo. Consultar `_canon/integrations/atria/canon.json` ou Railway env vars.

---

## GitHub

| Campo | Valor |
|-------|-------|
| **Repo** | `Tech-EMN/casa-bionica` |
| **URL** | https://github.com/Tech-EMN/casa-bionica |
| **Branch deploy** | `master` |
| **CI/CD** | Railway auto-deploy on push |

---

## Supabase

| Campo | Valor |
|-------|-------|
| **Project Ref** | `rkiclxviqinciwwumwfb` |
| **URL** | https://rkiclxviqinciwwumwfb.supabase.co |
| **Region** | sa-east-1 (São Paulo) |
| **Publishable Key** | `sb_publishable_YodIBQnViXePbBlLFiSqxA_***` |
| **Secret Key** | `sb_secret_***` (ver `_canon/integrations/atria/canon.json`) |
| **DB Password** | `***` (ver Railway env var `DATABASE_URL`) |

### Connection String (formato)

```
# PostgreSQL padrão
postgresql://postgres:<DB_PASSWORD>@db.rkiclxviqinciwwumwfb.supabase.co:5432/postgres

# Python async (SQLAlchemy)
postgresql+asyncpg://postgres:<DB_PASSWORD>@db.rkiclxviqinciwwumwfb.supabase.co:5432/postgres

# Pooler (mesma região sa-east-1 — melhor latência no Railway)
postgresql+asyncpg://postgres:<DB_PASSWORD>@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

### Tabelas

| Tabela | Status | Índices |
|--------|:---:|---------|
| `crossing_events` | ✅ | sensor_id, home_id, event_timestamp, UNIQUE(sensor_id, timestamp) |
| `baselines` | ✅ | sensor_id+home_id |
| `alerts` | ✅ | home_id, sensor_id, triggered_at |

---

## Railway

| Campo | Valor |
|-------|-------|
| **Project ID** | `df9dee3e-d7a8-4c06-badc-1c96f5f834a7` |
| **Service ID** | `f362ac5b-e443-41f8-89e1-f86b21b4c453` |
| **Dashboard** | https://railway.app/project/df9dee3e-d7a8-4c06-badc-1c96f5f834a7 |

### Env Vars (Railway)

| Variável | Status |
|----------|:---:|
| `PORT` = `8000` | ✅ |
| `APP_ENV` = `production` | ✅ |
| `LOG_LEVEL` = `INFO` | ✅ |
| `HOME_ID` = `home-001` | ✅ |
| `DATABASE_URL` | ⬜ Pendente — **adicionar AGORA** |
| `MQTT_BROKER_HOST` | ⬜ Pendente (futuro) |

---

## Firmware (ESP32-C3)

| Campo | Valor |
|-------|-------|
| **Microcontrolador** | ESP32-C3 (4 unidades) |
| **Sensor** | 2× VL53L0X por módulo (I2C: 0x30 + 0x31) |
| **Protocolo** | HTTP POST direto (Walking Skeleton) |
| **API URL** | ⬜ Aguardando URL do Railway |
| **Endpoint** | `POST /ingest` |

---

## Endpoints (Backend)

| Método | Path | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Health check |
| `GET` | `/` | App info + docs link |
| `GET` | `/docs` | OpenAPI (Swagger UI) |
| `POST` | `/ingest` | Evento de travessia |
| `GET` | `/events` | Query eventos |
| `GET` | `/events/last` | Último evento |
| `GET` | `/baseline` | Baseline EWMA |
| `GET` | `/alerts` | Alertas ativos |
| `GET` | `/status/{home_id}` | Status agregado |
