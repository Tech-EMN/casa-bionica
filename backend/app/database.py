"""Casa Biônica — Database client via Supabase PostgREST API.

Evita IPv6/asyncpg/psycopg2 connection issues.
Usa HTTP REST na porta 443 (IPv4 via Cloudflare).
"""

import os

import httpx

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "https://rkiclxviqinciwwumwfb.supabase.co",
)
SUPABASE_KEY = ***"SUPABASE_KEY", "")


def get_headers():
    if not SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_KEY env var is empty. "
            "Add in Railway → Variables → SUPABASE_KEY=sb_sec… → Deploy"
        )
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def get_client():
    return httpx.Client(
        base_url=f"{SUPABASE_URL}/rest/v1",
        headers=get_headers(),
        timeout=30,
    )
