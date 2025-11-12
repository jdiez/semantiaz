#!/usr/bin/env python3

from clinical_trial_semantic_model import clinical_model
from semantic_view_generator import SemanticViewGenerator


def main():
    generator = SemanticViewGenerator(clinical_model)

    print("=== Snowflake Semantic View Generator ===\n")

    # Generate semantic view DDL
    view_name = f"sv_{clinical_model.name}"
    semantic_view_ddl = generator.generate_semantic_view(view_name)

    print(f"Generated Snowflake SEMANTIC VIEW: {view_name}")
    print("\nDDL:")
    print(semantic_view_ddl)

    print("\n" + "=" * 60 + "\n")

    # Generate deployment script
    deployment_script = generator.generate_deployment_script()

    with open("snowflake_semantic_view_deployment.sql", "w") as f:
        f.write(deployment_script)

    print("Deployment script saved to: snowflake_semantic_view_deployment.sql")
    print(f"Script length: {len(deployment_script)} characters")


if __name__ == "__main__":
    main()
