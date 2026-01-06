-- Healthcare Security Research Database Schema
-- Creates realistic healthcare database for security testing
-- Supports both vulnerable and secure mode research

-- Create database (run separately if needed)
-- CREATE DATABASE healthcare_security;
-- \c healthcare_security;

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS medical_records CASCADE;
DROP TABLE IF EXISTS admin_users CASCADE;
DROP TABLE IF EXISTS doctors CASCADE;
DROP TABLE IF EXISTS patients CASCADE;

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