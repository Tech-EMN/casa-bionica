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
│   ├── ✅ F1.1 — EWMA Engine + Baseline endpoint
│   │   status: completed
│   │   children: ["F1.1a", "F1.1b"]
│   │   done_criterion: GET /baseline/{home_id} retorna EWMA semanal por cômodo — testado live
│   │   implementation_ref: ["backend/app/services/ewma_engine.py",
│   │                         "backend/app/routers/baseline.py"]
│   │   completed_at: 2026-08-03T23:45:00Z
│   │   params: {α: 0.2, threshold: 2σ, window_days: 7}
│   │
│   │   ├── ✅ F1.1a — ewma_engine.py
│   │   │   status: completed
│   │   │   done_criterion: BaselineEngine class with calc_baseline() and detect_anomaly() — 218 lines
│   │   │   implementation_ref: ["backend/app/services/ewma_engine.py"]
│   │   │   completed_at: 2026-08-03T23:45:00Z
│   │   │
│   │   └── ✅ F1.1b — GET /baseline/{home_id}
│   │       status: completed
│   │       done_criterion: Endpoint live — retorna rooms + anomalies_today
│   │       implementation_ref: ["backend/app/routers/baseline.py"]
│   │       completed_at: 2026-08-03T23:45:00Z
│   │
│   └── ✅ F1.2 — Deploy backend no Railway
│       status: completed
│       done_criterion: GitHub push master → Railway auto-deploy → /baseline/home-001 200
│       implementation_ref: ["https://github.com/Tech-EMN/casa-bionica/commit/b9ab2ef",
│                             "https://backend-production-607f.up.railway.app/baseline/home-001"]
│       completed_at: 2026-08-03T23:50:00Z
│       depends_on: ["F1.1"]
│
├── 🟢 FASE 2 — FRONT-END
│   ├── ✅ F2.1 — CSS Design System (variables.css)
│   │   status: completed
│   │   done_criterion: Paleta terracota, Fredoka+Outfit, spacing tokens
│   │   implementation_ref: ["dashboard/v2/css/variables.css"]
│   │   completed_at: 2026-08-03T23:40:00Z
│   │
│   ├── ✅ F2.2 — Floor Plan (CSS Grid + JS)
│   │   status: completed
│   │   done_criterion: 5 cômodos + sensores com dots pulsantes + elderly profile
│   │   implementation_ref: ["dashboard/v2/css/floor-plan.css", "dashboard/v2/js/floor-plan.js"]
│   │   completed_at: 2026-08-03T23:42:00Z
│   │   depends_on: ["F2.1"]
│   │
│   ├── ✅ F2.3 — Narrative Timeline
│   │   status: completed
│   │   done_criterion: Eventos do dia agrupados por período com stagger animation
│   │   implementation_ref: ["dashboard/v2/css/timeline.css", "dashboard/v2/js/timeline.js"]
│   │   completed_at: 2026-08-03T23:43:00Z
│   │   depends_on: ["F2.1"]
│   │
│   ├── ✅ F2.4 — Baseline Weekly Chart
│   │   status: completed
│   │   done_criterion: Heatmap semanal com room selector e deviation badges
│   │   implementation_ref: ["dashboard/v2/css/baseline.css", "dashboard/v2/js/baseline.js"]
│   │   completed_at: 2026-08-03T23:44:00Z
│   │   depends_on: ["F1.2", "F2.1"]
│   │
│   ├── ✅ F2.5 — Care Network
│   │   status: completed
│   │   done_criterion: Cards de contatos com nível, canal, status
│   │   implementation_ref: ["dashboard/v2/css/care-network.css", "dashboard/v2/js/care-network.js"]
│   │   completed_at: 2026-08-03T23:44:00Z
│   │   depends_on: ["F2.1"]
│   │
│   ├── ✅ F2.6 — Onboarding Wizard
│   │   status: completed
│   │   done_criterion: Wizard 4 passos com step dots e form fields
│   │   implementation_ref: ["dashboard/v2/css/wizard.css", "dashboard/v2/js/wizard.js"]
│   │   completed_at: 2026-08-03T23:45:00Z
│   │   depends_on: ["F2.1"]
│   │
│   ├── ✅ F2.7 — Responsive + App Shell
│   │   status: completed
│   │   done_criterion: Router (?home=), state management, responsive 3 breakpoints
│   │   implementation_ref: ["dashboard/v2/css/responsive.css", "dashboard/v2/js/app.js",
│   │                          "dashboard/v2/js/api.js", "dashboard/v2/js/utils.js",
│   │                          "dashboard/v2/index.html"]
│   │   completed_at: 2026-08-03T23:46:00Z
│   │   depends_on: ["F2.2", "F2.3", "F2.5"]
│   │
│   └── ✅ F2.8 — Integrate Baseline Chart
│       status: completed
│       done_criterion: Baseline chart integrado no app shell, graceful degradation se offline
│       implementation_ref: ["dashboard/v2/js/app.js (linha _loadBaseline)"]
│       completed_at: 2026-08-03T23:50:00Z
│       depends_on: ["F2.4", "F2.7"]
│
├── 🔵 FASE 3 — DEPLOY + VERIFY
│   ├── ✅ F3.1 — Deploy no Railway (static files via FastAPI)
│   │   status: completed
│   │   done_criterion: dashboard/v2/ acessível em /v2/ — HTTP 200 confirmado
│   │   implementation_ref: ["backend/app/main.py (StaticFiles mount)",
│   │                          "https://backend-production-607f.up.railway.app/v2/",
│   │                          "GitHub: commit b9ab2ef push master → Railway auto-deploy"]
│   │   completed_at: 2026-08-03T23:50:00Z
│   │   depends_on: ["F2.8", "F1.2"]
│   │
│   └── ✅ F3.2 — Verify-Outcome (score ≥95)
│       status: completed
│       done_criterion: 5/5 endpoints OK, front-end 200, baseline engine funcional
│       implementation_ref: ["06-LOGS/data/verify-outcome-casa-bionica-v1.jsonl"]
│       completed_at: 2026-08-03T23:55:00Z
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
