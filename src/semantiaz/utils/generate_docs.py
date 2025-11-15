#!/usr/bin/env python3
"""Generate comprehensive documentation for the semantiaz package.

This script generates API documentation using pydoc and creates a structured
documentation website with module overviews, class references, and usage examples.
"""

import subprocess
import sys
from pathlib import Path


def generate_module_docs():
    """Generate documentation for all modules in the package."""

    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    # Create docs directory
    docs_dir = Path(__file__).parent / "docs" / "api"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Modules to document
    modules = [
        "semantiaz.models.semantic_model",
        "semantiaz.core.schema_extractor",
        "semantiaz.core.view_deployer",
        "semantiaz.core.semantic_view_generator",
        "semantiaz.quality.db_quality_assessor",
        "semantiaz.quality.dashboard_generator",
        "semantiaz.plotting.mermaid_generator",
        "semantiaz.converters.semantic_to_rdf",
        "semantiaz.converters.semantic_to_cypher",
        "semantiaz.cli_model_generator",
        "semantiaz.cli_generic_model_generator",
        "semantiaz.cli_knowledge_graph_generator",
        "semantiaz.cli_quality_assessment",
        "semantiaz.cli_mermaid",
    ]

    print("Generating API documentation...")

    for module_name in modules:
        try:
            # Generate HTML documentation
            _ = docs_dir / f"{module_name.replace('.', '_')}.html"
            cmd = [sys.executable, "-m", "pydoc", "-w", module_name]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=docs_dir)

            if result.returncode == 0:
                print(f"✓ Generated docs for {module_name}")
            else:
                print(f"✗ Failed to generate docs for {module_name}: {result.stderr}")

        except Exception as e:
            print(f"✗ Error generating docs for {module_name}: {e}")

    # Generate index page
    generate_index_page(docs_dir, modules)

    print(f"\nDocumentation generated in: {docs_dir}")
    print("Open docs/api/index.html in your browser to view the documentation.")


def generate_index_page(docs_dir: Path, modules: list):
    """Generate an index page for the documentation."""

    index_content = """<!DOCTYPE html>
<html>
<head>
    <title>Semantiaz API Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
        .module-list { list-style-type: none; padding: 0; }
        .module-list li { margin: 10px 0; }
        .module-list a { text-decoration: none; color: #3498db; font-weight: bold; }
        .module-list a:hover { color: #2980b9; }
        .description { color: #7f8c8d; margin-left: 20px; }
        .section { margin: 30px 0; }
    </style>
</head>
<body>
    <h1>Semantiaz API Documentation</h1>

    <div class="section">
        <h2>Overview</h2>
        <p>Semantiaz is a comprehensive semantic model management platform for data warehouses with multi-database support, quality assessment, knowledge graph generation, and interactive visualization capabilities.</p>
    </div>

    <div class="section">
        <h2>Core Modules</h2>
        <ul class="module-list">
            <li><a href="semantiaz_models_semantic_model.html">semantiaz.models.semantic_model</a>
                <div class="description">Core semantic model framework with Pydantic models</div></li>
            <li><a href="semantiaz_core_schema_extractor.html">semantiaz.core.schema_extractor</a>
                <div class="description">Snowflake database schema extraction</div></li>
            <li><a href="semantiaz_core_view_deployer.html">semantiaz.core.view_deployer</a>
                <div class="description">Semantic view deployment to Snowflake</div></li>
            <li><a href="semantiaz_core_semantic_view_generator.html">semantiaz.core.semantic_view_generator</a>
                <div class="description">Snowflake SEMANTIC VIEW DDL generation</div></li>
        </ul>
    </div>

    <div class="section">
        <h2>Quality Assessment</h2>
        <ul class="module-list">
            <li><a href="semantiaz_quality_db_quality_assessor.html">semantiaz.quality.db_quality_assessor</a>
                <div class="description">Database quality metrics evaluation for semantic layer readiness</div></li>
            <li><a href="semantiaz_quality_dashboard_generator.html">semantiaz.quality.dashboard_generator</a>
                <div class="description">Interactive Plotly and Vega-Lite dashboard generation</div></li>
        </ul>
    </div>

    <div class="section">
        <h2>Visualization & Plotting</h2>
        <ul class="module-list">
            <li><a href="semantiaz_plotting_mermaid_generator.html">semantiaz.plotting.mermaid_generator</a>
                <div class="description">Mermaid diagram generation for ER diagrams and semantic models</div></li>
        </ul>
    </div>

    <div class="section">
        <h2>Data Format Converters</h2>
        <ul class="module-list">
            <li><a href="semantiaz_converters_semantic_to_rdf.html">semantiaz.converters.semantic_to_rdf</a>
                <div class="description">RDF/OWL conversion from semantic models</div></li>
            <li><a href="semantiaz_converters_semantic_to_cypher.html">semantiaz.converters.semantic_to_cypher</a>
                <div class="description">Neo4j Cypher generation from semantic models</div></li>
        </ul>
    </div>

    <div class="section">
        <h2>CLI Modules</h2>
        <ul class="module-list">
            <li><a href="semantiaz_cli_model_generator.html">semantiaz.cli_model_generator</a>
                <div class="description">Snowflake-specific semantic model generation CLI</div></li>
            <li><a href="semantiaz_cli_generic_model_generator.html">semantiaz.cli_generic_model_generator</a>
                <div class="description">Multi-database semantic model generation with ibis</div></li>
            <li><a href="semantiaz_cli_knowledge_graph_generator.html">semantiaz.cli_knowledge_graph_generator</a>
                <div class="description">Knowledge graph generation from database content</div></li>
            <li><a href="semantiaz_cli_quality_assessment.html">semantiaz.cli_quality_assessment</a>
                <div class="description">Database quality assessment CLI with dashboard generation</div></li>
            <li><a href="semantiaz_cli_mermaid.html">semantiaz.cli_mermaid</a>
                <div class="description">Mermaid diagram generation CLI for various diagram types</div></li>
        </ul>
    </div>

    <div class="section">
        <h2>Quick Links</h2>
        <ul>
            <li><a href="../README.md">README</a> - Getting started and usage examples</li>
            <li><a href="https://github.com/kpdg464/semantiaz">GitHub Repository</a></li>
        </ul>
    </div>

</body>
</html>"""

    with open(docs_dir / "index.html", "w") as f:
        f.write(index_content)


if __name__ == "__main__":
    generate_module_docs()
