"""Database connection utilities for multi-backend support.

This module provides a centralized way to create database connections
across different backends using ibis, reducing code duplication in CLI modules.
"""

import click
import ibis


def create_database_connection(
    backend: str,
    database: str,
    connection_string: str | None = None,
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None,
    file_path: str | None = None,
    schema: str | None = None,
    account: str | None = None,
    warehouse: str | None = None,
):
    """Create a database connection using ibis for the specified backend.

    Args:
        backend: Database backend type (postgres, mysql, sqlite, duckdb, bigquery, starburst).
        database: Database name or project ID.
        connection_string: Optional connection string for postgres/mysql/starburst.
        host: Database host for postgres/mysql/starburst.
        port: Database port for postgres/mysql/starburst.
        user: Database user for postgres/mysql/starburst.
        password: Database password for postgres/mysql/starburst.
        file_path: File path for sqlite/duckdb.
        schema: Optional schema name.

    Returns:
        Ibis database connection object.

    Raises:
        ValueError: If backend is not supported or required parameters are missing.
        click.ClickException: If connection fails.
    """
    try:
        match backend:
            case "postgres":
                conn = (
                    ibis.postgres.connect(connection_string)
                    if connection_string
                    else ibis.postgres.connect(host=host, port=port, user=user, password=password, database=database)
                    if all([host, user, password, database])
                    else (_ for _ in ()).throw(ValueError("PostgreSQL requires host, user, password, and database"))
                )
            case "mysql":
                conn = (
                    ibis.mysql.connect(connection_string)
                    if connection_string
                    else ibis.mysql.connect(host=host, port=port, user=user, password=password, database=database)
                    if all([host, user, password, database])
                    else (_ for _ in ()).throw(ValueError("MySQL requires host, user, password, and database"))
                )
            case "sqlite":
                conn = ibis.sqlite.connect(file_path or f"{database}.db")
            case "duckdb":
                conn = ibis.duckdb.connect(file_path or f"{database}.db")
            case "bigquery":
                conn = ibis.bigquery.connect(project_id=database)
            case "starburst":
                conn = (
                    ibis.trino.connect(connection_string)
                    if connection_string
                    else ibis.trino.connect(
                        host=host, port=port or 8080, user=user, password=password, catalog=database, schema=schema
                    )
                    if all([host, user, database])
                    else (_ for _ in ()).throw(ValueError("Starburst requires host, user, and database"))
                )
            case "snowflake":
                import snowflake.connector

                conn = (
                    snowflake.connector.connect(
                        account=account,
                        user=user,
                        password=password,
                        warehouse=warehouse,
                        database=database,
                        schema=schema,
                    )
                    if all([account, user, password, warehouse, database])
                    else (_ for _ in ()).throw(
                        ValueError("Snowflake requires account, user, password, warehouse, and database")
                    )
                )
            case _:
                raise ValueError(f"Backend {backend} not supported")

        return conn

    except Exception as e:
        raise click.ClickException(f"Failed to connect to {backend}: {e!s}") from e


def get_supported_backends() -> list[str]:
    """Get list of supported database backends.

    Returns:
        List of supported backend names.
    """
    return ["postgres", "mysql", "sqlite", "duckdb", "bigquery", "starburst", "snowflake"]


def validate_backend_params(backend: str, **kwargs) -> None:
    """Validate that required parameters are provided for the backend.

    Args:
        backend: Database backend type.
        **kwargs: Connection parameters.

    Raises:
        ValueError: If required parameters are missing.
    """
    match backend:
        case "postgres" | "mysql" | "starburst":
            if not kwargs.get("connection_string"):
                required = ["host", "user", "database"]
                if backend in ["postgres", "mysql"]:
                    required.append("password")
                missing = [p for p in required if not kwargs.get(p)]
                if missing:
                    raise ValueError(f"{backend.title()} requires: {', '.join(missing)}")
        case "sqlite" | "duckdb":
            if not kwargs.get("file_path") and not kwargs.get("database"):
                raise ValueError(f"{backend.title()} requires either file_path or database name")
        case "bigquery":
            if not kwargs.get("database"):
                raise ValueError("BigQuery requires database (project_id)")
        case "snowflake":
            required = ["account", "user", "password", "warehouse", "database"]
            missing = [p for p in required if not kwargs.get(p)]
            if missing:
                raise ValueError(f"Snowflake requires: {', '.join(missing)}")
        case _:
            pass
