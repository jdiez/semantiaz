"""
Clinical Trial Operations Semantic Model
Simulated semantic model for a clinical trial database
"""

from .semantic_model import (
    BaseTable,
    Columns,
    Dimension,
    LogicalTable,
    Metric,
    Relationship,
    RelationshipColumn,
    SemanticModelBuilder,
    VerifiedQuery,
)

# Create semantic model builder
builder = SemanticModelBuilder()

# Create the clinical trial semantic model
clinical_model = builder.create_model(
    name="clinical_trial_operations",
)

# Define base tables
patients_table = BaseTable(database="clinical_db", schema="operations", table="patients")

sites_table = BaseTable(database="clinical_db", schema="operations", table="sites")

visits_table = BaseTable(database="clinical_db", schema="operations", table="visits")

adverse_events_table = BaseTable(database="clinical_db", schema="operations", table="adverse_events")

recruitment_events_table = BaseTable(database="clinical_db", schema="operations", table="recruitment_events")

quality_events_table = BaseTable(database="clinical_db", schema="operations", table="quality_events")

# Define dimensions
patient_dimensions = [
    Dimension(name="patient_id", data_type="STRING", unique=True, description="Unique patient identifier"),
    Dimension(
        name="age_group",
        data_type="STRING",
        expr="CASE WHEN age < 30 THEN 'Under 30' WHEN age < 50 THEN '30-49' ELSE '50+' END",
        description="Patient age grouping",
    ),
    Dimension(name="gender", data_type="STRING", description="Patient gender"),
    Dimension(name="enrollment_status", data_type="STRING", description="Current enrollment status"),
]

site_dimensions = [
    Dimension(name="site_id", data_type="STRING", unique=True, description="Unique site identifier"),
    Dimension(name="site_country", data_type="STRING", description="Country where site is located"),
    Dimension(name="site_type", data_type="STRING", description="Type of clinical site"),
]

visit_dimensions = [
    Dimension(name="visit_type", data_type="STRING", description="Type of patient visit"),
    Dimension(name="visit_status", data_type="STRING", description="Status of the visit"),
]

ae_dimensions = [
    Dimension(name="ae_severity", data_type="STRING", description="Severity level of adverse event"),
    Dimension(name="ae_category", data_type="STRING", description="Category of adverse event"),
]

recruitment_dimensions = [
    Dimension(name="event_type", data_type="STRING", description="Type of recruitment event"),
    Dimension(
        name="target_vs_actual",
        data_type="STRING",
        expr="CASE WHEN actual_count >= target_count THEN 'Met Target' ELSE 'Below Target' END",
        description="Target achievement status",
    ),
]

quality_dimensions = [
    Dimension(name="event_type", data_type="STRING", description="Type of quality event"),
    Dimension(name="severity", data_type="STRING", description="Severity of quality issue"),
    Dimension(name="resolution_status", data_type="STRING", description="Current resolution status"),
]

# Define logical tables
patients_logical = LogicalTable(
    name="patients",
    description="Patient enrollment and demographics",
    base_table=patients_table,
    primary_key=Columns(names=["patient_id"]),
    dimensions=patient_dimensions,
)

sites_logical = LogicalTable(
    name="sites",
    description="Clinical trial sites",
    base_table=sites_table,
    primary_key=Columns(names=["site_id"]),
    dimensions=site_dimensions,
)

visits_logical = LogicalTable(
    name="visits",
    description="Patient visits and appointments",
    base_table=visits_table,
    primary_key=Columns(names=["visit_id"]),
    dimensions=visit_dimensions,
)

adverse_events_logical = LogicalTable(
    name="adverse_events",
    description="Adverse events reported during trial",
    base_table=adverse_events_table,
    primary_key=Columns(names=["ae_id"]),
    dimensions=ae_dimensions,
)

recruitment_events_logical = LogicalTable(
    name="recruitment_events",
    description="Recruitment activities and milestones",
    base_table=recruitment_events_table,
    primary_key=Columns(names=["recruitment_id"]),
    dimensions=recruitment_dimensions,
)

quality_events_logical = LogicalTable(
    name="quality_events",
    description="Quality issues and protocol deviations",
    base_table=quality_events_table,
    primary_key=Columns(names=["quality_id"]),
    dimensions=quality_dimensions,
)

# Define relationships
patient_site_rel = Relationship(
    name="patient_to_site",
    left_table="patients",
    right_table="sites",
    relationship_columns=[RelationshipColumn(left_column="site_id", right_column="site_id")],
    relationship_type="MANY_TO_ONE",
)

patient_visit_rel = Relationship(
    name="patient_to_visits",
    left_table="patients",
    right_table="visits",
    relationship_columns=[RelationshipColumn(left_column="patient_id", right_column="patient_id")],
    relationship_type="ONE_TO_MANY",
)

patient_ae_rel = Relationship(
    name="patient_to_adverse_events",
    left_table="patients",
    right_table="adverse_events",
    relationship_columns=[RelationshipColumn(left_column="patient_id", right_column="patient_id")],
    relationship_type="ONE_TO_MANY",
)

site_recruitment_rel = Relationship(
    name="site_to_recruitment_events",
    left_table="sites",
    right_table="recruitment_events",
    relationship_columns=[RelationshipColumn(left_column="site_id", right_column="site_id")],
    relationship_type="ONE_TO_MANY",
)

site_quality_rel = Relationship(
    name="site_to_quality_events",
    left_table="sites",
    right_table="quality_events",
    relationship_columns=[RelationshipColumn(left_column="site_id", right_column="site_id")],
    relationship_type="ONE_TO_MANY",
)

patient_quality_rel = Relationship(
    name="patient_to_quality_events",
    left_table="patients",
    right_table="quality_events",
    relationship_columns=[RelationshipColumn(left_column="patient_id", right_column="patient_id")],
    relationship_type="ONE_TO_MANY",
)

# Define metrics
enrollment_metrics = [
    Metric(name="total_patients", description="Total number of enrolled patients", expr="COUNT(DISTINCT patient_id)"),
    Metric(
        name="active_patients",
        description="Number of active patients",
        expr="COUNT(DISTINCT CASE WHEN enrollment_status = 'Active' THEN patient_id END)",
    ),
    Metric(
        name="enrollment_rate",
        description="Patient enrollment rate",
        expr="total_patients / NULLIF(target_enrollment, 0) * 100",
    ),
]

visit_metrics = [
    Metric(name="total_visits", description="Total number of visits", expr="COUNT(visit_id)"),
    Metric(
        name="completed_visits",
        description="Number of completed visits",
        expr="COUNT(CASE WHEN visit_status = 'Completed' THEN visit_id END)",
    ),
    Metric(
        name="visit_completion_rate",
        description="Visit completion rate",
        expr="completed_visits / NULLIF(total_visits, 0) * 100",
    ),
]

safety_metrics = [
    Metric(name="total_adverse_events", description="Total adverse events", expr="COUNT(ae_id)"),
    Metric(
        name="serious_adverse_events",
        description="Serious adverse events",
        expr="COUNT(CASE WHEN ae_severity = 'Serious' THEN ae_id END)",
    ),
    Metric(
        name="ae_rate_per_patient",
        description="Adverse events per patient",
        expr="total_adverse_events / NULLIF(total_patients, 0)",
    ),
]

recruitment_metrics = [
    Metric(name="total_recruitment_events", description="Total recruitment events", expr="COUNT(recruitment_id)"),
    Metric(
        name="recruitment_success_rate",
        description="Percentage of events meeting target",
        expr="COUNT(CASE WHEN actual_count >= target_count THEN recruitment_id END) / NULLIF(COUNT(recruitment_id), 0) * 100",
    ),
    Metric(
        name="avg_recruitment_performance",
        description="Average actual vs target recruitment",
        expr="AVG(actual_count / NULLIF(target_count, 0) * 100)",
    ),
]

quality_metrics = [
    Metric(name="total_quality_events", description="Total quality events", expr="COUNT(quality_id)"),
    Metric(
        name="major_quality_issues",
        description="Major quality issues",
        expr="COUNT(CASE WHEN severity = 'Major' THEN quality_id END)",
    ),
    Metric(
        name="quality_resolution_rate",
        description="Percentage of resolved quality issues",
        expr="COUNT(CASE WHEN resolution_status = 'Resolved' THEN quality_id END) / NULLIF(COUNT(quality_id), 0) * 100",
    ),
]

# Define verified queries
sample_queries = [
    VerifiedQuery(
        name="enrollment_by_site",
        question="How many patients are enrolled at each site?",
        sql="SELECT s.site_id, s.site_country, COUNT(p.patient_id) as patient_count FROM sites s LEFT JOIN patients p ON s.site_id = p.site_id GROUP BY s.site_id, s.site_country",
    ),
    VerifiedQuery(
        name="adverse_events_by_severity",
        question="What is the distribution of adverse events by severity?",
        sql="SELECT ae_severity, COUNT(*) as event_count FROM adverse_events GROUP BY ae_severity ORDER BY event_count DESC",
    ),
    VerifiedQuery(
        name="recruitment_performance_by_site",
        question="Which sites are meeting their recruitment targets?",
        sql="SELECT s.site_id, s.site_country, AVG(r.actual_count / NULLIF(r.target_count, 0) * 100) as avg_performance FROM sites s JOIN recruitment_events r ON s.site_id = r.site_id GROUP BY s.site_id, s.site_country ORDER BY avg_performance DESC",
    ),
    VerifiedQuery(
        name="quality_issues_by_type",
        question="What are the most common quality issues?",
        sql="SELECT event_type, severity, COUNT(*) as issue_count FROM quality_events GROUP BY event_type, severity ORDER BY issue_count DESC",
    ),
]

# Build the complete semantic model
clinical_model.logical_tables = [
    patients_logical,
    sites_logical,
    visits_logical,
    adverse_events_logical,
    recruitment_events_logical,
    quality_events_logical,
]
clinical_model.relationships = [
    patient_site_rel,
    patient_visit_rel,
    patient_ae_rel,
    site_recruitment_rel,
    site_quality_rel,
    patient_quality_rel,
]
clinical_model.metrics = enrollment_metrics + visit_metrics + safety_metrics + recruitment_metrics + quality_metrics
clinical_model.verified_queries = sample_queries

print(f"Created clinical trial semantic model with {len(clinical_model.logical_tables)} tables")
print(f"Model includes {len(clinical_model.metrics)} metrics and {len(clinical_model.relationships)} relationships")
