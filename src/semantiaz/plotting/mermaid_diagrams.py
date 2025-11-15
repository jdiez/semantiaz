"""Comprehensive Mermaid diagram generation class with methods for each diagram type.

This module provides a unified interface for generating various types of Mermaid diagrams
including flowcharts, ER diagrams, sequence diagrams, Gantt charts, and more.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DiagramType(Enum):
    """Supported Mermaid diagram types."""

    FLOWCHART = "flowchart"
    ER_DIAGRAM = "erDiagram"
    SEQUENCE = "sequenceDiagram"
    GANTT = "gantt"
    PIE = "pie"
    GITGRAPH = "gitGraph"
    CLASS = "classDiagram"
    STATE = "stateDiagram"
    JOURNEY = "journey"


@dataclass
class Node:
    """Represents a node in a diagram."""

    id: str
    label: str
    shape: str = "rect"  # rect, circle, diamond, etc.
    style: str | None = None


@dataclass
class Edge:
    """Represents an edge/connection between nodes."""

    from_node: str
    to_node: str
    label: str | None = None
    style: str = "solid"  # solid, dashed, dotted


@dataclass
class Entity:
    """Represents an entity in ER diagrams."""

    name: str
    attributes: list[dict[str, str]]  # [{"name": "id", "type": "int", "key": "PK"}]


@dataclass
class Relationship:
    """Represents a relationship in ER diagrams."""

    from_entity: str
    to_entity: str
    cardinality: str  # "||--o{", "||--||", etc.
    label: str | None = None


class MermaidDiagrams:
    """Comprehensive Mermaid diagram generator with methods for each diagram type.

    This class provides methods to generate various types of Mermaid diagrams with
    proper syntax and styling. Each method accepts structured input parameters
    and returns valid Mermaid markup.
    """

    def __init__(self):
        """Initialize the Mermaid diagram generator."""
        self.theme = "default"
        self.direction = "TD"  # Top-Down

    def create_flowchart(
        self, nodes: list[Node], edges: list[Edge], direction: str = "TD", title: str | None = None
    ) -> str:
        """Create a Mermaid flowchart diagram.

        Args:
            nodes: List of Node objects representing flowchart nodes.
            edges: List of Edge objects representing connections.
            direction: Flow direction (TD, LR, BT, RL).
            title: Optional diagram title.

        Returns:
            Mermaid flowchart markup string.
        """
        lines = [f"flowchart {direction}"]

        if title:
            lines.insert(0, f"---\ntitle: {title}\n---")

        # Add nodes
        for node in nodes:
            shape_map = {
                "rect": f"{node.id}[{node.label}]",
                "circle": f"{node.id}(({node.label}))",
                "diamond": f"{node.id}{{{node.label}}}",
                "hexagon": f"{node.id}{{{{{node.label}}}}}",
                "stadium": f"{node.id}([{node.label}])",
            }
            lines.append(f"    {shape_map.get(node.shape, shape_map['rect'])}")

        # Add edges
        for edge in edges:
            arrow_map = {
                "solid": "-->",
                "dashed": "-.->",
                "dotted": "..->",
                "thick": "==>",
            }
            arrow = arrow_map.get(edge.style, "-->")

            if edge.label:
                lines.append(f"    {edge.from_node} {arrow}|{edge.label}| {edge.to_node}")
            else:
                lines.append(f"    {edge.from_node} {arrow} {edge.to_node}")

        return "\n".join(lines)

    def create_er_diagram(
        self, entities: list[Entity], relationships: list[Relationship], title: str | None = None
    ) -> str:
        """Create a Mermaid ER diagram.

        Args:
            entities: List of Entity objects with attributes.
            relationships: List of Relationship objects.
            title: Optional diagram title.

        Returns:
            Mermaid ER diagram markup string.
        """
        lines = ["erDiagram"]

        if title:
            lines.insert(0, f"---\ntitle: {title}\n---")

        # Add entities with attributes
        for entity in entities:
            lines.append(f"    {entity.name} {{")
            for attr in entity.attributes:
                key_indicator = f" {attr.get('key', '')}" if attr.get("key") else ""
                lines.append(f"        {attr['type']} {attr['name']}{key_indicator}")
            lines.append("    }")

        # Add relationships
        for rel in relationships:
            label_part = f" : {rel.label}" if rel.label else ""
            lines.append(f"    {rel.from_entity} {rel.cardinality} {rel.to_entity}{label_part}")

        return "\n".join(lines)

    def create_sequence_diagram(
        self, participants: list[str], messages: list[dict[str, str]], title: str | None = None
    ) -> str:
        """Create a Mermaid sequence diagram.

        Args:
            participants: List of participant names.
            messages: List of message dicts with 'from', 'to', 'message', 'type' keys.
            title: Optional diagram title.

        Returns:
            Mermaid sequence diagram markup string.
        """
        lines = ["sequenceDiagram"]

        if title:
            lines.insert(0, f"---\ntitle: {title}\n---")

        # Add participants
        for participant in participants:
            lines.append(f"    participant {participant}")

        # Add messages
        for msg in messages:
            msg_type = msg.get("type", "sync")
            arrow_map = {"sync": "->", "async": "->>", "return": "-->>", "activate": "+"}
            arrow = arrow_map.get(msg_type, "->")

            lines.append(f"    {msg['from']}{arrow}{msg['to']}: {msg['message']}")

        return "\n".join(lines)

    def create_gantt_chart(self, tasks: list[dict[str, Any]], title: str | None = None) -> str:
        """Create a Mermaid Gantt chart.

        Args:
            tasks: List of task dicts with 'name', 'id', 'start', 'duration' keys.
            title: Optional diagram title.

        Returns:
            Mermaid Gantt chart markup string.
        """
        lines = ["gantt"]

        if title:
            lines.append(f"    title {title}")

        lines.append("    dateFormat  YYYY-MM-DD")

        # Group tasks by section if provided
        sections = {}
        for task in tasks:
            section = task.get("section", "Tasks")
            if section not in sections:
                sections[section] = []
            sections[section].append(task)

        for section_name, section_tasks in sections.items():
            lines.append(f"    section {section_name}")
            for task in section_tasks:
                status = task.get("status", "")
                lines.append(f"    {task['name']} :{status} {task['id']}, {task['start']}, {task['duration']}")

        return "\n".join(lines)

    def create_pie_chart(self, data: dict[str, float], title: str | None = None) -> str:
        """Create a Mermaid pie chart.

        Args:
            data: Dictionary mapping labels to values.
            title: Optional diagram title.

        Returns:
            Mermaid pie chart markup string.
        """
        lines = ["pie"]

        if title:
            lines.append(f"    title {title}")

        for label, value in data.items():
            lines.append(f'    "{label}" : {value}')

        return "\n".join(lines)

    def create_class_diagram(
        self, classes: list[dict[str, Any]], relationships: list[dict[str, str]], title: str | None = None
    ) -> str:
        """Create a Mermaid class diagram.

        Args:
            classes: List of class dicts with 'name', 'attributes', 'methods' keys.
            relationships: List of relationship dicts with 'from', 'to', 'type' keys.
            title: Optional diagram title.

        Returns:
            Mermaid class diagram markup string.
        """
        lines = ["classDiagram"]

        if title:
            lines.insert(0, f"---\ntitle: {title}\n---")

        # Add classes
        for cls in classes:
            lines.append(f"    class {cls['name']} {{")

            # Add attributes
            for attr in cls.get("attributes", []):
                visibility = attr.get("visibility", "+")
                lines.append(f"        {visibility}{attr['name']} {attr['type']}")

            # Add methods
            for method in cls.get("methods", []):
                visibility = method.get("visibility", "+")
                params = method.get("params", "")
                return_type = method.get("return_type", "void")
                lines.append(f"        {visibility}{method['name']}({params}) {return_type}")

            lines.append("    }")

        # Add relationships
        for rel in relationships:
            rel_map = {"inheritance": "<|--", "composition": "*--", "aggregation": "o--", "association": "-->"}
            symbol = rel_map.get(rel["type"], "-->")
            lines.append(f"    {rel['from']} {symbol} {rel['to']}")

        return "\n".join(lines)

    def create_state_diagram(
        self, states: list[str], transitions: list[dict[str, str]], title: str | None = None
    ) -> str:
        """Create a Mermaid state diagram.

        Args:
            states: List of state names.
            transitions: List of transition dicts with 'from', 'to', 'trigger' keys.
            title: Optional diagram title.

        Returns:
            Mermaid state diagram markup string.
        """
        lines = ["stateDiagram-v2"]

        if title:
            lines.insert(0, f"---\ntitle: {title}\n---")

        # Add states
        for state in states:
            lines.append(f"    {state}")

        # Add transitions
        for transition in transitions:
            trigger = f" : {transition['trigger']}" if transition.get("trigger") else ""
            lines.append(f"    {transition['from']} --> {transition['to']}{trigger}")

        return "\n".join(lines)

    def create_user_journey(self, journey_data: dict[str, Any], title: str | None = None) -> str:
        """Create a Mermaid user journey diagram.

        Args:
            journey_data: Dict with 'title', 'actors', 'sections' keys.
            title: Optional diagram title.

        Returns:
            Mermaid user journey markup string.
        """
        lines = ["journey"]

        if title:
            lines.append(f"    title {title}")
        elif journey_data.get("title"):
            lines.append(f"    title {journey_data['title']}")

        for section in journey_data.get("sections", []):
            lines.append(f"    section {section['name']}")
            for task in section.get("tasks", []):
                actors_scores = []
                for actor in journey_data.get("actors", []):
                    score = task.get("scores", {}).get(actor, 5)
                    actors_scores.append(f"{actor}: {score}")

                lines.append(f"      {task['name']}: {': '.join(actors_scores)}")

        return "\n".join(lines)

    def add_styling(self, diagram: str, styles: dict[str, str]) -> str:
        """Add CSS styling to a Mermaid diagram.

        Args:
            diagram: Base Mermaid diagram markup.
            styles: Dictionary mapping element IDs to CSS styles.

        Returns:
            Diagram with styling applied.
        """
        lines = diagram.split("\n")

        # Add styling at the end
        for element_id, style in styles.items():
            lines.append(f"    style {element_id} {style}")

        return "\n".join(lines)
