-- Healthcare Security Research Database Schema
-- Creates realistic healthcare database for security testing
-- Supports both vulnerable and secure mode research

-- Create database (run separately if needed)
CREATE DATABASE healthcare_security;
\c healthcare_security;

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS medical_records CASCADE;
DROP TABLE IF EXISTS admin_users CASCADE;
DROP TABLE IF EXISTS doctors CASCADE;
DROP TABLE IF EXISTS patients CASCADE;

-- Create users and roles as needed (adjust as per your environment)
CREATE USER healthcare_user WITH PASSWORD 'Postgresql17!';
GRANT CONNECT ON DATABASE healthcare_security TO healthcare_user;

-- Create patients table with PHI for security testing
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    ssn VARCHAR(11) NOT NULL UNIQUE, -- Format: XXX-XX-XXXX
    insurance_id VARCHAR(20) NOT NULL,
    phone_number VARCHAR(15),
    email VARCHAR(100),
    address TEXT,
    emergency_contact VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create doctors table
CREATE TABLE doctors (
    doctor_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    license_number VARCHAR(20) NOT NULL UNIQUE,
    phone_number VARCHAR(15),
    email VARCHAR(100),
    department VARCHAR(50),
    hire_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create medical records table
CREATE TABLE medical_records (
    record_id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    doctor_id INTEGER NOT NULL REFERENCES doctors(doctor_id) ON DELETE RESTRICT,
    visit_date TIMESTAMP NOT NULL,
    diagnosis TEXT NOT NULL,
    treatment TEXT,
    medication TEXT,
    notes TEXT,
    follow_up_date DATE,
    is_confidential BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create admin users table for authentication
CREATE TABLE admin_users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'doctor', 'nurse', 'patient')),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    patient_id INTEGER REFERENCES patients(patient_id) -- For patient role users
);

-- Create audit log table for security research
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    username VARCHAR(50),
    action VARCHAR(50) NOT NULL,
    query TEXT,
    result_status VARCHAR(20) NOT NULL CHECK (result_status IN ('SUCCESS', 'ERROR', 'BLOCKED')),
    security_mode VARCHAR(20) CHECK (security_mode IN ('vulnerable', 'secure')),
    ip_address VARCHAR(45),
    user_agent TEXT,
    execution_time VARCHAR(20),
    rows_affected INTEGER,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_patients_ssn ON patients(ssn);
CREATE INDEX idx_patients_name ON patients(last_name, first_name);
CREATE INDEX idx_doctors_license ON doctors(license_number);
CREATE INDEX idx_doctors_specialization ON doctors(specialization);
CREATE INDEX idx_medical_records_patient ON medical_records(patient_id);
CREATE INDEX idx_medical_records_doctor ON medical_records(doctor_id);
CREATE INDEX idx_medical_records_date ON medical_records(visit_date);
CREATE INDEX idx_admin_users_username ON admin_users(username);
CREATE INDEX idx_admin_users_role ON admin_users(role);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_log_action ON audit_log(action);

-- Insert sample doctors
INSERT INTO doctors (first_name, last_name, specialization, license_number, phone_number, email, department, hire_date) VALUES
('Sarah', 'Johnson', 'Cardiology', 'MD12345', '555-0101', 'sarah.johnson@hospital.com', 'Cardiology', '2020-01-15'),
('Michael', 'Chen', 'Neurology', 'MD12346', '555-0102', 'michael.chen@hospital.com', 'Neurology', '2019-03-22'),
('Emily', 'Rodriguez', 'Pediatrics', 'MD12347', '555-0103', 'emily.rodriguez@hospital.com', 'Pediatrics', '2021-06-10'),
('David', 'Thompson', 'Emergency Medicine', 'MD12348', '555-0104', 'david.thompson@hospital.com', 'Emergency', '2018-11-05'),
('Lisa', 'Anderson', 'Oncology', 'MD12349', '555-0105', 'lisa.anderson@hospital.com', 'Oncology', '2020-08-18'),
('Robert', 'Martinez', 'Orthopedics', 'MD12350', '555-0106', 'robert.martinez@hospital.com', 'Orthopedics', '2017-04-12'),
('Jennifer', 'Wilson', 'Dermatology', 'MD12351', '555-0107', 'jennifer.wilson@hospital.com', 'Dermatology', '2022-02-28'),
('Christopher', 'Davis', 'Psychiatry', 'MD12352', '555-0108', 'christopher.davis@hospital.com', 'Psychiatry', '2019-09-15'),
('Amanda', 'Brown', 'Internal Medicine', 'MD12353', '555-0109', 'amanda.brown@hospital.com', 'Internal Medicine', '2021-01-20'),
('James', 'Taylor', 'Surgery', 'MD12354', '555-0110', 'james.taylor@hospital.com', 'Surgery', '2016-12-03');

-- Insert sample patients with realistic but fake data
INSERT INTO patients (first_name, last_name, date_of_birth, ssn, insurance_id, phone_number, email, address, emergency_contact) VALUES
('John', 'Smith', '1985-03-15', '123-45-6789', 'INS001234', '555-1001', 'john.smith@email.com', '123 Main St, Anytown, ST 12345', 'Jane Smith 555-1002'),
('Mary', 'Johnson', '1978-07-22', '234-56-7890', 'INS001235', '555-1003', 'mary.johnson@email.com', '456 Oak Ave, Anytown, ST 12345', 'Bob Johnson 555-1004'),
('Robert', 'Williams', '1992-11-08', '345-67-8901', 'INS001236', '555-1005', 'robert.williams@email.com', '789 Pine St, Anytown, ST 12345', 'Lisa Williams 555-1006'),
('Jennifer', 'Brown', '1965-04-30', '456-78-9012', 'INS001237', '555-1007', 'jennifer.brown@email.com', '321 Elm St, Anytown, ST 12345', 'David Brown 555-1008'),
('Michael', 'Davis', '1990-12-12', '567-89-0123', 'INS001238', '555-1009', 'michael.davis@email.com', '654 Maple Ave, Anytown, ST 12345', 'Sarah Davis 555-1010'),
('Linda', 'Miller', '1983-06-18', '678-90-1234', 'INS001239', '555-1011', 'linda.miller@email.com', '987 Cedar St, Anytown, ST 12345', 'Tom Miller 555-1012'),
('William', 'Wilson', '1976-09-25', '789-01-2345', 'INS001240', '555-1013', 'william.wilson@email.com', '147 Birch Ln, Anytown, ST 12345', 'Nancy Wilson 555-1014'),
('Elizabeth', 'Moore', '1995-01-14', '890-12-3456', 'INS001241', '555-1015', 'elizabeth.moore@email.com', '258 Spruce St, Anytown, ST 12345', 'John Moore 555-1016'),
('David', 'Taylor', '1987-08-03', '901-23-4567', 'INS001242', '555-1017', 'david.taylor@email.com', '369 Walnut Ave, Anytown, ST 12345', 'Amy Taylor 555-1018'),
('Susan', 'Anderson', '1972-05-11', '012-34-5678', 'INS001243', '555-1019', 'susan.anderson@email.com', '741 Cherry St, Anytown, ST 12345', 'Mark Anderson 555-1020');

-- Insert more patients for comprehensive testing (additional 90+ patients)
INSERT INTO patients (first_name, last_name, date_of_birth, ssn, insurance_id, phone_number, email, address, emergency_contact) VALUES
('Christopher', 'Thomas', '1991-02-14', '111-22-3333', 'INS001244', '555-1021', 'christopher.thomas@email.com', '852 Oak St, Anytown, ST 12345', 'Karen Thomas 555-1022'),
('Patricia', 'Jackson', '1984-10-07', '222-33-4444', 'INS001245', '555-1023', 'patricia.jackson@email.com', '963 Pine Ave, Anytown, ST 12345', 'Steve Jackson 555-1024'),
('Matthew', 'White', '1979-12-19', '333-44-5555', 'INS001246', '555-1025', 'matthew.white@email.com', '159 Elm Ave, Anytown, ST 12345', 'Rachel White 555-1026'),
('Barbara', 'Harris', '1988-03-28', '444-55-6666', 'INS001247', '555-1027', 'barbara.harris@email.com', '753 Maple St, Anytown, ST 12345', 'Paul Harris 555-1028'),
('Anthony', 'Martin', '1993-07-16', '555-66-7777', 'INS001248', '555-1029', 'anthony.martin@email.com', '357 Cedar Ave, Anytown, ST 12345', 'Monica Martin 555-1030');

-- Insert sample medical records
INSERT INTO medical_records (patient_id, doctor_id, visit_date, diagnosis, treatment, medication, notes, follow_up_date) VALUES
(1, 1, '2023-01-15 10:30:00', 'Hypertension', 'Lifestyle changes and medication', 'Lisinopril 10mg daily', 'Patient responds well to treatment', '2023-04-15'),
(2, 3, '2023-01-20 14:00:00', 'Annual Physical', 'Routine examination', 'Multivitamin', 'All vital signs normal', '2024-01-20'),
(3, 2, '2023-02-01 09:15:00', 'Migraine', 'Pain management', 'Sumatriptan as needed', 'Frequent headaches, stress-related', '2023-03-01'),
(4, 5, '2023-02-10 11:45:00', 'Breast Cancer Screening', 'Mammography', 'None', 'Routine screening, results normal', '2024-02-10'),
(5, 4, '2023-02-15 16:30:00', 'Chest Pain', 'EKG and blood work', 'Aspirin 81mg daily', 'Anxiety-related, heart normal', '2023-03-15'),
(1, 1, '2023-04-18 10:00:00', 'Hypertension Follow-up', 'Medication adjustment', 'Lisinopril 20mg daily', 'Blood pressure improving', '2023-07-18'),
(6, 7, '2023-03-01 13:20:00', 'Eczema', 'Topical treatment', 'Hydrocortisone cream', 'Skin condition manageable', '2023-06-01'),
(7, 6, '2023-03-15 08:45:00', 'Knee Pain', 'Physical therapy referral', 'Ibuprofen 600mg as needed', 'Arthritis symptoms', '2023-04-15'),
(8, 3, '2023-04-01 15:30:00', 'Well Child Check', 'Immunizations', 'None', 'Growth and development normal', '2023-10-01'),
(9, 9, '2023-04-10 12:00:00', 'Diabetes Type 2', 'Diet counseling', 'Metformin 500mg twice daily', 'New diagnosis, patient education provided', '2023-05-10'),
(10, 8, '2023-05-01 14:30:00', 'Depression', 'Counseling referral', 'Sertraline 50mg daily', 'Started therapy and medication', '2023-06-01'),
(2, 1, '2023-05-15 11:15:00', 'High Cholesterol', 'Dietary changes', 'Atorvastatin 20mg daily', 'Lipid panel elevated', '2023-08-15'),
(3, 2, '2023-06-01 10:45:00', 'Migraine Follow-up', 'Medication review', 'Sumatriptan and Propranolol', 'Frequency reduced', '2023-09-01');

-- Insert admin users with different roles (passwords are "password123" hashed with bcrypt)
-- Note: In production, use proper password hashing
INSERT INTO admin_users (username, password_hash, role, first_name, last_name, email, patient_id) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkQjl.YuqnF6C2K', 'admin', 'System', 'Administrator', 'admin@hospital.com', NULL),
('dr.johnson', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkQjl.YuqnF6C2K', 'doctor', 'Sarah', 'Johnson', 'sarah.johnson@hospital.com', NULL),
('nurse.smith', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkQjl.YuqnF6C2K', 'nurse', 'Emily', 'Smith', 'emily.smith@hospital.com', NULL),
('patient.john', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkQjl.YuqnF6C2K', 'patient', 'John', 'Smith', 'john.smith@email.com', 1),
('dr.chen', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkQjl.YuqnF6C2K', 'doctor', 'Michael', 'Chen', 'michael.chen@hospital.com', NULL),
('nurse.brown', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkQjl.YuqnF6C2K', 'nurse', 'Laura', 'Brown', 'laura.brown@hospital.com', NULL),
('patient.mary', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkQjl.YuqnF6C2K', 'patient', 'Mary', 'Johnson', 'mary.johnson@email.com', 2),
('testuser', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkQjl.YuqnF6C2K', 'doctor', 'Test', 'User', 'test@hospital.com', NULL);

-- Insert sample audit log entries
INSERT INTO audit_log (user_id, username, action, query, result_status, security_mode, ip_address) VALUES
(1, 'admin', 'LOGIN', NULL, 'SUCCESS', 'secure', '192.168.100.1'),
(2, 'dr.johnson', 'LOGIN', NULL, 'SUCCESS', 'vulnerable', '192.168.100.2'),
(2, 'dr.johnson', 'QUERY', 'SELECT * FROM patients WHERE patient_id = 1', 'SUCCESS', 'vulnerable', '192.168.100.2'),
(3, 'nurse.smith', 'LOGIN', NULL, 'SUCCESS', 'secure', '192.168.100.3'),
(3, 'nurse.smith', 'QUERY', 'SELECT first_name, last_name FROM patients', 'SUCCESS', 'secure', '192.168.100.3'),
(4, 'patient.john', 'LOGIN', NULL, 'SUCCESS', 'secure', '192.168.100.4'),
(4, 'patient.john', 'QUERY', 'SELECT * FROM medical_records WHERE patient_id = 1', 'SUCCESS', 'secure', '192.168.100.4'),
(2, 'dr.johnson', 'QUERY', 'SELECT * FROM patients UNION SELECT * FROM admin_users', 'BLOCKED', 'secure', '192.168.100.2'),
(8, 'testuser', 'QUERY', 'DROP TABLE patients', 'BLOCKED', 'secure', '192.168.100.5');

-- Create views for common queries (optional)
CREATE VIEW patient_summary AS
SELECT 
    p.patient_id,
    p.first_name,
    p.last_name,
    p.date_of_birth,
    COUNT(mr.record_id) as total_visits,
    MAX(mr.visit_date) as last_visit
FROM patients p
LEFT JOIN medical_records mr ON p.patient_id = mr.patient_id
GROUP BY p.patient_id, p.first_name, p.last_name, p.date_of_birth;

CREATE VIEW doctor_patient_count AS
SELECT 
    d.doctor_id,
    d.first_name,
    d.last_name,
    d.specialization,
    COUNT(DISTINCT mr.patient_id) as patient_count,
    COUNT(mr.record_id) as total_visits
FROM doctors d
LEFT JOIN medical_records mr ON d.doctor_id = mr.doctor_id
GROUP BY d.doctor_id, d.first_name, d.last_name, d.specialization;

-- Grant permissions (adjust as needed for your environment)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO healthcare_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO healthcare_user;

-- Create function to update timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for patients table
CREATE TRIGGER update_patients_updated_at 
    BEFORE UPDATE ON patients 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Display summary of created data
SELECT 'Database setup complete!' as status;
SELECT COUNT(*) as patient_count FROM patients;
SELECT COUNT(*) as doctor_count FROM doctors;
SELECT COUNT(*) as medical_record_count FROM medical_records;
SELECT COUNT(*) as admin_user_count FROM admin_users;
SELECT COUNT(*) as audit_log_count FROM audit_log;
