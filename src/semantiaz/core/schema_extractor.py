"""Extract database schema and generate semantic model YAML."""

from dataclasses import dataclass
from typing import Any

import snowflake.connector
import yaml


@dataclass
class TableSchema:
    name: str
    columns: list[dict[str, Any]]
    primary_keys: list[str]
    foreign_keys: list[dict[str, str]]


class SchemaExtractor:
    """Extract schema from Snowflake and generate semantic model YAML."""

    def __init__(self, config: dict[str, str]):
        self.config = config

    def extract_schema(self, database: str, schema: str) -> dict[str, TableSchema]:
        """Extract schema information from Snowflake."""
        with snowflake.connector.connect(**self.config) as conn:
            cursor = conn.cursor()

            # Get tables
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s AND table_catalog = %s
            """,
                (schema, database),
            )
            tables = [row[0] for row in cursor.fetchall()]

            schema_info = {}
            for table in tables:
                schema_info[table] = self._extract_table_schema(cursor, database, schema, table)

            return schema_info

    def _extract_table_schema(self, cursor, database: str, schema: str, table: str) -> TableSchema:
        """Extract schema for a single table."""
        columns = self._get_table_columns(cursor, database, schema, table)
        primary_keys = self._get_primary_keys(cursor, database, schema, table)
        foreign_keys = self._get_foreign_keys(cursor, database, schema, table)
        return TableSchema(table, columns, primary_keys, foreign_keys)

    def _get_table_columns(self, cursor, database: str, schema: str, table: str) -> list[dict[str, Any]]:
        """Get column information for a table."""
        cursor.execute(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_catalog = %s
            AND table_schema = %s
            AND table_name = %s
            ORDER BY ordinal_position
        """,
            (database, schema, table),
        )
        return [{"name": row[0], "type": row[1], "nullable": row[2] == "YES"} for row in cursor.fetchall()]

    def _get_primary_keys(self, cursor, database: str, schema: str, table: str) -> list[str]:
        """Get primary key columns for a table."""
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_catalog = %s
            AND tc.table_schema = %s
            AND tc.table_name = %s
            AND tc.constraint_type = 'PRIMARY KEY'
        """,
            (database, schema, table),
        )
        return [row[0] for row in cursor.fetchall()]

    def _get_foreign_keys(self, cursor, database: str, schema: str, table: str) -> list[dict[str, str]]:
        """Get foreign key relationships for a table."""
        cursor.execute(
            """
            SELECT kcu.column_name, ccu.table_name, ccu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_catalog = %s
            AND tc.table_schema = %s
            AND tc.table_name = %s
            AND tc.constraint_type = 'FOREIGN KEY'
        """,
            (database, schema, table),
        )
        return [{"column": row[0], "ref_table": row[1], "ref_column": row[2]} for row in cursor.fetchall()]

    def generate_semantic_yaml(self, schema_info: dict[str, TableSchema], model_name: str) -> str:
        """Generate semantic model YAML from schema information."""
        semantic_model = self._create_base_model(model_name)
        semantic_model["logical_tables"] = self._generate_logical_tables(schema_info)
        semantic_model["relationships"] = self._generate_relationships(schema_info)
        return yaml.dump(semantic_model, default_flow_style=False, sort_keys=False)

    def _create_base_model(self, model_name: str) -> dict[str, Any]:
        """Create base semantic model structure."""
        return {
            "name": model_name,
            "description": f"Semantic model for {model_name}",
            "logical_tables": [],
            "metrics": [],
            "relationships": [],
        }

    def _generate_logical_tables(self, schema_info: dict[str, TableSchema]) -> list[dict[str, Any]]:
        """Generate logical tables from schema information."""
        return [
            self._create_logical_table(table_name, table_schema) for table_name, table_schema in schema_info.items()
        ]

    def _create_logical_table(self, table_name: str, table_schema: TableSchema) -> dict[str, Any]:
        """Create a logical table definition."""
        logical_table = {
            "name": table_name,
            "description": f"Logical table for {table_name}",
            "base_table": {
                "database": self.config.get("database", ""),
                "schema": self.config.get("schema", ""),
                "table": table_name,
            },
            "dimensions": [],
            "measures": [],
        }

        for col in table_schema.columns:
            if col["type"] in ["NUMBER", "DECIMAL", "FLOAT", "DOUBLE"]:
                logical_table["measures"].append(self._create_measure(col))
            else:
                logical_table["dimensions"].append(self._create_dimension(col))

        return logical_table

    def _create_dimension(self, col: dict[str, Any]) -> dict[str, str]:
        """Create a dimension definition from column."""
        return {
            "name": col["name"],
            "description": f"Dimension for {col['name']}",
            "expr": col["name"],
            "data_type": col["type"],
        }

    def _create_measure(self, col: dict[str, Any]) -> dict[str, str]:
        """Create a measure definition from column."""
        return {
            "name": f"{col['name']}_sum",
            "description": f"Sum of {col['name']}",
            "expr": f"SUM({col['name']})",
            "data_type": col["type"],
        }

    def _generate_relationships(self, schema_info: dict[str, TableSchema]) -> list[dict[str, Any]]:
        """Generate relationships from foreign key information."""
        relationships = []
        for table_name, table_schema in schema_info.items():
            for fk in table_schema.foreign_keys:
                relationships.append({
                    "left_table": table_name,
                    "right_table": fk["ref_table"],
                    "join_type": "LEFT JOIN",
                    "relationship_columns": [{"left_column": fk["column"], "right_column": fk["ref_column"]}],
                })
        return relationships
