"""Tests for database quality assessor module."""

from unittest.mock import Mock, patch

import pytest

from semantiaz.quality.db_quality_assessor import DatabaseQualityAssessor, QualityMetric, QualityReport


class TestDatabaseQualityAssessor:
    """Test cases for DatabaseQualityAssessor class."""

    @pytest.fixture
    def mock_connection(self):
        """Mock database connection."""
        conn = Mock()
        conn.list_tables.return_value = ["customers", "orders"]
        return conn

    @pytest.fixture
    def assessor(self, mock_connection):
        """Create DatabaseQualityAssessor instance."""
        return DatabaseQualityAssessor(mock_connection)

    def test_assess_table_documentation(self, assessor, mock_connection):
        """Test table documentation assessment."""
        # Mock table with schema
        mock_table = Mock()
        mock_table.schema.return_value.items.return_value = [("id", "int64"), ("name", "string")]
        mock_connection.table.return_value = mock_table

        metric = assessor._assess_table_documentation(["customers", "orders"])

        assert isinstance(metric, QualityMetric)
        assert metric.name == "Table Documentation Coverage"
        assert 0 <= metric.score <= 100

    def test_assess_column_documentation(self, assessor, mock_connection):
        """Test column documentation assessment."""
        mock_table = Mock()
        mock_table.schema.return_value.items.return_value = [("id", "int64"), ("name", "string"), ("email", "string")]
        mock_connection.table.return_value = mock_table

        metric = assessor._assess_column_documentation(["customers"])

        assert isinstance(metric, QualityMetric)
        assert metric.name == "Column Documentation Coverage"
        assert 0 <= metric.score <= 100

    def test_assess_primary_keys(self, assessor):
        """Test primary key assessment."""
        metric = assessor._assess_primary_keys(["customers", "orders"])

        assert isinstance(metric, QualityMetric)
        assert metric.name == "Primary Key Coverage"
        assert metric.score == 0  # No primary keys detected in mock

    def test_assess_data_types(self, assessor, mock_connection):
        """Test data type assessment."""
        mock_table = Mock()
        mock_table.schema.return_value.items.return_value = [("id", "int64"), ("name", "string"), ("amount", "float64")]
        mock_connection.table.return_value = mock_table

        metric = assessor._assess_data_types(["customers"])

        assert isinstance(metric, QualityMetric)
        assert metric.name == "Data Type Appropriateness"
        assert 0 <= metric.score <= 100

    def test_assess_null_patterns(self, assessor, mock_connection):
        """Test null pattern assessment."""
        import pandas as pd

        # Mock table data with nulls
        mock_table = Mock()
        mock_table.to_pandas.return_value = pd.DataFrame({"id": [1, 2, 3, None], "name": ["A", "B", None, "D"]})
        mock_connection.table.return_value = mock_table

        metric = assessor._assess_null_patterns(["customers"])

        assert isinstance(metric, QualityMetric)
        assert metric.name == "Null Value Patterns"
        assert 0 <= metric.score <= 100

    def test_generate_report(self, assessor):
        """Test quality report generation."""
        with (
            patch.object(assessor, "_assess_table_documentation") as mock_table_doc,
            patch.object(assessor, "_assess_column_documentation") as mock_col_doc,
            patch.object(assessor, "_assess_primary_keys") as mock_pk,
            patch.object(assessor, "_assess_foreign_keys") as mock_fk,
            patch.object(assessor, "_assess_data_types") as mock_dt,
            patch.object(assessor, "_assess_null_patterns") as mock_null,
            patch.object(assessor, "_assess_data_consistency") as mock_consistency,
            patch.object(assessor, "_assess_duplicate_records") as mock_duplicates,
        ):
            # Mock all assessment methods
            mock_table_doc.return_value = QualityMetric("Table Doc", 80, [])
            mock_col_doc.return_value = QualityMetric("Column Doc", 70, [])
            mock_pk.return_value = QualityMetric("Primary Keys", 90, [])
            mock_fk.return_value = QualityMetric("Foreign Keys", 60, [])
            mock_dt.return_value = QualityMetric("Data Types", 85, [])
            mock_null.return_value = QualityMetric("Null Patterns", 75, [])
            mock_consistency.return_value = QualityMetric("Consistency", 80, [])
            mock_duplicates.return_value = QualityMetric("Duplicates", 95, [])

            report = assessor.generate_report()

            assert isinstance(report, QualityReport)
            assert len(report.metrics) == 8
            assert 0 <= report.overall_score <= 100
            assert 0 <= report.schema_score <= 100
            assert 0 <= report.content_score <= 100

    def test_quality_metric_creation(self):
        """Test QualityMetric creation."""
        metric = QualityMetric(name="Test Metric", score=85.5, issues=["Issue 1", "Issue 2"])

        assert metric.name == "Test Metric"
        assert metric.score == 85.5
        assert len(metric.issues) == 2
