"""Tests for Mermaid diagram generator module."""

import pytest

from semantiaz.plotting.mermaid_diagrams import Edge, Entity, MermaidDiagrams, Node, Relationship


class TestMermaidDiagrams:
    """Test cases for MermaidDiagrams class."""

    @pytest.fixture
    def generator(self):
        """Create MermaidDiagrams instance."""
        return MermaidDiagrams()

    def test_create_flowchart(self, generator):
        """Test flowchart creation."""
        nodes = [
            Node(id="A", label="Start", shape="rect"),
            Node(id="B", label="Process", shape="rect"),
            Node(id="C", label="End", shape="rect"),
        ]
        edges = [Edge(from_node="A", to_node="B", label="Begin"), Edge(from_node="B", to_node="C", label="Finish")]

        diagram = generator.create_flowchart(nodes, edges, direction="TD", title="Test Flow")

        assert "flowchart TD" in diagram
        assert "A[Start]" in diagram
        assert "B[Process]" in diagram
        assert "C[End]" in diagram
        assert "A -->|Begin| B" in diagram
        assert "B -->|Finish| C" in diagram

    def test_create_er_diagram(self, generator):
        """Test ER diagram creation."""
        entities = [
            Entity(
                name="Customer",
                attributes=[{"name": "id", "type": "int", "key": "PK"}, {"name": "name", "type": "string"}],
            ),
            Entity(
                name="Order",
                attributes=[
                    {"name": "id", "type": "int", "key": "PK"},
                    {"name": "customer_id", "type": "int", "key": "FK"},
                ],
            ),
        ]
        relationships = [Relationship(from_entity="Customer", to_entity="Order", cardinality="||--o{", label="places")]

        diagram = generator.create_er_diagram(entities, relationships, title="Test ER")

        assert "erDiagram" in diagram
        assert "Customer {" in diagram
        assert "int id PK" in diagram
        assert "string name" in diagram
        assert "Order {" in diagram
        assert "Customer ||--o{ Order : places" in diagram

    def test_create_sequence_diagram(self, generator):
        """Test sequence diagram creation."""
        participants = ["Alice", "Bob"]
        messages = [
            {"from": "Alice", "to": "Bob", "message": "Hello", "type": "sync"},
            {"from": "Bob", "to": "Alice", "message": "Hi there", "type": "return"},
        ]

        diagram = generator.create_sequence_diagram(participants, messages, title="Test Sequence")

        assert "sequenceDiagram" in diagram
        assert "participant Alice" in diagram
        assert "participant Bob" in diagram
        assert "Alice->>Bob: Hello" in diagram
        assert "Bob-->>Alice: Hi there" in diagram

    def test_create_gantt_chart(self, generator):
        """Test Gantt chart creation."""
        tasks = [
            {"name": "Task 1", "id": "task1", "start": "2024-01-01", "duration": "5d", "section": "Phase 1"},
            {
                "name": "Task 2",
                "id": "task2",
                "start": "2024-01-06",
                "duration": "3d",
                "section": "Phase 1",
                "status": "done",
            },
        ]

        diagram = generator.create_gantt_chart(tasks, title="Test Gantt")

        assert "gantt" in diagram
        assert "title Test Gantt" in diagram
        assert "section Phase 1" in diagram
        assert "Task 1 :task1, 2024-01-01, 5d" in diagram
        assert "Task 2 :done, task2, 2024-01-06, 3d" in diagram

    def test_create_pie_chart(self, generator):
        """Test pie chart creation."""
        data = {"Category A": 30, "Category B": 45, "Category C": 25}

        diagram = generator.create_pie_chart(data, title="Test Pie")

        assert "pie title Test Pie" in diagram
        assert '"Category A" : 30' in diagram
        assert '"Category B" : 45' in diagram
        assert '"Category C" : 25' in diagram

    def test_create_class_diagram(self, generator):
        """Test class diagram creation."""
        classes = [
            {
                "name": "Animal",
                "attributes": [{"name": "name", "type": "string", "visibility": "+"}],
                "methods": [{"name": "makeSound", "return_type": "void", "visibility": "+"}],
            },
            {
                "name": "Dog",
                "attributes": [{"name": "breed", "type": "string", "visibility": "+"}],
                "methods": [{"name": "bark", "return_type": "void", "visibility": "+"}],
            },
        ]
        relationships = [{"from": "Animal", "to": "Dog", "type": "inheritance"}]

        diagram = generator.create_class_diagram(classes, relationships, title="Test Class")

        assert "classDiagram" in diagram
        assert "class Animal {" in diagram
        assert "+string name" in diagram
        assert "+makeSound() void" in diagram
        assert "class Dog {" in diagram
        assert "Animal <|-- Dog" in diagram

    def test_node_shapes(self, generator):
        """Test different node shapes in flowchart."""
        nodes = [
            Node(id="A", label="Rectangle", shape="rect"),
            Node(id="B", label="Circle", shape="circle"),
            Node(id="C", label="Diamond", shape="diamond"),
            Node(id="D", label="Hexagon", shape="hexagon"),
            Node(id="E", label="Stadium", shape="stadium"),
        ]
        edges = []

        diagram = generator.create_flowchart(nodes, edges)

        assert "A[Rectangle]" in diagram
        assert "B((Circle))" in diagram
        assert "C{Diamond}" in diagram
        assert "D{{Hexagon}}" in diagram
        assert "E([Stadium])" in diagram

    def test_edge_styles(self, generator):
        """Test different edge styles in flowchart."""
        nodes = [Node(id="A", label="Start"), Node(id="B", label="End")]
        edges = [
            Edge(from_node="A", to_node="B", style="solid"),
            Edge(from_node="A", to_node="B", style="dashed"),
            Edge(from_node="A", to_node="B", style="dotted"),
            Edge(from_node="A", to_node="B", style="thick"),
        ]

        diagram = generator.create_flowchart(nodes, edges)

        assert "A --> B" in diagram  # solid (default)
        assert "A -.-> B" in diagram  # dashed
        assert "A ..-> B" in diagram  # dotted
        assert "A ==> B" in diagram  # thick
