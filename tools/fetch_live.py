#!/usr/bin/env python3
"""Descarga los datos vivos del perfil desde la API GraphQL de GitHub y los guarda en data/live.json.

- contribuciones del último año, días activos, racha actual y mejor racha
- lenguajes de los repos públicos propios (sin forks ni este repo de perfil), por bytes de código

Uso:  GITHUB_TOKEN=... python tools/fetch_live.py
En la GitHub Action el token lo pone GitHub solo (secrets.GITHUB_TOKEN).
Si algo falla, sale con error para que la Action se marque en rojo y no se publiquen datos a medias.
"""
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "live.json"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def graphql(token, login):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": f"{login}-profile"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]["user"]


def streaks(days, today):
    """days: lista ordenada de (fecha, n). Devuelve (racha actual, mejor racha, días activos)."""
    longest = run = 0
    for _, n in days:
        run = run + 1 if n > 0 else 0
        longest = max(longest, run)
    active = sum(1 for _, n in days if n > 0)
    # la racha actual cuenta hasta hoy; si hoy aún no hay contribuciones, hasta ayer
    current = 0
    for date, n in reversed(days):
        if date > today:
            continue
        if n > 0:
            current += 1
        elif date == today and current == 0:
            continue
        else:
            break
    return current, longest, active


def languages(repos, skip):
    totals, colors = {}, {}
    for repo in repos:
        if repo["name"].lower() == skip.lower():
            continue
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            totals[name] = totals.get(name, 0) + e["size"]
            colors[name] = e["node"]["color"] or "#8b949e"
    grand = sum(totals.values()) or 1
    top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:6]
    return [{"name": n, "color": colors[n], "pct": round(100 * b / grand, 1)} for n, b in top]


def main():
    profile = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    login = profile["user"]
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Falta GITHUB_TOKEN", file=sys.stderr)
        return 1
    user = graphql(token, login)
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = sorted((d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"])
    today = dt.date.today().isoformat()
    current, longest, active = streaks(days, today)
    live = {
        "updated": today,
        "total": cal["totalContributions"],
        "active_days": active,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": max((n for _, n in days), default=0),
        "languages": languages(user["repositories"]["nodes"], skip=login),
    }
    OUT.write_text(json.dumps(live, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(live, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
