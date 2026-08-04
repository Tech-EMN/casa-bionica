# Casa Biônica — Deploy & Manutenção

> **Última atualização:** 2026-08-04

## Deploy (Automático via Railway)

```bash
cd projects/casa-bionica
git add -A
git commit -m "descrição da mudança"
git push origin master
# → Railway detecta push no branch master → auto-deploy
```

**Tempo típico de deploy:** 60-90 segundos após o push.

**Verificação pós-deploy:**
```bash
curl -s https://backend-production-607f.up.railway.app/health
curl -s https://backend-production-607f.up.railway.app/v2/
```

## Ambiente

| Variável | Valor | Onde |
|----------|-------|------|
| `SUPABASE_URL` | `https://rkiclxviqinciwwumwfb.supabase.co` | Railway env |
| `SUPABASE_KEY` | `***` (service_role) | Railway env (secret) |
| `HOME_ID` | `home-001` | Railway env |
| `APP_ENV` | `production` | Railway env |
| `PORT` | `8000` | Railway auto |

## Supabase

- **Projeto:** `rkiclxviqinciwwumwfb` (sa-east-1)
- **Dashboard:** https://supabase.com/dashboard/project/rkiclxviqinciwwumwfb
- **API docs:** https://rkiclxviqinciwwumwfb.supabase.co/rest/v1/

### Atualizar dados manualmente

```bash
# Via Management API (PAT)
curl -X POST "https://api.supabase.com/v1/projects/rkiclxviqinciwwumwfb/database/query" \
  -H "Authorization: Bearer $SUPABASE_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "UPDATE homes SET elderly_name = '"'"'Nome'"'"' WHERE home_id = '"'"'home-001'"'"';"}'

# Via Admin endpoint (mais simples)
curl -X PATCH "https://backend-production-607f.up.railway.app/admin/homes/home-001" \
  -H "Content-Type: application/json" \
  -d '{"elderly_name":"Novo Nome"}'
```

## Diagrama de Infra

```
GitHub (master) → Railway (FastAPI + static files)
                      ├── GET /v2/ → dashboard SPA
                      ├── POST /ingest → grava no Supabase
                      └── GET /status, /events, /baseline → lê do Supabase
                                                           ↓
                                              Supabase PostgREST (sa-east-1)
```

## Backup

- **Código:** GitHub (histórico completo de commits)
- **Dados:** Supabase (backups automáticos, retenção 7 dias no plano gratuito)
- **Config:** Railway env vars (persistem entre deploys)
