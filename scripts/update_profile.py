#!/usr/bin/env python3
"""Refresh public GitHub stats and render theme-aware profile cards."""

from __future__ import annotations

import html
import json
import os
import ssl
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import certifi

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "profile-config.json"
STATS_PATH = ROOT / "assets" / "stats.json"
ASCII_PATH = ROOT / "assets" / "avatar-ascii.txt"
API = "https://api.github.com"

THEMES = {
    "dark": {
        "background": "#0d1117", "panel": "#161b22", "border": "#30363d",
        "text": "#e6edf3", "muted": "#8b949e", "accent": "#7ee787",
        "blue": "#79c0ff", "red": "#ff7b72", "yellow": "#d29922",
    },
    "light": {
        "background": "#ffffff", "panel": "#f6f8fa", "border": "#d0d7de",
        "text": "#1f2328", "muted": "#656d76", "accent": "#1a7f37",
        "blue": "#0969da", "red": "#cf222e", "yellow": "#bf8700",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def github_get(path: str, token: str = "") -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "shivamchopra7-profile-updater",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"{API}{path}", headers=headers)
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(request, timeout=25, context=context) as response:
            return json.load(response)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        raise RuntimeError(f"GitHub API request failed for {path}: {exc}") from exc


def public_stats(username: str, previous: dict[str, Any]) -> dict[str, Any]:
    token = os.environ.get("GITHUB_TOKEN", "")
    user = github_get(f"/users/{urllib.parse.quote(username)}", token)
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        batch = github_get(
            f"/users/{urllib.parse.quote(username)}/repos?type=owner&per_page=100&page={page}",
            token,
        )
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    commits: int | str = previous.get("public_commits_365d", "--")
    since = (datetime.now(timezone.utc) - timedelta(days=365)).date().isoformat()
    query = urllib.parse.quote(f"author:{username} author-date:>={since}")
    try:
        commits = github_get(f"/search/commits?q={query}&per_page=1", token)["total_count"]
    except (RuntimeError, KeyError, TypeError):
        # Search can be independently rate-limited; keep the last known value.
        pass

    return {
        "account_year": str(user.get("created_at", "----"))[:4],
        "followers": user.get("followers", "--"),
        "public_commits_365d": commits,
        "public_repos": user.get("public_repos", len(repos)),
        "stars_received": sum(repo.get("stargazers_count", 0) for repo in repos),
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


def safe(value: Any) -> str:
    return html.escape(str(value), quote=True)


def tspan_lines(lines: list[str], x: int, y: int, step: int) -> str:
    return "\n".join(
        f'<tspan x="{x}" y="{y + index * step}">{safe(line)}</tspan>'
        for index, line in enumerate(lines)
    )


def detail_lines(rows: list[tuple[str, str]], x: int, y: int, step: int) -> str:
    return "\n".join(
        f'<tspan x="{x}" y="{y + index * step}" class="label">{safe(label):}</tspan>'
        f'<tspan x="{x + 124}" y="{y + index * step}">{safe(value)}</tspan>'
        for index, (label, value) in enumerate(rows)
    )


def render_svg(config: dict[str, Any], stats: dict[str, Any], ascii_art: str, theme: str) -> str:
    c = THEMES[theme]
    details = [
        ("Role", config["role"]),
        ("Company", config["company"]),
        ("Location", config["location"]),
        ("Products", ", ".join(config["products"])),
        ("Focus", ", ".join(config["focus"])),
        ("Languages", ", ".join(config["programming"])),
        ("Web", ", ".join(config["stack"])),
        ("AI", ", ".join(config["ai_stack"])),
    ]
    stat_line = (
        f'{stats["public_repos"]} repos  ·  {stats["stars_received"]} stars  ·  '
        f'{stats["followers"]} followers  ·  {stats["public_commits_365d"]} public commits / 365d'
    )
    portrait = ascii_art.rstrip().splitlines()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720" role="img" aria-labelledby="title desc">
  <title id="title">Shivam Chopra GitHub profile</title>
  <desc id="desc">Terminal-style profile card for Shivam Chopra, Founder and AI Product Builder at illusionArt AI.</desc>
  <style>
    .mono {{ font: 18px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; fill: {c["text"]}; }}
    .small {{ font-size: 15px; }} .portrait {{ font-size: 13px; fill: {c["blue"]}; }}
    .label {{ fill: {c["accent"]}; font-weight: 700; }} .muted {{ fill: {c["muted"]}; }}
  </style>
  <rect width="1200" height="720" rx="28" fill="{c["background"]}"/>
  <rect x="25" y="25" width="1150" height="670" rx="18" fill="{c["panel"]}" stroke="{c["border"]}" stroke-width="2"/>
  <circle cx="62" cy="61" r="8" fill="{c["red"]}"/><circle cx="88" cy="61" r="8" fill="{c["yellow"]}"/><circle cx="114" cy="61" r="8" fill="{c["accent"]}"/>
  <text x="600" y="67" text-anchor="middle" class="mono small muted">{safe(config["username"])} — profile</text>
  <line x1="25" y1="94" x2="1175" y2="94" stroke="{c["border"]}" stroke-width="2"/>
  <text x="65" y="137" class="mono"><tspan class="label">{safe(config["username"])}@{safe(config["terminal_host"])}</tspan><tspan class="muted">:~$ whoami</tspan></text>
  <text class="mono portrait">{tspan_lines(portrait, 68, 182, 15)}</text>
  <text x="550" y="186" class="mono" font-size="26" font-weight="700">{safe(config["name"])}</text>
  <text class="mono small">{detail_lines(details, 550, 228, 39)}</text>
  <line x1="550" y1="557" x2="1128" y2="557" stroke="{c["border"]}"/>
  <text x="550" y="591" class="mono small"><tspan class="label">Web         </tspan>{safe(config["website"])}  ·  {safe(config["company_website"])}</text>
  <text x="550" y="622" class="mono small"><tspan class="label">Connect     </tspan>{safe(config["linkedin"])}</text>
  <rect x="55" y="650" width="1090" height="1" fill="{c["border"]}"/>
  <text x="600" y="677" text-anchor="middle" class="mono small muted">{safe(stat_line)}  ·  building since {safe(stats["account_year"])}</text>
</svg>
'''


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> None:
    config = load_json(CONFIG_PATH)
    previous = load_json(STATS_PATH) if STATS_PATH.exists() else {}
    ascii_art = ASCII_PATH.read_text(encoding="utf-8")
    stats = public_stats(os.environ.get("GITHUB_USERNAME", config["username"]), previous)
    outputs = {
        ROOT / "assets" / "profile-dark.svg": render_svg(config, stats, ascii_art, "dark"),
        ROOT / "assets" / "profile-light.svg": render_svg(config, stats, ascii_art, "light"),
        STATS_PATH: json.dumps(stats, indent=2, sort_keys=True) + "\n",
    }
    for path, content in outputs.items():
        atomic_write(path, content)
        print(f"updated {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
