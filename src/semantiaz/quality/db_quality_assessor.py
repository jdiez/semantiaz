"""Database quality assessment for semantic layer readiness.

This module provides comprehensive quality assessment capabilities for relational databases
to determine readiness for semantic layer implementation. It evaluates both schema
structure and data content quality across multiple dimensions.
"""

import logging
from dataclasses import dataclass


@dataclass
class QualityMetric:
    """Individual quality metric with score and diagnostic information.

    Attributes:
        name: Human-readable name of the quality metric.
        score: Quality score from 0-100, where 100 is perfect quality.
        details: Detailed description of the metric assessment.
        issues: List of specific issues found during assessment.
    """

    name: str
    score: float  # 0-100
    details: str
    issues: list[str]


@dataclass
class QualityReport:
    """Comprehensive quality assessment report.

    Attributes:
        overall_score: Overall quality score (0-100) combining schema and content.
        schema_score: Schema-specific quality score (0-100).
        content_score: Content-specific quality score (0-100).
        metrics: List of individual quality metrics assessed.
        recommendations: List of actionable recommendations for improvement.
    """

    overall_score: float
    schema_score: float
    content_score: float
    metrics: list[QualityMetric]
    recommendations: list[str]


class DatabaseQualityAssessor:
    """Assess database schema and content quality for semantic layer readiness.

    This class provides comprehensive quality assessment capabilities for relational
    databases, evaluating both structural (schema) and content quality dimensions
    to determine readiness for semantic layer implementation.
    """

    def __init__(self, connection: object, neutral_score: int = 50, sample_size: int = 1000):
        """Initialize the quality assessor with a database connection.

        Args:
            connection: Ibis database connection object for accessing the database.
            neutral_score: Default neutral score for metrics that cannot be assessed.
            sample_size: Number of rows to sample per table for content analysis.
        """
        self.connection = connection
        self.neutral_score = neutral_score
        self.sample_size = sample_size  # Default sample size for content analysis

    def assess_quality(self, schema: str | None = None, sample_size: int = 1000) -> QualityReport:
        """Perform comprehensive quality assessment of database.

        Evaluates both schema quality (structure, documentation, relationships) and
        content quality (null values, consistency, duplicates) to generate an overall
        readiness score for semantic layer implementation.

        Args:
            schema: Optional schema name to limit assessment scope.
            sample_size: Number of rows to sample per table for content analysis.

        Returns:
            QualityReport containing overall scores, individual metrics, and recommendations.
        """
        metrics = []

        # Schema quality metrics
        metrics.append(self._assess_table_documentation())
        metrics.append(self._assess_column_documentation())
        metrics.append(self._assess_primary_keys())
        metrics.append(self._assess_foreign_keys())
        metrics.append(self._assess_data_types())

        # Content quality metrics
        metrics.append(self._assess_null_values(sample_size))
        metrics.append(self._assess_data_consistency(sample_size))
        metrics.append(self._assess_duplicate_records(sample_size))

        # Calculate scores
        schema_metrics = metrics[:5]
        content_metrics = metrics[5:]

        schema_score = sum(m.score for m in schema_metrics) / len(schema_metrics)
        content_score = sum(m.score for m in content_metrics) / len(content_metrics)
        overall_score = (schema_score + content_score) / 2

        recommendations = self._generate_recommendations(metrics)

        return QualityReport(
            overall_score=overall_score,
            schema_score=schema_score,
            content_score=content_score,
            metrics=metrics,
            recommendations=recommendations,
        )

    def _assess_table_documentation(self, score: int = 50) -> QualityMetric:
        """Assess quality of table-level documentation.

        Evaluates presence and quality of table comments/descriptions.
        Note: Generic ibis interface cannot access table comments, so this
        returns a neutral score with appropriate warnings.
        Args:
            score: Default score to assign since documentation cannot be assessed.
        Returns:
            QualityMetric with documentation coverage assessment.
        """
        _ = self.connection.list_tables()

        # Most databases don't expose table comments via ibis

        return QualityMetric(
            name="Table Documentation",
            score=score,
            details="Documentation assessment requires database-specific queries",
            issues=["Cannot assess table documentation via generic interface"],
        )

    def _assess_column_documentation(self, score: int = 50) -> QualityMetric:
        """Assess quality of column-level documentation.

        Evaluates presence and quality of column comments/descriptions.
        Note: Generic ibis interface cannot access column comments, so this
        returns a neutral score with column count information.
        Args:
            score: Default score to assign since documentation cannot be assessed.

        Returns:
            QualityMetric with column documentation assessment.
        """
        tables = self.connection.list_tables()
        total_columns = 0

        for table_name in tables:
            try:
                table = self.connection.table(table_name)

            except Exception as e:
                logging.warning(f"Failed to access table {table_name}: {e}")
                continue
            else:
                total_columns += len(table.schema())

        return QualityMetric(
            name="Column Documentation",
            score=score,
            details=f"Found {total_columns} columns across {len(tables)} tables",
            issues=["Cannot assess column documentation via generic interface"],
        )

    def _assess_primary_keys(self) -> QualityMetric:
        """Assess primary key coverage across tables.

        Evaluates what percentage of tables have identifiable primary keys
        by looking for columns with 'id' in the name. This is a heuristic
        approach since constraint information isn't available via ibis.

        Returns:
            QualityMetric with primary key coverage assessment.
        """
        tables = self.connection.list_tables()
        tables_with_pk = 0
        issues = []

        for table_name in tables:
            try:
                table = self.connection.table(table_name)
                columns = list(table.schema().keys())
                if any("id" in col.lower() for col in columns):
                    tables_with_pk += 1
                else:
                    issues.append(f"Table {table_name} may lack primary key")
            except Exception:
                continue

        score = (tables_with_pk / len(tables)) * 100 if tables else 0

        return QualityMetric(
            name="Primary Key Coverage",
            score=score,
            details=f"{tables_with_pk}/{len(tables)} tables have identifiable primary keys",
            issues=issues,
        )

    def _assess_foreign_keys(self) -> QualityMetric:
        """Assess foreign key relationship coverage.

        Evaluates potential foreign key relationships by identifying columns
        that end with '_id' pattern, which typically indicates foreign keys
        in well-designed schemas.

        Returns:
            QualityMetric with foreign key relationship assessment.
        """
        tables = self.connection.list_tables()
        potential_fks = 0

        for table_name in tables:
            try:
                table = self.connection.table(table_name)
                columns = list(table.schema().keys())
                fk_candidates = [col for col in columns if col.endswith("_id") and col != "id"]
                potential_fks += len(fk_candidates)
            except Exception:
                continue

        score = min(potential_fks * 10, 100)

        return QualityMetric(
            name="Foreign Key Relationships",
            score=score,
            details=f"{potential_fks} potential foreign key columns found",
            issues=(["No foreign key relationships detected"] if potential_fks == 0 else []),
        )

    def _assess_data_types(self) -> QualityMetric:
        """Assess appropriateness of column data types.

        Evaluates whether column data types are semantically appropriate
        based on column names and type patterns (e.g., date columns should
        have date types, ID columns should be integers).

        Returns:
            QualityMetric with data type appropriateness assessment.
        """
        tables = self.connection.list_tables()
        total_columns = 0
        appropriate_types = 0
        issues = []

        for table_name in tables:
            try:
                table = self.connection.table(table_name)
                for col_name, col_type in table.schema().items():
                    total_columns += 1
                    type_str = str(col_type).lower()

                    if (
                        ("date" in col_name.lower() and "date" in type_str)
                        or ("id" in col_name.lower() and "int" in type_str)
                        or "string" in type_str
                        or "varchar" in type_str
                    ):
                        appropriate_types += 1
                    else:
                        issues.append(f"{table_name}.{col_name}: {col_type}")
            except Exception:
                continue

        score = (appropriate_types / total_columns) * 100 if total_columns else 0

        return QualityMetric(
            name="Data Type Appropriateness",
            score=score,
            details=f"{appropriate_types}/{total_columns} columns have appropriate types",
            issues=issues[:5],  # Limit issues shown
        )

    def _assess_null_values(self, sample_size: int) -> QualityMetric:
        """Assess null value patterns in data content.

        Analyzes actual data to identify columns with high null percentages,
        which can indicate data quality issues or incomplete data collection.

        Args:
            sample_size: Number of rows to sample per table for analysis.

        Returns:
            QualityMetric with null value quality assessment.
        """
        tables = self.connection.list_tables()
        total_columns = 0
        high_null_columns = 0
        issues = []

        for table_name in tables:
            try:
                table = self.connection.table(table_name).limit(sample_size)
                data = table.execute()

                for col in data.columns:
                    total_columns += 1
                    null_pct = (data[col].isnull().sum() / len(data)) * 100

                    if null_pct > 50:
                        high_null_columns += 1
                        issues.append(f"{table_name}.{col}: {null_pct:.1f}% null")
            except Exception:
                continue

        score = max(0, 100 - (high_null_columns / total_columns * 100)) if total_columns else 0

        return QualityMetric(
            name="Null Value Quality",
            score=score,
            details=f"{high_null_columns}/{total_columns} columns have >50% null values",
            issues=issues[:5],
        )

    def _assess_data_consistency(self, sample_size: int) -> QualityMetric:
        """Assess data consistency patterns in text columns.

        Analyzes text columns for formatting inconsistencies such as mixed
        case patterns, which can indicate data entry issues or lack of
        standardization.

        Args:
            sample_size: Number of rows to sample per table for analysis.

        Returns:
            QualityMetric with data consistency assessment.
        """
        tables = self.connection.list_tables()
        inconsistent_columns = 0
        total_text_columns = 0
        issues = []

        for table_name in tables:
            try:
                table = self.connection.table(table_name).limit(sample_size)
                data = table.execute()

                for col in data.columns:
                    if data[col].dtype == "object":
                        total_text_columns += 1
                        unique_values = data[col].dropna().unique()

                        if len(unique_values) > 1:
                            has_upper = any(str(v).isupper() for v in unique_values[:10] if str(v).isalpha())
                            has_lower = any(str(v).islower() for v in unique_values[:10] if str(v).isalpha())

                            if has_upper and has_lower:
                                inconsistent_columns += 1
                                issues.append(f"{table_name}.{col}: mixed case formatting")
            except Exception:
                continue

        score = max(0, 100 - (inconsistent_columns / total_text_columns * 100)) if total_text_columns else 100

        return QualityMetric(
            name="Data Consistency",
            score=score,
            details=f"{inconsistent_columns}/{total_text_columns} text columns have formatting issues",
            issues=issues[:5],
        )

    def _assess_duplicate_records(self, sample_size: int) -> QualityMetric:
        """Assess presence of duplicate records in tables.

        Identifies tables containing duplicate rows, which can indicate
        data quality issues or missing unique constraints.

        Args:
            sample_size: Number of rows to sample per table for analysis.

        Returns:
            QualityMetric with duplicate record assessment.
        """
        tables = self.connection.list_tables()
        tables_with_duplicates = 0
        issues = []

        for table_name in tables:
            try:
                table = self.connection.table(table_name).limit(sample_size)
                data = table.execute()

                duplicates = data.duplicated().sum()
                if duplicates > 0:
                    tables_with_duplicates += 1
                    dup_pct = (duplicates / len(data)) * 100
                    issues.append(f"{table_name}: {duplicates} duplicates ({dup_pct:.1f}%)")
            except Exception:
                continue

        score = max(0, 100 - (tables_with_duplicates / len(tables) * 100)) if tables else 100

        return QualityMetric(
            name="Duplicate Records",
            score=score,
            details=f"{tables_with_duplicates}/{len(tables)} tables have duplicate records",
            issues=issues[:5],
        )

    def _generate_recommendations(self, metrics: list[QualityMetric]) -> list[str]:
        """Generate actionable recommendations based on quality metrics.

        Analyzes quality metric scores to generate specific, actionable
        recommendations for improving database quality before implementing
        a semantic layer.

        Args:
            metrics: List of quality metrics from assessment.

        Returns:
            List of actionable recommendation strings.
        """
        recommendations = []

        for metric in metrics:
            if metric.score < 70:
                if metric.name == "Primary Key Coverage":
                    recommendations.append("Define primary keys for all tables")
                elif metric.name == "Foreign Key Relationships":
                    recommendations.append("Establish foreign key relationships between tables")
                elif metric.name == "Null Value Quality":
                    recommendations.append("Address columns with high null percentages")
                elif metric.name == "Data Consistency":
                    recommendations.append("Standardize data formatting across columns")
                elif metric.name == "Duplicate Records":
                    recommendations.append("Remove duplicate records and add uniqueness constraints")

        return recommendations
