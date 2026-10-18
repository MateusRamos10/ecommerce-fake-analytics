# Plano de ExecuÃ§Ã£o: E-commerce Fake de EletrÃ´nicos para PortfÃ³lio de Web Analytics

> Documento para ser entregue a uma IA executora com acesso aos ambientes via MCP (GitHub, Vercel, GTM, GA4, BigQuery, Looker Studio).
> A ordem das fases Ã© obrigatÃ³ria. NÃ£o pule fases e nÃ£o popule o BigQuery antes da Fase 8.

---

## 1. Objetivo

Construir um e-commerce fake de **eletrÃ´nicos**, minimalista, para um portfÃ³lio de anÃ¡lise de dados e web analytics. O projeto gera dados prÃ³prios (reais, via navegador automatizado, e histÃ³ricos, via carga direta) para sustentar dois estudos:

1. **Checkout Abandonment** (funil de compra e pontos de abandono)
2. **Cohort Analysis** (retenÃ§Ã£o de usuÃ¡rios ao longo do tempo)

AlÃ©m de dados comuns de e-commerce (receita, produtos, canais, dispositivos).

Todo o projeto deve usar apenas serviÃ§os **gratuitos**.

---

## 2. Stack e decisÃµes fechadas

| Camada | DecisÃ£o |
|---|---|
| CÃ³digo | **GitHub, repositÃ³rio privado** (ninguÃ©m faz fork; quem quiser replicar entra em contato com o autor) |
| Hospedagem do site | **Vercel**, conectado ao GitHub |
| Coleta | **Google Tag Manager** + **GA4** |
| Armazenamento/anÃ¡lise | **BigQuery** (exportaÃ§Ã£o diÃ¡ria do GA4, modo sandbox/gratuito) |
| Dashboard | **Looker Studio** |
| Simulador de trÃ¡fego | **Playwright em Python**, executado no **GitHub Actions** com agendamento (`schedule`) |
| Estado dos usuÃ¡rios simulados | **Arquivo JSON em branch dedicado** (`state`), com commit a cada execuÃ§Ã£o |
| Carga histÃ³rica | **Script Python** que gera 1 ano de dados direto no BigQuery |
| VPS (OCI A1.Flex, 4 OCPUs, 24 GB) | **NÃ£o Ã© usada.** Fica como plano B se o GitHub Actions limitar algo |

### DecisÃµes de comportamento

- O site Ã© **estÃ¡tico e minimalista**, com poucas pÃ¡ginas e poucos produtos.
- A pÃ¡gina de pagamento simula cartÃ£o com **campos travados** (somente leitura). O cartÃ£o fixo Ã© `6100 6311 5623 1213`. O usuÃ¡rio nÃ£o edita os dados, mas o evento de pagamento Ã© registrado.
- Todo acesso ao site exibe um **pop-up** avisando que Ã© um e-commerce fake de portfÃ³lio, mais um **disclaimer fixo no rodapÃ©**.
- **Toda interaÃ§Ã£o humana** (do autor ou de qualquer visitante) tambÃ©m Ã© registrada. Um parÃ¢metro diferencia humano de simulado.
- O Playwright roda "para sempre", sem depender de mÃ¡quina ligada.
- Os dados histÃ³ricos **nunca** vÃ£o para o GA4 (o Measurement Protocol sÃ³ aceita atÃ© 72h no passado). Eles vÃ£o direto para o BigQuery, separados dos dados reais.

---

## 3. Arquitetura (visÃ£o geral)

```
[GitHub privado] --deploy--> [Vercel: loja fake]
                                   |
                                   v dataLayer
                              [GTM] ---> [GA4] --exportaÃ§Ã£o diÃ¡ria--> [BigQuery: dataset ga4 (dados reais)]
                                   ^                                          |
[GitHub Actions + Playwright] -----+ (navega no site de verdade)               |
        |                                                                      v
        +--> branch "state" (JSON com usuÃ¡rios agendados para retornar)   [view unificada] --> [Looker Studio]
                                                                               ^
[Script de carga histÃ³rica 1 ano] --> [BigQuery: dataset historical] ----------+
```

---

## 4. Regras para a IA executora

1. Execute as fases na ordem. Ao fim de cada fase, valide os critÃ©rios de conclusÃ£o antes de avanÃ§ar.
2. Nunca grave segredos no cÃ³digo. IDs e credenciais ficam em **GitHub Secrets** (Actions) e variÃ¡veis de ambiente da Vercel.
3. Quando uma etapa exigir aÃ§Ã£o manual do autor (criar conta, aprovar permissÃ£o, vincular serviÃ§o sem suporte via MCP), pare e liste exatamente o que o autor precisa fazer.
4. **NÃ£o popule o BigQuery com dados histÃ³ricos antes da Fase 8.** O esquema deve ser copiado do que o GA4 realmente exportar.
5. Dados histÃ³ricos ficam em dataset separado e marcados como simulados.
6. Documente cada decisÃ£o no README conforme avanÃ§a.
7. Se algo contradizer este plano (ex.: limite de plano, API indisponÃ­vel), informe e proponha alternativa antes de seguir.

---

## 5. DefiniÃ§Ãµes de negÃ³cio e de mediÃ§Ã£o

### 5.1 Perguntas de negÃ³cio

**Checkout abandonment**
- Em qual etapa do funil os usuÃ¡rios mais abandonam?
- Como a taxa de abandono varia por dispositivo, canal (origem/mÃ­dia), tipo de usuÃ¡rio e dia/Ã©poca do ano?
- Qual o valor mÃ©dio dos carrinhos abandonados e a receita potencial perdida?
- Quais produtos/categorias sÃ£o mais abandonados?

**Cohort analysis**
- Qual a retenÃ§Ã£o de usuÃ¡rios nos dias 1, 3 e 7 (e semanas seguintes) por coorte de primeira visita?
- A retenÃ§Ã£o varia por canal de aquisiÃ§Ã£o?
- Qual a receita acumulada por coorte? Quantos compram em dias diferentes?
- UsuÃ¡rios recorrentes convertem mais que novos?

**Gerais**
- Receita por canal, produtos mais vistos vs. comprados, comportamento por dispositivo, impacto da sazonalidade.

### 5.2 Eventos do dataLayer (padrÃ£o GA4 e-commerce, com objeto `items`)

Funil e navegaÃ§Ã£o:
- `view_item_list`
- `select_item`
- `view_item`
- `add_to_cart`
- `view_cart`
- `begin_checkout`
- `add_shipping_info`
- `add_payment_info`
- `purchase` (com `transaction_id`, `value`, `currency`, `items`)

UsuÃ¡rio:
- `login` (login simulado, define `user_id`)
- `sign_up` (opcional, para marcar cadastro)

### 5.3 ParÃ¢metros extras (customizados)

| ParÃ¢metro | FunÃ§Ã£o |
|---|---|
| `traffic_type` | `human`, `simulated` ou `historical_simulated` |
| `env` | `prod` ou `dev` (para separar testes) |
| `abandonment_stage` | Etapa em que o usuÃ¡rio parou (ex.: `cart`, `begin_checkout`, `shipping`, `payment`) |
| `user_type` | `new` ou `returning` |
| `device_profile` | Perfil de dispositivo usado na simulaÃ§Ã£o |
| `cart_value` | Valor do carrinho na etapa (quando Ãºtil) |

### 5.4 Dados necessÃ¡rios para os dois estudos

**Checkout abandonment:** eventos de cada etapa do funil; valor do carrinho, itens e categoria por etapa; dispositivo; origem/mÃ­dia (UTMs); tipo de usuÃ¡rio; parÃ¢metro de etapa de abandono.

**Cohort analysis:** identificador persistente (`client_id`/`user_pseudo_id`, mais `user_id` simulado apÃ³s login); data da primeira visita e dos retornos; compras em dias diferentes; origem de aquisiÃ§Ã£o.

### 5.5 CatÃ¡logo

- 10 a 15 produtos de **eletrÃ´nicos**, em poucas categorias (sugestÃ£o: Celulares, Notebooks, Ãudio, AcessÃ³rios, Casa Inteligente).
- PreÃ§os variados (ex.: de R$ 49 a R$ 6.000) para gerar carrinhos de valores diferentes.
- Moeda: BRL.

---

## 6. Fases de implementaÃ§Ã£o

### Fase 0: PreparaÃ§Ã£o do repositÃ³rio e acessos

**Tarefas**
- Criar repositÃ³rio **privado** no GitHub com a estrutura da seÃ§Ã£o 7.
- Criar branch `state` (vazio, sÃ³ com `state.json` inicial).
- Conectar o repositÃ³rio Ã  Vercel.
- Confirmar acesso via MCP a: GitHub, Vercel, GTM, GA4, BigQuery, Looker Studio. Listar o que nÃ£o estÃ¡ disponÃ­vel.
- Criar projeto no Google Cloud (BigQuery sandbox) e service account para as cargas e consultas.

**ConcluÃ­da quando:** a IA consegue ler/escrever no repositÃ³rio, publicar na Vercel e consultar o BigQuery.

---

### Fase 1: Planejamento e plano de mediÃ§Ã£o

**Tarefas**
- Registrar no README as perguntas de negÃ³cio (5.1).
- Fechar o catÃ¡logo (5.5) em um arquivo `products.json`.
- Escrever o **plano de mediÃ§Ã£o** (`docs/measurement-plan.md`): cada evento, parÃ¢metros, quando dispara e em qual pÃ¡gina.

**ConcluÃ­da quando:** o plano de mediÃ§Ã£o estÃ¡ versionado e cobre todos os eventos de 5.2 e parÃ¢metros de 5.3.

---

### Fase 2: Site fake (loja de eletrÃ´nicos)

**PÃ¡ginas**
1. Home / listagem de produtos
2. PÃ¡gina de produto
3. Carrinho
4. Checkout (dados de entrega)
5. Pagamento (campos de cartÃ£o travados, `6100 6311 5623 1213`)
6. ConfirmaÃ§Ã£o de compra
7. Login simulado (gera `user_id`)

**Requisitos**
- HTML/JS estÃ¡tico, minimalista, responsivo (mobile e desktop).
- **Pop-up de aviso** em toda entrada no site ("e-commerce fake de portfÃ³lio") e **disclaimer no rodapÃ©** de todas as pÃ¡ginas.
- O pop-up nÃ£o deve bloquear a automaÃ§Ã£o: o botÃ£o de fechar precisa ter seletor estÃ¡vel (ex.: `data-testid`), e o Playwright fecha o aviso a cada sessÃ£o.
- Atributos `data-testid` nos elementos principais para o Playwright (botÃµes de comprar, carrinho, checkout, pagar).
- Estado do carrinho no navegador (sem backend).
- O campo `env` deve vir de configuraÃ§Ã£o, e o `traffic_type` ser definido como `human` por padrÃ£o (o Playwright o sobrescreve para `simulated`, ver Fase 6).

**ConcluÃ­da quando:** Ã© possÃ­vel navegar de ponta a ponta (home atÃ© confirmaÃ§Ã£o) manualmente e o site estÃ¡ publicado na Vercel.

---

### Fase 3: ImplementaÃ§Ã£o do dataLayer

**Tarefas**
- Implementar o `dataLayer.push` de todos os eventos de 5.2, com `items` completo (`item_id`, `item_name`, `item_category`, `price`, `quantity`).
- Incluir os parÃ¢metros extras de 5.3.
- Sinalizador de trÃ¡fego: o site lÃª um marcador (ex.: parÃ¢metro de URL, cookie ou variÃ¡vel injetada pelo Playwright) para definir `traffic_type = simulated`; sem marcador, assume `human`.
- Registrar `abandonment_stage` conforme a Ãºltima etapa alcanÃ§ada (detectada quando o usuÃ¡rio sai ou quando a sessÃ£o simulada termina).
- Validar no console do navegador.

**ConcluÃ­da quando:** cada aÃ§Ã£o do usuÃ¡rio gera o evento correto no `dataLayer`, com todos os parÃ¢metros.

---

### Fase 4: ConfiguraÃ§Ã£o do GTM

**Tarefas**
- Instalar o snippet do contÃªiner no site.
- Criar variÃ¡veis de dataLayer, acionadores (um por evento) e tags de evento GA4 com parÃ¢metros mapeados.
- Tag de configuraÃ§Ã£o do GA4 com o ID de mediÃ§Ã£o.
- Validar no modo **Preview**.
- Publicar o contÃªiner e **exportar o JSON** para `gtm/container.json` no repositÃ³rio.

**ConcluÃ­da quando:** todos os eventos aparecem no Preview com parÃ¢metros corretos e o JSON do contÃªiner estÃ¡ versionado.

---

### Fase 5: ConfiguraÃ§Ã£o do GA4

**Tarefas**
- Criar propriedade e fluxo de dados web.
- Marcar `purchase` como **evento-chave**.
- Criar **dimensÃµes personalizadas** (escopo de evento/usuÃ¡rio): `traffic_type`, `env`, `abandonment_stage`, `user_type`, `device_profile`.
- Configurar **filtro de trÃ¡fego interno/teste** (ex.: filtrar `env=dev`) e ativÃ¡-lo apÃ³s validar.
- Validar no **DebugView** e em Tempo real.
- Vincular ao **BigQuery** com exportaÃ§Ã£o **diÃ¡ria** (criar o dataset em regiÃ£o adequada, sugestÃ£o `US` ou `southamerica-east1`; usar a mesma regiÃ£o nos datasets histÃ³ricos).
- Ativar a exportaÃ§Ã£o de usuÃ¡rios/pseudonimizaÃ§Ã£o apenas se necessÃ¡rio.

**ConcluÃ­da quando:** eventos aparecem no GA4 e o link com o BigQuery estÃ¡ ativo.

> AtenÃ§Ã£o: a primeira tabela exportada pode levar atÃ© ~24h para aparecer. A Fase 8 sÃ³ comeÃ§a depois disso.

---

### Fase 6: Simulador de trÃ¡fego (Playwright + Python)

**Comportamento**
- **Volume:** 6 sessÃµes por dia em perÃ­odo normal; **10 sessÃµes por dia** em Ã©pocas sazonais.
- **HorÃ¡rios aleatÃ³rios:** o workflow agenda disparos em janelas espalhadas ao longo do dia e o script sorteia se roda naquela janela e com qual atraso, de modo que o total diÃ¡rio seja respeitado e os horÃ¡rios nÃ£o sejam fixos. Pesos maiores para horÃ¡rios de pico (almoÃ§o e noite).
- **Sazonalidade (aumentar volume e conversÃ£o):** Dia do Consumidor (15/03), Dia das MÃ£es (maio), Dia dos Namorados (12/06), Dia dos Pais (agosto), Black Friday (novembro), Natal (dezembro). CalendÃ¡rio em arquivo de configuraÃ§Ã£o editÃ¡vel.
- **Fluxo de navegaÃ§Ã£o:** abrir o site, fechar o pop-up, navegar pela listagem, visualizar produto, adicionar ao carrinho, ver carrinho, iniciar checkout, entrega, pagamento e, quando for o caso, concluir a compra.
- **Abandono (foco do estudo):** a taxa-base Ã© de **~70% de abandono de quem chega ao `begin_checkout`** e **~30% de compra**, mas a taxa **oscila por dia, dispositivo e canal** (nÃ£o pode ser exatamente 70% sempre). Abandonos ocorrem em etapas variadas (`cart`, `begin_checkout`, `shipping`, `payment`). SessÃµes tambÃ©m podem abandonar antes do checkout (sÃ³ vendo produtos).
- **VariaÃ§Ãµes:** UTMs (orgÃ¢nico, direto, e-mail, redes sociais, anÃºncios pagos), perfis de dispositivo (desktop e mobile, viewports e user agents de navegadores comuns), tempo entre aÃ§Ãµes com variaÃ§Ã£o humana.
- **MarcaÃ§Ã£o:** toda sessÃ£o simulada define `traffic_type = simulated` e `env = prod`.

**RetenÃ§Ã£o realista (coorte)**
- Cada sessÃ£o de **novo usuÃ¡rio** comeÃ§a sem cookies e cria um usuÃ¡rio novo.
- **Apenas uma pequena parte** dos usuÃ¡rios Ã© agendada para voltar. NÃ£o replicar todos.
- Retornos aproximadamente nos dias **1, 3 e 7**, com variaÃ§Ã£o de Â±1 dia, e a probabilidade de retorno decrescente (mais gente volta no dia 1 que no dia 7). A taxa varia por canal de aquisiÃ§Ã£o.
- UsuÃ¡rios que retornam usam o **`storage_state`** salvo (cookies, incluindo `_ga`), mantendo o mesmo `client_id`. Retornantes tÃªm chance maior de comprar.
- Compras em dias diferentes para o mesmo usuÃ¡rio (para receita por coorte).
- Quem nÃ£o estÃ¡ agendado "some" do estado, como visitantes reais.

**Estado (branch `state`)**
- `state.json` guarda apenas os usuÃ¡rios agendados: identificador interno, `storage_state`, data da primeira visita, datas previstas de retorno, canal de aquisiÃ§Ã£o, histÃ³rico mÃ­nimo.
- A cada execuÃ§Ã£o, o workflow faz checkout do branch `state`, o script lÃª/atualiza o JSON e o workflow faz **commit** do resultado.
- Remover entradas expiradas (retornos jÃ¡ realizados ou passados da janela de 7 dias).
- O commit periÃ³dico tambÃ©m garante atividade no repositÃ³rio.
- **Controle de concorrÃªncia** (`concurrency` no workflow) para evitar duas execuÃ§Ãµes simultÃ¢neas escrevendo no mesmo estado.

**GitHub Actions**
- Workflow com `schedule` (cron em UTC, lembrando que pode atrasar alguns minutos) e `workflow_dispatch` para disparo manual.
- Setup do Python, instalaÃ§Ã£o do Playwright e do Chromium, execuÃ§Ã£o em modo headless.
- Garantir `browser.close()` e timeout por sessÃ£o.
- **OrÃ§amento de minutos (repo privado, 2.000 min/mÃªs grÃ¡tis):** 10 execuÃ§Ãµes/dia Ã— 2 a 3 min = ~600 a 900 min/mÃªs. Monitorar e ajustar se aproximar do limite. Usar cache de dependÃªncias para reduzir o tempo de setup.
- Secrets: URL do site, ID do GA4/GTM quando necessÃ¡rio.

**LimitaÃ§Ãµes a documentar:** IP de datacenter do GitHub (geografia pobre e pouco variada), GA4 pode filtrar trÃ¡fego com aparÃªncia de robÃ´ (configurar navegador comum e conferir), volume baixo.

**ConcluÃ­da quando:** o workflow roda sozinho, os eventos de sessÃµes simuladas aparecem no GA4 (DebugView/Tempo real), o estado persiste no branch `state` e um usuÃ¡rio agendado retorna com o mesmo `client_id`.

---

### Fase 7: OperaÃ§Ã£o contÃ­nua e monitoramento

**Tarefas**
- Deixar o workflow rodando por **pelo menos 2 semanas** antes de seguir para a anÃ¡lise (8 dias Ã© o mÃ­nimo para existir a coorte do dia 7).
- Criar um **workflow de verificaÃ§Ã£o** (ou alerta simples) que avise se o nÃºmero de sessÃµes do dia ficou abaixo do esperado ou se o workflow falhou.
- Acompanhar o consumo de minutos do GitHub Actions.
- Conferir se as tabelas diÃ¡rias `events_YYYYMMDD` estÃ£o sendo geradas no BigQuery.

**ConcluÃ­da quando:** hÃ¡ pelo menos 8 a 14 dias de dados reais no BigQuery sem falhas relevantes.

---

### Fase 8: InspeÃ§Ã£o do esquema real do GA4 no BigQuery

**Esta fase vem antes de qualquer carga histÃ³rica.**

**Tarefas**
- Via MCP, listar as tabelas do dataset exportado pelo GA4 (`events_YYYYMMDD`, e `events_intraday_*` se existir).
- Extrair o **esquema completo** (campos, tipos, `STRUCT`s e `REPEATED`): `event_date`, `event_timestamp`, `event_name`, `event_params`, `user_properties`, `user_pseudo_id`, `user_id`, `device`, `geo`, `traffic_source`, `collected_traffic_source`, `session_traffic_source_last_click`, `items`, `ecommerce` etc.
- Analisar **dados reais**: como `ga_session_id`, `ga_session_number`, `session_engagement_time`, `page_location`, `engagement_time_msec` e os parÃ¢metros customizados aparecem; como eventos automÃ¡ticos (`first_visit`, `session_start`, `user_engagement`, `page_view`) se comportam.
- Documentar o esquema e as particularidades em `docs/ga4-schema.md`.
- Medir proporÃ§Ãµes reais para calibrar o gerador (eventos por sessÃ£o, tempo entre eventos, distribuiÃ§Ã£o de dispositivos).

**ConcluÃ­da quando:** `docs/ga4-schema.md` descreve o esquema real e as regras de preenchimento observadas.

---

### Fase 9: Carga histÃ³rica de 1 ano no BigQuery

**SÃ³ executar depois da Fase 8.**

**Regras**
- Gerar **12 meses** de dados anteriores ao inÃ­cio dos dados reais, sem sobreposiÃ§Ã£o de datas com as tabelas do GA4.
- Gravar em **dataset separado** (ex.: `ga4_historical`), com **tabelas por dia** (`events_YYYYMMDD`) e **esquema idÃªntico** ao do GA4 (Fase 8).
- Marcar todos os eventos com `traffic_type = historical_simulated` (em `event_params`) para separaÃ§Ã£o nas anÃ¡lises.
- **Sazonalidade:** volume maior nos perÃ­odos sazonais (seÃ§Ã£o 6, Fase 6), com crescimento gradual ao longo do ano e variaÃ§Ã£o por dia da semana.
- **Mesma lÃ³gica do Playwright:** taxa de abandono ~70% com oscilaÃ§Ã£o por dia/dispositivo/canal, abandono em etapas variadas, UTMs, dispositivos.
- **Coortes:** usuÃ¡rios com `user_pseudo_id` estÃ¡vel, retornos aproximados nos dias 1, 3 e 7 (decrescentes e variÃ¡veis por canal), compras em dias distintos.
- **ConsistÃªncia interna:** `event_timestamp` em microssegundos coerente com `event_date`; `ga_session_id` (timestamp do inÃ­cio da sessÃ£o) coerente entre eventos; `ga_session_number` incrementando; sequÃªncia de eventos lÃ³gica (`view_item` antes de `add_to_cart` etc.); `purchase` com `transaction_id` Ãºnico e `value` igual Ã  soma dos itens; eventos automÃ¡ticos (`first_visit`, `session_start`, `page_view`) gerados como o GA4 faz.
- Carga via `load job` em lotes (nÃ£o por inserÃ§Ã£o linha a linha), em modo sandbox sem custos de streaming.
- Script reexecutÃ¡vel (idempotente): rodar de novo substitui as tabelas histÃ³ricas sem duplicar.

**ConcluÃ­da quando:** o dataset histÃ³rico tem 12 meses contÃ­nuos, o esquema bate com o do GA4 e consultas de validaÃ§Ã£o (contagem por dia, funil, retenÃ§Ã£o) retornam valores plausÃ­veis.

---

### Fase 10: View unificada e modelagem

**Tarefas**
- Criar uma **view** que une `ga4.events_*` (real) e `ga4_historical.events_*` (histÃ³rico), expondo uma coluna `data_source` (`real` ou `historical`) e o `traffic_type`.
- Criar views/tabelas derivadas para facilitar o Looker:
  - `sessions` (uma linha por `user_pseudo_id` + `ga_session_id`, com canal, dispositivo, etapa mÃ¡xima do funil, valor)
  - `funnel_steps`
  - `purchases`
  - `user_first_visit` (coorte por data da primeira visita)
- Garantir que filtros por `traffic_type` e `data_source` funcionem (humano, simulado, histÃ³rico).

**ConcluÃ­da quando:** as views retornam dados dos dois datasets e as consultas de teste batem com contagens manuais.

---

### Fase 11: AnÃ¡lise em SQL

**Checkout abandonment**
- Funil por etapa: `view_item` â†’ `add_to_cart` â†’ `begin_checkout` â†’ `add_shipping_info` â†’ `add_payment_info` â†’ `purchase`, com taxa de conversÃ£o e abandono entre etapas.
- Abandono por dispositivo, canal, tipo de usuÃ¡rio, categoria de produto e Ã©poca do ano.
- Valor mÃ©dio do carrinho abandonado e receita perdida.

**Cohort analysis**
- RetenÃ§Ã£o por coorte de primeira visita nos dias 1, 3 e 7 (e por semana).
- RetenÃ§Ã£o por canal de aquisiÃ§Ã£o.
- Receita acumulada por coorte e recorrÃªncia de compra.

**Gerais**
- Receita por canal, produtos mais vistos vs. comprados, sazonalidade (receita e sessÃµes por mÃªs/semana).

Salvar as consultas em `sql/` com comentÃ¡rios.

**ConcluÃ­da quando:** cada pergunta da seÃ§Ã£o 5.1 tem uma consulta que a responde.

---

### Fase 12: Dashboard no Looker Studio

**PÃ¡ginas sugeridas**
1. VisÃ£o geral (receita, sessÃµes, conversÃ£o, sazonalidade)
2. Funil de checkout e abandono (por etapa, dispositivo e canal)
3. RetenÃ§Ã£o por coorte (matriz de coortes)
4. Produtos e categorias

**Regras**
- Fonte de dados: as views do BigQuery (Fase 10).
- Filtros de `data_source` e `traffic_type`.
- Nota visÃ­vel no dashboard informando que os dados sÃ£o simulados.

Se o MCP nÃ£o permitir criar o relatÃ³rio do Looker, a IA entrega as consultas/views prontas e um roteiro passo a passo para o autor montar as pÃ¡ginas manualmente.

**ConcluÃ­da quando:** o dashboard responde Ã s perguntas de negÃ³cio e estÃ¡ compartilhÃ¡vel (visualizaÃ§Ã£o).

---

### Fase 13: DocumentaÃ§Ã£o e portfÃ³lio

**Tarefas**
- README com arquitetura (diagrama da seÃ§Ã£o 3), plano de mediÃ§Ã£o, lÃ³gica da simulaÃ§Ã£o, passos para operar o projeto e estrutura do repositÃ³rio.
- SeÃ§Ã£o de **limitaÃ§Ãµes**: dados simulados, IP Ãºnico de datacenter, volume baixo no trÃ¡fego real, histÃ³rico fora do GA4.
- SeÃ§Ã£o de **como replicar**: o repositÃ³rio Ã© privado e quem quiser replicar deve entrar em contato com o autor.
- Case com **insights** e prints do dashboard.
- Registro das decisÃµes e dos dados simulados (transparÃªncia sobre o que Ã© real e o que Ã© histÃ³rico gerado).

**ConcluÃ­da quando:** uma pessoa externa entende o projeto e consegue avaliar o resultado sÃ³ lendo o README e o dashboard.

---

## 7. Estrutura sugerida do repositÃ³rio

```
/
â”œâ”€â”€ site/                     # loja fake (HTML/JS estÃ¡tico, publicada na Vercel)
â”‚   â”œâ”€â”€ index.html, produto, carrinho, checkout, pagamento, confirmacao, login
â”‚   â”œâ”€â”€ products.json
â”‚   â””â”€â”€ assets/
â”œâ”€â”€ gtm/
â”‚   â””â”€â”€ container.json        # contÃªiner exportado
â”œâ”€â”€ simulator/
â”‚   â”œâ”€â”€ main.py               # orquestra as sessÃµes do dia
â”‚   â”œâ”€â”€ sessions.py           # fluxo de navegaÃ§Ã£o e abandono
â”‚   â”œâ”€â”€ profiles.py           # perfis de dispositivo, canais e UTMs
â”‚   â”œâ”€â”€ state.py              # leitura/escrita do state.json
â”‚   â”œâ”€â”€ seasonality.json      # calendÃ¡rio sazonal e volumes
â”‚   â””â”€â”€ requirements.txt
â”œâ”€â”€ historical/
â”‚   â”œâ”€â”€ generate.py           # gerador de 1 ano (sÃ³ apÃ³s Fase 8)
â”‚   â””â”€â”€ config.json
â”œâ”€â”€ sql/                      # views e anÃ¡lises
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ measurement-plan.md
â”‚   â””â”€â”€ ga4-schema.md
â”œâ”€â”€ .github/workflows/
â”‚   â”œâ”€â”€ simulate.yml          # agendamento do Playwright
â”‚   â””â”€â”€ healthcheck.yml       # verificaÃ§Ã£o de execuÃ§Ã£o
â”œâ”€â”€ .env.example
â””â”€â”€ README.md
```

Branch dedicado: `state` (contÃ©m apenas `state.json`).

---

## 8. Riscos e pontos de atenÃ§Ã£o

| Risco | MitigaÃ§Ã£o |
|---|---|
| GA4 filtrar trÃ¡fego com aparÃªncia de robÃ´ | Navegador com user agent comum, comportamento humano, conferir nos primeiros testes |
| Perda do estado quebra a coorte | Estado versionado no branch `state` (commit a cada execuÃ§Ã£o), com `concurrency` |
| Estouro de minutos do GitHub Actions (2.000/mÃªs) | Cache de dependÃªncias, monitorar consumo, ajustar volume sazonal |
| Agendamento do Actions atrasar ou falhar | Healthcheck e execuÃ§Ã£o manual (`workflow_dispatch`) |
| HistÃ³rico sobrepor dados reais | Dataset separado, datas sem sobreposiÃ§Ã£o, coluna `data_source` |
| Esquema histÃ³rico divergir do real | Fase 8 obrigatÃ³ria antes da Fase 9 |
| Testes poluÃ­rem a anÃ¡lise | `env=dev` e filtro no GA4 |
| TrÃ¡fego humano misturado ao simulado | `traffic_type` em todos os eventos |
| Dados de um Ãºnico IP | Documentar como limitaÃ§Ã£o |
| Primeira exportaÃ§Ã£o do GA4 demorar | Aguardar atÃ© ~24h apÃ³s o link com o BigQuery |

---

## 9. Ordem resumida (checklist)

1. [x] Fase 0: RepositÃ³rio, branch `state`, Vercel, acessos MCP, projeto no Google Cloud
2. [x] Fase 1: Perguntas, catÃ¡logo, plano de mediÃ§Ã£o
3. [x] Fase 2: Site fake com pop-up e rodapÃ©
4. [ ] Fase 3: dataLayer
5. [ ] Fase 4: GTM (e export do JSON)
6. [ ] Fase 5: GA4 (dimensÃµes, filtros, link com BigQuery)
7. [ ] Fase 6: Simulador Playwright + Actions + estado
8. [ ] Fase 7: Operar 2+ semanas e monitorar
9. [ ] Fase 8: Inspecionar o esquema real do GA4 no BigQuery
10. [ ] Fase 9: Carga histÃ³rica de 1 ano no BigQuery
11. [ ] Fase 10: View unificada e modelagem
12. [ ] Fase 11: AnÃ¡lises em SQL
13. [ ] Fase 12: Dashboard no Looker Studio
14. [ ] Fase 13: DocumentaÃ§Ã£o e case de portfÃ³lio

---

## 10. SuposiÃ§Ãµes assumidas (confirmar com o autor se necessÃ¡rio)

- 6 sessÃµes/dia Ã© o volume normal e 10 sessÃµes/dia o volume sazonal.
- Taxa-base de 70% de abandono no `begin_checkout` e 30% de compra, com oscilaÃ§Ã£o.
- Moeda BRL e calendÃ¡rio sazonal brasileiro.
- ExportaÃ§Ã£o do GA4 para o BigQuery em modo **diÃ¡rio** (gratuito), sem streaming.
- A pessoa autora cria as contas e aprova permissÃµes que o MCP nÃ£o consiga executar.
