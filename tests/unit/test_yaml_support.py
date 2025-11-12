#!/usr/bin/env python3

"""
Test YAML support for semantic models
"""

from semantic_model import SemanticModel
from semantic_view_generator import SemanticViewGenerator


def main():
    print("=== YAML Semantic Model Support Test ===\n")

    # Load semantic model from YAML
    print("1. Loading semantic model from YAML...")
    try:
        clinical_model = SemanticModel.from_yaml("clinical_trial_semantic_model.yaml")
        print(f"✓ Successfully loaded: {clinical_model.name}")
        print(f"  - Tables: {len(clinical_model.logical_tables)}")
        print(f"  - Relationships: {len(clinical_model.relationships)}")
        print(f"  - Metrics: {len(clinical_model.metrics)}")
        print(f"  - Verified queries: {len(clinical_model.verified_queries)}")
    except Exception as e:
        print(f"✗ Error loading YAML: {e}")
        return

    print("\n" + "=" * 50 + "\n")

    # Export to JSON
    print("2. Exporting to JSON...")
    json_content = clinical_model.to_json("clinical_model_from_yaml.json")
    print(f"✓ Exported to JSON: {len(json_content)} characters")

    print("\n" + "=" * 50 + "\n")

    # Generate semantic view from YAML model
    print("3. Generating Snowflake semantic view...")
    generator = SemanticViewGenerator(clinical_model)
    semantic_view_ddl = generator.generate_semantic_view()

    print("✓ Generated semantic view DDL:")
    print(semantic_view_ddl[:200] + "..." if len(semantic_view_ddl) > 200 else semantic_view_ddl)

    # Save to file
    with open("semantic_view_from_yaml.sql", "w") as f:
        f.write(semantic_view_ddl)
    print("✓ Saved to: semantic_view_from_yaml.sql")

    print("\n" + "=" * 50 + "\n")

    # Round-trip test: YAML -> Model -> YAML
    print("4. Round-trip test (YAML -> Model -> YAML)...")
    yaml_output = clinical_model.to_yaml("clinical_model_roundtrip.yaml")
    print(f"✓ Round-trip YAML: {len(yaml_output)} characters")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()
