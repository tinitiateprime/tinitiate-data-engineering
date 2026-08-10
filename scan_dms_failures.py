from unittest.mock import MagicMock, patch

import db.connection as conn_module
import psycopg2
import pytest
from core.exceptions import DatabaseConnectionError, ExternalServiceError
from db.connection import (
    TS_IDLE,
    TS_INERROR,
    TS_INTRANS,
    TS_UNKNOWN,
    _log_pg_error,
    execute_query,
    get_db_connection,
    get_pool,
    ping_db,
    ping_db_extended,
)
from psycopg2 import pool


@pytest.fixture(autouse=True)
def reset_pool():
    """Ensures the per-database connection pool cache is reset between tests."""
    conn_module._pools = {}
    yield
    conn_module._pools = {}


@pytest.fixture
def mock_settings(mocker):
    settings_mock = mocker.patch("db.connection.settings", autospec=False)
    settings_mock.DATABASES = {
        "mtdm": {
            "dbname": "test_db",
            "user": "test_user",
            "password": "test_password",
            "host": "test_host",
            "port": 5432,
            "connect_timeout": 30,
            "statement_timeout_ms": 10,
            "maxconn": 5,
        },
        "mtdm_synth": {
            "dbname": "test_synth_db",
            "user": "test_synth_user",
            "password": "test_synth_password",
            "host": "test_synth_host",
            "port": 5432,
            "connect_timeout": 30,
            "statement_timeout_ms": 10,
            "maxconn": 5,
        },
    }
    settings_mock.DEFAULT_PAGE_SIZE = 50
    return settings_mock


def test_get_pool_success(mock_settings, mocker):
    mock_simple_pool = mocker.patch("db.connection.pool.SimpleConnectionPool")
    mock_instance = MagicMock()
    mock_simple_pool.return_value = mock_instance

    p = get_pool("mtdm")

    assert p == mock_instance
    mock_simple_pool.assert_called_once_with(
        minconn=1,
        maxconn=5,
        dbname="test_db",
        user="test_user",
        password="test_password",
        host="test_host",
        port=5432,
        connect_timeout=30,
        options="-c statement_timeout=10",
    )

    # Second call for the same db should return the same cached pool
    p2 = get_pool("mtdm")
    assert p2 == p
    assert mock_simple_pool.call_count == 1


def test_get_pool_defaults_to_mtdm(mock_settings, mocker):
    """Calling get_pool() with no argument should resolve to the mtdm database."""
    mock_simple_pool = mocker.patch("db.connection.pool.SimpleConnectionPool")
    mock_instance = MagicMock()
    mock_simple_pool.return_value = mock_instance

    p = get_pool()

    assert p == mock_instance
    assert mock_simple_pool.call_args[1]["dbname"] == "test_db"


def test_get_pool_synth_uses_synth_settings(mock_settings, mocker):
    mock_simple_pool = mocker.patch("db.connection.pool.SimpleConnectionPool")
    mock_instance = MagicMock()
    mock_simple_pool.return_value = mock_instance

    p = get_pool("mtdm_synth")

    assert p == mock_instance
    mock_simple_pool.assert_called_once_with(
        minconn=1,
        maxconn=5,
        dbname="test_synth_db",
        user="test_synth_user",
        password="test_synth_password",
        host="test_synth_host",
        port=5432,
        connect_timeout=30,
        options="-c statement_timeout=10",
    )


def test_get_pool_multiple_databases_are_independent(mock_settings, mocker):
    """mtdm and mtdm_synth pools should be created and cached independently."""
    mock_simple_pool = mocker.patch("db.connection.pool.SimpleConnectionPool")
    mock_mtdm_instance = MagicMock()
    mock_synth_instance = MagicMock()
    mock_simple_pool.side_effect = [mock_mtdm_instance, mock_synth_instance]

    p_mtdm = get_pool("mtdm")
    p_synth = get_pool("mtdm_synth")

    assert p_mtdm == mock_mtdm_instance
    assert p_synth == mock_synth_instance
    assert p_mtdm != p_synth
    assert mock_simple_pool.call_count == 2

    # Re-requesting either should hit the cache, not create a new pool
    assert get_pool("mtdm") == p_mtdm
    assert get_pool("mtdm_synth") == p_synth
    assert mock_simple_pool.call_count == 2


def test_get_pool_unknown_database(mock_settings, mocker):
    mocker.patch("db.connection.pool.SimpleConnectionPool")

    with pytest.raises(DatabaseConnectionError, match="Unknown database"):
        get_pool("not_a_real_db")


def test_get_pool_no_maxconn(mock_settings, mocker):
    # Delete the maxconn setting to test the fallback behavior
    del mock_settings.DATABASES["mtdm"]["maxconn"]
    mock_simple_pool = mocker.patch("db.connection.pool.SimpleConnectionPool")

    get_pool("mtdm")

    # Assert maxconn defaults to 10
    assert mock_simple_pool.call_args[1]["maxconn"] == 10


def test_get_pool_exception(mock_settings, mocker):
    mocker.patch(
        "db.connection.pool.SimpleConnectionPool", side_effect=Exception("DB Error")
    )

    with pytest.raises(
        DatabaseConnectionError, match="Could not connect to the database cluster."
    ):
        get_pool("mtdm")


@pytest.fixture
def mock_pool_instance(mocker):
    mock_pool = MagicMock()
    conn_module._pools = {"mtdm": mock_pool}
    return mock_pool


@pytest.fixture
def mock_synth_pool_instance(mocker):
    mock_pool = MagicMock()
    conn_module._pools["mtdm_synth"] = mock_pool
    return mock_pool


def test_get_db_connection_success(mock_pool_instance):
    mock_conn = MagicMock()
    mock_conn.closed = 0
    mock_conn.get_transaction_status.return_value = TS_IDLE
    mock_pool_instance.getconn.return_value = mock_conn

    with get_db_connection() as conn:
        assert conn == mock_conn

    mock_pool_instance.putconn.assert_called_once_with(mock_conn)


def test_get_db_connection_uses_requested_database(
    mock_pool_instance, mock_synth_pool_instance
):
    mock_conn = MagicMock()
    mock_conn.closed = 0
    mock_conn.get_transaction_status.return_value = TS_IDLE
    mock_synth_pool_instance.getconn.return_value = mock_conn

    with get_db_connection("mtdm_synth") as conn:
        assert conn == mock_conn

    mock_synth_pool_instance.putconn.assert_called_once_with(mock_conn)
    mock_pool_instance.getconn.assert_not_called()


def test_get_db_connection_closed(mock_pool_instance):
    mock_conn_closed = MagicMock()
    mock_conn_closed.closed = 1

    mock_conn_open = MagicMock()
    mock_conn_open.closed = 0
    mock_conn_open.get_transaction_status.return_value = TS_IDLE

    mock_pool_instance.getconn.side_effect = [mock_conn_closed, mock_conn_open]

    with get_db_connection() as conn:
        assert conn == mock_conn_open

    mock_pool_instance.putconn.assert_any_call(mock_conn_closed, close=True)
    mock_pool_instance.putconn.assert_called_with(mock_conn_open)


def test_get_db_connection_closed_putconn_exception(mock_pool_instance):
    mock_conn_closed = MagicMock()
    mock_conn_closed.closed = 1

    mock_conn_open = MagicMock()
    mock_conn_open.closed = 0
    mock_conn_open.get_transaction_status.return_value = TS_IDLE

    mock_pool_instance.getconn.side_effect = [mock_conn_closed, mock_conn_open]

    def putconn_side_effect(c, close=False):
        if c == mock_conn_closed and close:
            raise Exception("Putconn closed error")

    mock_pool_instance.putconn.side_effect = putconn_side_effect

    with get_db_connection() as conn:
        assert conn == mock_conn_open


def test_get_db_connection_status_unknown(mock_pool_instance):
    mock_conn = MagicMock()
    mock_conn.closed = 0
    mock_conn.get_transaction_status.side_effect = Exception("Status error")
    mock_pool_instance.getconn.return_value = mock_conn

    with get_db_connection() as conn:
        assert conn == mock_conn


def test_get_db_connection_status_intrans(mock_pool_instance):
    """Test connection handling when status is TS_INTRANS."""
    mock_conn = MagicMock()
    mock_conn.closed = 0
    mock_conn.get_transaction_status.return_value = TS_INTRANS
    mock_pool_instance.getconn.return_value = mock_conn

    with get_db_connection() as conn:
        assert conn == mock_conn

    mock_conn.rollback.assert_called_once()


def test_get_db_connection_status_inerror(mock_pool_instance):
    mock_conn = MagicMock()
    mock_conn.closed = 0
    mock_conn.get_transaction_status.return_value = TS_INERROR
    mock_pool_instance.getconn.return_value = mock_conn

    with get_db_connection() as conn:
        assert conn == mock_conn

    mock_conn.rollback.assert_called_once()


def test_get_db_connection_status_inerror_rollback_exception(mock_pool_instance):
    mock_conn_err = MagicMock()
    mock_conn_err.closed = 0
    mock_conn_err.get_transaction_status.return_value = TS_INERROR
    mock_conn_err.rollback.side_effect = Exception("Rollback error")

    mock_conn_new = MagicMock()
    mock_conn_new.closed = 0
    mock_conn_new.get_transaction_status.return_value = TS_IDLE

    mock_pool_instance.getconn.side_effect = [mock_conn_err, mock_conn_new]

    with get_db_connection() as conn:
        assert conn == mock_conn_new

    mock_pool_instance.putconn.assert_any_call(mock_conn_err, close=True)


def test_get_db_connection_finally_putconn_exception(mock_pool_instance):
    mock_conn = MagicMock()
    mock_conn.closed = 0
    mock_conn.get_transaction_status.return_value = TS_IDLE
    mock_pool_instance.getconn.return_value = mock_conn

    def putconn_side_effect(c, close=False):
        if not close:
            raise Exception("Putconn error")

    mock_pool_instance.putconn.side_effect = putconn_side_effect

    with get_db_connection() as conn:
        pass

    mock_pool_instance.putconn.assert_any_call(mock_conn, close=True)


def test_get_db_connection_finally_putconn_both_exceptions(mock_pool_instance):
    mock_conn = MagicMock()
    mock_conn.closed = 0
    mock_conn.get_transaction_status.return_value = TS_IDLE
    mock_pool_instance.getconn.return_value = mock_conn

    mock_pool_instance.putconn.side_effect = Exception("All putconns fail")

    with get_db_connection() as conn:
        pass


@pytest.fixture
def mock_db_context(mocker):
    mock_conn_ctx = MagicMock()
    mock_conn = MagicMock()
    mock_conn_ctx.__enter__.return_value = mock_conn
    mocker.patch("db.connection.get_db_connection", return_value=mock_conn_ctx)
    return mock_conn


def test_execute_query_success(mock_db_context):
    mock_cur = MagicMock()
    mock_cur.description = True
    mock_cur.fetchall.return_value = [{"row_id": 1}, {"row_id": 2}]

    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    res = execute_query("SELECT 1", limit=2)

    assert len(res["items"]) == 2
    assert res["page"]["cursor"] == "2"
    assert res["page"]["has_more"] is True
    mock_db_context.commit.assert_called_once()


def test_execute_query_result_less_than_limit(mock_db_context):
    """Test query execution when result count is less than the limit."""
    mock_cur = MagicMock()
    mock_cur.description = True
    mock_cur.fetchall.return_value = [{"row_id": 1}]

    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    res = execute_query("SELECT 1", limit=10)

    assert len(res["items"]) == 1
    assert res["page"]["has_more"] is False


def test_execute_query_success_id_fallback(mock_db_context):
    mock_cur = MagicMock()
    mock_cur.description = True
    mock_cur.fetchall.return_value = [{"id": 42}]

    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    res = execute_query("SELECT 1", limit=1)

    assert res["page"]["cursor"] == "42"
    assert res["page"]["has_more"] is True


def test_execute_query_no_id_val(mock_db_context):
    mock_cur = MagicMock()
    mock_cur.description = True
    mock_cur.fetchall.return_value = [{"other_key": 42}]

    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    res = execute_query("SELECT 1", limit=1)

    assert res["page"]["cursor"] is None
    assert res["page"]["has_more"] is False


def test_execute_query_no_limit(mock_db_context):
    mock_cur = MagicMock()
    mock_cur.description = True
    mock_cur.fetchall.return_value = [{"id": 42}]

    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    res = execute_query("SELECT 1", limit=None)

    assert res["page"]["cursor"] is None
    assert res["page"]["has_more"] is False


def test_execute_query_no_description(mock_db_context):
    mock_cur = MagicMock()
    mock_cur.description = None

    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    res = execute_query("INSERT 1")

    assert res["items"] == []


def test_execute_query_generic_exception(mock_db_context):
    mock_cur = MagicMock()
    mock_cur.execute.side_effect = Exception("Generic error")

    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    with pytest.raises(Exception, match="Generic error"):
        execute_query("SELECT 1")


def test_execute_query_uses_requested_database(mocker):
    mock_conn_ctx = MagicMock()
    mock_conn = MagicMock()
    mock_conn_ctx.__enter__.return_value = mock_conn
    mock_get_db_connection = mocker.patch(
        "db.connection.get_db_connection", return_value=mock_conn_ctx
    )

    mock_cur = MagicMock()
    mock_cur.description = None
    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_conn.cursor.return_value = mock_conn_cursor_ctx

    execute_query("SELECT 1", db_name="mtdm_synth")

    mock_get_db_connection.assert_called_once_with("mtdm_synth")


def test_ping_db_success(mock_db_context):
    mock_cur = MagicMock()
    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    assert ping_db() is True
    mock_cur.execute.assert_called_once_with("SELECT 1")


def test_ping_db_exception(mock_db_context):
    mock_cur = MagicMock()
    mock_cur.execute.side_effect = Exception("ping error")
    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    assert ping_db() is False


def test_ping_db_extended_success(mock_db_context):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = ("db1", 10, 2, 8, 0, "00:00:01")

    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    res = ping_db_extended()

    assert res == {
        "database": "db1",
        "total_connections": 10,
        "active_queries": 2,
        "idle_connections": 8,
        "waiting_connections": 0,
        "longest_running_query": "00:00:01",
    }


def test_ping_db_extended_no_data(mock_db_context):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = None

    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    res = ping_db_extended()

    assert res == {"error": "No stats returned"}


def test_ping_db_extended_transient_failure(mock_db_context, mocker):
    mock_sleep = mocker.patch("time.sleep")
    mock_cur = MagicMock()
    mock_cur.execute.side_effect = [Exception("error1"), None]  # Fail then succeed
    mock_cur.fetchone.return_value = ("db1", 10, 2, 8, 0, "00:00:01")

    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    res = ping_db_extended(retries=2, backoff_seconds=0.1)

    assert "database" in res
    mock_sleep.assert_called_once_with(0.1)


def test_ping_db_extended_all_failures(mock_db_context, mocker):
    mock_sleep = mocker.patch("time.sleep")
    mock_cur = MagicMock()
    mock_cur.execute.side_effect = Exception("error1")

    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    res = ping_db_extended(retries=2, backoff_seconds=0.1)

    assert res == {}
    mock_sleep.assert_called_once()


def test_ping_db_extended_no_retries(mock_db_context):
    """Test extended ping with zero retries."""
    mock_cur = MagicMock()
    mock_cur.execute.side_effect = Exception("error")

    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_db_context.cursor.return_value = mock_conn_cursor_ctx

    res = ping_db_extended(retries=0)
    assert res == {}


def test_ping_db_extended_uses_requested_database(mocker):
    mock_conn_ctx = MagicMock()
    mock_conn = MagicMock()
    mock_conn_ctx.__enter__.return_value = mock_conn
    mock_get_db_connection = mocker.patch(
        "db.connection.get_db_connection", return_value=mock_conn_ctx
    )

    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = ("db1", 10, 2, 8, 0, "00:00:01")
    mock_conn_cursor_ctx = MagicMock()
    mock_conn_cursor_ctx.__enter__.return_value = mock_cur
    mock_conn.cursor.return_value = mock_conn_cursor_ctx

    ping_db_extended(db_name="mtdm_synth")

    mock_get_db_connection.assert_called_once_with("mtdm_synth")
