"""Perfis de dispositivo, canais de aquisição e regras de retenção/conversão."""
from datetime import timedelta

UA_DESKTOP = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

# nome, peso, tipo, configuração (viewport próprio ou descritor de dispositivo do Playwright)
DEVICES = [
    {"name": "desktop_1920", "w": 22, "kind": "desktop", "viewport": {"width": 1920, "height": 1080}},
    {"name": "desktop_1366", "w": 16, "kind": "desktop", "viewport": {"width": 1366, "height": 768}},
    {"name": "mobile_pixel7", "w": 34, "kind": "mobile", "device": "Pixel 7"},
    {"name": "mobile_galaxy", "w": 28, "kind": "mobile", "device": "Galaxy S9+"},
]

CHANNELS = [
    {"name": "direct", "w": 28, "utm": None, "referer": None},
    {"name": "organic", "w": 30, "utm": None, "referer": "https://www.google.com/"},
    {"name": "paid_search", "w": 14, "referer": None, "utm": {
        "utm_source": "google", "utm_medium": "cpc",
        "campaign": ["eletronicos_busca", "notebooks_busca", "celulares_busca"]}},
    {"name": "social", "w": 12, "referer": None, "utm": {
        "utm_source": "instagram", "utm_medium": "social",
        "campaign": ["stories_lancamentos", "reels_audio"]}},
    {"name": "email", "w": 10, "referer": None, "utm": {
        "utm_source": "newsletter", "utm_medium": "email",
        "campaign": ["ofertas_semana", "carrinho_abandonado"]}},
]
CHANNEL_BY_NAME = {c["name"]: c for c in CHANNELS}
DEVICE_BY_NAME = {d["name"]: d for d in DEVICES}

# Fator de retenção e ajuste de conversão por canal e dispositivo
RETENTION = {"direct": 1.3, "organic": 1.0, "paid_search": 0.6, "social": 0.7, "email": 1.6}
CONV_CHANNEL = {"email": 0.06, "direct": 0.02, "organic": 0.0, "paid_search": -0.03, "social": -0.04}
CONV_DEVICE = {"desktop": 0.06, "mobile": -0.04}

# (dia base, deslocamentos possíveis, pesos dos deslocamentos, probabilidade base de voltar)
RETURNS = [
    (1, [1, 2], [3, 1], 0.18),
    (3, [2, 3, 4], [1, 2, 1], 0.10),
    (7, [6, 7, 8], [1, 2, 1], 0.06),
]


def pick(rng, items):
    return rng.choices(items, weights=[i["w"] for i in items])[0]


def return_channel(rng):
    """Quem volta costuma vir direto ou por e-mail."""
    name = rng.choices(["direct", "email", "organic"], weights=[60, 25, 15])[0]
    return CHANNEL_BY_NAME[name]


def schedule_returns(rng, channel, purchased, today):
    """Sorteia se (e quando) o usuário volta. A maioria nunca volta."""
    f = RETENTION[channel] * (1.8 if purchased else 1.0)
    days = set()
    for _, offsets, weights, p in RETURNS:
        if rng.random() < min(p * f, 0.9):
            days.add(rng.choices(offsets, weights=weights)[0])
    return sorted((today + timedelta(days=d)).isoformat() for d in days)


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def probabilities(device_kind, channel, user_type, season_bonus, noise):
    """Probabilidades do funil nesta sessão.

    `buy` é a chance de comprar DADO QUE iniciou o checkout (base ~30%,
    ou seja, ~70% abandonam), com oscilação por dia, dispositivo e canal.
    """
    buy = (0.30 + CONV_DEVICE[device_kind] + CONV_CHANNEL[channel]
           + (0.08 if user_type == "returning" else 0.0) + season_bonus + noise)
    return {
        "bounce": 0.18,
        "add": clamp(0.35 + noise, 0.2, 0.5),
        "view_cart": 0.85,
        "checkout": clamp(0.62 + noise * 0.5, 0.45, 0.8),
        "buy": clamp(buy, 0.12, 0.50),
        "login": 0.20 if user_type == "new" else 0.35,
    }
