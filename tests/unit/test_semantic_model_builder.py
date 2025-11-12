#!/usr/bin/env python3

"""
Test script for the improved SemanticModelBuilder
Demonstrates fluent API for building semantic models
"""

from semantic_model import SemanticModelBuilder


def main():
    print("=== SemanticModelBuilder Test ===\n")

    # Create builder and build a model using fluent API
    builder = SemanticModelBuilder()

    # Build a retail analytics model
    model = (
        builder.create_model("retail_analytics", "Retail sales and customer analytics model")
        # Add tables
        .add_table("customers", "retail_db", "sales", "customers", "Customer master data", ["customer_id"])
        .add_table("orders", "retail_db", "sales", "orders", "Customer orders", ["order_id"])
        .add_table("products", "retail_db", "catalog", "products", "Product catalog", ["product_id"])
        # Add dimensions
        .add_dimension("customers", "customer_id", "STRING", "Unique customer identifier", unique=True)
        .add_dimension("customers", "customer_segment", "STRING", "Customer segmentation")
        .add_dimension("customers", "region", "STRING", "Customer region")
        .add_dimension("orders", "order_date", "DATE", "Order date")
        .add_dimension("orders", "order_status", "STRING", "Order status")
        .add_dimension("products", "product_name", "STRING", "Product name")
        .add_dimension("products", "category", "STRING", "Product category")
        .add_dimension(
            "products",
            "price_tier",
            "STRING",
            "Price tier classification",
            expr="CASE WHEN price < 50 THEN 'Low' WHEN price < 200 THEN 'Medium' ELSE 'High' END",
        )
        # Add relationships
        .add_relationship("customer_orders", "orders", "customers", "customer_id", "customer_id")
        .add_relationship("order_products", "orders", "products", "product_id", "product_id")
        # Add metrics
        .add_metric("total_customers", "COUNT(DISTINCT customer_id)", "Total number of customers")
        .add_metric("total_orders", "COUNT(DISTINCT order_id)", "Total number of orders")
        .add_metric("total_revenue", "SUM(order_amount)", "Total revenue")
        .add_metric("avg_order_value", "AVG(order_amount)", "Average order value")
        .add_metric("customer_lifetime_value", "total_revenue / NULLIF(total_customers, 0)", "Customer lifetime value")
        # Add verified queries
        .add_verified_query(
            "revenue_by_region",
            "What is the revenue breakdown by customer region?",
            "SELECT c.region, SUM(o.order_amount) as revenue FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.region",
        )
        .add_verified_query(
            "top_products",
            "What are the top selling products?",
            "SELECT p.product_name, COUNT(o.order_id) as order_count FROM products p JOIN orders o ON p.product_id = o.product_id GROUP BY p.product_name ORDER BY order_count DESC LIMIT 10",
            verified_by="data_analyst",
            onboarding=True,
        )
        .build()
    )

    print(f"Built model: {model.name}")
    print(f"Tables: {len(model.logical_tables)}")
    print(f"Relationships: {len(model.relationships)}")
    print(f"Metrics: {len(model.metrics)}")
    print(f"Verified queries: {len(model.verified_queries)}")

    print("\n" + "=" * 50 + "\n")

    # Validate the model
    print("Validating model...")
    validation = builder.validate_current_model()
    print(f"Valid: {validation['valid']}")
    if validation["issues"]:
        print("Issues:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
    if validation["warnings"]:
        print("Warnings:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")

    print("\n" + "=" * 50 + "\n")

    # Export to YAML
    print("Exporting to YAML...")
    yaml_content = model.to_yaml("retail_analytics_model.yaml")
    print(f"Exported {len(yaml_content)} characters to retail_analytics_model.yaml")

    # Show sample of YAML content
    print("\nSample YAML content:")
    print(yaml_content[:300] + "..." if len(yaml_content) > 300 else yaml_content)

    print("\n" + "=" * 50 + "\n")

    # Test loading from YAML
    print("Testing YAML round-trip...")
    builder2 = SemanticModelBuilder()
    builder2.load_from_yaml("retail_analytics_model.yaml")

    loaded_model = builder2.get_model("retail_analytics")
    if loaded_model:
        print(f"✓ Successfully loaded model: {loaded_model.name}")
        print(f"  Tables: {len(loaded_model.logical_tables)}")
        print(f"  Metrics: {len(loaded_model.metrics)}")
    else:
        print("✗ Failed to load model")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()
