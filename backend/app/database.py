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
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

client = httpx.Client(base_url=f"{SUPABASE_URL}/rest/v1", headers=HEADERS, timeout=30)
