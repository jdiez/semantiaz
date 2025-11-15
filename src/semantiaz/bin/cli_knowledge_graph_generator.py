"""CLI for generating knowledge graphs from database schema and content"""

from typing import Any

import click


def generate_rdf_knowledge_graph(connection, schema_info: dict[str, Any], limit: int = 100) -> str:
    """Generate RDF knowledge graph from schema and data"""
    rdf_triples = []

    # Add prefixes
    rdf_triples.extend([
        "@prefix kg: <http://example.org/kg/> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "",
    ])

    for table_name, _table_info in schema_info["tables"].items():
        try:
            table = connection.table(table_name)
            data = table.limit(limit).execute()

            # Create instances from data
            for idx, row in data.iterrows():
                entity_uri = f"kg:{table_name}_{idx}"
                rdf_triples.append(f"{entity_uri} rdf:type kg:{table_name} .")

                for col_name, value in row.items():
                    if value is not None:
                        if isinstance(value, str):
                            rdf_triples.append(f'{entity_uri} kg:{col_name} "{value}" .')
                        else:
                            rdf_triples.append(f"{entity_uri} kg:{col_name} {value} .")
        except Exception as e:
            click.echo(f"Warning: Could not extract data from {table_name}: {e}")

    return "\n".join(rdf_triples)


def generate_cypher_knowledge_graph(connection, schema_info: dict[str, Any], limit: int = 100) -> str:
    """Generate Cypher knowledge graph from schema and data"""
    cypher_statements = []

    for table_name, _table_info in schema_info["tables"].items():
        try:
            table = connection.table(table_name)
            data = table.limit(limit).execute()

            # Create nodes from data
            for _idx, row in data.iterrows():
                props = []
                for col_name, value in row.items():
                    if value is not None:
                        if isinstance(value, str):
                            props.append(f"{col_name}: '{value}'")
                        else:
                            props.append(f"{col_name}: {value}")

                props_str = ", ".join(props)
                cypher_statements.append(f"CREATE (:{table_name} {{{props_str}}})")
        except Exception as e:
            click.echo(f"Warning: Could not extract data from {table_name}: {e}")

    return ";\n".join(cypher_statements) + ";"


def get_generic_schema_info(connection, schema: str | None = None) -> dict[str, Any]:
    """Extract schema information using ibis"""
    schema_info = {"tables": {}, "foreign_keys": []}

    table_names = connection.list_tables(schema=schema)

    for table_name in table_names:
        try:
            table = connection.table(table_name, schema=schema)
            columns = []
            for col_name, col_type in table.schema().items():
                columns.append({"name": col_name, "type": str(col_type), "ibis_type": col_type})

            schema_info["tables"][table_name] = {
                "comment": None,
                "columns": columns,
                "primary_key": [],
                "foreign_keys": [],
            }
        except Exception as e:
            click.echo(f"Warning: Could not process table {table_name}: {e}")

    return schema_info


@click.command()
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
@click.option("--format", "output_format", type=click.Choice(["rdf", "cypher"]), required=True, help="Output format")
@click.option("--output", required=True, help="Output file path")
@click.option("--limit", default=100, help="Limit rows per table")
def generate_knowledge_graph(
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
    output_format,
    output,
    limit,
):
    """Generate knowledge graph from database schema and content"""

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

        # Extract schema
        click.echo(f"Extracting schema and data from {backend} database...")
        schema_info = get_generic_schema_info(conn, schema)

        if not schema_info["tables"]:
            click.echo("No tables found")
            return

        # Generate knowledge graph
        click.echo(f"Generating {output_format} knowledge graph...")
        if output_format == "rdf":
            content = generate_rdf_knowledge_graph(conn, schema_info, limit)
        else:
            content = generate_cypher_knowledge_graph(conn, schema_info, limit)

        # Save output
        with open(output, "w") as f:
            f.write(content)

        click.echo(f"Knowledge graph saved to {output}")
        click.echo(f"Processed {len(schema_info['tables'])} tables with up to {limit} rows each")

    except Exception as e:
        click.echo(f"Error: {e}")
        return
    finally:
        if "conn" in locals():
            conn.disconnect()


if __name__ == "__main__":
    generate_knowledge_graph()
