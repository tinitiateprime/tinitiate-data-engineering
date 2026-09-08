# tests/unit/test_db_connection.py

from unittest.mock import MagicMock, patch

import pytest

from db.connection import ping_db_extended


def test_ping_db_extended_success(mocker):
    """
    Test that successful query results are correctly mapped to the response dict.
    """

    # Mock the connection context manager
    mock_conn = MagicMock()
    mock_cur = mock_conn.cursor.return_value.__enter__.return_value

    # Simulate the tuple returned by the SQL query in ping_db_extended
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
        assert "longest_running_query" in result

        mock_cur.execute.assert_called_once()


def test_ping_db_extended_no_row(mocker):
    """
    Test the behavior when the query executes but returns no rows.
    """

    mock_conn = MagicMock()
    mock_cur = mock_conn.cursor.return_value.__enter__.return_value

    # No row found
    mock_cur.fetchone.return_value = None

    with patch("db.connection.get_db_connection") as mock_get_conn:
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        result = ping_db_extended()

        assert result == {"error": "No stats returned"}


def test_ping_db_extended_exception(mocker):
    """
    Verify that an exception in the DB layer returns an empty dict (unhealthy).
    """

    with patch(
        "db.connection.get_db_connection",
        side_effect=Exception("Connection Timeout"),
    ):
        result = ping_db_extended()

        assert result == {}


def test_get_pool_returns_pool():
    """
    Test get_pool returns a connection pool.
    """

    # IMPORTANT:
    # Import the module itself so that we reset and test the SAME module state.
    import db.connection as conn_module

    # Patch where SimpleConnectionPool is USED.
    with patch("db.connection.SimpleConnectionPool") as mock_pool:

        # Mock pool instance
        mock_pool_instance = MagicMock()
        mock_pool.return_value = mock_pool_instance

        # Reset cached pool to force get_pool() to initialize a new one
        conn_module._pool = None

        pool = conn_module.get_pool()

        assert pool is not None
        assert pool is mock_pool_instance

        # Confirm exactly one pool was created
        mock_pool.assert_called_once()


def test_ping_db_extended_partial_data(mocker):
    """
    Test handling of partial data from database query.
    """

    mock_conn = MagicMock()
    mock_cur = mock_conn.cursor.return_value.__enter__.return_value

    # Return partial data (missing some fields)
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

        mock_cur.execute.assert_called_once()
