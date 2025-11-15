"""Generic CLI for generating semantic models from any RDBMS using ibis"""

from typing import Any

import click

from ..models.semantic_model import (
    BaseTable,
    Columns,
    Dimension,
    Fact,
    Metric,
    SemanticModel,
    Table,
)


def infer_data_type_category(ibis_type: str) -> str:
    """Infer semantic category from ibis data type"""
    type_str = str(ibis_type).lower()
    if any(t in type_str for t in ["int", "float", "double", "decimal", "numeric"]):
        return "numeric"
    elif any(t in type_str for t in ["date", "time", "timestamp"]):
        return "temporal"
    elif any(t in type_str for t in ["string", "varchar", "char", "text", "bool"]):
        return "categorical"
    return "categorical"


def get_generic_schema_info(connection, schema: str | None = None) -> dict[str, Any]:
    """Extract schema information using ibis"""
    schema_info = {"tables": {}, "foreign_keys": []}

    # Get all tables
    table_names = connection.list_tables(schema=schema)

    for table_name in table_names:
        try:
            table = connection.table(table_name, schema=schema)

            # Get column information
            columns = []
            for col_name, col_type in table.schema().items():
                columns.append({"name": col_name, "type": str(col_type), "ibis_type": col_type})

            schema_info["tables"][table_name] = {
                "comment": None,  # ibis doesn't provide table comments generically
                "columns": columns,
                "primary_key": [],  # Would need database-specific queries
                "foreign_keys": [],  # Would need database-specific queries
            }

        except Exception as e:
            click.echo(f"Warning: Could not process table {table_name}: {e}")
            continue

    return schema_info


def create_semantic_model_from_generic_schema(
    model_name: str, database: str, schema: str | None, schema_info: dict[str, Any]
) -> SemanticModel:
    """Create semantic model from generic schema information"""

    model = SemanticModel(
        name=model_name,
        description=f"Semantic model for {database}" + (f".{schema}" if schema else ""),
        tables=[],
        relationships=[],
        metrics=[],
    )

    # Create tables with dimensions and facts
    for table_name, table_info in schema_info["tables"].items():
        base_table = BaseTable(database=database, schema=schema, table=table_name)
        primary_key = Columns(columns=table_info["primary_key"]) if table_info["primary_key"] else None

        dimensions = []
        facts = []

        for col_info in table_info["columns"]:
            col_name = col_info["name"]
            col_type = col_info["type"]

            category = infer_data_type_category(col_type)

            # Create dimension for categorical/temporal, fact for numeric
            if category in ["categorical", "temporal"]:
                dimension = Dimension(name=col_name, description=None, data_type=col_type, expr=col_name)
                dimensions.append(dimension)
            elif category == "numeric":
                fact = Fact(name=col_name, description=None, data_type=col_type, expr=col_name)
                facts.append(fact)

        table = Table(
            name=table_name,
            description=table_info["comment"],
            base_table=base_table,
            primary_key=primary_key,
            dimensions=dimensions,
            facts=facts if facts else None,
        )

        model.add_table(table)

    # Create basic count metrics for each table
    for table_name in schema_info["tables"]:
        metric = Metric(name=f"{table_name}_count", description=f"Count of records in {table_name}", expr="COUNT(*)")
        model.add_metric(metric)

    return model


@click.command()
@click.option("--model-name", required=True, help="Name for the semantic model")
@click.option(
    "--backend",
    required=True,
    type=click.Choice(["postgres", "mysql", "sqlite", "duckdb", "snowflake", "bigquery", "starburst"]),
    help="Database backend",
)
@click.option("--connection-string", help="Database connection string (for postgres/mysql)")
@click.option("--host", help="Database host")
@click.option("--port", type=int, help="Database port")
@click.option("--user", help="Database user")
@click.option("--password", help="Database password")
@click.option("--database", required=True, help="Database name")
@click.option("--schema", help="Schema name (optional)")
@click.option("--file-path", help="File path (for sqlite/duckdb)")
@click.option("--account", help="Snowflake account")
@click.option("--warehouse", help="Snowflake warehouse")
@click.option("--output", required=True, help="Output YAML file path")
@click.option("--rdf-output", help="Optional RDF/TTL output file path")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["yaml", "rdf", "cypher", "all"]),
    default="yaml",
    help="Output format",
)
@click.option("--cypher-output", help="Optional Cypher output file path")
def generate_generic_model(
    model_name,
    backend,
    connection_string,
    host,
    port,
    user,
    password,
    database,
    schema,
    file_path,
    account,
    warehouse,
    output,
    rdf_output,
    output_format,
    cypher_output,
):
    """Generate semantic model from any RDBMS using ibis with optional RDF/Cypher export"""

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

        # Extract schema information
        click.echo(f"Extracting schema from {backend} database...")
        schema_info = get_generic_schema_info(conn, schema)

        if not schema_info["tables"]:
            click.echo("No tables found in the database")
            return

        # Generate semantic model
        click.echo("Generating semantic model...")
        model = create_semantic_model_from_generic_schema(model_name, database, schema, schema_info)

        # Export based on format
        if output_format in ["yaml", "all"]:
            model.to_yaml(output)
            click.echo(f"Semantic model saved to {output}")

        if output_format in ["rdf", "all"]:
            try:
                from ..converters.semantic_to_rdf import SemanticToRDFConverter

                converter = SemanticToRDFConverter()
                rdf_content = converter.convert(model)

                rdf_file = rdf_output or output.replace(".yaml", ".ttl").replace(".yml", ".ttl")
                with open(rdf_file, "w") as f:
                    f.write(rdf_content)
                click.echo(f"RDF model saved to {rdf_file}")
            except ImportError:
                click.echo("Warning: RDF converter not available. Install rdflib to enable RDF export.")

        if output_format in ["cypher", "all"]:
            from ..converters.semantic_to_cypher import SemanticToCypherConverter

            converter = SemanticToCypherConverter()
            cypher_content = converter.convert(model)

            cypher_file = cypher_output or output.replace(".yaml", ".cypher").replace(".yml", ".cypher")
            with open(cypher_file, "w") as f:
                f.write(cypher_content)
            click.echo(f"Cypher model saved to {cypher_file}")

        # Print summary
        click.echo("Generated model with:")
        click.echo(f"  - {len(model.tables)} tables")
        click.echo(f"  - {len(model.relationships)} relationships")
        click.echo(f"  - {len(model.metrics)} metrics")

    except Exception as e:
        click.echo(f"Error: {e}")
    finally:
        if "conn" in locals():
            conn.disconnect()


if __name__ == "__main__":
    generate_generic_model()
