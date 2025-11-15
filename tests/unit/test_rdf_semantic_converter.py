"""Tests for RDF semantic converter module."""

from unittest.mock import Mock, patch

import pytest

from semantiaz.converters.rdf_semantic_converter import RDFSemanticConverter
from semantiaz.models.semantic_model import Dimension, SemanticModel, Table


class TestRDFSemanticConverter:
    """Test cases for RDFSemanticConverter class."""

    @pytest.fixture
    def converter(self):
        """Create RDFSemanticConverter instance."""
        return RDFSemanticConverter()

    @pytest.fixture
    def sample_turtle_content(self):
        """Sample Turtle RDF content for testing."""
        return """
        @prefix : <http://example.org/ontology#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        :Person rdf:type owl:Class ;
                rdfs:label "Person" ;
                rdfs:comment "A human being" .

        :Organization rdf:type owl:Class ;
                     rdfs:label "Organization" ;
                     rdfs:comment "A group or company" .

        :name rdf:type owl:DatatypeProperty ;
              rdfs:label "name" ;
              rdfs:comment "The name of something" ;
              rdfs:domain :Person ;
              rdfs:range xsd:string .

        :age rdf:type owl:DatatypeProperty ;
             rdfs:label "age" ;
             rdfs:comment "The age in years" ;
             rdfs:domain :Person ;
             rdfs:range xsd:integer .

        :worksFor rdf:type owl:ObjectProperty ;
                  rdfs:label "works for" ;
                  rdfs:comment "Employment relationship" ;
                  rdfs:domain :Person ;
                  rdfs:range :Organization .
        """

    def test_load_rdf_string(self, converter, sample_turtle_content):
        """Test loading RDF from string."""
        converter.load_rdf_string(sample_turtle_content, "turtle")

        assert len(converter.classes) > 0
        assert len(converter.properties) > 0
        assert "Person" in converter.classes
        assert "Organization" in converter.classes

    def test_extract_ontology_elements(self, converter, sample_turtle_content):
        """Test extraction of ontology elements."""
        converter.load_rdf_string(sample_turtle_content, "turtle")

        # Check classes
        assert "Person" in converter.classes
        assert converter.classes["Person"]["label"] == "Person"
        assert converter.classes["Person"]["comment"] == "A human being"

        # Check datatype properties
        assert "name" in converter.properties
        assert converter.properties["name"]["type"] == "datatype"
        assert converter.properties["name"]["label"] == "name"

        # Check object properties
        assert "worksFor" in converter.properties
        assert converter.properties["worksFor"]["type"] == "object"

    def test_map_datatype_to_sql(self, converter):
        """Test RDF datatype to SQL mapping."""
        assert converter._map_datatype_to_sql("http://www.w3.org/2001/XMLSchema#string") == "STRING"
        assert converter._map_datatype_to_sql("http://www.w3.org/2001/XMLSchema#integer") == "INTEGER"
        assert converter._map_datatype_to_sql("http://www.w3.org/2001/XMLSchema#decimal") == "DECIMAL"
        assert converter._map_datatype_to_sql("http://www.w3.org/2001/XMLSchema#boolean") == "BOOLEAN"
        assert converter._map_datatype_to_sql("http://www.w3.org/2001/XMLSchema#date") == "DATE"
        assert converter._map_datatype_to_sql("unknown_type") == "STRING"

    def test_map_sql_to_datatype(self, converter):
        """Test SQL to RDF datatype mapping."""
        assert converter._map_sql_to_datatype("STRING") == "http://www.w3.org/2001/XMLSchema#string"
        assert converter._map_sql_to_datatype("INTEGER") == "http://www.w3.org/2001/XMLSchema#integer"
        assert converter._map_sql_to_datatype("DECIMAL") == "http://www.w3.org/2001/XMLSchema#decimal"
        assert converter._map_sql_to_datatype("BOOLEAN") == "http://www.w3.org/2001/XMLSchema#boolean"
        assert converter._map_sql_to_datatype("DATE") == "http://www.w3.org/2001/XMLSchema#date"
        assert converter._map_sql_to_datatype("UNKNOWN") == "http://www.w3.org/2001/XMLSchema#string"

    def test_convert_to_semantic_model(self, converter, sample_turtle_content):
        """Test conversion from RDF to semantic model."""
        converter.load_rdf_string(sample_turtle_content, "turtle")

        model = converter.convert_to_semantic_model("test_model", "test_db", "test_schema")

        assert isinstance(model, SemanticModel)
        assert model.name == "test_model"
        assert len(model.logical_tables) > 0

        # Check that classes became tables
        table_names = [table.name for table in model.logical_tables]
        assert "person" in table_names
        assert "organization" in table_names

    def test_get_ontology_stats(self, converter, sample_turtle_content):
        """Test ontology statistics."""
        converter.load_rdf_string(sample_turtle_content, "turtle")

        stats = converter.get_ontology_stats()

        assert isinstance(stats, dict)
        assert "classes" in stats
        assert "object_properties" in stats
        assert "datatype_properties" in stats
        assert "total_triples" in stats
        assert stats["classes"] == 2
        assert stats["datatype_properties"] == 2
        assert stats["object_properties"] == 1

    def test_export_mapping_report(self, converter, sample_turtle_content):
        """Test mapping report generation."""
        converter.load_rdf_string(sample_turtle_content, "turtle")

        report = converter.export_mapping_report()

        assert isinstance(report, str)
        assert "RDF/OWL to Semantic Model Mapping Report" in report
        assert "Classes converted to tables" in report
        assert "Person -> person" in report
        assert "Organization -> organization" in report

    def test_convert_from_semantic_model(self, converter):
        """Test conversion from semantic model to RDF."""
        # Create a simple semantic model
        model = SemanticModel(name="test_model")

        # Add a table with dimensions
        table = Table(name="person", description="Person table")
        table.dimensions = [
            Dimension(name="name", data_type="STRING", description="Person name"),
            Dimension(name="age", data_type="INTEGER", description="Person age"),
        ]
        model.add_table(table)

        graph = converter.convert_from_semantic_model(model)

        assert len(graph) > 0
        # The graph should contain triples for the ontology

    def test_get_semantic_model_as_rdf_string(self, converter):
        """Test getting semantic model as RDF string."""
        model = SemanticModel(name="test_model")
        table = Table(name="person", description="Person table")
        table.dimensions = [Dimension(name="name", data_type="STRING", description="Person name")]
        model.add_table(table)

        rdf_string = converter.get_semantic_model_as_rdf_string(model, "turtle")

        assert isinstance(rdf_string, str)
        assert len(rdf_string) > 0
        # Should contain turtle syntax
        assert "@prefix" in rdf_string or "PREFIX" in rdf_string

    @patch("builtins.open", create=True)
    def test_export_semantic_model_to_rdf(self, mock_open, converter):
        """Test exporting semantic model to RDF file."""
        model = SemanticModel(name="test_model")
        table = Table(name="person", description="Person table")
        model.add_table(table)

        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        rdf_content = converter.export_semantic_model_to_rdf(model, "/path/to/output.ttl", "turtle")

        assert isinstance(rdf_content, str)
        mock_open.assert_called_once_with("/path/to/output.ttl", "w", encoding="utf-8")
        mock_file.write.assert_called_once()

    def test_get_local_name(self, converter):
        """Test local name extraction from URI."""
        from rdflib import URIRef

        uri1 = URIRef("http://example.org/ontology#Person")
        uri2 = URIRef("http://example.org/ontology/Person")

        assert converter._get_local_name(uri1) == "Person"
        assert converter._get_local_name(uri2) == "Person"

    def test_empty_ontology(self, converter):
        """Test handling of empty ontology."""
        converter.load_rdf_string("", "turtle")

        assert len(converter.classes) == 0
        assert len(converter.properties) == 0

        model = converter.convert_to_semantic_model("empty_model")
        assert len(model.logical_tables) == 0
