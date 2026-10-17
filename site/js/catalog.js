(async()=>{
  const P=await loadProducts(),page=document.body.dataset.page,app=$('#app');
  const attrs=p=>`data-product-id="${p.id}" data-product-name="${p.name}" data-product-price="${p.price}" data-product-category="${p.category}"`;
  if(page==='home'){
    const cats=['Todos',...new Set(P.map(p=>p.category))];
    const draw=c=>{
      $('#grid').innerHTML=P.filter(p=>c==='Todos'||p.category===c).map(p=>`<article class="card" data-testid="product-card" ${attrs(p)}><a href="produto.html?id=${p.id}" data-testid="product-link"><img src="${p.image}" alt="${p.name}" loading="lazy"><h3>${p.name}</h3></a><p class="cat">${p.category}</p><p class="price">${BRL(p.price)}</p><a class="btn ghost" href="produto.html?id=${p.id}">Ver detalhes</a></article>`).join('');
      document.querySelectorAll('.chip').forEach(b=>b.setAttribute('aria-pressed',b.dataset.category===c));
    };
    $('#filters').innerHTML=cats.map(c=>`<button class="chip" data-testid="category-filter" data-category="${c}">${c}</button>`).join('');
    document.querySelectorAll('.chip').forEach(b=>b.onclick=()=>draw(b.dataset.category));
    draw('Todos');
  }
  if(page==='product'){
    const p=P.find(x=>x.id===new URLSearchParams(location.search).get('id'));
    if(!p){app.innerHTML='<h1>Produto não encontrado</h1><a class="btn" href="index.html">Voltar à loja</a>';return}
    document.title=p.name+' | volta';
    app.innerHTML=`<div class="detail" data-testid="product-detail" ${attrs(p)}><img src="${p.image}" alt="${p.name}"><div><p class="cat">${p.category}</p><h1>${p.name}</h1><p>${p.description}</p><p class="price">${BRL(p.price)}</p><button class="btn" data-testid="add-to-cart">Adicionar ao carrinho</button><div id="added"></div></div></div>`;
    $('[data-testid="add-to-cart"]').onclick=()=>{Cart.add(p.id);$('#added').innerHTML='<p class="note" role="status">Adicionado ao carrinho. <a href="carrinho.html">Ver carrinho</a></p>'};
  }
})();
