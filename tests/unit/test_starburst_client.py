"""Tests for Starburst client module."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from semantiaz.core.starburst_client import StarburstClient


class TestStarburstClient:
    """Test cases for StarburstClient class."""

    @pytest.fixture
    def client_config(self):
        """Sample client configuration."""
        return {
            "host": "starburst.example.com",
            "port": 8080,
            "user": "testuser",
            "password": "testpass",
            "catalog": "hive",
            "schema": "default",
        }

    @pytest.fixture
    def client(self, client_config):
        """Create StarburstClient instance."""
        return StarburstClient(**client_config)

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_connect_with_params(self, mock_connect, client):
        """Test connection with individual parameters."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        result = client.connect()

        assert result == mock_conn
        mock_connect.assert_called_once_with(
            host="starburst.example.com",
            port=8080,
            user="testuser",
            password="testpass",
            catalog="hive",
            schema="default",
        )

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_connect_with_connection_string(self, mock_connect):
        """Test connection with connection string."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        client = StarburstClient(host="localhost", connection_string="trino://user@host:8080/catalog")

        result = client.connect()

        assert result == mock_conn
        mock_connect.assert_called_once_with("trino://user@host:8080/catalog")

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_connect_failure(self, mock_connect, client):
        """Test connection failure handling."""
        mock_connect.side_effect = Exception("Connection failed")

        with pytest.raises(ConnectionError, match="Failed to connect to Starburst"):
            client.connect()

    def test_disconnect(self, client):
        """Test disconnection."""
        mock_conn = Mock()
        client._connection = mock_conn

        client.disconnect()

        mock_conn.disconnect.assert_called_once()
        assert client._connection is None

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_list_catalogs(self, mock_connect, client):
        """Test listing catalogs."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Mock SQL result
        mock_result = Mock()
        mock_result.to_pandas.return_value = pd.DataFrame({"Catalog": ["hive", "iceberg", "delta"]})
        mock_conn.sql.return_value = mock_result

        catalogs = client.list_catalogs()

        assert catalogs == ["hive", "iceberg", "delta"]
        mock_conn.sql.assert_called_once_with("SHOW CATALOGS")

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_list_schemas(self, mock_connect, client):
        """Test listing schemas."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        mock_result = Mock()
        mock_result.to_pandas.return_value = pd.DataFrame({"Schema": ["default", "staging", "prod"]})
        mock_conn.sql.return_value = mock_result

        schemas = client.list_schemas()

        assert schemas == ["default", "staging", "prod"]
        mock_conn.sql.assert_called_once_with("SHOW SCHEMAS FROM hive")

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_list_schemas_with_catalog(self, mock_connect, client):
        """Test listing schemas with specific catalog."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        mock_result = Mock()
        mock_result.to_pandas.return_value = pd.DataFrame({"Schema": ["schema1", "schema2"]})
        mock_conn.sql.return_value = mock_result

        schemas = client.list_schemas("iceberg")

        assert schemas == ["schema1", "schema2"]
        mock_conn.sql.assert_called_once_with("SHOW SCHEMAS FROM iceberg")

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_list_tables(self, mock_connect, client):
        """Test listing tables."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        mock_result = Mock()
        mock_result.to_pandas.return_value = pd.DataFrame({"Table": ["customers", "orders", "products"]})
        mock_conn.sql.return_value = mock_result

        tables = client.list_tables()

        assert tables == ["customers", "orders", "products"]
        mock_conn.sql.assert_called_once_with("SHOW TABLES FROM hive.default")

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_get_table_schema(self, mock_connect, client):
        """Test getting table schema."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Mock table schema
        mock_table = Mock()
        mock_schema = Mock()
        mock_schema.items.return_value = [
            ("id", Mock(nullable=False, __str__=lambda x: "bigint")),
            ("name", Mock(nullable=True, __str__=lambda x: "varchar")),
        ]
        mock_table.schema.return_value = mock_schema
        mock_conn.table.return_value = mock_table

        schema_info = client.get_table_schema("customers")

        assert schema_info["table_name"] == "customers"
        assert schema_info["catalog"] == "hive"
        assert schema_info["schema"] == "default"
        assert len(schema_info["columns"]) == 2
        assert schema_info["columns"][0]["name"] == "id"
        assert schema_info["columns"][0]["type"] == "bigint"
        assert schema_info["columns"][0]["nullable"] is False

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_get_context(self, mock_connect, client):
        """Test getting connection context."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Mock session query
        mock_result = Mock()
        mock_result.to_pandas.return_value = pd.DataFrame({"current_catalog": ["hive"], "current_schema": ["default"]})
        mock_result.empty = False
        mock_conn.sql.return_value = mock_result

        # Mock list_catalogs
        with patch.object(client, "list_catalogs", return_value=["hive", "iceberg"]):
            context = client.get_context()

        assert context["host"] == "starburst.example.com"
        assert context["port"] == 8080
        assert context["user"] == "testuser"
        assert context["catalog"] == "hive"
        assert context["schema"] == "default"
        assert context["connected"] is True
        assert context["current_catalog"] == "hive"
        assert context["current_schema"] == "default"
        assert context["available_catalogs"] == 2

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_execute_query(self, mock_connect, client):
        """Test executing SQL query."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        expected_df = pd.DataFrame({"count": [100]})
        mock_result = Mock()
        mock_result.to_pandas.return_value = expected_df
        mock_conn.sql.return_value = mock_result

        result = client.execute_query("SELECT COUNT(*) as count FROM customers")

        assert result.equals(expected_df)
        mock_conn.sql.assert_called_once_with("SELECT COUNT(*) as count FROM customers")

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_test_connection(self, mock_connect, client):
        """Test connection testing."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        mock_result = Mock()
        mock_result.to_pandas.return_value = pd.DataFrame({"test": [1]})
        mock_conn.sql.return_value = mock_result

        result = client.test_connection()

        assert result is True
        mock_conn.sql.assert_called_once_with("SELECT 1 as test")

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_test_connection_failure(self, mock_connect, client):
        """Test connection testing failure."""
        mock_connect.side_effect = Exception("Connection failed")

        result = client.test_connection()

        assert result is False

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_get_cluster_info(self, mock_connect, client):
        """Test getting cluster information."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Mock nodes query
        nodes_df = pd.DataFrame({
            "coordinator": [True, False],
            "http_uri": ["http://coordinator:8080", "http://worker:8080"],
        })

        # Mock version query
        version_df = pd.DataFrame([["Trino 400"]])

        def sql_side_effect(query):
            mock_result = Mock()
            if "nodes" in query:
                mock_result.to_pandas.return_value = nodes_df
            elif "version" in query:
                mock_result.to_pandas.return_value = version_df
            return mock_result

        mock_conn.sql.side_effect = sql_side_effect

        info = client.get_cluster_info()

        assert info["host"] == "starburst.example.com"
        assert info["port"] == 8080
        assert info["user"] == "testuser"
        assert info["connection_status"] == "connected"
        assert info["node_count"] == 2
        assert info["coordinator"] == "http://coordinator:8080"
        assert info["version"] == "Trino 400"

    def test_context_manager(self, client):
        """Test context manager functionality."""
        with patch.object(client, "connect") as mock_connect, patch.object(client, "disconnect") as mock_disconnect:
            with client:
                pass

            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once()

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_list_objects(self, mock_connect, client):
        """Test listing all objects in schema."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Mock list_tables
        with patch.object(client, "list_tables", return_value=["table1", "table2"]):
            # Mock information_schema query for views
            mock_result = Mock()
            mock_result.to_pandas.return_value = pd.DataFrame({"table_name": ["view1"], "table_type": ["VIEW"]})
            mock_conn.sql.return_value = mock_result

            objects = client.list_objects()

        expected_objects = [
            {"name": "table1", "type": "TABLE"},
            {"name": "table2", "type": "TABLE"},
            {"name": "view1", "type": "VIEW"},
        ]

        assert objects == expected_objects

    @patch("semantiaz.core.starburst_client.ibis.trino.connect")
    def test_error_handling(self, mock_connect, client):
        """Test error handling in various methods."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.sql.side_effect = Exception("Query failed")

        # Test that methods return empty results on error instead of crashing
        assert client.list_catalogs() == []
        assert client.list_schemas() == []
        assert client.list_tables() == []
        assert client.list_views() == []
        assert client.list_objects() == []
        assert client.get_table_schema("test") == {}

        # Test context returns error info
        context = client.get_context()
        assert "error" in context
