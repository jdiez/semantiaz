#!/usr/bin/env python3
"""CLI for semantic model operations."""

from pathlib import Path

import click
import duckdb
import snowflake.connector

from .bin.cli_generic_model_generator import generate_generic_model
from .bin.cli_knowledge_graph_generator import generate_knowledge_graph
from .bin.cli_mermaid import mermaid
from .bin.cli_model_generator import generate_model
from .bin.cli_quality_assessment import assess_quality
from .core.schema_extractor import SchemaExtractor
from .core.view_deployer import ViewDeployer


@click.group()
def cli():
    """Semantic model operations."""
    pass


cli.add_command(generate_model, name="generate-model")
cli.add_command(generate_generic_model, name="generate-generic-model")
cli.add_command(generate_knowledge_graph, name="generate-kg")
cli.add_command(assess_quality, name="assess-quality")
cli.add_command(mermaid)


@cli.command()
@click.option("--account", required=True, help="Snowflake account")
@click.option("--user", required=True, help="Snowflake user")
@click.option("--password", required=True, help="Snowflake password")
@click.option("--warehouse", required=True, help="Snowflake warehouse")
@click.option("--database", required=True, help="Snowflake database")
@click.option("--schema", required=True, help="Snowflake schema")
@click.option("--model-name", required=True, help="Name for semantic model")
@click.option("--output", required=True, help="Output YAML file path")
def extract(account, user, password, warehouse, database, schema, model_name, output):
    """Extract schema and create semantic model."""
    config = {
        "account": account,
        "user": user,
        "password": password,
        "warehouse": warehouse,
        "database": database,
        "schema": schema,
    }

    extractor = SchemaExtractor(config)
    schema_info = extractor.extract_schema(database, schema)
    yaml_content = extractor.generate_semantic_yaml(schema_info, model_name)

    with open(output, "w") as f:
        f.write(yaml_content)

    click.echo(f"Semantic model saved to {output}")


@cli.command()
@click.option("--account", required=True, help="Snowflake account")
@click.option("--user", required=True, help="Snowflake user")
@click.option("--password", required=True, help="Snowflake password")
@click.option("--warehouse", required=True, help="Snowflake warehouse")
@click.option("--database", required=True, help="Snowflake database")
@click.option("--schema", required=True, help="Snowflake schema")
@click.option("--yaml-file", required=True, help="Semantic model YAML file")
@click.option("--prefix", default="semantic_", help="View name prefix")
def deploy(account, user, password, warehouse, database, schema, yaml_file, prefix):
    """Deploy views from semantic model."""
    config = {
        "account": account,
        "user": user,
        "password": password,
        "warehouse": warehouse,
        "database": database,
        "schema": schema,
    }

    deployer = ViewDeployer(config)
    deployed_views = deployer.deploy_all_views(yaml_file, prefix)

    click.echo(f"Deployed {len(deployed_views)} views:")
    for view in deployed_views:
        click.echo(f"  - {view}")


@cli.command("setup-db")
@click.option("--database", "-d", type=click.Choice(["snowflake", "duckdb"]), required=True, help="Database type")
@click.option(
    "--dataset", type=click.Choice(["clinical", "biomarker", "drug", "all"]), default="all", help="Dataset to create"
)
@click.option("--snowflake-account", help="Snowflake account")
@click.option("--snowflake-user", help="Snowflake user")
@click.option("--snowflake-password", help="Snowflake password")
@click.option("--snowflake-warehouse", help="Snowflake warehouse")
@click.option("--duckdb-path", default="semantiaz.db", help="DuckDB file path")
def setup_db(
    database, dataset, snowflake_account, snowflake_user, snowflake_password, snowflake_warehouse, duckdb_path
):
    """Create sample databases."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    sql_files = {
        "clinical": data_dir / "clinical_trial_database.sql",
        "biomarker": data_dir / "biomarker_database.sql",
        "drug": data_dir / "drug_development_database.sql",
    }

    datasets = [dataset] if dataset != "all" else ["clinical", "biomarker", "drug"]

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

        for ds in datasets:
            click.echo(f"Creating {ds} database on Snowflake...")
            with open(sql_files[ds]) as f:
                sql_content = f.read()
            _execute_snowflake_sql(config, sql_content)
            click.echo(f"✓ {ds} database created")

    elif database == "duckdb":
        for ds in datasets:
            click.echo(f"Creating {ds} database on DuckDB...")
            with open(sql_files[ds]) as f:
                sql_content = f.read()
            adapted_sql = _adapt_sql_for_duckdb(sql_content)
            _execute_duckdb_sql(duckdb_path, adapted_sql)
            click.echo(f"✓ {ds} database created")

        click.echo(f"DuckDB file created at: {duckdb_path}")


def _adapt_sql_for_duckdb(sql_content):
    """Adapt Snowflake SQL for DuckDB."""
    sql_content = sql_content.replace("USE DATABASE", "-- USE DATABASE")
    sql_content = sql_content.replace("USE SCHEMA", "-- USE SCHEMA")
    sql_content = sql_content.replace("CREATE DATABASE IF NOT EXISTS", "-- CREATE DATABASE IF NOT EXISTS")
    sql_content = sql_content.replace("CREATE SCHEMA IF NOT EXISTS", "-- CREATE SCHEMA IF NOT EXISTS")
    sql_content = sql_content.replace("CREATE OR REPLACE TABLE", "CREATE TABLE IF NOT EXISTS")
    sql_content = sql_content.replace("STRING", "VARCHAR")

    lines = sql_content.split("\n")
    filtered_lines = [line for line in lines if "FOREIGN KEY" not in line]
    return "\n".join(filtered_lines)


def _execute_snowflake_sql(config, sql_content):
    """Execute SQL on Snowflake."""
    with snowflake.connector.connect(**config) as conn:
        cursor = conn.cursor()
        statements = sql_content.split(";")
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt)


def _execute_duckdb_sql(db_path, sql_content):
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


if __name__ == "__main__":
    cli()
