-- Biomarker Characterization Database
-- Create database and schemas
CREATE DATABASE IF NOT EXISTS biomarker_db;
USE DATABASE biomarker_db;

CREATE SCHEMA IF NOT EXISTS molecular;
CREATE SCHEMA IF NOT EXISTS laboratory;
CREATE SCHEMA IF NOT EXISTS clinical;
CREATE SCHEMA IF NOT EXISTS results;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Biomarkers table
USE SCHEMA molecular;
CREATE OR REPLACE TABLE biomarkers (
    biomarker_id STRING PRIMARY KEY,
    biomarker_name STRING,
    biomarker_type STRING,
    molecular_pathway STRING,
    tissue_specificity STRING,
    biomarker_class STRING,
    validation_status STRING,
    detection_method STRING
);

INSERT INTO biomarkers VALUES
('BM001', 'EGFR', 'protein', 'EGFR signaling', 'lung', 'predictive', 'Validated', 'IHC'),
('BM002', 'KRAS', 'gene', 'RAS/MAPK pathway', 'colorectal', 'predictive', 'Validated', 'NGS'),
('BM003', 'HER2', 'protein', 'HER2 signaling', 'breast', 'predictive', 'Validated', 'IHC'),
('BM004', 'PD-L1', 'protein', 'immune checkpoint', 'multiple', 'predictive', 'Validated', 'IHC'),
('BM005', 'BRCA1', 'gene', 'DNA repair', 'breast/ovarian', 'diagnostic', 'Validated', 'NGS'),
('BM006', 'PSA', 'protein', 'androgen signaling', 'prostate', 'diagnostic', 'Validated', 'ELISA'),
('BM007', 'CA-125', 'protein', 'glycoprotein', 'ovarian', 'diagnostic', 'Under Review', 'ELISA'),
('BM008', 'miR-21', 'miRNA', 'oncomiR', 'multiple', 'prognostic', 'Research', 'qPCR'),
('BM009', 'VEGF', 'protein', 'angiogenesis', 'multiple', 'prognostic', 'Under Review', 'ELISA'),
('BM010', 'TP53', 'gene', 'tumor suppressor', 'multiple', 'prognostic', 'Validated', 'NGS'),
('BM011', 'ALK', 'protein', 'ALK signaling', 'lung', 'predictive', 'Validated', 'IHC'),
('BM012', 'BRAF', 'gene', 'MAPK pathway', 'melanoma', 'predictive', 'Validated', 'NGS'),
('BM013', 'PIK3CA', 'gene', 'PI3K pathway', 'breast', 'predictive', 'Under Review', 'NGS'),
('BM014', 'MSI', 'gene', 'DNA mismatch repair', 'colorectal', 'predictive', 'Validated', 'PCR'),
('BM015', 'TMB', 'gene', 'tumor mutation burden', 'multiple', 'predictive', 'Under Review', 'NGS'),
('BM016', 'CEA', 'protein', 'glycoprotein', 'colorectal', 'diagnostic', 'Validated', 'ELISA'),
('BM017', 'AFP', 'protein', 'glycoprotein', 'liver', 'diagnostic', 'Validated', 'ELISA'),
('BM018', 'miR-155', 'miRNA', 'oncomiR', 'lymphoma', 'prognostic', 'Research', 'qPCR'),
('BM019', 'CTLA-4', 'protein', 'immune checkpoint', 'multiple', 'predictive', 'Under Review', 'IHC'),
('BM020', 'ROS1', 'protein', 'kinase signaling', 'lung', 'predictive', 'Validated', 'FISH'),
('BM021', 'NTRK', 'protein', 'kinase signaling', 'multiple', 'predictive', 'Validated', 'NGS'),
('BM022', 'IDH1', 'gene', 'metabolic pathway', 'glioma', 'diagnostic', 'Validated', 'NGS'),
('BM023', 'MGMT', 'gene', 'DNA repair', 'glioma', 'predictive', 'Validated', 'PCR'),
('BM024', 'AR', 'protein', 'androgen signaling', 'prostate', 'prognostic', 'Under Review', 'IHC'),
('BM025', 'ESR1', 'gene', 'estrogen signaling', 'breast', 'predictive', 'Under Review', 'NGS'),
('BM026', 'MET', 'protein', 'growth factor signaling', 'lung', 'predictive', 'Research', 'IHC'),
('BM027', 'FGFR', 'protein', 'growth factor signaling', 'bladder', 'predictive', 'Under Review', 'NGS'),
('BM028', 'CDK4', 'protein', 'cell cycle', 'sarcoma', 'diagnostic', 'Research', 'IHC'),
('BM029', 'PD-1', 'protein', 'immune checkpoint', 'multiple', 'predictive', 'Validated', 'IHC'),
('BM030', 'LAG-3', 'protein', 'immune checkpoint', 'multiple', 'predictive', 'Research', 'IHC');

-- Molecular Assays table
USE SCHEMA laboratory;
CREATE OR REPLACE TABLE assays (
    assay_id STRING PRIMARY KEY,
    biomarker_id STRING,
    assay_name STRING,
    assay_type STRING,
    platform STRING,
    sample_type STRING,
    assay_status STRING,
    sensitivity DECIMAL(5,2),
    specificity DECIMAL(5,2),
    detection_limit DECIMAL(10,4),
    assay_cost DECIMAL(8,2),
    FOREIGN KEY (biomarker_id) REFERENCES molecular.biomarkers(biomarker_id)
);

INSERT INTO assays VALUES
('ASY001', 'BM001', 'EGFR IHC Assay', 'IHC', 'Ventana BenchMark', 'tissue', 'Active', 95.5, 92.3, 0.1, 150.00),
('ASY002', 'BM002', 'KRAS Mutation Panel', 'NGS', 'Illumina MiSeq', 'tissue', 'Active', 98.2, 99.1, 0.05, 300.00),
('ASY003', 'BM003', 'HER2 IHC/FISH', 'IHC', 'Dako Omnis', 'tissue', 'Active', 96.8, 94.5, 0.2, 200.00),
('ASY004', 'BM004', 'PD-L1 22C3 Assay', 'IHC', 'Dako Autostainer', 'tissue', 'Active', 93.7, 91.2, 0.15, 180.00),
('ASY005', 'BM005', 'BRCA1/2 Sequencing', 'NGS', 'Ion Torrent', 'blood', 'Active', 99.5, 98.8, 0.01, 500.00),
('ASY006', 'BM006', 'PSA ELISA', 'ELISA', 'Abbott Architect', 'blood', 'Active', 97.3, 95.1, 0.02, 25.00),
('ASY007', 'BM007', 'CA-125 ELISA', 'ELISA', 'Roche Cobas', 'blood', 'Active', 89.4, 87.6, 0.5, 30.00),
('ASY008', 'BM008', 'miR-21 qPCR', 'PCR', 'Applied Biosystems', 'blood', 'Development', 92.1, 88.9, 0.001, 75.00),
('ASY009', 'BM009', 'VEGF ELISA', 'ELISA', 'R&D Systems', 'blood', 'Active', 94.2, 90.7, 0.1, 120.00),
('ASY010', 'BM010', 'TP53 Sequencing', 'NGS', 'Illumina NextSeq', 'tissue', 'Active', 97.8, 96.4, 0.02, 250.00),
('ASY011', 'BM011', 'ALK IHC Assay', 'IHC', 'Ventana BenchMark', 'tissue', 'Active', 94.8, 93.1, 0.12, 160.00),
('ASY012', 'BM012', 'BRAF Mutation Test', 'NGS', 'Illumina NextSeq', 'tissue', 'Active', 97.5, 98.2, 0.03, 280.00),
('ASY013', 'BM013', 'PIK3CA Sequencing', 'NGS', 'Ion Torrent', 'tissue', 'Development', 96.1, 95.8, 0.04, 320.00),
('ASY014', 'BM014', 'MSI PCR Panel', 'PCR', 'Applied Biosystems', 'tissue', 'Active', 98.9, 97.3, 0.02, 220.00),
('ASY015', 'BM015', 'TMB NGS Panel', 'NGS', 'Illumina NovaSeq', 'tissue', 'Development', 95.2, 94.7, 0.01, 800.00),
('ASY016', 'BM016', 'CEA ELISA', 'ELISA', 'Abbott Architect', 'blood', 'Active', 91.8, 89.4, 0.1, 35.00),
('ASY017', 'BM017', 'AFP ELISA', 'ELISA', 'Roche Cobas', 'blood', 'Active', 93.6, 91.2, 0.05, 40.00),
('ASY018', 'BM018', 'miR-155 qPCR', 'PCR', 'Applied Biosystems', 'blood', 'Research', 89.7, 87.3, 0.002, 85.00),
('ASY019', 'BM019', 'CTLA-4 IHC', 'IHC', 'Dako Autostainer', 'tissue', 'Development', 92.4, 90.8, 0.18, 190.00),
('ASY020', 'BM020', 'ROS1 FISH', 'FISH', 'Abbott Molecular', 'tissue', 'Active', 96.3, 95.1, 0.1, 350.00),
('ASY021', 'BM021', 'NTRK NGS Panel', 'NGS', 'Illumina MiSeq', 'tissue', 'Active', 97.9, 96.8, 0.02, 450.00),
('ASY022', 'BM022', 'IDH1 Sequencing', 'NGS', 'Ion Torrent', 'tissue', 'Active', 98.4, 97.6, 0.01, 380.00),
('ASY023', 'BM023', 'MGMT PCR', 'PCR', 'Applied Biosystems', 'tissue', 'Active', 94.7, 93.2, 0.05, 180.00),
('ASY024', 'BM024', 'AR IHC Assay', 'IHC', 'Ventana BenchMark', 'tissue', 'Development', 91.5, 89.8, 0.2, 170.00),
('ASY025', 'BM025', 'ESR1 Sequencing', 'NGS', 'Illumina NextSeq', 'blood', 'Development', 95.8, 94.3, 0.03, 420.00),
('ASY026', 'BM026', 'MET IHC Assay', 'IHC', 'Dako Omnis', 'tissue', 'Research', 88.9, 86.7, 0.25, 200.00),
('ASY027', 'BM027', 'FGFR NGS Panel', 'NGS', 'Ion Torrent', 'tissue', 'Development', 96.7, 95.4, 0.02, 390.00),
('ASY028', 'BM028', 'CDK4 IHC Assay', 'IHC', 'Ventana BenchMark', 'tissue', 'Research', 90.3, 88.1, 0.3, 160.00),
('ASY029', 'BM029', 'PD-1 IHC Assay', 'IHC', 'Dako Autostainer', 'tissue', 'Active', 93.1, 91.7, 0.16, 185.00),
('ASY030', 'BM030', 'LAG-3 IHC Assay', 'IHC', 'Ventana BenchMark', 'tissue', 'Research', 87.6, 85.2, 0.35, 210.00);

-- Patient Samples table
USE SCHEMA clinical;
CREATE OR REPLACE TABLE samples (
    sample_id STRING PRIMARY KEY,
    patient_id STRING,
    sample_type STRING,
    collection_site STRING,
    sample_status STRING,
    storage_condition STRING,
    collection_date DATE,
    processing_date DATE,
    sample_volume DECIMAL(6,2),
    sample_quality_score DECIMAL(4,2)
);

INSERT INTO samples VALUES
('SMP001', 'PT001', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-01-15', '2024-01-16', 10.0, 9.2),
('SMP002', 'PT001', 'tissue', 'tumor biopsy', 'Processed', 'FFPE', '2024-01-15', '2024-01-17', 2.5, 8.8),
('SMP003', 'PT002', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-01-18', '2024-01-19', 12.0, 9.5),
('SMP004', 'PT002', 'tissue', 'tumor biopsy', 'Processing', 'FFPE', '2024-01-18', NULL, 3.2, 9.1),
('SMP005', 'PT003', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-01-20', '2024-01-21', 8.5, 8.9),
('SMP006', 'PT004', 'urine', 'midstream', 'Processed', 'frozen -20C', '2024-01-22', '2024-01-23', 50.0, 7.8),
('SMP007', 'PT005', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-01-25', '2024-01-26', 11.2, 9.3),
('SMP008', 'PT005', 'tissue', 'normal adjacent', 'Processed', 'FFPE', '2024-01-25', '2024-01-27', 1.8, 8.5),
('SMP009', 'PT006', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-01-28', '2024-01-29', 9.8, 9.0),
('SMP010', 'PT007', 'tissue', 'tumor biopsy', 'Processed', 'FFPE', '2024-01-30', '2024-02-01', 4.1, 9.4),
('SMP011', 'PT008', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-02-02', '2024-02-03', 11.5, 9.1),
('SMP012', 'PT008', 'tissue', 'tumor biopsy', 'Processed', 'FFPE', '2024-02-02', '2024-02-04', 3.8, 8.9),
('SMP013', 'PT009', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-02-05', '2024-02-06', 9.2, 8.7),
('SMP014', 'PT010', 'urine', 'midstream', 'Processed', 'frozen -20C', '2024-02-08', '2024-02-09', 45.0, 8.2),
('SMP015', 'PT011', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-02-10', '2024-02-11', 10.8, 9.4),
('SMP016', 'PT012', 'tissue', 'tumor biopsy', 'Processing', 'FFPE', '2024-02-12', NULL, 2.9, 8.6),
('SMP017', 'PT013', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-02-15', '2024-02-16', 13.1, 9.0),
('SMP018', 'PT014', 'tissue', 'normal adjacent', 'Processed', 'FFPE', '2024-02-18', '2024-02-20', 2.1, 8.3),
('SMP019', 'PT015', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-02-22', '2024-02-23', 8.9, 8.8),
('SMP020', 'PT016', 'tissue', 'tumor biopsy', 'Processed', 'FFPE', '2024-02-25', '2024-02-27', 4.5, 9.2),
('SMP021', 'PT017', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-02-28', '2024-03-01', 11.7, 9.3),
('SMP022', 'PT018', 'urine', 'midstream', 'Processed', 'frozen -20C', '2024-03-02', '2024-03-03', 52.0, 7.9),
('SMP023', 'PT019', 'blood', 'peripheral', 'Processing', 'frozen -80C', '2024-03-05', NULL, 9.6, 8.5),
('SMP024', 'PT020', 'tissue', 'tumor biopsy', 'Processed', 'FFPE', '2024-03-08', '2024-03-10', 3.4, 8.7),
('SMP025', 'PT021', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-03-12', '2024-03-13', 12.3, 9.1),
('SMP026', 'PT022', 'tissue', 'normal adjacent', 'Processed', 'FFPE', '2024-03-15', '2024-03-17', 1.9, 8.4),
('SMP027', 'PT023', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-03-18', '2024-03-19', 10.4, 8.9),
('SMP028', 'PT024', 'tissue', 'tumor biopsy', 'Processed', 'FFPE', '2024-03-22', '2024-03-24', 4.2, 9.0),
('SMP029', 'PT025', 'blood', 'peripheral', 'Processed', 'frozen -80C', '2024-03-25', '2024-03-26', 8.7, 8.6),
('SMP030', 'PT026', 'urine', 'midstream', 'Processing', 'frozen -20C', '2024-03-28', NULL, 48.0, 7.5);

-- Biomarker Measurements table
USE SCHEMA results;
CREATE OR REPLACE TABLE measurements (
    measurement_id STRING PRIMARY KEY,
    sample_id STRING,
    biomarker_id STRING,
    assay_id STRING,
    measurement_status STRING,
    measurement_unit STRING,
    reference_range STRING,
    measurement_date DATE,
    measured_value DECIMAL(12,4),
    fold_change DECIMAL(8,3),
    p_value DECIMAL(8,6),
    confidence_interval_lower DECIMAL(8,3),
    confidence_interval_upper DECIMAL(8,3),
    FOREIGN KEY (sample_id) REFERENCES clinical.samples(sample_id),
    FOREIGN KEY (biomarker_id) REFERENCES molecular.biomarkers(biomarker_id),
    FOREIGN KEY (assay_id) REFERENCES laboratory.assays(assay_id)
);

INSERT INTO measurements VALUES
('MSR001', 'SMP001', 'BM006', 'ASY006', 'completed', 'ng/mL', '0-4.0', '2024-01-17', 12.5, 3.125, 0.001234, 2.8, 3.5),
('MSR002', 'SMP002', 'BM001', 'ASY001', 'completed', 'H-score', '0-300', '2024-01-18', 280.0, 2.8, 0.000567, 2.5, 3.1),
('MSR003', 'SMP003', 'BM005', 'ASY005', 'completed', 'mutation', 'wildtype', '2024-01-20', 1.0, NULL, 0.045678, NULL, NULL),
('MSR004', 'SMP005', 'BM007', 'ASY007', 'completed', 'U/mL', '0-35', '2024-01-22', 85.3, 2.437, 0.002345, 2.1, 2.8),
('MSR005', 'SMP006', 'BM008', 'ASY008', 'completed', 'fold change', '1.0', '2024-01-24', 4.2, 4.2, 0.012345, 3.8, 4.6),
('MSR006', 'SMP007', 'BM009', 'ASY009', 'completed', 'pg/mL', '0-150', '2024-01-27', 320.8, 2.139, 0.003456, 1.9, 2.4),
('MSR007', 'SMP008', 'BM003', 'ASY003', 'completed', 'IHC score', '0-3+', '2024-01-28', 3.0, NULL, 0.000123, NULL, NULL),
('MSR008', 'SMP009', 'BM004', 'ASY004', 'completed', 'TPS %', '0-100', '2024-01-30', 65.0, NULL, 0.001789, NULL, NULL),
('MSR009', 'SMP010', 'BM010', 'ASY010', 'completed', 'mutation', 'wildtype', '2024-02-02', 1.0, NULL, 0.023456, NULL, NULL),
('MSR010', 'SMP001', 'BM002', 'ASY002', 'pending', 'mutation', 'wildtype', NULL, NULL, NULL, NULL, NULL, NULL),
('MSR011', 'SMP011', 'BM011', 'ASY011', 'completed', 'IHC score', '0-3+', '2024-02-04', 2.0, NULL, 0.034567, NULL, NULL),
('MSR012', 'SMP012', 'BM012', 'ASY012', 'completed', 'mutation', 'wildtype', '2024-02-05', 1.0, NULL, 0.012789, NULL, NULL),
('MSR013', 'SMP013', 'BM016', 'ASY016', 'completed', 'ng/mL', '0-5.0', '2024-02-07', 18.7, 3.74, 0.001567, 3.2, 4.3),
('MSR014', 'SMP014', 'BM017', 'ASY017', 'completed', 'ng/mL', '0-10', '2024-02-10', 45.2, 4.52, 0.000789, 4.1, 4.9),
('MSR015', 'SMP015', 'BM018', 'ASY018', 'completed', 'fold change', '1.0', '2024-02-12', 6.8, 6.8, 0.008901, 6.2, 7.4),
('MSR016', 'SMP017', 'BM020', 'ASY020', 'completed', 'FISH ratio', '>2.0', '2024-02-17', 3.5, NULL, 0.002345, NULL, NULL),
('MSR017', 'SMP018', 'BM021', 'ASY021', 'completed', 'mutation', 'wildtype', '2024-02-21', 1.0, NULL, 0.015678, NULL, NULL),
('MSR018', 'SMP019', 'BM022', 'ASY022', 'completed', 'mutation', 'wildtype', '2024-02-24', 1.0, NULL, 0.007890, NULL, NULL),
('MSR019', 'SMP020', 'BM023', 'ASY023', 'completed', 'methylation %', '0-100', '2024-02-28', 25.8, NULL, 0.045123, NULL, NULL),
('MSR020', 'SMP021', 'BM029', 'ASY029', 'completed', 'TPS %', '0-100', '2024-03-02', 42.0, NULL, 0.003456, NULL, NULL),
('MSR021', 'SMP022', 'BM006', 'ASY006', 'completed', 'ng/mL', '0-4.0', '2024-03-04', 8.9, 2.225, 0.012345, 1.9, 2.6),
('MSR022', 'SMP024', 'BM013', 'ASY013', 'completed', 'mutation', 'wildtype', '2024-03-11', 1.0, NULL, 0.023456, NULL, NULL),
('MSR023', 'SMP025', 'BM014', 'ASY014', 'completed', 'MSI status', 'MSS', '2024-03-14', 1.0, NULL, 0.001234, NULL, NULL),
('MSR024', 'SMP026', 'BM015', 'ASY015', 'completed', 'mutations/Mb', '0-20', '2024-03-18', 12.4, NULL, 0.034567, NULL, NULL),
('MSR025', 'SMP027', 'BM024', 'ASY024', 'completed', 'H-score', '0-300', '2024-03-20', 180.0, 1.8, 0.007890, 1.5, 2.1),
('MSR026', 'SMP028', 'BM025', 'ASY025', 'completed', 'mutation', 'wildtype', '2024-03-25', 1.0, NULL, 0.045678, NULL, NULL),
('MSR027', 'SMP029', 'BM026', 'ASY026', 'completed', 'IHC score', '0-3+', '2024-03-27', 1.0, NULL, 0.012345, NULL, NULL),
('MSR028', 'SMP011', 'BM027', 'ASY027', 'pending', 'mutation', 'wildtype', NULL, NULL, NULL, NULL, NULL, NULL),
('MSR029', 'SMP013', 'BM028', 'ASY028', 'pending', 'IHC score', '0-3+', NULL, NULL, NULL, NULL, NULL, NULL),
('MSR030', 'SMP015', 'BM030', 'ASY030', 'pending', 'TPS %', '0-100', NULL, NULL, NULL, NULL, NULL, NULL);

-- Clinical Studies table
CREATE OR REPLACE TABLE studies (
    study_id STRING PRIMARY KEY,
    study_name STRING,
    study_type STRING,
    disease_indication STRING,
    study_phase STRING,
    study_status STRING,
    primary_endpoint STRING,
    study_start_date DATE,
    study_end_date DATE,
    enrolled_patients INTEGER,
    study_duration_months INTEGER
);

INSERT INTO studies VALUES
('STD001', 'Lung Cancer Biomarker Study', 'cohort', 'NSCLC', 'Phase II', 'Active', 'Overall Survival', '2023-06-01', '2025-12-31', 150, 30),
('STD002', 'Breast Cancer Precision Medicine', 'RCT', 'Breast Cancer', 'Phase III', 'Active', 'Progression Free Survival', '2023-01-15', '2026-06-30', 300, 42),
('STD003', 'Prostate Cancer Screening', 'case-control', 'Prostate Cancer', 'Observational', 'Completed', 'Diagnostic Accuracy', '2022-03-01', '2024-02-29', 500, 24),
('STD004', 'Ovarian Cancer Early Detection', 'cohort', 'Ovarian Cancer', 'Phase I', 'Active', 'Sensitivity/Specificity', '2024-01-01', '2025-12-31', 100, 24),
('STD005', 'Multi-Cancer Liquid Biopsy', 'cohort', 'Multiple Cancers', 'Phase II', 'Recruiting', 'Detection Rate', '2024-02-01', '2026-01-31', 200, 24),
('STD006', 'Melanoma Immunotherapy Biomarkers', 'RCT', 'Melanoma', 'Phase III', 'Active', 'Response Rate', '2023-09-01', '2026-08-31', 250, 36),
('STD007', 'Colorectal Cancer MSI Study', 'cohort', 'Colorectal Cancer', 'Phase II', 'Active', 'Progression Free Survival', '2023-12-01', '2025-11-30', 180, 24),
('STD008', 'Glioma IDH Mutation Analysis', 'case-control', 'Glioma', 'Observational', 'Recruiting', 'Diagnostic Accuracy', '2024-03-01', '2025-02-28', 120, 12),
('STD009', 'Pan-Cancer TMB Validation', 'cohort', 'Multiple Cancers', 'Phase II', 'Active', 'Response Rate', '2023-07-15', '2025-07-14', 350, 24),
('STD010', 'Liver Cancer AFP Screening', 'cohort', 'Hepatocellular Carcinoma', 'Observational', 'Completed', 'Early Detection Rate', '2022-01-01', '2023-12-31', 400, 24),
('STD011', 'Sarcoma CDK4 Expression', 'case-control', 'Sarcoma', 'Phase I', 'Recruiting', 'Biomarker Prevalence', '2024-01-15', '2024-12-31', 80, 12),
('STD012', 'Bladder Cancer FGFR Study', 'RCT', 'Bladder Cancer', 'Phase II', 'Active', 'Response Rate', '2023-10-01', '2025-09-30', 160, 24),
('STD013', 'Lymphoma miRNA Profiling', 'cohort', 'Lymphoma', 'Observational', 'Active', 'Prognostic Value', '2023-05-01', '2025-04-30', 140, 24),
('STD014', 'Immune Checkpoint Combination', 'RCT', 'Multiple Cancers', 'Phase III', 'Recruiting', 'Overall Survival', '2024-02-15', '2027-02-14', 450, 36),
('STD015', 'Precision Oncology Platform', 'cohort', 'Multiple Cancers', 'Phase II', 'Active', 'Treatment Selection Accuracy', '2023-11-01', '2025-10-31', 300, 24);

-- Patient Outcomes table
CREATE OR REPLACE TABLE outcomes (
    outcome_id STRING PRIMARY KEY,
    patient_id STRING,
    study_id STRING,
    outcome_type STRING,
    outcome_status STRING,
    treatment_response STRING,
    disease_progression STRING,
    baseline_date DATE,
    last_followup_date DATE,
    event_date DATE,
    survival_time_days INTEGER,
    progression_free_survival_days INTEGER,
    hazard_ratio DECIMAL(6,3),
    overall_survival_probability DECIMAL(5,3),
    FOREIGN KEY (study_id) REFERENCES studies(study_id)
);

INSERT INTO outcomes VALUES
('OUT001', 'PT001', 'STD001', 'survival', 'event', 'Partial Response', 'Progressive Disease', '2023-06-15', '2024-01-15', '2024-01-10', 214, 180, 1.25, 0.65),
('OUT002', 'PT002', 'STD002', 'survival', 'censored', 'Complete Response', 'Stable Disease', '2023-02-01', '2024-02-01', NULL, 365, 365, 0.75, 0.85),
('OUT003', 'PT003', 'STD003', 'response', 'event', 'No Response', 'Progressive Disease', '2022-04-01', '2023-12-01', '2023-11-15', 593, 228, 1.45, 0.45),
('OUT004', 'PT004', 'STD001', 'survival', 'censored', 'Stable Disease', 'Stable Disease', '2023-07-01', '2024-02-01', NULL, 215, 215, 0.95, 0.75),
('OUT005', 'PT005', 'STD002', 'response', 'event', 'Partial Response', 'Progressive Disease', '2023-03-15', '2024-01-20', '2024-01-15', 306, 280, 1.15, 0.70),
('OUT006', 'PT006', 'STD004', 'survival', 'ongoing', 'Complete Response', 'Stable Disease', '2024-01-15', '2024-02-15', NULL, 31, 31, 0.65, 0.90),
('OUT007', 'PT007', 'STD005', 'response', 'ongoing', 'Partial Response', 'Stable Disease', '2024-02-01', '2024-02-15', NULL, 14, 14, 0.85, 0.80),
('OUT008', 'PT008', 'STD006', 'survival', 'event', 'Complete Response', 'Stable Disease', '2023-09-15', '2024-03-15', '2024-03-10', 177, 177, 0.55, 0.88),
('OUT009', 'PT009', 'STD007', 'response', 'censored', 'Partial Response', 'Stable Disease', '2023-12-15', '2024-03-15', NULL, 91, 91, 0.82, 0.78),
('OUT010', 'PT010', 'STD008', 'survival', 'ongoing', 'Stable Disease', 'Stable Disease', '2024-03-15', '2024-03-30', NULL, 15, 15, 1.05, 0.72),
('OUT011', 'PT011', 'STD009', 'response', 'event', 'Complete Response', 'Progressive Disease', '2023-08-01', '2024-02-01', '2024-01-25', 177, 147, 0.68, 0.82),
('OUT012', 'PT012', 'STD010', 'survival', 'event', 'No Response', 'Progressive Disease', '2022-02-01', '2023-10-15', '2023-10-01', 607, 242, 1.38, 0.48),
('OUT013', 'PT013', 'STD011', 'response', 'ongoing', 'Partial Response', 'Stable Disease', '2024-02-01', '2024-03-15', NULL, 43, 43, 0.91, 0.76),
('OUT014', 'PT014', 'STD012', 'survival', 'censored', 'Complete Response', 'Stable Disease', '2023-10-15', '2024-03-15', NULL, 152, 152, 0.72, 0.84),
('OUT015', 'PT015', 'STD013', 'response', 'event', 'Partial Response', 'Progressive Disease', '2023-05-15', '2024-01-15', '2024-01-10', 240, 210, 1.12, 0.68),
('OUT016', 'PT016', 'STD014', 'survival', 'ongoing', 'Complete Response', 'Stable Disease', '2024-03-01', '2024-03-30', NULL, 29, 29, 0.58, 0.92),
('OUT017', 'PT017', 'STD015', 'response', 'censored', 'Partial Response', 'Stable Disease', '2023-11-15', '2024-03-15', NULL, 121, 121, 0.87, 0.79),
('OUT018', 'PT018', 'STD001', 'survival', 'event', 'No Response', 'Progressive Disease', '2023-06-30', '2024-02-28', '2024-02-20', 235, 185, 1.42, 0.52),
('OUT019', 'PT019', 'STD002', 'response', 'ongoing', 'Stable Disease', 'Stable Disease', '2023-02-15', '2024-03-15', NULL, 394, 394, 0.98, 0.74),
('OUT020', 'PT020', 'STD003', 'survival', 'event', 'Partial Response', 'Progressive Disease', '2022-04-15', '2023-11-30', '2023-11-15', 579, 214, 1.28, 0.58),
('OUT021', 'PT021', 'STD004', 'response', 'ongoing', 'Complete Response', 'Stable Disease', '2024-01-30', '2024-03-30', NULL, 60, 60, 0.62, 0.89);

-- Biomarker Associations table
USE SCHEMA analytics;
CREATE OR REPLACE TABLE associations (
    association_id STRING PRIMARY KEY,
    biomarker_id STRING,
    outcome_id STRING,
    association_type STRING,
    analysis_method STRING,
    significance_level STRING,
    correlation_coefficient DECIMAL(6,3),
    p_value DECIMAL(8,6),
    odds_ratio DECIMAL(6,3),
    auc_score DECIMAL(5,3),
    sensitivity DECIMAL(5,2),
    specificity DECIMAL(5,2),
    FOREIGN KEY (biomarker_id) REFERENCES molecular.biomarkers(biomarker_id),
    FOREIGN KEY (outcome_id) REFERENCES clinical.outcomes(outcome_id)
);

INSERT INTO associations VALUES
('ASC001', 'BM001', 'OUT001', 'predictive', 'logistic regression', '0.05', 0.65, 0.001234, 2.45, 0.82, 78.5, 85.2),
('ASC002', 'BM002', 'OUT002', 'predictive', 'cox regression', '0.01', -0.42, 0.000567, 0.58, 0.75, 82.1, 79.3),
('ASC003', 'BM003', 'OUT003', 'prognostic', 'kaplan-meier', '0.05', 0.38, 0.045678, 1.85, 0.68, 71.4, 73.8),
('ASC004', 'BM004', 'OUT004', 'predictive', 'logistic regression', '0.01', 0.72, 0.002345, 3.12, 0.89, 86.7, 91.2),
('ASC005', 'BM005', 'OUT005', 'diagnostic', 'roc analysis', '0.001', 0.58, 0.000123, 2.78, 0.94, 92.5, 88.9),
('ASC006', 'BM006', 'OUT006', 'diagnostic', 'roc analysis', '0.001', 0.81, 0.000089, 4.25, 0.96, 94.2, 92.1),
('ASC007', 'BM007', 'OUT007', 'prognostic', 'cox regression', '0.05', 0.45, 0.023456, 1.95, 0.73, 75.8, 77.4),
('ASC008', 'BM011', 'OUT008', 'predictive', 'logistic regression', '0.01', 0.68, 0.001567, 2.89, 0.85, 81.2, 87.4),
('ASC009', 'BM012', 'OUT009', 'predictive', 'cox regression', '0.05', -0.38, 0.034567, 0.62, 0.72, 76.8, 78.9),
('ASC010', 'BM014', 'OUT010', 'predictive', 'chi-square', '0.01', 0.52, 0.007890, 2.15, 0.78, 74.3, 82.1),
('ASC011', 'BM015', 'OUT011', 'predictive', 'logistic regression', '0.001', 0.74, 0.000234, 3.45, 0.91, 88.9, 93.2),
('ASC012', 'BM016', 'OUT012', 'diagnostic', 'roc analysis', '0.05', 0.42, 0.012345, 1.78, 0.69, 68.7, 75.4),
('ASC013', 'BM017', 'OUT013', 'diagnostic', 'roc analysis', '0.001', 0.79, 0.000456, 3.98, 0.93, 91.5, 89.8),
('ASC014', 'BM020', 'OUT014', 'predictive', 'logistic regression', '0.01', 0.61, 0.003456, 2.67, 0.83, 79.4, 86.1),
('ASC015', 'BM021', 'OUT015', 'predictive', 'cox regression', '0.05', -0.35, 0.023456, 0.71, 0.74, 72.1, 80.3),
('ASC016', 'BM022', 'OUT016', 'diagnostic', 'chi-square', '0.001', 0.86, 0.000123, 4.78, 0.97, 95.2, 94.6),
('ASC017', 'BM023', 'OUT017', 'predictive', 'logistic regression', '0.01', 0.55, 0.004567, 2.34, 0.81, 77.8, 84.2),
('ASC018', 'BM029', 'OUT018', 'predictive', 'cox regression', '0.05', 0.48, 0.015678, 2.12, 0.76, 73.5, 81.7),
('ASC019', 'BM013', 'OUT019', 'predictive', 'logistic regression', '0.01', -0.41, 0.006789, 0.59, 0.73, 70.9, 77.8),
('ASC020', 'BM024', 'OUT020', 'prognostic', 'kaplan-meier', '0.05', 0.39, 0.034567, 1.92, 0.71, 69.2, 76.5),
('ASC021', 'BM025', 'OUT021', 'predictive', 'logistic regression', '0.01', 0.63, 0.002345, 2.71, 0.84, 80.1, 86.8);
