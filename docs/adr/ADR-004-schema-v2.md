# ADR-004 — Schema v2 (9 Tabelas)

**Status:** ✅ Aceito  
**Data:** 2026-08-02  
**Decisores:** Daedalus (AG01), Eduardo Nunes (sponsor)

---

## Contexto

O schema v1 (asyncpg + SQLAlchemy) tinha 4 tabelas e modelagem direta. Durante a migração para PostgREST (ADR-003), o schema foi expandido para cobrir o modelo de negócio completo identificado no requirements-dive, no Design Comercial, e no Premortem.

## Decisão

Schema v2 com 9 tabelas, modelando o domínio completo de monitoramento de idosos:

| Tabela | Propósito | Business Rule |
|--------|-----------|---------------|
| `homes` | Residência monitorada | 1 home = 1 idoso principal |
| `users` | Familiar/operador que acessa o dashboard | N:M com homes via `user_homes` |
| `user_homes` | Relação N:M users↔homes | Familiar pode monitorar múltiplas residências |
| `passages` | Passagem entre cômodos | 1 passagem = 2 sensores VL53L0X + 1 ESP32 |
| `devices` | ESP32-C3 físico | Vinculado a uma passagem e uma home |
| `events` | Evento de travessia (time-series) | entry/exit + distance_mm + timestamp |
| `alerts` | Alerta disparado por anomalia | status: pending→notified→acknowledged→resolved |
| `emergency_contacts` | Contatos de emergência | N1→N2→N3 com escalation_timeout |
| `escalation_log` | Histórico de escalação | Rastreabilidade de quem foi notificado e quando |

## Alternativas Consideradas

- **Schema v1 (4 tabelas):** Rejeitado — não suportava multi-home, multi-contato, nem log de escalação
- **Schema NoSQL (MongoDB):** Rejeitado — time-series events precisam de índices relacionais (joins com homes/devices)

## Consequências

- **Positivo:** Modelo completo cobre S2 (familiar) e S4 (Home Care operator) sem migração
- **Positivo:** `user_homes` permite N:M nativo → multi-residência sem workaround
- **Negativo:** 9 tabelas = 9 endpoints PostgREST para administrar — overhead de manutenção
- **Negativo:** `home_id` como TEXT + UUID (dual key) — débito técnico conhecido (ver auditoria argus §CRITICAL 3)

## Referências

- `backend/alembic/versions/002_full_schema.sql` — DDL completo
- `backend/app/schemas/__init__.py` — Pydantic models
- `docs/adr/ADR-003-postgrest-vs-sqlalchemy.md` — Migração que originou o schema v2
