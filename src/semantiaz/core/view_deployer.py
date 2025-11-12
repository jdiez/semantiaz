"""Deploy semantic views from annotated YAML models."""

import snowflake.connector
import yaml

from ..models.semantic_model import SemanticModel


class ViewDeployer:
    """Deploy semantic views to Snowflake from annotated semantic models."""

    def __init__(self, config: dict[str, str]):
        self.config = config

    def load_semantic_model(self, yaml_path: str) -> SemanticModel:
        """Load semantic model from YAML file."""
        with open(yaml_path) as f:
            model_data = yaml.safe_load(f)
        return SemanticModel.from_dict(model_data)

    def generate_view_sql(self, model: SemanticModel, view_name: str) -> str:
        """Generate SQL for creating a semantic view."""
        # Get base tables
        base_tables = []
        for table in model.logical_tables:
            base_table = table.base_table
            full_name = f"{base_table.database}.{base_table.schema}.{base_table.table}"
            base_tables.append(f"{full_name} AS {table.name}")

        # Build SELECT clause with dimensions and metrics
        select_items = []

        # Add dimensions
        for table in model.logical_tables:
            for dim in table.dimensions:
                select_items.append(f"{table.name}.{dim.expr} AS {dim.name}")

        # Add measures/metrics
        for table in model.logical_tables:
            for measure in table.measures:
                select_items.append(f"{measure.expr} AS {measure.name}")

        # Add model-level metrics
        for metric in model.metrics:
            select_items.append(f"{metric.expr} AS {metric.name}")

        # Build FROM clause
        from_clause = base_tables[0] if base_tables else ""

        # Add JOINs
        join_clauses = []
        for rel in model.relationships:
            if rel.relationship_columns:
                join_col = rel.relationship_columns[0]
                join_clause = f"{rel.join_type} {rel.right_table} ON {rel.left_table}.{join_col.left_column} = {rel.right_table}.{join_col.right_column}"
                join_clauses.append(join_clause)

        # Construct final SQL using safe string formatting
        select_clause = ",\n    ".join(select_items)
        sql = f"CREATE OR REPLACE VIEW {view_name} AS\nSELECT\n    {select_clause}\nFROM {from_clause}"

        if join_clauses:
            join_clause_str = "\n".join(join_clauses)
            sql += f"\n{join_clause_str}"

        return sql

    def deploy_view(self, model: SemanticModel, view_name: str) -> bool:
        """Deploy semantic view to Snowflake."""
        try:
            sql = self.generate_view_sql(model, view_name)

            with snowflake.connector.connect(**self.config) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return True
        except Exception as e:
            print(f"Error deploying view: {e}")
            return False

    def deploy_all_views(self, yaml_path: str, view_prefix: str = "semantic_") -> list[str]:
        """Deploy all possible views from a semantic model."""
        model = self.load_semantic_model(yaml_path)
        deployed_views = []

        # Deploy a main view combining all tables
        main_view_name = f"{view_prefix}{model.name}"
        if self.deploy_view(model, main_view_name):
            deployed_views.append(main_view_name)

        # Deploy individual table views
        for table in model.logical_tables:
            table_model = SemanticModel(
                name=f"{model.name}_{table.name}",
                description=f"View for {table.name}",
                logical_tables=[table],
                metrics=[],
                relationships=[],
            )
            view_name = f"{view_prefix}{table.name}"
            if self.deploy_view(table_model, view_name):
                deployed_views.append(view_name)

        return deployed_views
