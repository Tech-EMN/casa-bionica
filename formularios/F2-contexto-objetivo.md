# F2 · Contexto e Objetivo

> **Fonte:** PARTE V — Workbook "Soluções ATRIA Corp" | Metodologia E1.S6
> **Regra:** Uma página. Se o cliente precisar de mais de uma, o escopo está aberto demais.
> **Extração:** 02/Ago/2026 — Daedalus (AG01)

---

## 1. Qual processo ou decisão vocês querem que a solução afete?

**Pré-preenchido (PRD + Design Comercial):**

Detecção precoce de quedas de idosos que moram sozinhos, através do monitoramento passivo do tempo de permanência por cômodo. A solução afeta:

- **Processo primário:** Detecção de anomalia de rotina → alerta ao familiar → intervenção rápida
- **Decisão afetada:** O familiar decide se aciona emergência com base em dados objetivos (tempo excedido no cômodo), em vez de ansiedade/incerteza

**A confirmar com cliente:** ___

---

## 2. Como esse processo funciona hoje, em cinco linhas?

**Pré-preenchido (hipótese H1):**

1. Idoso vive sozinho (ou passa a maior parte do dia sozinho)
2. Familiar liga/visita periodicamente para verificar bem-estar
3. Se idoso não atende telefone, familiar se desloca ou pede para vizinho verificar
4. Em caso de queda real ("long lie"), idoso pode ficar horas/dias no chão sem socorro
5. Não há monitoramento contínuo — a detecção depende de falha de contato (reativo, não proativo)

**A confirmar com cliente:** ___

---

## 3. Quantas vezes por dia/mês isso acontece?

**Pré-preenchido:**

- Ocupação de cômodos: múltiplas vezes por dia (cada transição entre cômodos gera evento)
- Evento crítico (anomalia de permanência): estimado < 1/mês por idoso em risco
- Cenário-alvo: detecção de "long lie" — 1 evento pode ser fatal se não detectado

**A confirmar com cliente:** ___

---

## 4. Quanto tempo leva hoje, por ocorrência?

**Pré-preenchido:**

- **Sem sistema:** Tempo de "long lie" típico: 4-72 horas até descoberta
- **Com Casa Biônica (alvo):** Detecção em < 5 minutos após anomalia de permanência
- **Tempo total detecção→alerta:** < 5 segundos (RF04/NFR04)

**A confirmar com cliente:** ___

---

## 5. Quantas pessoas estão envolvidas?

**Pré-preenchido:**

- **Idoso:** 1 (persona primária: P1 "Frágil Solitária", 78+, mora sozinha)
- **Familiar cuidador:** 1-3 (persona secundária: "sandwich generation", 40-55 anos)
- **Contatos de emergência:** 2-3 (escalada N1→N2→N3)
- **Gestor ILPI/Home Care:** N/A na Fase 1 (persona terciária, entra em S4)

**A confirmar com cliente:** ___

---

## 6. O que acontece hoje quando dá errado?

**Pré-preenchido:**

- Idoso cai e não consegue se levantar
- Ninguém percebe por horas (ou dias)
- Sequelas graves: fratura de quadril (mortalidade 20-30% em 1 ano), hipotermia, desidratação, rabdomiólise
- Desfecho fatal em casos extremos (16.345 óbitos por queda em idosos no Brasil em 2024 — SBTO)
- Trauma psicológico permanente no idoso (medo de cair de novo) e no familiar (culpa)

**A confirmar com cliente:** ___

---

## 7. Como vocês vão saber, daqui a seis meses, que valeu a pena?

> ⚠️ **A pergunta 7 é a mais importante do formulário. A resposta vira critério de aceite.**
> Cliente que não consegue respondê-la ainda não tem projeto — tem intenção.

**Pré-preenchido (métricas do PRD):**

- [ ] Protótipo funcional end-to-end: sensor → cloud → notificação em < 5s
- [ ] Precisão de detecção de presença > 90% (sem falsos negativos)
- [ ] Taxa de falsos positivos < 2/dia após calibração de 7 dias
- [ ] Ao menos 1 evento real de "long lie" detectado e socorrido com sucesso
- [ ] Familiar relata redução mensurável de ansiedade (NPS > 50)
- [ ] Idoso aceitou o sistema (não removeu/desligou sensores após 6 meses)

**A confirmar com cliente:** ___

---

## 8. Que prazo existe e por quê? Há data externa (regulatória, contratual, sazonal)?

**Pré-preenchido:**

- **Prototipo:** sem data externa rígida
- **Fase 1 (PoC):** definido no cronograma da planilha Casa-Bionica-Atividades
- **Sazonalidade:** inverno = maior incidência de quedas (idosos mais agasalhados, menor mobilidade)
- **Regulatório:** sem gatilho regulatório imediato (ANVISA apenas para dispositivo médico classe II+, não aplicável ao protótipo)

**A confirmar com cliente:** ___

---

## 9. Isso já foi tentado antes? O que aconteceu?

**Pré-preenchido:**

- **Mercado brasileiro:** Tellus é o concorrente local conhecido (sensores + assinatura, foco ILPI)
- **Mercado internacional:** 15 analogs mapeados (Nobi, Cherry Labs, Vayyar, Alarm.com Wellness, etc.)
- **Tentativas anteriores do cliente:** desconhecido — a confirmar na oficina E06
- **Diferencial Casa Biônica:** passivo (sem câmera, sem wearable), foco em baseline de rotina, baixo custo (R$299 vs R$1.000+)

**A confirmar com cliente:** ___

---

## Ratificação

| Campo | Valor |
|-------|-------|
| **Preenchido por** | Daedalus (AG01) com base em PRD v1.1 e Design Comercial v1.0 |
| **Data de extração** | 02/Ago/2026 |
| **Fonte** | Workbook "Soluções ATRIA Corp" — PARTE V |
| **Ratificado por** | ______ em __/__/____ |
| **Confiança** | Pré-preenchido (a confirmar em E06) |
