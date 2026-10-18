# volta: Loja Fake de EletrÃ´nicos para Web Analytics

E-commerce **fictÃ­cio** criado para estruturar um projeto de portfÃ³lio completo de **Web Analytics e Engenharia de Dados**. Nenhum produto Ã© vendido e nenhum dado de pagamento Ã© real.

ðŸŒ **Site no ar:** [https://ecommerce-fake-analytics.vercel.app](https://ecommerce-fake-analytics.vercel.app)

---

## 1. Perguntas de NegÃ³cio do Projeto

O projeto coleta dados para responder a dois estudos aprofundados de e-commerce:

### A. Checkout Abandonment (Abandono de Funil)
- Em qual etapa do funil (`cart` â†’ `begin_checkout` â†’ `shipping` â†’ `payment` â†’ `purchase`) os usuÃ¡rios mais abandonam?
- Como a taxa de abandono varia por dispositivo (Desktop vs. Mobile), canal de trÃ¡fego (UTMs) e sazonalidade?
- Qual o valor mÃ©dio monetÃ¡rio dos carrinhos abandonados e o impacto financeiro potencial?
- Quais categorias e produtos sofrem maior Ã­ndice de abandono?

### B. Cohort Analysis (RetenÃ§Ã£o e RecorrÃªncia)
- Qual a taxa de retenÃ§Ã£o nos marcos D1, D3 e D7 (e semanas seguintes) por coorte de primeira visita?
- A retenÃ§Ã£o de clientes varia por canal de aquisiÃ§Ã£o?
- Qual a receita acumulada gerada por cada coorte ao longo do tempo?
- UsuÃ¡rios recorrentes convertem mais que novos visitantes?

---

## 2. Arquitetura da SoluÃ§Ã£o

```
[GitHub Privado] --deploy--> [Vercel: Loja Fake]
                                   |
                                   v dataLayer
                              [GTM] ---> [GA4] --export diÃ¡rio--> [BigQuery: dataset ga4]
                                   ^                                      |
[GitHub Actions + Playwright] -----+ (trÃ¡fego automatizado)                |
        |                                                                 v
        +--> branch "state" (cookies JSON para coortes)            [Views SQL Unificadas] --> [Looker Studio]
                                                                          ^
[Script Carga HistÃ³rica 1 ano] --------> [BigQuery: dataset historical] --+
```

---

## 3. Estrutura do RepositÃ³rio

- `site/`: Arquivos estÃ¡ticos da loja (HTML, CSS, JS, assets) publicados na Vercel.
- `docs/measurement-plan.md`: [Plano de MediÃ§Ã£o detalhado](docs/measurement-plan.md) com eventos, parÃ¢metros e regras.
- `docs/plano-execucao-ecommerce-fake.md`: Plano diretor de execuÃ§Ã£o do portfÃ³lio.
- `simulator/`: RobÃ´ Playwright para automaÃ§Ã£o de trÃ¡fego e simulaÃ§Ã£o de coortes (Fase 6).
- `historical/`: Gerador da carga sintÃ©tica de 1 ano para o BigQuery (Fase 9).
- `sql/`: Views e queries analÃ­ticas de abandono e coorte (Fases 10 e 11).

---

## 4. Rodar Localmente

```bash
cd site
python -m http.server 8000
# Acesse http://localhost:8000
```

