"""Database connection utility for multiple backends using ibis.

This module provides a unified interface for connecting to various database backends
with standardized parameter handling and connection management.
"""

from contextlib import contextmanager
from typing import Any

import ibis


class DatabaseConnector:
    """Unified database connection manager for multiple backends.

    Provides a consistent interface for connecting to various database systems
    including PostgreSQL, MySQL, SQLite, DuckDB, BigQuery, and Snowflake.
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
            backend: Database backend type ('postgres', 'mysql', 'sqlite', 'duckdb', 'bigquery').
            database: Database name or project ID.
            connection_string: Optional connection string (overrides individual params).
            host: Database host (for postgres/mysql).
            port: Database port (for postgres/mysql).
            user: Database username (for postgres/mysql).
            password: Database password (for postgres/mysql).
            file_path: File path (for sqlite/duckdb).
            **kwargs: Additional backend-specific parameters.

        Returns:
            Ibis database connection object.

        Raises:
            ValueError: If backend is not supported or required parameters are missing.
        """
        if backend == "postgres":
            if connection_string:
                return ibis.postgres.connect(connection_string)
            else:
                if not all([host, user, password, database]):
                    raise ValueError("PostgreSQL requires host, user, password, and database")
                return ibis.postgres.connect(
                    host=host, port=port, user=user, password=password, database=database, **kwargs
                )

        elif backend == "mysql":
            if connection_string:
                return ibis.mysql.connect(connection_string)
            else:
                if not all([host, user, password, database]):
                    raise ValueError("MySQL requires host, user, password, and database")
                return ibis.mysql.connect(
                    host=host, port=port, user=user, password=password, database=database, **kwargs
                )

        elif backend == "sqlite":
            db_path = file_path or f"{database}.db"
            return ibis.sqlite.connect(db_path, **kwargs)

        elif backend == "duckdb":
            db_path = file_path or f"{database}.db"
            return ibis.duckdb.connect(db_path, **kwargs)

        elif backend == "bigquery":
            return ibis.bigquery.connect(project_id=database, **kwargs)

        else:
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
    def validate_connection_params(backend: str, **params) -> dict[str, Any]:
        """Validate connection parameters for a specific backend.

        Args:
            backend: Database backend type.
            **params: Connection parameters to validate.

        Returns:
            Dictionary of validated parameters.

        Raises:
            ValueError: If required parameters are missing.
        """
        required_params = {
            "postgres": ["host", "user", "password", "database"],
            "mysql": ["host", "user", "password", "database"],
            "sqlite": ["database"],
            "duckdb": ["database"],
            "bigquery": ["database"],
        }

        if backend not in required_params:
            raise ValueError(f"Unsupported backend: {backend}")

        # Check if connection_string is provided (overrides individual params)
        if params.get("connection_string"):
            return params

        # Validate required parameters
        missing = []
        for param in required_params[backend]:
            if not params.get(param):
                missing.append(param)

        if missing:
            raise ValueError(f"Missing required parameters for {backend}: {missing}")

        return params
