-- Clinical Trial Operations Database
-- Create database and schema
CREATE DATABASE IF NOT EXISTS clinical_db;
USE DATABASE clinical_db;
CREATE SCHEMA IF NOT EXISTS operations;
USE SCHEMA operations;

-- Sites table
CREATE OR REPLACE TABLE sites (
    site_id STRING PRIMARY KEY,
    site_country STRING,
    site_type STRING
);

INSERT INTO sites VALUES
('SITE001', 'USA', 'Academic Medical Center'),
('SITE002', 'USA', 'Private Practice'),
('SITE003', 'Canada', 'Hospital'),
('SITE004', 'UK', 'Academic Medical Center'),
('SITE005', 'Germany', 'Hospital'),
('SITE006', 'France', 'Private Practice'),
('SITE007', 'Japan', 'Hospital'),
('SITE008', 'Australia', 'Academic Medical Center'),
('SITE009', 'USA', 'Hospital'),
('SITE010', 'USA', 'Academic Medical Center'),
('SITE011', 'Canada', 'Private Practice'),
('SITE012', 'UK', 'Hospital'),
('SITE013', 'Germany', 'Academic Medical Center'),
('SITE014', 'France', 'Hospital'),
('SITE015', 'Japan', 'Private Practice'),
('SITE016', 'Australia', 'Hospital'),
('SITE017', 'Italy', 'Academic Medical Center'),
('SITE018', 'Spain', 'Hospital'),
('SITE019', 'Netherlands', 'Private Practice'),
('SITE020', 'Sweden', 'Academic Medical Center'),
('SITE021', 'Brazil', 'Hospital'),
('SITE022', 'Mexico', 'Private Practice'),
('SITE023', 'South Korea', 'Academic Medical Center'),
('SITE024', 'India', 'Hospital');

-- Patients table
CREATE OR REPLACE TABLE patients (
    patient_id STRING PRIMARY KEY,
    site_id STRING,
    age INTEGER,
    gender STRING,
    enrollment_status STRING,
    target_enrollment INTEGER DEFAULT 100,
    FOREIGN KEY (site_id) REFERENCES sites(site_id)
);

INSERT INTO patients VALUES
('PAT001', 'SITE001', 45, 'Female', 'Active', 100),
('PAT002', 'SITE001', 52, 'Male', 'Active', 100),
('PAT003', 'SITE001', 38, 'Female', 'Completed', 100),
('PAT004', 'SITE002', 61, 'Male', 'Active', 100),
('PAT005', 'SITE002', 29, 'Female', 'Withdrawn', 100),
('PAT006', 'SITE003', 47, 'Male', 'Active', 100),
('PAT007', 'SITE003', 55, 'Female', 'Active', 100),
('PAT008', 'SITE004', 42, 'Male', 'Completed', 100),
('PAT009', 'SITE004', 36, 'Female', 'Active', 100),
('PAT010', 'SITE005', 58, 'Male', 'Active', 100),
('PAT011', 'SITE005', 33, 'Female', 'Active', 100),
('PAT012', 'SITE006', 49, 'Male', 'Completed', 100),
('PAT013', 'SITE006', 41, 'Female', 'Active', 100),
('PAT014', 'SITE007', 53, 'Male', 'Active', 100),
('PAT015', 'SITE008', 39, 'Female', 'Active', 100),
('PAT016', 'SITE009', 44, 'Male', 'Active', 100),
('PAT017', 'SITE009', 31, 'Female', 'Active', 100),
('PAT018', 'SITE010', 56, 'Male', 'Completed', 100),
('PAT019', 'SITE010', 48, 'Female', 'Active', 100),
('PAT020', 'SITE011', 62, 'Male', 'Active', 100),
('PAT021', 'SITE011', 35, 'Female', 'Withdrawn', 100),
('PAT022', 'SITE012', 50, 'Male', 'Active', 100),
('PAT023', 'SITE012', 43, 'Female', 'Active', 100),
('PAT024', 'SITE013', 37, 'Male', 'Completed', 100),
('PAT025', 'SITE013', 59, 'Female', 'Active', 100),
('PAT026', 'SITE014', 46, 'Male', 'Active', 100),
('PAT027', 'SITE014', 32, 'Female', 'Active', 100),
('PAT028', 'SITE015', 54, 'Male', 'Completed', 100),
('PAT029', 'SITE015', 40, 'Female', 'Active', 100),
('PAT030', 'SITE016', 51, 'Male', 'Active', 100),
('PAT031', 'SITE017', 28, 'Female', 'Active', 100),
('PAT032', 'SITE017', 63, 'Male', 'Active', 100),
('PAT033', 'SITE018', 45, 'Female', 'Completed', 100),
('PAT034', 'SITE018', 38, 'Male', 'Active', 100),
('PAT035', 'SITE019', 57, 'Female', 'Active', 100),
('PAT036', 'SITE019', 34, 'Male', 'Withdrawn', 100),
('PAT037', 'SITE020', 49, 'Female', 'Active', 100),
('PAT038', 'SITE020', 42, 'Male', 'Active', 100),
('PAT039', 'SITE021', 53, 'Female', 'Completed', 100),
('PAT040', 'SITE021', 36, 'Male', 'Active', 100),
('PAT041', 'SITE022', 47, 'Female', 'Active', 100),
('PAT042', 'SITE022', 55, 'Male', 'Active', 100),
('PAT043', 'SITE023', 41, 'Female', 'Active', 100),
('PAT044', 'SITE023', 58, 'Male', 'Completed', 100),
('PAT045', 'SITE024', 33, 'Female', 'Active', 100);

-- Visits table
CREATE OR REPLACE TABLE visits (
    visit_id STRING PRIMARY KEY,
    patient_id STRING,
    visit_type STRING,
    visit_status STRING,
    visit_date DATE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

INSERT INTO visits VALUES
('VIS001', 'PAT001', 'Screening', 'Completed', '2024-01-15'),
('VIS002', 'PAT001', 'Baseline', 'Completed', '2024-01-22'),
('VIS003', 'PAT001', 'Week 4', 'Completed', '2024-02-19'),
('VIS004', 'PAT002', 'Screening', 'Completed', '2024-01-16'),
('VIS005', 'PAT002', 'Baseline', 'Completed', '2024-01-23'),
('VIS006', 'PAT003', 'Screening', 'Completed', '2024-01-10'),
('VIS007', 'PAT003', 'Baseline', 'Completed', '2024-01-17'),
('VIS008', 'PAT003', 'Week 4', 'Completed', '2024-02-14'),
('VIS009', 'PAT003', 'Week 8', 'Completed', '2024-03-14'),
('VIS010', 'PAT004', 'Screening', 'Completed', '2024-01-18'),
('VIS011', 'PAT004', 'Baseline', 'Missed', '2024-01-25'),
('VIS012', 'PAT005', 'Screening', 'Completed', '2024-01-12'),
('VIS013', 'PAT006', 'Screening', 'Completed', '2024-01-20'),
('VIS014', 'PAT006', 'Baseline', 'Completed', '2024-01-27'),
('VIS015', 'PAT007', 'Screening', 'Completed', '2024-01-21'),
('VIS016', 'PAT008', 'Screening', 'Completed', '2024-01-25'),
('VIS017', 'PAT008', 'Baseline', 'Completed', '2024-02-01'),
('VIS018', 'PAT009', 'Screening', 'Completed', '2024-01-28'),
('VIS019', 'PAT010', 'Screening', 'Completed', '2024-02-02'),
('VIS020', 'PAT010', 'Baseline', 'Completed', '2024-02-09'),
('VIS021', 'PAT011', 'Screening', 'Completed', '2024-02-05'),
('VIS022', 'PAT012', 'Screening', 'Completed', '2024-02-08'),
('VIS023', 'PAT012', 'Baseline', 'Completed', '2024-02-15'),
('VIS024', 'PAT013', 'Screening', 'Completed', '2024-02-12'),
('VIS025', 'PAT014', 'Screening', 'Completed', '2024-02-18'),
('VIS026', 'PAT015', 'Screening', 'Completed', '2024-02-22'),
('VIS027', 'PAT016', 'Screening', 'Completed', '2024-02-25'),
('VIS028', 'PAT017', 'Screening', 'Completed', '2024-03-01'),
('VIS029', 'PAT018', 'Screening', 'Completed', '2024-03-05'),
('VIS030', 'PAT019', 'Screening', 'Completed', '2024-03-08'),
('VIS031', 'PAT020', 'Screening', 'Completed', '2024-03-12'),
('VIS032', 'PAT021', 'Screening', 'Completed', '2024-03-15'),
('VIS033', 'PAT022', 'Screening', 'Completed', '2024-03-18'),
('VIS034', 'PAT023', 'Screening', 'Completed', '2024-03-22'),
('VIS035', 'PAT024', 'Screening', 'Completed', '2024-03-25'),
('VIS036', 'PAT025', 'Screening', 'Completed', '2024-03-28'),
('VIS037', 'PAT026', 'Screening', 'Completed', '2024-04-01'),
('VIS038', 'PAT027', 'Screening', 'Completed', '2024-04-05'),
('VIS039', 'PAT028', 'Screening', 'Completed', '2024-04-08'),
('VIS040', 'PAT029', 'Screening', 'Completed', '2024-04-12'),
('VIS041', 'PAT030', 'Screening', 'Completed', '2024-04-15'),
('VIS042', 'PAT031', 'Screening', 'Completed', '2024-04-18'),
('VIS043', 'PAT032', 'Screening', 'Completed', '2024-04-22'),
('VIS044', 'PAT033', 'Screening', 'Completed', '2024-04-25'),
('VIS045', 'PAT034', 'Screening', 'Completed', '2024-04-28');

-- Adverse Events table
CREATE OR REPLACE TABLE adverse_events (
    ae_id STRING PRIMARY KEY,
    patient_id STRING,
    ae_severity STRING,
    ae_category STRING,
    ae_description STRING,
    onset_date DATE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

INSERT INTO adverse_events VALUES
('AE001', 'PAT001', 'Mild', 'Gastrointestinal', 'Nausea', '2024-01-25'),
('AE002', 'PAT002', 'Moderate', 'Neurological', 'Headache', '2024-01-28'),
('AE003', 'PAT003', 'Mild', 'Dermatological', 'Rash', '2024-02-01'),
('AE004', 'PAT004', 'Serious', 'Cardiovascular', 'Chest pain', '2024-02-05'),
('AE005', 'PAT006', 'Mild', 'Gastrointestinal', 'Diarrhea', '2024-02-10'),
('AE006', 'PAT007', 'Moderate', 'Respiratory', 'Cough', '2024-02-12'),
('AE007', 'PAT008', 'Mild', 'Musculoskeletal', 'Joint pain', '2024-02-15'),
('AE008', 'PAT009', 'Moderate', 'Gastrointestinal', 'Vomiting', '2024-02-18'),
('AE009', 'PAT010', 'Serious', 'Neurological', 'Seizure', '2024-02-20'),
('AE010', 'PAT011', 'Mild', 'Dermatological', 'Itching', '2024-02-22'),
('AE011', 'PAT012', 'Moderate', 'Gastrointestinal', 'Nausea', '2024-02-25'),
('AE012', 'PAT013', 'Mild', 'Neurological', 'Dizziness', '2024-02-28'),
('AE013', 'PAT014', 'Moderate', 'Dermatological', 'Rash', '2024-03-02'),
('AE014', 'PAT015', 'Mild', 'Respiratory', 'Shortness of breath', '2024-03-05'),
('AE015', 'PAT016', 'Serious', 'Cardiovascular', 'Arrhythmia', '2024-03-08'),
('AE016', 'PAT017', 'Mild', 'Gastrointestinal', 'Constipation', '2024-03-12'),
('AE017', 'PAT018', 'Moderate', 'Musculoskeletal', 'Back pain', '2024-03-15'),
('AE018', 'PAT019', 'Mild', 'Neurological', 'Fatigue', '2024-03-18'),
('AE019', 'PAT020', 'Moderate', 'Dermatological', 'Dry skin', '2024-03-22'),
('AE020', 'PAT021', 'Serious', 'Gastrointestinal', 'GI bleeding', '2024-03-25'),
('AE021', 'PAT022', 'Mild', 'Respiratory', 'Cough', '2024-03-28'),
('AE022', 'PAT023', 'Moderate', 'Neurological', 'Headache', '2024-04-01'),
('AE023', 'PAT024', 'Mild', 'Musculoskeletal', 'Muscle cramps', '2024-04-05'),
('AE024', 'PAT025', 'Moderate', 'Cardiovascular', 'Hypertension', '2024-04-08'),
('AE025', 'PAT026', 'Mild', 'Gastrointestinal', 'Heartburn', '2024-04-12'),
('AE026', 'PAT027', 'Serious', 'Neurological', 'Confusion', '2024-04-15'),
('AE027', 'PAT028', 'Mild', 'Dermatological', 'Bruising', '2024-04-18'),
('AE028', 'PAT029', 'Moderate', 'Respiratory', 'Wheezing', '2024-04-22'),
('AE029', 'PAT030', 'Mild', 'Gastrointestinal', 'Loss of appetite', '2024-04-25'),
('AE030', 'PAT031', 'Moderate', 'Musculoskeletal', 'Joint stiffness', '2024-04-28');

-- Recruitment Events table
CREATE OR REPLACE TABLE recruitment_events (
    recruitment_id STRING PRIMARY KEY,
    site_id STRING,
    event_type STRING,
    event_date DATE,
    target_count INTEGER,
    actual_count INTEGER,
    notes STRING,
    FOREIGN KEY (site_id) REFERENCES sites(site_id)
);

INSERT INTO recruitment_events VALUES
('REC001', 'SITE001', 'Screening Started', '2024-01-01', 10, 8, 'Initial recruitment phase'),
('REC002', 'SITE001', 'Enrollment Target Met', '2024-02-15', 5, 5, 'Met monthly target'),
('REC003', 'SITE002', 'Screening Started', '2024-01-05', 8, 6, 'Slower than expected'),
('REC004', 'SITE003', 'Recruitment Milestone', '2024-01-20', 12, 10, 'Good progress'),
('REC005', 'SITE004', 'Screening Started', '2024-01-10', 15, 12, 'Strong initial response'),
('REC006', 'SITE005', 'Enrollment Challenge', '2024-02-01', 10, 4, 'Need to increase outreach'),
('REC007', 'SITE006', 'Recruitment Success', '2024-02-10', 8, 9, 'Exceeded target'),
('REC008', 'SITE007', 'Screening Started', '2024-01-25', 6, 5, 'On track'),
('REC009', 'SITE008', 'Enrollment Boost', '2024-03-01', 12, 15, 'Marketing campaign effective'),
('REC010', 'SITE009', 'Recruitment Review', '2024-02-20', 10, 8, 'Need strategy adjustment'),
('REC011', 'SITE010', 'Screening Started', '2024-02-05', 14, 11, 'Moderate progress'),
('REC012', 'SITE011', 'Enrollment Target Met', '2024-03-15', 7, 7, 'Consistent performance'),
('REC013', 'SITE012', 'Recruitment Challenge', '2024-03-01', 9, 5, 'Site capacity issues'),
('REC014', 'SITE013', 'Screening Started', '2024-02-15', 11, 9, 'Good initial response'),
('REC015', 'SITE014', 'Enrollment Success', '2024-03-20', 8, 10, 'Exceeded expectations'),
('REC016', 'SITE015', 'Recruitment Milestone', '2024-03-10', 6, 6, 'Met quarterly goal'),
('REC017', 'SITE016', 'Screening Started', '2024-03-05', 13, 8, 'Need improvement'),
('REC018', 'SITE017', 'Enrollment Boost', '2024-04-01', 9, 12, 'Strong referral network'),
('REC019', 'SITE018', 'Recruitment Review', '2024-03-25', 7, 6, 'Close to target'),
('REC020', 'SITE019', 'Screening Started', '2024-03-15', 10, 7, 'Steady progress');

-- Quality Events table
CREATE OR REPLACE TABLE quality_events (
    quality_id STRING PRIMARY KEY,
    site_id STRING,
    patient_id STRING,
    event_type STRING,
    severity STRING,
    event_date DATE,
    description STRING,
    resolution_status STRING,
    corrective_action STRING,
    FOREIGN KEY (site_id) REFERENCES sites(site_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

INSERT INTO quality_events VALUES
('QE001', 'SITE001', 'PAT001', 'Protocol Deviation', 'Minor', '2024-01-20', 'Visit window exceeded by 2 days', 'Resolved', 'Documented in case report form'),
('QE002', 'SITE001', 'PAT002', 'Data Query', 'Minor', '2024-01-25', 'Missing vital signs data', 'Resolved', 'Data retrieved and entered'),
('QE003', 'SITE002', 'PAT004', 'Protocol Violation', 'Major', '2024-02-01', 'Prohibited medication taken', 'Under Review', 'Investigating impact on study'),
('QE004', 'SITE003', 'PAT006', 'Consent Issue', 'Minor', '2024-02-05', 'Informed consent not properly dated', 'Resolved', 'Corrected and re-signed'),
('QE005', 'SITE004', 'PAT008', 'Data Discrepancy', 'Minor', '2024-02-10', 'Lab values inconsistent', 'Resolved', 'Lab re-run confirmed values'),
('QE006', 'SITE005', 'PAT010', 'Protocol Deviation', 'Moderate', '2024-02-15', 'Incorrect dosing for 3 days', 'Resolved', 'Dosing corrected, safety review completed'),
('QE007', 'SITE006', 'PAT012', 'Documentation Error', 'Minor', '2024-02-20', 'Incorrect date on CRF', 'Resolved', 'Date corrected with explanation'),
('QE008', 'SITE007', 'PAT014', 'Eligibility Issue', 'Major', '2024-02-25', 'Patient did not meet inclusion criteria', 'Under Review', 'Reviewing enrollment decision'),
('QE009', 'SITE008', 'PAT015', 'Data Query', 'Minor', '2024-03-01', 'Unclear adverse event description', 'Resolved', 'Additional details provided'),
('QE010', 'SITE009', 'PAT016', 'Protocol Deviation', 'Minor', '2024-03-05', 'Lab draw outside window', 'Resolved', 'Documented deviation rationale'),
('QE011', 'SITE010', 'PAT018', 'Consent Issue', 'Moderate', '2024-03-10', 'Patient withdrew consent verbally only', 'Resolved', 'Written withdrawal obtained'),
('QE012', 'SITE011', 'PAT020', 'Data Discrepancy', 'Minor', '2024-03-15', 'Height/weight measurements inconsistent', 'Resolved', 'Measurements re-taken'),
('QE013', 'SITE012', 'PAT022', 'Protocol Violation', 'Major', '2024-03-20', 'Concomitant medication not reported', 'Under Review', 'Safety assessment ongoing'),
('QE014', 'SITE013', 'PAT024', 'Documentation Error', 'Minor', '2024-03-25', 'Missing investigator signature', 'Resolved', 'Signature obtained'),
('QE015', 'SITE014', 'PAT026', 'Data Query', 'Minor', '2024-03-30', 'Incomplete medical history', 'Resolved', 'Additional history documented'),
('QE016', 'SITE015', 'PAT028', 'Protocol Deviation', 'Moderate', '2024-04-05', 'Study drug taken with food', 'Resolved', 'Patient re-educated on dosing'),
('QE017', 'SITE016', 'PAT030', 'Eligibility Issue', 'Minor', '2024-04-10', 'Lab value borderline for inclusion', 'Resolved', 'Medical monitor approved enrollment'),
('QE018', 'SITE017', 'PAT031', 'Data Discrepancy', 'Minor', '2024-04-15', 'ECG interpretation differs', 'Resolved', 'Cardiologist review completed'),
('QE019', 'SITE018', 'PAT033', 'Consent Issue', 'Minor', '2024-04-20', 'Patient questions about study procedures', 'Resolved', 'Additional counseling provided'),
('QE020', 'SITE019', 'PAT035', 'Protocol Deviation', 'Minor', '2024-04-25', 'Visit rescheduled outside window', 'Resolved', 'Documented acceptable deviation');
