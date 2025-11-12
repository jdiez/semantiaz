#!/usr/bin/env python3

import json
import os

from snowflake_semantic_mcp_server import SNOWFLAKE_CONFIG, mcp


def load_config():
    """Load configuration from file if it exists"""
    config_file = "mcp_config.json"
    if os.path.exists(config_file):
        with open(config_file) as f:
            config = json.load(f)
            return config.get("snowflake", SNOWFLAKE_CONFIG)
    return SNOWFLAKE_CONFIG


def main():
    """Start the MCP server with configuration"""
    config = load_config()

    # Update global config
    SNOWFLAKE_CONFIG.update(config)

    print("Starting Snowflake Semantic Model MCP Server...")
    print(f"Database: {config.get('database', 'N/A')}")
    print(f"Schema: {config.get('schema', 'N/A')}")

    # Start the server
    mcp.run()


if __name__ == "__main__":
    main()
