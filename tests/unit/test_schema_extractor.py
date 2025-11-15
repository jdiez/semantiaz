"""Tests for schema extractor module."""

from unittest.mock import Mock, patch

import pytest

from semantiaz.core.schema_extractor import SchemaExtractor, TableSchema


class TestSchemaExtractor:
    """Test cases for SchemaExtractor class."""

    @pytest.fixture
    def config(self):
        """Sample configuration for testing."""
        return {
            "account": "test_account",
            "user": "test_user",
            "password": "test_password",
            "warehouse": "test_warehouse",
            "database": "test_db",
            "schema": "test_schema",
        }

    @pytest.fixture
    def extractor(self, config):
        """Create SchemaExtractor instance."""
        return SchemaExtractor(config)

    @patch("semantiaz.core.schema_extractor.snowflake.connector.connect")
    def test_extract_schema(self, mock_connect, extractor):
        """Test schema extraction from Snowflake."""
        # Mock connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock table list query
        mock_cursor.fetchall.return_value = [("table1",), ("table2",)]

        # Mock table schema extraction
        with patch.object(extractor, "_extract_table_schema") as mock_extract:
            mock_extract.return_value = TableSchema(
                name="table1",
                columns=[{"name": "id", "type": "NUMBER", "nullable": False}],
                primary_keys=["id"],
                foreign_keys=[],
            )

            result = extractor.extract_schema("test_db", "test_schema")

            assert len(result) == 2
            assert "table1" in result
            assert "table2" in result

    def test_create_dimension(self, extractor):
        """Test dimension creation from column."""
        col = {"name": "customer_name", "type": "VARCHAR", "nullable": True}
        dimension = extractor._create_dimension(col)

        assert dimension["name"] == "customer_name"
        assert dimension["data_type"] == "VARCHAR"
        assert dimension["expr"] == "customer_name"

    def test_create_measure(self, extractor):
        """Test measure creation from numeric column."""
        col = {"name": "amount", "type": "NUMBER", "nullable": True}
        measure = extractor._create_measure(col)

        assert measure["name"] == "amount_sum"
        assert measure["expr"] == "SUM(amount)"
        assert measure["data_type"] == "NUMBER"

    def test_generate_semantic_yaml(self, extractor):
        """Test YAML generation from schema info."""
        schema_info = {
            "customers": TableSchema(
                name="customers",
                columns=[
                    {"name": "id", "type": "NUMBER", "nullable": False},
                    {"name": "name", "type": "VARCHAR", "nullable": True},
                ],
                primary_keys=["id"],
                foreign_keys=[],
            )
        }

        yaml_content = extractor.generate_semantic_yaml(schema_info, "test_model")

        assert "name: test_model" in yaml_content
        assert "logical_tables:" in yaml_content
        assert "customers" in yaml_content
