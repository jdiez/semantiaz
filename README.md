# semantiaz

[![Release](https://img.shields.io/github/v/release/kpdg464/semantiaz)](https://img.shields.io/github/v/release/kpdg464/semantiaz)
[![Build status](https://img.shields.io/github/actions/workflow/status/kpdg464/semantiaz/main.yml?branch=main)](https://github.com/kpdg464/semantiaz/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/kpdg464/semantiaz/branch/main/graph/badge.svg)](https://codecov.io/gh/kpdg464/semantiaz)
[![Commit activity](https://img.shields.io/github/commit-activity/m/kpdg464/semantiaz)](https://img.shields.io/github/commit-activity/m/kpdg464/semantiaz)
[![License](https://img.shields.io/github/license/kpdg464/semantiaz)](https://img.shields.io/github/license/kpdg464/semantiaz)

Comprehensive semantic model management platform for data warehouses with multi-database support, quality assessment, knowledge graph generation, and interactive visualization capabilities.

- **Github repository**: <https://github.com/kpdg464/semantiaz/>
- **Documentation** <https://kpdg464.github.io/semantiaz/>

## Features

### Core Capabilities
- **Multi-Database Support**: Generate semantic models from any RDBMS (PostgreSQL, MySQL, SQLite, DuckDB, BigQuery) using ibis
- **Schema Extraction**: Extract database schemas and generate semantic model YAML with intelligent type inference
- **View Deployment**: Deploy semantic views from annotated YAML models to Snowflake
- **Quality Assessment**: Comprehensive database quality evaluation for semantic layer readiness

### Knowledge Graph & Visualization
- **Knowledge Graph Generation**: Create RDF/TTL or Cypher knowledge graphs from database schema and content
- **Interactive Dashboards**: Generate Plotly and Vega-Lite dashboards for quality metrics visualization
- **Mermaid Diagrams**: Create ER diagrams, semantic model visualizations, and quality metric charts

### Data Format Conversion
- **RDF/OWL Conversion**: Convert between semantic models and RDF ontologies
- **Cypher Export**: Generate Neo4j Cypher statements from semantic models
- **Multiple Output Formats**: Support for YAML, JSON, RDF/TTL, Cypher, HTML dashboards

### Integration & Automation
- **MCP Server**: Model Context Protocol server for semantic operations
- **CLI Interface**: Comprehensive command-line tools for all operations
- **Sample Databases**: Pre-built clinical trial, biomarker, and drug development datasets

## Installation

```bash
make install
```

## Quick Start

### Generate Semantic Model (Generic - Any Database)

```bash
# From PostgreSQL
python -m semantiaz.cli generate-generic-model \
  --model-name my_model \
  --backend postgres \
  --host localhost \
  --user postgres \
  --password pass \
  --database mydb \
  --output model.yaml

# From DuckDB with multiple formats
python -m semantiaz.cli generate-generic-model \
  --model-name my_model \
  --backend duckdb \
  --database mydb \
  --file-path mydb.duckdb \
  --format all \
  --output model.yaml \
  --rdf-output model.ttl \
  --cypher-output model.cypher
```

### Generate Knowledge Graph

```bash
# RDF Knowledge Graph
python -m semantiaz.cli generate-kg \
  --backend postgres \
  --host localhost \
  --user postgres \
  --password pass \
  --database mydb \
  --format rdf \
  --output knowledge_graph.ttl

# Cypher Knowledge Graph
python -m semantiaz.cli generate-kg \
  --backend duckdb \
  --database mydb \
  --file-path mydb.duckdb \
  --format cypher \
  --output knowledge_graph.cypher
```

### Assess Database Quality

```bash
# Quality assessment with interactive dashboard
python -m semantiaz.cli assess-quality \
  --backend postgres \
  --host localhost \
  --user postgres \
  --password pass \
  --database mydb \
  --dashboard plotly \
  --dashboard-output quality_dashboard.html
```

### Generate Mermaid Diagrams

```bash
# Database ER diagram
python -m semantiaz.cli mermaid database-erd \
  --backend duckdb \
  --database mydb \
  --file-path mydb.duckdb \
  --output database_schema.mmd

# Semantic model diagram
python -m semantiaz.cli mermaid semantic-model \
  --yaml-file model.yaml \
  --output semantic_model.mmd

# Quality metrics diagram
python -m semantiaz.cli mermaid quality-metrics \
  --backend postgres \
  --host localhost \
  --user postgres \
  --password pass \
  --database mydb \
  --output quality_metrics.mmd
```

### Snowflake-Specific Operations

```bash
# Extract schema (Snowflake-specific)
python -m semantiaz.cli extract \
  --account your_account \
  --user your_user \
  --password your_pass \
  --warehouse your_wh \
  --database your_db \
  --schema your_schema \
  --model-name my_model \
  --output model.yaml

# Deploy views to Snowflake
python -m semantiaz.cli deploy \
  --account your_account \
  --user your_user \
  --password your_pass \
  --warehouse your_wh \
  --database your_db \
  --schema your_schema \
  --yaml-file model.yaml \
  --prefix semantic_
```

### Setup Sample Databases

```bash
# Create all sample databases on DuckDB
python -m semantiaz.cli setup-db --database duckdb

# Create specific database on Snowflake
python -m semantiaz.cli setup-db --database snowflake \
  --dataset clinical \
  --snowflake-account your_account \
  --snowflake-user your_user \
  --snowflake-password your_pass \
  --snowflake-warehouse your_wh
```

## Project Structure

```
src/semantiaz/
├── core/                      # Core functionality
│   ├── schema_extractor.py         # Snowflake schema extraction
│   ├── view_deployer.py            # Semantic view deployment
│   └── semantic_view_generator.py  # Snowflake SEMANTIC VIEW DDL generation
├── models/                    # Semantic models and schemas
│   ├── semantic_model.py           # Core semantic model framework
│   └── clinical_trial_semantic_model.py  # Sample clinical trial model
├── converters/                # Data format converters
│   ├── semantic_to_rdf.py          # RDF/OWL conversion
│   └── semantic_to_cypher.py       # Neo4j Cypher conversion
├── quality/                   # Database quality assessment
│   ├── db_quality_assessor.py      # Quality metrics evaluation
│   └── dashboard_generator.py      # Interactive dashboard generation
├── plotting/                  # Visualization and diagramming
│   └── mermaid_generator.py        # Mermaid diagram generation
├── servers/                   # MCP server implementations
│   └── snowflake_semantic_mcp_server.py  # MCP server for Snowflake
├── cli_*.py                   # CLI command modules
│   ├── cli_model_generator.py      # Snowflake model generation
│   ├── cli_generic_model_generator.py  # Multi-database model generation
│   ├── cli_knowledge_graph_generator.py  # Knowledge graph generation
│   ├── cli_quality_assessment.py   # Quality assessment CLI
│   └── cli_mermaid.py              # Mermaid diagram CLI
└── cli.py                     # Main CLI interface

data/                          # Sample data and schemas
├── clinical_trial_database.sql     # Clinical trial sample database
├── clinical_trial_semantic_model.yaml  # Sample semantic model
├── biomarker_database.sql          # Biomarker sample database
└── drug_development_database.sql   # Drug development sample database

docs/                          # Documentation
tests/unit/                    # Unit tests
```

## CLI Commands Overview

### Model Generation
- `generate-model` - Generate semantic model from Snowflake (legacy)
- `generate-generic-model` - Generate semantic model from any database with RDF/Cypher export
- `generate-kg` - Generate knowledge graphs (RDF/Cypher) from database content

### Quality & Assessment
- `assess-quality` - Comprehensive database quality assessment with dashboards

### Visualization
- `mermaid database-erd` - Generate database ER diagrams
- `mermaid semantic-model` - Generate semantic model flowcharts
- `mermaid quality-metrics` - Generate quality metrics visualizations

### Snowflake Operations
- `extract` - Extract Snowflake schema to semantic model
- `deploy` - Deploy semantic views to Snowflake

### Utilities
- `setup-db` - Create sample databases (DuckDB/Snowflake)

## Development

```bash
make install
uv run pre-commit run -a
```

## Use Cases

### Data Engineering
- **Schema Documentation** - Generate comprehensive documentation from existing databases
- **Quality Assessment** - Evaluate database readiness before implementing semantic layers
- **Migration Planning** - Assess and visualize database structure for migration projects

### Analytics & BI
- **Semantic Layer Creation** - Build semantic models for business intelligence tools
- **Knowledge Graph Construction** - Create graph representations of relational data
- **Data Lineage** - Visualize relationships and dependencies in data models

### Data Governance
- **Quality Monitoring** - Continuous assessment of data quality metrics
- **Documentation Generation** - Automated creation of data dictionaries and ER diagrams
- **Compliance Reporting** - Generate reports on data structure and quality for audits



## Supported Databases

### Via Ibis (Generic Commands)
- **PostgreSQL** - Full support with connection strings or individual parameters
- **MySQL** - Full support with connection strings or individual parameters
- **SQLite** - File-based database support
- **DuckDB** - File-based analytical database support
- **BigQuery** - Google Cloud BigQuery support

### Native Integration
- **Snowflake** - Full semantic layer support with view deployment

## Output Formats

### Semantic Models
- **YAML** - Human-readable semantic model definitions
- **JSON** - Machine-readable semantic model format

### Knowledge Graphs
- **RDF/TTL** - Resource Description Framework in Turtle format
- **Cypher** - Neo4j graph database query language

### Visualizations
- **Plotly HTML** - Interactive web-based dashboards
- **Vega-Lite JSON** - Declarative visualization specifications
- **Mermaid** - Text-based diagrams for documentation

## Quality Assessment Metrics

### Schema Quality (Structure)
- Table documentation coverage
- Column documentation coverage
- Primary key coverage
- Foreign key relationships
- Data type appropriateness

### Content Quality (Data)
- Null value patterns
- Data consistency
- Duplicate records

### Readiness Assessment
- **Ready (80-100%)** - Database is ready for semantic layer
- **Minor Improvements (60-79%)** - Small fixes needed
- **Major Improvements (<60%)** - Significant work required

## MCP Tools Available

- `create_semantic_model_from_schema` - Generate YAML from database schema
- `deploy_semantic_view` - Deploy single view from YAML
- `deploy_all_views_from_yaml` - Deploy multiple views from YAML
- `convert_rdf_to_semantic_model_tool` - Convert RDF/OWL to semantic model
- `export_semantic_model_to_rdf` - Export semantic model to RDF/OWL

## License

MIT License
