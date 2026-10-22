# Simulador de tráfego

Playwright (Python) rodando no GitHub Actions (`.github/workflows/simulate.yml`).

## Como funciona
- **Plano do dia:** 6 sessões (normal) ou 10 (períodos sazonais, em `seasonality.json`), com horas sorteadas por data e mais peso no almoço e à noite.
- **Execução:** o workflow dispara 16 vezes por dia (08h–23h em Brasília). Um passo `--gate` sem dependências decide se há sessões pendentes; se não houver, o job termina em segundos (economiza minutos do Actions).
- **Funil:** ~30% de compra entre quem inicia o checkout (~70% abandonam), com oscilação por dia, dispositivo, canal e tipo de usuário. Abandonos ocorrem no carrinho, no checkout ou no pagamento.
- **Retenção:** só uma pequena parte dos usuários novos é agendada para voltar (~dias 1, 3 e 7, com variação), com cookies/`client_id` guardados em `state.json` no branch `state`. Quem compra volta mais. Quem não volta some do estado.

## Contrato com o site (Fase 3)
Antes de cada sessão o simulador grava no `localStorage`:

| Chave | Valores |
|---|---|
| `traffic_type` | `simulated` (sem a chave, o site assume `human`) |
| `env` | `prod` ou `dev` |
| `user_type` | `new` ou `returning` |
| `device_profile` | ex.: `mobile_pixel7` |

O `dataLayer` precisa ler essas chaves e enviá-las como parâmetros dos eventos.

## Configuração
- Secret do repositório: `SITE_URL` (URL do site na Vercel, sem barra final).
- Teste manual: Actions > simulate > Run workflow, com `sessions` = 3 e `env` = `dev`.
- `state.json` fica na raiz do branch `state`.
