(async()=>{
  const page=document.body.dataset.page,P=await loadProducts(),app=$('#app');
  const items=Cart.get().map(i=>({...P.find(x=>x.id===i.id),qty:i.qty})).filter(i=>i.id);
  const total=items.reduce((a,i)=>a+i.price*i.qty,0);
  const gaItems=its=>its.map(i=>({item_id:i.id,item_name:i.name,item_category:i.category,price:i.price,quantity:i.qty}));
  const summary=(its,t)=>`<aside class="summary" data-testid="order-summary"><h2>Resumo do pedido</h2>${its.map(i=>`<p class="line"><span>${i.qty}× ${i.name}</span><span>${BRL(i.price*i.qty)}</span></p>`).join('')}<p class="line total-line"><strong>Total</strong><strong data-testid="order-total">${BRL(t)}</strong></p></aside>`;
  const read=k=>{try{return JSON.parse(sessionStorage.getItem(k))}catch{return null}};

  if(page==='checkout'){
    if(!items.length)return location.replace('carrinho.html');
    const u=User(),s=read('shipping')||{};
    const f=(n,l,t='text',x='')=>`<label>${l}<input name="${n}" type="${t}" required data-testid="field-${n}" value="${s[n]||(n==='email'&&u?u.email:'')}" ${x}></label>`;
    app.innerHTML=`<div class="checkout"><form class="form" id="f" data-testid="shipping-form">${f('nome','Nome completo')}${f('email','E-mail','email')}${f('endereco','Endereço')}<div class="two">${f('cidade','Cidade')}${f('cep','CEP','text','pattern="\\d{5}-?\\d{3}" inputmode="numeric" placeholder="00000-000"')}</div><button class="btn" data-testid="shipping-submit">Continuar para o pagamento</button></form>${summary(items,total)}</div>`;

    // add_shipping_info ao submeter o formulário de entrega
    $('#f').onsubmit=e=>{
      e.preventDefault();
      const shipping=Object.fromEntries(new FormData(e.target));
      sessionStorage.setItem('shipping',JSON.stringify(shipping));
      Analytics.push('add_shipping_info',{
        currency:'BRL',
        value:total,
        items:gaItems(items)
      },{cart_value:total,abandonment_stage:'shipping'});
      sessionStorage.setItem('abandonment_stage','shipping');
      location.href='pagamento.html';
    };
  }

  if(page==='payment'){
    if(!items.length)return location.replace('carrinho.html');
    const s=read('shipping');if(!s)return location.replace('checkout.html');
    const r=(n,l,v)=>`<label>${l}<input name="${n}" value="${v}" readonly aria-readonly="true" data-testid="card-${n}"></label>`;
    app.innerHTML=`<div class="checkout"><form class="form" id="f" data-testid="payment-form">${r('numero','Número do cartão','6100 6311 5623 1213')}${r('nome','Nome no cartão','CLIENTE TESTE')}<div class="two">${r('validade','Validade','12/30')}${r('cvv','CVV','123')}</div><p class="cat">Dados fictícios e fixos. Nada é cobrado.</p><button class="btn" data-testid="pay-submit">Pagar ${BRL(total)}</button></form>${summary(items,total)}</div>`;

    // add_payment_info ao visualizar a página de pagamento
    Analytics.push('add_payment_info',{
      currency:'BRL',
      value:total,
      items:gaItems(items)
    },{payment_type:'credit_card',cart_value:total,abandonment_stage:'payment'});
    sessionStorage.setItem('abandonment_stage','payment');

    $('#f').onsubmit=e=>{
      e.preventDefault();
      const txId='VLT-'+Date.now().toString(36).toUpperCase();
      const o={id:txId,date:new Date().toISOString(),total,shipping:s,items:items.map(({id,name,price,qty,category})=>({id,name,price,qty,category}))};
      sessionStorage.setItem('lastOrder',JSON.stringify(o));
      sessionStorage.removeItem('shipping');
      sessionStorage.removeItem('abandonment_stage');
      Cart.set([]);

      // purchase event — dispara antes de redirecionar
      Analytics.push('purchase',{
        transaction_id:txId,
        currency:'BRL',
        value:total,
        items:gaItems(items)
      },{cart_value:total,abandonment_stage:'purchase'});

      location.href='confirmacao.html';
    };
  }

  if(page==='confirmation'){
    const o=read('lastOrder');if(!o)return location.replace('index.html');
    app.innerHTML=`<div class="ok" data-testid="order-confirmation"><h1>Compra confirmada</h1><p class="lead">Obrigado, ${o.shipping.nome}. Este pedido é fictício e nada foi cobrado.</p><p>Pedido <strong data-testid="order-id">${o.id}</strong></p>${summary(o.items,o.total)}<p style="margin-top:24px"><a class="btn" href="index.html" data-testid="back-to-store">Voltar à loja</a></p></div>`;
  }
})();
