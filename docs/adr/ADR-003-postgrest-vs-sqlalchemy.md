# ADR-003 — PostgREST REST API em vez de SQLAlchemy Direto

- **Status:** Aceito
- **Data:** 03/Ago/2026
- **Decisor:** Daedalus (AG01), forçado por restrição técnica

---

## Contexto

O backend precisa persistir eventos de travessia no Supabase. A stack original (IMPLEMENTATION-SEED.md) previa SQLAlchemy + asyncpg para conexão direta ao PostgreSQL. A implementação revelou 3 falhas consecutivas que forçaram a migração para PostgREST REST API.

## Falhas Encontradas (Medical Protocol)

| # | Falha | Causa Raiz |
|---|-------|-----------|
| 1 | `asyncpg` não conecta ao Supabase | Supabase usa SNI-based routing; asyncpg não envia `tenant identifier` |
| 2 | `psycopg2` não conecta via Railway | `db.rkiclxviqinciwwumwfb.supabase.co` resolve SOMENTE para IPv6; Railway containers não alcançam IPv6 |
| 3 | Pooler Supabase (porta 6543) rejeita `psycopg2` | Pooler exige tenant identifier via SNI; `psycopg2` não customiza SNI via `hostaddr` |

## Alternativas Consideradas

| Abordagem | Vantagem | Desvantagem | Veredito |
|-----------|----------|-------------|:---:|
| **A) SQLAlchemy + asyncpg** | ORM completo, migrations | Incompatível com Supabase SNI | ❌ Falhou |
| **B) SQLAlchemy + psycopg2** | Síncrono, compatível com `psql` | Railway sem IPv6 → unreachable | ❌ Falhou |
| **C) Pooler Supabase + psycopg2** | IPv4 via pooler | SNI routing não suportado pelo driver | ❌ Falhou |
| **D) PostgREST REST API** | HTTPS porta 443, IPv4 nativo | Sem ORM, queries manuais | ✅ Funcionou |

## Decisão

**Opção D — Supabase PostgREST REST API via `httpx`.**

### Justificativa

1. **Funciona:** Única opção que conectou. `https://rkiclxviqinciwwumwfb.supabase.co` resolve para IPv4 (104.18.38.10 via Cloudflare) — Railway alcança.
2. **Simplicidade:** 7 dependências vs 30. Docker image ~100MB vs ~300MB. Sem `libpq-dev`, sem `asyncpg`, sem `psycopg2`.
3. **Escala:** PostgREST suporta joins aninhados (`select=devices(passages(name))`), filtros (`eq.`, `in.`, `gte.`), ordenação. Suficiente para MVP.

### Consequências

- ✅ Conexão estável (IPv4, HTTPS)
- ✅ Setup simplificado (sem drivers de banco)
- ✅ Segurança (API key, não senha de banco)
- ❌ Sem ORM — queries são strings
- ❌ Sem migrations automáticas (Alembic)
- ❌ Lógica de negócio no Python (não em stored procedures)

---

## Referências

- Railway build logs (02/Ago/2026): `ENOIDENTIFIER`, `Network is unreachable`
- Supabase IPv6-only: `dig AAAA db.rkiclxviqinciwwumwfb.supabase.co` → `2600:1f11:d68:...`
- Supabase IPv4 pooler: `dig A aws-0-sa-east-1.pooler.supabase.com` → `54.94.90.106`
- PostgREST test: `curl https://rkiclxviqinciwwumwfb.supabase.co/rest/v1/crossing_events` → `200 OK`
- ADR-001: Stack decision (Python + FastAPI, AX 7.7)
