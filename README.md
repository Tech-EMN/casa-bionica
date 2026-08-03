# Casa Biônica — PRJ-033

> Sistema de monitoramento de idosos por sensores ToF VL53L0X + ESP32-C3.
> Walking Skeleton funcional — backend online, schema v2 ativo.

## 🚀 Quick Start

```bash
# Backend (Python 3.12 + FastAPI + PostgREST)
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload
# → http://localhost:8000/docs

# Firmware (ESP32-C3)
# Abrir firmware/sensor/sensor.ino no Arduino IDE
# Substituir WIFI_SSID, WIFI_PASS, SENSOR_ID
# Upload → eventos aparecem em GET /events
```

## 📡 Endpoints

| Método | Path | Descrição |
|--------|------|-----------|
| `POST` | `/ingest` | Evento de travessia (ESP32 → backend) |
| `GET` | `/events` | Query eventos com filtros |
| `GET` | `/status/{home_id}` | Dashboard completo |
| `GET` | `/presence/{home_id}` | Em casa / Ausente |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | OpenAPI (Swagger UI) |

**Produção:** `https://backend-production-607f.up.railway.app`

## 🏗️ Arquitetura

```
ESP32-C3 (4×) ──HTTP POST──→ Railway (FastAPI) ──HTTPS──→ Supabase PostgREST
```

- **Stack:** Python 3.12 + FastAPI + httpx + Supabase REST API
- **Infra:** Railway (auto-deploy GitHub master) + Supabase (sa-east-1)
- **Schema:** 9 tabelas (homes, users, passages, devices, events, alerts, emergency_contacts, escalation_log, user_homes)

## 📂 Documentos

| Documento | Conteúdo |
|-----------|----------|
| [`CANON.md`](CANON.md) | Registro de integração — tokens, URLs, endpoints |
| [`PLANNING-TREE.md`](PLANNING-TREE.md) | Pipeline E01-E20 + maturity ladder |
| [`arquitetura/AX-DECISION.md`](arquitetura/AX-DECISION.md) | Stack decision (AX scoring) |
| [`arquitetura/STACK-DECISION.md`](arquitetura/STACK-DECISION.md) | Análise comparativa de stacks |
| [`arquitetura/REFERENCIAS-projetos.md`](arquitetura/REFERENCIAS-projetos.md) | 4 projetos referência analisados |
| [`arquitetura/IMPLEMENTATION-SEED.md`](arquitetura/IMPLEMENTATION-SEED.md) | ⚠️ Desatualizado — ver abaixo |
| [`formularios/`](formularios/) | F2, F3, F4 extraídos da PARTE V do workbook |
| [`backend/alembic/versions/002_full_schema.sql`](backend/alembic/versions/002_full_schema.sql) | Schema SQL completo |

> ⚠️ `IMPLEMENTATION-SEED.md` descreve a arquitetura ORIGINAL (asyncpg + SQLAlchemy). A arquitetura REAL é PostgREST (ver `backend/app/database.py`). O ADR da migração está pendente.

## 🔧 Firmware

- [`firmware/sensor/sensor.ino`](firmware/sensor/sensor.ino) — 226 linhas, state machine IDLE→ZONE_A→ZONE_B
- Exemplo C++ simplificado (70 linhas): enviado no Telegram (msg #26504)

## 🗄️ Schema (Supabase)

```
homes → passages → devices → events
homes → emergency_contacts
homes → alerts → escalation_log
users → user_homes ← homes
```

9 tabelas, Supabase project `rkiclxviqinciwwumwfb` (sa-east-1).

## 📋 Decisões de Arquitetura

| ADR | Decisão | Status |
|-----|---------|:---:|
| ADR-001 | Python + FastAPI (AX 7.7) | ✅ Documentado em AX-DECISION.md |
| ADR-002 | HTTP POST direto (ESP32→Backend) | ⬜ Pendente |
| ADR-003 | PostgREST em vez de SQLAlchemy direto | ⬜ Pendente |
| ADR-004 | Schema v2 (9 tabelas, 10 business rules) | ⬜ Pendente |

## 🏷️ Version

`v2.1.0` — PostgREST backend, schema v2, Railway production
