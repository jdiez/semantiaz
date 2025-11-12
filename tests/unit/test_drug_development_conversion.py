#!/usr/bin/env python3

"""
Test script for drug development pipeline conversion between YAML and RDF
"""

from rdf_semantic_converter import RDFSemanticConverter, convert_rdf_to_semantic_model
from semantic_model import SemanticModel
from semantic_view_generator import SemanticViewGenerator


def load_drug_model():
    """Load YAML semantic model"""
    print("1. Loading drug development semantic model from YAML...")
    try:
        drug_model = SemanticModel.from_yaml("drug_development_pipeline.yaml")
        print(f"✓ Loaded model: {drug_model.name}")
        print(f"  - Tables: {len(drug_model.logical_tables)}")
        print(f"  - Relationships: {len(drug_model.relationships)}")
        print(f"  - Metrics: {len(drug_model.metrics)}")
        print(f"  - Verified queries: {len(drug_model.verified_queries)}")

        print("\n  Tables in pipeline:")
        for table in drug_model.logical_tables:
            print(f"    - {table.name}: {len(table.dimensions)} dimensions, {len(table.facts)} facts")
    except Exception as e:
        print(f"✗ Error loading YAML: {e}")
        return None
    else:
        return drug_model


def convert_yaml_to_rdf(drug_model):
    """Convert YAML model to RDF"""
    print("2. Converting semantic model to RDF ontology...")
    try:
        converter = RDFSemanticConverter()
        rdf_content = converter.export_semantic_model_to_rdf(
            drug_model, "drug_development_from_yaml.ttl", format="turtle", namespace_uri="http://example.org/pharma#"
        )
        print(f"✓ Converted to RDF: {len(rdf_content)} characters")
        print("✓ Saved to: drug_development_from_yaml.ttl")

        print("\nSample RDF content:")
        lines = rdf_content.split("\n")
        for line in lines[:20]:
            print(f"  {line}")
        if len(lines) > 20:
            print("  ...")
    except Exception as e:
        print(f"✗ Error converting to RDF: {e}")


def load_original_rdf():
    """Load original RDF ontology"""
    print("3. Loading original RDF ontology...")
    try:
        original_rdf_model = convert_rdf_to_semantic_model("drug_development_ontology.ttl", "drug_development_from_rdf")
        print(f"✓ Loaded RDF model: {original_rdf_model.name}")
        print(f"  - Tables: {len(original_rdf_model.logical_tables)}")
        print(f"  - Relationships: {len(original_rdf_model.relationships)}")

        print("\n  Tables from RDF:")
        for table in original_rdf_model.logical_tables:
            print(f"    - {table.name}: {len(table.dimensions)} dimensions")
    except Exception as e:
        print(f"✗ Error loading RDF: {e}")


def generate_view_from_yaml(drug_model):
    """Generate Snowflake semantic view from YAML model"""
    print("4. Generating Snowflake semantic view from YAML model...")
    try:
        view_generator = SemanticViewGenerator(drug_model)
        semantic_view_ddl = view_generator.generate_semantic_view("sv_drug_development")

        with open("drug_development_semantic_view.sql", "w") as f:
            f.write(semantic_view_ddl)

        print("✓ Generated Snowflake SEMANTIC VIEW DDL")
        print("✓ Saved to: drug_development_semantic_view.sql")

        print("\nSample DDL:")
        ddl_lines = semantic_view_ddl.split("\n")
        for line in ddl_lines[:15]:
            print(f"  {line}")
        if len(ddl_lines) > 15:
            print("  ...")
    except Exception as e:
        print(f"✗ Error generating semantic view: {e}")


def generate_rdf_mapping_report():
    """Generate mapping report"""
    print("5. Generating RDF mapping report...")
    try:
        converter = RDFSemanticConverter()
        converter.load_rdf("drug_development_ontology.ttl")
        mapping_report = converter.export_mapping_report()

        with open("drug_development_mapping_report.txt", "w") as f:
            f.write(mapping_report)

        print("✓ Generated mapping report")
        print("✓ Saved to: drug_development_mapping_report.txt")

        print("\nSample mapping report:")
        report_lines = mapping_report.split("\n")
        for line in report_lines[:20]:
            print(f"  {line}")
        if len(report_lines) > 20:
            print("  ...")
    except Exception as e:
        print(f"✗ Error generating mapping report: {e}")


def test_rdf_export_formats(drug_model):
    """Export YAML model in different RDF formats"""
    print("6. Testing different RDF export formats...")
    formats = ["turtle", "xml", "n3"]
    for fmt in formats:
        try:
            converter = RDFSemanticConverter()
            rdf_output = converter.get_semantic_model_as_rdf_string(
                drug_model, format=fmt, namespace_uri="http://example.org/pharma#"
            )
            filename = f"drug_development.{fmt}"
            with open(filename, "w") as f:
                f.write(rdf_output)
            print(f"   ✓ {fmt.upper()}: {len(rdf_output)} characters → {filename}")
        except Exception as e:
            print(f"   ✗ {fmt.upper()}: {e}")


def main():
    print("=== Drug Development Pipeline Conversion Test ===\n")

    drug_model = load_drug_model()
    if not drug_model:
        return

    print("\n" + "=" * 60 + "\n")
    convert_yaml_to_rdf(drug_model)

    print("\n" + "=" * 60 + "\n")
    load_original_rdf()

    print("\n" + "=" * 60 + "\n")
    generate_view_from_yaml(drug_model)

    print("\n" + "=" * 60 + "\n")
    generate_rdf_mapping_report()

    print("\n" + "=" * 60 + "\n")
    test_rdf_export_formats(drug_model)

    print("\n=== Test Complete ===")
    print("\nGenerated files:")
    print("  - drug_development_from_yaml.ttl")
    print("  - drug_development_semantic_view.sql")
    print("  - drug_development_mapping_report.txt")
    print("  - drug_development.turtle")
    print("  - drug_development.xml")
    print("  - drug_development.n3")


if __name__ == "__main__":
    main()
