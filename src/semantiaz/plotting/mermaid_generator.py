"""Generate Mermaid diagrams from database schema and semantic models.

This module provides capabilities to create Mermaid diagram representations of
database schemas, semantic models, and quality metrics. Mermaid diagrams are
text-based and can be rendered in documentation, GitHub, and other platforms.
"""

from typing import Any

from ..models.semantic_model import SemanticModel


class MermaidGenerator:
    """Generate Mermaid diagrams for database schemas and semantic models.

    This class creates various types of Mermaid diagrams including ER diagrams
    for database schemas, flowcharts for semantic models, and quality metric
    visualizations. All diagrams are generated as Mermaid markup text.
    """

    def generate_database_erd(self, connection, schema: str | None = None) -> str:
        """Generate Mermaid ER diagram from database schema.

        Creates an Entity-Relationship diagram showing tables, columns, data types,
        and relationships inferred from foreign key naming patterns.

        Args:
            connection: Ibis database connection object.
            schema: Optional schema name to limit diagram scope.

        Returns:
            Mermaid ER diagram markup as string.
        """
        tables = connection.list_tables(schema=schema)

        mermaid_lines = ["erDiagram"]

        # Generate table definitions
        for table_name in tables:
            try:
                table = connection.table(table_name, schema=schema)
                table_schema = table.schema()

                # Add table with columns
                for col_name, col_type in table_schema.items():
                    type_str = str(col_type).upper()

                    # Determine key type
                    key_indicator = ""
                    if "id" in col_name.lower() and col_name.lower() == "id":
                        key_indicator = " PK"
                    elif col_name.lower().endswith("_id"):
                        key_indicator = " FK"

                    mermaid_lines.append(f"    {table_name} {{")
                    mermaid_lines.append(f"        {type_str} {col_name}{key_indicator}")
                    mermaid_lines.append("    }")
                    break  # Only show structure once per table

                # Add actual column definitions
                mermaid_lines.append(f"    {table_name} {{")
                for col_name, col_type in table_schema.items():
                    type_str = str(col_type).replace("(", "").replace(")", "").upper()[:10]
                    key_indicator = ""
                    if "id" in col_name.lower() and col_name.lower() == "id":
                        key_indicator = " PK"
                    elif col_name.lower().endswith("_id"):
                        key_indicator = " FK"

                    mermaid_lines.append(f"        {type_str} {col_name}{key_indicator}")
                mermaid_lines.append("    }")

            except Exception:
                continue

        # Generate relationships based on foreign key patterns
        for table_name in tables:
            try:
                table = connection.table(table_name, schema=schema)
                columns = list(table.schema().keys())

                for col_name in columns:
                    if col_name.lower().endswith("_id") and col_name.lower() != "id":
                        # Infer referenced table
                        ref_table = col_name[:-3]  # Remove '_id'
                        if ref_table in tables:
                            mermaid_lines.append(f"    {ref_table} ||--o{{ {table_name} : has")
            except Exception:
                continue

        return "\n".join(mermaid_lines)

    def generate_semantic_model_diagram(self, model: SemanticModel) -> str:
        """Generate Mermaid flowchart diagram from semantic model.

        Creates a flowchart showing logical tables, dimensions, facts, relationships,
        and metrics with color-coded styling for different element types.

        Args:
            model: SemanticModel object to visualize.

        Returns:
            Mermaid flowchart diagram markup as string.
        """
        mermaid_lines = ["graph TD"]

        # Add tables as nodes
        for table in model.tables:
            table_label = f"{table.name}\\n[{len(table.dimensions)} dims, {len(table.facts or [])} facts]"
            mermaid_lines.append(f'    {table.name}["{table_label}"]')
            mermaid_lines.append(f"    {table.name} --> {table.name}_dims[Dimensions]")

            # Add dimensions
            for dim in table.dimensions:
                dim_id = f"{table.name}_{dim.name}"
                mermaid_lines.append(f'    {table.name}_dims --> {dim_id}["{dim.name}\\n{dim.data_type or ""}"]')

            # Add facts
            if table.facts:
                mermaid_lines.append(f"    {table.name} --> {table.name}_facts[Facts]")
                for fact in table.facts:
                    fact_id = f"{table.name}_{fact.name}"
                    mermaid_lines.append(
                        f'    {table.name}_facts --> {fact_id}["{fact.name}\\n{fact.data_type or ""}"]'
                    )

        # Add relationships
        for rel in model.relationships:
            mermaid_lines.append(f"    {rel.left_table} -.-> {rel.right_table}")

        # Add metrics
        if model.metrics:
            mermaid_lines.append('    Metrics["📊 Metrics"]')
            for metric in model.metrics:
                metric_id = f"metric_{metric.name or 'unnamed'}"
                mermaid_lines.append(f'    Metrics --> {metric_id}["{metric.name or "Unnamed"}\\n{metric.expr or ""}"]')

        # Add styling
        mermaid_lines.extend([
            "    classDef tableClass fill:#e1f5fe",
            "    classDef dimClass fill:#f3e5f5",
            "    classDef factClass fill:#e8f5e8",
            "    classDef metricClass fill:#fff3e0",
        ])

        return "\n".join(mermaid_lines)

    def generate_quality_metrics_diagram(self, metrics: list[dict[str, Any]]) -> str:
        """Generate Mermaid flowchart diagram for quality metrics.

        Creates a flowchart showing quality metrics grouped by category (Schema vs Content)
        with color coding based on score thresholds (green/orange/red).

        Args:
            metrics: List of dictionaries containing metric data with 'name' and 'score' keys.

        Returns:
            Mermaid flowchart diagram markup as string.
        """
        mermaid_lines = ["graph LR"]

        # Group metrics by category
        schema_metrics = []
        content_metrics = []

        for i, metric in enumerate(metrics):
            if i < 5:  # First 5 are schema metrics
                schema_metrics.append(metric)
            else:
                content_metrics.append(metric)

        # Add schema quality section
        mermaid_lines.append('    Schema["📋 Schema Quality"]')
        for metric in schema_metrics:
            score = metric.get("score", 0)
            color = "green" if score >= 80 else "orange" if score >= 60 else "red"
            metric_id = metric["name"].replace(" ", "_")
            mermaid_lines.append(f'    Schema --> {metric_id}["{metric["name"]}\\n{score:.1f}%"]')
            mermaid_lines.append(f"    class {metric_id} {color}Class")

        # Add content quality section
        mermaid_lines.append('    Content["📊 Content Quality"]')
        for metric in content_metrics:
            score = metric.get("score", 0)
            color = "green" if score >= 80 else "orange" if score >= 60 else "red"
            metric_id = metric["name"].replace(" ", "_")
            mermaid_lines.append(f'    Content --> {metric_id}["{metric["name"]}\\n{score:.1f}%"]')
            mermaid_lines.append(f"    class {metric_id} {color}Class")

        # Add styling
        mermaid_lines.extend([
            "    classDef greenClass fill:#c8e6c9",
            "    classDef orangeClass fill:#ffe0b2",
            "    classDef redClass fill:#ffcdd2",
        ])

        return "\n".join(mermaid_lines)
