"""CLI for generating Mermaid diagrams"""

import click
import ibis

from ..models.semantic_model import SemanticModel
from ..plotting.mermaid_generator import MermaidGenerator


@click.group()
def mermaid():
    """Generate Mermaid diagrams"""
    pass


@mermaid.command()
@click.option(
    "--backend",
    required=True,
    type=click.Choice(["postgres", "mysql", "sqlite", "duckdb", "bigquery", "snowflake"]),
    help="Database backend",
)
@click.option("--connection-string", help="Database connection string")
@click.option("--host", help="Database host")
@click.option("--port", type=int, help="Database port")
@click.option("--user", help="Database user")
@click.option("--password", help="Database password")
@click.option("--database", required=True, help="Database name")
@click.option("--schema", help="Schema name (optional)")
@click.option("--file-path", help="File path (for sqlite/duckdb)")
@click.option("--account", help="Snowflake account")
@click.option("--warehouse", help="Snowflake warehouse")
@click.option("--output", required=True, help="Output Mermaid file")
def database_erd(
    backend, connection_string, host, port, user, password, database, schema, file_path, account, warehouse, output
):
    """Generate database ER diagram"""

    try:
        # Create connection
        from ..utils.database_connections import create_database_connection

        conn = create_database_connection(
            backend=backend,
            database=database,
            connection_string=connection_string,
            host=host,
            port=port,
            user=user,
            password=password,
            file_path=file_path,
            schema=schema,
            account=account,
            warehouse=warehouse,
        )

        # Generate diagram
        generator = MermaidGenerator()
        mermaid_content = generator.generate_database_erd(conn, schema)

        # Save output
        with open(output, "w") as f:
            f.write(mermaid_content)

        click.echo(f"Database ER diagram saved to {output}")

    except Exception as e:
        click.echo(f"Error: {e}")
    finally:
        if "conn" in locals():
            conn.disconnect()


@mermaid.command()
@click.option("--yaml-file", required=True, help="Semantic model YAML file")
@click.option("--output", required=True, help="Output Mermaid file")
def semantic_model(yaml_file, output):
    """Generate semantic model diagram"""

    try:
        # Load semantic model
        model = SemanticModel.from_yaml(yaml_file)

        # Generate diagram
        generator = MermaidGenerator()
        mermaid_content = generator.generate_semantic_model_diagram(model)

        # Save output
        with open(output, "w") as f:
            f.write(mermaid_content)

        click.echo(f"Semantic model diagram saved to {output}")

    except Exception as e:
        click.echo(f"Error: {e}")


@mermaid.command()
@click.option(
    "--backend",
    required=True,
    type=click.Choice(["postgres", "mysql", "sqlite", "duckdb", "bigquery"]),
    help="Database backend",
)
@click.option("--connection-string", help="Database connection string")
@click.option("--host", help="Database host")
@click.option("--port", type=int, help="Database port")
@click.option("--user", help="Database user")
@click.option("--password", help="Database password")
@click.option("--database", required=True, help="Database name")
@click.option("--schema", help="Schema name (optional)")
@click.option("--file-path", help="File path (for sqlite/duckdb)")
@click.option("--output", required=True, help="Output Mermaid file")
def quality_metrics(backend, connection_string, host, port, user, password, database, schema, file_path, output):
    """Generate quality metrics diagram"""

    try:
        # Create connection
        if backend == "postgres":
            if connection_string:
                conn = ibis.postgres.connect(connection_string)
            else:
                conn = ibis.postgres.connect(host=host, port=port, user=user, password=password, database=database)
        elif backend == "mysql":
            if connection_string:
                conn = ibis.mysql.connect(connection_string)
            else:
                conn = ibis.mysql.connect(host=host, port=port, user=user, password=password, database=database)
        elif backend == "sqlite":
            conn = ibis.sqlite.connect(file_path or f"{database}.db")
        elif backend == "duckdb":
            conn = ibis.duckdb.connect(file_path or f"{database}.db")
        elif backend == "bigquery":
            conn = ibis.bigquery.connect(project_id=database)
        else:
            click.echo(f"Backend {backend} not supported")
            return

        # Assess quality
        from ..quality.db_quality_assessor import DatabaseQualityAssessor

        assessor = DatabaseQualityAssessor(conn)
        report = assessor.assess_quality(schema)

        # Convert metrics to dict format
        metrics_data = [{"name": m.name, "score": m.score, "details": m.details} for m in report.metrics]

        # Generate diagram
        generator = MermaidGenerator()
        mermaid_content = generator.generate_quality_metrics_diagram(metrics_data)

        # Save output
        with open(output, "w") as f:
            f.write(mermaid_content)

        click.echo(f"Quality metrics diagram saved to {output}")

    except Exception as e:
        click.echo(f"Error: {e}")
    finally:
        if "conn" in locals():
            conn.disconnect()


if __name__ == "__main__":
    mermaid()
