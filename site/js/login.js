(()=>{
  const app=$('#app'),u=User();
  if(u){
    app.innerHTML=`<div class="form"><p>Você está logado como <strong data-testid="user-email">${u.email}</strong>.</p><button class="btn" data-testid="logout">Sair</button></div>`;
    $('[data-testid="logout"]').onclick=()=>{localStorage.removeItem('user');location.reload()};
    return;
  }
  app.innerHTML=`<form class="form" id="f" data-testid="login-form"><label>E-mail<input name="email" type="email" required data-testid="login-email"></label><label>Senha<input name="senha" type="password" required data-testid="login-password"></label><p class="cat">Login simulado: qualquer e-mail e senha funcionam.</p><button class="btn" data-testid="login-submit">Entrar</button></form>`;
  $('#f').onsubmit=e=>{
    e.preventDefault();
    const fd=new FormData(e.target);
    const userId='u_'+Math.random().toString(36).slice(2,10);
    const email=fd.get('email');
    localStorage.setItem('user',JSON.stringify({id:userId,email}));

    // login event
    Analytics.push('login',{},{method:'email',user_id:userId});

    location.href='index.html';
  };
})();
