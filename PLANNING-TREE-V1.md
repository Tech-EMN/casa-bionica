# Planning Tree — Casa Biônica Front-End V1

> **Data:** 2026-08-03T23:35:00Z | **Elaboração:** Daedalus (AG01)
> **Fonte:** HANDOFF (E04 done, backend v2.1.0 live), Decisões Q1-Q8
> **Escopo:** Front-end V1 "Raízes" + Baseline Engine + Deploy

## 🔴 TRONCO — Decisões Imutáveis

| Decisão | Valor | Fonte |
|----------|-------|-------|
| Stack backend | Python 3.12 + FastAPI + Supabase PostgREST | HANDOFF §8 |
| Stack frontend | Vanilla JS + CSS Grid, zero frameworks | Q6=A (casa, não hospital) |
| Tom visual | Fredoka + Outfit, paleta terracota | Q6=A |
| Elemento central | Planta da casa + Timeline narrativa | Q8=A+B |
| Canal de alerta | WhatsApp apenas (dashboard é passivo) | Q2=A |
| Usuário V1 | Familiar Auto-Case + Investor-ready | Q1=A+D |
| Multi-home | URL param ?home=, sem switcher | Q5=B |
| Onboarding | Wizard + link mágico, instalador físico | Q4=B+C |
| Timeout alerta | 60min OU contextual OU 2σ/2× | Q7=Híbrido |
| Analytics | Timeline + baseline semanal | Q3=B+C |

## 🌳 ÁRVORE

```
CASA BIÔNICA — FRONT-END V1 + BASELINE ENGINE
│
├── 🟡 FASE 0 — PLANEJAMENTO
│   ├── ✅ F0.1 — Criar PLANNING-TREE-V1.md
│   │   status: completed
│   │   done_criterion: Árvore completa com dependências e gates
│   │   implementation_ref: ["projects/casa-bionica/PLANNING-TREE-V1.md"]
│   │   completed_at: 2026-08-03T23:35:00Z
│   │
│   ├── ✅ F0.2 — Classificar itens E05
│   │   status: completed
│   │   done_criterion: RF01-05, NFR01-05, US01-US05 classificados C0-C5
│   │   implementation_ref: ["projects/casa-bionica/formularios/E05-classificacao-itens.md"]
│   │   completed_at: 2026-08-03T23:40:00Z
│   │
│   └── ✅ F0.3 — Criar FRONTEND-V1-SPEC.md
│       status: completed
│       done_criterion: Mockup, árvore de componentes, endpoints EBI
│       implementation_ref: ["projects/casa-bionica/docs/FRONTEND-V1-SPEC.md"]
│       completed_at: 2026-08-03T23:40:00Z
│
├── 🟠 FASE 1 — BACKEND
│   ├── ⬜ F1.1 — EWMA Engine + Baseline endpoint
│   │   children: ["F1.1a", "F1.1b"]
│   │   done_criterion: GET /baseline/{home_id} retorna EWMA semanal por cômodo
│   │   params: {α: 0.2, threshold: 2σ, window_days: 7}
│   │
│   │   ├── ⬜ F1.1a — ewma_engine.py
│   │   │   done_criterion: Classe BaselineEngine com calc_baseline() e detect_anomaly()
│   │   │   implementation_ref: ["backend/app/services/ewma_engine.py"]
│   │   │
│   │   └── ⬜ F1.1b — GET /baseline/{home_id}
│   │       done_criterion: Endpoint registrado no router, responde 200
│   │       implementation_ref: ["backend/app/routers/baseline.py"]
│   │
│   └── ⬜ F1.2 — Deploy backend no Railway
│       done_criterion: GitHub push → Railway auto-deploy → /baseline/home-001 200
│       depends_on: ["F1.1"]
│
├── 🟢 FASE 2 — FRONT-END
│   ├── 🔄 F2.1 — CSS Design System (variables.css)
│   │   status: in_progress
│   │   done_criterion: Paleta, tipografia, spacing, radius definidos
│   │   implementation_ref: ["dashboard/v2/css/variables.css"]
│   │
│   ├── ⬜ F2.2 — Floor Plan (CSS Grid + JS)
│   │   done_criterion: 5 cômodos + sensores + dots pulsantes
│   │   implementation_ref: ["dashboard/v2/css/floor-plan.css", "dashboard/v2/js/floor-plan.js"]
│   │   depends_on: ["F2.1"]
│   │
│   ├── ⬜ F2.3 — Narrative Timeline
│   │   done_criterion: Eventos do dia agrupados por período (madrugada/manhã/tarde/noite)
│   │   implementation_ref: ["dashboard/v2/css/timeline.css", "dashboard/v2/js/timeline.js"]
│   │   depends_on: ["F2.1"]
│   │
│   ├── ⬜ F2.4 — Baseline Weekly Chart
│   │   done_criterion: Gráfico semanal real vs baseline por cômodo
│   │   implementation_ref: ["dashboard/v2/css/baseline.css", "dashboard/v2/js/baseline.js"]
│   │   depends_on: ["F1.2", "F2.1"]
│   │
│   ├── ⬜ F2.5 — Care Network
│   │   done_criterion: Cards de contatos com nome, nível, canal, status
│   │   implementation_ref: ["dashboard/v2/css/care-network.css", "dashboard/v2/js/care-network.js"]
│   │   depends_on: ["F2.1"]
│   │
│   ├── ⬜ F2.6 — Onboarding Wizard
│   │   done_criterion: Wizard 4 passos funcional
│   │   implementation_ref: ["dashboard/v2/css/wizard.css", "dashboard/v2/js/wizard.js"]
│   │   depends_on: ["F2.1"]
│   │
│   ├── ⬜ F2.7 — Responsive + App Shell
│   │   done_criterion: Router (?home=), state, responsive breakpoints
│   │   implementation_ref: ["dashboard/v2/css/responsive.css", "dashboard/v2/js/app.js", "dashboard/v2/js/api.js", "dashboard/v2/index.html"]
│   │   depends_on: ["F2.2", "F2.3", "F2.5"]
│   │
│   └── ⬜ F2.8 — Integrate Baseline Chart
│       done_criterion: Baseline chart integrado no index.html
│       depends_on: ["F2.4", "F2.7"]
│
├── 🔵 FASE 3 — DEPLOY + VERIFY
│   ├── ⬜ F3.1 — Deploy no Railway (static files via FastAPI)
│   │   done_criterion: dashboard/v2/ acessível em /v2/
│   │   implementation_ref: ["backend/app/main.py (StaticFiles mount)"]
│   │   depends_on: ["F2.8", "F1.2"]
│   │
│   └── ⬜ F3.2 — Verify-Outcome (score ≥95)
│       done_criterion: Todos endpoints 200, front-end carrega, 5 cômodos visíveis
│       depends_on: ["F3.1"]
│
└── 🟣 FASE 4 — PÓS-DEPLOY
    ├── ⬜ F4.1 — Seed 5 casas PoC
    ├── ⬜ F4.2 — Testar com ESP32 + VL53L0X
    ├── ⬜ F4.3 — Feedback do Eduardo
    └── ⬜ F4.4 — Pitch deck com screenshot
```

## 📊 DEPENDÊNCIAS

```
F0.1 → F0.2 → F0.3
                  ↓
F1.1a ─┬─ F1.1 ── F1.2 ──────────────┐
F1.1b ─┘                               │
                                       ▼
F2.1 ─┬─ F2.2 ─┐              F2.4 ────┤
      ├─ F2.3 ─┤                        │
      ├─ F2.5 ─┼─ F2.7 ── F2.8 ── F3.1 ── F3.2
      └─ F2.6 ─┘
```

## ⏱️ TIMELINE

| Fase | Duração | Paralelizável |
|------|---------|---------------|
| F0 | 1h | Não |
| F1 | 2-3h | F1.1a + F1.1b sim |
| F2 | 4-6h | F2.2..F2.6 sim após F2.1 |
| F3 | 30min | Não |
| **Total** | **7-10h** | — |
