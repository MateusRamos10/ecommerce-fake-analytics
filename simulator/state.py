"""Estado persistente do simulador (arquivo JSON no branch `state`).

Guarda apenas:
- o contador de sessões já executadas no dia;
- os usuários que estão AGENDADOS para voltar (com cookies/client_id).
Quem não volta simplesmente não fica no arquivo, como um visitante real.
"""
import json
import os

PATH = os.environ.get("STATE_PATH", "state_branch/state.json")


def load():
    try:
        with open(PATH, encoding="utf-8") as f:
            S = json.load(f)
    except Exception:  # arquivo vazio, inexistente ou inválido
        S = {}
    if not isinstance(S, dict): # o branch state nasceu como []
        S = {}
    S.setdefault("version", 1)
    S.setdefault("day", {"date": None, "executed": 0})
    S.setdefault("users", [])
    return S


def save(S):
    os.makedirs(os.path.dirname(PATH) or ".", exist_ok=True)
    tmp = PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(S, f, separators=(",", ":"), sort_keys=True)
    os.replace(tmp, PATH)


def start_day(S, today):
    """Zera o contador se o dia mudou e descarta retornos já vencidos."""
    iso = today.isoformat()
    if S["day"].get("date") != iso:
        S["day"] = {"date": iso, "executed": 0}
    keep = []
    for u in S["users"]:
        u["returns"] = [d for d in u["returns"] if d >= iso]
        if u["returns"]:
            keep.append(u)
    S["users"] = keep
