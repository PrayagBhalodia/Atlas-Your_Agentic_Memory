"""ATLAS — Track A shared DB connection.

Single place every Track A script/tool gets a CockroachDB connection, so TLS and DSN
quirks are handled once. search / fetch / record all import get_conn() from here.

Why the sslrootcert normalization:
  CockroachDB Cloud strings default to `sslmode=verify-full`, which makes libpq look for
  a CA file at ~/.postgresql/root.crt. That file doesn't exist locally. Cockroach Cloud
  certs ARE signed by a public CA, but we can't just use `sslrootcert=system`: psycopg2's
  wheel bundles its own OpenSSL whose compiled-in default CA path isn't Ubuntu's
  /etc/ssl/certs, so `system` resolves to an empty trust store and verification fails.
  So we point sslrootcert at the actual OS CA bundle file explicitly — full verification,
  no cert download, works regardless of OpenSSL's compiled default.
"""
import os
import threading
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from dotenv import load_dotenv
import psycopg2
from psycopg2 import pool as _pg_pool

load_dotenv()

# Common OS CA bundle locations, most-specific first. Debian/Ubuntu ships the first one.
_CA_BUNDLES = [
    "/etc/ssl/certs/ca-certificates.crt",   # Debian/Ubuntu
    "/etc/pki/tls/certs/ca-bundle.crt",     # RHEL/Fedora
    "/etc/ssl/cert.pem",                     # macOS/BSD
]


def _system_ca_bundle() -> str | None:
    for path in _CA_BUNDLES:
        if os.path.exists(path):
            return path
    try:
        import certifi  # optional fallback if installed
        return certifi.where()
    except ImportError:
        return None


def _normalize_dsn(url: str) -> str:
    parts = urlparse(url)
    q = parse_qs(parts.query)
    if q.get("sslmode", ["verify-full"])[0] in ("verify-full", "verify-ca") \
            and "sslrootcert" not in q:
        bundle = _system_ca_bundle()
        if bundle:
            q["sslrootcert"] = [bundle]
    return urlunparse(parts._replace(query=urlencode(q, doseq=True)))


def get_dsn() -> str:
    url = os.getenv("COCKROACH_DATABASE_URL")
    if not url:
        raise SystemExit(
            "COCKROACH_DATABASE_URL is missing from .env.\n"
            "cockroachlabs.cloud → cluster 'atlasdb' → Connect → General connection string."
        )
    return _normalize_dsn(url)


# One pool for the whole process, so an agentic question (which fans out to many
# search/fetch/record calls across three agents) reuses a handful of connections
# instead of doing a fresh TLS+auth handshake to CockroachDB Serverless every call.
# Module state survives Streamlit reruns, so the pool persists across interactions.
_POOL_MIN = int(os.getenv("DB_POOL_MIN", "1"))
_POOL_MAX = int(os.getenv("DB_POOL_MAX", "8"))
_pool = None
_pool_lock = threading.Lock()


def _get_pool():
    global _pool
    if _pool is None:  # double-checked locking: only the first caller builds the pool
        with _pool_lock:
            if _pool is None:
                _pool = _pg_pool.ThreadedConnectionPool(_POOL_MIN, _POOL_MAX, get_dsn())
    return _pool


def get_conn():
    """Borrow a pooled psycopg2 connection (autocommit off). Return it with put_conn()."""
    return _get_pool().getconn()


def put_conn(conn) -> None:
    """Return a connection to the pool. putconn rolls back any open transaction; if the
    connection is already dead (e.g. the server dropped an idle link) it's discarded."""
    if conn is None:
        return
    _get_pool().putconn(conn, close=bool(getattr(conn, "closed", 0)))
