"""Convert semantic models to Cypher queries for Neo4j"""

from ..models.semantic_model import SemanticModel


class SemanticToCypherConverter:
    """Convert semantic model to Cypher CREATE statements for Neo4j"""

    def convert(self, model: SemanticModel) -> str:
        """Convert semantic model to Cypher"""
        cypher_statements = []

        # Create nodes for each table
        for table in model.tables:
            # Create table node
            table_props = {
                "name": table.name,
                "description": table.description or "",
                "database": table.base_table.database if table.base_table else "",
                "schema": table.base_table.schema if table.base_table else "",
            }

            props_str = ", ".join([f"{k}: '{v}'" for k, v in table_props.items() if v])
            cypher_statements.append(f"CREATE (:{table.name}:Table {{{props_str}}})")

            # Create dimension nodes
            for dim in table.dimensions:
                dim_props = {"name": dim.name, "data_type": dim.data_type or "", "description": dim.description or ""}
                props_str = ", ".join([f"{k}: '{v}'" for k, v in dim_props.items() if v])
                cypher_statements.append(f"CREATE (:{dim.name}:Dimension {{{props_str}}})")
                cypher_statements.append(f"MATCH (t:{table.name}), (d:{dim.name}) CREATE (t)-[:HAS_DIMENSION]->(d)")

            # Create fact nodes
            if table.facts:
                for fact in table.facts:
                    fact_props = {
                        "name": fact.name,
                        "data_type": fact.data_type or "",
                        "description": fact.description or "",
                    }
                    props_str = ", ".join([f"{k}: '{v}'" for k, v in fact_props.items() if v])
                    cypher_statements.append(f"CREATE (:{fact.name}:Fact {{{props_str}}})")
                    cypher_statements.append(f"MATCH (t:{table.name}), (f:{fact.name}) CREATE (t)-[:HAS_FACT]->(f)")

        # Create relationship edges
        for rel in model.relationships:
            cypher_statements.append(
                f"MATCH (l:{rel.left_table}), (r:{rel.right_table}) "
                f"CREATE (l)-[:RELATED_TO {{name: '{rel.name}', type: '{rel.relationship_type}'}}]->(r)"
            )

        # Create metric nodes
        for metric in model.metrics:
            metric_props = {
                "name": metric.name or "",
                "description": metric.description or "",
                "expr": metric.expr or "",
            }
            props_str = ", ".join([f"{k}: '{v}'" for k, v in metric_props.items() if v])
            cypher_statements.append(f"CREATE (:{metric.name or 'metric'}:Metric {{{props_str}}})")

        return ";\n".join(cypher_statements) + ";"
