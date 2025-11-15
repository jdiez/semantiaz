"""Tests for database connections utility module."""

from unittest.mock import Mock, patch

import click
import pytest

from semantiaz.utils.database_connections import (
    create_database_connection,
    get_supported_backends,
    validate_backend_params,
)


class TestDatabaseConnections:
    """Test cases for database connection utilities."""

    def test_get_supported_backends(self):
        """Test getting list of supported backends."""
        backends = get_supported_backends()

        assert isinstance(backends, list)
        assert "postgres" in backends
        assert "mysql" in backends
        assert "sqlite" in backends
        assert "duckdb" in backends
        assert "bigquery" in backends
        assert "snowflake" in backends

    def test_validate_backend_params_postgres_with_connection_string(self):
        """Test PostgreSQL validation with connection string."""
        # Should not raise exception
        validate_backend_params("postgres", connection_string="postgresql://user:pass@host/db")

    def test_validate_backend_params_postgres_with_individual_params(self):
        """Test PostgreSQL validation with individual parameters."""
        # Should not raise exception
        validate_backend_params("postgres", host="localhost", user="user", password="pass", database="testdb")

    def test_validate_backend_params_postgres_missing_params(self):
        """Test PostgreSQL validation with missing parameters."""
        with pytest.raises(ValueError, match="PostgreSQL requires"):
            validate_backend_params("postgres", host="localhost")

    def test_validate_backend_params_sqlite(self):
        """Test SQLite validation."""
        # Should not raise exception
        validate_backend_params("sqlite", file_path="/path/to/db.sqlite")
        validate_backend_params("sqlite", database="testdb")

    def test_validate_backend_params_sqlite_missing_params(self):
        """Test SQLite validation with missing parameters."""
        with pytest.raises(ValueError, match="SQLite requires"):
            validate_backend_params("sqlite")

    def test_validate_backend_params_bigquery(self):
        """Test BigQuery validation."""
        # Should not raise exception
        validate_backend_params("bigquery", database="project-id")

    def test_validate_backend_params_bigquery_missing_params(self):
        """Test BigQuery validation with missing parameters."""
        with pytest.raises(ValueError, match="BigQuery requires"):
            validate_backend_params("bigquery")

    def test_validate_backend_params_snowflake(self):
        """Test Snowflake validation."""
        # Should not raise exception
        validate_backend_params(
            "snowflake", account="account", user="user", password="pass", warehouse="wh", database="db"
        )

    def test_validate_backend_params_snowflake_missing_params(self):
        """Test Snowflake validation with missing parameters."""
        with pytest.raises(ValueError, match="Snowflake requires"):
            validate_backend_params("snowflake", account="account", user="user")

    @patch("semantiaz.utils.database_connections.ibis.postgres.connect")
    def test_create_postgres_connection_with_string(self, mock_connect):
        """Test PostgreSQL connection creation with connection string."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        conn = create_database_connection(
            backend="postgres", database="testdb", connection_string="postgresql://user:pass@host/db"
        )

        assert conn == mock_conn
        mock_connect.assert_called_once_with("postgresql://user:pass@host/db")

    @patch("semantiaz.utils.database_connections.ibis.postgres.connect")
    def test_create_postgres_connection_with_params(self, mock_connect):
        """Test PostgreSQL connection creation with individual parameters."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        conn = create_database_connection(
            backend="postgres", database="testdb", host="localhost", port=5432, user="user", password="pass"
        )

        assert conn == mock_conn
        mock_connect.assert_called_once_with(
            host="localhost", port=5432, user="user", password="pass", database="testdb"
        )

    @patch("semantiaz.utils.database_connections.ibis.sqlite.connect")
    def test_create_sqlite_connection(self, mock_connect):
        """Test SQLite connection creation."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        conn = create_database_connection(backend="sqlite", database="testdb", file_path="/path/to/test.db")

        assert conn == mock_conn
        mock_connect.assert_called_once_with("/path/to/test.db")

    @patch("semantiaz.utils.database_connections.ibis.duckdb.connect")
    def test_create_duckdb_connection(self, mock_connect):
        """Test DuckDB connection creation."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        conn = create_database_connection(backend="duckdb", database="testdb", file_path="/path/to/test.duckdb")

        assert conn == mock_conn
        mock_connect.assert_called_once_with("/path/to/test.duckdb")

    @patch("semantiaz.utils.database_connections.ibis.bigquery.connect")
    def test_create_bigquery_connection(self, mock_connect):
        """Test BigQuery connection creation."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        conn = create_database_connection(backend="bigquery", database="project-id")

        assert conn == mock_conn
        mock_connect.assert_called_once_with(project_id="project-id")

    @patch("semantiaz.utils.database_connections.snowflake.connector.connect")
    def test_create_snowflake_connection(self, mock_connect):
        """Test Snowflake connection creation."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        conn = create_database_connection(
            backend="snowflake",
            database="testdb",
            account="account",
            user="user",
            password="pass",
            warehouse="wh",
            schema="schema",
        )

        assert conn == mock_conn
        mock_connect.assert_called_once_with(
            account="account", user="user", password="pass", warehouse="wh", database="testdb", schema="schema"
        )

    def test_create_connection_unsupported_backend(self):
        """Test connection creation with unsupported backend."""
        with pytest.raises(click.ClickException, match="Backend unsupported not supported"):
            create_database_connection(backend="unsupported", database="test")

    @patch("semantiaz.utils.database_connections.ibis.postgres.connect")
    def test_create_connection_failure(self, mock_connect):
        """Test connection creation failure handling."""
        mock_connect.side_effect = Exception("Connection failed")

        with pytest.raises(click.ClickException, match="Failed to connect to postgres"):
            create_database_connection(
                backend="postgres", database="testdb", host="localhost", user="user", password="pass"
            )
