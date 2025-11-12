#!/usr/bin/env python3

"""
RDF/OWL to Semantic Model Converter
Converts RDF/OWL ontologies into semantic models for Snowflake
"""

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS
from semantic_model import BaseTable, Columns, Dimension, LogicalTable, Relationship, RelationshipColumn, SemanticModel


class RDFSemanticConverter:
    """Converts RDF/OWL ontologies to semantic models"""

    def __init__(self) -> None:
        """Initialize RDFSemanticConverter"""
        self.graph = Graph()
        self.classes: dict[str, dict] = {}
        self.properties: dict[str, dict] = {}
        self.individuals: dict[str, dict] = {}

    def load_rdf(self, file_path: str, rdf_format: str = "turtle") -> None:
        """Load RDF/OWL file from path
        Args:
            file_path (str): Path to RDF/OWL file
            rdf_format (str): Format of RDF file (e.g., 'turtle', 'xml', 'n3')
        Returns:
            None
        """
        self.graph.parse(file_path, format=rdf_format)
        self._extract_ontology_elements()

    def load_rdf_string(self, rdf_content: str, rdf_format: str = "turtle") -> None:
        """Load RDF/OWL from string
        Args:
            rdf_content (str): RDF/OWL content as string
            rdf_format (str): Format of RDF content (e.g., 'turtle', 'xml', 'n3')
        Returns:
            None
        """
        self.graph.parse(data=rdf_content, format=rdf_format)
        self._extract_ontology_elements()

    def _extract_ontology_elements(self) -> None:
        """Extract classes, properties, and individuals from RDF graph
        Args:
            None
        Returns:
            None
        """
        # Extract classes
        for subj in self.graph.subjects(RDF.type, OWL.Class):
            class_name = self._get_local_name(subj)
            self.classes[class_name] = {
                "uri": str(subj),
                "label": self._get_label(subj),
                "comment": self._get_comment(subj),
                "superclasses": list(self.graph.objects(subj, RDFS.subClassOf)),
                "properties": [],
            }

        # Extract object properties
        for subj in self.graph.subjects(RDF.type, OWL.ObjectProperty):
            prop_name = self._get_local_name(subj)
            self.properties[prop_name] = {
                "uri": str(subj),
                "label": self._get_label(subj),
                "comment": self._get_comment(subj),
                "domain": list(self.graph.objects(subj, RDFS.domain)),
                "range": list(self.graph.objects(subj, RDFS.range)),
                "type": "object",
            }

        # Extract data properties
        for subj in self.graph.subjects(RDF.type, OWL.DatatypeProperty):
            prop_name = self._get_local_name(subj)
            self.properties[prop_name] = {
                "uri": str(subj),
                "label": self._get_label(subj),
                "comment": self._get_comment(subj),
                "domain": list(self.graph.objects(subj, RDFS.domain)),
                "range": list(self.graph.objects(subj, RDFS.range)),
                "type": "datatype",
            }

    def _get_local_name(self, uri: URIRef) -> str:
        """Extract local name from URI
        Args:
            uri (URIRef): The URI to extract the local name from
        Returns:
            str: Local name extracted from the URI
        """
        return str(uri).split("#")[-1].split("/")[-1]

    def _get_label(self, uri: URIRef) -> str | None:
        """Get rdfs:label for URI
        Args:
            uri (URIRef): The URI to get the label for
        Returns:
            str | None: The label if exists, else None
        """
        labels = list(self.graph.objects(uri, RDFS.label))
        return str(labels[0]) if labels else None

    def _get_comment(self, uri: URIRef) -> str | None:
        """Get rdfs:comment for URI
        Args:
            uri (URIRef): The URI to get the comment for
        Returns:
            str | None: The comment if exists, else None
        """
        comments = list(self.graph.objects(uri, RDFS.comment))
        return str(comments[0]) if comments else None

    def _map_datatype_to_sql(self, datatype_uri: str) -> str:
        """Map RDF datatype to SQL datatype
        Args:
            datatype_uri (str): RDF datatype URI
        Returns:
            str: Corresponding SQL datatype
        """
        datatype_mapping = {
            "http://www.w3.org/2001/XMLSchema#string": "STRING",
            "http://www.w3.org/2001/XMLSchema#int": "INTEGER",
            "http://www.w3.org/2001/XMLSchema#integer": "INTEGER",
            "http://www.w3.org/2001/XMLSchema#decimal": "DECIMAL",
            "http://www.w3.org/2001/XMLSchema#float": "FLOAT",
            "http://www.w3.org/2001/XMLSchema#double": "DOUBLE",
            "http://www.w3.org/2001/XMLSchema#boolean": "BOOLEAN",
            "http://www.w3.org/2001/XMLSchema#date": "DATE",
            "http://www.w3.org/2001/XMLSchema#dateTime": "TIMESTAMP",
            "http://www.w3.org/2001/XMLSchema#time": "TIME",
        }
        return datatype_mapping.get(datatype_uri, "STRING")

    def _map_sql_to_datatype(self, sql_type: str) -> str:
        """Map SQL datatype to RDF datatype
        Args:
            sql_type (str): SQL datatype
        Returns:
            str: Corresponding RDF datatype URI
        """
        sql_mapping = {
            "STRING": "http://www.w3.org/2001/XMLSchema#string",
            "INTEGER": "http://www.w3.org/2001/XMLSchema#integer",
            "DECIMAL": "http://www.w3.org/2001/XMLSchema#decimal",
            "FLOAT": "http://www.w3.org/2001/XMLSchema#float",
            "DOUBLE": "http://www.w3.org/2001/XMLSchema#double",
            "BOOLEAN": "http://www.w3.org/2001/XMLSchema#boolean",
            "DATE": "http://www.w3.org/2001/XMLSchema#date",
            "TIMESTAMP": "http://www.w3.org/2001/XMLSchema#dateTime",
            "TIME": "http://www.w3.org/2001/XMLSchema#time",
        }
        return sql_mapping.get(sql_type.upper(), "http://www.w3.org/2001/XMLSchema#string")

    def convert_to_semantic_model(
        self, model_name: str, database: str = "ontology_db", schema: str = "semantic"
    ) -> SemanticModel:
        """Convert RDF/OWL to semantic model
        Args:
            model_name (str): Name of the semantic model
            database (str): Target database name
            schema (str): Target schema name
        Returns:
            SemanticModel: Converted semantic model
        """
        model = SemanticModel(name=model_name)

        # Convert classes to logical tables
        for class_name, class_info in self.classes.items():
            table_name = class_name.lower()
            description = class_info.get("comment") or class_info.get("label")

            # Create base table
            base_table = BaseTable(database=database, schema=schema, table=table_name)

            # Create logical table with ID as primary key
            pk = Columns(names=[f"{table_name}_id"])
            logical_table = LogicalTable(
                name=table_name, description=description, base_table=base_table, primary_key=pk
            )

            # Add ID dimension
            id_dimension = Dimension(
                name=f"{table_name}_id",
                data_type="STRING",
                unique=True,
                description=f"Unique identifier for {class_name}",
            )
            logical_table.dimensions.append(id_dimension)

            # Add dimensions from datatype properties
            for prop_name, prop_info in self.properties.items():
                if prop_info["type"] == "datatype":
                    # Check if property applies to this class
                    domain_classes = [self._get_local_name(d) for d in prop_info["domain"]]
                    if not domain_classes or class_name in domain_classes:
                        # Determine SQL datatype
                        range_types = [str(r) for r in prop_info["range"]]
                        sql_type = self._map_datatype_to_sql(range_types[0]) if range_types else "STRING"

                        dimension = Dimension(
                            name=prop_name,
                            data_type=sql_type,
                            description=prop_info.get("comment") or prop_info.get("label"),
                        )
                        logical_table.dimensions.append(dimension)

            model.add_table(logical_table)

        # Convert object properties to relationships
        for prop_name, prop_info in self.properties.items():
            if prop_info["type"] == "object":
                domain_classes = [self._get_local_name(d) for d in prop_info["domain"]]
                range_classes = [self._get_local_name(r) for r in prop_info["range"]]

                # Create relationships between domain and range classes
                for domain_class in domain_classes:
                    for range_class in range_classes:
                        if domain_class in self.classes and range_class in self.classes:
                            rel_name = f"{domain_class.lower()}_to_{range_class.lower()}_{prop_name}"

                            rel_col = RelationshipColumn(
                                left_column=f"{range_class.lower()}_id", right_column=f"{range_class.lower()}_id"
                            )

                            relationship = Relationship(
                                name=rel_name,
                                left_table=domain_class.lower(),
                                right_table=range_class.lower(),
                                relationship_columns=[rel_col],
                                relationship_type="MANY_TO_ONE",
                            )

                            model.add_relationship(relationship)

        return model

    def get_ontology_stats(self) -> dict[str, int]:
        """Get statistics about the loaded ontology
        Args:
            None
        Returns:
            dict[str, int]: Statistics including number of classes, properties, and triples
        """
        return {
            "classes": len(self.classes),
            "object_properties": len([p for p in self.properties.values() if p["type"] == "object"]),
            "datatype_properties": len([p for p in self.properties.values() if p["type"] == "datatype"]),
            "total_triples": len(self.graph),
        }

    def export_mapping_report(self) -> str:
        """Generate a mapping report showing RDF to semantic model conversion
        Args:
            None
        Returns:
            str: Mapping report as a string
        """
        report = ["RDF/OWL to Semantic Model Mapping Report", "=" * 50, ""]

        report.append(f"Classes converted to tables: {len(self.classes)}")
        for class_name, class_info in self.classes.items():
            report.append(f"  - {class_name} -> {class_name.lower()}")
            if class_info.get("comment"):
                report.append(f"    Description: {class_info['comment']}")

        report.append("")
        report.append(
            f"Object properties converted to relationships: {len([p for p in self.properties.values() if p['type'] == 'object'])}"
        )
        for prop_name, prop_info in self.properties.items():
            if prop_info["type"] == "object":
                report.append(f"  - {prop_name}")
                if prop_info.get("comment"):
                    report.append(f"    Description: {prop_info['comment']}")

        report.append("")
        report.append(
            f"Datatype properties converted to dimensions: {len([p for p in self.properties.values() if p['type'] == 'datatype'])}"
        )
        for prop_name, prop_info in self.properties.items():
            if prop_info["type"] == "datatype":
                range_types = [str(r) for r in prop_info["range"]]
                sql_type = self._map_datatype_to_sql(range_types[0]) if range_types else "STRING"
                report.append(f"  - {prop_name} -> {sql_type}")

        return "\n".join(report)

    def convert_from_semantic_model(
        self, semantic_model: SemanticModel, namespace_uri: str = "http://example.org/semantic#"
    ) -> Graph:
        """Convert semantic model to RDF/OWL ontology
        Args:
            semantic_model (SemanticModel): The semantic model to convert
            namespace_uri (str): The base namespace URI for the ontology
        Returns:
            Graph: RDFLib Graph representing the ontology
        """
        graph = Graph()

        # Define namespaces
        ns = Namespace(namespace_uri)
        graph.bind("", ns)
        graph.bind("owl", OWL)
        graph.bind("rdfs", RDFS)
        graph.bind("rdf", RDF)

        # Create ontology declaration
        ontology_uri = URIRef(namespace_uri.rstrip("#/"))
        graph.add((ontology_uri, RDF.type, OWL.Ontology))
        graph.add((ontology_uri, RDFS.label, Literal(f"{semantic_model.name} Ontology")))
        graph.add((
            ontology_uri,
            RDFS.comment,
            Literal(f"Ontology generated from semantic model: {semantic_model.name}"),
        ))

        # Convert logical tables to OWL classes
        for table in semantic_model.logical_tables:
            class_uri = ns[table.name.title()]
            graph.add((class_uri, RDF.type, OWL.Class))
            graph.add((class_uri, RDFS.label, Literal(table.name.title())))
            if table.description:
                graph.add((class_uri, RDFS.comment, Literal(table.description)))

            # Convert dimensions to datatype properties
            for dim in table.dimensions:
                if dim.name.endswith("_id"):  # Skip ID fields
                    continue

                prop_uri = ns[dim.name]
                graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
                graph.add((prop_uri, RDFS.label, Literal(dim.name.replace("_", " ").title())))
                if dim.description:
                    graph.add((prop_uri, RDFS.comment, Literal(dim.description)))

                # Set domain
                graph.add((prop_uri, RDFS.domain, class_uri))

                # Set range based on data type
                if dim.data_type:
                    xsd_type = URIRef(self._map_sql_to_datatype(dim.data_type))
                    graph.add((prop_uri, RDFS.range, xsd_type))

        # Convert relationships to object properties
        for rel in semantic_model.relationships:
            prop_name = rel.name.replace("_to_", "_").replace("_", "")
            prop_uri = ns[prop_name]

            graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
            graph.add((prop_uri, RDFS.label, Literal(prop_name.replace("_", " ").title())))

            # Set domain and range
            domain_class = ns[rel.left_table.title()]
            range_class = ns[rel.right_table.title()]
            graph.add((prop_uri, RDFS.domain, domain_class))
            graph.add((prop_uri, RDFS.range, range_class))

        return graph

    def export_semantic_model_to_rdf(
        self,
        semantic_model: SemanticModel,
        output_path: str,
        rdf_format: str = "turtle",
        namespace_uri: str = "http://example.org/semantic#",
    ) -> str:
        """Export semantic model to RDF file
        Args:
            semantic_model (SemanticModel): The semantic model to export
            output_path (str): Path to output RDF file
            rdf_format (str): RDF serialization format (e.g., 'turtle', 'xml', 'n3')
            namespace_uri (str): The base namespace URI for the ontology
        Returns:
            str: RDF content as a string
        """
        graph = self.convert_from_semantic_model(semantic_model, namespace_uri)
        rdf_content = graph.serialize(format=rdf_format)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rdf_content)

        return rdf_content

    def get_semantic_model_as_rdf_string(
        self,
        semantic_model: SemanticModel,
        rdf_format: str = "turtle",
        namespace_uri: str = "http://example.org/semantic#",
    ) -> str:
        """Get semantic model as RDF string
        Args:
            semantic_model (SemanticModel): The semantic model to convert
            rdf_format (str): RDF serialization format (e.g., 'turtle', 'xml', 'n3')
            namespace_uri (str): The base namespace URI for the ontology
        Returns:
            str: RDF content as a string
        """
        graph = self.convert_from_semantic_model(semantic_model, namespace_uri)
        return graph.serialize(format=rdf_format)


def convert_rdf_to_semantic_model(
    rdf_file: str, model_name: str, database: str = "ontology_db", schema: str = "semantic", rdf_format: str = "turtle"
) -> SemanticModel:
    """Convenience function to convert RDF file to semantic model
    Args:
        rdf_file (str): Path to RDF/OWL file
        model_name (str): Name of the semantic model
        database (str): Target database name
        schema (str): Target schema name
        rdf_format (str): Format of RDF file (e.g., 'turtle', 'xml', 'n3')
    Returns:
        SemanticModel: Converted semantic model
    """
    converter = RDFSemanticConverter()
    converter.load_rdf(rdf_file, rdf_format)
    return converter.convert_to_semantic_model(model_name, database, schema)


def convert_semantic_model_to_rdf(
    semantic_model: SemanticModel,
    output_path: str,
    rdf_format: str = "turtle",
    namespace_uri: str = "http://example.org/semantic#",
) -> str:
    """Convenience function to convert semantic model to RDF file
    Args:
        semantic_model (SemanticModel): The semantic model to convert
        output_path (str): Path to output RDF file
        rdf_format (str): RDF serialization format (e.g., 'turtle', 'xml', 'n3')
        namespace_uri (str): The base namespace URI for the ontology
    Returns:
        str: RDF content as a string
    """
    converter = RDFSemanticConverter()
    return converter.export_semantic_model_to_rdf(semantic_model, output_path, rdf_format, namespace_uri)
