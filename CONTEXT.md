# CONTEXT.md — Casa Biônica Glossary

> Domain vocabulary. Use these exact terms in all code, docs, and conversations.
> Fonte: improve-codebase-architecture §Language, organizational-lightness §1.5.

---

## Domain Terms

| Termo | Definição |
|-------|-----------|
| **Crossing Event** | Um corpo cruzou uma passagem. Atributos: device_id, direction, distance_mm, event_timestamp. |
| **Passagem** (Passage) | Limite entre dois ambientes (ex: Quarto↔Corredor). 1 passagem = 2 sensores VL53L0X + 1 ESP32-C3. Tipos: `room` (interior) ou `entrance` (porta de entrada). |
| **Device** (Sensor Module) | Unidade física: 1 ESP32-C3 + 2 VL53L0X instalados em uma passagem. Identificado por `sensor_id` (ex: `sensor-quarto-01`). |
| **Home** (Residência) | Unidade de monitoramento. 1 home = 1 idoso principal + N passages + M emergency_contacts. Identificada por `home_id` (ex: `home-001`). |
| **Long Lie** | Idoso caído e incapaz de se levantar por horas/dias. Evento-alvo do sistema. |
| **Presence** | Estado derivado: "home" (último evento da entrada foi `entry`) ou "away" (último foi `exit`). |
| **EWMA** | Exponentially Weighted Moving Average. α=0.2, threshold=2σ, janela=7 dias. Usado para baseline de rotina. |
| **Baseline** | Perfil de ocupação normal por sensor + faixa horária. Calculado via EWMA. |
| **Anomaly** | Duração atual no ambiente > baseline.mean + 2×baseline.std. |
| **Alert** | Notificação de anomalia. Status: pending → notified → acknowledged → resolved → escalated_external. |
| **Escalation** | Cadeia de notificação: N1 (prioridade 1) → timeout → N2 → timeout → N3 → timeout → SAMU (external). |
| **Walking Skeleton** | Fase atual. 1 residência, 5 passagens, Eduardo como simulador. Objetivo: sistema end-to-end 7 dias. |

---

## Architecture Terms (improve-codebase-architecture)

| Termo | Definição |
|-------|-----------|
| **Module** | Qualquer coisa com interface + implementação (função, classe, arquivo, serviço). |
| **Interface** | Tudo que o caller precisa saber: tipos, invariantes, modos de erro, ordenação. |
| **Depth** | Comportamento complexo atrás de interface simples. Alto leverage. |
| **Seam** | Onde a interface vive. Comportamento pode ser alterado sem editar in-place. |
| **Adapter** | Implementação concreta de uma interface num seam. |
| **Leverage** | O que callers ganham com depth. |
| **Locality** | Mudanças, bugs, conhecimento concentrados em um lugar. |
| **Deletion Test** | Imaginar deletar o módulo. Se complexidade desaparece = pass-through. Se reaparece = ganha seu lugar. |

---

## Sensor IDs

| `sensor_id` | Passage | Type |
|-------------|---------|:---:|
| `sensor-quarto-01` | Quarto ↔ Corredor | room |
| `sensor-banheiro-01` | Banheiro ↔ Corredor | room |
| `sensor-cozinha-01` | Cozinha ↔ Corredor | room |
| `sensor-sala-01` | Sala ↔ Corredor | room |
| `sensor-entrada-01` | Porta de entrada | entrance |

---

## Environment

| Variável | Valor | Onde |
|----------|-------|------|
| `SUPABASE_KEY` | `sb_sec…***` | Railway env var |
| `SUPABASE_URL` | `https://rkiclxviqinciwwumwfb.supabase.co` | Railway env var |
| `HOME_ID` | `home-001` | Railway env var |
| `API_URL` | `https://backend-production-607f.up.railway.app/ingest` | ESP32 firmware |

---

## Version

`v2.1.0` — PostgREST backend, schema v2, Railway production (03/Ago/2026)
