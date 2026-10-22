"""Orquestra as sessões simuladas do dia.

Uso:
  python simulator/main.py --gate   # só decide quantas sessões rodar agora (sem dependências)
  python simulator/main.py          # executa as sessões pendentes

Variáveis de ambiente: SITE_URL (obrigatória), SIM_ENV (prod|dev), STATE_PATH,
FORCE_SESSIONS (executa N sessões agora, ignorando o plano do dia), MAX_PER_RUN.
"""
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import profiles as pf
import state as st

TZ = ZoneInfo("America/Sao_Paulo")
CFG = json.loads((Path(__file__).parent / "seasonality.json").read_text(encoding="utf-8"))
MAX_PER_RUN = int(os.environ.get("MAX_PER_RUN", "4"))
# Peso de cada hora (horário de Brasília): mais movimento no almoço e à noite
HOUR_WEIGHTS = {8: 2, 9: 3, 10: 4, 11: 5, 12: 7, 13: 6, 14: 5, 15: 5,
                16: 5, 17: 5, 18: 6, 19: 8, 20: 10, 21: 10, 22: 8, 23: 4}


def season(day):
    mmdd = day.strftime("%m-%d")
    for p in CFG["periods"]:
        if p["start"] <= mmdd <= p["end"]:
            return CFG["seasonal"], p["name"]
    return CFG["normal"], None


def day_slots(day):
    """Horas das sessões do dia. Determinístico por data (mesmo plano em todas as execuções)."""
    conf, _ = season(day)
    rng = random.Random(day.isoformat())
    hours = list(HOUR_WEIGHTS)
    return sorted(rng.choices(hours, weights=[HOUR_WEIGHTS[h] for h in hours], k=conf["sessions"]))


def pending(S, slots, hour):
    """Sessões planejadas para até a hora atual que ainda não rodaram (cobre atrasos do cron)."""
    return [h for h in slots[S["day"]["executed"]:] if h <= hour][:MAX_PER_RUN]


def plan_now():
    now = datetime.now(TZ)
    S = st.load()
    st.start_day(S, now.date())
    force = int(os.environ.get("FORCE_SESSIONS") or 0)
    slots = day_slots(now.date())
    todo = [now.hour] * min(force, MAX_PER_RUN * 5) if force else pending(S, slots, now.hour)
    return now, S, slots, todo, force


def gate():
    now, S, slots, todo, force = plan_now()
    conf, nome = season(now.date())
    print(f"{now:%Y-%m-%d %H:%M} BRT | plano do dia: {len(slots)} sessões em {slots} "
          f"| sazonal: {nome} | já feitas: {S['day']['executed']} | agora: {len(todo)}")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"sessions={len(todo)}\n")


def run():
    from playwright.sync_api import sync_playwright
    import sessions

    base_url = os.environ["SITE_URL"]
    env = os.environ.get("SIM_ENV", "prod")
    now, S, slots, todo, force = plan_now()
    if not todo:
        print("Nada a executar agora.")
        return 0
    today = now.date()
    conf, _ = season(today)
    day_rng = random.Random("noise-" + today.isoformat())
    day_noise = day_rng.gauss(0, 0.04)                       # dia bom ou ruim
    kind_noise = {"desktop": day_rng.gauss(0, 0.02), "mobile": day_rng.gauss(0, 0.02)}
    rng = random.Random()                                    # aleatório de verdade
    due = [u for u in S["users"] if today.isoformat() in u["returns"]]
    falhas = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        for i, _hour in enumerate(todo):
            restantes = (len(todo) - i) if force else max(len(slots) - S["day"]["executed"], 1)
            p_volta = min(len(due) / restantes, 0.5) if due else 0
            user = None
            if due and rng.random() < p_volta:               # esta sessão é um retorno
                user = rng.choice(due)
                due.remove(user)
                device = pf.DEVICE_BY_NAME[user["device"]]
                channel = pf.return_channel(rng)
                user_type, email, storage = "returning", user["email"], user["storage_state"]
            else:                                            # usuário novo, sem cookies
                device, channel = pf.pick(rng, pf.DEVICES), pf.pick(rng, pf.CHANNELS)
                user_type, storage = "new", None
                email = f"cliente{rng.randint(10000, 99999)}@exemplo.com"
            probs = pf.probabilities(device["kind"], channel["name"], user_type,
                                     conf["conversion_bonus"], day_noise + kind_noise[device["kind"]])
            res, final_state = sessions.run_session(pw, browser, {
                "base_url": base_url, "env": env, "rng": rng, "p": probs,
                "device": device, "channel": channel, "user_type": user_type,
                "email": email, "storage_state": storage})
            if res.get("error"):
                falhas += 1
            if user:                                         # consome o retorno de hoje
                user["returns"].remove(today.isoformat())
                user["storage_state"] = final_state
                if not user["returns"]:
                    S["users"].remove(user)
            else:                                            # talvez volte nos próximos dias
                dias = pf.schedule_returns(rng, channel["name"], res["purchased"], today)
                if dias and not res.get("error"):
                    S["users"].append({"id": f"u{rng.randint(10**7, 10**8 - 1)}", "email": email,
                                       "created": today.isoformat(), "device": device["name"],
                                       "channel": channel["name"], "returns": dias,
                                       "storage_state": final_state})
            if not force:
                S["day"]["executed"] += 1
            st.save(S)                                       # salva a cada sessão
            print(f"[{i + 1}/{len(todo)}] {user_type:9} {device['name']:14} {channel['name']:12} "
                  f"-> {res['stage']:9} compra={res['purchased']} "
                  f"{'ERRO ' + res['error'] if res.get('error') else ''}")
        browser.close()
    return 1 if falhas == len(todo) else 0


if __name__ == "__main__":
    if "--gate" in sys.argv:
        gate()
    else:
        sys.exit(run())
