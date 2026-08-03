# FRONTEND-V1-SPEC.md — Casa Biônica "Raízes"

> **Versão:** 1.0 | **Data:** 2026-08-03
> **Decisões:** Q1-Q8 | **Skills:** anti-slop-design, requirements-dive

---

## 1. Visão

Dashboard de monitoramento de idosos. A casa do idoso É a interface.
Zero cards abstratos. Planta baixa com sensores pulsantes + timeline narrativa.

**Usuário:** Familiar (filho/a, 40-55 anos) — quer resposta rápida: "está tudo bem?"
**Tom:** Casa, não hospital. Quente, humano, acolhedor.
**Diferencial:** Nenhum concorrente usa a planta da casa como interface principal.

---

## 2. Stack

| Camada | Escolha | Justificativa |
|--------|---------|---------------|
| HTML | Vanilla HTML5 | Zero dependências |
| CSS | CSS Grid + Custom Properties | Planta da casa como grid |
| JS | Vanilla ES6 | 5 componentes, <50KB bundle |
| Fontes | Fredoka (headings) + Outfit (body) | Google Fonts, 2 pesos cada |
| Deploy | FastAPI StaticFiles mount | `/v2/` no Railway |

---

## 3. Paleta & Design Tokens

```css
:root {
  --color-bg:       #faf7f2;    /* papel quente */
  --color-surface:  #ffffff;
  --color-text:     #1a1815;
  --color-muted:    #8c8279;
  --color-accent:   #c7745e;    /* terracota */
  --color-accent2:  #5b8c5a;    /* verde-musgo (normal) */
  --color-warning:  #e8a838;    /* âmbar (atenção) */
  --color-danger:   #c75050;    /* vermelho suave (alerta) */
  --color-border:   #e8e0d5;

  --font-display:   'Fredoka', sans-serif;
  --font-body:      'Outfit', sans-serif;

  --radius-sm:      8px;
  --radius-md:      16px;
  --radius-lg:      24px;

  --space-xs:       4px;
  --space-sm:       8px;
  --space-md:       16px;
  --space-lg:       24px;
  --space-xl:       40px;
}
```

---

## 4. Componentes

### 4.1 FloorPlan (CSS Grid)
- Grid 4×3 com áreas nomeadas: `quarto`, `banheiro`, `cozinha`, `sala`, `corredor`, `entrada`
- Cada cômodo = `grid-area` com borda arredondada, cor de fundo, label
- Sensores = dots (◉) posicionados nas passagens entre cômodos
- Último evento = dot pulsa com animação CSS `@keyframes pulse`
- Foto do idoso + nome + status dentro do cômodo atual
- Dados: `GET /status/{home_id}` → `devices[]`, `last_event`, `presence`

### 4.2 NarrativeTimeline
- Seções: madrugada (0-6h), manhã (6-12h), tarde (12-18h), noite (18-24h)
- Cada evento = timestamp, emoji do cômodo, descrição, duração, barra proporcional
- Baseline indicator: ✅ normal, ⚠ acima do normal, 🔴 crítico
- Dados: `GET /events?home_id=&from=&limit=50`

### 4.3 BaselineWeekly
- Tabela/heatmap: linhas = cômodos, colunas = dias da semana (Seg..Dom)
- Dois indicadores por célula: real (barra preenchida) + baseline (barra vazada)
- Desvios >2σ marcados com ⚠
- Dados: `GET /baseline/{home_id}` (PROPOSTO — F1.1)

### 4.4 CareNetwork
- Cards horizontais: nome, relação, nível (N1/N2/N3), canal (📱), status (🟢/🟡)
- Indicador de timeout: "após 60min inativo"
- Botão "+ Adicionar Contato"
- Dados: `GET /status/{home_id}` → `emergency_contacts[]`

### 4.5 OnboardingWizard (modal)
- Step 1: Dados do idoso (nome, idade, foto)
- Step 2: Endereço + planta da casa (selecionar template)
- Step 3: Contatos de emergência
- Step 4: Pareamento de sensores (QR code)
- Dados: POST via Supabase PostgREST (INFERIDO)

---

## 5. Endpoints (EBI)

| Endpoint | Método | Status | Usado por |
|----------|--------|--------|-----------|
| `/health` | GET | ✅ VERIFICADO | App shell (health check) |
| `/status/{home_id}` | GET | ✅ VERIFICADO | FloorPlan, CareNetwork |
| `/events?home_id=&from=&limit=` | GET | ✅ VERIFICADO | NarrativeTimeline |
| `/presence/{home_id}` | GET | ✅ VERIFICADO | FloorPlan (presence indicator) |
| `/baseline/{home_id}` | GET | 📋 PROPOSTO | BaselineWeekly |
| `/ingest` | POST | ✅ VERIFICADO | OnboardingWizard (debug inject) |

---

## 6. Estrutura de Arquivos

```
dashboard/v2/
├── index.html
├── css/
│   ├── variables.css
│   ├── floor-plan.css
│   ├── timeline.css
│   ├── baseline.css
│   ├── care-network.css
│   ├── wizard.css
│   └── responsive.css
├── js/
│   ├── app.js
│   ├── api.js
│   ├── floor-plan.js
│   ├── timeline.js
│   ├── baseline.js
│   ├── care-network.js
│   ├── wizard.js
│   └── utils.js
└── assets/
```

---

## 7. Responsividade

| Breakpoint | Layout |
|------------|--------|
| < 640px (mobile) | Coluna única: planta → timeline → baseline → contatos |
| 640-1024px (tablet) | Planta + timeline lado a lado |
| > 1024px (desktop) | Grid 2-col: planta (60%) + (timeline + baseline + contatos) (40%) |

---

## 8. Anti-Slop Checklist

- [x] Fonte NÃO é Inter (Fredoka + Outfit)
- [x] Sem gradiente roxo no hero
- [x] Layout com assimetria intencional (grid irregular da planta)
- [x] Paleta: 1 dominante quente + accent terracota
- [x] Animações com propósito (pulse no sensor ativo, stagger na timeline)
- [x] Sem box-shadow default
- [x] Whitespace generoso, bordas mínimas
