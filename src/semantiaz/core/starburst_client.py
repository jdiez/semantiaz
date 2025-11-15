"""Starburst client for database operations and metadata management."""

import logging
from typing import Any

import ibis
from ibis import BaseBackend

logger = logging.getLogger(__name__)


class StarburstClient:
    """Client for Starburst database operations using Trino connector."""

    def __init__(
        self,
        host: str,
        port: int = 8080,
        user: str = "admin",
        password: str | None = None,
        catalog: str | None = None,
        schema: str | None = None,
        connection_string: str | None = None,
    ):
        """Initialize Starburst client.

        Args:
            host: Starburst cluster host
            port: Starburst cluster port (default: 8080)
            user: Username for authentication
            password: Password for authentication
            catalog: Default catalog to use
            schema: Default schema to use
            connection_string: Optional Trino connection string
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.catalog = catalog
        self.schema = schema
        self.connection_string = connection_string
        self._connection: BaseBackend | None = None

    def connect(self) -> BaseBackend:
        """Establish connection to Starburst cluster.

        Returns:
            Ibis Trino backend connection

        Raises:
            ConnectionError: If connection fails
        """
        try:
            if self.connection_string:
                self._connection = ibis.trino.connect(self.connection_string)
            else:
                self._connection = ibis.trino.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    catalog=self.catalog,
                    schema=self.schema,
                )
            logger.info(f"Connected to Starburst at {self.host}:{self.port}")
            return self._connection
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Starburst: {e}") from e

    def disconnect(self) -> None:
        """Close connection to Starburst cluster."""
        if self._connection:
            self._connection.disconnect()
            self._connection = None
            logger.info("Disconnected from Starburst")

    @property
    def connection(self) -> BaseBackend:
        """Get active connection, creating one if needed."""
        if not self._connection:
            self.connect()
        return self._connection

    def list_catalogs(self) -> list[str]:
        """List all available catalogs.

        Returns:
            List of catalog names
        """
        try:
            query = "SHOW CATALOGS"
            result = self.connection.sql(query).to_pandas()
            return result["Catalog"].tolist()
        except Exception:
            logger.exception("Failed to list catalogs")
            return []

    def list_schemas(self, catalog: str | None = None) -> list[str]:
        """List schemas in a catalog.

        Args:
            catalog: Catalog name (uses default if not specified)

        Returns:
            List of schema names
        """
        try:
            catalog = catalog or self.catalog
            query = f"SHOW SCHEMAS FROM {catalog}" if catalog else "SHOW SCHEMAS"

            result = self.connection.sql(query).to_pandas()
            return result["Schema"].tolist()
        except Exception:
            logger.exception("Failed to list schemas")
            return []

    def list_tables(self, catalog: str | None = None, schema: str | None = None) -> list[str]:
        """List tables in a schema.

        Args:
            catalog: Catalog name (uses default if not specified)
            schema: Schema name (uses default if not specified)

        Returns:
            List of table names
        """
        try:
            catalog = catalog or self.catalog
            schema = schema or self.schema

            if catalog and schema:
                query = f"SHOW TABLES FROM {catalog}.{schema}"
            elif schema:
                query = f"SHOW TABLES FROM {schema}"
            else:
                query = "SHOW TABLES"

            result = self.connection.sql(query).to_pandas()
            return result["Table"].tolist()
        except Exception:
            logger.exception("Failed to list tables")
            return []

    def list_views(self, catalog: str | None = None, schema: str | None = None) -> list[str]:
        """List views in a schema.

        Args:
            catalog: Catalog name (uses default if not specified)
            schema: Schema name (uses default if not specified)

        Returns:
            List of view names
        """
        try:
            catalog = catalog or self.catalog
            schema = schema or self.schema

            # Get all objects and filter for views
            objects = self.list_objects(catalog, schema)
            return [obj["name"] for obj in objects if obj["type"] == "VIEW"]
        except Exception:
            logger.exception("Failed to list views")
            return []

    def list_objects(self, catalog: str | None = None, schema: str | None = None) -> list[dict[str, Any]]:
        """List all objects (tables, views, etc.) in a schema.

        Args:
            catalog: Catalog name (uses default if not specified)
            schema: Schema name (uses default if not specified)

        Returns:
            List of objects with name and type information
        """
        try:
            catalog = catalog or self.catalog
            schema = schema or self.schema

            objects = []

            # Get tables
            tables = self.list_tables(catalog, schema)
            objects.extend([{"name": table, "type": "TABLE"} for table in tables])

            # Get views using information_schema
            if catalog and schema:
                query = f"""
                SELECT table_name, table_type
                FROM {catalog}.information_schema.tables
                WHERE table_schema = '{schema}'
                """
                result = self.connection.sql(query).to_pandas()
                for _, row in result.iterrows():
                    if row["table_type"] == "VIEW":
                        objects.append({"name": row["table_name"], "type": "VIEW"})

            return objects
        except Exception:
            logger.exception("Failed to list objects")
            return []

    def get_table_schema(
        self, table_name: str, catalog: str | None = None, schema: str | None = None
    ) -> dict[str, Any]:
        """Get schema information for a table.

        Args:
            table_name: Name of the table
            catalog: Catalog name (uses default if not specified)
            schema: Schema name (uses default if not specified)

        Returns:
            Dictionary with table schema information
        """
        try:
            catalog = catalog or self.catalog
            schema = schema or self.schema

            if catalog and schema:
                full_name = f"{catalog}.{schema}.{table_name}"
            elif schema:
                full_name = f"{schema}.{table_name}"
            else:
                full_name = table_name

            table = self.connection.table(full_name)
            schema_info = table.schema()

            columns = []
            for col_name, col_type in schema_info.items():
                columns.append({"name": col_name, "type": str(col_type), "nullable": col_type.nullable})

            return {"table_name": table_name, "catalog": catalog, "schema": schema, "columns": columns}
        except Exception:
            logger.exception("Failed to get table schema for {table_name}")
            return {}

    def get_context(self) -> dict[str, Any]:
        """Get current connection context information.

        Returns:
            Dictionary with context information
        """
        try:
            context = {
                "host": self.host,
                "port": self.port,
                "user": self.user,
                "catalog": self.catalog,
                "schema": self.schema,
                "connected": self._connection is not None,
            }

            if self._connection:
                # Get current session info
                try:
                    session_query = "SELECT current_catalog, current_schema"
                    session_result = self.connection.sql(session_query).to_pandas()
                    if not session_result.empty:
                        context["current_catalog"] = session_result.iloc[0]["current_catalog"]
                        context["current_schema"] = session_result.iloc[0]["current_schema"]
                except Exception:
                    pass  # Session info not critical

                # Get available catalogs count
                catalogs = self.list_catalogs()
                context["available_catalogs"] = len(catalogs)
                context["catalogs"] = catalogs[:5]  # First 5 catalogs

            return context
        except Exception as e:
            logger.exception("Failed to get context")
            return {"error": str(e)}

    def execute_query(self, query: str) -> Any:
        """Execute a SQL query.

        Args:
            query: SQL query to execute

        Returns:
            Query result as pandas DataFrame
        """
        try:
            result = self.connection.sql(query).to_pandas()
            logger.info(f"Executed query successfully: {query[:100]}...")
            return result
        except Exception:
            logger.exception("Failed to execute query")
            raise

    def test_connection(self) -> bool:
        """Test the connection to Starburst.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.connect()
            # Simple test query
            result = self.connection.sql("SELECT 1 as test").to_pandas()
            return len(result) == 1 and result.iloc[0]["test"] == 1
        except Exception:
            logger.exception("Connection test failed")
            return False

    def get_cluster_info(self) -> dict[str, Any]:
        """Get Starburst cluster information.

        Returns:
            Dictionary with cluster information
        """
        try:
            info = {
                "host": self.host,
                "port": self.port,
                "user": self.user,
                "connection_status": "connected" if self._connection else "disconnected",
            }

            if self._connection:
                # Get cluster nodes info
                try:
                    nodes_query = "SELECT * FROM system.runtime.nodes"
                    nodes_result = self.connection.sql(nodes_query).to_pandas()
                    info["node_count"] = len(nodes_result)
                    info["coordinator"] = (
                        nodes_result[nodes_result["coordinator"]]["http_uri"].iloc[0]
                        if not nodes_result.empty
                        else None
                    )
                except Exception:
                    pass  # Node info not critical

                # Get version info
                try:
                    version_query = "SELECT version()"
                    version_result = self.connection.sql(version_query).to_pandas()
                    if not version_result.empty:
                        info["version"] = version_result.iloc[0].iloc[0]
                except Exception:
                    pass  # Version info not critical

            return info
        except Exception as e:
            logger.exception("Failed to get cluster info")
            return {"error": str(e)}

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
