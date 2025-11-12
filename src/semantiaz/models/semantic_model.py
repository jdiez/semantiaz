"""Framework to build Snowflake Cortex Semantic Models"""

import json
from typing import Annotated, Optional

import yaml
from pydantic import BaseModel, Field
from typing_extensions import Literal


class SemanticModelError(Exception):
    """Base exception for semantic model operations"""

    pass


class NoCurrentModelError(SemanticModelError):
    """Raised when no current model is available"""

    pass


class TableNotFoundError(SemanticModelError):
    """Raised when a table is not found"""

    pass


class CortexSearchService(BaseModel):
    """Configuration for Cortex Search Service integration"""

    service: Annotated[str | None, Field(default=None, description="Search service name")]
    literal_column: Annotated[str | None, Field(default=None, description="Literal column for search")]
    database: Annotated[str | None, Field(default=None, description="Database for search service")]
    schema: Annotated[str | None, Field(default=None, description="Schema for search service")]


class Dimension(BaseModel):
    """A dimension represents categorical data that provides context to facts, such as product, customer, or location information.
    Dimensions typically contain descriptive text values, such as product names or customer addresses.
    They are used to filter, group, and label facts in analyses and reports."""

    name: Annotated[str, Field(description="The name of the dimension")]
    synonyms: Annotated[list[str], Field(default=[], description="Alternative names for the dimension")]
    description: Annotated[
        str | None, Field(default=None, description="A description of what the dimension represents")
    ]
    expr: Annotated[str | None, Field(default=None, description="SQL expression defining the dimension")]
    data_type: Annotated[str | None, Field(default=None, description="The data type of the dimension")]
    unique: Annotated[bool, Field(default=False, description="Whether the dimension values are unique")]
    cortex_search_service: Annotated[
        CortexSearchService | None, Field(default=None, description="Cortex search service configuration")
    ]
    is_enum: Annotated[bool, Field(default=False, description="Whether the dimension is an enumeration")]


class TimeDimension(BaseModel):
    """A time dimension provides temporal context for analyzing facts across different periods.
    It enables tracking metrics over specific time intervals (dates, months, years) and supports analyses such as trend identification and period-over-period comparisons."""

    name: Annotated[str, Field(description="The name of the time dimension")]
    synonyms: Annotated[list[str], Field(default=[], description="Alternative names for the time dimension")]
    description: Annotated[str | None, Field(default=None, description="A description of the time dimension")]
    expr: Annotated[str | None, Field(default=None, description="SQL expression defining the time dimension")]
    data_type: Annotated[int | float | None, Field(default=None, description="The data type of the time dimension")]
    unique: Annotated[bool, Field(default=False, description="Whether the time dimension values are unique")]


class Fact(BaseModel):
    """Facts are measurable, quantitative data that provide context for analyses.
    Facts represent numeric values related to business processes, such as sales, cost, or quantity.
    A fact is an unaggregated, row-level concept."""

    name: Annotated[str, Field(description="The name of the fact")]
    synonyms: Annotated[list[str], Field(default=[], description="Alternative names for the fact")]
    description: Annotated[str | None, Field(default=None, description="A description of what the fact represents")]
    access_modifier: Annotated[
        Literal["public_access", "private_access"],
        Field(default="public_access", description="Access level for the fact"),
    ]
    expr: Annotated[str | None, Field(default=None, description="SQL expression defining the fact")]
    data_type: Annotated[str | None, Field(default=None, description="The data type of the fact")]


class Metric(BaseModel):
    """A metric is a quantifiable measure of business performance expressed as a SQL formula.
    You can use metrics as key performance indicators (KPIs) in reports and dashboards.
    You can calculate two kinds of metrics:
        - Regular metrics aggregate values (using functions such as SUM or AVG) over a fact column.
        - Derived metrics are calculated from existing metrics, using arithmetic operations such as addition or division.
    Define metrics at their most granular level for aggregation at higher levels.
    """

    name: Annotated[str | None, Field(default=None, description="The name of the metric")]
    synonyms: Annotated[list[str], Field(default=[], description="Alternative names for the metric")]
    description: Annotated[str | None, Field(default=None, description="A description of what the metric measures")]
    access_modifier: Annotated[
        Literal["public_access", "private_access"],
        Field(default="public_access", description="Access level for the metric"),
    ]
    expr: Annotated[str | None, Field(default=None, description="SQL expression defining the metric calculation")]


class Filter(BaseModel):
    """A filter is a condition that limits query results to specific data subsets based on criteria such as time period, location, or category."""

    name: Annotated[str, Field(description="The name of the filter")]
    synonyms: Annotated[list[str], Field(default=[], description="Alternative names for the filter")]
    description: Annotated[str | None, Field(default=None, description="A description of what the filter does")]
    comments: Annotated[list[str], Field(default=[], description="Additional comments about the filter")]
    expr: Annotated[str | None, Field(default=None, description="SQL expression defining the filter condition")]


class RelationshipColumn(BaseModel):
    """Defines a pair of columns that form a relationship between two tables."""

    left_column: Annotated[
        str | None, Field(default=None, description="Column name from the left table in the relationship")
    ]
    right_column: Annotated[
        str | None, Field(default=None, description="Column name from the right table in the relationship")
    ]


class Relationship(BaseModel):
    """Relationships connect logical tables through joins on shared keys.
    For example, there could be a relationship between the customers and orders tables through a join on the customer_id column.
    You can use joins to analyze order data with customer attributes."""

    name: Annotated[str, Field(description="The name of the relationship")]
    left_table: Annotated[str, Field(description="Name of the left table in the relationship")]
    right_table: Annotated[str, Field(description="Name of the right table in the relationship")]
    relationship_columns: Annotated[
        list[RelationshipColumn], Field(description="List of column pairs that define the relationship")
    ]
    join_type: Annotated[Literal["left_outer", "inner"], Field(default="inner", description="Type of SQL join to use")]
    relationship_type: Annotated[
        Literal["one_to_one", "many_to_one"],
        Field(default="many_to_one", description="Cardinality of the relationship"),
    ]


class VerifiedQuery(BaseModel):
    """A verified query is a pre-defined SQL query that has been validated to produce correct results for a specific natural language question.
    It serves as a benchmark for evaluating the accuracy of AI-generated queries against known correct outputs."""

    name: Annotated[str | None, Field(default=None, description="A descriptive name of the query")]
    question: Annotated[
        str | None, Field(default=None, description="The natural language question that this query answers")
    ]
    verified_at: Annotated[
        int | None,
        Field(
            default=None,
            description="Time (in seconds since the UNIX epoch, January 1, 1970) when the query was verified",
        ),
    ]
    verified_by: Annotated[str | None, Field(default=None, description="Name of the person who verified the query")]
    use_as_onboarding_question: Annotated[
        bool, Field(default=False, description="Marks this question as an onboarding question for the end user")
    ]
    sql: Annotated[str | None, Field(default=None, description="The SQL query for answering the question")]


class CustomInstruction(BaseModel):
    """Custom instructions provide additional context or guidelines for using the semantic model.
    They can help tailor the behavior of AI systems or other tools that interact with the model."""

    instruction_text: Annotated[str, Field(description="Custom instruction text for the semantic model")]


class Columns(BaseModel):
    """A collection of column names used for primary keys or other purposes.
    This class is used to define the structure of primary keys in logical tables."""

    names: Annotated[list[str], Field(default=[], description="List of column names")]


class BaseTable(BaseModel):
    """A base table represents a physical table in the database that underlies a logical table in the semantic model.
    It contains metadata about the table's location and structure."""

    database: Annotated[str | None, Field(default=None, description="Database name containing the table")]
    schema: Annotated[str | None, Field(default=None, description="Schema name containing the table")]
    table: Annotated[str | None, Field(default=None, description="Table name")]


class LogicalTable(BaseModel):
    """A logical table represents a conceptual table in the semantic model.
    It may map to one or more physical tables in the database and contains dimensions that define its structure."""

    name: Annotated[str, Field(description="The name of the logical table")]
    description: Annotated[str | None, Field(default=None, description="A description of the logical table")]
    base_table: Annotated[BaseTable | None, Field(default=None, description="The underlying physical table")]
    primary_key: Annotated[Columns | None, Field(default=None, description="Primary key columns for this table")]
    dimensions: Annotated[list[Dimension], Field(default=[], description="List of dimensions in this table")]
    time_dimensions: Annotated[
        list[TimeDimension], Field(default=[], description="List of time dimensions in this table")
    ]
    facts: Annotated[list[Fact], Field(default=[], description="List of facts in this table")]
    metrics: Annotated[list[Metric], Field(default=[], description="List of metrics scoped to this table")]
    filters: Annotated[list[Filter], Field(default=[], description="List of filters for this table")]


class SemanticModel(BaseModel):
    """A semantic model defines a business-oriented representation of data for analysis and reporting.
    It includes logical tables, relationships, dimensions, and metrics that provide a unified view of the underlying data sources."""

    name: Annotated[str, Field(description="The name of the semantic model")]
    description: Annotated[str | None, Field(default=None, description="Description of the semantic model")]
    comments: Annotated[str | None, Field(default=None, description="Additional comments about the semantic model")]
    logical_tables: Annotated[
        list[LogicalTable], Field(default=[], description="List of logical tables in the semantic model")
    ]
    relationships: Annotated[list[Relationship], Field(default=[], description="List of relationships between tables")]
    metrics: Annotated[list[Metric], Field(default=[], description="List of metrics scoped to the semantic model")]
    verified_queries: Annotated[
        list[VerifiedQuery], Field(default=[], description="List of verified queries for the model")
    ]
    custom_instructions: Annotated[
        list[CustomInstruction], Field(default=[], description="List of custom instructions for the model")
    ]

    def add_table(self, table: LogicalTable) -> None:
        """Add a logical table to the semantic model"""
        # Check if the table already exists
        for existing_table in self.logical_tables:
            if existing_table.name == table.name:
                return
        self.logical_tables.append(table)

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the semantic model"""
        # Check if the relationship already exists
        for existing_relationship in self.relationships:
            if existing_relationship.name == relationship.name:
                return
        self.relationships.append(relationship)

    def add_metric(self, metric: Metric) -> None:
        """Add a metric to the semantic model"""
        # Check if the metric already exists
        for existing_metric in self.metrics:
            if existing_metric.name == metric.name:
                return
        self.metrics.append(metric)

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "SemanticModel":
        """Load semantic model from YAML file"""
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        # Support 'tables' as alias for 'logical_tables'
        if "tables" in data and "logical_tables" not in data:
            data["logical_tables"] = data.pop("tables")
        return cls.model_validate(data)

    @classmethod
    def from_yaml_string(cls, yaml_string: str) -> "SemanticModel":
        """Load semantic model from YAML string"""
        data = yaml.safe_load(yaml_string)
        # Support 'tables' as alias for 'logical_tables'
        if "tables" in data and "logical_tables" not in data:
            data["logical_tables"] = data.pop("tables")
        return cls.model_validate(data)

    def to_yaml(self, yaml_path: Optional[str] = None) -> str:
        """Export semantic model to YAML format"""
        data = self.model_dump(exclude_none=True)
        # Use 'tables' instead of 'logical_tables' in YAML output
        if "logical_tables" in data:
            data["tables"] = data.pop("logical_tables")
        yaml_content = yaml.dump(data, default_flow_style=False, sort_keys=False)
        if yaml_path:
            with open(yaml_path, "w") as f:
                f.write(yaml_content)
        return yaml_content

    def to_json(self, json_path: Optional[str] = None) -> str:
        """Export semantic model to JSON format"""
        json_content = json.dumps(self.model_dump(exclude_none=True), indent=2)
        if json_path:
            with open(json_path, "w") as f:
                f.write(json_content)
        return json_content

    def get_table(self, name: str) -> LogicalTable | None:
        """Get a table by name"""
        return next((t for t in self.logical_tables if t.name == name), None)

    def get_metric(self, name: str) -> Metric | None:
        """Get a metric by name"""
        return next((m for m in self.metrics if m.name == name), None)

    def get_relationship(self, name: str) -> Relationship | None:
        """Get a relationship by name"""
        return next((r for r in self.relationships if r.name == name), None)


class SemanticModelBuilder(BaseModel):
    """Builder class for constructing semantic models programmatically.
    Provides fluent API for building complex semantic models step by step."""

    models: Annotated[
        list[SemanticModel], Field(default=[], description="List of semantic models managed by this builder")
    ]
    current_model: Annotated[
        SemanticModel | None, Field(default=None, description="Currently active model being built")
    ]

    def create_model(self, name: str, description: str | None = None) -> "SemanticModelBuilder":
        """Create a new semantic model and set it as current"""
        model = SemanticModel(name=name)
        if description:
            model.custom_instructions.append(CustomInstruction(instruction_text=description))
        self.models.append(model)
        self.current_model = model
        return self

    def add_table(
        self,
        name: str,
        database: str,
        schema: str,
        table: str,
        description: str | None = None,
        primary_key: list[str] | None = None,
    ) -> "SemanticModelBuilder":
        """Add a logical table to the current model"""
        if not self.current_model:
            raise NoCurrentModelError()

        base_table = BaseTable(database=database, schema=schema, table=table)
        pk = Columns(names=primary_key or [])
        logical_table = LogicalTable(name=name, description=description, base_table=base_table, primary_key=pk)
        self.current_model.add_table(logical_table)
        return self

    def add_dimension(
        self,
        table_name: str,
        name: str,
        data_type: str | None = None,
        description: str | None = None,
        expr: str | None = None,
        unique: bool = False,
        synonyms: list[str] | None = None,
    ) -> "SemanticModelBuilder":
        """Add a dimension to a specific table"""
        if not self.current_model:
            raise NoCurrentModelError()

        table = next((t for t in self.current_model.logical_tables if t.name == table_name), None)
        if not table:
            raise TableNotFoundError()

        dimension = Dimension(
            name=name, data_type=data_type, description=description, expr=expr, unique=unique, synonyms=synonyms or []
        )
        table.dimensions.append(dimension)
        return self

    def add_relationship(
        self,
        name: str,
        left_table: str,
        right_table: str,
        left_column: str,
        right_column: str,
        relationship_type: str = "MANY_TO_ONE",
        join_type: str = "INNER",
    ) -> "SemanticModelBuilder":
        """Add a relationship between tables"""
        if not self.current_model:
            raise NoCurrentModelError()

        rel_col = RelationshipColumn(left_column=left_column, right_column=right_column)
        relationship = Relationship(
            name=name,
            left_table=left_table,
            right_table=right_table,
            relationship_columns=[rel_col],
            relationship_type=relationship_type,
            join_type=join_type,
        )
        self.current_model.add_relationship(relationship)
        return self

    def add_metric(self, name: str, expr: str, description: str | None = None) -> "SemanticModelBuilder":
        """Add a metric to the current model"""
        if not self.current_model:
            raise NoCurrentModelError()

        metric = Metric(name=name, expr=expr, description=description)
        self.current_model.add_metric(metric)
        return self

    def add_verified_query(
        self, name: str, question: str, sql: str, verified_by: str | None = None, onboarding: bool = False
    ) -> "SemanticModelBuilder":
        """Add a verified query to the current model"""
        if not self.current_model:
            raise NoCurrentModelError()

        query = VerifiedQuery(
            name=name, question=question, sql=sql, verified_by=verified_by, use_as_onboarding_question=onboarding
        )
        self.current_model.verified_queries.append(query)
        return self

    def build(self) -> SemanticModel:
        """Return the current model and reset builder"""
        if not self.current_model:
            raise NoCurrentModelError()

        model = self.current_model
        self.current_model = None
        return model

    def get_model(self, name: str) -> SemanticModel | None:
        """Get a model by name"""
        return next((m for m in self.models if m.name == name), None)

    def get_models(self) -> list[SemanticModel]:
        """Get all models"""
        return self.models

    def load_from_yaml(self, yaml_path: str) -> "SemanticModelBuilder":
        """Load a model from YAML and add to builder"""
        model = SemanticModel.from_yaml(yaml_path)
        self.models.append(model)
        self.current_model = model
        return self

    def export_current_to_yaml(self, yaml_path: str) -> "SemanticModelBuilder":
        """Export current model to YAML"""
        if not self.current_model:
            raise NoCurrentModelError()

        self.current_model.to_yaml(yaml_path)
        return self

    def validate_current_model(self) -> dict[str, any]:
        """Validate the current model and return validation results"""
        if not self.current_model:
            raise NoCurrentModelError()

        issues = []
        warnings = []

        # Check for tables without dimensions
        for table in self.current_model.logical_tables:
            if not table.dimensions:
                warnings.append(f"Table {table.name} has no dimensions")
            if not table.primary_key.names:
                warnings.append(f"Table {table.name} has no primary key")

        # Check for orphaned relationships
        table_names = {t.name for t in self.current_model.logical_tables}
        for rel in self.current_model.relationships:
            if rel.left_table not in table_names:
                issues.append(f"Relationship {rel.name} references unknown left table: {rel.left_table}")
            if rel.right_table not in table_names:
                issues.append(f"Relationship {rel.name} references unknown right table: {rel.right_table}")

        # Check for metrics without expressions
        for metric in self.current_model.metrics:
            if not metric.expr:
                issues.append(f"Metric {metric.name} has no expression")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "tables": len(self.current_model.logical_tables),
            "relationships": len(self.current_model.relationships),
            "metrics": len(self.current_model.metrics),
        }
