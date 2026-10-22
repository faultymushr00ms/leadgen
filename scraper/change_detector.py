"""
Page change detector for nightly scan.
Hashes source pages and only re-parses pages that changed.
Extracts rates, supplier names, and term dates with regex.
Optional Ollama summarizer — skipped if not running.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import date
from typing import Optional

import requests

HASH_STORE = os.path.join("data", "cache", "page_hashes.json")
RATE_RE = re.compile(r"(\d+\.\d+)\s*[¢c](?:/kWh)?", re.IGNORECASE)
TERM_RE = re.compile(
    r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"\s+\d{1,2},?\s+20\d{2}",
    re.IGNORECASE,
)
SUPPLIER_RE = re.compile(
    r"\b(Dynegy|Constellation|NRG|Vistra|Nextera|AEP Energy|"
    r"Direct Energy|Spark Energy|Major Energy|Verde Energy|"
    r"Discount Power|Shipley Energy|FirstEnergy Solutions)\b",
    re.IGNORECASE,
)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
DELAY = 2.0
TIMEOUT = 20
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"


def _load_hashes() -> dict:
    if os.path.exists(HASH_STORE):
        with open(HASH_STORE) as f:
            return json.load(f)
    return {}


def _save_hashes(hashes: dict) -> None:
    os.makedirs(os.path.dirname(HASH_STORE), exist_ok=True)
    with open(HASH_STORE, "w") as f:
        json.dump(hashes, f, indent=2)


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()[:16]


def _extract(text: str) -> dict:
    rates = [float(m) for m in RATE_RE.findall(text) if 5.0 <= float(m) <= 20.0]
    suppliers = list(dict.fromkeys(SUPPLIER_RE.findall(text)))
    terms = TERM_RE.findall(text)
    return {
        "rates_found": rates,
        "suppliers_found": suppliers,
        "term_dates_found": terms,
    }


def _ollama_summary(text: str, zone_name: str) -> Optional[str]:
    snippet = text[:3000]
    prompt = (
        f"Summarize in ONE plain sentence what this web page says about the energy "
        f"aggregation program for {zone_name}. Do not invent rates or dates. "
        f"If you cannot tell, say 'No clear aggregation information found.'\n\n{snippet}"
    )
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception:
        pass
    return None


def _ollama_available() -> bool:
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def fetch_and_detect(
    zone_name: str,
    url: str,
    use_ollama: bool = True,
) -> dict:
    """
    Fetch url, compare hash, extract facts if changed.
    Returns a result dict — never raises.
    """
    result: dict = {
        "zone": zone_name,
        "url": url,
        "fetched_at": date.today().isoformat(),
        "changed": False,
        "skipped": False,
        "error": None,
        "extracted": {},
        "ollama_summary": None,
    }

    if not url:
        result["skipped"] = True
        result["error"] = "no source URL"
        return result

    try:
        time.sleep(DELAY)
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        text = resp.text
    except Exception as exc:
        result["error"] = str(exc)
        return result

    current_hash = _hash(text)
    hashes = _load_hashes()
    stored_hash = hashes.get(url)

    if stored_hash == current_hash:
        result["changed"] = False
        return result

    result["changed"] = True
    result["old_hash"] = stored_hash
    result["new_hash"] = current_hash
    result["extracted"] = _extract(text)

    if use_ollama and _ollama_available():
        result["ollama_summary"] = _ollama_summary(text, zone_name)

    hashes[url] = current_hash
    _save_hashes(hashes)
    return result
