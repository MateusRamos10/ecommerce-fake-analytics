"""Fluxo de uma sessão simulada, usando os data-testid da loja."""
import json
from urllib.parse import urlencode

from profiles import UA_DESKTOP

NOMES = ["Ana Souza", "Bruno Lima", "Carla Dias", "Diego Alves", "Elisa Rocha",
         "Felipe Costa", "Gabriela Nunes", "Hugo Martins", "Isabela Reis", "João Pereira"]
RUAS = ["Rua das Flores", "Av. Brasil", "Rua Sete de Setembro", "Rua XV de Novembro", "Av. Paulista"]
CIDADES = ["São Paulo", "Campinas", "Botucatu", "Bauru", "Sorocaba", "Rio de Janeiro", "Belo Horizonte"]


def pausa(page, rng, a=0.8, b=2.4):
    """Pausa com variação humana entre as ações."""
    page.wait_for_timeout(int(rng.uniform(a, b) * 1000))


def init_script(meta):
    """Marca a sessão como simulada para o site (contrato com app.js do Analytics).

    O app.js lê `window.__PLAYWRIGHT_SIMULATED__` para definir traffic_type = simulated.
    Também gravamos os demais parâmetros no sessionStorage, porque o app.js lê env
    e os demais valores de lá (e não do localStorage).
    """
    return ("try{Object.defineProperty(navigator,'webdriver',{get:()=>undefined});}catch(e){}"
            "window.__PLAYWRIGHT_SIMULATED__=true;"
            "try{const m=%s;for(const k in m)sessionStorage.setItem(k,m[k]);window.SIM_META=m;}catch(e){}"
            % json.dumps(meta))


def fechar_aviso(page, rng):
    botao = page.get_by_test_id("modal-close")
    try:
        botao.wait_for(state="visible", timeout=4000)
        pausa(page, rng, 0.6, 1.8)
        botao.click()
    except Exception:
        pass


def preencher_entrega(page, rng, email):
    campos = {
        "field-nome": rng.choice(NOMES),
        "field-email": email,
        "field-endereco": f"{rng.choice(RUAS)}, {rng.randint(10, 1500)}",
        "field-cidade": rng.choice(CIDADES),
        "field-cep": f"{rng.randint(10000, 99999)}-{rng.randint(100, 999)}",
    }
    for testid, valor in campos.items():
        page.get_by_test_id(testid).fill(valor)
        pausa(page, rng, 0.3, 1.0)


def login(page, rng, email):
    page.get_by_test_id("login-link").click()
    page.get_by_test_id("login-email").fill(email)
    page.get_by_test_id("login-password").fill("senha123")
    pausa(page, rng, 0.5, 1.5)
    page.get_by_test_id("login-submit").click()
    page.get_by_test_id("product-card").first.wait_for()


def fluxo(page, c, res):
    rng, p = c["rng"], c["p"]
    url = c["base_url"].rstrip("/") + "/"
    utm = c["channel"].get("utm")
    if utm:
        q = {k: v for k, v in utm.items() if k != "campaign"}
        q["utm_campaign"] = rng.choice(utm["campaign"])
        url += "?" + urlencode(q)
    page.goto(url, referer=c["channel"].get("referer"))
    fechar_aviso(page, rng)
    page.get_by_test_id("product-card").first.wait_for()

    if rng.random() < p["bounce"]:           # saiu na home
        res["stage"] = "home"
        pausa(page, rng, 2, 6)
        return

    logado = page.evaluate("!!localStorage.getItem('user')")
    if not logado and rng.random() < p["login"]:
        login(page, rng, c["email"])
        pausa(page, rng)

    if rng.random() < 0.3:                   # usa o filtro de categoria
        filtros = page.get_by_test_id("category-filter")
        filtros.nth(rng.randrange(filtros.count())).click()
        pausa(page, rng)

    n_ver = rng.choice([1, 1, 2, 2, 3])
    res["stage"] = "browse"
    for i in range(n_ver):
        cards = page.get_by_test_id("product-card")
        cards.nth(rng.randrange(cards.count())).get_by_test_id("product-link").click()
        page.get_by_test_id("add-to-cart").wait_for()
        res["viewed"] += 1
        pausa(page, rng, 1.5, 4)
        if rng.random() < p["add"]:
            page.get_by_test_id("add-to-cart").click()
            res["added"] += 1
            pausa(page, rng, 0.6, 1.5)
        if i < n_ver - 1:
            page.get_by_test_id("home-link").click()
            page.get_by_test_id("product-card").first.wait_for()
            pausa(page, rng)

    if res["added"] == 0:
        return
    res["stage"] = "cart"
    if rng.random() > p["view_cart"]:
        return
    page.get_by_test_id("cart-link").click()
    page.get_by_test_id("cart-checkout").wait_for()
    pausa(page, rng, 1.5, 4)
    if rng.random() < 0.15:                  # ajusta uma quantidade
        page.get_by_test_id("qty-inc").first.click()
        pausa(page, rng)
    if rng.random() > p["checkout"]:
        return                               # abandona no carrinho

    page.get_by_test_id("cart-checkout").click()
    page.get_by_test_id("field-nome").wait_for()
    res["stage"] = "checkout"
    pausa(page, rng, 1.5, 4)

    if rng.random() > p["buy"]:              # ABANDONO após begin_checkout
        if rng.random() < 0.5:
            pausa(page, rng, 3, 8)           # sai na página de entrega
            return
        preencher_entrega(page, rng, c["email"])
        page.get_by_test_id("shipping-submit").click()
        page.get_by_test_id("pay-submit").wait_for()
        res["stage"] = "payment"
        pausa(page, rng, 3, 9)               # sai na página de pagamento
        return

    preencher_entrega(page, rng, c["email"])  # COMPRA
    page.get_by_test_id("shipping-submit").click()
    page.get_by_test_id("pay-submit").wait_for()
    pausa(page, rng, 2, 5)
    page.get_by_test_id("pay-submit").click()
    page.get_by_test_id("order-confirmation").wait_for()
    res["stage"], res["purchased"] = "purchase", True
    pausa(page, rng, 2, 4)


def run_session(pw, browser, c):
    """Executa uma sessão. Retorna (resultado, storage_state final)."""
    dev = c["device"]
    if "device" in dev:
        opts = dict(pw.devices[dev["device"]])
    else:
        opts = {"viewport": dev["viewport"], "user_agent": UA_DESKTOP}
    opts.update(locale="pt-BR", timezone_id="America/Sao_Paulo")
    if c["storage_state"]:
        opts["storage_state"] = c["storage_state"]
    ctx = browser.new_context(**opts)
    ctx.set_default_timeout(15000)
    ctx.add_init_script(init_script({
        "traffic_type": "simulated", "env": c["env"],
        "user_type": c["user_type"], "device_profile": dev["name"]}))
    page = ctx.new_page()
    res = {"stage": "home", "purchased": False, "viewed": 0, "added": 0}
    final_state = c["storage_state"]
    try:
        fluxo(page, c, res)
        page.wait_for_timeout(1500)          # deixa os hits do GA4 saírem
        page.goto("about:blank")             # dispara pagehide/visibilitychange
        page.wait_for_timeout(800)
    except Exception as e:
        res["error"] = repr(e)[:200]
    finally:
        try:
            final_state = ctx.storage_state()
        except Exception:
            pass
        ctx.close()
    return res, final_state
