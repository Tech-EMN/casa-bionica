# ADR-002 — Protocolo de Comunicação ESP32 → Backend

- **Status:** Aceito
- **Data:** 03/Ago/2026
- **Decisor:** Daedalus (AG01), ratificado por Eduardo Nunes

---

## Contexto

O Walking Skeleton exige que 4 módulos ESP32-C3 (cada um com 2× VL53L0X) enviem eventos de travessia ao backend na nuvem. É preciso escolher o protocolo de comunicação.

## Alternativas Consideradas

| Protocolo | Peças móveis | Consumo sensor | Setup | Migração futura |
|-----------|:---:|:---:|---|---|
| **A) HTTP POST direto** | 2 (ESP32 + FastAPI) | Alto (WiFi ligado) | Zero infra | Rewrite firmware |
| **B) MQTT** | 3 (+Mosquitto) | Alto (WiFi ligado) | Broker extra | Adiciona gateway |
| **C) BLE → Gateway → HTTP** | 4 (+Gateway ESP32) | Baixo (BLE) | +1 ESP32 | Cresce natural |
| **D) ESP-NOW → Gateway → HTTP** | 4 (+Gateway) | Baixo (ESP-NOW) | +1 ESP32 | Vendor lock-in |

## Decisão

**Opção A — HTTP POST direto para o Walking Skeleton.**

### Justificativa

1. **Organizational-Lightness:** 2 peças móveis vs 4. "Subtrair antes de adicionar." A bateria não é restrição crítica com Eduardo como simulador (troca baterias quando quiser).
2. **Velocidade:** Firmware em 30 linhas. Backend já tem `POST /ingest` pronto. Zero configuração extra.
3. **Caminho de migração:** Quando a bateria se tornar requisito (PoC com familiar 65+), migrar para BLE (opção C). A state machine de detecção não muda — só o transporte.

### Consequências

- ✅ Walking Skeleton funcional em horas
- ✅ Simplicidade máxima
- ❌ Bateria dura horas/dias, não meses
- ❌ Firmware precisa ser reescrito ao migrar para BLE (mas state machine é preservada)

---

## Referências

- PRD Casa Biônica v1.1, §11 (Requirements-Dive Q1-Q12)
- E04 Kickoff, Rodada 5 (Eduardo: "ritmo imediato, 3 dias")
- Organizational-Lightness §2: "Subtrair antes de adicionar"
- 4 projetos referência analisados (todos convergem para dual-sensor, divergem no transporte)
