"""CLI for database quality assessment"""

import click

from ..quality.db_quality_assessor import DatabaseQualityAssessor


@click.command()
@click.option(
    "--backend",
    required=True,
    type=click.Choice(["postgres", "mysql", "sqlite", "duckdb", "bigquery", "snowflake"]),
    help="Database backend",
)
@click.option("--connection-string", help="Database connection string")
@click.option("--host", help="Database host")
@click.option("--port", type=int, help="Database port")
@click.option("--user", help="Database user")
@click.option("--password", help="Database password")
@click.option("--database", required=True, help="Database name")
@click.option("--schema", help="Schema name (optional)")
@click.option("--file-path", help="File path (for sqlite/duckdb)")
@click.option("--account", help="Snowflake account")
@click.option("--warehouse", help="Snowflake warehouse")
@click.option("--sample-size", default=1000, help="Sample size for content analysis")
@click.option("--output", help="Output report file (optional)")
@click.option("--dashboard", type=click.Choice(["plotly", "vega"]), help="Generate interactive dashboard")
@click.option("--dashboard-output", help="Dashboard output file")
def assess_quality(
    backend,
    connection_string,
    host,
    port,
    user,
    password,
    database,
    schema,
    file_path,
    account,
    warehouse,
    sample_size,
    output,
    dashboard,
    dashboard_output,
):
    """Assess database quality for semantic layer readiness"""

    try:
        # Create connection
        from ..utils.database_connections import create_database_connection

        conn = create_database_connection(
            backend=backend,
            database=database,
            connection_string=connection_string,
            host=host,
            port=port,
            user=user,
            password=password,
            file_path=file_path,
            schema=schema,
            account=account,
            warehouse=warehouse,
        )

        # Perform assessment
        click.echo("Assessing database quality...")
        assessor = DatabaseQualityAssessor(conn)
        report = assessor.assess_quality(schema, sample_size)

        # Display results
        click.echo("\n=== DATABASE QUALITY REPORT ===")
        click.echo(f"Overall Score: {report.overall_score:.1f}/100")
        click.echo(f"Schema Score: {report.schema_score:.1f}/100")
        click.echo(f"Content Score: {report.content_score:.1f}/100")

        click.echo("\n=== DETAILED METRICS ===")
        for metric in report.metrics:
            click.echo(f"\n{metric.name}: {metric.score:.1f}/100")
            click.echo(f"  {metric.details}")
            if metric.issues:
                click.echo("  Issues:")
                for issue in metric.issues[:3]:  # Show top 3 issues
                    click.echo(f"    - {issue}")

        click.echo("\n=== RECOMMENDATIONS ===")
        for i, rec in enumerate(report.recommendations, 1):
            click.echo(f"{i}. {rec}")

        # Generate dashboard if requested
        if dashboard:
            from ..quality.dashboard_generator import QualityDashboardGenerator

            generator = QualityDashboardGenerator()

            if dashboard == "plotly":
                dashboard_html = generator.generate_plotly_dashboard(report)
                dashboard_file = dashboard_output or "quality_dashboard.html"
                with open(dashboard_file, "w") as f:
                    f.write(dashboard_html)
                click.echo(f"Plotly dashboard saved to {dashboard_file}")

            elif dashboard == "vega":
                vega_spec = generator.generate_vega_dashboard(report)
                dashboard_file = dashboard_output or "quality_dashboard.json"
                with open(dashboard_file, "w") as f:
                    f.write(vega_spec)
                click.echo(f"Vega-Lite spec saved to {dashboard_file}")

        # Save report if requested
        if output:
            report_content = f"""DATABASE QUALITY REPORT
Overall Score: {report.overall_score:.1f}/100
Schema Score: {report.schema_score:.1f}/100
Content Score: {report.content_score:.1f}/100

DETAILED METRICS:
"""
            for metric in report.metrics:
                report_content += f"\n{metric.name}: {metric.score:.1f}/100\n"
                report_content += f"  {metric.details}\n"
                if metric.issues:
                    report_content += "  Issues:\n"
                    for issue in metric.issues:
                        report_content += f"    - {issue}\n"

            report_content += "\nRECOMMENDATIONS:\n"
            for i, rec in enumerate(report.recommendations, 1):
                report_content += f"{i}. {rec}\n"

            with open(output, "w") as f:
                f.write(report_content)
            click.echo(f"\nReport saved to {output}")

        # Readiness assessment
        if report.overall_score >= 80:
            click.echo("\n✅ Database is READY for semantic layer implementation")
        elif report.overall_score >= 60:
            click.echo("\n⚠️  Database needs MINOR improvements before semantic layer")
        else:
            click.echo("\n❌ Database needs MAJOR improvements before semantic layer")

    except Exception as e:
        click.echo(f"Error: {e}")
    finally:
        if "conn" in locals():
            conn.disconnect()


if __name__ == "__main__":
    assess_quality()
