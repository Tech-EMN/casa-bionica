# Análise de Stack — Casa Biônica (Walking Skeleton → PoC → MVP)

> **Delegado por:** Eduardo Nunes (02/Ago/2026)
> **Decisor técnico:** Daedalus (AG01)
> **Regra:** Stack deve funcionar da POC até o MVP. Revisão só no Traction-Ready.
> **Fontes:** 7 projetos referência analisados (4 originais + 3 adicionais)

---

## Projetos Referência — Matriz de Stack

| # | Projeto | Firmware Sensor | Protocolo | Gateway | Backend/Cloud | Frontend | Lang |
|---|---------|----------------|-----------|---------|---------------|----------|------|
| 1 | **RooDe** | ESPHome + C++ custom component | MQTT + HA API | ESP32 | Home Assistant | HA Dashboard | C++ / YAML |
| 2 | **Smart Access Monitor** | Arduino C++ | HTTP (WebServer ESP32) | — (direto) | WebServer no ESP32 | Chart.js HTML | C++ / JS |
| 3 | **Reddit Doorway Counter** | Arduino C++ | BLE | ESP32-C6 | — (post Reddit) | — | C++ |
| 4 | **ST Manual (oficial)** | STM32 C driver | — | — | — | — | C |
| 5 | **ESPHome VL53L0X** | ESPHome nativo | MQTT | — | Home Assistant | HA Dashboard | YAML |
| 6 | **Tasmota VL53L0X** | Tasmota (C++) | MQTT | — | Qualquer broker MQTT | Node-RED / Grafana | C++ |
| 7 | **OpenMQTTGateway** | C++ (Arduino) | MQTT | ESP32 | Broker MQTT | Grafana / HA | C++ |

### Padrões convergentes:

1. **Firmware do sensor: 100% C++** — Não há alternativa. Arduino framework ou ESP-IDF. ESPHome é wrapper YAML sobre C++.
2. **Protocolo sensor→gateway: MQTT domina** (5/7 projetos). BLE aparece em 1 (Reddit). HTTP direto em 1 (acadêmico).
3. **Gateway: ESP32 em todos** — Quando existe gateway separado, é sempre ESP32.
4. **Backend cloud: Home Assistant em 4/7** — Projetos DIY convergem para HA. Nenhum usa backend customizado.
5. **NENHUM projeto referência usa:** Node.js, Python, Go, PostgreSQL, ou qualquer stack "web tradicional" no backend.

---

## Arquitetura em 3 Camadas

```
┌─────────────────────────────────────────────────────────┐
│ CAMADA 1 — SENSOR (ESP32-C3)                            │
│ Firmware: C++ (Arduino framework) ← FIXO, não tem escolha│
│ Responsabilidades: ler VL53L0X, state machine, BLE/MQTT │
└─────────────────────────────────────────────────────────┘
                          │
                          │ BLE ou MQTT ou ESP-NOW
                          │
┌─────────────────────────────────────────────────────────┐
│ CAMADA 2 — GATEWAY (ESP32-C3)                           │
│ Firmware: C++ (Arduino framework) ← FIXO                │
│ Responsabilidades: agregar eventos, WiFi, forward cloud │
└─────────────────────────────────────────────────────────┘
                          │
                          │ MQTT ou HTTP/2 ou WebSocket
                          │
┌─────────────────────────────────────────────────────────┐
│ CAMADA 3 — CLOUD (Railway)                              │
│ ← AQUI está a decisão de stack                          │
│ Responsabilidades: ingest, TSDB, baseline EWMA, alertas │
└─────────────────────────────────────────────────────────┘
```

As camadas 1 e 2 são C++ (Arduino) — não há escolha. A decisão real está na **Camada 3**.

---

## Opções para a Camada 3 (Cloud Backend)

### Opção A — Python + FastAPI + SQLite → Postgres

```
Gateway ──MQTT──→ [Mosquitto broker] ──→ FastAPI ──→ SQLite/Postgres
                                              │
                                         EWMA engine
                                              │
                                         Push notification
```

| Prós | Contras |
|------|---------|
| Python = mesma linguagem dos scripts de dados/ML futuros | Single-threaded (mitigado com uvicorn workers) |
| FastAPI é o framework mais rápido para prototipagem | MQTT broker extra para gerenciar (Mosquitto) |
| SQLite → Postgres é migração trivial (1 script SQLAlchemy) | Python não é a stack típica de IoT (mas não importa — os dados já chegaram) |
| ATRIA já usa Python em outros projetos | |
| Ecossistema rico: numpy, scipy, pandas para baseline EWMA | |
| Documentação massiva, ChatGPT-friendly | |

**Estimativa:** 4-6h para Walking Skeleton (1 endpoint de ingest + 1 de leitura)

---

### Opção B — Node.js + Express + SQLite → Postgres (TimescaleDB)

```
Gateway ──MQTT──→ [Mosquitto broker] ──→ Express ──→ SQLite/Postgres+TimescaleDB
                                              │
                                         EWMA engine (JS)
                                              │
                                         Push notification
```

| Prós | Contras |
|------|---------|
| JavaScript full-stack (dashboard + backend mesma lang) | EWMA engine em JS é menos natural que Python |
| Event-driven (natural para IoT) | TimescaleDB é Postgres com extensão — overhead para Walking Skeleton |
| TimescaleDB é o padrão ouro para time-series | MQTT broker extra |
| ATRIA já usa Node.js em outros projetos | Prototipagem mais lenta que FastAPI (mais boilerplate) |

**Estimativa:** 6-8h para Walking Skeleton

---

### Opção C — Go + SQLite

```
Gateway ──MQTT──→ [Mosquitto broker] ──→ Go ──→ SQLite
                                              │
                                         EWMA engine
                                              │
                                         Push notification
```

| Prós | Contras |
|------|---------|
| Performance máxima, binário único | Ninguém na ATRIA programa em Go |
| Concorrência nativa (goroutines = IoT) | Curva de aprendizado adiciona 1-2 semanas |
| Compila para qualquer plataforma | Menos bibliotecas maduras para ML/analytics |
| Consumo mínimo de recursos | Overengineering para 1 idoso, 4 sensores |

**Estimativa:** 2-3 semanas (incluindo aprendizado)

---

### Opção D — Minimalista: ESP32 Gateway como servidor HTTP

```
Gateway ──HTTP──→ Cloud Function (Railway) ──→ SQLite
   │
   └── WebServer no ESP32 (dashboard básico)
```

| Prós | Contras |
|------|---------|
| Zero infraestrutura de backend | Dashboard no ESP32 = 4MB flash limitado |
| Custo zero (Railway free tier) | Sem baseline real (não cabe no ESP32) |
| Setup em 1-2h | Perde todos os dados se ESP32 reiniciar |
| | Inviável para PoC/MVP |

**Estimativa:** 1-2h (mas inútil para os próximos passos)

---

## Recomendação: **Opcão A — Python + FastAPI + SQLite**

### Justificativa (6 fatores):

**1. Velocidade de prototipagem (fator #1 para Walking Skeleton)**
FastAPI + SQLite = 1 arquivo, ~100 linhas, endpoints funcionando em 4h. Node.js precisa de projeto, middleware, MQTT client setup. Go precisa aprender a linguagem.

**2. SQLite → Postgres é um script de 15 linhas**
```python
# Migração: Trocar connection string
# sqlite:///casa_bionica.db  →  postgresql://user:pass@host/casa_bionica
# SQLAlchemy faz o resto. Zero mudança no código de aplicação.
```
Isso atende a restrição do Eduardo: "stack não muda do protótipo para PoC/MVP".

**3. Python é a linguagem natural para baseline EWMA**
```python
import numpy as np
# EWMA: alpha=0.2, threshold=2σ
ewma = df['duration'].ewm(alpha=0.2).mean()
std = df['duration'].ewm(alpha=0.2).std()
anomaly = current > ewma + 2 * std
```
4 linhas. Em JS: ~40 linhas ou biblioteca externa.

**4. Ecossistema de ML/analytics futuro**
Quando chegar no Traction-Ready e precisar de ML preditivo (risco de queda), Python é a linguagem. Não precisará reescrever o backend.

**5. MQTT broker é commodity**
Mosquitto roda em Docker, 20MB RAM, setup de 5 minutos. Não é complexidade relevante.

**6. ATRIA já usa Python**
Há familiaridade no ecossistema.

### Arquitetura concreta (Walking Skeleton):

```
Sensor ESP32-C3 (4×)
  │ BLE advertisement (evento de travessia)
  │ Payload: {sensor_id, timestamp, direction}
  ▼
Gateway ESP32-C3
  │ WiFi + MQTT publish
  │ Topic: casa_bionica/events
  ▼
Mosquitto MQTT Broker (Docker, Railway)
  │
  ▼
FastAPI (Python, Railway)
  │ POST /ingest (subscriber MQTT → SQLite)
  │ GET  /events?sensor_id=&from=&to=
  │ GET  /baseline?sensor_id=
  │ GET  /alerts?status=active
  │
  ▼
SQLite (arquivo, mesmo container)
  │ Tabelas: events, baseline, alerts
  │
  ▼
Dashboard HTML (Netlify ou mesmo Railway)
  │ Status atual, timeline 24h, últimos alertas
```

### O que NÃO precisa agora:
- ❌ TimescaleDB (MVP, não Walking Skeleton)
- ❌ Docker Compose multi-container (1 container basta)
- ❌ Redis/cache (4 sensores, 1 idoso = ~200 eventos/dia)
- ❌ Autenticação JWT (só Eduardo acessa)
- ❌ CI/CD complexo (git push + railway up)

---

## ⚠️ Riscos e Mitigações

| Risco | Prob | Impacto | Mitigação |
|-------|------|---------|-----------|
| Python lento para ingestão high-frequency | Baixa | Baixo | 4 sensores = ~1 evento/minuto. Python sobra |
| SQLite corrompe com múltiplos writers | Muito Baixa | Médio | 1 writer (FastAPI). SQLite é safe single-writer |
| MQTT broker cai | Baixa | Médio | Mosquitto é rock-solid. Healthcheck + restart |
| Falta familiaridade ATRIA com FastAPI | Baixa | Baixo | FastAPI é Flask-like. Curva de 2h |

---

## Stack Final (Decisão Técnica)

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| **Sensor firmware** | C++ (Arduino) + VL53L0X library | Única opção. State machine de travessia |
| **Sensor→Gateway** | BLE (primeira semana) → ESP-NOW (se BLE lento) | Baixo consumo. Sem lib externa |
| **Gateway firmware** | C++ (Arduino) + WiFi + PubSubClient (MQTT) | Padrão de todos os refs |
| **MQTT Broker** | Mosquitto (Docker) | Commodity. 5min setup |
| **Backend** | **Python 3.12 + FastAPI** | Velocidade, EWMA nativo, migração trivial SQLite→Postgres |
| **ORM** | SQLAlchemy 2.0 (async) | Abstraction over SQLite/Postgres |
| **Banco (WS)** | SQLite | Zero-config. Arquivo único. Backup = cp |
| **Banco (PoC/MVP)** | PostgreSQL + TimescaleDB | Migração: trocar connection string |
| **EWMA Engine** | NumPy + Pandas (job horário) | 4 linhas de código |
| **Dashboard** | HTML estático (Netlify) ou FastAPI Jinja2 | WS: Jinja2 (1 template). MVP: React/Vue |
| **Deploy** | Railway (git push) | ATRIA padrão. GitHub Actions opcional |
| **Notificação** | Twilio/WhatsApp API (MVP) | WS: console.log. PoC: email. MVP: WhatsApp |
