"""Tests for Starburst database connection support."""

from unittest.mock import Mock, patch

import click
import pytest

from semantiaz.utils.database_connections import create_database_connection, validate_backend_params


class TestStarburstConnection:
    """Test cases for Starburst database connection support."""

    def test_validate_starburst_params_with_connection_string(self):
        """Test Starburst validation with connection string."""
        # Should not raise exception
        validate_backend_params("starburst", connection_string="trino://user@host:8080/catalog")

    def test_validate_starburst_params_with_individual_params(self):
        """Test Starburst validation with individual parameters."""
        # Should not raise exception
        validate_backend_params("starburst", host="starburst.example.com", user="user", database="catalog")

    def test_validate_starburst_params_missing_required(self):
        """Test Starburst validation with missing required parameters."""
        with pytest.raises(ValueError, match="Starburst requires"):
            validate_backend_params("starburst", host="localhost")

    @patch("semantiaz.utils.database_connections.ibis.trino.connect")
    def test_create_starburst_connection_with_string(self, mock_connect):
        """Test Starburst connection creation with connection string."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        conn = create_database_connection(
            backend="starburst", database="catalog", connection_string="trino://user@host:8080/catalog"
        )

        assert conn == mock_conn
        mock_connect.assert_called_once_with("trino://user@host:8080/catalog")

    @patch("semantiaz.utils.database_connections.ibis.trino.connect")
    def test_create_starburst_connection_with_params(self, mock_connect):
        """Test Starburst connection creation with individual parameters."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        conn = create_database_connection(
            backend="starburst",
            database="catalog",
            host="starburst.example.com",
            port=8080,
            user="user",
            password="pass",
            schema="schema1",
        )

        assert conn == mock_conn
        mock_connect.assert_called_once_with(
            host="starburst.example.com", port=8080, user="user", password="pass", catalog="catalog", schema="schema1"
        )

    @patch("semantiaz.utils.database_connections.ibis.trino.connect")
    def test_create_starburst_connection_default_port(self, mock_connect):
        """Test Starburst connection with default port."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        conn = create_database_connection(
            backend="starburst", database="catalog", host="starburst.example.com", user="user"
        )

        assert conn == mock_conn
        mock_connect.assert_called_once_with(
            host="starburst.example.com",
            port=8080,  # Default port
            user="user",
            password=None,
            catalog="catalog",
            schema=None,
        )

    @patch("semantiaz.utils.database_connections.ibis.trino.connect")
    def test_create_starburst_connection_failure(self, mock_connect):
        """Test Starburst connection creation failure handling."""
        mock_connect.side_effect = Exception("Connection failed")

        with pytest.raises(click.ClickException, match="Failed to connect to starburst"):
            create_database_connection(
                backend="starburst", database="catalog", host="starburst.example.com", user="user"
            )

    def test_starburst_in_supported_backends(self):
        """Test that Starburst is included in supported backends."""
        from semantiaz.utils.database_connections import get_supported_backends

        backends = get_supported_backends()
        assert "starburst" in backends
