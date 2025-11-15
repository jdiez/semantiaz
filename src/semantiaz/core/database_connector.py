"""Database connection utility for multiple backends using ibis.

This module provides a unified interface for connecting to various database backends
with standardized parameter handling and connection management.
"""

import re
from contextlib import contextmanager
from typing import Any

import ibis


class DatabaseConnector:
    """Unified database connection manager for multiple backends.

    Provides a consistent interface for connecting to various database systems
    including PostgreSQL, MySQL, SQLite, DuckDB, BigQuery, Redshift, Starburst, and Snowflake.
    """

    @staticmethod
    def create_connection(
        backend: str,
        database: str,
        connection_string: str | None = None,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        file_path: str | None = None,
        **kwargs,
    ):
        """Create database connection based on backend type.

        Args:
            backend: Database backend type ('postgres', 'mysql', 'sqlite', 'duckdb', 'bigquery', 'redshift', 'starburst').
            database: Database name or catalog.
            connection_string: Optional connection string (overrides individual params).
            host: Database host (for postgres/mysql/redshift/starburst).
            port: Database port (for postgres/mysql/redshift/starburst).
            user: Database username (for postgres/mysql/redshift/starburst).
            password: Database password (for postgres/mysql/redshift/starburst).
            file_path: File path (for sqlite/duckdb).
            **kwargs: Additional backend-specific parameters (e.g., schema for starburst).

        Returns:
            Ibis database connection object.

        Raises:
            ValueError: If backend is not supported or required parameters are missing.
        """
        if connection_string:
            DatabaseConnector.validate_connection_string(backend, connection_string)

        match backend:
            case "postgres":
                if connection_string:
                    return ibis.postgres.connect(connection_string)
                if not all([host, user, password, database]):
                    raise ValueError("PostgreSQL requires host, user, password, and database")
                return ibis.postgres.connect(
                    host=host, port=port, user=user, password=password, database=database, **kwargs
                )
            case "mysql":
                if connection_string:
                    return ibis.mysql.connect(connection_string)
                if not all([host, user, password, database]):
                    raise ValueError("MySQL requires host, user, password, and database")
                return ibis.mysql.connect(
                    host=host, port=port, user=user, password=password, database=database, **kwargs
                )
            case "sqlite":
                return ibis.sqlite.connect(file_path or f"{database}.db", **kwargs)
            case "duckdb":
                return ibis.duckdb.connect(file_path or f"{database}.db", **kwargs)
            case "bigquery":
                return ibis.bigquery.connect(project_id=database, **kwargs)
            case "redshift":
                if connection_string:
                    return ibis.postgres.connect(connection_string)
                if not all([host, user, password, database]):
                    raise ValueError("Redshift requires host, user, password, and database")
                return ibis.postgres.connect(
                    host=host, port=port or 5439, user=user, password=password, database=database, **kwargs
                )
            case "starburst":
                if connection_string:
                    return ibis.trino.connect(connection_string)
                if not all([host, user, database]):
                    raise ValueError("Starburst requires host, user, and database (catalog)")
                schema = kwargs.pop("schema", None)
                return ibis.trino.connect(
                    host=host,
                    port=port or 8080,
                    user=user,
                    password=password,
                    catalog=database,
                    schema=schema,
                    **kwargs,
                )
            case _:
                raise ValueError(f"Unsupported backend: {backend}")

    @staticmethod
    @contextmanager
    def get_connection(
        backend: str,
        database: str,
        connection_string: str | None = None,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        file_path: str | None = None,
        **kwargs,
    ):
        """Context manager for database connections with automatic cleanup.

        Args:
            Same as create_connection().

        Yields:
            Ibis database connection object.

        Example:
            with DatabaseConnector.get_connection('postgres', 'mydb', host='localhost',
                                                 user='user', password='pass') as conn:
                tables = conn.list_tables()
        """
        conn = None
        try:
            conn = DatabaseConnector.create_connection(
                backend=backend,
                database=database,
                connection_string=connection_string,
                host=host,
                port=port,
                user=user,
                password=password,
                file_path=file_path,
                **kwargs,
            )
            yield conn
        finally:
            if conn and hasattr(conn, "disconnect"):
                try:
                    conn.disconnect()
                except Exception:
                    pass  # Ignore disconnect errors

    @staticmethod
    def validate_connection_string(backend: str, connection_string: str) -> bool:
        """Validate connection string format for a specific backend.

        Args:
            backend: Database backend type.
            connection_string: Connection string to validate.

        Returns:
            True if valid.

        Raises:
            ValueError: If connection string format is invalid.
        """
        patterns = {
            "postgres": r"^postgresql://[^:]+:[^@]+@[^/]+/\w+",
            "mysql": r"^mysql://[^:]+:[^@]+@[^/]+/\w+",
            "redshift": r"^postgresql://[^:]+:[^@]+@[^/]+/\w+",
            "starburst": r"^trino://[^@]+@[^/]+/\w+",
            "sqlite": r"^sqlite:///.*\.db$",
            "duckdb": r"^duckdb:///.*\.db$",
            "snowflake": r"^snowflake://[^:]+:[^@]+@[^/]+/\w+/\w+",
            "bigquery": r"^bigquery://[^/]+/\w+",
        }

        pattern = patterns.get(backend)
        if not pattern:
            return True

        if not re.match(pattern, connection_string):
            raise ValueError(f"Invalid {backend} connection string format")

        return True

    @staticmethod
    def validate_connection_params(backend: str, **params) -> dict[str, Any]:
        """Validate connection parameters for a specific backend.

        Args:
            backend: Database backend type.
            **params: Connection parameters to validate.

        Returns:
            Dictionary of validated parameters.

        Raises:
            ValueError: If required parameters are missing or invalid.
        """
        if params.get("connection_string"):
            DatabaseConnector.validate_connection_string(backend, params["connection_string"])
            return params

        match backend:
            case "postgres" | "mysql" | "redshift":
                required = ["host", "user", "password", "database"]
            case "starburst":
                required = ["host", "user", "database"]
            case "sqlite" | "duckdb" | "bigquery":
                required = ["database"]
            case _:
                raise ValueError(f"Unsupported backend: {backend}")

        missing = [p for p in required if not params.get(p)]
        if missing:
            raise ValueError(f"Missing required parameters for {backend}: {missing}")

        return params
