(async()=>{
  const P=await loadProducts(),app=$('#cart');
  const draw=()=>{
    const items=Cart.get().map(i=>({...i,p:P.find(x=>x.id===i.id)})).filter(i=>i.p);
    if(!items.length){app.innerHTML='<p>Seu carrinho está vazio.</p><a class="btn" href="index.html">Ver produtos</a>';return}
    const sub=items.reduce((a,i)=>a+i.p.price*i.qty,0);
    app.innerHTML=items.map(({p,qty})=>`<div class="row" data-testid="cart-item" data-product-id="${p.id}" data-product-name="${p.name}" data-product-price="${p.price}" data-product-category="${p.category}"><img src="${p.image}" alt="${p.name}"><div><h3>${p.name}</h3><p class="cat">${BRL(p.price)}</p></div><div class="qty"><button data-testid="qty-dec" data-id="${p.id}" aria-label="Diminuir quantidade">−</button><span data-testid="qty-value">${qty}</span><button data-testid="qty-inc" data-id="${p.id}" aria-label="Aumentar quantidade">+</button></div><button class="link" data-testid="remove-item" data-id="${p.id}">Remover</button></div>`).join('')+`<div class="total"><span>Subtotal <span data-testid="cart-subtotal">${BRL(sub)}</span></span><a class="btn" href="checkout.html" data-testid="cart-checkout">Finalizar compra</a></div>`;
    const q=id=>Cart.get().find(x=>x.id===id).qty;
    app.querySelectorAll('[data-testid="qty-inc"]').forEach(b=>b.onclick=()=>{Cart.setQty(b.dataset.id,q(b.dataset.id)+1);draw()});
    app.querySelectorAll('[data-testid="qty-dec"]').forEach(b=>b.onclick=()=>{Cart.setQty(b.dataset.id,q(b.dataset.id)-1);draw()});
    app.querySelectorAll('[data-testid="remove-item"]').forEach(b=>b.onclick=()=>{Cart.setQty(b.dataset.id,0);draw()});
  };
  draw();
})();
