"""
Snowflake Semantic View Generator
Generates Snowflake SEMANTIC VIEW DDL based on semantic model definitions
"""

from typing import Optional

from semantic_model import SemanticModel


class SemanticViewGenerator:
    def __init__(self, semantic_model: SemanticModel):
        self.semantic_model = semantic_model

    def _format_synonyms(self, synonyms: list[str]) -> str:
        """Format synonyms for Snowflake syntax"""
        if not synonyms:
            return ""
        formatted = "', '".join(synonyms)
        return f"WITH SYNONYMS = ('{formatted}')"

    def _generate_logical_tables(self) -> str:
        """Generate TABLES clause for semantic view"""
        table_defs = []

        for table in self.semantic_model.logical_tables:
            base_table = table.base_table
            full_name = f"{base_table.database}.{base_table.schema}.{base_table.table}"

            table_def = f"{table.name} AS {full_name}"

            # Add primary key
            if table.primary_key.names:
                pk_cols = ", ".join(table.primary_key.names)
                table_def += f" PRIMARY KEY ({pk_cols})"

            # Add comment if description exists
            if table.description:
                table_def += f" COMMENT = '{table.description}'"

            table_defs.append(table_def)

        return ",\n    ".join(table_defs)

    def _generate_relationships(self) -> str:
        """Generate RELATIONSHIPS clause for semantic view"""
        if not self.semantic_model.relationships:
            return ""

        rel_defs = []

        for rel in self.semantic_model.relationships:
            if not rel.relationship_columns:
                continue

            join_col = rel.relationship_columns[0]
            rel_def = (
                f"{rel.left_table} ({join_col.left_column}) REFERENCES {rel.right_table} ({join_col.right_column})"
            )
            rel_defs.append(rel_def)

        return ",\n    ".join(rel_defs)

    def _generate_dimensions(self) -> str:
        """Generate DIMENSIONS clause for semantic view"""
        dim_defs = []

        for table in self.semantic_model.logical_tables:
            for dim in table.dimensions:
                if dim.expr:
                    dim_def = f"PUBLIC {table.name}.{dim.name} AS {dim.expr}"
                else:
                    dim_def = f"PUBLIC {table.name}.{dim.name} AS {dim.name}"

                # Add synonyms
                if dim.synonyms:
                    dim_def += f" {self._format_synonyms(dim.synonyms)}"

                # Add comment
                if dim.description:
                    dim_def += f" COMMENT = '{dim.description}'"

                dim_defs.append(dim_def)

        return ",\n    ".join(dim_defs)

    def _generate_metrics(self) -> str:
        """Generate METRICS clause for semantic view"""
        metric_defs = []

        for metric in self.semantic_model.metrics:
            if not metric.expr or not metric.name:
                continue

            # Use first table as default table alias
            table_alias = self.semantic_model.logical_tables[0].name if self.semantic_model.logical_tables else "t"
            metric_def = f"PUBLIC {table_alias}.{metric.name} AS {metric.expr}"

            # Add comment
            if metric.description:
                metric_def += f" COMMENT = '{metric.description}'"

            metric_defs.append(metric_def)

        return ",\n    ".join(metric_defs)

    def generate_semantic_view(self, view_name: Optional[str] = None) -> str:
        """Generate complete Snowflake SEMANTIC VIEW DDL"""
        if not view_name:
            view_name = f"sv_{self.semantic_model.name}"

        # Get database and schema from first table
        first_table = self.semantic_model.logical_tables[0] if self.semantic_model.logical_tables else None
        if first_table and first_table.base_table:
            full_view_name = f"{first_table.base_table.database}.{first_table.base_table.schema}.{view_name}"
        else:
            full_view_name = view_name

        sql_parts = [f"CREATE OR REPLACE SEMANTIC VIEW {full_view_name}"]

        # TABLES clause
        tables_clause = self._generate_logical_tables()
        if tables_clause:
            sql_parts.append(f"  TABLES (\n    {tables_clause}\n  )")

        # RELATIONSHIPS clause
        relationships_clause = self._generate_relationships()
        if relationships_clause:
            sql_parts.append(f"  RELATIONSHIPS (\n    {relationships_clause}\n  )")

        # DIMENSIONS clause
        dimensions_clause = self._generate_dimensions()
        if dimensions_clause:
            sql_parts.append(f"  DIMENSIONS (\n    {dimensions_clause}\n  )")

        # METRICS clause
        metrics_clause = self._generate_metrics()
        if metrics_clause:
            sql_parts.append(f"  METRICS (\n    {metrics_clause}\n  )")

        # Add comment
        sql_parts.append(f"  COMMENT = 'Semantic view for {self.semantic_model.name} clinical trial operations'")

        return "\n".join(sql_parts)

    def generate_all_views(self) -> dict[str, str]:
        """Generate semantic view DDL"""
        view_name = f"sv_{self.semantic_model.name}"
        return {view_name: self.generate_semantic_view(view_name)}

    def generate_deployment_script(self) -> str:
        """Generate deployment script for semantic view"""
        views = self.generate_all_views()

        script_parts = [
            "-- Snowflake Semantic View Deployment Script",
            f"-- Generated for semantic model: {self.semantic_model.name}",
            "-- This script creates a Snowflake SEMANTIC VIEW",
            "",
            "-- Enable semantic views (if not already enabled)",
            "-- ALTER ACCOUNT SET ENABLE_SEMANTIC_VIEWS = TRUE;",
            "",
        ]

        for view_name, view_sql in views.items():
            script_parts.extend([
                f"-- {view_name}",
                view_sql + ";",
                "",
                "-- Grant usage on semantic view",
                f"-- GRANT USAGE ON SEMANTIC VIEW {view_name} TO ROLE <role_name>;",
                "",
            ])

        return "\n".join(script_parts)
