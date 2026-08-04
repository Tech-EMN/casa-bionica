# Casa Biônica — Troubleshooting & Runbook

> **Última atualização:** 2026-08-04

## Cenários

### C1 — Dashboard não carrega (loading infinito)

**Sintoma:** Tela "Carregando..." por mais de 10 segundos.

**Causa provável:** Erro de JavaScript silencioso (ex: syntax error em arquivo .js).

**Diagnóstico:**
```bash
# 1. Abrir DevTools (F12) → Console → ver erros em vermelho
# 2. Verificar Network tab → procurar 404/500 em chamadas API
# 3. Verificar syntax dos JS files:
node -c dashboard/v2/js/*.js
```

**Correção:** Corrigir o erro de sintaxe, `git push master` → Railway auto-deploy.

---

### C2 — API retorna 500

**Sintoma:** `/status/home-001` retorna erro interno.

**Causas possíveis:**
- Supabase offline ou quota excedida
- Variável de ambiente `SUPABASE_KEY` ausente no Railway

**Diagnóstico:**
```bash
curl -s https://backend-production-607f.up.railway.app/health
curl -s https://backend-production-607f.up.railway.app/status/home-001
```

**Correção:**
- Verificar [Supabase Dashboard](https://supabase.com/dashboard/project/rkiclxviqinciwwumwfb) → status
- Verificar [Railway Dashboard](https://railway.app) → variáveis de ambiente

---

### C3 — Baseline não calcula

**Sintoma:** `/baseline/home-001` retorna rooms vazio.

**Causa:** Menos de 2 eventos por sensor (EWMA precisa de par entry/exit).

**Correção:** Aguardar 7 dias de calibração com eventos reais. Se urgente, injetar eventos via:
```bash
curl -X POST https://backend-production-607f.up.railway.app/ingest \
  -H "Content-Type: application/json" \
  -d '{"sensor_id":"sensor-quarto-01","home_id":"home-001","direction":"entry","distance_mm":1050,"event_timestamp":"2026-08-04T12:00:00Z"}'
```

---

### C4 — ESP32 não envia eventos

**Sintoma:** Nenhum evento novo em `GET /events`.

**Diagnóstico:**
1. Verificar WiFi do ESP32 (Serial Monitor)
2. Verificar se `WIFI_SSID` e `WIFI_PASS` estão corretos no firmware
3. Testar endpoint manualmente: `curl -X POST .../ingest`

---

### C5 — Railway deploy falhou

**Sintoma:** `git push` feito mas `/health` retorna versão antiga.

**Diagnóstico:**
1. Verificar [Railway Dashboard](https://railway.app) → Deployments → último log
2. Verificar se `requirements.txt` está atualizado

**Correção:** Forçar redeploy manual no Railway Dashboard.

---

### C6 — Supabase conexão recusada

**Sintoma:** Erro 401 ou timeout nas chamadas PostgREST.

**Diagnóstico:**
```bash
curl -s "https://rkiclxviqinciwwumwfb.supabase.co/rest/v1/homes?limit=1" \
  -H "apikey: $SUPABASE_KEY"
```

**Correção:** Regenerar API key no Supabase Dashboard → atualizar `SUPABASE_KEY` no Railway.

---

### C7 — Dados aparecem desatualizados no dashboard

**Sintoma:** Dashboard mostra eventos antigos.

**Causa:** Polling interval (30s status, 60s timeline). Recarregar a página força refresh imediato.

---

### C8 — Home ID não encontrado

**Sintoma:** `GET /status/home-002` retorna vazio.

**Causa:** `home_id` não existe na tabela `homes`.

**Correção:** Seedar nova home via Supabase Dashboard ou:
```bash
curl -X PATCH "https://backend-production-607f.up.railway.app/admin/homes/home-002" \
  -H "Content-Type: application/json" \
  -d '{"elderly_name":"Novo Idoso","name":"Casa 002"}'
```
