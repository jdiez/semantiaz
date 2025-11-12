#!/usr/bin/env python3

"""
Test bidirectional conversion between RDF/OWL and Semantic Models
"""

from rdf_semantic_converter import RDFSemanticConverter, convert_rdf_to_semantic_model, convert_semantic_model_to_rdf
from semantic_model import SemanticModel


def test_rdf_roundtrip():
    """Test RDF → Semantic Model → RDF round-trip"""
    print("1. Testing RDF → Semantic Model → RDF round-trip...")
    try:
        print("   Loading original RDF ontology...")
        original_model = convert_rdf_to_semantic_model("sample_ontology.ttl", "healthcare_test")
        print(f"   ✓ Converted to semantic model: {original_model.name}")
        print(f"     - Tables: {len(original_model.logical_tables)}")
        print(f"     - Relationships: {len(original_model.relationships)}")

        print("   Converting semantic model back to RDF...")
        rdf_content = convert_semantic_model_to_rdf(
            original_model, "healthcare_roundtrip.ttl", format="turtle", namespace_uri="http://example.org/healthcare#"
        )
        print(f"   ✓ Exported to RDF: {len(rdf_content)} characters")
    except Exception as e:
        print(f"   ✗ Error in round-trip test: {e}")
        return None
    else:
        return original_model


def test_yaml_to_rdf():
    """Test YAML → Semantic Model → RDF conversion"""
    print("2. Testing YAML → Semantic Model → RDF conversion...")
    try:
        print("   Loading semantic model from YAML...")
        yaml_model = SemanticModel.from_yaml("clinical_trial_semantic_model.yaml")
        print(f"   ✓ Loaded from YAML: {yaml_model.name}")

        print("   Converting to RDF ontology...")
        converter = RDFSemanticConverter()
        rdf_string = converter.get_semantic_model_as_rdf_string(
            yaml_model, format="turtle", namespace_uri="http://example.org/clinical#"
        )

        with open("clinical_trial_ontology.ttl", "w") as f:
            f.write(rdf_string)

        print(f"   ✓ Converted to RDF: {len(rdf_string)} characters")
        print("   ✓ Saved to: clinical_trial_ontology.ttl")
    except Exception as e:
        print(f"   ✗ Error in YAML→RDF conversion: {e}")
        return None
    else:
        return yaml_model


def show_rdf_samples():
    """Show RDF content samples"""
    print("3. Sample RDF content from conversions...")
    try:
        with open("healthcare_roundtrip.ttl") as f:
            healthcare_rdf = f.read()

        print("   Healthcare ontology (round-trip):")
        lines = healthcare_rdf.split("\n")
        for line in lines[:15]:
            print(f"     {line}")
        if len(lines) > 15:
            print("     ...")

        print("\n   Clinical trial ontology (from YAML):")
        with open("clinical_trial_ontology.ttl") as f:
            clinical_rdf = f.read()

        lines = clinical_rdf.split("\n")
        for line in lines[:15]:
            print(f"     {line}")
        if len(lines) > 15:
            print("     ...")
    except Exception as e:
        print(f"   ✗ Error reading RDF files: {e}")


def validate_roundtrip(original_model):
    """Validate round-trip conversion"""
    print("4. Validating round-trip conversion...")
    try:
        roundtrip_model = convert_rdf_to_semantic_model("healthcare_roundtrip.ttl", "healthcare_roundtrip_test")
        print(f"   ✓ Re-loaded round-trip model: {roundtrip_model.name}")
        print(f"     - Tables: {len(roundtrip_model.logical_tables)}")
        print(f"     - Relationships: {len(roundtrip_model.relationships)}")

        print("   Comparison with original:")
        print(f"     Original tables: {len(original_model.logical_tables)}")
        print(f"     Round-trip tables: {len(roundtrip_model.logical_tables)}")
        print(f"     Original relationships: {len(original_model.relationships)}")
        print(f"     Round-trip relationships: {len(roundtrip_model.relationships)}")

        if len(original_model.logical_tables) == len(roundtrip_model.logical_tables):
            print("   ✓ Table count preserved")
        else:
            print("   ⚠ Table count differs")
    except Exception as e:
        print(f"   ✗ Error in validation: {e}")


def test_rdf_formats(yaml_model):
    """Test different RDF formats"""
    print("5. Testing different RDF formats...")
    formats = ["turtle", "xml", "n3"]
    for fmt in formats:
        try:
            converter = RDFSemanticConverter()
            rdf_output = converter.get_semantic_model_as_rdf_string(
                yaml_model, format=fmt, namespace_uri="http://example.org/clinical#"
            )
            filename = f"clinical_trial.{fmt}"
            with open(filename, "w") as f:
                f.write(rdf_output)
            print(f"   ✓ {fmt.upper()}: {len(rdf_output)} characters → {filename}")
        except Exception as e:
            print(f"   ✗ {fmt.upper()}: {e}")


def main():
    print("=== Bidirectional RDF ↔ Semantic Model Conversion Test ===\n")

    original_model = test_rdf_roundtrip()
    if not original_model:
        return

    print("\n" + "=" * 60 + "\n")
    yaml_model = test_yaml_to_rdf()
    if not yaml_model:
        return

    print("\n" + "=" * 60 + "\n")
    show_rdf_samples()

    print("\n" + "=" * 60 + "\n")
    validate_roundtrip(original_model)

    print("\n" + "=" * 60 + "\n")
    test_rdf_formats(yaml_model)

    print("\n=== Test Complete ===")
    print("\nGenerated files:")
    print("  - healthcare_roundtrip.ttl")
    print("  - clinical_trial_ontology.ttl")
    print("  - clinical_trial.turtle")
    print("  - clinical_trial.xml")
    print("  - clinical_trial.n3")


if __name__ == "__main__":
    main()
