"""Generate interactive dashboards from database quality metrics.

This module provides capabilities to create interactive visualizations of database
quality assessment results using Plotly and Vega-Lite. The dashboards help users
understand quality metrics, identify issues, and assess readiness for semantic
layer implementation.
"""

import json

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .db_quality_assessor import QualityReport


class QualityDashboardGenerator:
    """Generate interactive dashboards from quality assessment results.

    This class creates comprehensive visual dashboards that display database quality
    metrics in an interactive format, supporting both Plotly (HTML) and Vega-Lite
    (JSON specification) output formats.
    """

    def generate_plotly_dashboard(self, report: QualityReport) -> str:
        """Generate interactive HTML dashboard using Plotly.

        Creates a comprehensive dashboard with multiple visualizations including
        gauge charts, bar charts, pie charts, scatter plots, and histograms to
        display quality metrics and readiness assessment.

        Args:
            report: QualityReport containing assessment results and metrics.

        Returns:
            Complete HTML string with embedded Plotly dashboard.
        """

        # Create subplots
        fig = make_subplots(
            rows=3,
            cols=2,
            subplot_titles=(
                "Overall Scores",
                "Quality Metrics",
                "Schema vs Content",
                "Metric Details",
                "Score Distribution",
                "Readiness Status",
            ),
            specs=[
                [{"type": "indicator"}, {"type": "bar"}],
                [{"type": "pie"}, {"type": "scatter"}],
                [{"type": "histogram"}, {"type": "indicator"}],
            ],
        )

        # Overall score gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=report.overall_score,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Overall Quality Score"},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": self._get_color(report.overall_score)},
                    "steps": [
                        {"range": [0, 50], "color": "lightgray"},
                        {"range": [50, 80], "color": "yellow"},
                        {"range": [80, 100], "color": "lightgreen"},
                    ],
                    "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 70},
                },
            ),
            row=1,
            col=1,
        )

        # Quality metrics bar chart
        metric_names = [m.name for m in report.metrics]
        metric_scores = [m.score for m in report.metrics]
        colors = [self._get_color(score) for score in metric_scores]

        fig.add_trace(go.Bar(x=metric_names, y=metric_scores, marker_color=colors, name="Metric Scores"), row=1, col=2)

        # Schema vs Content pie chart
        fig.add_trace(
            go.Pie(
                labels=["Schema Quality", "Content Quality"],
                values=[report.schema_score, report.content_score],
                name="Quality Breakdown",
            ),
            row=2,
            col=1,
        )

        # Metric details scatter
        fig.add_trace(
            go.Scatter(
                x=list(range(len(report.metrics))),
                y=metric_scores,
                mode="markers+text",
                text=metric_names,
                textposition="top center",
                marker={"size": [score / 5 for score in metric_scores], "color": colors, "opacity": 0.7},
                name="Metrics Detail",
            ),
            row=2,
            col=2,
        )

        # Score distribution histogram
        fig.add_trace(go.Histogram(x=metric_scores, nbinsx=10, name="Score Distribution"), row=3, col=1)

        # Readiness indicator
        readiness_score = self._get_readiness_score(report.overall_score)
        fig.add_trace(
            go.Indicator(
                mode="number+gauge",
                value=readiness_score,
                title={"text": "Readiness Level"},
                gauge={
                    "axis": {"range": [0, 3]},
                    "bar": {"color": self._get_readiness_color(readiness_score)},
                    "steps": [
                        {"range": [0, 1], "color": "red"},
                        {"range": [1, 2], "color": "yellow"},
                        {"range": [2, 3], "color": "green"},
                    ],
                },
            ),
            row=3,
            col=2,
        )

        # Update layout
        fig.update_layout(height=800, title_text="Database Quality Assessment Dashboard", showlegend=False)

        return fig.to_html(include_plotlyjs=True)

    def generate_vega_dashboard(self, report: QualityReport) -> str:
        """Generate Vega-Lite dashboard specification.

        Creates a Vega-Lite specification for an interactive dashboard that can
        be rendered in web browsers or embedded in applications supporting
        Vega-Lite visualizations.

        Args:
            report: QualityReport containing assessment results and metrics.

        Returns:
            JSON string containing Vega-Lite specification.
        """

        # Prepare data
        metrics_data = [
            {"metric": m.name, "score": m.score, "category": "Schema" if i < 5 else "Content", "issues": len(m.issues)}
            for i, m in enumerate(report.metrics)
        ]

        vega_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "title": "Database Quality Assessment Dashboard",
            "data": {"values": metrics_data},
            "vconcat": [
                {
                    "hconcat": [
                        {
                            "title": "Overall Quality Score",
                            "mark": {"type": "arc", "innerRadius": 50},
                            "data": {
                                "values": [{"score": report.overall_score, "remaining": 100 - report.overall_score}]
                            },
                            "encoding": {
                                "theta": {"field": "score", "type": "quantitative"},
                                "color": {
                                    "field": "score",
                                    "type": "quantitative",
                                    "scale": {"range": ["red", "yellow", "green"]},
                                },
                            },
                        },
                        {
                            "title": "Quality Metrics",
                            "mark": "bar",
                            "encoding": {
                                "x": {"field": "metric", "type": "nominal", "axis": {"labelAngle": -45}},
                                "y": {"field": "score", "type": "quantitative"},
                                "color": {
                                    "field": "score",
                                    "type": "quantitative",
                                    "scale": {"range": ["red", "yellow", "green"]},
                                },
                            },
                        },
                    ]
                },
                {
                    "hconcat": [
                        {
                            "title": "Schema vs Content Quality",
                            "mark": "arc",
                            "data": {
                                "values": [
                                    {"category": "Schema", "score": report.schema_score},
                                    {"category": "Content", "score": report.content_score},
                                ]
                            },
                            "encoding": {
                                "theta": {"field": "score", "type": "quantitative"},
                                "color": {"field": "category", "type": "nominal"},
                            },
                        },
                        {
                            "title": "Issues by Metric",
                            "mark": "circle",
                            "encoding": {
                                "x": {"field": "score", "type": "quantitative"},
                                "y": {"field": "issues", "type": "quantitative"},
                                "size": {"field": "score", "type": "quantitative"},
                                "color": {"field": "category", "type": "nominal"},
                                "tooltip": ["metric", "score", "issues"],
                            },
                        },
                    ]
                },
            ],
        }

        return json.dumps(vega_spec, indent=2)

    def _get_color(self, score: float) -> str:
        """Get color code based on quality score.

        Args:
            score: Quality score from 0-100.

        Returns:
            Color string ('green', 'orange', or 'red') based on score thresholds.
        """
        if score >= 80:
            return "green"
        elif score >= 60:
            return "orange"
        else:
            return "red"

    def _get_readiness_score(self, overall_score: float) -> int:
        """Convert overall score to readiness level.

        Args:
            overall_score: Overall quality score from 0-100.

        Returns:
            Readiness level: 1 (major improvements), 2 (minor improvements), or 3 (ready).
        """
        if overall_score >= 80:
            return 3  # Ready
        elif overall_score >= 60:
            return 2  # Minor improvements
        else:
            return 1  # Major improvements

    def _get_readiness_color(self, readiness_score: int) -> str:
        """Get color code for readiness level.

        Args:
            readiness_score: Readiness level (1-3).

        Returns:
            Color string corresponding to readiness level.
        """
        colors = {1: "red", 2: "orange", 3: "green"}
        return colors.get(readiness_score, "gray")
