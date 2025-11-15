"""FastMCP Server for Mermaid diagram generation with comprehensive tools and resources.

This server provides tools for generating various types of Mermaid diagrams,
along with prompts for user interaction and resources containing Mermaid specifications.
"""

import logging

from fastmcp import FastMCP

from ..plotting.mermaid_diagrams import Edge, Entity, MermaidDiagrams, Node, Relationship

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the server and Mermaid generator
mcp = FastMCP("mermaid-diagram-server")
mermaid_generator = MermaidDiagrams()

# Mermaid specification resources
MERMAID_SPECS = {
    "flowchart_spec": """
# Mermaid Flowchart Specification

## Syntax
```
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[End]
    C --> D
```

## Node Shapes
- Rectangle: `A[Text]`
- Circle: `A((Text))`
- Diamond: `A{Text}`
- Hexagon: `A{{Text}}`
- Stadium: `A([Text])`

## Arrows
- Solid: `-->`
- Dashed: `-.->`
- Dotted: `..->`
- Thick: `==>`

## Directions
- TD: Top Down
- LR: Left Right
- BT: Bottom Top
- RL: Right Left
""",
    "er_diagram_spec": """
# Mermaid ER Diagram Specification

## Syntax
```
erDiagram
    CUSTOMER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        int customer_id FK
        date order_date
    }
    CUSTOMER ||--o{ ORDER : places
```

## Cardinality
- `||--o{` : One to many
- `||--||` : One to one
- `}o--o{` : Many to many
- `||--o|` : One to zero or one

## Attribute Types
- PK: Primary Key
- FK: Foreign Key
- UK: Unique Key
""",
    "sequence_spec": """
# Mermaid Sequence Diagram Specification

## Syntax
```
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob
    B-->>A: Hello Alice
    A->>B: How are you?
    B-->>A: I'm good, thanks!
```

## Message Types
- `->` : Synchronous message
- `->>` : Asynchronous message
- `-->>` : Return message
- `-x` : Lost message
""",
    "gantt_spec": """
# Mermaid Gantt Chart Specification

## Syntax
```
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Planning
    Research    :done, research, 2024-01-01, 2024-01-15
    Design      :active, design, 2024-01-10, 2024-01-25
    section Development
    Coding      :coding, after design, 30d
    Testing     :testing, after coding, 15d
```

## Task Status
- `:done` : Completed
- `:active` : In progress
- `:crit` : Critical path
""",
    "class_diagram_spec": """
# Mermaid Class Diagram Specification

## Syntax
```
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound() void
    }
    class Dog {
        +String breed
        +bark() void
    }
    Animal <|-- Dog
```

## Visibility
- `+` : Public
- `-` : Private
- `#` : Protected
- `~` : Package

## Relationships
- `<|--` : Inheritance
- `*--` : Composition
- `o--` : Aggregation
- `-->` : Association
""",
}


# Register resources
for spec_name, content in MERMAID_SPECS.items():
    mcp.add_resource(
        uri=f"mermaid://{spec_name}",
        name=f"Mermaid {spec_name.replace('_', ' ').title()}",
        description=f"Specification and examples for {spec_name.replace('_', ' ')}",
        text=content,
    )


@mcp.prompt()
def create_flowchart(purpose: str, complexity: str = "medium") -> str:
    """Guide user through creating a flowchart diagram."""
    return f"""I'll help you create a flowchart for {purpose}.

Let's start by identifying the key steps:

1. **Start/End Points**: What triggers the process and how does it conclude?
2. **Decision Points**: Where are choices or conditions evaluated?
3. **Process Steps**: What actions or operations occur?
4. **Flow Direction**: How do steps connect to each other?

For a {complexity} complexity diagram, consider:
- Simple: 3-7 nodes with linear flow
- Medium: 8-15 nodes with some branching
- Complex: 15+ nodes with multiple decision paths

Please describe:
1. The starting point of your process
2. The main steps involved
3. Any decision points or branches
4. The ending point(s)

I'll then generate the appropriate Mermaid flowchart syntax for you."""


@mcp.prompt()
def create_er_diagram(domain: str, entities: str = "several") -> str:
    """Guide user through creating an ER diagram."""
    return f"""I'll help you create an ER diagram for {domain} with {entities} entities.

Let's identify the components:

1. **Entities**: What are the main objects/concepts?
   - Examples: Customer, Order, Product, User, etc.

2. **Attributes**: What properties does each entity have?
   - Include data types (int, string, date, etc.)
   - Mark primary keys (PK) and foreign keys (FK)

3. **Relationships**: How do entities connect?
   - One-to-one (||--||)
   - One-to-many (||--o{{)
   - Many-to-many (}}o--o{{)

Please provide:
1. List of main entities in your {domain}
2. Key attributes for each entity
3. How entities relate to each other
4. Any constraints or special relationships

I'll generate the Mermaid ER diagram syntax based on your input."""


@mcp.prompt()
def diagram_troubleshooting(diagram_type: str, error_message: str = "") -> str:
    """Help troubleshoot Mermaid diagram rendering issues."""
    error_section = f"\nError message: {error_message}" if error_message else ""
    return f"""I'll help troubleshoot your {diagram_type} diagram.

Common issues and solutions:

**Syntax Errors:**
- Check for missing quotes around labels with spaces
- Verify proper arrow syntax (-->, -.>, etc.)
- Ensure proper indentation (4 spaces recommended)

**Rendering Issues:**
- Special characters may need escaping
- Very long labels might need line breaks
- Complex diagrams may need simplification

**Performance:**
- Large diagrams (50+ nodes) may render slowly
- Consider breaking into multiple smaller diagrams{error_section}

Please share:
1. Your current Mermaid code
2. What you expected to see
3. What actually happened
4. Any error messages

I'll help identify and fix the issue."""


@mcp.prompt()
def diagram_optimization(current_diagram: str, goals: str = "general improvement") -> str:
    """Suggest improvements for existing Mermaid diagrams."""
    current_section = f"\nCurrent diagram to optimize: {current_diagram}" if current_diagram else ""
    return f"""I'll help optimize your Mermaid diagram for {goals}.

Optimization strategies:

**Readability:**
- Use clear, concise labels
- Group related elements
- Maintain consistent styling
- Add appropriate spacing

**Aesthetics:**
- Apply consistent color schemes
- Use appropriate node shapes
- Balance diagram layout
- Add styling classes

**Performance:**
- Minimize crossing lines
- Reduce diagram complexity
- Use subgraphs for organization{current_section}

Please share:
1. Your current Mermaid diagram code
2. Specific areas you want to improve
3. Your target audience
4. Any constraints or requirements

I'll provide specific optimization suggestions."""


@mcp.tool()
def create_flowchart_tool(nodes: list[dict], edges: list[dict], direction: str = "TD", title: str | None = None) -> str:
    """Create a Mermaid flowchart diagram.

    Args:
        nodes: List of nodes with id, label, and optional shape
        edges: List of edges with from_node, to_node, optional label and style
        direction: Flow direction (TD, LR, BT, RL)
        title: Optional diagram title
    """
    try:
        node_objects = [Node(**node) for node in nodes]
        edge_objects = [Edge(**edge) for edge in edges]

        diagram = mermaid_generator.create_flowchart(
            nodes=node_objects, edges=edge_objects, direction=direction, title=title
        )

        return f"Generated Mermaid flowchart:\n\n```mermaid\n{diagram}\n```"
    except Exception as e:
        logger.exception("Error creating flowchart")
        return f"Error generating flowchart: {e!s}"


@mcp.tool()
def create_er_diagram_tool(
    entities: list[dict], relationships: list[dict] | None = None, title: str | None = None
) -> str:
    """Create a Mermaid ER diagram.

    Args:
        entities: List of entities with name and attributes
        relationships: Optional list of relationships between entities
        title: Optional diagram title
    """
    try:
        entity_objects = [Entity(**entity) for entity in entities]
        relationship_objects = [Relationship(**rel) for rel in (relationships or [])]

        diagram = mermaid_generator.create_er_diagram(
            entities=entity_objects, relationships=relationship_objects, title=title
        )

        return f"Generated Mermaid ER diagram:\n\n```mermaid\n{diagram}\n```"
    except Exception as e:
        logger.exception("Error creating ER diagram")
        return f"Error generating ER diagram: {e!s}"


@mcp.tool()
def create_sequence_diagram_tool(participants: list[str], messages: list[dict], title: str | None = None) -> str:
    """Create a Mermaid sequence diagram.

    Args:
        participants: List of participant names
        messages: List of messages with from, to, message, and optional type
        title: Optional diagram title
    """
    try:
        diagram = mermaid_generator.create_sequence_diagram(participants=participants, messages=messages, title=title)

        return f"Generated Mermaid sequence diagram:\n\n```mermaid\n{diagram}\n```"
    except Exception as e:
        logger.exception("Error creating sequence diagram")
        return f"Error generating sequence diagram: {e!s}"


@mcp.tool()
def create_gantt_chart_tool(tasks: list[dict], title: str | None = None) -> str:
    """Create a Mermaid Gantt chart.

    Args:
        tasks: List of tasks with name, id, start, duration, optional section and status
        title: Optional chart title
    """
    try:
        diagram = mermaid_generator.create_gantt_chart(tasks=tasks, title=title)

        return f"Generated Mermaid Gantt chart:\n\n```mermaid\n{diagram}\n```"
    except Exception as e:
        logger.exception("Error creating Gantt chart")
        return f"Error generating Gantt chart: {e!s}"


@mcp.tool()
def create_pie_chart_tool(data: dict[str, float], title: str | None = None) -> str:
    """Create a Mermaid pie chart.

    Args:
        data: Dictionary mapping labels to values
        title: Optional chart title
    """
    try:
        diagram = mermaid_generator.create_pie_chart(data=data, title=title)

        return f"Generated Mermaid pie chart:\n\n```mermaid\n{diagram}\n```"
    except Exception as e:
        logger.exception("Error creating pie chart")
        return f"Error generating pie chart: {e!s}"


@mcp.tool()
def create_class_diagram_tool(
    classes: list[dict], relationships: list[dict] | None = None, title: str | None = None
) -> str:
    """Create a Mermaid class diagram.

    Args:
        classes: List of classes with name, optional attributes and methods
        relationships: Optional list of relationships between classes
        title: Optional diagram title
    """
    try:
        diagram = mermaid_generator.create_class_diagram(
            classes=classes, relationships=relationships or [], title=title
        )

        return f"Generated Mermaid class diagram:\n\n```mermaid\n{diagram}\n```"
    except Exception as e:
        logger.exception("Error creating class diagram")
        return f"Error generating class diagram: {e!s}"


if __name__ == "__main__":
    mcp.run()
