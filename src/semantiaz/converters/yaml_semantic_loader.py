#!/usr/bin/env python3

"""
YAML Semantic Model Loader
Load semantic models from YAML configuration files
"""

from semantic_model import SemanticModel


def load_clinical_model_from_yaml():
    """Load the clinical trial semantic model from YAML"""
    return SemanticModel.from_yaml("clinical_trial_semantic_model.yaml")


def main():
    # Load semantic model from YAML
    clinical_model = load_clinical_model_from_yaml()

    print(f"Loaded semantic model: {clinical_model.name}")
    print(f"Tables: {len(clinical_model.logical_tables)}")
    print(f"Relationships: {len(clinical_model.relationships)}")
    print(f"Metrics: {len(clinical_model.metrics)}")
    print(f"Verified queries: {len(clinical_model.verified_queries)}")

    # Export to JSON for comparison
    json_output = clinical_model.to_json("clinical_model_from_yaml.json")
    print(f"\nExported to JSON: {len(json_output)} characters")


if __name__ == "__main__":
    main()
