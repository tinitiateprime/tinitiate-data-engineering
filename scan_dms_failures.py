# tests/unit/test_db_connection.py

from unittest.mock import MagicMock, patch

import pytest

from db.connection import ping_db_extended


def test_ping_db_extended_success(mocker):
    """
    Test that successful query results are correctly mapped
    to the response dictionary.
    """

    mock_conn = MagicMock()
    mock_cur = mock_conn.cursor.return_value.__enter__.return_value

    mock_cur.fetchone.return_value = (
        "test_db",
        10,
        2,
        8,
        0,
        "00:00:01",
    )

    with patch("db.connection.get_db_connection") as mock_get_conn:
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        result = ping_db_extended()

        assert result["database"] == "test_db"
        assert result["total_connections"] == 10
        assert result["active_queries"] == 2
        assert result["idle_connections"] == 8
        assert result["waiting_connections"] == 0
        assert result["longest_running_query"] == "00:00:01"

        mock_cur.execute.assert_called_once()


def test_ping_db_extended_no_row(mocker):
    """
    Test behavior when the query succeeds but returns no row.
    """

    mock_conn = MagicMock()
    mock_cur = mock_conn.cursor.return_value.__enter__.return_value

    mock_cur.fetchone.return_value = None

    with patch("db.connection.get_db_connection") as mock_get_conn:
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        result = ping_db_extended()

        assert result == {"error": "No stats returned"}


def test_ping_db_extended_exception(mocker):
    """
    Verify that an exception in the DB layer returns
    an empty dictionary after retries.
    """

    with patch(
        "db.connection.get_db_connection",
        side_effect=Exception("Connection Timeout"),
    ), patch("db.connection.time.sleep"):

        result = ping_db_extended()

        assert result == {}


def test_get_pool_returns_pool():
    """
    Test get_pool creates and returns the connection pool
    for the default database.
    """

    import db.connection as conn_module

    # Current implementation uses _pools, not _pool.
    conn_module._pools.clear()

    try:
        # connection.py imports:
        # from psycopg2 import errorcodes, pool
        #
        # Therefore patch pool where connection.py uses it.
        with patch(
            "db.connection.pool.SimpleConnectionPool"
        ) as mock_pool:

            mock_pool_instance = MagicMock()
            mock_pool.return_value = mock_pool_instance

            result = conn_module.get_pool()

            assert result is not None
            assert result is mock_pool_instance

            # Verify that the pool was cached under "default"
            assert conn_module._pools["default"] is mock_pool_instance

            mock_pool.assert_called_once()

    finally:
        # Do not allow this test's cached mock pool to affect later tests.
        conn_module._pools.clear()


def test_ping_db_extended_partial_data(mocker):
    """
    Test handling of partial data returned by the database query.
    """

    mock_conn = MagicMock()
    mock_cur = mock_conn.cursor.return_value.__enter__.return_value

    mock_cur.fetchone.return_value = (
        "test_db",
        5,
        1,
        None,
        None,
        None,
    )

    with patch("db.connection.get_db_connection") as mock_get_conn:
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        result = ping_db_extended()

        assert result["database"] == "test_db"
        assert result["total_connections"] == 5
        assert result["active_queries"] == 1
        assert result["idle_connections"] is None
        assert result["waiting_connections"] is None
        assert result["longest_running_query"] is None

        mock_cur.execute.assert_called_once()
