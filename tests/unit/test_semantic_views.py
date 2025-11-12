#!/usr/bin/env python3

"""
Test script for semantic view generation
Demonstrates how to generate and deploy semantic views
"""

from clinical_trial_semantic_model import clinical_model
from semantic_view_generator import SemanticViewGenerator


def main():
    # Initialize the view generator
    generator = SemanticViewGenerator(clinical_model)

    print("=== Semantic View Generator Test ===\n")

    # Generate all views
    print("1. Generating all semantic views...")
    views = generator.generate_all_views()

    print(f"Generated {len(views)} views:")
    for view_name in views:
        print(f"  - {view_name}")

    print("\n" + "=" * 50 + "\n")

    # Show sample view definitions
    print("2. Sample view definitions:\n")

    for view_name, view_sql in list(views.items())[:2]:  # Show first 2 views
        print(f"--- {view_name} ---")
        print(view_sql)
        print("\n" + "-" * 30 + "\n")

    # Generate deployment script
    print("3. Generating deployment script...")
    deployment_script = generator.generate_deployment_script()

    # Save deployment script to file
    with open("semantic_views_deployment.sql", "w") as f:
        f.write(deployment_script)

    print("Deployment script saved to: semantic_views_deployment.sql")
    print(f"Script length: {len(deployment_script)} characters")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()
