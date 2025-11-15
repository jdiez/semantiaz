"""Tests for dashboard generator module."""

import json

import pytest

from semantiaz.quality.dashboard_generator import QualityDashboardGenerator
from semantiaz.quality.db_quality_assessor import QualityMetric, QualityReport


class TestQualityDashboardGenerator:
    """Test cases for QualityDashboardGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create QualityDashboardGenerator instance."""
        return QualityDashboardGenerator()

    @pytest.fixture
    def sample_report(self):
        """Create sample quality report for testing."""
        metrics = [
            QualityMetric("Table Documentation", 85, ["Missing docs for table1"]),
            QualityMetric("Column Documentation", 70, ["Missing docs for col1", "Missing docs for col2"]),
            QualityMetric("Primary Keys", 90, []),
            QualityMetric("Foreign Keys", 60, ["Missing FK in table2"]),
            QualityMetric("Data Types", 80, ["Inconsistent types"]),
            QualityMetric("Null Patterns", 75, ["High nulls in col3"]),
            QualityMetric("Data Consistency", 85, []),
            QualityMetric("Duplicates", 95, []),
        ]

        return QualityReport(
            overall_score=80.0,
            schema_score=78.75,
            content_score=81.25,
            metrics=metrics,
            readiness_level="Minor Improvements Needed",
        )

    def test_generate_plotly_dashboard(self, generator, sample_report):
        """Test Plotly dashboard generation."""
        html_content = generator.generate_plotly_dashboard(sample_report)

        assert isinstance(html_content, str)
        assert "plotly" in html_content.lower()
        assert "database quality assessment dashboard" in html_content.lower()
        assert "html" in html_content.lower()

    def test_generate_vega_dashboard(self, generator, sample_report):
        """Test Vega-Lite dashboard generation."""
        vega_spec = generator.generate_vega_dashboard(sample_report)

        assert isinstance(vega_spec, str)

        # Parse JSON to validate structure
        spec = json.loads(vega_spec)
        assert "$schema" in spec
        assert "vega-lite" in spec["$schema"]
        assert "title" in spec
        assert "data" in spec
        assert "vconcat" in spec

    def test_get_color_mapping(self, generator):
        """Test color mapping based on scores."""
        assert generator._get_color(85) == "green"
        assert generator._get_color(70) == "orange"
        assert generator._get_color(45) == "red"

    def test_get_readiness_score(self, generator):
        """Test readiness score calculation."""
        assert generator._get_readiness_score(85) == 3  # Ready
        assert generator._get_readiness_score(70) == 2  # Minor improvements
        assert generator._get_readiness_score(45) == 1  # Major improvements

    def test_get_readiness_color(self, generator):
        """Test readiness color mapping."""
        assert generator._get_readiness_color(3) == "green"
        assert generator._get_readiness_color(2) == "orange"
        assert generator._get_readiness_color(1) == "red"
        assert generator._get_readiness_color(0) == "gray"

    def test_vega_spec_structure(self, generator, sample_report):
        """Test Vega-Lite specification structure."""
        vega_spec = generator.generate_vega_dashboard(sample_report)
        spec = json.loads(vega_spec)

        # Check main structure
        assert "vconcat" in spec
        assert len(spec["vconcat"]) == 2

        # Check first row (hconcat)
        first_row = spec["vconcat"][0]
        assert "hconcat" in first_row
        assert len(first_row["hconcat"]) == 2

        # Check second row (hconcat)
        second_row = spec["vconcat"][1]
        assert "hconcat" in second_row
        assert len(second_row["hconcat"]) == 2

    def test_dashboard_with_empty_metrics(self, generator):
        """Test dashboard generation with empty metrics."""
        empty_report = QualityReport(
            overall_score=0.0,
            schema_score=0.0,
            content_score=0.0,
            metrics=[],
            readiness_level="Major Improvements Needed",
        )

        html_content = generator.generate_plotly_dashboard(empty_report)
        vega_spec = generator.generate_vega_dashboard(empty_report)

        assert isinstance(html_content, str)
        assert isinstance(vega_spec, str)

        # Should still be valid JSON
        spec = json.loads(vega_spec)
        assert "$schema" in spec
