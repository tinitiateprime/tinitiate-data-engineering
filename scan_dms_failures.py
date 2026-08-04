# main-function\mt-dm-lambda-src\db\connection.py
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional

import psycopg2

# Import from your new Layer 0
from core.config import settings
from core.exceptions import DatabaseConnectionError, ExternalServiceError
from core.logging import logger
from core.utils import time_block
from psycopg2 import errorcodes, pool
from psycopg2 import extensions as ext
from psycopg2.extras import RealDictCursor

# ---------------------------------------------------------------------------
# Version-agnostic transaction status constants
# ---------------------------------------------------------------------------
TS_IDLE = getattr(ext, "TRANSACTION_STATUS_IDLE", getattr(ext, "STATUS_READY", 0))
TS_ACTIVE = getattr(ext, "TRANSACTION_STATUS_ACTIVE", getattr(ext, "STATUS_BEGIN", 1))
TS_INTRANS = getattr(
    ext, "TRANSACTION_STATUS_INTRANS", getattr(ext, "STATUS_IN_TRANSACTION", 2)
)
TS_INERROR = getattr(ext, "TRANSACTION_STATUS_INERROR", 3)
TS_UNKNOWN = getattr(ext, "TRANSACTION_STATUS_UNKNOWN", 4)

# ---------------------------------------------------------------------------
# Connection pools, keyed by database name (e.g. "default", "synth")
# ---------------------------------------------------------------------------
_pools: Dict[str, Any] = {}


def get_pool(db_key: str = "default"):
    """
    Returns (creating if necessary) the connection pool for the given
    database key. db_key must exist in settings.DATABASES.
    """
    global _pools
    if db_key not in _pools:
        try:
            # logger.debug(f"Initializing database connection pool for '{db_key}'...")
            cfg = settings.DATABASES[db_key]
            _pools[db_key] = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=(
                    settings.DB_POOL_MAXCONN
                    if hasattr(settings, "DB_POOL_MAXCONN")
                    else 10
                ),
                dbname=cfg["dbname"],
                user=cfg["user"],
                password=cfg["password"],
                host=cfg["host"],
                port=cfg["port"],
                connect_timeout=settings.DB_CONNECT_TIMEOUT_SECONDS,
                options=f"-c statement_timeout={settings.DB_STATEMENT_TIMEOUT_MS}",
            )
            # logger.debug(f"Connection pool established for '{db_key}'.")
        except Exception as e:
            logger.exception(
                "Failed to create connection pool for '%s'. Root cause: %s",
                db_key,
                e,
            )
            raise DatabaseConnectionError(
                f"Could not connect to the database cluster ('{db_key}')."
            ) from e
    return _pools[db_key]


@contextmanager
def get_db_connection(db_key: str = "default"):
    p = get_pool(db_key)
    conn = p.getconn()
    try:
        # Check if connection is closed
        if getattr(conn, "closed", 0):
            try:
                p.putconn(conn, close=True)
            except Exception:
                pass
            conn = p.getconn()

        def _status(c):
            try:
                return c.get_transaction_status()
            except Exception:
                return TS_UNKNOWN

        status = _status(conn)
        if status in (TS_INERROR, TS_INTRANS):
            logger.debug(f"Cleaning up borrowed conn (status={status})")
            try:
                conn.rollback()
            except Exception:
                p.putconn(conn, close=True)
                conn = p.getconn()

        yield conn

    finally:
        try:
            p.putconn(conn)
        except Exception:
            try:
                p.putconn(conn, close=True)
            except Exception:
                pass


def _log_pg_error(
    e: psycopg2.Error,
    cur=None,
    params: Optional[Dict] = None,
    prefix: str = "PostgreSQL error",
) -> dict:  # pragma: no cover
    """
    Logs the error and returns a dictionary of diagnostic details for API responses.
    """
    # 1. Extract basic error info
    err_code = getattr(e, "pgcode", "UNKNOWN")
    err_name = (
        errorcodes.lookup(err_code) if err_code != "UNKNOWN" else "UNDEFINED_ERROR"
    )

    # 2. Extract deep diagnostics from the 'diag' attribute
    # These fields are populated by the PostgreSQL server
    diag = getattr(e, "diag", None)
    details_map = {
        "code": err_code,
        "type": err_name,
        "message": str(e).split("\n")[0].strip(),  # First line is usually the summary
        "constraint": getattr(diag, "constraint_name", None),
        "column": getattr(diag, "column_name", None),
        "datatype": getattr(diag, "datatype_name", None),
    }

    # 3. Log the error internally for server-side tracking
    log_context = {**details_map, "params": params}
    if cur and hasattr(cur, "query") and cur.query:
        log_context["executed_query"] = (
            cur.query.decode("utf-8") if isinstance(cur.query, bytes) else cur.query
        )

    logger.error(f"{prefix}: {details_map['message']}", extra={"db_error": log_context})

    # 4. Return the filtered dict (omit internal query/params for security)
    return {k: v for k, v in details_map.items() if v is not None}


def execute_query(
    query: str,
    params: Optional[Dict[Any, Any]] = None,
    limit: Optional[int] = settings.DEFAULT_PAGE_SIZE,
    cursor_factory=RealDictCursor,
    db_key: str = "default",
):
    with get_db_connection(db_key) as conn:
        prev_autocommit = conn.autocommit
        conn.autocommit = False
        cur = None

        logger.debug(
            f"DB - execute_query plan: {query}, {params}, {limit}, {cursor_factory}"
        )

        try:
            with conn.cursor(cursor_factory=cursor_factory) as cur:
                with time_block("DB Execution"):
                    cur.execute(query, params)
                    items = list(cur.fetchall()) if cur.description else []

                # Pagination logic
                next_token = None
                if limit is not None and len(items) >= limit:
                    last = items[-1]
                    id_val = last.get("row_id") or last.get("id")
                    if id_val:
                        next_token = str(id_val)

                conn.commit()

                return {
                    "items": items,
                    "page": {"cursor": next_token, "has_more": next_token is not None},
                }

        except (psycopg2.Error, Exception) as e:
            try:
                conn.rollback()
            except Exception:  # pragma: no cover
                pass

            if isinstance(e, psycopg2.Error):  # pragma: no cover
                # Capture the diagnostic dictionary
                error_details = _log_pg_error(e, cur, params)

                # Pass details to your custom exception
                logger.exception(
                    f"Database query failed: {e}, raising ExternalServiceError"
                )
                raise ExternalServiceError(
                    message=f"Database query failed: {e.pgcode}",
                    details=error_details,  # Ensure your ExternalServiceError accepts this
                ) from e
            else:
                logger.exception(f"Internal processing error: {e}")
                raise
        finally:
            conn.autocommit = prev_autocommit


def ping_db(db_key: str = "default") -> bool:
    """Verifies the database connection is alive."""
    try:
        with get_db_connection(db_key) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def ping_db_extended(
    db_key: str = "default", retries: int = 3, backoff_seconds: float = 0.25
) -> dict:
    """
    Performs a deep health check by querying Postgres activity stats.
    Retries transient failures during cold starts, then returns DB metrics or an error map.
    """
    sql = """
        SELECT
            datname AS database_name,
            count(*)::int AS total_connections,
            count(*) FILTER (WHERE state = 'active')::int AS active_queries,
            count(*) FILTER (WHERE state = 'idle')::int AS idle_connections,
            count(*) FILTER (WHERE wait_event IS NOT NULL)::int AS waiting_connections,
            MAX(now() - query_start) FILTER (WHERE state = 'active')::text AS longest_running_query
        FROM pg_stat_activity
        WHERE datname = current_database()
        GROUP BY datname;
    """

    for attempt in range(1, retries + 1):
        try:
            with get_db_connection(db_key) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    row = cur.fetchone()
                    if row:
                        return {
                            "database": row[0],
                            "total_connections": row[1],
                            "active_queries": row[2],
                            "idle_connections": row[3],
                            "waiting_connections": row[4],
                            "longest_running_query": row[5],
                        }
                    return {"error": "No stats returned"}
        except Exception as e:
            if attempt < retries:
                logger.warning(
                    "Deep health check transient failure (attempt %s/%s): %s",
                    attempt,
                    retries,
                    str(e),
                )
                time.sleep(backoff_seconds * attempt)
                continue
            logger.exception("Deep health check failed after retries: %s", e)
            return {}
    return {}
