# HANDOFF — Daedalus (AG01) — 2026-08-03T03:10:00Z

**Tipo:** inter-stage (E04 Kickoff → Walking Skeleton Day 1)
**Projeto:** Casa Biônica (PRJ-033) **Árvore:** `projects/casa-bionica/PLANNING-TREE.md` **Nó atual:** E04 concluído, E05 pendente

---

## 1. Objetivo imediato

Transformar o Casa Biônica de conceito (PRD + Design Comercial) em Walking Skeleton funcional: backend online, schema criado, firmware pronto para upload, documentação auditada. **Alcançado.** Backend responde em `backend-production-607f.up.railway.app`, 4 endpoints verificados com `POST /ingest → 201`.

---

## 2. Posição na árvore

- **Nó current:** E04 (Workshop de Kickoff) — ✅ **done** (6 rodadas de decisão, 03/Ago)
- **Próximo nó:** E05 (Coleta e Classificação de Itens de Entrada) — ⬜ **pending**
- **Plano:** `projects/casa-bionica/PLANNING-TREE.md` (pipeline E01-E20 completo, 312 linhas)

---

## 3. Decisões desta sessão

| # | Decisão | Aprovada por | Data |
|---|---------|-------------|------|
| 1 | Walking Skeleton = sistema end-to-end 7 dias em 1 apto real (opção B) | Eduardo | 02/Ago |
| 2 | 4 passagens monitoradas + 1 entrada (opção C, Q10=C) | Eduardo | 02/Ago |
| 3 | Eduardo como simulador → familiar 65+ na PoC (opção B→C) | Eduardo | 02/Ago |
| 4 | Stack backend: Python 3.12 + FastAPI (AX 7.7) | Daedalus, ratificado Eduardo | 02/Ago |
| 5 | Infra: Railway + Supabase Postgres (AX 8.4) | Eduardo (escolheu B) | 02/Ago |
| 6 | PostgREST REST API em vez de SQLAlchemy direto (ADR-003) | Forçado por restrição técnica | 02/Ago |
| 7 | HTTP POST direto ESP32→Backend (ADR-002) | Daedalus, validado por Organizational-Lightness | 02/Ago |
| 8 | Schema v2 — 9 tabelas projetadas com 10 perguntas de negócio | Eduardo (respondeu 10 Qs) | 03/Ago |
| 9 | 1 idoso/residência (Q1=A), multi-residência para familiar (Q8=B) | Eduardo | 03/Ago |
| 10 | SAMU como último nível de escalação (Q4=C) | Eduardo | 03/Ago |

---

## 4. Progresso

| Item | Status |
|------|:---:|
| E04 Kickoff — 6 rodadas de múltipla escolha | ✅ concluído |
| Stack backend definida (AX scoring completo) | ✅ concluído |
| Infraestrutura (GitHub + Railway + Supabase) | ✅ concluído |
| Backend v2.1.0 online — todos endpoints respondendo | ✅ concluído |
| Schema v2 — 9 tabelas + seed data (home-001) | ✅ concluído |
| Firmware ESP32-C3 (sensor.ino, 226 linhas) | ✅ enviado |
| Exemplo C++ simplificado (70 linhas, NTP) | ✅ enviado |
| Documentação (README, CANON, CONTEXT, ADRs, Stress Test 27/36) | ✅ concluído |
| Verify-Outcome (Score 96/100) | ✅ concluído |
| E05 — Coleta e Classificação de Itens de Entrada | ⬜ pendente |
| E06 — Oficina de Domínio (R1) | ⬜ pendente |
| Firmware ESP32 — upload e teste real com VL53L0X | ⬜ pendente (Eduardo) |
| IMPLEMENTATION-SEED.md — atualizar para refletir PostgREST | ⬜ pendente |

---

## 5. Itens pendentes

- **E05** — Classificar itens de entrada (RF01-RF05, NFR01-NFR05, US01-US05 do PRD) como C0-C5
- **Firmware** — Eduardo precisa gravar o sensor.ino nos 4 ESP32-C3 e testar travessia real
- **IMPLEMENTATION-SEED.md** — ainda descreve stack asyncpg/SQLAlchemy. Atualizar para PostgREST v2.1.0
- **Baseline EWMA** — código existe (ewma_engine.py) mas foi removido na migração PostgREST. Precisa ser reimplementado sobre a API REST
- **Notificação** — endpoint existe mas notifier não implementado (Walking Skeleton não precisa)
- **Dashboard** — `dashboard/index.html` existe mas não foi testado contra os endpoints v2

---

## 6. Arquivos-chave

- **Modificados (últimos 10):**
  - `docs/adr/ADR-003-postgrest-vs-sqlalchemy.md`
  - `docs/adr/ADR-002-protocolo-sensor.md`
  - `CONTEXT.md`
  - `README.md`
  - `backend/app/services/ingest_service.py`
  - `backend/app/routers/status.py`
  - `backend/app/routers/events.py`
  - `backend/app/routers/ingest.py`
  - `backend/app/schemas/__init__.py`
  - `backend/app/main.py`

- **Lidos repetidamente:**
  - `_canon/integrations/atria/canon.json` (integrações Railway, Supabase, GitHub)
  - `skills/AX-stack-choosing/SKILL.md` (framework de decisão de stack)
  - `skills/medical-protocol/SKILL.md` (diagnóstico de 3 falhas de build)
  - `skills/organizational-lightness/SKILL.md` (lean schema design)
  - `skills/requirements-dive/SKILL.md` (10 perguntas de negócio)

- **Criados (27 arquivos):**
  - `README.md`, `CANON.md`, `CONTEXT.md`, `PLANNING-TREE.md`
  - `arquitetura/AX-DECISION.md`, `STACK-DECISION.md`, `REFERENCIAS-projetos.md`, `IMPLEMENTATION-SEED.md`
  - `docs/adr/ADR-002-protocolo-sensor.md`, `docs/adr/ADR-003-postgrest-vs-sqlalchemy.md`
  - `formularios/F2-contexto-objetivo.md`, `F3-inventario-sistemas.md`, `F4-restricoes-politicas.md`, `README.md`
  - `backend/` (Dockerfile, requirements.txt, 10 arquivos Python, SQL migration)
  - `firmware/sensor/sensor.ino`, `dashboard/index.html`
  - `.env.example`, `railway.toml`, `.gitignore`

---

## 7. Ferramentas/Integrações em uso

| Ferramenta | Propósito | Última verificação |
|-----------|-----------|-------------------|
| **GitHub** (`Tech-EMN/casa-bionica`) | Repo principal, auto-deploy trigger | 03/Ago 03:05 UTC |
| **Railway** (`df9dee3e`) | Backend hosting, `backend-production-607f.up.railway.app` | 03/Ago 03:05 UTC |
| **Supabase** (`rkiclxviqinciwwumwfb`) | PostgreSQL + PostgREST, sa-east-1, 9 tabelas | 03/Ago 03:05 UTC |
| **Supabase PAT** (`sbp_4ff…`) | DDL via Management API | Funcional |
| **Railway Project Token** (`73c0c2…`) | ⚠️ Expirou/revogado após deploy | Indisponível |
| **Railway Account Token** (`c928fd…`) | ❌ Morto — retorna Not Authorized | Indisponível |

---

## 8. Stack (AX) + regras de negócio ativas

**Stack:** Python 3.12 + FastAPI + httpx + Supabase PostgREST REST API (v2.1.0-postgrest)

**Regras de negócio (10 perguntas Requirements-Dive):**
- Q1=A: 1 idoso/residência
- Q2: Contatos podem repetir entre residências (denormalizado por home)
- Q3=A: Escalação sequencial (N1→N2→N3) com timeout
- Q4=C: SAMU como último nível (tabela `escalation_log`)
- Q5=A: Qualquer contato pode resolver alerta
- Q6=B: Sensores relocáveis (tabela `passages` separada)
- Q7=A: Dados mantidos indefinidamente
- Q8=B: Familiar pode monitorar múltiplas residências (N:M `user_homes`)
- Q9=A: 1 canal por contato (phone direto)
- Q10=C: Sensor de entrada para presença (`passage_type=entrance`)

---

## 9. Instruções de retomada

1. **Ler este HANDOFF.md** — todas as decisões e estado estão aqui
2. **Verificar backend:** `curl https://backend-production-607f.up.railway.app/health` deve retornar `{"status":"ok"}`
3. **Perguntar a Eduardo:**
   - "Conseguiu gravar o firmware nos ESP32? As travessias estão chegando no backend?"
   - "Quer prosseguir com E05 (classificação de itens) ou pular direto para testar o hardware?"
4. **Se hardware ok:** Prosseguir para E06 (Oficina de Domínio) usando o roteiro R1 da PARTE V do workbook
5. **Se hardware com problema:** Debugar firmware ESP32 — verificar WiFi, NTP, formato JSON, URL
6. **Pendências de código:** Reimplementar EWMA baseline engine sobre PostgREST, atualizar IMPLEMENTATION-SEED.md

---

## 10. Notas de honestidade

- ✅ **Verificado:** Backend online, todos endpoints HTTP 200/201. Supabase 9 tabelas com seed data. GitHub push up-to-date. Verify-Outcome 96/100. Railway auto-deploy funcional (último commit 2baf60f).
- ✅ **Verificado:** `POST /ingest` com sensor-quarto-01 → 201 Created, evento aparece em `GET /events`. Testado com curl do servidor.
- ⚠️ **Inferido:** Railway GitHub auto-deploy funciona (confirmado pelo version bump v0.1.0→v0.2.0→v2.1.0), mas o mecanismo exato de trigger não foi inspecionado — pode ser webhook ou polling.
- ⚠️ **Inferido:** Supabase free tier inclui backups diários automáticos — NÃO verificado. Assumido como true para risco baixo no Walking Skeleton.
- ❓ **Incerto:** O token Railway projeto (`73c0c2…`) falhou em queries após o deploy final. Não se sabe se foi revogado, expirado, ou se o escopo mudou. Account token (`c928fd…`) está morto desde o início da sessão. **Retomar: pedir novo token a Eduardo se precisar de acesso via API.**
- ❓ **Incerto:** IMPLEMENTATION-SEED.md ainda referencia asyncpg/SQLAlchemy. Não atualizado porque a decisão de mantê-lo como "histórico" vs "atualizado" não foi tomada. Retomar: perguntar a Eduardo se atualiza ou arquiva.
- ❓ **Incerto:** O firmware sensor.ino NÃO foi testado em hardware real. A state machine e o HTTP POST foram validados apenas via curl. Retomar: primeiro teste real com ESP32-C3 + VL53L0X.
