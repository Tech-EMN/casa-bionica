# F3 · Inventário Declarado de Sistemas

> **Fonte:** PARTE V — Workbook "Soluções ATRIA Corp" | Metodologia E1.S6
> **Regra:** Uma linha por sistema. Declarado ≠ verificado. Este formulário produz a hipótese que E10 vai confrontar com evidência.
> **Extração:** 02/Ago/2026 — Daedalus (AG01)

---

## Inventário

| # | Sistema | Fornecedor | O que guarda/faz | Tem API? | Documentada? | Quem administra | Ambiente de teste? | Já integrado a quê |
|---|---------|-----------|-------------------|----------|-------------|-----------------|-------------------|---------------------|
| 1 | **Sensor ToF VL53L1X** | STMicroelectronics | Detecção de passagem no batente (distância, direção entrada/saída). 6 unidades por kit. | I2C (hardware) | ✅ Datasheet público | ATRIA (firmware) | ✅ Protoboard + ESP32 | Multiplexador TCA9548A (até 8 sensores) |
| 2 | **Hub ESP32-C3** | Espressif | Agrega eventos dos sensores, buffer local (24h), envia para cloud via MQTT/HTTPS | ✅ WiFi + BLE | ✅ SDK ESP-IDF | ATRIA (firmware) | ✅ Simulador local | Sensores ToF (I2C), Cloud (MQTT) |
| 3 | **Ingestão Cloud (API)** | ATRIA (a definir stack) | Recebe eventos do hub, normaliza, enfileira | ✅ REST / MQTT | 📋 A documentar | ATRIA (backend) | 📋 Staging Railway | Time-Series DB |
| 4 | **Time-Series DB** | A decidir: TimescaleDB ou InfluxDB | Armazena eventos (sensor_id, timestamp, tipo_evento) + métricas de baseline | ✅ SQL / Flux | 📋 Conforme stack escolhida | ATRIA (devops) | 📋 Sim | API de Ingestão, Motor de Baseline |
| 5 | **Motor de Baseline (EWMA)** | ATRIA (a definir stack) | Calcula baseline de rotina por cômodo+faixa horária, detecta anomalias (>2σ ou >2× máx histórico) | 📋 API interna | 📋 A documentar | ATRIA (data/ML) | 📋 Notebook/Python | Time-Series DB, Notificação |
| 6 | **Serviço de Notificação** | Firebase Cloud Messaging / Twilio | Envia push notification + SMS/WhatsApp para familiar | ✅ Firebase Admin SDK / Twilio REST API | ✅ Documentadas | ATRIA (backend) | ✅ Sandbox | Motor de Baseline |
| 7 | **Dashboard Web** | ATRIA (a definir stack) | Status do idoso (último cômodo, timeline, alertas), gestão de contatos de emergência | ✅ REST (consome API interna) | 📋 A documentar | ATRIA (frontend) | 📋 Netlify preview | API de Ingestão (read-only) |
| 8 | **Firebase / Auth** | Google | Autenticação do familiar (login) + push notifications | ✅ Firebase Auth SDK | ✅ Documentada | ATRIA (dev) | ✅ Sim | Dashboard Web, App |
| 9 | **Railway (Cloud Provider)** | Railway | Hospedagem do backend + banco de dados + ingestão | ✅ Railway API | ✅ Documentada | ATRIA (devops) | ✅ Staging env | GitHub (CI/CD) |
| 10 | **GitHub** | GitHub | Código fonte (firmware, backend, frontend), CI/CD, versionamento | ✅ GitHub API + Actions | ✅ Documentada | ATRIA (dev) | ✅ Branches | Railway (deploy) |

---

## Sistemas do Cliente (a preencher em E06/E10)

| # | Sistema | Fornecedor | O que guarda/faz | Tem API? | Documentada? | Quem administra | Ambiente de teste? | Já integrado a quê |
|---|---------|-----------|-------------------|----------|-------------|-----------------|-------------------|---------------------|
| C1 | A preencher | | | | | | | |
| C2 | A preencher | | | | | | | |
| C3 | A preencher | | | | | | | |

---

## Notas

- **Declarado ≠ verificado:** Todos os sistemas ATRIA listados acima são planejados para o protótipo. E10 (prova de realidade) deve confrontar com evidência de funcionamento real.
- **Sensores:** ToF VL53L1X é a decisão de 02/Ago/2026. PIR descartado. mmWave (LD2410) permanece como alternativa se ToF apresentar limitações em campo.
- **Stack de backend/DB:** A decidir via AX-stack-choosing (Node.js+Express vs Python+FastAPI vs Go; PostgreSQL+TimescaleDB vs InfluxDB vs SQLite).
- **Sistemas do cliente:** A preencher durante E06 (oficina de domínio) e E12 (entrevista com operador).

---

## Ratificação

| Campo | Valor |
|-------|-------|
| **Preenchido por** | Daedalus (AG01) com base em PRD v1.1 |
| **Data de extração** | 02/Ago/2026 |
| **Fonte** | Workbook "Soluções ATRIA Corp" — PARTE V + PRD Casa Biônica v1.1 |
| **Ratificado por** | ______ em __/__/____ |
| **Confiança** | Sistemas ATRIA: VERIFICADO (PRD). Sistemas cliente: a preencher |
