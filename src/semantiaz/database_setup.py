#!/usr/bin/env python3
"""CLI script to create databases on Snowflake or DuckDB."""

from pathlib import Path

import click
import duckdb
import snowflake.connector


def get_sql_files():
    """Get paths to SQL files."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    return {
        "clinical": data_dir / "clinical_trial_database.sql",
        "biomarker": data_dir / "biomarker_database.sql",
        "drug": data_dir / "drug_development_database.sql",
    }


def adapt_sql_for_duckdb(sql_content):
    """Adapt Snowflake SQL for DuckDB."""
    # Remove Snowflake-specific commands
    sql_content = sql_content.replace("USE DATABASE", "-- USE DATABASE")
    sql_content = sql_content.replace("USE SCHEMA", "-- USE SCHEMA")
    sql_content = sql_content.replace("CREATE DATABASE IF NOT EXISTS", "-- CREATE DATABASE IF NOT EXISTS")
    sql_content = sql_content.replace("CREATE SCHEMA IF NOT EXISTS", "-- CREATE SCHEMA IF NOT EXISTS")
    sql_content = sql_content.replace("CREATE OR REPLACE TABLE", "CREATE TABLE IF NOT EXISTS")
    sql_content = sql_content.replace("STRING", "VARCHAR")

    # Remove foreign key constraints (DuckDB has limited FK support)
    lines = sql_content.split("\n")
    filtered_lines = []
    for line in lines:
        if "FOREIGN KEY" not in line:
            filtered_lines.append(line)

    return "\n".join(filtered_lines)


def execute_snowflake_sql(config, sql_content):
    """Execute SQL on Snowflake."""
    with snowflake.connector.connect(**config) as conn:
        cursor = conn.cursor()
        statements = sql_content.split(";")
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt)


def execute_duckdb_sql(db_path, sql_content):
    """Execute SQL on DuckDB."""
    with duckdb.connect(db_path) as conn:
        statements = sql_content.split(";")
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    conn.execute(stmt)
                except Exception as e:
                    click.echo(f"Warning: {e}")


@click.command()
@click.option(
    "--database", "-d", type=click.Choice(["snowflake", "duckdb"]), required=True, help="Database type to create"
)
@click.option(
    "--dataset",
    "-ds",
    type=click.Choice(["clinical", "biomarker", "drug", "all"]),
    default="all",
    help="Dataset to create",
)
@click.option("--snowflake-account", help="Snowflake account")
@click.option("--snowflake-user", help="Snowflake user")
@click.option("--snowflake-password", help="Snowflake password")
@click.option("--snowflake-warehouse", help="Snowflake warehouse")
@click.option("--duckdb-path", default="semantiaz.db", help="DuckDB file path")
def create_database(
    database, dataset, snowflake_account, snowflake_user, snowflake_password, snowflake_warehouse, duckdb_path
):
    """Create semantic databases on Snowflake or DuckDB."""

    sql_files = get_sql_files()
    datasets_to_create = [dataset] if dataset != "all" else ["clinical", "biomarker", "drug"]

    if database == "snowflake":
        if not all([snowflake_account, snowflake_user, snowflake_password, snowflake_warehouse]):
            click.echo("Error: Snowflake credentials required")
            return

        config = {
            "account": snowflake_account,
            "user": snowflake_user,
            "password": snowflake_password,
            "warehouse": snowflake_warehouse,
        }

        for ds in datasets_to_create:
            click.echo(f"Creating {ds} database on Snowflake...")
            with open(sql_files[ds]) as f:
                sql_content = f.read()
            execute_snowflake_sql(config, sql_content)
            click.echo(f"✓ {ds} database created")

    elif database == "duckdb":
        for ds in datasets_to_create:
            click.echo(f"Creating {ds} database on DuckDB...")
            with open(sql_files[ds]) as f:
                sql_content = f.read()
            adapted_sql = adapt_sql_for_duckdb(sql_content)
            execute_duckdb_sql(duckdb_path, adapted_sql)
            click.echo(f"✓ {ds} database created")

        click.echo(f"DuckDB file created at: {duckdb_path}")


if __name__ == "__main__":
    create_database()
