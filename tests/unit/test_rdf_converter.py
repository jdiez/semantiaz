#!/usr/bin/env python3

"""
Test script for RDF/OWL to Semantic Model converter
"""

from rdf_semantic_converter import RDFSemanticConverter, convert_rdf_to_semantic_model
from semantic_view_generator import SemanticViewGenerator


def load_rdf_ontology():
    """Load and convert RDF ontology"""
    print("1. Loading healthcare ontology from RDF...")
    try:
        converter = RDFSemanticConverter()
        converter.load_rdf("sample_ontology.ttl", format="turtle")
        stats = converter.get_ontology_stats()
        print("✓ Loaded ontology with:")
        print(f"  - Classes: {stats['classes']}")
        print(f"  - Object Properties: {stats['object_properties']}")
        print(f"  - Datatype Properties: {stats['datatype_properties']}")
        print(f"  - Total Triples: {stats['total_triples']}")
    except Exception as e:
        print(f"✗ Error loading RDF: {e}")
        return None
    else:
        return converter


def convert_to_semantic_model(converter):
    """Convert to semantic model"""
    print("2. Converting to semantic model...")
    try:
        semantic_model = converter.convert_to_semantic_model(
            "healthcare_ontology", database="healthcare_db", schema="ontology"
        )
        print(f"✓ Created semantic model: {semantic_model.name}")
        print(f"  - Tables: {len(semantic_model.logical_tables)}")
        print(f"  - Relationships: {len(semantic_model.relationships)}")

        print("\n  Tables created:")
        for table in semantic_model.logical_tables:
            print(f"    - {table.name}: {len(table.dimensions)} dimensions")
    except Exception as e:
        print(f"✗ Error converting: {e}")
        return None
    else:
        return semantic_model


def generate_mapping_report(converter):
    """Generate mapping report"""
    print("3. Generating mapping report...")
    mapping_report = converter.export_mapping_report()
    print(mapping_report)
    with open("rdf_mapping_report.txt", "w") as f:
        f.write(mapping_report)
    print("\n✓ Mapping report saved to: rdf_mapping_report.txt")


def export_to_yaml(semantic_model):
    """Export semantic model to YAML"""
    print("4. Exporting semantic model to YAML...")
    try:
        yaml_content = semantic_model.to_yaml("healthcare_ontology_model.yaml")
        print(f"✓ Exported to YAML: {len(yaml_content)} characters")

        print("\nSample YAML content:")
        lines = yaml_content.split("\n")
        for line in lines[:15]:
            print(f"  {line}")
        if len(lines) > 15:
            print("  ...")
    except Exception as e:
        print(f"✗ Error exporting YAML: {e}")


def generate_snowflake_view(semantic_model):
    """Generate Snowflake semantic view"""
    print("5. Generating Snowflake semantic view...")
    try:
        view_generator = SemanticViewGenerator(semantic_model)
        semantic_view_ddl = view_generator.generate_semantic_view("sv_healthcare_ontology")
        print("✓ Generated Snowflake SEMANTIC VIEW DDL")
        print("\nSample DDL:")
        ddl_lines = semantic_view_ddl.split("\n")
        for line in ddl_lines[:10]:
            print(f"  {line}")
        if len(ddl_lines) > 10:
            print("  ...")

        with open("healthcare_semantic_view.sql", "w") as f:
            f.write(semantic_view_ddl)
        print("\n✓ DDL saved to: healthcare_semantic_view.sql")
    except Exception as e:
        print(f"✗ Error generating semantic view: {e}")


def test_convenience_function():
    """Test convenience function"""
    print("6. Testing convenience function...")
    try:
        model2 = convert_rdf_to_semantic_model(
            "sample_ontology.ttl", "healthcare_model_v2", database="healthcare_v2", schema="models"
        )
        print(f"✓ Created model via convenience function: {model2.name}")
        print(f"  - Tables: {len(model2.logical_tables)}")
    except Exception as e:
        print(f"✗ Error with convenience function: {e}")


def main():
    print("=== RDF/OWL to Semantic Model Converter Test ===\n")

    converter = load_rdf_ontology()
    if not converter:
        return

    print("\n" + "=" * 50 + "\n")
    semantic_model = convert_to_semantic_model(converter)
    if not semantic_model:
        return

    print("\n" + "=" * 50 + "\n")
    generate_mapping_report(converter)

    print("\n" + "=" * 50 + "\n")
    export_to_yaml(semantic_model)

    print("\n" + "=" * 50 + "\n")
    generate_snowflake_view(semantic_model)

    print("\n" + "=" * 50 + "\n")
    test_convenience_function()

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()
