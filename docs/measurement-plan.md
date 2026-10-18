# Plano de MediÃ§Ã£o: E-commerce Fake de EletrÃ´nicos (volta)

Documento de especificaÃ§Ã£o tÃ©cnica para a camada de dados (`dataLayer`), Google Tag Manager (GTM), Google Analytics 4 (GA4) e exportaÃ§Ã£o BigQuery.

---

## 1. Perguntas de NegÃ³cio

### 1.1 Checkout Abandonment (Abandono de Funil)
1. Em qual etapa do funil (`cart` â†’ `begin_checkout` â†’ `shipping` â†’ `payment` â†’ `purchase`) ocorre o maior volume de desistÃªncia?
2. Como a taxa de abandono varia por dispositivo (Mobile vs. Desktop), canal de aquisiÃ§Ã£o (UTM source/medium) e sazonalidade?
3. Qual o valor monetÃ¡rio mÃ©dio dos carrinhos abandonados e a receita potencial perdida?
4. Quais produtos e categorias sofrem maior abandono apÃ³s serem adicionados ao carrinho?

### 1.2 Cohort Analysis (RetenÃ§Ã£o e RecorrÃªncia)
1. Qual a taxa de retenÃ§Ã£o nos D1, D3 e D7 para coortes de primeira visita?
2. Como a retenÃ§Ã£o se comporta por canal de aquisiÃ§Ã£o?
3. Qual o valor de receita acumulada por coorte ao longo do tempo?
4. UsuÃ¡rios recorrentes apresentam maior taxa de conversÃ£o que novos visitantes?

---

## 2. ParÃ¢metros Customizados Globais

| ParÃ¢metro | Tipo | Escopo | Valores PossÃ­veis | DescriÃ§Ã£o |
|---|---|---|---|---|
| `traffic_type` | String | Evento / UsuÃ¡rio | `human`, `simulated`, `historical_simulated` | Diferencia visitas manuais do trÃ¡fego do robÃ´ e da carga histÃ³rica |
| `env` | String | Evento | `prod`, `dev` | Separa ambientes de teste de produÃ§Ã£o |
| `abandonment_stage` | String | Evento / SessÃ£o | `none`, `cart`, `begin_checkout`, `shipping`, `payment` | Ãšltima etapa alcanÃ§ada pelo usuÃ¡rio |
| `user_type` | String | UsuÃ¡rio | `new`, `returning` | ClassificaÃ§Ã£o do usuÃ¡rio na sessÃ£o |
| `device_profile` | String | Evento | `desktop_chrome`, `mobile_safari`, etc. | Perfil de tela/user agent simulado |
| `cart_value` | Number | Evento | Ex: `1599.90` | Valor monetÃ¡rio acumulado do carrinho no momento do evento |

---

## 3. Matriz de Eventos do dataLayer (PadrÃ£o E-commerce GA4)

### 3.1 NavegaÃ§Ã£o e CatÃ¡logo

#### `view_item_list`
* **PÃ¡gina:** `index.html` (Home)
* **Disparo:** Quando a listagem de produtos ou filtro de categoria Ã© renderizado.
* **Payload:**
```javascript
window.dataLayer.push({
  event: 'view_item_list',
  traffic_type: 'human',
  env: 'prod',
  item_list_name: 'CatÃ¡logo Geral',
  ecommerce: {
    items: [
      { item_id: 'p01', item_name: 'Aurora X1', item_category: 'Celulares', price: 3299.00, index: 1 },
      // ...
    ]
  }
});
```

#### `select_item`
* **PÃ¡gina:** `index.html`
* **Disparo:** Ao clicar em um card de produto para ver detalhes.
* **Payload:**
```javascript
window.dataLayer.push({
  event: 'select_item',
  traffic_type: 'human',
  env: 'prod',
  ecommerce: {
    items: [{ item_id: 'p01', item_name: 'Aurora X1', item_category: 'Celulares', price: 3299.00 }]
  }
});
```

#### `view_item`
* **PÃ¡gina:** `produto.html?id=...`
* **Disparo:** Ao carregar a pÃ¡gina de detalhes de um produto especÃ­fico.
* **Payload:**
```javascript
window.dataLayer.push({
  event: 'view_item',
  traffic_type: 'human',
  env: 'prod',
  ecommerce: {
    value: 3299.00,
    currency: 'BRL',
    items: [{ item_id: 'p01', item_name: 'Aurora X1', item_category: 'Celulares', price: 3299.00, quantity: 1 }]
  }
});
```

---

### 3.2 Carrinho e Funil de ConversÃ£o

#### `add_to_cart`
* **PÃ¡gina:** `produto.html`
* **Disparo:** Ao clicar no botÃ£o `Adicionar ao carrinho`.
* **Payload:**
```javascript
window.dataLayer.push({
  event: 'add_to_cart',
  traffic_type: 'human',
  env: 'prod',
  cart_value: 3299.00,
  ecommerce: {
    value: 3299.00,
    currency: 'BRL',
    items: [{ item_id: 'p01', item_name: 'Aurora X1', item_category: 'Celulares', price: 3299.00, quantity: 1 }]
  }
});
```

#### `view_cart`
* **PÃ¡gina:** `carrinho.html`
* **Disparo:** Ao acessar a pÃ¡gina do carrinho com itens.
* **Payload:**
```javascript
window.dataLayer.push({
  event: 'view_cart',
  traffic_type: 'human',
  env: 'prod',
  cart_value: 3299.00,
  abandonment_stage: 'cart',
  ecommerce: {
    value: 3299.00,
    currency: 'BRL',
    items: [...]
  }
});
```

#### `begin_checkout`
* **PÃ¡gina:** `carrinho.html` -> `checkout.html`
* **Disparo:** Ao clicar no botÃ£o `Finalizar compra` no carrinho ou carregar `checkout.html`.
* **Payload:**
```javascript
window.dataLayer.push({
  event: 'begin_checkout',
  traffic_type: 'human',
  env: 'prod',
  cart_value: 3299.00,
  abandonment_stage: 'begin_checkout',
  ecommerce: {
    value: 3299.00,
    currency: 'BRL',
    items: [...]
  }
});
```

#### `add_shipping_info`
* **PÃ¡gina:** `checkout.html`
* **Disparo:** Ao submeter o formulÃ¡rio de entrega para ir ao pagamento.
* **Payload:**
```javascript
window.dataLayer.push({
  event: 'add_shipping_info',
  traffic_type: 'human',
  env: 'prod',
  shipping_tier: 'PadrÃ£o',
  cart_value: 3299.00,
  abandonment_stage: 'shipping',
  ecommerce: {
    value: 3299.00,
    currency: 'BRL',
    items: [...]
  }
});
```

#### `add_payment_info`
* **PÃ¡gina:** `pagamento.html`
* **Disparo:** Ao carregar a tela de pagamento com o cartÃ£o de crÃ©dito fictÃ­cio preparado.
* **Payload:**
```javascript
window.dataLayer.push({
  event: 'add_payment_info',
  traffic_type: 'human',
  env: 'prod',
  payment_type: 'CartÃ£o de CrÃ©dito',
  cart_value: 3299.00,
  abandonment_stage: 'payment',
  ecommerce: {
    value: 3299.00,
    currency: 'BRL',
    items: [...]
  }
});
```

#### `purchase`
* **PÃ¡gina:** `confirmacao.html`
* **Disparo:** Ao processar o pagamento com sucesso na tela de confirmaÃ§Ã£o.
* **Payload:**
```javascript
window.dataLayer.push({
  event: 'purchase',
  traffic_type: 'human',
  env: 'prod',
  abandonment_stage: 'none',
  ecommerce: {
    transaction_id: 'VLT-K89ABC12',
    value: 3299.00,
    currency: 'BRL',
    items: [...]
  }
});
```

---

### 3.3 AutenticaÃ§Ã£o e UsuÃ¡rio

#### `login`
* **PÃ¡gina:** `login.html`
* **Disparo:** Ao fazer login simulado com e-mail.
* **Payload:**
```javascript
window.dataLayer.push({
  event: 'login',
  method: 'email',
  user_id: 'usr_xyz123',
  traffic_type: 'human',
  env: 'prod'
});
```
