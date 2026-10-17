# Plano de Execução: E-commerce Fake de Eletrônicos para Portfólio de Web Analytics

> Documento para ser entregue a uma IA executora com acesso aos ambientes via MCP (GitHub, Vercel, GTM, GA4, BigQuery, Looker Studio).
> A ordem das fases é obrigatória. Não pule fases e não popule o BigQuery antes da Fase 8.

---

## 1. Objetivo

Construir um e-commerce fake de **eletrônicos**, minimalista, para um portfólio de análise de dados e web analytics. O projeto gera dados próprios (reais, via navegador automatizado, e históricos, via carga direta) para sustentar dois estudos:

1. **Checkout Abandonment** (funil de compra e pontos de abandono)
2. **Cohort Analysis** (retenção de usuários ao longo do tempo)

Além de dados comuns de e-commerce (receita, produtos, canais, dispositivos).

Todo o projeto deve usar apenas serviços **gratuitos**.

---

## 2. Stack e decisões fechadas

| Camada | Decisão |
|---|---|
| Código | **GitHub, repositório privado** (ninguém faz fork; quem quiser replicar entra em contato com o autor) |
| Hospedagem do site | **Vercel**, conectado ao GitHub |
| Coleta | **Google Tag Manager** + **GA4** |
| Armazenamento/análise | **BigQuery** (exportação diária do GA4, modo sandbox/gratuito) |
| Dashboard | **Looker Studio** |
| Simulador de tráfego | **Playwright em Python**, executado no **GitHub Actions** com agendamento (`schedule`) |
| Estado dos usuários simulados | **Arquivo JSON em branch dedicado** (`state`), com commit a cada execução |
| Carga histórica | **Script Python** que gera 1 ano de dados direto no BigQuery |
| VPS (OCI A1.Flex, 4 OCPUs, 24 GB) | **Não é usada.** Fica como plano B se o GitHub Actions limitar algo |

### Decisões de comportamento

- O site é **estático e minimalista**, com poucas páginas e poucos produtos.
- A página de pagamento simula cartão com **campos travados** (somente leitura). O cartão fixo é `6100 6311 5623 1213`. O usuário não edita os dados, mas o evento de pagamento é registrado.
- Todo acesso ao site exibe um **pop-up** avisando que é um e-commerce fake de portfólio, mais um **disclaimer fixo no rodapé**.
- **Toda interação humana** (do autor ou de qualquer visitante) também é registrada. Um parâmetro diferencia humano de simulado.
- O Playwright roda "para sempre", sem depender de máquina ligada.
- Os dados históricos **nunca** vão para o GA4 (o Measurement Protocol só aceita até 72h no passado). Eles vão direto para o BigQuery, separados dos dados reais.

---

## 3. Arquitetura (visão geral)

```
[GitHub privado] --deploy--> [Vercel: loja fake]
                                   |
                                   v dataLayer
                              [GTM] ---> [GA4] --exportação diária--> [BigQuery: dataset ga4 (dados reais)]
                                   ^                                          |
[GitHub Actions + Playwright] -----+ (navega no site de verdade)               |
        |                                                                      v
        +--> branch "state" (JSON com usuários agendados para retornar)   [view unificada] --> [Looker Studio]
                                                                               ^
[Script de carga histórica 1 ano] --> [BigQuery: dataset historical] ----------+
```

---

## 4. Regras para a IA executora

1. Execute as fases na ordem. Ao fim de cada fase, valide os critérios de conclusão antes de avançar.
2. Nunca grave segredos no código. IDs e credenciais ficam em **GitHub Secrets** (Actions) e variáveis de ambiente da Vercel.
3. Quando uma etapa exigir ação manual do autor (criar conta, aprovar permissão, vincular serviço sem suporte via MCP), pare e liste exatamente o que o autor precisa fazer.
4. **Não popule o BigQuery com dados históricos antes da Fase 8.** O esquema deve ser copiado do que o GA4 realmente exportar.
5. Dados históricos ficam em dataset separado e marcados como simulados.
6. Documente cada decisão no README conforme avança.
7. Se algo contradizer este plano (ex.: limite de plano, API indisponível), informe e proponha alternativa antes de seguir.

---

## 5. Definições de negócio e de medição

### 5.1 Perguntas de negócio

**Checkout abandonment**
- Em qual etapa do funil os usuários mais abandonam?
- Como a taxa de abandono varia por dispositivo, canal (origem/mídia), tipo de usuário e dia/época do ano?
- Qual o valor médio dos carrinhos abandonados e a receita potencial perdida?
- Quais produtos/categorias são mais abandonados?

**Cohort analysis**
- Qual a retenção de usuários nos dias 1, 3 e 7 (e semanas seguintes) por coorte de primeira visita?
- A retenção varia por canal de aquisição?
- Qual a receita acumulada por coorte? Quantos compram em dias diferentes?
- Usuários recorrentes convertem mais que novos?

**Gerais**
- Receita por canal, produtos mais vistos vs. comprados, comportamento por dispositivo, impacto da sazonalidade.

### 5.2 Eventos do dataLayer (padrão GA4 e-commerce, com objeto `items`)

Funil e navegação:
- `view_item_list`
- `select_item`
- `view_item`
- `add_to_cart`
- `view_cart`
- `begin_checkout`
- `add_shipping_info`
- `add_payment_info`
- `purchase` (com `transaction_id`, `value`, `currency`, `items`)

Usuário:
- `login` (login simulado, define `user_id`)
- `sign_up` (opcional, para marcar cadastro)

### 5.3 Parâmetros extras (customizados)

| Parâmetro | Função |
|---|---|
| `traffic_type` | `human`, `simulated` ou `historical_simulated` |
| `env` | `prod` ou `dev` (para separar testes) |
| `abandonment_stage` | Etapa em que o usuário parou (ex.: `cart`, `begin_checkout`, `shipping`, `payment`) |
| `user_type` | `new` ou `returning` |
| `device_profile` | Perfil de dispositivo usado na simulação |
| `cart_value` | Valor do carrinho na etapa (quando útil) |

### 5.4 Dados necessários para os dois estudos

**Checkout abandonment:** eventos de cada etapa do funil; valor do carrinho, itens e categoria por etapa; dispositivo; origem/mídia (UTMs); tipo de usuário; parâmetro de etapa de abandono.

**Cohort analysis:** identificador persistente (`client_id`/`user_pseudo_id`, mais `user_id` simulado após login); data da primeira visita e dos retornos; compras em dias diferentes; origem de aquisição.

### 5.5 Catálogo

- 10 a 15 produtos de **eletrônicos**, em poucas categorias (sugestão: Celulares, Notebooks, Áudio, Acessórios, Casa Inteligente).
- Preços variados (ex.: de R$ 49 a R$ 6.000) para gerar carrinhos de valores diferentes.
- Moeda: BRL.

---

## 6. Fases de implementação

### Fase 0: Preparação do repositório e acessos

**Tarefas**
- Criar repositório **privado** no GitHub com a estrutura da seção 7.
- Criar branch `state` (vazio, só com `state.json` inicial).
- Conectar o repositório à Vercel.
- Confirmar acesso via MCP a: GitHub, Vercel, GTM, GA4, BigQuery, Looker Studio. Listar o que não está disponível.
- Criar projeto no Google Cloud (BigQuery sandbox) e service account para as cargas e consultas.

**Concluída quando:** a IA consegue ler/escrever no repositório, publicar na Vercel e consultar o BigQuery.

---

### Fase 1: Planejamento e plano de medição

**Tarefas**
- Registrar no README as perguntas de negócio (5.1).
- Fechar o catálogo (5.5) em um arquivo `products.json`.
- Escrever o **plano de medição** (`docs/measurement-plan.md`): cada evento, parâmetros, quando dispara e em qual página.

**Concluída quando:** o plano de medição está versionado e cobre todos os eventos de 5.2 e parâmetros de 5.3.

---

### Fase 2: Site fake (loja de eletrônicos)

**Páginas**
1. Home / listagem de produtos
2. Página de produto
3. Carrinho
4. Checkout (dados de entrega)
5. Pagamento (campos de cartão travados, `6100 6311 5623 1213`)
6. Confirmação de compra
7. Login simulado (gera `user_id`)

**Requisitos**
- HTML/JS estático, minimalista, responsivo (mobile e desktop).
- **Pop-up de aviso** em toda entrada no site ("e-commerce fake de portfólio") e **disclaimer no rodapé** de todas as páginas.
- O pop-up não deve bloquear a automação: o botão de fechar precisa ter seletor estável (ex.: `data-testid`), e o Playwright fecha o aviso a cada sessão.
- Atributos `data-testid` nos elementos principais para o Playwright (botões de comprar, carrinho, checkout, pagar).
- Estado do carrinho no navegador (sem backend).
- O campo `env` deve vir de configuração, e o `traffic_type` ser definido como `human` por padrão (o Playwright o sobrescreve para `simulated`, ver Fase 6).

**Concluída quando:** é possível navegar de ponta a ponta (home até confirmação) manualmente e o site está publicado na Vercel.

---

### Fase 3: Implementação do dataLayer

**Tarefas**
- Implementar o `dataLayer.push` de todos os eventos de 5.2, com `items` completo (`item_id`, `item_name`, `item_category`, `price`, `quantity`).
- Incluir os parâmetros extras de 5.3.
- Sinalizador de tráfego: o site lê um marcador (ex.: parâmetro de URL, cookie ou variável injetada pelo Playwright) para definir `traffic_type = simulated`; sem marcador, assume `human`.
- Registrar `abandonment_stage` conforme a última etapa alcançada (detectada quando o usuário sai ou quando a sessão simulada termina).
- Validar no console do navegador.

**Concluída quando:** cada ação do usuário gera o evento correto no `dataLayer`, com todos os parâmetros.

---

### Fase 4: Configuração do GTM

**Tarefas**
- Instalar o snippet do contêiner no site.
- Criar variáveis de dataLayer, acionadores (um por evento) e tags de evento GA4 com parâmetros mapeados.
- Tag de configuração do GA4 com o ID de medição.
- Validar no modo **Preview**.
- Publicar o contêiner e **exportar o JSON** para `gtm/container.json` no repositório.

**Concluída quando:** todos os eventos aparecem no Preview com parâmetros corretos e o JSON do contêiner está versionado.

---

### Fase 5: Configuração do GA4

**Tarefas**
- Criar propriedade e fluxo de dados web.
- Marcar `purchase` como **evento-chave**.
- Criar **dimensões personalizadas** (escopo de evento/usuário): `traffic_type`, `env`, `abandonment_stage`, `user_type`, `device_profile`.
- Configurar **filtro de tráfego interno/teste** (ex.: filtrar `env=dev`) e ativá-lo após validar.
- Validar no **DebugView** e em Tempo real.
- Vincular ao **BigQuery** com exportação **diária** (criar o dataset em região adequada, sugestão `US` ou `southamerica-east1`; usar a mesma região nos datasets históricos).
- Ativar a exportação de usuários/pseudonimização apenas se necessário.

**Concluída quando:** eventos aparecem no GA4 e o link com o BigQuery está ativo.

> Atenção: a primeira tabela exportada pode levar até ~24h para aparecer. A Fase 8 só começa depois disso.

---

### Fase 6: Simulador de tráfego (Playwright + Python)

**Comportamento**
- **Volume:** 6 sessões por dia em período normal; **10 sessões por dia** em épocas sazonais.
- **Horários aleatórios:** o workflow agenda disparos em janelas espalhadas ao longo do dia e o script sorteia se roda naquela janela e com qual atraso, de modo que o total diário seja respeitado e os horários não sejam fixos. Pesos maiores para horários de pico (almoço e noite).
- **Sazonalidade (aumentar volume e conversão):** Dia do Consumidor (15/03), Dia das Mães (maio), Dia dos Namorados (12/06), Dia dos Pais (agosto), Black Friday (novembro), Natal (dezembro). Calendário em arquivo de configuração editável.
- **Fluxo de navegação:** abrir o site, fechar o pop-up, navegar pela listagem, visualizar produto, adicionar ao carrinho, ver carrinho, iniciar checkout, entrega, pagamento e, quando for o caso, concluir a compra.
- **Abandono (foco do estudo):** a taxa-base é de **~70% de abandono de quem chega ao `begin_checkout`** e **~30% de compra**, mas a taxa **oscila por dia, dispositivo e canal** (não pode ser exatamente 70% sempre). Abandonos ocorrem em etapas variadas (`cart`, `begin_checkout`, `shipping`, `payment`). Sessões também podem abandonar antes do checkout (só vendo produtos).
- **Variações:** UTMs (orgânico, direto, e-mail, redes sociais, anúncios pagos), perfis de dispositivo (desktop e mobile, viewports e user agents de navegadores comuns), tempo entre ações com variação humana.
- **Marcação:** toda sessão simulada define `traffic_type = simulated` e `env = prod`.

**Retenção realista (coorte)**
- Cada sessão de **novo usuário** começa sem cookies e cria um usuário novo.
- **Apenas uma pequena parte** dos usuários é agendada para voltar. Não replicar todos.
- Retornos aproximadamente nos dias **1, 3 e 7**, com variação de ±1 dia, e a probabilidade de retorno decrescente (mais gente volta no dia 1 que no dia 7). A taxa varia por canal de aquisição.
- Usuários que retornam usam o **`storage_state`** salvo (cookies, incluindo `_ga`), mantendo o mesmo `client_id`. Retornantes têm chance maior de comprar.
- Compras em dias diferentes para o mesmo usuário (para receita por coorte).
- Quem não está agendado "some" do estado, como visitantes reais.

**Estado (branch `state`)**
- `state.json` guarda apenas os usuários agendados: identificador interno, `storage_state`, data da primeira visita, datas previstas de retorno, canal de aquisição, histórico mínimo.
- A cada execução, o workflow faz checkout do branch `state`, o script lê/atualiza o JSON e o workflow faz **commit** do resultado.
- Remover entradas expiradas (retornos já realizados ou passados da janela de 7 dias).
- O commit periódico também garante atividade no repositório.
- **Controle de concorrência** (`concurrency` no workflow) para evitar duas execuções simultâneas escrevendo no mesmo estado.

**GitHub Actions**
- Workflow com `schedule` (cron em UTC, lembrando que pode atrasar alguns minutos) e `workflow_dispatch` para disparo manual.
- Setup do Python, instalação do Playwright e do Chromium, execução em modo headless.
- Garantir `browser.close()` e timeout por sessão.
- **Orçamento de minutos (repo privado, 2.000 min/mês grátis):** 10 execuções/dia × 2 a 3 min = ~600 a 900 min/mês. Monitorar e ajustar se aproximar do limite. Usar cache de dependências para reduzir o tempo de setup.
- Secrets: URL do site, ID do GA4/GTM quando necessário.

**Limitações a documentar:** IP de datacenter do GitHub (geografia pobre e pouco variada), GA4 pode filtrar tráfego com aparência de robô (configurar navegador comum e conferir), volume baixo.

**Concluída quando:** o workflow roda sozinho, os eventos de sessões simuladas aparecem no GA4 (DebugView/Tempo real), o estado persiste no branch `state` e um usuário agendado retorna com o mesmo `client_id`.

---

### Fase 7: Operação contínua e monitoramento

**Tarefas**
- Deixar o workflow rodando por **pelo menos 2 semanas** antes de seguir para a análise (8 dias é o mínimo para existir a coorte do dia 7).
- Criar um **workflow de verificação** (ou alerta simples) que avise se o número de sessões do dia ficou abaixo do esperado ou se o workflow falhou.
- Acompanhar o consumo de minutos do GitHub Actions.
- Conferir se as tabelas diárias `events_YYYYMMDD` estão sendo geradas no BigQuery.

**Concluída quando:** há pelo menos 8 a 14 dias de dados reais no BigQuery sem falhas relevantes.

---

### Fase 8: Inspeção do esquema real do GA4 no BigQuery

**Esta fase vem antes de qualquer carga histórica.**

**Tarefas**
- Via MCP, listar as tabelas do dataset exportado pelo GA4 (`events_YYYYMMDD`, e `events_intraday_*` se existir).
- Extrair o **esquema completo** (campos, tipos, `STRUCT`s e `REPEATED`): `event_date`, `event_timestamp`, `event_name`, `event_params`, `user_properties`, `user_pseudo_id`, `user_id`, `device`, `geo`, `traffic_source`, `collected_traffic_source`, `session_traffic_source_last_click`, `items`, `ecommerce` etc.
- Analisar **dados reais**: como `ga_session_id`, `ga_session_number`, `session_engagement_time`, `page_location`, `engagement_time_msec` e os parâmetros customizados aparecem; como eventos automáticos (`first_visit`, `session_start`, `user_engagement`, `page_view`) se comportam.
- Documentar o esquema e as particularidades em `docs/ga4-schema.md`.
- Medir proporções reais para calibrar o gerador (eventos por sessão, tempo entre eventos, distribuição de dispositivos).

**Concluída quando:** `docs/ga4-schema.md` descreve o esquema real e as regras de preenchimento observadas.

---

### Fase 9: Carga histórica de 1 ano no BigQuery

**Só executar depois da Fase 8.**

**Regras**
- Gerar **12 meses** de dados anteriores ao início dos dados reais, sem sobreposição de datas com as tabelas do GA4.
- Gravar em **dataset separado** (ex.: `ga4_historical`), com **tabelas por dia** (`events_YYYYMMDD`) e **esquema idêntico** ao do GA4 (Fase 8).
- Marcar todos os eventos com `traffic_type = historical_simulated` (em `event_params`) para separação nas análises.
- **Sazonalidade:** volume maior nos períodos sazonais (seção 6, Fase 6), com crescimento gradual ao longo do ano e variação por dia da semana.
- **Mesma lógica do Playwright:** taxa de abandono ~70% com oscilação por dia/dispositivo/canal, abandono em etapas variadas, UTMs, dispositivos.
- **Coortes:** usuários com `user_pseudo_id` estável, retornos aproximados nos dias 1, 3 e 7 (decrescentes e variáveis por canal), compras em dias distintos.
- **Consistência interna:** `event_timestamp` em microssegundos coerente com `event_date`; `ga_session_id` (timestamp do início da sessão) coerente entre eventos; `ga_session_number` incrementando; sequência de eventos lógica (`view_item` antes de `add_to_cart` etc.); `purchase` com `transaction_id` único e `value` igual à soma dos itens; eventos automáticos (`first_visit`, `session_start`, `page_view`) gerados como o GA4 faz.
- Carga via `load job` em lotes (não por inserção linha a linha), em modo sandbox sem custos de streaming.
- Script reexecutável (idempotente): rodar de novo substitui as tabelas históricas sem duplicar.

**Concluída quando:** o dataset histórico tem 12 meses contínuos, o esquema bate com o do GA4 e consultas de validação (contagem por dia, funil, retenção) retornam valores plausíveis.

---

### Fase 10: View unificada e modelagem

**Tarefas**
- Criar uma **view** que une `ga4.events_*` (real) e `ga4_historical.events_*` (histórico), expondo uma coluna `data_source` (`real` ou `historical`) e o `traffic_type`.
- Criar views/tabelas derivadas para facilitar o Looker:
  - `sessions` (uma linha por `user_pseudo_id` + `ga_session_id`, com canal, dispositivo, etapa máxima do funil, valor)
  - `funnel_steps`
  - `purchases`
  - `user_first_visit` (coorte por data da primeira visita)
- Garantir que filtros por `traffic_type` e `data_source` funcionem (humano, simulado, histórico).

**Concluída quando:** as views retornam dados dos dois datasets e as consultas de teste batem com contagens manuais.

---

### Fase 11: Análise em SQL

**Checkout abandonment**
- Funil por etapa: `view_item` → `add_to_cart` → `begin_checkout` → `add_shipping_info` → `add_payment_info` → `purchase`, com taxa de conversão e abandono entre etapas.
- Abandono por dispositivo, canal, tipo de usuário, categoria de produto e época do ano.
- Valor médio do carrinho abandonado e receita perdida.

**Cohort analysis**
- Retenção por coorte de primeira visita nos dias 1, 3 e 7 (e por semana).
- Retenção por canal de aquisição.
- Receita acumulada por coorte e recorrência de compra.

**Gerais**
- Receita por canal, produtos mais vistos vs. comprados, sazonalidade (receita e sessões por mês/semana).

Salvar as consultas em `sql/` com comentários.

**Concluída quando:** cada pergunta da seção 5.1 tem uma consulta que a responde.

---

### Fase 12: Dashboard no Looker Studio

**Páginas sugeridas**
1. Visão geral (receita, sessões, conversão, sazonalidade)
2. Funil de checkout e abandono (por etapa, dispositivo e canal)
3. Retenção por coorte (matriz de coortes)
4. Produtos e categorias

**Regras**
- Fonte de dados: as views do BigQuery (Fase 10).
- Filtros de `data_source` e `traffic_type`.
- Nota visível no dashboard informando que os dados são simulados.

Se o MCP não permitir criar o relatório do Looker, a IA entrega as consultas/views prontas e um roteiro passo a passo para o autor montar as páginas manualmente.

**Concluída quando:** o dashboard responde às perguntas de negócio e está compartilhável (visualização).

---

### Fase 13: Documentação e portfólio

**Tarefas**
- README com arquitetura (diagrama da seção 3), plano de medição, lógica da simulação, passos para operar o projeto e estrutura do repositório.
- Seção de **limitações**: dados simulados, IP único de datacenter, volume baixo no tráfego real, histórico fora do GA4.
- Seção de **como replicar**: o repositório é privado e quem quiser replicar deve entrar em contato com o autor.
- Case com **insights** e prints do dashboard.
- Registro das decisões e dos dados simulados (transparência sobre o que é real e o que é histórico gerado).

**Concluída quando:** uma pessoa externa entende o projeto e consegue avaliar o resultado só lendo o README e o dashboard.

---

## 7. Estrutura sugerida do repositório

```
/
├── site/                     # loja fake (HTML/JS estático, publicada na Vercel)
│   ├── index.html, produto, carrinho, checkout, pagamento, confirmacao, login
│   ├── products.json
│   └── assets/
├── gtm/
│   └── container.json        # contêiner exportado
├── simulator/
│   ├── main.py               # orquestra as sessões do dia
│   ├── sessions.py           # fluxo de navegação e abandono
│   ├── profiles.py           # perfis de dispositivo, canais e UTMs
│   ├── state.py              # leitura/escrita do state.json
│   ├── seasonality.json      # calendário sazonal e volumes
│   └── requirements.txt
├── historical/
│   ├── generate.py           # gerador de 1 ano (só após Fase 8)
│   └── config.json
├── sql/                      # views e análises
├── docs/
│   ├── measurement-plan.md
│   └── ga4-schema.md
├── .github/workflows/
│   ├── simulate.yml          # agendamento do Playwright
│   └── healthcheck.yml       # verificação de execução
├── .env.example
└── README.md
```

Branch dedicado: `state` (contém apenas `state.json`).

---

## 8. Riscos e pontos de atenção

| Risco | Mitigação |
|---|---|
| GA4 filtrar tráfego com aparência de robô | Navegador com user agent comum, comportamento humano, conferir nos primeiros testes |
| Perda do estado quebra a coorte | Estado versionado no branch `state` (commit a cada execução), com `concurrency` |
| Estouro de minutos do GitHub Actions (2.000/mês) | Cache de dependências, monitorar consumo, ajustar volume sazonal |
| Agendamento do Actions atrasar ou falhar | Healthcheck e execução manual (`workflow_dispatch`) |
| Histórico sobrepor dados reais | Dataset separado, datas sem sobreposição, coluna `data_source` |
| Esquema histórico divergir do real | Fase 8 obrigatória antes da Fase 9 |
| Testes poluírem a análise | `env=dev` e filtro no GA4 |
| Tráfego humano misturado ao simulado | `traffic_type` em todos os eventos |
| Dados de um único IP | Documentar como limitação |
| Primeira exportação do GA4 demorar | Aguardar até ~24h após o link com o BigQuery |

---

## 9. Ordem resumida (checklist)

1. [ ] Fase 0: Repositório, branch `state`, Vercel, acessos MCP, projeto no Google Cloud
2. [ ] Fase 1: Perguntas, catálogo, plano de medição
3. [ ] Fase 2: Site fake com pop-up e rodapé
4. [ ] Fase 3: dataLayer
5. [ ] Fase 4: GTM (e export do JSON)
6. [ ] Fase 5: GA4 (dimensões, filtros, link com BigQuery)
7. [ ] Fase 6: Simulador Playwright + Actions + estado
8. [ ] Fase 7: Operar 2+ semanas e monitorar
9. [ ] Fase 8: Inspecionar o esquema real do GA4 no BigQuery
10. [ ] Fase 9: Carga histórica de 1 ano no BigQuery
11. [ ] Fase 10: View unificada e modelagem
12. [ ] Fase 11: Análises em SQL
13. [ ] Fase 12: Dashboard no Looker Studio
14. [ ] Fase 13: Documentação e case de portfólio

---

## 10. Suposições assumidas (confirmar com o autor se necessário)

- 6 sessões/dia é o volume normal e 10 sessões/dia o volume sazonal.
- Taxa-base de 70% de abandono no `begin_checkout` e 30% de compra, com oscilação.
- Moeda BRL e calendário sazonal brasileiro.
- Exportação do GA4 para o BigQuery em modo **diário** (gratuito), sem streaming.
- A pessoa autora cria as contas e aprova permissões que o MCP não consiga executar.
