# semantiaz

[![Release](https://img.shields.io/github/v/release/kpdg464/semantiaz)](https://img.shields.io/github/v/release/kpdg464/semantiaz)
[![Build status](https://img.shields.io/github/actions/workflow/status/kpdg464/semantiaz/main.yml?branch=main)](https://github.com/kpdg464/semantiaz/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/kpdg464/semantiaz/branch/main/graph/badge.svg)](https://codecov.io/gh/kpdg464/semantiaz)
[![Commit activity](https://img.shields.io/github/commit-activity/m/kpdg464/semantiaz)](https://img.shields.io/github/commit-activity/m/kpdg464/semantiaz)
[![License](https://img.shields.io/github/license/kpdg464/semantiaz)](https://img.shields.io/github/license/kpdg464/semantiaz)

Semantic model management for data warehouses with Snowflake integration, RDF/OWL conversion, and MCP server capabilities.

- **Github repository**: <https://github.com/kpdg464/semantiaz/>
- **Documentation** <https://kpdg464.github.io/semantiaz/>

## Features

- **Schema Extraction**: Generate semantic model YAML from Snowflake database schemas
- **View Deployment**: Deploy semantic views from annotated YAML models
- **RDF/OWL Conversion**: Convert between semantic models and RDF ontologies
- **MCP Server**: Model Context Protocol server for semantic operations
- **CLI Interface**: Command-line tools for schema extraction and view deployment

## Installation

```bash
make install
```

## Quick Start

### Extract Schema to Semantic Model

```bash
python -m semantiaz.cli extract \
  --account your_account \
  --user your_user \
  --password your_pass \
  --warehouse your_wh \
  --database your_db \
  --schema your_schema \
  --model-name my_model \
  --output model.yaml
```

### Deploy Views from Semantic Model

```bash
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
# Create all databases on DuckDB
python -m semantiaz.cli setup-db --database duckdb

# Create specific database on Snowflake
python -m semantiaz.cli setup-db --database snowflake \
  --dataset clinical \
  --snowflake-account your_account \
  --snowflake-user your_user \
  --snowflake-password your_pass \
  --snowflake-warehouse your_wh
```

### Start MCP Server

```bash
python -m semantiaz.servers.snowflake_semantic_mcp_server
```

## Project Structure

```
src/semantiaz/
├── core/                 # Core functionality
│   ├── schema_extractor.py    # Database schema extraction
│   ├── view_deployer.py       # Semantic view deployment
│   └── semantic_view_generator.py
├── models/               # Semantic models and schemas
├── converters/           # Data format converters
├── servers/              # MCP server implementations
└── cli.py               # Command-line interface

data/                    # YAML, TTL, JSON data files
tests/unit/              # Unit tests
```

## Development

```bash
make install
uv run pre-commit run -a
```



## MCP Tools Available

- `create_semantic_model_from_schema` - Generate YAML from database schema
- `deploy_semantic_view` - Deploy single view from YAML
- `deploy_all_views_from_yaml` - Deploy multiple views from YAML
- `convert_rdf_to_semantic_model_tool` - Convert RDF/OWL to semantic model
- `export_semantic_model_to_rdf` - Export semantic model to RDF/OWL

## License

MIT License
