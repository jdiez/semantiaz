"""Tests for FastMCP Mermaid server module."""

from unittest.mock import patch

from semantiaz.servers.mermaid_mcp_server import (
    create_class_diagram_tool,
    create_er_diagram,
    create_er_diagram_tool,
    create_flowchart,
    create_flowchart_tool,
    create_gantt_chart_tool,
    create_pie_chart_tool,
    create_sequence_diagram_tool,
    diagram_optimization,
    diagram_troubleshooting,
    mcp,
)


class TestFastMCPServer:
    """Test cases for FastMCP Mermaid server."""

    def test_create_flowchart_prompt(self):
        """Test flowchart creation prompt."""
        result = create_flowchart("user registration", "simple")

        assert isinstance(result, str)
        assert "user registration" in result
        assert "simple" in result
        assert "flowchart" in result.lower()
        assert "Start/End Points" in result

    def test_create_er_diagram_prompt(self):
        """Test ER diagram creation prompt."""
        result = create_er_diagram("e-commerce", "5")

        assert isinstance(result, str)
        assert "e-commerce" in result
        assert "5" in result
        assert "ER diagram" in result
        assert "Entities" in result

    def test_diagram_troubleshooting_prompt(self):
        """Test diagram troubleshooting prompt."""
        result = diagram_troubleshooting("flowchart", "Syntax error on line 5")

        assert isinstance(result, str)
        assert "flowchart" in result
        assert "Syntax error on line 5" in result
        assert "troubleshoot" in result.lower()
        assert "Syntax Errors" in result

    def test_diagram_optimization_prompt(self):
        """Test diagram optimization prompt."""
        current_diagram = "flowchart TD\n    A --> B"
        result = diagram_optimization(current_diagram, "readability")

        assert isinstance(result, str)
        assert "readability" in result
        assert current_diagram in result
        assert "optimize" in result.lower()
        assert "Readability" in result

    @patch("semantiaz.servers.mermaid_mcp_server.mermaid_generator")
    def test_create_flowchart_tool(self, mock_generator):
        """Test flowchart tool execution."""
        mock_generator.create_flowchart.return_value = "flowchart TD\n    A[Start] --> B[End]"

        nodes = [{"id": "A", "label": "Start", "shape": "rect"}, {"id": "B", "label": "End", "shape": "rect"}]
        edges = [{"from_node": "A", "to_node": "B", "label": "Process"}]

        result = create_flowchart_tool(nodes, edges, "TD", "Test Flow")

        assert isinstance(result, str)
        assert "Generated Mermaid flowchart" in result
        assert "```mermaid" in result
        assert "flowchart TD" in result

    @patch("semantiaz.servers.mermaid_mcp_server.mermaid_generator")
    def test_create_er_diagram_tool(self, mock_generator):
        """Test ER diagram tool execution."""
        mock_generator.create_er_diagram.return_value = "erDiagram\n    Customer ||--o{ Order : places"

        entities = [
            {
                "name": "Customer",
                "attributes": [{"name": "id", "type": "int", "key": "PK"}, {"name": "name", "type": "string"}],
            }
        ]
        relationships = [{"from_entity": "Customer", "to_entity": "Order", "cardinality": "||--o{", "label": "places"}]

        result = create_er_diagram_tool(entities, relationships, "Test ER")

        assert isinstance(result, str)
        assert "Generated Mermaid ER diagram" in result
        assert "```mermaid" in result
        assert "erDiagram" in result

    @patch("semantiaz.servers.mermaid_mcp_server.mermaid_generator")
    def test_create_sequence_diagram_tool(self, mock_generator):
        """Test sequence diagram tool execution."""
        mock_generator.create_sequence_diagram.return_value = "sequenceDiagram\n    Alice->>Bob: Hello"

        participants = ["Alice", "Bob"]
        messages = [{"from": "Alice", "to": "Bob", "message": "Hello", "type": "sync"}]

        result = create_sequence_diagram_tool(participants, messages, "Test Sequence")

        assert isinstance(result, str)
        assert "Generated Mermaid sequence diagram" in result
        assert "```mermaid" in result
        assert "sequenceDiagram" in result

    @patch("semantiaz.servers.mermaid_mcp_server.mermaid_generator")
    def test_create_gantt_chart_tool(self, mock_generator):
        """Test Gantt chart tool execution."""
        mock_generator.create_gantt_chart.return_value = "gantt\n    title Test Project"

        tasks = [{"name": "Task 1", "id": "task1", "start": "2024-01-01", "duration": "5d", "section": "Phase 1"}]

        result = create_gantt_chart_tool(tasks, "Test Gantt")

        assert isinstance(result, str)
        assert "Generated Mermaid Gantt chart" in result
        assert "```mermaid" in result
        assert "gantt" in result

    @patch("semantiaz.servers.mermaid_mcp_server.mermaid_generator")
    def test_create_pie_chart_tool(self, mock_generator):
        """Test pie chart tool execution."""
        mock_generator.create_pie_chart.return_value = 'pie title Test Pie\n    "A" : 30'

        data = {"Category A": 30, "Category B": 70}

        result = create_pie_chart_tool(data, "Test Pie")

        assert isinstance(result, str)
        assert "Generated Mermaid pie chart" in result
        assert "```mermaid" in result
        assert "pie title" in result

    @patch("semantiaz.servers.mermaid_mcp_server.mermaid_generator")
    def test_create_class_diagram_tool(self, mock_generator):
        """Test class diagram tool execution."""
        mock_generator.create_class_diagram.return_value = "classDiagram\n    class Animal"

        classes = [
            {
                "name": "Animal",
                "attributes": [{"name": "name", "type": "string", "visibility": "+"}],
                "methods": [{"name": "makeSound", "return_type": "void", "visibility": "+"}],
            }
        ]
        relationships = [{"from": "Animal", "to": "Dog", "type": "inheritance"}]

        result = create_class_diagram_tool(classes, relationships, "Test Class")

        assert isinstance(result, str)
        assert "Generated Mermaid class diagram" in result
        assert "```mermaid" in result
        assert "classDiagram" in result

    @patch("semantiaz.servers.mermaid_mcp_server.mermaid_generator")
    def test_tool_error_handling(self, mock_generator):
        """Test error handling in tools."""
        mock_generator.create_flowchart.side_effect = Exception("Test error")

        nodes = [{"id": "A", "label": "Start"}]
        edges = []

        result = create_flowchart_tool(nodes, edges)

        assert isinstance(result, str)
        assert "Error generating flowchart" in result
        assert "Test error" in result

    def test_prompt_with_default_values(self):
        """Test prompts with default parameter values."""
        result = create_flowchart("process workflow")  # No complexity specified

        assert isinstance(result, str)
        assert "process workflow" in result
        assert "medium" in result  # Default complexity

    def test_troubleshooting_prompt_without_error(self):
        """Test troubleshooting prompt without error message."""
        result = diagram_troubleshooting("sequence")  # No error message

        assert isinstance(result, str)
        assert "sequence" in result
        assert "troubleshoot" in result.lower()
        # Should not contain error message section
        assert "Error message:" not in result

    def test_optimization_prompt_without_current_diagram(self):
        """Test optimization prompt without current diagram."""
        result = diagram_optimization("", "performance")

        assert isinstance(result, str)
        assert "performance" in result
        assert "optimize" in result.lower()
        # Should not contain current diagram section
        assert "Current diagram to optimize:" not in result

    def test_mcp_server_initialization(self):
        """Test that MCP server is properly initialized."""
        assert mcp is not None
        assert hasattr(mcp, "run")

    @patch("semantiaz.servers.mermaid_mcp_server.logger")
    def test_logging_on_error(self, mock_logger):
        """Test that errors are properly logged."""
        with patch("semantiaz.servers.mermaid_mcp_server.mermaid_generator") as mock_generator:
            mock_generator.create_flowchart.side_effect = Exception("Test error")

            nodes = [{"id": "A", "label": "Start"}]
            edges = []

            create_flowchart_tool(nodes, edges)

            mock_logger.error.assert_called_once()
