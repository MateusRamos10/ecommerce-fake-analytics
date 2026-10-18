const $=(s,r=document)=>r.querySelector(s);
const BRL=n=>n.toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
const Cart={
  get(){try{return JSON.parse(localStorage.getItem('cart'))||[]}catch{return[]}},
  set(c){localStorage.setItem('cart',JSON.stringify(c));Cart.badge()},
  add(id,q=1){const c=Cart.get(),i=c.find(x=>x.id===id);i?i.qty+=q:c.push({id,qty:q});Cart.set(c)},
  setQty(id,q){const c=Cart.get();Cart.set(q<1?c.filter(x=>x.id!==id):c.map(x=>x.id===id?{...x,qty:q}:x))},
  count(){return Cart.get().reduce((a,x)=>a+x.qty,0)},
  badge(){const b=$('[data-testid="cart-count"]');if(b)b.textContent=Cart.count()}
};
window.dataLayer = window.dataLayer || [];

const Analytics = {
  getTrafficType() {
    const params = new URLSearchParams(location.search);
    if (params.get('traffic_type')) {
      sessionStorage.setItem('traffic_type', params.get('traffic_type'));
      return params.get('traffic_type');
    }
    return sessionStorage.getItem('traffic_type') || (window.__PLAYWRIGHT_SIMULATED__ ? 'simulated' : 'human');
  },
  getEnv() {
    const params = new URLSearchParams(location.search);
    if (params.get('env')) {
      sessionStorage.setItem('env', params.get('env'));
      return params.get('env');
    }
    return sessionStorage.getItem('env') || (location.hostname.includes('localhost') ? 'dev' : 'prod');
  },
  getUserType() {
    const firstVisit = localStorage.getItem('first_visit_date');
    const today = new Date().toISOString().slice(0, 10);
    if (!firstVisit) {
      localStorage.setItem('first_visit_date', today);
      return 'new';
    }
    return firstVisit === today ? 'new' : 'returning';
  },
  getDeviceProfile() {
    const params = new URLSearchParams(location.search);
    return params.get('device_profile') || (window.innerWidth <= 768 ? 'mobile' : 'desktop');
  },
  push(eventName, ecommerceData = {}, extraParams = {}) {
    window.dataLayer.push({ ecommerce: null });
    const currentUser = User();
    const payload = {
      event: eventName,
      traffic_type: Analytics.getTrafficType(),
      env: Analytics.getEnv(),
      user_type: Analytics.getUserType(),
      device_profile: Analytics.getDeviceProfile(),
      ...(currentUser?.id ? { user_id: currentUser.id } : {}),
      ...extraParams
    };
    if (ecommerceData && Object.keys(ecommerceData).length > 0) {
      payload.ecommerce = ecommerceData;
    }
    window.dataLayer.push(payload);
  }
};

let _p;const loadProducts=()=>_p||(_p=fetch('products.json').then(r=>r.json()));
const User=()=>{try{return JSON.parse(localStorage.getItem('user'))}catch{return null}};

(function layout(){
  const u=User();
  document.body.insertAdjacentHTML('afterbegin',`<header class="hdr"><a href="index.html" data-testid="home-link"><img src="assets/logo.svg" alt="volta" height="28"></a><nav><a href="index.html">Loja</a><a href="login.html" data-testid="login-link">${u?u.email:'Entrar'}</a><a href="carrinho.html" data-testid="cart-link">Carrinho <span class="count" data-testid="cart-count">0</span></a></nav></header>`);
  document.body.insertAdjacentHTML('beforeend',`<footer class="ftr" data-testid="site-footer"><strong>Loja fictícia de portfólio.</strong> Nenhum produto é vendido e nenhum dado de pagamento é real. <span data-testid="site-version"></span></footer>`);
  fetch('version.json').then(r=>r.json()).then(v=>{$('[data-testid="site-version"]').textContent='v'+v.version}).catch(()=>{});
  Cart.badge();
  if(!sessionStorage.getItem('disclaimerSeen')){
    document.body.insertAdjacentHTML('beforeend',`<div class="overlay" data-testid="disclaimer-modal"><div class="modal" role="dialog" aria-modal="true" aria-labelledby="mt"><h2 id="mt">Esta é uma loja fictícia</h2><p>A volta é um e-commerce fake criado para um projeto de portfólio. Nenhum produto é vendido e nenhum dado de pagamento é real.</p><button class="btn" data-testid="modal-close">Entendi</button></div></div>`);
    const m=$('[data-testid="disclaimer-modal"]'),b=$('[data-testid="modal-close"]');
    b.focus();
    b.onclick=()=>{sessionStorage.setItem('disclaimerSeen','1');m.remove()};
  }
})();
