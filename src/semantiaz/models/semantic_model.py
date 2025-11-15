"""Framework to build Snowflake Cortex Semantic Models"""

import json
from datetime import datetime
from typing import Annotated, Literal

import sqlglot
import yaml
from pydantic import BaseModel, Field, field_validator


class SemanticModelError(Exception):
    """Base exception for semantic model operations"""

    def __init__(self, message: str) -> None:
        """Initialize SemanticModelError with a message"""
        super().__init__(f"Semantic Model Error: {message}")


class NoCurrentModelError(SemanticModelError):
    """Raised when no current model is available"""

    def __init__(self) -> None:
        """Initialize NoCurrentModelError with a default message"""
        super().__init__("No current semantic model is set in the builder")


class TableNotFoundError(SemanticModelError):
    """Raised when a table is not found"""

    def __init__(self) -> None:
        """Initialize TableNotFoundError with a default message"""
        super().__init__("Table not found in the current semantic model")


class VerifiedQueryError(SemanticModelError):
    """Raised when there is an error with a verified query"""

    def __init__(self, message: str) -> None:
        """Initialize VerifiedQueryError with a message"""
        super().__init__(f"Verified Query Error: {message}")


class SQLValidationError(SemanticModelError):
    """Raised when SQL validation fails"""

    def __init__(self, message: str) -> None:
        """Initialize SQLValidationError with a message"""
        super().__init__(f"SQL Validation Error: {message}")


class CortexSearchService(BaseModel):
    """Configuration for Cortex Search Service integration"""

    service: Annotated[str | None, Field(default=None, description="Search service name")]
    literal_column: Annotated[str | None, Field(default=None, description="Literal column for search")]
    database: Annotated[str | None, Field(default=None, description="Database for search service")]
    schema: Annotated[str | None, Field(default=None, description="Schema for search service")]


class Dimension(BaseModel):
    """A dimension represents categorical data that provides context to Facts, such as product, customer, or location information.
    Dimensions typically contain descriptive text values, such as product names or customer addresses.
    They are used to filter, group, and label Facts in analyses and reports."""

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


class TimeDimensions(BaseModel):
    """A time dimension provides temporal context for analyzing Facts across different periods.
    It enables tracking metrics over specific time intervals (dates, months, years) and
    supports analyses such as trend identification and period-over-period comparisons."""

    name: Annotated[str, Field(description="The name of the time dimension")]
    synonyms: Annotated[list[str], Field(default=[], description="Alternative names for the time dimension")]
    description: Annotated[str | None, Field(default=None, description="A description of the time dimension")]
    expr: Annotated[str | None, Field(default=None, description="SQL expression defining the time dimension")]
    data_type: Annotated[int | float | None, Field(default=None, description="The data type of the time dimension")]
    unique: Annotated[bool, Field(default=False, description="Whether the time dimension values are unique")]


class Fact(BaseModel):
    """Fact are measurable, quantitative data that provide context for analyses.
    Fact represent numeric values related to business processes, such as sales, cost, or quantity.
    A Fact is an unaggregated, row-level concept."""

    name: Annotated[str, Field(description="The name of the Facts")]
    synonyms: Annotated[list[str], Field(default=[], description="Alternative names for the Facts")]
    description: Annotated[str | None, Field(default=None, description="A description of what the Facts represents")]
    access_modifier: Annotated[
        Literal["public_access", "private_access"],
        Field(default="public_access", description="Access level for the Facts"),
    ]
    expr: Annotated[str | None, Field(default=None, description="SQL expression defining the Facts")]
    data_type: Annotated[str | None, Field(default=None, description="The data type of the Facts")]


class Metric(BaseModel):
    """A metric is a quantifiable measure of business performance expressed as a SQL formula.
    You can use metrics as key performance indicators (KPIs) in reports and dashboards.
    You can calculate two kinds of metrics:
        - Regular metrics aggregate values (using functions such as SUM or AVG) over a Facts column.
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

    @field_validator("verified_at", mode="before")
    @classmethod
    def validate_verified_at(cls, v) -> int:
        """Validate that verified_at is an integer timestamp"""
        match v:
            case int():
                try:
                    datetime.fromtimestamp(v)
                except Exception as e:
                    raise VerifiedQueryError(message=str(e)) from e
                return v
            case str() if v.isdigit():
                return int(v)
            case _:
                raise VerifiedQueryError(message="bad_type_for_verified_at") from None

    @field_validator("sql", mode="after")
    def validate_sql(cls, v: str) -> str:
        """Validate that sql is a non-empty string
        Arguments:
            v: The SQL string to validate
        Returns:
            The validated SQL string
        Raises:
            VerifiedQueryError: If the SQL string is empty or invalid
        """
        if v is None or not v.strip():
            raise VerifiedQueryError(message="sql_cannot_be_empty") from None
        try:
            sqlglot.parse_one(v)
        except sqlglot.errors.ParseError as e:
            raise VerifiedQueryError(message=f"invalid_SQL: {e}!s") from e
        return v


class ModuleCustomInstructions(BaseModel):
    """Custom instructions provide additional context or guidelines for using the semantic model.
    They can help tailor the behavior of AI systems or other tools that interact with the model."""

    sql_generation: Annotated[list[str] | None, Field(description="Custom instruction text for the semantic model")]
    question_categorization: Annotated[
        list[str] | None,
        Field(
            description="You can use the question_categorization component to block questions about specific topics."
            "For example, if you want to block questions about users, you might set the following instructions. "
            "You can also use question categorization instructions to ask for missing details."
            "In the following example, Cortex Analyst asks the user to provide a product type "
            "if they ask about users and do not specify one."
        ),
    ]


class Columns(BaseModel):
    """A collection of column names used for primary keys or other purposes.
    This class is used to define the structure of primary keys in logical tables."""

    columns: Annotated[list[str], Field(default=[], description="List of column names")]


class BaseTable(BaseModel):
    """A base table represents a physical table in the database that underlies a logical table in the semantic model.
    It contains metadata about the table's location and structure."""

    database: Annotated[str | None, Field(default=None, description="Database name containing the table")]
    schema: Annotated[str | None, Field(default=None, description="Schema name containing the table")]
    table: Annotated[str | None, Field(default=None, description="Table name")]


class Table(BaseModel):
    """A logical table represents a conceptual table in the semantic model.
    It may map to one or more physical tables in the database and contains dimensions that define its structure."""

    name: Annotated[str, Field(description="The name of the logical table")]
    description: Annotated[str | None, Field(default=None, description="A description of the logical table")]
    base_table: Annotated[BaseTable | None, Field(default=None, description="The underlying physical table")]
    primary_key: Annotated[Columns | None, Field(default=None, description="Primary key columns for this table")]
    dimensions: Annotated[list[Dimension], Field(default=[], description="List of dimensions in this table")]
    time_dimensions: Annotated[
        list[TimeDimensions] | None, Field(default=None, description="List of time dimensions in this table")
    ]
    facts: Annotated[list[Fact] | None, Field(default=None, description="List of Facts in this table")]
    metrics: Annotated[list[Metric] | None, Field(default=None, description="List of metrics scoped to this table")]
    filters: Annotated[list[Filter] | None, Field(default=None, description="List of filters for this table")]


class SemanticModel(BaseModel):
    """A semantic model defines a business-oriented representation of data for analysis and reporting.
    It includes logical tables, relationships, dimensions, and metrics that provide a unified view of the underlying data sources."""

    name: Annotated[
        str,
        Field(
            description="A descriptive name for this semantic model."
            "Must be unique and follow the unquoted identifiers requirements."
            "It also cannot conflict with Snowflake reserved keywords."
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            default=None,
            description="A description of this semantic model, including details of what kind of analysis it’s useful for.",
        ),
    ]
    comments: Annotated[str | None, Field(default=None, description="Additional comments about the semantic model")]
    tables: Annotated[list[Table], Field(default=[], description="List of logical tables in the semantic model")]
    relationships: Annotated[list[Relationship], Field(default=[], description="List of relationships between tables")]
    metrics: Annotated[list[Metric], Field(default=[], description="List of metrics scoped to the semantic model")]
    verified_queries: Annotated[
        list[VerifiedQuery], Field(default=[], description="List of verified queries for the model")
    ]
    custom_instructions: Annotated[
        ModuleCustomInstructions | None,
        Field(
            default=None,
            description="Define logic that influences how user questions are interpreted before SQL is generated"
            "Maintain separate, more structured instructions for different parts of the Analyst workflow."
            "Using natural language, you can tell AI Agents exactly how to generate SQL queries from within your semantic model YAML file."
            "For example, use custom instructions to tell Agent Analyst what you mean by performance or financial year."
            "In this way, you can improve the accuracy of the generated SQL by incorporating custom logic or additional elements.",
        ),
    ]

    def add_table(self, table: Table) -> None:
        """Add a logical table to the semantic model"""
        # Check if the table already exists
        for existing_table in self.tables:
            if existing_table.name == table.name:
                return
        self.tables.append(table)

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
        return cls.model_validate(data)

    @classmethod
    def from_yaml_string(cls, yaml_string: str) -> "SemanticModel":
        """Load semantic model from YAML string"""
        data = yaml.safe_load(yaml_string)
        return cls.model_validate(data)

    def to_yaml(self, yaml_path: str | None = None) -> str:
        """Export semantic model to YAML format"""
        data = self.model_dump(exclude_none=True)
        yaml_content = yaml.dump(data, default_flow_style=False, sort_keys=False)
        if yaml_path:
            with open(yaml_path, "w") as f:
                f.write(yaml_content)
        return yaml_content

    def to_json(self, json_path: str | None = None) -> str:
        """Export semantic model to JSON format"""
        json_content = json.dumps(self.model_dump(exclude_none=True), indent=2)
        if json_path:
            with open(json_path, "w") as f:
                f.write(json_content)
        return json_content

    def get_table(self, name: str) -> Table | None:
        """Get a table by name"""
        return next((t for t in self.tables if t.name == name), None)

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
        model = SemanticModel(name=name, description=description)
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
        pk = Columns(columns=primary_key or [])
        logical_table = Table(name=name, description=description, base_table=base_table, primary_key=pk)
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

        table = next((t for t in self.current_model.tables if t.name == table_name), None)
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
        for table in self.current_model.tables:
            if not table.dimensions:
                warnings.append(f"Table {table.name} has no dimensions")
            if table.primary_key and not table.primary_key.columns:
                warnings.append(f"Table {table.name} has no primary key")

        # Check for orphaned relationships
        table_names = {t.name for t in self.current_model.tables}
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
            "tables": len(self.current_model.tables),
            "relationships": len(self.current_model.relationships),
            "metrics": len(self.current_model.metrics),
        }
