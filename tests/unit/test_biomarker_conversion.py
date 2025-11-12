#!/usr/bin/env python3

"""
Test script for biomarker characterization conversion between YAML and RDF
"""

from rdf_semantic_converter import RDFSemanticConverter, convert_rdf_to_semantic_model
from semantic_model import SemanticModel
from semantic_view_generator import SemanticViewGenerator


def load_biomarker_model():
    """Load biomarker YAML semantic model"""
    print("1. Loading biomarker characterization semantic model from YAML...")
    try:
        biomarker_model = SemanticModel.from_yaml("biomarker_characterization.yaml")
        print(f"✓ Loaded model: {biomarker_model.name}")
        print(f"  - Tables: {len(biomarker_model.logical_tables)}")
        print(f"  - Relationships: {len(biomarker_model.relationships)}")
        print(f"  - Metrics: {len(biomarker_model.metrics)}")
        print(f"  - Verified queries: {len(biomarker_model.verified_queries)}")

        print("\n  Biomarker pipeline tables:")
        for table in biomarker_model.logical_tables:
            dims = len(table.dimensions)
            facts = len(table.facts) if hasattr(table, "facts") else 0
            time_dims = len(table.time_dimensions) if hasattr(table, "time_dimensions") else 0
            print(f"    - {table.name}: {dims} dimensions, {facts} facts, {time_dims} time dimensions")
    except Exception as e:
        print(f"✗ Error loading YAML: {e}")
        return None
    else:
        return biomarker_model


def convert_to_rdf(biomarker_model):
    """Convert YAML model to RDF"""
    print("2. Converting biomarker semantic model to RDF ontology...")
    try:
        converter = RDFSemanticConverter()
        rdf_content = converter.export_semantic_model_to_rdf(
            biomarker_model, "biomarker_from_yaml.ttl", format="turtle", namespace_uri="http://example.org/biomarker#"
        )
        print(f"✓ Converted to RDF: {len(rdf_content)} characters")
        print("✓ Saved to: biomarker_from_yaml.ttl")

        print("\nSample RDF content (first 25 lines):")
        lines = rdf_content.split("\n")
        for line in lines[:25]:
            print(f"  {line}")
        if len(lines) > 25:
            print("  ...")
    except Exception as e:
        print(f"✗ Error converting to RDF: {e}")


def load_rdf_ontology():
    """Load original RDF ontology and convert to semantic model"""
    print("3. Loading original biomarker RDF ontology...")
    try:
        original_rdf_model = convert_rdf_to_semantic_model("biomarker_ontology.ttl", "biomarker_from_rdf")
        print(f"✓ Loaded RDF model: {original_rdf_model.name}")
        print(f"  - Tables: {len(original_rdf_model.logical_tables)}")
        print(f"  - Relationships: {len(original_rdf_model.relationships)}")

        print("\n  Tables from RDF ontology:")
        for table in original_rdf_model.logical_tables:
            print(f"    - {table.name}: {len(table.dimensions)} dimensions")
    except Exception as e:
        print(f"✗ Error loading RDF: {e}")


def generate_semantic_view(biomarker_model):
    """Generate Snowflake semantic view"""
    print("4. Generating Snowflake semantic view for biomarker characterization...")
    try:
        view_generator = SemanticViewGenerator(biomarker_model)
        semantic_view_ddl = view_generator.generate_semantic_view("sv_biomarker_characterization")

        with open("biomarker_semantic_view.sql", "w") as f:
            f.write(semantic_view_ddl)

        print("✓ Generated Snowflake SEMANTIC VIEW DDL")
        print("✓ Saved to: biomarker_semantic_view.sql")

        print("\nSample DDL (first 20 lines):")
        ddl_lines = semantic_view_ddl.split("\n")
        for line in ddl_lines[:20]:
            print(f"  {line}")
        if len(ddl_lines) > 20:
            print("  ...")
    except Exception as e:
        print(f"✗ Error generating semantic view: {e}")


def analyze_model_structure(biomarker_model):
    """Analyze biomarker model structure"""
    print("5. Analyzing biomarker model structure...")
    try:
        print("  Key biomarker entities:")
        key_tables = ["biomarkers", "molecular_assays", "biomarker_measurements", "patient_outcomes"]
        for table_name in key_tables:
            table = next((t for t in biomarker_model.logical_tables if t.name == table_name), None)
            if table:
                print(f"    - {table.name}: {table.description}")

        print("\n  Key metrics for biomarker analysis:")
        key_metrics = ["biomarker_validation_rate", "significant_associations", "high_performance_biomarkers"]
        for metric_name in key_metrics:
            metric = next((m for m in biomarker_model.metrics if m.name == metric_name), None)
            if metric:
                print(f"    - {metric.name}: {metric.description}")

        print("\n  Sample verified queries:")
        for query in biomarker_model.verified_queries[:3]:
            print(f"    - {query.name}: {query.question}")
    except Exception as e:
        print(f"✗ Error analyzing model: {e}")


def export_multiple_formats(biomarker_model):
    """Export in multiple RDF formats"""
    print("6. Testing biomarker model export in different RDF formats...")
    formats = ["turtle", "xml", "n3"]
    for fmt in formats:
        try:
            converter = RDFSemanticConverter()
            rdf_output = converter.get_semantic_model_as_rdf_string(
                biomarker_model, format=fmt, namespace_uri="http://example.org/biomarker#"
            )
            filename = f"biomarker_characterization.{fmt}"
            with open(filename, "w") as f:
                f.write(rdf_output)
            print(f"   ✓ {fmt.upper()}: {len(rdf_output)} characters → {filename}")
        except Exception as e:
            print(f"   ✗ {fmt.upper()}: {e}")


def generate_mapping_report():
    """Generate mapping report"""
    print("7. Generating biomarker RDF mapping report...")
    try:
        converter = RDFSemanticConverter()
        converter.load_rdf("biomarker_ontology.ttl")
        mapping_report = converter.export_mapping_report()

        with open("biomarker_mapping_report.txt", "w") as f:
            f.write(mapping_report)

        print("✓ Generated mapping report")
        print("✓ Saved to: biomarker_mapping_report.txt")

        print("\nSample mapping report (first 25 lines):")
        report_lines = mapping_report.split("\n")
        for line in report_lines[:25]:
            print(f"  {line}")
        if len(report_lines) > 25:
            print("  ...")
    except Exception as e:
        print(f"✗ Error generating mapping report: {e}")


def main():
    print("=== Biomarker Characterization Conversion Test ===\n")

    biomarker_model = load_biomarker_model()
    if not biomarker_model:
        return

    print("\n" + "=" * 70 + "\n")
    convert_to_rdf(biomarker_model)

    print("\n" + "=" * 70 + "\n")
    load_rdf_ontology()

    print("\n" + "=" * 70 + "\n")
    generate_semantic_view(biomarker_model)

    print("\n" + "=" * 70 + "\n")
    analyze_model_structure(biomarker_model)

    print("\n" + "=" * 70 + "\n")
    export_multiple_formats(biomarker_model)

    print("\n" + "=" * 70 + "\n")
    generate_mapping_report()

    print("\n=== Test Complete ===")
    print("\nGenerated files for biomarker characterization:")
    print("  - biomarker_from_yaml.ttl")
    print("  - biomarker_semantic_view.sql")
    print("  - biomarker_mapping_report.txt")
    print("  - biomarker_characterization.turtle")
    print("  - biomarker_characterization.xml")
    print("  - biomarker_characterization.n3")

    print("\nBiomarker model summary:")
    print(f"  - {len(biomarker_model.logical_tables)} tables covering molecular to clinical data")
    print(f"  - {len(biomarker_model.relationships)} relationships linking biomarkers to outcomes")
    print(f"  - {len(biomarker_model.metrics)} metrics for biomarker performance analysis")
    print(f"  - {len(biomarker_model.verified_queries)} verified queries for common analyses")


if __name__ == "__main__":
    main()
