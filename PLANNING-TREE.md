# Planning Tree — Casa Biônica (PRJ-033)

> **Metodologia:** E1.S6 (Workbook "Soluções ATRIA Corp")
> **Fase atual:** Fase 0 — Discovery & Architecture Planning
> **Elaboração:** Daedalus (AG01) — 02/Ago/2026
> **Fontes:** Workbook PARTE I-VI, PRD v1.1, Design Comercial v1.0, Hardware Discussion, 4 Projetos Referência

---

## 🌳 ÁRVORE DE PLANEJAMENTO (NÍVEL 1)

```
CASA BIÔNICA
│
├── 🔴 TRONCO ─── Decisões de Arquitetura Irreversíveis
│   ├── Sensor: VL53L0X/L1X (ToF) — decidido 02/Ago/2026
│   ├── MCU: ESP32-C3 — decidido 02/Ago/2026
│   ├── Dual-sensor por passagem — padrão convergente dos 4 refs
│   ├── Arquitetura: Sensor burro + Gateway + Cloud inteligente
│   └── Bateria: 2×AA ou CR123A, alvo 2 anos
│
├── 🟡 FASE 0 — DISCOVERY (atual)
│   │
│   ├── ✅ E01 — Hipóteses Iniciais
│   │   ├── H1: Long lie é o evento-alvo (VALIDADA — PRD + personas)
│   │   ├── H2: Tempo de permanência é proxy confiável (VALIDADA — refs)
│   │   ├── H3: ToF VL53 é o sensor certo (VALIDADA — hardware doc)
│   │   ├── H4: Arquitetura sensor burro + cloud inteligente (VALIDADA)
│   │   └── H5: Bateria 2 anos com dual-sensor + PIR wake-up (EM VALIDAÇÃO)
│   │
│   ├── ✅ E02 — Leitura do Workbook
│   │   ├── PARTE I (Glossário)
│   │   ├── PARTE II (Etapas E01-E20)
│   │   ├── PARTE III (Classificação C0-C5)
│   │   ├── PARTE IV (Modo de Usar)
│   │   ├── ✅ PARTE V (Formulários F1-F8 + Roteiros R1-R4)
│   │   └── PARTE VI (Checklists P0-P4)
│   │
│   ├── ✅ E03 — Extração de Formulários (PARTE V)
│   │   ├── ✅ F2 — Contexto e Objetivo (pré-preenchido)
│   │   ├── ✅ F3 — Inventário de Sistemas (10 sistemas + tabela cliente)
│   │   ├── ✅ F4 — Restrições e Políticas (12 restrições mapeadas)
│   │   └── 📋 F1, F5, F6, F7, F8, R1-R4 (templates, não extraídos)
│   │
│   ├── ⬜ E04 — Workshop de Kickoff
│   │   ├── Participantes: Eduardo (sponsor) + Daedalus (facilitador)
│   │   ├── Duração: 2h
│   │   ├── Pauta:
│   │   │   ├── Ratificar F2 (contexto e objetivo)
│   │   │   ├── Validar personas (P1-P10 do Design Comercial)
│   │   │   ├── Confirmar restrições F4 (R1-R12)
│   │   │   ├── Definir escopo do Walking Skeleton (quais passagens? qual idoso?)
│   │   │   └── Acordar critérios de sucesso (pergunta 7 do F2)
│   │   └── Gate P0: Escopo aceito, sponsor confirmado, agenda E06+E08 definida
│   │
│   └── ⬜ E05 — Coleta e Classificação de Itens de Entrada
│       ├── Fonte: PRD v1.1 (RF01-RF05, NF01-NF05, US01-US05)
│       ├── Fonte: Hardware Discussion (13 perguntas + respostas)
│       ├── Fonte: Design Comercial (S0-S5, personas, analogs)
│       ├── Classificar cada item como C0-C5
│       ├── Preencher F1 para cada item
│       └── Gate P1: Todo item classificado, propósito ratificado
│
├── 🟠 FASE 1 — DOMAIN DISCOVERY
│   │
│   ├── ⬜ E06 — Oficina de Domínio (R1)
│   │   ├── Participantes: Eduardo + stakeholders técnicos (se houver)
│   │   ├── Roteiro R1: 3h45 + intervalo
│   │   ├── Blocos:
│   │   │   ├── 0:00 — Abertura (regra: sem hierarquia na parede)
│   │   │   ├── 0:15 — Eventos do processo (um por nota)
│   │   │   ├── 0:45 — Linha do tempo coletiva
│   │   │   ├── 1:30 — Pontos de dor, espera, retrabalho, decisão
│   │   │   ├── 2:15 — Intervalo
│   │   │   ├── 2:30 — Vocabulário divergente
│   │   │   ├── 3:15 — Fronteiras de responsabilidade
│   │   │   └── 3:45 — Fechamento
│   │   ├── Saídas: timeline de eventos, glossário ubíquo, mapa de dor, fronteiras
│   │   └── Gate P0: Confirmado antes de E06
│   │
│   ├── ⬜ E07 — Preparar Material da Oficina de Qualidade
│   │   ├── Preencher F5 (material de apoio)
│   │   ├── Conteúdo: 9 características ISO 25010 em linguagem de negócio
│   │   ├── 2 exemplos de cenário por característica
│   │   ├── Agenda + lista de participantes
│   │   └── Enviar 3 dias antes de E08
│   │
│   └── ⬜ E08 — Oficina de Qualidade (R2)
│       ├── Roteiro R2: sequência QAW (8 passos, 5h)
│       ├── Passos:
│       │   ├── 1. Apresentação do método (15min)
│       │   ├── 2. Apresentação de negócio (cliente)
│       │   ├── 3. Contexto arquitetural conhecido
│       │   ├── 4. Identificação dos drivers
│       │   ├── 5. Brainstorming de cenários (≥1 por driver)
│       │   ├── 6. Consolidação (só funde com concordância)
│       │   ├── 7. Priorização por voto (n/4 votos cada)
│       │   └── 8. Refinamento do topo (4-5 cenários em F6)
│       ├── Saídas: cenários de qualidade priorizados (F6), mapa de drivers
│       └── Gate P1: Drivers identificados, cenários priorizados
│
├── 🟢 FASE 2 — ARCHITECTURE DEFINITION
│   │
│   ├── ⬜ E09 — Mapa de Drivers
│   │   ├── Consolidar drivers C1-C5 do E05 + cenários do E08
│   │   ├── Cruzar com restrições F4
│   │   ├── Priorizar: o que guia a arquitetura vs o que é restrição
│   │   └── Saída: matriz drivers × restrições × cenários
│   │
│   ├── ⬜ E10 — Prova de Realidade
│   │   ├── Confrontar F3 (inventário declarado) com evidência
│   │   ├── Verificar cada sistema: API existe? Documentada? Funciona?
│   │   ├── Testar VL53L0X em campo real (apartamento, não bancada)
│   │   ├── Medir: distâncias reais, falsos positivos, falsos negativos
│   │   └── Gate P2: Inventário verificado, gaps documentados
│   │
│   ├── ⬜ E11 — Baseline Arquitetural (AS-IS)
│   │   ├── Documentar arquitetura atual (se existir sistema legado)
│   │   ├── Para Casa Biônica: não há legado → este é o baseline zero
│   │   └── Saída: diagrama C4 Nível 1 (Contexto) + Nível 2 (Container)
│   │
│   ├── ⬜ E12 — Entrevista com Operador (R4)
│   │   ├── Roteiro R4: individual, 45min, sem chefia
│   │   ├── ⚠️ Adaptação: operador = familiar cuidador (persona secundária)
│   │   ├── Perguntas críticas:
│   │   │   ├── 1. Me mostre como você monitora hoje (peça a tela)
│   │   │   ├── 2. O que mais toma seu tempo?
│   │   │   ├── 3. Onde você corrige na mão?
│   │   │   ├── 4. Tem planilha própria fora do sistema? ← MAIS PRODUTIVA
│   │   │   ├── 5. Como sabe que fez certo?
│   │   │   ├── 6. Quando dá errado, como descobre?
│   │   │   ├── 7. O que mudaria se pudesse?
│   │   │   ├── 8. Se der errado, qual foi o motivo?
│   │   │   └── 9. O que já tentaram que não deu certo?
│   │   └── Saída: requisitos não documentados, planilhas paralelas, dores reais
│   │
│   ├── ⬜ E13 — Design da Solução (TO-BE)
│   │   ├── Stack decision via AX-stack-choosing
│   │   │   ├── Backend: Node.js vs Python/FastAPI vs Go
│   │   │   ├── Banco: TimescaleDB vs InfluxDB vs SQLite
│   │   │   ├── Cloud: Railway (ATRIA padrão) vs AWS vs Fly.io
│   │   │   └── Protocolo gateway: MQTT vs HTTP/2 vs WebSocket
│   │   ├── Diagrama C4 Nível 3 (Componente) + Nível 4 (Código)
│   │   ├── Decisão de protocolo sensor↔gateway: BLE vs ESP-NOW
│   │   ├── Schema do time-series DB (eventos, baseline, alertas)
│   │   ├── API contracts (OpenAPI 3.0)
│   │   └── Gate P2: Design revisado, stack decidida
│   │
│   ├── ⬜ E14 — Análise de Tradeoffs
│   │   ├── Documentar tradeoffs explícitos:
│   │   │   ├── Dual-sensor vs single-sensor (custo × confiabilidade)
│   │   │   ├── BLE vs ESP-NOW (compatibilidade × latência)
│   │   │   ├── Edge vs Cloud baseline (latência × complexidade)
│   │   │   ├── Bateria 2×AA vs CR123A (disponibilidade × tamanho)
│   │   │   └── MQTT vs HTTP (eficiência energética × simplicidade)
│   │   ├── Cada tradeoff: o que melhora × o que piora
│   │   └── Saída: matriz de tradeoffs com recomendações preliminares
│   │
│   ├── ⬜ E15 — Prototipação e Validação Técnica
│   │   ├── **Momento atual do Eduardo** (comprando sensores, 02/Ago)
│   │   ├── Sprint 1: VL53L0X lendo distância via Serial (Dia 1)
│   │   ├── Sprint 2: State machine de travessia (Dia 2)
│   │   ├── Sprint 3: BLE sensor→gateway + MQTT→cloud (Dia 3-5)
│   │   ├── Sprint 4: Calibração EWMA + baseline (Dia 6-7)
│   │   ├── Sprint 5: Dashboard web mínimo (Dia 8-10)
│   │   └── Gate P3: Protótipo funcional end-to-end, métricas coletadas
│   │
│   └── ⬜ E16 — Sessão de Tradeoff com Sponsor (R3)
│       ├── Roteiro R3: 2h30
│       ├── Blocos:
│       │   ├── 0:00 — Retomada do propósito + cenários priorizados
│       │   ├── 0:15 — Tradeoffs, um a um, SEM recomendação ATRIA
│       │   ├── 1:30 — Manifestação do sponsor sobre cada um
│       │   ├── 2:00 — SÓ AGORA ATRIA recomenda e justifica
│       │   └── 2:30 — Registro das decisões (F7 ADRs) + assinatura
│       └── Saídas: ADRs ratificados, tradeoffs decididos pelo sponsor
│
├── 🔵 FASE 3 — VALIDATION & DELIVERY
│   │
│   ├── ⬜ E17 — Implementação do Walking Skeleton
│   │   ├── Pipeline CI/CD (GitHub Actions → Railway)
│   │   ├── Deploy da stack escolhida em E13
│   │   ├── End-to-end: sensor → gateway → ingest → DB → dashboard
│   │   ├── Com 1 passagem apenas (escopo mínimo)
│   │   └── Gate P3: Walking Skeleton funcionando em ambiente staging
│   │
│   ├── ⬜ E18 — Testes e Validação
│   │   ├── Testes de travessia (normal, rápido, parando, voltando)
│   │   ├── Testes de falso positivo (pet, mochila, robô, visita)
│   │   ├── Testes de bateria (INA219 — medir 4 estados)
│   │   ├── Testes de conectividade (WiFi cai, BLE range)
│   │   ├── Testes de baseline (7 dias de calibração)
│   │   └── Métricas-alvo:
│   │       ├── Precisão detecção > 90%
│   │       ├── Falsos positivos < 2/dia
│   │       ├── Latência end-to-end < 5s
│   │       └── Uptime > 99%
│   │
│   ├── ⬜ E19 — Documentação e Runbooks
│   │   ├── Runbook de instalação (15min, sem técnico)
│   │   ├── Runbook de troubleshooting (8 cenários)
│   │   ├── Runbook de calibração e recalibração
│   │   ├── Documentação da API (OpenAPI)
│   │   └── Diagramas C4 atualizados (N1-N4)
│   │
│   └── ⬜ E20 — Devolução ao Cliente
│       ├── Devolver itens C0 (F8 — Registro de Encaminhamento)
│       ├── Apresentar protótipo funcional
│       ├── Coletar aceite do cliente
│       └── Gate P4: Aceite formal, próximos passos para MVP
│
└── 🟣 PÓS-ENTREGA — MATURITY LADDER
    │
    ├── Walking Skeleton (Fase 1 — atual)
    │   ├── 1 passagem, 1 idoso, bancada + 1 apto real
    │   ├── Métricas básicas de detecção
    │   └── Sem baseline adaptativo ainda
    │
    ├── MVP (Fase 2)
    │   ├── 4-6 passagens, 3-5 idosos beta
    │   ├── Baseline EWMA funcional
    │   ├── App web para familiar
    │   ├── Escalada de alerta (N1→N2)
    │   └── Bateria validada > 12 meses
    │
    ├── Traction-Ready (Fase 3)
    │   ├── Produção: 50+ residências
    │   ├── Dashboard S3 (seguradoras) — dados anonimizados
    │   ├── App mobile nativo
    │   ├── Chip 4G opcional (Kit Pro)
    │   └── Certificação ANVISA (se aplicável)
    │
    └── Scale-Ready (Fase 4)
        ├── 500+ residências
        ├── White-label S4 (ILPIs)
        ├── Multi-idoso por residência
        ├── Integração com operadoras de saúde
        └── ML preditivo (risco de queda antes de acontecer)
```

---

## 📊 MATRIZ DE GATES (PARTE VI)

| Gate | Estágio | Checklist | Status |
|------|---------|-----------|--------|
| **P0** | Pré-E01 | Escopo aceito · Kit de Entrada devolvido · Agenda de acessos · Sponsor identificado · Participantes E06+E08 nomeados | ⬜ Pendente (E04) |
| **P1** | Pós-E05 | Propósito ratificado · Todo item C0-C5 · Cenários priorizados | ⬜ Pendente |
| **P2** | Pós-E08 | Design revisado · Stack decidida · Inventário verificado | ⬜ Pendente |
| **P3** | Pós-E15 | Protótipo funcional · Métricas coletadas · Tradeoffs decididos | ⬜ Pendente |
| **P4** | Pós-E20 | Aceite formal · Itens C0 devolvidos · Próximos passos definidos | ⬜ Pendente |

---

## 🔗 DEPENDÊNCIAS CRÍTICAS

```
E04 (Kickoff)
├── Precisa: Eduardo disponível 2h
├── Bloqueia: E05, E06, E08
└── Risco: baixo (Eduardo é sponsor e está ativo)

E06 (Oficina de Domínio)
├── Precisa: E04 concluído
├── Precisa: stakeholders técnicos (se houver)
└── Risco: médio (depende de agenda de terceiros)

E08 (Oficina de Qualidade)
├── Precisa: E06 + E07 concluídos
├── Precisa: F5 enviado 3 dias antes
└── Risco: médio (precisa de participantes diversos)

E12 (Entrevista com Operador)
├── ⚠️ ADAPTAÇÃO: "operador" = familiar cuidador
├── Precisa: acesso a familiares de idosos (recrutar 3-5)
└── Risco: ALTO (recrutamento de participantes externos)

E15 (Prototipação Técnica)
├── Precisa: sensores em mãos ← EM ANDAMENTO (Eduardo comprando)
├── Precisa: E10 (prova de realidade) validando ambiente real
└── Risco: médio (depende de hardware físico)
```

---

## ⏱️ TIMELINE ESTIMADA

| Fase | Etapas | Duração | Depende de |
|------|--------|---------|-----------|
| **Fase 0** (Discovery) | E01-E05 | 1-2 semanas | Kickoff com Eduardo |
| **Fase 1** (Domain) | E06-E08 | 2-3 semanas | Agendas dos participantes |
| **Fase 2** (Architecture) | E09-E16 | 4-6 semanas | Hardware + prototipação |
| **Fase 3** (Delivery) | E17-E20 | 3-4 semanas | Fase 2 concluída |
| **TOTAL até P4** | E01-E20 | 10-15 semanas | — |

---

## 🎯 PRÓXIMA AÇÃO IMEDIATA

**E04 — Workshop de Kickoff**

Agendar 2h com Eduardo para:
1. Ratificar F2 (as 9 perguntas pré-preenchidas)
2. Validar personas-alvo para POC (idoso sozinho, apto 50-120m², sem pets)
3. Confirmar 12 restrições F4 (especialmente R1: sem câmera, R2: sem wearable)
4. Definir Walking Skeleton (qual passagem? qual hardware exato?)
5. Acordar métricas de sucesso (pergunta 7 do F2)
6. Nomear participantes para E06 e E08

**Duração estimada:** 2h
**Preparação necessária:** Levar F2, F3, F4 impressos (ou abertos no Drive)
**Gate P0 checklist:** Sponsor confirmado ✅ (Eduardo) · Escopo aceito ⬜ · Kit de Entrada ⬜ · Agenda E06+E08 ⬜
