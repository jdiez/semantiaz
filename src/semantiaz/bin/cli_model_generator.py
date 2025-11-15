"""CLI for generating semantic models from database connections"""

from typing import Any

import click
import snowflake.connector

from ..models.semantic_model import (
    BaseTable,
    Columns,
    Dimension,
    Metric,
    Relationship,
    RelationshipColumn,
    SemanticModel,
    Table,
)


def infer_data_type_category(data_type: str) -> str:
    """Infer semantic category from SQL data type"""
    data_type = data_type.upper()
    if any(t in data_type for t in ["INT", "BIGINT", "SMALLINT", "TINYINT", "NUMBER"]) or any(
        t in data_type for t in ["DECIMAL", "FLOAT", "DOUBLE", "REAL"]
    ):
        return "numeric"
    elif any(t in data_type for t in ["DATE", "TIME", "TIMESTAMP"]):
        return "temporal"
    elif any(t in data_type for t in ["VARCHAR", "CHAR", "TEXT", "STRING"]) or "BOOLEAN" in data_type:
        return "categorical"
    return "categorical"


def get_snowflake_schema_info(conn, database: str, schema: str) -> dict[str, Any]:
    """Extract schema information from Snowflake"""
    cursor = conn.cursor()

    # Get tables
    cursor.execute(f"SHOW TABLES IN SCHEMA {database}.{schema}")
    tables = cursor.fetchall()

    schema_info = {"tables": {}, "foreign_keys": []}

    for table_row in tables:
        table_name = table_row[1]  # TABLE_NAME column
        table_comment = table_row[5] if len(table_row) > 5 else None  # COMMENT column

        # Get columns for this table
        cursor.execute(f"DESCRIBE TABLE {database}.{schema}.{table_name}")
        columns = cursor.fetchall()

        # Get primary key info
        cursor.execute(f"""
            SELECT column_name FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = '{schema}' AND tc.table_name = '{table_name}'
            AND tc.constraint_type = 'PRIMARY KEY'
        """)
        pk_columns = [row[0] for row in cursor.fetchall()]

        # Get foreign key info
        cursor.execute(f"""
            SELECT kcu.column_name, kcu.referenced_table_name, kcu.referenced_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = '{schema}' AND tc.table_name = '{table_name}'
            AND tc.constraint_type = 'FOREIGN KEY'
        """)
        fk_info = cursor.fetchall()

        schema_info["tables"][table_name] = {
            "comment": table_comment,
            "columns": columns,
            "primary_key": pk_columns,
            "foreign_keys": fk_info,
        }

        # Store foreign key relationships
        for fk_col, ref_table, ref_col in fk_info:
            schema_info["foreign_keys"].append({
                "from_table": table_name,
                "from_column": fk_col,
                "to_table": ref_table,
                "to_column": ref_col,
            })

    return schema_info


def create_semantic_model_from_schema(
    model_name: str, database: str, schema: str, schema_info: dict[str, Any]
) -> SemanticModel:
    """Create semantic model from schema information"""

    model = SemanticModel(
        name=model_name, description=f"Semantic model for {database}.{schema}", tables=[], relationships=[], metrics=[]
    )

    # Create tables with dimensions
    for table_name, table_info in schema_info["tables"].items():
        base_table = BaseTable(database=database, schema=schema, table=table_name)
        primary_key = Columns(columns=table_info["primary_key"]) if table_info["primary_key"] else None

        dimensions = []
        facts = []

        for col_info in table_info["columns"]:
            col_name = col_info[0]
            col_type = col_info[1]
            col_comment = col_info[8] if len(col_info) > 8 else None

            category = infer_data_type_category(col_type)

            # Create dimension for categorical/temporal, fact for numeric
            if category in ["categorical", "temporal"]:
                dimension = Dimension(name=col_name, description=col_comment, data_type=col_type, expr=col_name)
                dimensions.append(dimension)
            elif category == "numeric" and col_name not in table_info["primary_key"]:
                # Skip primary key columns for facts
                from ..models.semantic_model import Fact

                fact = Fact(name=col_name, description=col_comment, data_type=col_type, expr=col_name)
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

    # Create relationships from foreign keys
    for i, fk in enumerate(schema_info["foreign_keys"]):
        rel_col = RelationshipColumn(left_column=fk["from_column"], right_column=fk["to_column"])

        relationship = Relationship(
            name=f"{fk['from_table']}_to_{fk['to_table']}_{i}",
            left_table=fk["from_table"],
            right_table=fk["to_table"],
            relationship_columns=[rel_col],
            join_type="inner",
            relationship_type="many_to_one",
        )

        model.add_relationship(relationship)

    # Create basic count metrics for each table
    for table_name in schema_info["tables"]:
        metric = Metric(name=f"{table_name}_count", description=f"Count of records in {table_name}", expr="COUNT(*)")
        model.add_metric(metric)

    return model


@click.command()
@click.option("--model-name", required=True, help="Name for the semantic model")
@click.option("--account", required=True, help="Snowflake account")
@click.option("--user", required=True, help="Snowflake username")
@click.option("--password", required=True, help="Snowflake password")
@click.option("--warehouse", required=True, help="Snowflake warehouse")
@click.option("--database", required=True, help="Database name")
@click.option("--schema", required=True, help="Schema name")
@click.option("--output", required=True, help="Output YAML file path")
def generate_model(model_name, account, user, password, warehouse, database, schema, output):
    """Generate semantic model from Snowflake database schema"""

    # Connect to Snowflake
    conn = snowflake.connector.connect(
        account=account, user=user, password=password, warehouse=warehouse, database=database, schema=schema
    )

    try:
        # Extract schema information
        click.echo(f"Extracting schema from {database}.{schema}...")
        schema_info = get_snowflake_schema_info(conn, database, schema)

        # Generate semantic model
        click.echo("Generating semantic model...")
        model = create_semantic_model_from_schema(model_name, database, schema, schema_info)

        # Export to YAML
        model.to_yaml(output)
        click.echo(f"Semantic model saved to {output}")

        # Print summary
        click.echo("Generated model with:")
        click.echo(f"  - {len(model.tables)} tables")
        click.echo(f"  - {len(model.relationships)} relationships")
        click.echo(f"  - {len(model.metrics)} metrics")

    finally:
        conn.close()


if __name__ == "__main__":
    generate_model()
