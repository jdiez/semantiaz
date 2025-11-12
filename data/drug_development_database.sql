-- Drug Development Pipeline Database
-- Create database and schemas
CREATE DATABASE IF NOT EXISTS pharma_db;
USE DATABASE pharma_db;

CREATE SCHEMA IF NOT EXISTS discovery;
CREATE SCHEMA IF NOT EXISTS preclinical;
CREATE SCHEMA IF NOT EXISTS clinical;
CREATE SCHEMA IF NOT EXISTS regulatory;
CREATE SCHEMA IF NOT EXISTS manufacturing;
CREATE SCHEMA IF NOT EXISTS commercial;

-- Targets table
USE SCHEMA discovery;
CREATE OR REPLACE TABLE targets (
    target_id STRING PRIMARY KEY,
    target_name STRING,
    target_type STRING,
    disease_indication STRING,
    validation_status STRING
);

INSERT INTO targets VALUES
('TGT001', 'EGFR', 'receptor', 'Non-Small Cell Lung Cancer', 'Validated'),
('TGT002', 'HER2', 'receptor', 'Breast Cancer', 'Validated'),
('TGT003', 'VEGFR2', 'receptor', 'Colorectal Cancer', 'Validated'),
('TGT004', 'PD-1', 'receptor', 'Melanoma', 'Validated'),
('TGT005', 'BRAF', 'enzyme', 'Melanoma', 'Validated'),
('TGT006', 'ALK', 'enzyme', 'Non-Small Cell Lung Cancer', 'Validated'),
('TGT007', 'CDK4/6', 'enzyme', 'Breast Cancer', 'Validated'),
('TGT008', 'PARP', 'enzyme', 'Ovarian Cancer', 'Under Review'),
('TGT009', 'mTOR', 'enzyme', 'Renal Cell Carcinoma', 'Under Review'),
('TGT010', 'JAK2', 'enzyme', 'Myelofibrosis', 'Research');

-- Compounds table
CREATE OR REPLACE TABLE compounds (
    compound_id STRING PRIMARY KEY,
    target_id STRING,
    compound_name STRING,
    molecular_formula STRING,
    therapeutic_area STRING,
    discovery_method STRING,
    compound_status STRING,
    discovery_date DATE,
    FOREIGN KEY (target_id) REFERENCES targets(target_id)
);

INSERT INTO compounds VALUES
('CMP001', 'TGT001', 'Erlotinib', 'C22H23N3O4', 'Oncology', 'Structure-Based Drug Design', 'Approved', '1995-03-15'),
('CMP002', 'TGT002', 'Trastuzumab', 'C6470H10012N1726O2013S42', 'Oncology', 'Monoclonal Antibody', 'Approved', '1992-08-20'),
('CMP003', 'TGT003', 'Bevacizumab', 'C6538H10072N1716O2036S44', 'Oncology', 'Monoclonal Antibody', 'Approved', '1993-11-10'),
('CMP004', 'TGT004', 'Pembrolizumab', 'C6562H10066N1722O2036S44', 'Oncology', 'Monoclonal Antibody', 'Approved', '2006-05-12'),
('CMP005', 'TGT005', 'Vemurafenib', 'C23H18ClF2N3O3S', 'Oncology', 'High-Throughput Screening', 'Approved', '2005-09-08'),
('CMP006', 'TGT006', 'Crizotinib', 'C21H22Cl2FN5O', 'Oncology', 'Structure-Based Drug Design', 'Approved', '2004-02-18'),
('CMP007', 'TGT007', 'Palbociclib', 'C24H29N7O2', 'Oncology', 'Rational Drug Design', 'Approved', '2007-12-03'),
('CMP008', 'TGT008', 'Olaparib', 'C24H23FN4O3', 'Oncology', 'Structure-Based Drug Design', 'Approved', '2003-07-25'),
('CMP009', 'TGT009', 'Everolimus', 'C53H83NO14', 'Oncology', 'Natural Product Derivation', 'Approved', '1999-04-14'),
('CMP010', 'TGT010', 'Ruxolitinib', 'C17H18N6', 'Hematology', 'Structure-Based Drug Design', 'Approved', '2008-01-30'),
('CMP011', 'TGT001', 'Compound-X1', 'C25H28N4O5', 'Oncology', 'AI-Driven Discovery', 'Phase II', '2020-06-15'),
('CMP012', 'TGT008', 'Compound-Y2', 'C26H25FN4O4', 'Oncology', 'Fragment-Based Drug Design', 'Phase I', '2021-03-22');

-- Preclinical Studies table
USE SCHEMA preclinical;
CREATE OR REPLACE TABLE studies (
    study_id STRING PRIMARY KEY,
    compound_id STRING,
    study_type STRING,
    study_phase STRING,
    study_status STRING,
    species STRING,
    study_start_date DATE,
    study_end_date DATE,
    efficacy_score DECIMAL(5,2),
    safety_score DECIMAL(5,2),
    study_cost DECIMAL(10,2),
    FOREIGN KEY (compound_id) REFERENCES discovery.compounds(compound_id)
);

INSERT INTO studies VALUES
('PCS001', 'CMP001', 'Efficacy', 'in vitro', 'Completed', 'Cell Line', '1996-01-15', '1996-06-30', 85.5, 92.3, 150000.00),
('PCS002', 'CMP001', 'Toxicology', 'in vivo', 'Completed', 'Mouse', '1996-07-01', '1997-02-28', 78.2, 88.7, 450000.00),
('PCS003', 'CMP002', 'Efficacy', 'in vitro', 'Completed', 'Cell Line', '1993-03-01', '1993-09-15', 92.1, 95.4, 200000.00),
('PCS004', 'CMP002', 'Toxicology', 'in vivo', 'Completed', 'Primate', '1993-10-01', '1994-08-31', 89.3, 91.2, 800000.00),
('PCS005', 'CMP003', 'Efficacy', 'in vitro', 'Completed', 'Cell Line', '1994-05-01', '1994-11-30', 87.6, 93.8, 180000.00),
('PCS006', 'CMP004', 'Efficacy', 'in vitro', 'Completed', 'Cell Line', '2007-01-15', '2007-07-31', 94.2, 96.1, 250000.00),
('PCS007', 'CMP005', 'Toxicology', 'in vivo', 'Completed', 'Mouse', '2006-03-01', '2006-12-15', 82.4, 85.9, 380000.00),
('PCS008', 'CMP011', 'Efficacy', 'in vitro', 'Completed', 'Cell Line', '2021-01-15', '2021-06-30', 88.7, 91.5, 320000.00),
('PCS009', 'CMP011', 'Toxicology', 'in vivo', 'Active', 'Mouse', '2021-07-01', '2022-03-31', 85.3, 89.2, 520000.00),
('PCS010', 'CMP012', 'Efficacy', 'in vitro', 'Completed', 'Cell Line', '2022-01-01', '2022-05-31', 79.8, 87.4, 280000.00);

-- Clinical Trials table
USE SCHEMA clinical;
CREATE OR REPLACE TABLE trials (
    trial_id STRING PRIMARY KEY,
    compound_id STRING,
    trial_phase STRING,
    trial_status STRING,
    indication STRING,
    sponsor STRING,
    primary_endpoint STRING,
    trial_start_date DATE,
    trial_end_date DATE,
    enrolled_patients INTEGER,
    trial_budget DECIMAL(12,2),
    success_rate DECIMAL(5,2),
    FOREIGN KEY (compound_id) REFERENCES discovery.compounds(compound_id)
);

INSERT INTO trials VALUES
('TRL001', 'CMP001', 'Phase I', 'Completed', 'NSCLC', 'Genentech', 'Safety/Tolerability', '1997-06-01', '1998-12-31', 45, 5000000.00, 78.5),
('TRL002', 'CMP001', 'Phase II', 'Completed', 'NSCLC', 'Genentech', 'Response Rate', '1999-03-01', '2001-08-31', 150, 15000000.00, 65.2),
('TRL003', 'CMP001', 'Phase III', 'Completed', 'NSCLC', 'Genentech', 'Overall Survival', '2002-01-15', '2004-12-31', 750, 75000000.00, 58.7),
('TRL004', 'CMP002', 'Phase I', 'Completed', 'Breast Cancer', 'Genentech', 'Safety/Tolerability', '1995-09-01', '1997-03-31', 35, 4500000.00, 82.1),
('TRL005', 'CMP002', 'Phase II', 'Completed', 'Breast Cancer', 'Genentech', 'Response Rate', '1997-06-01', '1999-11-30', 200, 18000000.00, 71.3),
('TRL006', 'CMP002', 'Phase III', 'Completed', 'Breast Cancer', 'Genentech', 'Disease-Free Survival', '2000-02-01', '2003-07-31', 900, 95000000.00, 64.8),
('TRL007', 'CMP004', 'Phase I', 'Completed', 'Melanoma', 'Merck', 'Safety/Tolerability', '2009-01-15', '2010-09-30', 55, 6500000.00, 85.4),
('TRL008', 'CMP004', 'Phase II', 'Completed', 'Melanoma', 'Merck', 'Response Rate', '2011-03-01', '2013-05-31', 180, 22000000.00, 73.9),
('TRL009', 'CMP004', 'Phase III', 'Completed', 'Melanoma', 'Merck', 'Overall Survival', '2013-08-01', '2016-12-31', 850, 120000000.00, 68.2),
('TRL010', 'CMP011', 'Phase I', 'Active', 'NSCLC', 'BioTech Inc', 'Safety/Tolerability', '2022-09-01', '2024-06-30', 30, 8000000.00, NULL),
('TRL011', 'CMP012', 'Phase I', 'Recruiting', 'Ovarian Cancer', 'Pharma Corp', 'Safety/Tolerability', '2023-03-01', '2024-12-31', 25, 7500000.00, NULL);

-- Regulatory Submissions table
USE SCHEMA regulatory;
CREATE OR REPLACE TABLE submissions (
    submission_id STRING PRIMARY KEY,
    compound_id STRING,
    submission_type STRING,
    regulatory_agency STRING,
    submission_status STRING,
    approval_status STRING,
    priority_designation STRING,
    submission_date DATE,
    approval_date DATE,
    review_time_days INTEGER,
    FOREIGN KEY (compound_id) REFERENCES discovery.compounds(compound_id)
);

INSERT INTO submissions VALUES
('SUB001', 'CMP001', 'NDA', 'FDA', 'Approved', 'Approved', 'Standard', '2004-05-15', '2004-11-18', 187),
('SUB002', 'CMP001', 'MAA', 'EMA', 'Approved', 'Approved', 'Standard', '2004-08-20', '2005-03-25', 217),
('SUB003', 'CMP002', 'BLA', 'FDA', 'Approved', 'Approved', 'Priority Review', '1998-02-10', '1998-09-25', 227),
('SUB004', 'CMP002', 'MAA', 'EMA', 'Approved', 'Approved', 'Standard', '1998-06-15', '1999-02-08', 238),
('SUB005', 'CMP003', 'BLA', 'FDA', 'Approved', 'Approved', 'Standard', '2003-09-26', '2004-02-26', 153),
('SUB006', 'CMP004', 'BLA', 'FDA', 'Approved', 'Approved', 'Priority Review', '2014-04-28', '2014-09-04', 129),
('SUB007', 'CMP005', 'NDA', 'FDA', 'Approved', 'Approved', 'Breakthrough Therapy', '2011-01-17', '2011-08-17', 212),
('SUB008', 'CMP006', 'NDA', 'FDA', 'Approved', 'Approved', 'Priority Review', '2011-03-25', '2011-08-26', 154),
('SUB009', 'CMP007', 'NDA', 'FDA', 'Approved', 'Approved', 'Standard', '2014-12-19', '2015-02-03', 46),
('SUB010', 'CMP008', 'NDA', 'FDA', 'Approved', 'Approved', 'Priority Review', '2014-07-16', '2014-12-19', 156),
('SUB011', 'CMP011', 'IND', 'FDA', 'Active', 'Under Review', 'Fast Track', '2022-06-15', NULL, NULL),
('SUB012', 'CMP012', 'IND', 'FDA', 'Submitted', 'Under Review', 'Standard', '2023-01-20', NULL, NULL);

-- Manufacturing table
USE SCHEMA manufacturing;
CREATE OR REPLACE TABLE production (
    batch_id STRING PRIMARY KEY,
    compound_id STRING,
    manufacturing_site STRING,
    formulation_type STRING,
    batch_status STRING,
    quality_grade STRING,
    production_date DATE,
    batch_size INTEGER,
    production_cost DECIMAL(10,2),
    yield_percentage DECIMAL(5,2),
    FOREIGN KEY (compound_id) REFERENCES discovery.compounds(compound_id)
);

INSERT INTO production VALUES
('BTH001', 'CMP001', 'South San Francisco, CA', 'Tablet', 'Released', 'Grade A', '2024-01-15', 100000, 125000.00, 94.5),
('BTH002', 'CMP001', 'South San Francisco, CA', 'Tablet', 'Released', 'Grade A', '2024-01-22', 150000, 187500.00, 96.2),
('BTH003', 'CMP002', 'Vacaville, CA', 'Injectable', 'Released', 'Grade A', '2024-01-10', 5000, 450000.00, 92.8),
('BTH004', 'CMP002', 'Vacaville, CA', 'Injectable', 'Released', 'Grade A', '2024-01-25', 7500, 675000.00, 94.1),
('BTH005', 'CMP003', 'Oceanside, CA', 'Injectable', 'Released', 'Grade A', '2024-01-08', 3000, 520000.00, 91.3),
('BTH006', 'CMP004', 'West Point, PA', 'Injectable', 'Released', 'Grade A', '2024-01-12', 2500, 890000.00, 93.7),
('BTH007', 'CMP005', 'Basel, Switzerland', 'Tablet', 'Released', 'Grade A', '2024-01-18', 80000, 320000.00, 95.4),
('BTH008', 'CMP006', 'Kalamazoo, MI', 'Capsule', 'Released', 'Grade A', '2024-01-20', 120000, 280000.00, 97.1),
('BTH009', 'CMP007', 'Freiburg, Germany', 'Capsule', 'Released', 'Grade A', '2024-01-14', 90000, 450000.00, 94.8),
('BTH010', 'CMP008', 'Macclesfield, UK', 'Tablet', 'Released', 'Grade A', '2024-01-28', 75000, 380000.00, 93.2);

-- Commercialization table
USE SCHEMA commercial;
CREATE OR REPLACE TABLE products (
    product_id STRING PRIMARY KEY,
    compound_id STRING,
    brand_name STRING,
    market_segment STRING,
    launch_status STRING,
    geographic_market STRING,
    launch_date DATE,
    revenue DECIMAL(15,2),
    units_sold INTEGER,
    market_share DECIMAL(5,2),
    FOREIGN KEY (compound_id) REFERENCES discovery.compounds(compound_id)
);

INSERT INTO products VALUES
('PRD001', 'CMP001', 'Tarceva', 'NSCLC Treatment', 'Launched', 'North America', '2004-11-18', 1250000000.00, 2500000, 15.8),
('PRD002', 'CMP001', 'Tarceva', 'NSCLC Treatment', 'Launched', 'Europe', '2005-03-25', 890000000.00, 1780000, 12.3),
('PRD003', 'CMP002', 'Herceptin', 'Breast Cancer Treatment', 'Launched', 'North America', '1998-09-25', 3200000000.00, 1600000, 28.5),
('PRD004', 'CMP002', 'Herceptin', 'Breast Cancer Treatment', 'Launched', 'Europe', '1999-02-08', 2800000000.00, 1400000, 25.2),
('PRD005', 'CMP003', 'Avastin', 'Colorectal Cancer Treatment', 'Launched', 'North America', '2004-02-26', 2900000000.00, 580000, 22.1),
('PRD006', 'CMP004', 'Keytruda', 'Melanoma Treatment', 'Launched', 'North America', '2014-09-04', 4500000000.00, 450000, 35.7),
('PRD007', 'CMP005', 'Zelboraf', 'Melanoma Treatment', 'Launched', 'North America', '2011-08-17', 850000000.00, 170000, 8.9),
('PRD008', 'CMP006', 'Xalkori', 'NSCLC Treatment', 'Launched', 'North America', '2011-08-26', 1100000000.00, 220000, 11.2),
('PRD009', 'CMP007', 'Ibrance', 'Breast Cancer Treatment', 'Launched', 'North America', '2015-02-03', 2700000000.00, 540000, 18.9),
('PRD010', 'CMP008', 'Lynparza', 'Ovarian Cancer Treatment', 'Launched', 'North America', '2014-12-19', 1600000000.00, 320000, 14.3);
