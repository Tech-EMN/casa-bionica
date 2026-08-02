# Projetos de Referência — Arquitetura Casa Biônica

> **Fonte:** Discussão inicial sobre Hardware do Protótipo (02/Ago/2026)
> **Propósito:** Extrair padrões arquiteturais dos 4 projetos de referência citados no documento de hardware
> **Compilação:** Daedalus (AG01) — 02/Ago/2026

---

## Matriz Comparativa

| Dimensão | #1 Reddit Counter | #2 Smart Access Monitor | #3 ST Manual | #4 RooDe |
|----------|-------------------|------------------------|--------------|----------|
| **Sensor** | 2× VL53L1X | 2× IR sensor | VL53L1X (oficial) | 2× VL53L0X → VL53L1X |
| **MCU** | ESP32-C6 | ESP32 | — | ESP32/ESP8266 |
| **Wake-up** | PIR | — (always on) | — | HC-SR501 PIR |
| **Direção** | ✅ Dual ToF | ✅ State machine (ENTER/EXIT) | ✅ Documentado | ✅ Dual ToF |
| **Bateria** | ✅ Bateria | ❌ USB | — | ✅ 18650 (~3 meses) |
| **Comunicação** | — | WebServer HTTP | — | MQTT (ESPHome) |
| **Display** | — | Chart.js web | — | OLED 128×32 |
| **Calibração** | — | — | ✅ Documentada | ✅ Desvio padrão |
| **Gabinete** | — | Breadboard | — | ✅ STL 3D printable |
| **Maturidade** | Post Reddit | Projeto acadêmico | Documento oficial | 2+ anos, open source |
| **Link** | [Reddit][1] | [OCW][2] | [Manualzz][3] | [GitHub][4] |

[1]: https://www.reddit.com/r/esp32/comments/1umb5x0/built_a_batterypowered_doorway_occupancy_counter/
[2]: https://ocw.cs.pub.ro/courses/iothings/proiecte/2025sric/esp32-smart-access-monitor
[3]: https://manualzz.com/doc/62100236/st-counting-people-user-manual
[4]: https://github.com/Lyr3x/Roode

---

## Padrões Arquiteturais Convergentes

### 1. Dual Sensor (ToF ou IR) — TODOS os projetos convergem

```
      BATENTE (vista superior)
    ┌─────────────────────────┐
    │                         │
    │  [Sensor A]  [Sensor B] │  ← ambos no mesmo lado
    │       ↓          ↓      │
    │   ═══════════════════   │  ← linha de travessia
    │                         │
    │           🚶            │
    └─────────────────────────┘
```

**Por que 2 sensores?**
- **Direção:** A→B primeiro = entrou; B→A primeiro = saiu
- **Redundância:** Se 1 falha, o outro ainda detecta passagem
- **Anti-falso-positivo:** Ambos precisam ativar em sequência (elimina objeto parado, pet pequeno)

**Padrão Casa Biônica:** Mesma abordagem. 2× VL53L0X por passagem, instalados no batente a ~1m de altura.

---

### 2. State Machine com Timeout — Projeto #2 e #4

**Padrão do Smart Access Monitor (#2):**
```
IDLE → ENTER_STAGE_1 (Sensor A ativa) → ENTER_STAGE_2 (Sensor B ativa em <2s) → COUNT++ → IDLE
IDLE → EXIT_STAGE_1  (Sensor B ativa) → EXIT_STAGE_2  (Sensor A ativa em <2s) → COUNT-- → IDLE
```
- Timeout: 2000ms entre sensores
- Se timeout expira → volta para IDLE (pessoa desistiu de atravessar)

**Padrão Casa Biônica:** Adotar state machine similar, mas sem decrementar (não precisamos de contagem líquida — cada travessia é um evento independente).

---

### 3. PIR como Wake-Up — Projeto #1 e #4

**Padrão RooDe (#4):**
```
Deep Sleep (8µA)
    ↓ PIR detecta movimento
Wake ESP32 (50ms)
    ↓ Liga VL53L0X
Mede distância (ambos sensores)
    ↓ Confirma travessia?
Transmite MQTT (50ms)
    ↓
Volta a dormir
```

**Por que PIR + ToF e não só ToF?**
- ToF precisa ficar medindo continuamente → consome ~18mA constante
- PIR consome ~50µA em modo de espera, acorda o sistema só quando detecta calor
- Consumo total cai de ~18mA contínuo para ~50µA em espera + picos de 100mA por 200ms

**Padrão Casa Biônica:** RooDe reporta 3 meses com 18650. Com otimização (ESP32-C3 deep sleep + CR123A ou 2×AA) e transmissão BLE mínima, 2 anos é plausível.

---

### 4. MQTT como Protocolo de Gateway — Projeto #4

**Padrão RooDe:**
```
Sensor ESP32 ──MQTT──→ Broker ──→ Home Assistant / Domoticz
```
- ESPHome framework para configuração
- MQTT para telemetria
- Home Assistant para dashboard e automação

**Padrão Casa Biônica:** Gateway ESP32-C3 com WiFi + MQTT → Cloud (Railway) → Dashboard. Mesmo padrão, substituindo Home Assistant por backend próprio.

---

### 5. Calibração por Desvio Padrão — Projeto #4

**Padrão RooDe:**
```
threshold = mean_distance + (n_std_deviations × std_dev)
```
- Recalibração automática via Domoticz
- Threshold adaptativo

**Padrão Casa Biônica:** Já alinhado — PRD especifica EWMA (média móvel exponencial) + threshold de 2σ. RooDe confirma que desvio padrão funciona em campo.

---

## Lições Aprendidas dos Projetos

### Do Reddit (#1)
> "A parte mais difícil foi o algoritmo para lidar com pessoas que param na porta ou desistem da travessia."

**Para Casa Biônica:** State machine com timeout de 2s (padrão #2). Se pessoa para no batente e não completa a travessia em 2s → descarta evento.

### Do Smart Access Monitor (#2)
> "Differentiating between entry and exit requires precise detection and timing."

**Para Casa Biônica:** Posição e distância entre os 2 sensores é crítica. Testar 5cm, 10cm e 15cm de separação.

### Do ST Manual (#3)
> "O VL53L1X foi projetado exatamente para contagem de pessoas."

**Para Casa Biônica:** Não estamos usando o sensor "fora da aplicação". A ST publicou algoritmo oficial — usar como referência primária.

### Do RooDe (#4)
> "With a pair of 18650 I used the system for about 3 months. Battery management can be improved."

**Para Casa Biônica:** 3 meses é linha de base pessimista. O RooDe usa ESP8266 (consome mais que ESP32-C3), 18650 (capacidade similar a 2×AA alcalinas). Com deep sleep otimizado + BLE (não WiFi no sensor) + VL53 em vez de polling contínuo → 12-24 meses é realista.

---

## Arquitetura Final Casa Biônica (POC V0)

Esta arquitetura sintetiza os 4 projetos de referência + decisões do documento de hardware:

```
                    RESIDÊNCIA
    ┌──────────────────────────────────────┐
    │                                      │
    │  Passagem 1    Passagem 2    Passagem N
    │  ┌─────────┐   ┌─────────┐   ┌─────────┐
    │  │ESP32-C3 │   │ESP32-C3 │   │ESP32-C3 │
    │  │2×VL53L0X│   │2×VL53L0X│   │2×VL53L0X│
    │  │PIR wake │   │PIR wake │   │PIR wake │
    │  │2×AA bat │   │2×AA bat │   │2×AA bat │
    │  └────┬────┘   └────┬────┘   └────┬────┘
    │       │ BLE         │ BLE         │ BLE
    │       └─────────┬───┴─────────────┘
    │                 │
    │          ┌──────┴──────┐
    │          │ GATEWAY     │
    │          │ ESP32-C3    │
    │          │ WiFi + MQTT │
    │          │ Tomada      │
    │          └──────┬──────┘
    └─────────────────┼────────────────────
                      │ WiFi
    ┌─────────────────┼────────────────────
    │          CLOUD (Railway)              │
    │  ┌──────────┐  ┌──────────┐          │
    │  │ Ingestão │→│TimeSeries│           │
    │  │  MQTT    │  │   DB     │           │
    │  └──────────┘  └────┬─────┘          │
    │                     │                 │
    │  ┌──────────────────┴──────┐          │
    │  │ Motor de Baseline (EWMA)│          │
    │  └──────────┬──────────────┘          │
    │             │                          │
    │  ┌──────────┴──────────┐              │
    │  │ Notificação + Dash  │              │
    │  └─────────────────────┘              │
    └───────────────────────────────────────┘
```

### Inspiração direta dos projetos:

| Componente | Origem | Adaptação Casa Biônica |
|-----------|--------|----------------------|
| 2× VL53L0X por passagem | Reddit #1 + RooDe #4 | Mantido — direção + redundância |
| State machine com timeout | Smart Access Monitor #2 | Adaptado — sem decremento, evento único |
| PIR wake-up | Reddit #1 + RooDe #4 | Mantido — essencial para bateria 2 anos |
| MQTT gateway | RooDe #4 | Mantido — gateway ESP32 → cloud |
| Calibração σ | RooDe #4 | Alinhado — EWMA + 2σ já no PRD |
| Algoritmo ST oficial | ST Manual #3 | Referência primária para detecção |

---

## Referências

| # | Projeto | URL | Tecnologia |
|---|---------|-----|-----------|
| 1 | Battery-powered doorway occupancy counter | [Reddit](https://www.reddit.com/r/esp32/comments/1umb5x0/built_a_batterypowered_doorway_occupancy_counter/) | ESP32-C6 + PIR + 2×VL53L1X |
| 2 | ESP32 Smart Access Monitor | [OCW](https://ocw.cs.pub.ro/courses/iothings/proiecte/2025sric/esp32-smart-access-monitor) | ESP32 + 2×IR + WebServer |
| 3 | ST Counting People User Manual | [Manualzz](https://manualzz.com/doc/62100236/st-counting-people-user-manual) | VL53L1X algoritmo oficial |
| 4 | RooDe — Reliable PeopleCounter | [GitHub](https://github.com/Lyr3x/Roode) | ESP32 + 2×VL53L0X + MQTT |
