# DOC2 — Semente de Implementação + Design de Módulos

> **Público:** Agente Construtor (Daedalus AG01 + sub-agentes)
> **Objetivo:** Sair do zero ao primeiro deploy funcional sem reabrir decisões arquiteturais
> **Skills base:** AX-stack-choosing + improve-codebase-architecture
> **Data:** 02/Ago/2026

---

## PARTE A — Decisões Arquiteturais Travadas

> ⚠️ **Regra:** Estas decisões são o ponto de partida. O agente construtor as assume. Só reabra se encontrar evidência concreta de que uma delas é inviável.

### A1. Backend Runtime & Framework
- **Decisão:** Python 3.12 + FastAPI 0.115+
- **Rejeitado:** Node.js/Express (P6 8 vs 9; EWMA 40 linhas vs 4); Go (AX 6.3 < 7)
- **Justificativa AX:** P1.1=9 (OpenAPI nativo), P3.1=9 (CLI total), P6=9 (modelo familiarizado)

### A2. Banco de Dados
- **Walking Skeleton:** SQLite (arquivo único, zero-config)
- **PoC/MVP:** PostgreSQL 16 + TimescaleDB (migração: trocar connection string SQLAlchemy)
- **Rejeitado:** MongoDB (P4.3 < 4, sem ACID); InfluxDB (SQL-like, mas ecossistema menor)
- **Justificativa AX:** P4.3=8 (ACID + migrations up/down + PITR no Postgres)

### A3. ORM / Data Layer
- **Decisão:** SQLAlchemy 2.0 (async) + Alembic (migrations)
- **Rejeitado:** Prisma (Node.js apenas); Django ORM (pesado para 200 eventos/dia)
- **Justificativa:** Abstrai SQLite→Postgres com troca de connection string. Zero rewrite.

### A4. MQTT Broker
- **Decisão:** Mosquitto 2.x (Docker, Railway)
- **Rejeitado:** EMQX (overkill); RabbitMQ (complexidade desnecessária para pub/sub simples)
- **Justificativa:** Commodity. 20MB RAM. Setup em 5 minutos.

### A5. Protocolo Sensor→Gateway
- **Decisão:** BLE advertisement (payload binário mínimo)
- **Fallback:** ESP-NOW se BLE tiver latência >500ms ou range <10m
- **Rejeitado:** WiFi no sensor (consome bateria); Zigbee (precisa de coordinator); LoRa (overkill indoor)

### A6. Hospedagem / Deploy
- **Decisão:** Railway (git push → deploy)
- **Rejeitado:** AWS (complexidade inicial); Fly.io (bom, mas ATRIA já usa Railway)
- **Justificativa AX:** P3.1=9 (railway up via CLI, zero dashboard)

### A7. Dashboard
- **Walking Skeleton:** Template Jinja2 servido pelo FastAPI (1 arquivo HTML)
- **MVP:** React/Vue estático no Netlify (consome API `/openapi.json`)
- **Rejeitado:** Dashboard no ESP32 (4MB flash, perde dados no reboot)

### A8. CI/CD
- **Walking Skeleton:** `git push` → Railway auto-deploy (basta)
- **MVP:** GitHub Actions (testes + deploy staging → produção)

### A9. Observabilidade
- **Decisão:** `structlog` (logs JSON) + `trace_id` por request
- **MVP:** Langfuse ou Helicone (budget tracking + tracing)

---

## PARTE B — Design de Módulos (improve-codebase-architecture)

> *"Depth = high leverage behind a small interface."*  
> *"The interface is the test surface."*  
> *"One adapter = hypothetical seam. Two adapters = real seam."*

### Arquitetura em 3 Camadas com Módulos

```
┌─────────────────────────────────────────────────────────┐
│ CAMADA 1 — SENSOR (ESP32-C3, C++ Arduino)               │
│                                                         │
│ ┌─────────────────────────────────────────────────┐    │
│ │ MÓDULO: CrossingDetector                         │    │
│ │ INTERFACE: detect() → CrossingEvent | None       │    │
│ │ DEPTH: State machine IDLE→ZONE_A→ZONE_B, timeout │    │
│ │        2 VL53L0X readings, direction inference   │    │
│ │ LEVERAGE: 1 call, ~200 lines of behavior behind  │    │
│ │ SEAM: CrossingDetector interface                  │    │
│ │ ADAPTER: VL53L0X dual-sensor (today)              │    │
│ │         mmWave sensor (future, same interface)    │    │
│ └─────────────────────────────────────────────────┘    │
│ ┌─────────────────────────────────────────────────┐    │
│ │ MÓDULO: BLEBroadcaster                           │    │
│ │ INTERFACE: broadcast(event: CrossingEvent) → OK  │    │
│ │ DEPTH: BLE advertisement packing, power mgmt     │    │
│ │ SEAM: Broadcaster interface                       │    │
│ │ ADAPTER: BLE (today), ESP-NOW (fallback)          │    │
│ └─────────────────────────────────────────────────┘    │
│ ┌─────────────────────────────────────────────────┐    │
│ │ MÓDULO: PowerManager                              │    │
│ │ INTERFACE: sleep() / wake() → OK                  │    │
│ │ DEPTH: Deep sleep cycles, PIR wake-up, battery    │    │
│ │ LEVERAGE: 2 calls control anos de bateria         │    │
│ └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │ BLE
┌─────────────────────────────────────────────────────────┐
│ CAMADA 2 — GATEWAY (ESP32-C3, C++ Arduino)              │
│                                                         │
│ ┌─────────────────────────────────────────────────┐    │
│ │ MÓDULO: BLEAggregator                            │    │
│ │ INTERFACE: on_event(event: CrossingEvent) → OK   │    │
│ │ DEPTH: BLE scan, dedup, buffer 24h, backfill     │    │
│ └─────────────────────────────────────────────────┘    │
│ ┌─────────────────────────────────────────────────┐    │
│ │ MÓDULO: MQTTPublisher                            │    │
│ │ INTERFACE: publish(topic, payload) → OK          │    │
│ │ DEPTH: WiFi reconnect, QoS 1, retained messages  │    │
│ │ SEAM: Publisher interface                         │    │
│ │ ADAPTER: MQTT (today), HTTP/2 (future)            │    │
│ └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │ MQTT
┌─────────────────────────────────────────────────────────┐
│ CAMADA 3 — CLOUD (Python + FastAPI, Railway)            │
│                                                         │
│ ┌─────────────────────────────────────────────────┐    │
│ │ MÓDULO: IngestService ★ DEEP                      │    │
│ │ INTERFACE: ingest(raw_event: dict) → EventID      │    │
│ │ DEPTH:                                            │    │
│ │   - Validate schema (Pydantic)                    │    │
│ │   - Normalize timestamp (UTC)                     │    │
│ │   - Dedup (idempotency: sensor_id+timestamp)      │    │
│ │   - Store in DB (SQLAlchemy async)                │    │
│ │   - Queue for baseline update (background task)   │    │
│ │ LEVERAGE: 1 POST endpoint, 5 behaviors behind     │    │
│ │ SEAM: EventStore interface (SQLite→Postgres)      │    │
│ │ TEST: Post event, read back, verify stored        │    │
│ └─────────────────────────────────────────────────┘    │
│ ┌─────────────────────────────────────────────────┐    │
│ │ MÓDULO: EWMABaselineEngine ★ DEEP                 │    │
│ │ INTERFACE: calculate(sensor_id, window_hours)     │    │
│ │           → Baseline(mean, std, threshold)        │    │
│ │ DEPTH:                                            │    │
│ │   - Query events window                           │    │
│ │   - EWMA: df['duration'].ewm(alpha=0.2).mean()    │    │
│ │   - Compute 2σ threshold                          │    │
│ │   - Update baseline row (upsert)                  │    │
│ │ LEVERAGE: 4 lines of NumPy, weeks of math behind  │    │
│ │ SEAM: BaselineCalculator interface                 │    │
│ │ ADAPTER: EWMA (today), LSTM/Transformer (future)  │    │
│ │ TEST: Feed known data, verify baseline matches    │    │
│ └─────────────────────────────────────────────────┘    │
│ ┌─────────────────────────────────────────────────┐    │
│ │ MÓDULO: AnomalyDetector ★ DEEP                    │    │
│ │ INTERFACE: check(sensor_id, current_duration)     │    │
│ │           → Alert | None                          │    │
│ │ DEPTH:                                            │    │
│ │   - Load baseline for sensor                      │    │
│ │   - Compare current > threshold?                  │    │
│ │   - Check cooldown (30min per sensor)             │    │
│ │   - Create alert record                           │    │
│ │   - Trigger notification pipeline                 │    │
│ │ LEVERAGE: 1 function call, critical safety logic  │    │
│ │ TEST: Inject anomaly, verify alert created        │    │
│ └─────────────────────────────────────────────────┘    │
│ ┌─────────────────────────────────────────────────┐    │
│ │ MÓDULO: Notifier ★ SHALLOW (many adapters)        │    │
│ │ INTERFACE: notify(alert: Alert, targets: list)    │    │
│ │ SEAM: NotificationChannel interface               │    │
│ │ ADAPTERS: ConsoleLog (WS), Email (PoC),           │    │
│ │          WhatsApp/Twilio (MVP), Push (MVP)        │    │
│ │ WHY SHALLOW: Interface = implementation. Each     │    │
│ │ adapter is simple; complexity is in routing,      │    │
│ │ not in the channel itself                         │    │
│ └─────────────────────────────────────────────────┘    │
│ ┌─────────────────────────────────────────────────┐    │
│ │ MÓDULO: DashboardAPI ★ MIXED DEPTH                │    │
│ │ INTERFACE: GET /api/status/{home_id}              │    │
│ │           GET /api/timeline/{home_id}?hours=24    │    │
│ │           GET /api/alerts/{home_id}?active=true   │    │
│ │ DEPTH: Queries são shallow (CRUD), mas GET/status │    │
│ │        é deep (agrega último evento + baseline +  │    │
│ │        alertas ativos em 1 chamada)               │    │
│ │ SEAM: ReadModel interface (SQLite→Postgres)       │    │
│ └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Teste de Deleção (improve-codebase-architecture)

| Módulo | Se deletado... | Veredito |
|--------|---------------|----------|
| **IngestService** | Complexidade reaparece em cada endpoint que recebe dados externos | ✅ Deep — ganha seu lugar |
| **EWMABaselineEngine** | Cálculo de baseline espalhado entre AnomalyDetector e Dashboard | ✅ Deep — concentra conhecimento matemático |
| **AnomalyDetector** | Lógica de threshold + cooldown replicada em cada chamada de Dashboard | ✅ Deep — concentra lógica de segurança |
| **Notifier** | Cada adapter vira código duplicado no AnomalyDetector | ⚠️ Shallow mas necessário — seam real com 2+ adapters |
| **DashboardAPI** | Cada cliente (web, mobile) implementa suas próprias queries | ⚠️ Mixed — GET /status é deep, queries CRUD são shallow |

---

## PARTE C — Scaffolding Inicial

```
casa-bionica/
├── firmware/
│   ├── sensor/
│   │   ├── sensor.ino              # ESP32-C3 firmware (4×)
│   │   ├── crossing_detector.h     # Módulo CrossingDetector
│   │   ├── crossing_detector.cpp   # State machine + VL53L0X
│   │   ├── ble_broadcaster.h       # Módulo BLEBroadcaster
│   │   ├── ble_broadcaster.cpp
│   │   ├── power_manager.h         # Módulo PowerManager
│   │   └── power_manager.cpp
│   └── gateway/
│       ├── gateway.ino             # ESP32-C3 firmware
│       ├── ble_aggregator.h        # Módulo BLEAggregator
│       ├── ble_aggregator.cpp
│       ├── mqtt_publisher.h        # Módulo MQTTPublisher
│       └── mqtt_publisher.cpp
│
├── backend/
│   ├── .env.example                # DATABASE_URL, MQTT_BROKER, etc.
│   ├── requirements.txt            # fastapi, sqlalchemy, pydantic, etc.
│   ├── docker-compose.yml          # mosquitto + fastapi (opcional)
│   ├── alembic.ini                 # Migrations config
│   ├── alembic/
│   │   └── versions/               # Migration files
│   ├── app/
│   │   ├── main.py                 # FastAPI app + lifespan
│   │   ├── config.py               # Settings from env vars (pydantic-settings)
│   │   ├── database.py             # SQLAlchemy async engine + session
│   │   ├── models/
│   │   │   ├── event.py            # CrossingEvent ORM model
│   │   │   ├── baseline.py         # Baseline ORM model
│   │   │   └── alert.py            # Alert ORM model
│   │   ├── schemas/
│   │   │   ├── event.py            # Pydantic schemas (request/response)
│   │   │   ├── baseline.py
│   │   │   └── alert.py
│   │   ├── routers/
│   │   │   ├── ingest.py           # POST /ingest (MQTT subscriber)
│   │   │   ├── events.py           # GET /events
│   │   │   ├── baseline.py         # GET /baseline
│   │   │   ├── alerts.py           # GET /alerts
│   │   │   └── status.py           # GET /status/{home_id}
│   │   ├── services/
│   │   │   ├── ingest_service.py   # Módulo IngestService (DEEP)
│   │   │   ├── ewma_engine.py      # Módulo EWMABaselineEngine (DEEP)
│   │   │   ├── anomaly_detector.py # Módulo AnomalyDetector (DEEP)
│   │   │   └── notifier.py         # Módulo Notifier (shallow, many adapters)
│   │   ├── mqtt/
│   │   │   └── subscriber.py       # MQTT client (aiomqtt)
│   │   └── middleware/
│   │       ├── trace_id.py         # Inject trace_id em cada request
│   │       └── error_handler.py    # RFC 9457 error formatting
│   └── tests/
│       ├── test_ingest.py
│       ├── test_ewma.py
│       ├── test_anomaly.py
│       └── conftest.py             # Fixtures: test DB, test client
│
├── dashboard/
│   └── index.html                  # Jinja2 template (WS) / React (MVP)
│
├── docs/
│   ├── ADR-001-stack-backend.md    # Esta decisão
│   ├── ADR-002-protocolo-sensor.md # BLE vs ESP-NOW
│   ├── ADR-003-banco-dados.md      # SQLite → Postgres migration path
│   └── api/
│       └── openapi.json            # Gerado do FastAPI (auto)
│
├── .github/
│   └── workflows/
│       └── deploy.yml              # Railway deploy (MVP)
│
├── README.md                       # Agent-oriented: install → config → deploy
└── CONTEXT.md                      # Domain glossary (improve-codebase-architecture)
```

---

## PARTE D — Comandos de Setup (Walking Skeleton)

```bash
# 1. Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy aiosqlite alembic pydantic-settings structlog aiomqtt
cp .env.example .env  # Edit DATABASE_URL=sqlite+aiosqlite:///casa_bionica.db
alembic upgrade head
uvicorn app.main:app --reload  # http://localhost:8000/docs → OpenAPI

# 2. MQTT Broker (Docker)
docker run -d --name mosquitto -p 1883:1883 eclipse-mosquitto

# 3. Firmware (Arduino IDE)
# Abrir firmware/sensor/sensor.ino → compilar → upload para ESP32-C3
# Abrir firmware/gateway/gateway.ino → compilar → upload para ESP32-C3

# 4. Deploy (Railway)
railway up  # ou git push (auto-deploy configurado)
```

---

## PARTE E — CONTEXT.md (Domain Glossary)

```markdown
# CONTEXT.md — Casa Biônica

## Domain Terms

- **Crossing Event:** Um corpo cruzou uma passagem. Atributos: sensor_id, timestamp_utc, direction (entry|exit), distance_mm.
- **Passagem:** Limite entre dois ambientes (ex: quarto→corredor). 1 passagem = 2 sensores VL53L0X.
- **Baseline:** Perfil de ocupação normal de um ambiente. Calculado via EWMA sobre 7 dias.
- **EWMA:** Exponentially Weighted Moving Average. alpha=0.2. Atualizado a cada novo evento.
- **Anomaly:** Duração atual no ambiente > baseline.mean + 2×baseline.std.
- **Alert:** Notificação de anomalia. Estado: pending → notified → acknowledged → resolved.
- **Long Lie:** Idoso caído e incapaz de se levantar por horas/dias. Evento-alvo do sistema.
- **Home:** Unidade de monitoramento (1 residência = 1 idoso no Walking Skeleton).

## Architecture Terms (improve-codebase-architecture)

- **Module:** Qualquer coisa com interface + implementação.
- **Interface:** Tudo que o caller precisa saber: tipos, invariantes, modos de erro, ordenação.
- **Depth:** Comportamento complexo atrás de interface simples. Muito leverage.
- **Seam:** Onde a interface vive. Comportamento pode ser alterado sem editar in-place.
- **Adapter:** Implementação concreta de uma interface num seam.
```

---

## PARTE F — Checklist de Estudo Prévio (ordenado)

1. ⬜ [VL53L0X API docs](https://www.st.com/resource/en/datasheet/vl53l0x.pdf) — Seções: I2C protocol, ranging modes, timing budget
2. ⬜ [RooDe peopleCounter32.yaml](https://github.com/Lyr3x/Roode/blob/master/peopleCounter32.yaml) — Configuração de referência: sampling, ROI, zones, thresholds
3. ⬜ [FastAPI SQLAlchemy async](https://fastapi.tiangolo.com/how-to/async-sql-encode-databases/) — Padrão para `async def` + `AsyncSession`
4. ⬜ [SQLAlchemy 2.0 ORM](https://docs.sqlalchemy.org/en/20/orm/quickstart.html) — Declarative base, async engine
5. ⬜ [aiomqtt](https://github.com/sbtinstruments/aiomqtt) — MQTT client async para Python
6. ⬜ [ESP32 Deep Sleep + BLE](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/sleep_modes.html) — Power management para sensor
7. ⬜ [ST People Counting Algorithm](https://www.st.com/resource/en/application_note/an5677-vl53l1x-people-counting-algorithm-stmicroelectronics.pdf) — Algoritmo oficial da fabricante

---

## PARTE G — Sequência de Implementação (3 dias, Opção C)

```
DIA 1 (HOJE) — Firmware + Backend em paralelo
├── Daedalus: backend/app/ completo (models, schemas, ingest, database)
├── Eduardo: firmware/sensor/ (VL53L0X lendo Serial)
└── Gate: sensor imprime distâncias? backend aceita POST?

DIA 2 — Integração + Baseline
├── Firmware: state machine de travessia + BLE broadcast
├── Gateway: BLE scan + forward MQTT
├── Backend: MQTT subscriber + EWMA engine + SQLite storage
└── Gate: evento de travessia chega no banco via MQTT?

DIA 3 — Dashboard + Teste End-to-End
├── Dashboard HTML (Jinja2): status, timeline, alertas
├── AnomalyDetector: threshold + cooldown
├── Teste: Eduardo simula rotina, verifica dashboard
└── Gate: sistema funciona 24h sem intervenção?
```

---

*"The interface is the test surface." — improve-codebase-architecture*
*"Agente construtor sai do zero ao primeiro deploy sem reabrir decisões." — AX-stack-choosing doc2 spec*
