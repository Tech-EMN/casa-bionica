# E05 — Classificação de Itens de Entrada (C0-C5)

> **Fonte:** PRD v1.1 §3-4-6 | **Data:** 2026-08-03
> **Escopo:** Front-End V1 "Raízes" — Familiar Auto-Case + Investor-ready

## Legenda

| Classe | Significado | Ação |
|--------|------------|------|
| **C0** | Fora do escopo | Devolver ao cliente (E20) |
| **C1** | Crítico | V1 não entrega sem isso |
| **C2** | Importante | V1 entrega parcial sem isso |
| **C3** | Desejável | Próximo incremento (V2+) |
| **C4** | Futuro | Roadmap (MVP/Scale) |
| **C5** | Descartado | Não se aplica mais |

---

## Requisitos Funcionais (RF01-RF05)

| ID | Descrição | Classe | Justificativa |
|----|-----------|--------|---------------|
| RF01 | Detecção de movimento entre cômodos | **C1** | Core do produto. Já implementado no backend (POST /ingest, GET /events). Front-end só consome |
| RF02 | Baseline de rotina (EWMA, 7 dias) | **C1** | Q3=B+C exige baseline semanal no dashboard. Depende de F1.1 (EWMA engine) |
| RF03 | Alerta de violação de rotina | **C2** | Disparado pelo backend (WhatsApp). Front-end só exibe status de alertas ativos. Lógica de disparo = backend |
| RF04 | Dashboard do familiar | **C1** | **Este é o escopo inteiro da V1.** Planta da casa + timeline + baseline |
| RF05 | Resiliência e offline (buffer 24h) | **C3** | Importante para produção, mas V1 é dashboard de monitoramento. Buffer é preocupação do firmware |

## Requisitos Não-Funcionais (NFR01-NFR05)

| ID | Descrição | Classe | Justificativa |
|----|-----------|--------|---------------|
| NFR01 | Privacidade (sem câmera, consentimento) | **C2** | Não é implementável em código de front-end. Mas afeta: zero coleta de dados no client-side, política de privacidade no footer |
| NFR02 | Consumo energético (<12 meses bateria) | **C3** | Preocupação do hardware/firmware. Dashboard só mostra nível de bateria se disponível no GET /status |
| NFR03 | Custo-alvo hardware (<R$250 kit) | **C3** | Preocupação de produto, não de front-end |
| NFR04 | Latência (<5s detecção→alerta) | **C2** | Dashboard faz polling 30s. A latência de 5s é entre sensor→WhatsApp, não entre sensor→dashboard |
| NFR05 | Disponibilidade (99% protótipo) | **C2** | Dashboard depende do backend. Se backend cair, dashboard mostra estado de erro. Health check passivo |

## User Stories (US01-US05)

| ID | Descrição | Classe | Justificativa |
|----|-----------|--------|---------------|
| US01 | Instalação guiada <15min | **C3** | Q4=B+C: wizard existe no app, mas instalação física é feita por técnico na PoC. Wizard cobre cadastro, não instalação de hardware |
| US02 | Período de calibração (7 dias) | **C2** | Dashboard deve mostrar "Aprendendo rotina — dia X de 7" enquanto baseline não está pronto. Sem alertas até completar |
| US03 | Alerta de queda | **C2** | Core do produto, mas disparado pelo backend/WhatsApp. Dashboard mostra: alertas ativos, status de escalação, histórico |
| US04 | Verificação de bem-estar (botão emergência) | **C3** | Botão "Acionar Emergência" no dashboard = V2. V1 foca em monitoramento passivo |
| US05 | Convite para outros familiares | **C3** | Multi-usuário read-only = V2. V1 = single user (o familiar do Auto-Case) |

---

## Resumo

| Classe | Contagem | Itens |
|--------|----------|-------|
| **C1** | 3 | RF01, RF02, RF04 |
| **C2** | 5 | RF03, NFR01, NFR04, NFR05, US02, US03 |
| **C3** | 6 | RF05, NFR02, NFR03, US01, US04, US05 |
| **C4** | 0 | — |
| **C5** | 0 | — |

**Gate P1:** ✅ 15 itens classificados. V1 cobre C1 (crítico) + parcialmente C2. C3+ ficam para V2/MVP.
