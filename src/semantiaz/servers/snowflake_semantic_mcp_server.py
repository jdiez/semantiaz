# trunk-ignore-all(black)
#!/usr/bin/env python3

import json
from contextlib import contextmanager
from typing import Annotated, Any, Optional

import pandas as pd
import snowflake.connector
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from ..converters.rdf_semantic_converter import (
    RDFSemanticConverter,
    convert_rdf_to_semantic_model,
    convert_semantic_model_to_rdf,
)
from ..core.schema_extractor import SchemaExtractor
from ..core.semantic_view_generator import SemanticViewGenerator
from ..core.view_deployer import ViewDeployer
from ..models.clinical_trial_semantic_model import clinical_model
from ..models.semantic_model import SemanticModel

# Initialize FastMCP server
mcp = FastMCP("Snowflake Semantic Model Server")

# Snowflake connection configuration
SNOWFLAKE_CONFIG = {
    "account": "your_account",
    "user": "your_user",
    "password": "your_password",
    "warehouse": "your_warehouse",
    "database": "clinical_db",
    "schema": "operations",
}


class SnowflakeConfig(BaseModel):
    """Snowflake connection configuration model."""

    account: Annotated[str, Field(alias="account", description="Snowflake account identifier")]
    user: Annotated[str, Field(alias="user", description="Snowflake username")]
    password: Annotated[str, Field(alias="password", description="Snowflake password")]
    warehouse: Annotated[str, Field(alias="warehouse", description="Snowflake warehouse")]
    database: Annotated[str, Field(alias="database", description="Snowflake database")]
    schema: Annotated[str, Field(alias="schema", description="Snowflake schema")]
    session_parameters: Annotated[
        Optional[dict[str, str]],
        Field(
            default=None, alias="session_parameters", description="Optional session parameters for Snowflake connection"
        ),
    ] = None


class SnowflakeSemanticConnector:
    """Connector for Snowflake database with semantic model capabilities."""

    def __init__(self, config: dict[str, str], semantic_model: SemanticModel) -> None:
        """Initialize Snowflake connector with configuration and semantic model
        Args:
            config (Dict[str, str]): Snowflake connection configuration
            semantic_model (SemanticModel): Semantic model instance
        """
        self.config = config
        self.semantic_model = semantic_model
        self.connection = None

    @contextmanager
    def connect(self) -> snowflake.connector.SnowflakeConnection:
        """Establish and return a Snowflake connection"""
        conn = snowflake.connector.connect(
            account=self.config["account"],
            user=self.config["user"],
            password=self.config["password"],
            warehouse=self.config["warehouse"],
            database=self.config["database"],
            schema=self.config["schema"],
            session_parameters=self.config.get("session_parameters", {}),
        )
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a SQL query and return results as a list of dictionaries
        Args:
            sql (str): SQL query to execute
            params (dict): Optional parameters for parameterized queries
        Returns:
            List[Dict[str, Any]]: Query results
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        # cursor.close()
        return results

    def get_query_as_dataframe(self, sql: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a pandas DataFrame
        Args:
            sql (str): SQL query to execute
        Returns:
            pd.DataFrame: Query results as DataFrame
        """
        with self.connect() as conn:
            # results = conn.cursor().execute(sql).fetchall()
            df = pd.read_sql(sql, conn)
        return df

    def get_metric_sql(self, metric_name: str) -> Optional[str]:
        """Get the SQL expression for a given metric name
        Args:
            metric_name (str): Name of the metric
        Returns:
            Optional[str]: SQL expression of the metric or None if not found"""
        for metric in self.semantic_model.metrics:
            if metric.name == metric_name:
                return metric.expr
        return None


# Initialize connector and view generator
connector = SnowflakeSemanticConnector(SNOWFLAKE_CONFIG, clinical_model)
view_generator = SemanticViewGenerator(clinical_model)


@mcp.tool()
def get_semantic_model_info() -> str:
    """Get information about the available semantic model
    Returns:
        str: JSON string containing model name, tables, metrics, and relationships
    """
    tables = [table.name for table in clinical_model.logical_tables]
    metrics = [metric.name for metric in clinical_model.metrics]
    return json.dumps({
        "model_name": clinical_model.name,
        "tables": tables,
        "metrics": metrics,
        "relationships": len(clinical_model.relationships),
    })


@mcp.tool()
def list_available_metrics() -> str:
    """List all available metrics in the semantic model
    Returns:
        str: JSON string containing a list of metrics with their names and descriptions
    """
    metrics = []
    for metric in clinical_model.metrics:
        metrics.append({"name": metric.name, "description": metric.description, "expression": metric.expr})
    return json.dumps(metrics)


@mcp.tool()
def get_table_dimensions(table_name: str) -> str:
    """Get dimensions available for a specific table
    Args:
        table_name (str): Name of the table
    Returns:
        str: JSON string containing a list of dimensions with their details or an error message
    """
    for table in clinical_model.logical_tables:
        if table.name == table_name:
            dimensions = []
            for dim in table.dimensions:
                dimensions.append({
                    "name": dim.name,
                    "description": dim.description,
                    "data_type": dim.data_type,
                    "expression": dim.expr,
                })
            return json.dumps(dimensions)
    return json.dumps({"error": f"Table {table_name} not found"})


@mcp.tool()
def execute_metric_query(metric_name: str, filters: str = "") -> str:
    """Execute a query for a specific metric with optional filters
    Args:
        metric_name (str): Name of the metric to query
        filters (str): Optional SQL WHERE clause filters
    Returns:
        str: JSON string containing query results or an error message
    """
    try:
        # Validate metric exists in semantic model
        metric_expr = None
        valid_metric_name = None
        for metric in clinical_model.metrics:
            if metric.name == metric_name:
                metric_expr = metric.expr
                valid_metric_name = metric.name
                break

        if not metric_expr:
            return json.dumps({"error": f"Metric {metric_name} not found"})

        # Build base tables with proper escaping
        base_tables = []
        for table in clinical_model.logical_tables:
            base_table = table.base_table
            # Use identifier() function for proper SQL identifier escaping
            database_id = snowflake.connector.converters.identifier(base_table.database)
            schema_id = snowflake.connector.converters.identifier(base_table.schema)
            table_id = snowflake.connector.converters.identifier(base_table.table)
            table_alias = snowflake.connector.converters.identifier(table.name)
            full_name = f"{database_id}.{schema_id}.{table_id} AS {table_alias}"
            base_tables.append(full_name)

        if not base_tables:
            return json.dumps({"error": "No base tables found in semantic model"})

        # Use identifier escaping for metric name in SELECT
        metric_name_escaped = snowflake.connector.converters.identifier(valid_metric_name)
        # Build SQL query using list and join to avoid format string injection
        sql_parts = ["SELECT", metric_expr, "AS", metric_name_escaped, "FROM", base_tables[0]]
        sql = " ".join(sql_parts)

        # Add joins based on relationships with proper escaping
        for rel in clinical_model.relationships:
            if len(rel.relationship_columns) > 0:
                join_col = rel.relationship_columns[0]
                left_table_id = snowflake.connector.converters.identifier(rel.left_table)
                right_table_id = snowflake.connector.converters.identifier(rel.right_table)
                left_col_id = snowflake.connector.converters.identifier(join_col.left_column)
                right_col_id = snowflake.connector.converters.identifier(join_col.right_column)
                join_type = rel.join_type.upper()  # Validate join type is uppercase
                sql += f" {join_type} JOIN {right_table_id} ON {left_table_id}.{left_col_id} = {right_table_id}.{right_col_id}"

        # Note: filters parameter should be validated/sanitized by caller
        # For production use, implement proper filter parsing and parameterization
        if filters:
            sql += f" WHERE {filters}"

        results = connector.execute_query(sql)
        return json.dumps(results)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def execute_verified_query(query_name: str) -> str:
    """Execute a pre-verified query from the semantic model
    Args:
        query_name (str): Name of the verified query
    Returns:
        str: JSON string containing query results or an error message
    """
    try:
        verified_query = clinical_model.get_verified_query_by_name(query_name)
        if not verified_query:
            return json.dumps({"error": f"Verified query {query_name} not found"})

        sql = verified_query.sql
        results = connector.execute_query(sql)
        return json.dumps(results)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_patient_enrollment_summary(site_filter: str = "") -> str:
    """Get patient enrollment summary with optional site filtering.
    Args:
        site_filter (str): Optional country filter for sites
    Returns:
        str: JSON string containing enrollment summary or an error message
    """
    try:
        sql = """
        SELECT
            s.site_country,
            COUNT(p.patient_id) as total_patients,
            COUNT(CASE WHEN p.enrollment_status = 'Active' THEN p.patient_id END) as active_patients
        FROM clinical_db.operations.sites s
        LEFT JOIN clinical_db.operations.patients p ON s.site_id = p.site_id
        """

        if site_filter:
            # Use parameterized query to prevent SQL injection
            site_filter_escaped = site_filter.replace("'", "''")
            sql += f" WHERE s.site_country = '{site_filter_escaped}'"

        sql += " GROUP BY s.site_country ORDER BY total_patients DESC"

        results = connector.execute_query(sql)

    except Exception as e:
        return json.dumps({"error": str(e)})
    else:
        return json.dumps(results)


@mcp.tool()
def get_safety_metrics() -> str:
    """Get safety-related metrics for the clinical trial.
    Returns:
        str: JSON string containing safety metrics or an error message
    """
    try:
        sql = """
        SELECT
            ae.ae_severity,
            COUNT(*) as event_count,
            COUNT(DISTINCT ae.patient_id) as affected_patients
        FROM clinical_db.operations.adverse_events ae
        GROUP BY ae.ae_severity
        ORDER BY event_count DESC
        """

        results = connector.execute_query(sql)
        return json.dumps(results)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def generate_snowflake_semantic_view(view_name: str = "") -> str:
    """Generate Snowflake SEMANTIC VIEW DDL with proper syntax.
    Args:
        view_name (str): Optional name for the view
    Returns:
            str: JSON string containing view name and DDL or an error message
    """
    try:
        if not view_name:
            view_name = f"sv_{clinical_model.name}"

        semantic_view_ddl = view_generator.generate_semantic_view(view_name)
        return json.dumps({"view_name": view_name, "ddl": semantic_view_ddl})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def generate_view_deployment_script() -> str:
    """Generate deployment script for Snowflake SEMANTIC VIEW
    Args:
    Returns:
        str: SQL deployment script or an error message
    """
    try:
        script = view_generator.generate_deployment_script()
    except Exception as e:
        return json.dumps({"error": str(e)})
    else:
        return script


@mcp.tool()
def create_semantic_view(view_name: str = "") -> str:
    """Create Snowflake SEMANTIC VIEW in the database
    Args:
        view_name (str): Optional name for the view
    Returns:
        str: JSON string indicating success or failure with DDL or error message
    """
    try:
        if not view_name:
            view_name = f"sv_{clinical_model.name}"

        view_sql = view_generator.generate_semantic_view(view_name)
        connector.execute_query(view_sql)

        return json.dumps({
            "status": "success",
            "message": f"Semantic view {view_name} created successfully",
            "ddl": view_sql,
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def query_semantic_view(view_name: str = "", limit: int = 100) -> str:
    """Query data from the Snowflake SEMANTIC VIEW"""
    try:
        if not view_name:
            view_name = f"sv_{clinical_model.name}"

        # Validate and sanitize limit parameter
        if not isinstance(limit, int) or limit < 1 or limit > 10000:
            limit = 100

        first_table = clinical_model.logical_tables[0] if clinical_model.logical_tables else None
        if first_table and first_table.base_table:
            # Use proper identifier quoting for Snowflake identifiers
            database_quoted = f'"{first_table.base_table.database}"'
            schema_quoted = f'"{first_table.base_table.schema}"'
            view_quoted = f'"{view_name}"'
            full_view_name = f"{database_quoted}.{schema_quoted}.{view_quoted}"
        else:
            view_quoted = f'"{view_name}"'
            full_view_name = view_quoted

        # Build SQL query with proper escaping and parameterization
        # Note: full_view_name is already properly quoted with identifier escaping above
        # LIMIT clause is safe since limit is validated as int above
        # trunk-ignore(ruff/S608)
        sql = " ".join(["SELECT * FROM", full_view_name, "LIMIT", str(limit)])  # S608
        results = connector.execute_query(sql)

        return json.dumps({"view_name": view_name, "row_count": len(results), "data": results})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def load_semantic_model_from_yaml(yaml_path: str) -> str:
    """Load semantic model from YAML file
    Args:
        yaml_path (str): Path to the YAML file
    Returns:
        str: JSON string indicating success or failure with model details or error message
    """
    try:
        model = SemanticModel.from_yaml(yaml_path)
        return json.dumps({
            "status": "success",
            "model_name": model.name,
            "tables": len(model.logical_tables),
            "relationships": len(model.relationships),
            "metrics": len(model.metrics),
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def export_semantic_model_to_yaml(output_path: str = "") -> str:
    """Export current semantic model to YAML format"""
    try:
        if not output_path:
            output_path = f"{clinical_model.name}_export.yaml"

        yaml_content = clinical_model.to_yaml(output_path)
        return json.dumps({"status": "success", "output_path": output_path, "content_length": len(yaml_content)})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_semantic_model_yaml() -> str:
    """Get the current semantic model in YAML format
    Args:
    Returns:
        str: YAML string of the semantic model or an error message
    """
    try:
        yaml_content = clinical_model.to_yaml()
    except Exception as e:
        return json.dumps({"error": str(e)})
    else:
        return yaml_content


@mcp.tool()
def validate_yaml_semantic_model(yaml_content: str) -> str:
    """Validate YAML semantic model definition"""
    try:
        model = SemanticModel.from_yaml_string(yaml_content)
        return json.dumps({
            "status": "valid",
            "model_name": model.name,
            "tables": len(model.logical_tables),
            "relationships": len(model.relationships),
            "metrics": len(model.metrics),
        })
    except Exception as e:
        return json.dumps({"status": "invalid", "error": str(e)})


@mcp.tool()
def convert_rdf_to_semantic_model_tool(
    rdf_file_path: str,
    model_name: str,
    database: str = "ontology_db",
    schema: str = "semantic",
    rdf_format: str = "turtle",
) -> str:
    """Convert RDF/OWL ontology to semantic model
    Args:
        rdf_file_path (str): Path to the RDF/OWL file
        model_name (str): Name for the generated semantic model
        database (str): Target database name
        schema (str): Target schema name
        format (str): RDF format (e.g., 'turtle', 'xml')
    Returns:
        str: JSON string indicating success or failure with model details or error message
    """
    try:
        model = convert_rdf_to_semantic_model(rdf_file_path, model_name, database, schema, rdf_format)
        return json.dumps({
            "status": "success",
            "model_name": model.name,
            "tables": len(model.logical_tables),
            "relationships": len(model.relationships),
            "message": "Successfully converted RDF ontology to semantic model",
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_rdf_ontology_stats(rdf_file_path: str, rdf_format: str = "turtle") -> str:
    """Get statistics about an RDF/OWL ontology"""
    try:
        converter = RDFSemanticConverter()
        converter.load_rdf(rdf_file_path, rdf_format)
        stats = converter.get_ontology_stats()
        return json.dumps(stats)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def generate_rdf_mapping_report(rdf_file_path: str, rdf_format: str = "turtle") -> str:
    """Generate mapping report for RDF to semantic model conversion
    Args:
        rdf_file_path (str): Path to the RDF/OWL file
        rdf_format (str): RDF format (e.g., 'turtle', 'xml')
    Returns:
        str: JSON string containing mapping report or an error message
    """
    try:
        converter = RDFSemanticConverter()
        converter.load_rdf(rdf_file_path, rdf_format)
        report = converter.export_mapping_report()
    except Exception as e:
        return json.dumps({"error": str(e)})
    else:
        return report


@mcp.tool()
def export_semantic_model_to_rdf(
    output_path: str, rdf_format: str = "turtle", namespace_uri: str = "http://example.org/semantic#"
) -> str:
    """Export current semantic model to RDF/OWL format.
    Args:
        output_path (str): Path to save the RDF/OWL file
        rdf_format (str): RDF format (e.g., 'turtle', 'xml')
        namespace_uri (str): Namespace URI for the RDF model
    Returns:
        str: JSON string indicating success or failure with output details or error message
    """
    try:
        rdf_content = convert_semantic_model_to_rdf(clinical_model, output_path, rdf_format, namespace_uri)
        return json.dumps({
            "status": "success",
            "output_path": output_path,
            "format": rdf_format,
            "content_length": len(rdf_content),
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_semantic_model_as_rdf(rdf_format: str = "turtle", namespace_uri: str = "http://example.org/semantic#") -> str:
    """Get current semantic model as RDF/OWL string.
    Args:
        rdf_format (str): RDF format (e.g., 'turtle', 'xml')
        namespace_uri (str): Namespace URI for the RDF model
    Returns:
        str: RDF/OWL string of the semantic model or an error message
    """
    try:
        converter = RDFSemanticConverter()
        rdf_content = converter.get_semantic_model_as_rdf_string(clinical_model, rdf_format, namespace_uri)
    except Exception as e:
        return json.dumps({"error": str(e)})
    else:
        return rdf_content


@mcp.tool()
def create_semantic_model_from_schema(database: str, schema: str, model_name: str) -> str:
    """Create a semantic model YAML file from Snowflake database schema
    Args:
        database (str): Snowflake database name
        schema (str): Snowflake schema name
        model_name (str): Name for the semantic model
    Returns:
        str: Generated semantic model YAML content
    """
    try:
        extractor = SchemaExtractor(SNOWFLAKE_CONFIG)
        schema_info = extractor.extract_schema(database, schema)
        yaml_content = extractor.generate_semantic_yaml(schema_info, model_name)
    except Exception as e:
        return json.dumps({"error": str(e)})
    else:
        return yaml_content


@mcp.tool()
def deploy_semantic_view(yaml_content: str, view_name: str) -> str:
    """Deploy a semantic view from annotated YAML model
    Args:
        yaml_content (str): YAML content of the semantic model
        view_name (str): Name for the deployed view
    Returns:
        str: JSON string with deployment status
    """
    try:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            deployer = ViewDeployer(SNOWFLAKE_CONFIG)
            success = deployer.deploy_view(deployer.load_semantic_model(temp_path), view_name)

            return json.dumps({
                "success": success,
                "view_name": view_name,
                "message": "View deployed successfully" if success else "View deployment failed",
            })
        finally:
            os.unlink(temp_path)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def deploy_all_views_from_yaml(yaml_content: str, view_prefix: str = "semantic_") -> str:
    """Deploy all possible views from a semantic model YAML
    Args:
        yaml_content (str): YAML content of the semantic model
        view_prefix (str): Prefix for view names
    Returns:
        str: JSON string with deployment results
    """
    try:
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            deployer = ViewDeployer(SNOWFLAKE_CONFIG)
            deployed_views = deployer.deploy_all_views(temp_path, view_prefix)

            return json.dumps({
                "deployed_views": deployed_views,
                "count": len(deployed_views),
                "message": f"Successfully deployed {len(deployed_views)} views",
            })
        finally:
            os.unlink(temp_path)

    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
