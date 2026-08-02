# F4 · Restrições e Políticas

> **Fonte:** PARTE V — Workbook "Soluções ATRIA Corp" | Metodologia E1.S6
> **Regra:** Tipos: tecnológica · dado/privacidade · segurança · contratual · orçamentária · política interna.
> A última coluna existe porque restrição já flexibilizada uma vez é negociável, e saber disso muda o espaço de desenho.
> **Extração:** 02/Ago/2026 — Daedalus (AG01)

---

## Restrições Mapeadas

| # | Restrição | Tipo | Autoridade que determinou | Desde | Documentada onde | Exceção já concedida antes? |
|---|-----------|------|--------------------------|-------|-----------------|---------------------------|
| R1 | **NENHUMA câmera no produto** — apenas sensores de presença (booleano). Diferencial competitivo e requisito de privacidade. | dado/privacidade · tecnológica | Eduardo Nunes (CEO) | Concepção do produto (2026) | PRD §NFR01, Design Comercial §Diferencial Competitivo | Não |
| R2 | **NENHUM wearable** — idoso não pode precisar vestir/carregar nada. O sistema deve ser 100% passivo. | tecnológica · política interna | Eduardo Nunes (CEO) | Concepção do produto (2026) | PRD §1 (Visão do Produto), Design Comercial §Posicionamento | Não (BLE tag no idoso como upsell futuro — Fase 3) |
| R3 | **WiFi é pré-requisito obrigatório** — sem chip 4G integrado no MVP. Segmento inicial: classe B+ (idosos com WiFi em casa). | tecnológica · orçamentária | Eduardo Nunes (Decisão Q5, Requirements-Dive) | 02/Ago/2026 | PRD §11 (Q5) | Roadmap: chip 4G como upsell futuro (Kit Pro) |
| R4 | **Custo-alvo do hardware (kit 6 sensores + 1 hub) < R$ 250** | orçamentária | Eduardo Nunes (CEO) | 02/Ago/2026 | PRD §NFR03 (atualizado Q1), Design Comercial §S1 | Não |
| R5 | **Preço de venda S1 (B2C): R$ 299-399** (one-shot) | orçamentária | Design Comercial (Esteira de Valor) | 02/Ago/2026 | Design Comercial §Etapa 3 (S1) | Não |
| R6 | **Sensor instalado acima de ~60cm do chão** — premissa: idoso sem pets no MVP. | tecnológica | Eduardo Nunes (Decisão Q8, Requirements-Dive) | 02/Ago/2026 | PRD §11 (Q8) | Não (suporte a pets em versão futura) |
| R7 | **LGPD — consentimento explícito do idoso e familiar** para coleta de dados de telemetria. Dados anonimizados para S3 (dashboard seguradoras). | dado/privacidade · contratual | Legislação brasileira (LGPD) | 2020 (lei) | PRD §NFR01, §11 (Q11) | Não |
| R8 | **1 idoso por residência no MVP** — casal de idosos NÃO é ICP. Exceção: casal onde um sai com frequência. | política interna | Eduardo Nunes (Decisão Q6, Requirements-Dive) | 02/Ago/2026 | PRD §11 (Q6) | Parcial: casal com um ausente é exceção aceita |
| R9 | **Bateria dos sensores ≥ 12 meses** (CR2032 ou similar). Hub conectado à tomada com consumo < 5W. | tecnológica | PRD §NFR02 | 02/Ago/2026 | PRD §NFR02 | Não |
| R10 | **Sem certificação ANVISA no protótipo** — fora do escopo da Fase 1. | contratual · regulatória | PRD §9 (Fora do Escopo) | 02/Ago/2026 | PRD §9 | Não (necessária para produção comercial) |
| R11 | **Buffer local de 24h no hub** — se WiFi cair, eventos são armazenados localmente com backfill na reconexão. Alerta se offline > 15 min. | tecnológica | PRD §RF05 | 02/Ago/2026 | PRD §RF05 | Não |
| R12 | **Opt-in explícito para coleta de dados (S3)** — desde dia 1, com consentimento LGPD. Dataset anonimizado é ativo estratégico para tese de investimento. | dado/privacidade · política interna | Eduardo Nunes (Decisão Q11, Requirements-Dive) | 02/Ago/2026 | PRD §11 (Q11) | Não |

---

## Restrições do Cliente (a preencher em E06/E10)

| # | Restrição | Tipo | Autoridade que determinou | Desde | Documentada onde | Exceção já concedida antes? |
|---|-----------|------|--------------------------|-------|-----------------|---------------------------|
| C1 | A preencher | | | | | |
| C2 | A preencher | | | | | |
| C3 | A preencher | | | | | |

---

## Análise de Flexibilidade

Restrições já flexibilizadas ou com caminho de flexibilização conhecido:

| # | Restrição original | Flexibilização | Impacto no design |
|---|-------------------|----------------|-------------------|
| R3 | WiFi obrigatório | Chip 4G como upsell (Kit Pro) no roadmap | Mesma arquitetura, hardware adicional |
| R8 | 1 idoso por residência | Casal com um ausente é exceção aceita | Baseline multi-pessoa é complexo — postergado |
| R2 | Sem wearable | BLE tag no idoso como upsell (Fase 3) | Adiciona complexidade de identificação individual |

---

## Notas

- **Restrição R1 (sem câmera) e R2 (sem wearable)** são os pilares do posicionamento competitivo. Flexibilizá-las descaracteriza o produto.
- **Restrição R4 (custo < R$250)** é o principal constraint de engenharia. Acima disso, o preço de venda S1 perde competitividade vs analogs internacionais.
- **Restrição R7 (LGPD)** é imutável. A arquitetura de dados deve prever anonimização desde o ingest.
- **Exceção já concedida = negociável.** Coluna crítica para E16 (sessão de tradeoff): se uma restrição já foi flexibilizada antes, o espaço de design se expande naquele ponto.

---

## Ratificação

| Campo | Valor |
|-------|-------|
| **Preenchido por** | Daedalus (AG01) com base em PRD v1.1, Design Comercial v1.0 e Requirements-Dive Q1-Q12 |
| **Data de extração** | 02/Ago/2026 |
| **Fonte** | Workbook "Soluções ATRIA Corp" — PARTE V + PRD Casa Biônica v1.1 |
| **Ratificado por** | ______ em __/__/____ |
| **Confiança** | R1-R12: VERIFICADO (documentos-fonte ATRIA). Restrições do cliente: a preencher |
