#!/usr/bin/env python3
"""
Sample Data Generation Script for Healthcare Security Research

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing

Generates realistic but fake healthcare data for security testing purposes.
Includes patients, doctors, medical records, and admin users with various
privilege levels for comprehensive security research.
"""

import os
import sys
import random
import bcrypt
from datetime import datetime, date, timedelta
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from models import Base, Patient, Doctor, MedicalRecord, AdminUser
from database import DatabaseManager


# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/data_generation.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="DEBUG",
    rotation="10 MB"
)

fake = Faker()


class HealthcareDataGenerator:
    """Generate comprehensive healthcare data for security research"""

    def __init__(self):
        logger.info("Initializing HealthcareDataGenerator")
        self.db_manager = DatabaseManager()
        self.session = self.db_manager.get_session()
        logger.success("Database session created")

        # SQL export file
        self.sql_export_file = f"sample_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        self.sql_statements = []

        # Medical specializations
        self.specializations = [
            'Cardiology', 'Neurology', 'Pediatrics', 'Oncology',
            'Orthopedics', 'Dermatology', 'Psychiatry', 'Emergency Medicine',
            'Internal Medicine', 'Surgery', 'Radiology', 'Anesthesiology',
            'Pathology', 'Family Medicine', 'Obstetrics and Gynecology',
            'Urology', 'Ophthalmology', 'ENT', 'Endocrinology', 'Gastroenterology'
        ]

        # Medical conditions for realistic diagnosis
        self.medical_conditions = [
            'Hypertension', 'Diabetes Type 2', 'Diabetes Type 1', 'Hyperlipidemia',
            'Asthma', 'COPD', 'Depression', 'Anxiety', 'Migraine', 'Arthritis',
            'Osteoporosis', 'Thyroid Disorder', 'Heart Disease', 'Stroke',
            'Cancer - Breast', 'Cancer - Lung', 'Cancer - Colon', 'Pneumonia',
            'Bronchitis', 'Allergies', 'Eczema', 'Psoriasis', 'GERD',
            'Kidney Disease', 'Liver Disease', 'Anemia', 'Sleep Apnea',
            'Fibromyalgia', 'Chronic Fatigue', 'Bipolar Disorder'
        ]

        # Common medications
        self.medications = [
            'Lisinopril', 'Metformin', 'Atorvastatin', 'Levothyroxine',
            'Amlodipine', 'Metoprolol', 'Omeprazole', 'Simvastatin',
            'Losartan', 'Gabapentin', 'Hydrochlorothiazide', 'Sertraline',
            'Furosemide', 'Prednisone', 'Tramadol', 'Albuterol',
            'Insulin', 'Aspirin', 'Ibuprofen', 'Acetaminophen'
        ]

        # Treatment descriptions
        self.treatments = [
            'Lifestyle modifications and medication management',
            'Physical therapy and exercise program',
            'Dietary counseling and nutrition plan',
            'Medication adjustment and monitoring',
            'Surgical consultation and evaluation',
            'Psychological counseling and therapy',
            'Regular monitoring and follow-up care',
            'Specialist referral for advanced treatment',
            'Emergency stabilization and monitoring',
            'Preventive care and health maintenance'
        ]

    def format_phone_number(self, max_length=15):
        """Generate a phone number that fits within the specified length"""
        # Generate a simple formatted phone number: (XXX) XXX-XXXX = 14 characters
        area = random.randint(200, 999)
        prefix = random.randint(200, 999)
        line = random.randint(1000, 9999)
        phone = f"({area}) {prefix}-{line}"

        # Ensure it doesn't exceed max_length
        if len(phone) > max_length:
            # Fallback to simple format: XXX-XXX-XXXX = 12 characters
            phone = f"{area}-{prefix}-{line}"

        logger.debug(f"Generated phone number: {phone} (length: {len(phone)})")
        return phone[:max_length]  # Truncate if still too long

    def escape_sql_string(self, value):
        """Escape single quotes for SQL"""
        if value is None:
            return 'NULL'
        if isinstance(value, str):
            return f"'{value.replace(chr(39), chr(39) + chr(39))}'"  # Escape single quotes
        if isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        if isinstance(value, (date, datetime)):
            return f"'{value.isoformat()}'"
        return str(value)

    def generate_patients(self, count: int = 150) -> list:
        """Generate realistic patient data"""
        patients = []

        logger.info(f"Starting generation of {count} patients")

        for i in range(count):
            try:
                # Generate realistic SSN format
                ssn = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"

                # Generate insurance ID
                insurance_id = f"INS{random.randint(100000, 999999)}"

                # Age distribution: more elderly patients for realistic healthcare data
                birth_year = random.choices(
                    range(1930, 2005),
                    weights=[1 if y < 1950 else 3 if y < 1970 else 5 if y < 1990 else 2 for y in range(1930, 2005)]
                )[0]

                birth_date = fake.date_of_birth(
                    minimum_age=datetime.now().year - birth_year - 1,
                    maximum_age=datetime.now().year - birth_year
                )

                first_name = fake.first_name()
                last_name = fake.last_name()
                phone = self.format_phone_number(15)
                email = fake.email()
                address = fake.address().replace('\n', ', ')[:200]  # Limit address length
                emergency_contact = f"{fake.name()} - {self.format_phone_number(15)}"[:100]  # Limit length

                patient = Patient(
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=birth_date,
                    ssn=ssn,
                    insurance_id=insurance_id,
                    phone_number=phone,
                    email=email,
                    address=address,
                    emergency_contact=emergency_contact
                )

                patients.append(patient)

                # Generate SQL INSERT statement
                sql = f"INSERT INTO patients (first_name, last_name, date_of_birth, ssn, insurance_id, phone_number, email, address, emergency_contact) VALUES ({self.escape_sql_string(first_name)}, {self.escape_sql_string(last_name)}, {self.escape_sql_string(birth_date)}, {self.escape_sql_string(ssn)}, {self.escape_sql_string(insurance_id)}, {self.escape_sql_string(phone)}, {self.escape_sql_string(email)}, {self.escape_sql_string(address)}, {self.escape_sql_string(emergency_contact)});"
                self.sql_statements.append(sql)

                if (i + 1) % 50 == 0:
                    logger.info(f"Generated {i + 1}/{count} patients")

            except Exception as e:
                logger.error(f"Error generating patient {i + 1}: {str(e)}")
                raise

        logger.success(f"Successfully generated {count} patients")
        return patients

    def generate_doctors(self, count: int = 25) -> list:
        """Generate realistic doctor data"""
        doctors = []

        logger.info(f"Starting generation of {count} doctors")

        for i in range(count):
            try:
                # Generate medical license number
                license_number = f"MD{random.randint(10000, 99999)}"

                # Hire date (within last 20 years, weighted toward more recent)
                hire_year = random.choices(
                    range(2004, 2024),
                    weights=[1 if y < 2010 else 3 if y < 2020 else 5 for y in range(2004, 2024)]
                )[0]

                hire_date = fake.date_between(
                    start_date=date(hire_year, 1, 1),
                    end_date=date(hire_year, 12, 31)
                )

                specialization = random.choice(self.specializations)
                first_name = fake.first_name()
                last_name = fake.last_name()
                phone = self.format_phone_number(15)
                email = fake.email()
                is_active = random.choice([True] * 9 + [False])  # 90% active

                doctor = Doctor(
                    first_name=first_name,
                    last_name=last_name,
                    specialization=specialization,
                    license_number=license_number,
                    phone_number=phone,
                    email=email,
                    department=specialization,
                    hire_date=hire_date,
                    is_active=is_active
                )

                doctors.append(doctor)

                # Generate SQL INSERT statement
                sql = f"INSERT INTO doctors (first_name, last_name, specialization, license_number, phone_number, email, department, hire_date, is_active) VALUES ({self.escape_sql_string(first_name)}, {self.escape_sql_string(last_name)}, {self.escape_sql_string(specialization)}, {self.escape_sql_string(license_number)}, {self.escape_sql_string(phone)}, {self.escape_sql_string(email)}, {self.escape_sql_string(specialization)}, {self.escape_sql_string(hire_date)}, {self.escape_sql_string(is_active)});"
                self.sql_statements.append(sql)

                logger.debug(f"Generated doctor: Dr. {first_name} {last_name} - {specialization}")

            except Exception as e:
                logger.error(f"Error generating doctor {i + 1}: {str(e)}")
                raise

        logger.success(f"Successfully generated {count} doctors")
        return doctors

    def generate_medical_records(self, patients: list, doctors: list, count: int = 800) -> list:
        """Generate realistic medical records"""
        medical_records = []

        logger.info(f"Starting generation of {count} medical records")

        for i in range(count):
            try:
                patient = random.choice(patients)
                doctor = random.choice([d for d in doctors if d.is_active])

                # Visit date (within last 3 years, weighted toward more recent)
                days_ago = random.choices(
                    range(1, 1096),  # 3 years
                    weights=[10 if d < 30 else 5 if d < 90 else 3 if d < 365 else 1 for d in range(1, 1096)]
                )[0]

                visit_date = datetime.now() - timedelta(days=days_ago)

                # Generate realistic diagnosis
                primary_condition = random.choice(self.medical_conditions)

                # 30% chance of multiple conditions
                if random.random() < 0.3:
                    secondary_condition = random.choice(self.medical_conditions)
                    diagnosis = f"{primary_condition}; {secondary_condition}"
                else:
                    diagnosis = primary_condition

                # Generate treatment based on condition
                treatment = random.choice(self.treatments)

                # Generate medication (80% of visits have medication)
                medication = None
                if random.random() < 0.8:
                    if 'diabetes' in diagnosis.lower():
                        medication = random.choice(['Metformin 500mg daily', 'Insulin as directed', 'Glipizide 5mg twice daily'])
                    elif 'hypertension' in diagnosis.lower():
                        medication = random.choice(['Lisinopril 10mg daily', 'Amlodipine 5mg daily', 'Metoprolol 50mg twice daily'])
                    elif 'depression' in diagnosis.lower():
                        medication = random.choice(['Sertraline 50mg daily', 'Fluoxetine 20mg daily', 'Escitalopram 10mg daily'])
                    else:
                        medication = f"{random.choice(self.medications)} as directed"

                # Generate notes (40% of records have detailed notes)
                notes = None
                if random.random() < 0.4:
                    note_types = [
                        "Patient responded well to treatment",
                        "Side effects reported, medication adjusted",
                        "Chronic condition requires ongoing monitoring",
                        "Patient education provided on lifestyle modifications",
                        "Referral to specialist recommended",
                        "Follow-up in 3 months",
                        "Patient non-compliant with medication regimen",
                        "Improvement noted since last visit"
                    ]
                    notes = random.choice(note_types)

                # Follow-up date (60% of visits have follow-up)
                follow_up_date = None
                if random.random() < 0.6:
                    follow_up_days = random.choice([7, 14, 30, 60, 90, 180])
                    follow_up_date = (visit_date + timedelta(days=follow_up_days)).date()

                # Confidential flag (10% of records)
                is_confidential = random.random() < 0.1

                medical_record = MedicalRecord(
                    patient_id=patient.patient_id,
                    doctor_id=doctor.doctor_id,
                    visit_date=visit_date,
                    diagnosis=diagnosis,
                    treatment=treatment,
                    medication=medication,
                    notes=notes,
                    follow_up_date=follow_up_date,
                    is_confidential=is_confidential
                )

                medical_records.append(medical_record)

                # Note: SQL generation for medical_records will use auto-generated IDs,
                # so we'll add a comment for manual adjustment
                sql = f"-- INSERT INTO medical_records (patient_id, doctor_id, visit_date, diagnosis, treatment, medication, notes, follow_up_date, is_confidential) VALUES (...patient_id..., ...doctor_id..., {self.escape_sql_string(visit_date)}, {self.escape_sql_string(diagnosis)}, {self.escape_sql_string(treatment)}, {self.escape_sql_string(medication)}, {self.escape_sql_string(notes)}, {self.escape_sql_string(follow_up_date)}, {self.escape_sql_string(is_confidential)});"
                self.sql_statements.append(sql)

                if (i + 1) % 100 == 0:
                    logger.info(f"Generated {i + 1}/{count} medical records")

            except Exception as e:
                logger.error(f"Error generating medical record {i + 1}: {str(e)}")
                raise

        logger.success(f"Successfully generated {count} medical records")
        return medical_records

    def generate_admin_users(self, patients: list) -> list:
        """Generate admin users with different roles"""
        admin_users = []

        logger.info("Starting generation of admin users")

        try:
            # Password for all test users (in production, use unique passwords)
            password_hash = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            logger.debug(f"Generated password hash (length: {len(password_hash)})")

            # Get email domain from config
            email_domain = Config.EMAIL_DOMAIN
            logger.info(f"Using email domain: {email_domain}")

            # System administrators
            admin_data = [
                ('admin', 'admin', 'System', 'Administrator', f'admin@{email_domain}'),
                ('security_admin', 'admin', 'Security', 'Administrator', f'security@{email_domain}')
            ]

            for username, role, first_name, last_name, email in admin_data:
                admin_users.append(AdminUser(
                    username=username,
                    password_hash=password_hash,
                    role=role,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    is_active=True
                ))
                logger.debug(f"Created admin user: {username}")

            # Doctor accounts
            doctor_accounts = [
                ('dr.smith', 'John', 'Smith', f'john.smith@{email_domain}'),
                ('dr.johnson', 'Sarah', 'Johnson', f'sarah.johnson@{email_domain}'),
                ('dr.williams', 'Michael', 'Williams', f'michael.williams@{email_domain}'),
                ('dr.brown', 'Emily', 'Brown', f'emily.brown@{email_domain}'),
                ('dr.davis', 'David', 'Davis', f'david.davis@{email_domain}')
            ]

            for username, first_name, last_name, email in doctor_accounts:
                admin_users.append(AdminUser(
                    username=username,
                    password_hash=password_hash,
                    role='doctor',
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    is_active=True
                ))
                logger.debug(f"Created doctor user: {username}")

            # Nurse accounts
            nurse_accounts = [
                ('nurse.wilson', 'Lisa', 'Wilson', f'lisa.wilson@{email_domain}'),
                ('nurse.garcia', 'Maria', 'Garcia', f'maria.garcia@{email_domain}'),
                ('nurse.martinez', 'Jennifer', 'Martinez', f'jennifer.martinez@{email_domain}'),
                ('nurse.anderson', 'Patricia', 'Anderson', f'patricia.anderson@{email_domain}')
            ]

            for username, first_name, last_name, email in nurse_accounts:
                admin_users.append(AdminUser(
                    username=username,
                    password_hash=password_hash,
                    role='nurse',
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    is_active=True
                ))
                logger.debug(f"Created nurse user: {username}")

            # Patient accounts (10 random patients get accounts)
            if len(patients) >= 10:
                selected_patients = random.sample(patients[:50], 10)  # Select from first 50 patients
                logger.info(f"Creating patient accounts for {len(selected_patients)} patients")

                for i, patient in enumerate(selected_patients):
                    username = f"patient.{patient.first_name.lower()}.{patient.last_name.lower()}"
                    username = username.replace(' ', '').replace("'", "")

                    admin_users.append(AdminUser(
                        username=username,
                        password_hash=password_hash,
                        role='patient',
                        first_name=patient.first_name,
                        last_name=patient.last_name,
                        email=patient.email,
                        is_active=True,
                        patient_id=patient.patient_id
                    ))
                    logger.debug(f"Created patient user: {username}")
            else:
                logger.warning("Not enough patients to create patient accounts")

            # Test accounts for security research
            test_accounts = [
                ('test_admin', 'admin', 'Test', 'Admin', f'test.admin@{email_domain}'),
                ('test_doctor', 'doctor', 'Test', 'Doctor', f'test.doctor@{email_domain}'),
                ('test_nurse', 'nurse', 'Test', 'Nurse', f'test.nurse@{email_domain}'),
                ('test_patient', 'patient', 'Test', 'Patient', f'test.patient@{email_domain}'),
                ('vulnerable_user', 'doctor', 'Vulnerable', 'User', f'vulnerable@{email_domain}'),
                ('attack_test', 'nurse', 'Attack', 'Test', f'attack.test@{email_domain}')
            ]

            for username, role, first_name, last_name, email in test_accounts:
                patient_id = None
                if role == 'patient' and patients:
                    patient_id = random.choice(patients[:10]).patient_id

                admin_users.append(AdminUser(
                    username=username,
                    password_hash=password_hash,
                    role=role,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    is_active=True,
                    patient_id=patient_id
                ))
                logger.debug(f"Created test user: {username} ({role})")

            # Generate SQL for admin users
            for user in admin_users:
                sql = f"INSERT INTO admin_users (username, password_hash, role, first_name, last_name, email, is_active, patient_id) VALUES ({self.escape_sql_string(user.username)}, {self.escape_sql_string(user.password_hash)}, {self.escape_sql_string(user.role)}, {self.escape_sql_string(user.first_name)}, {self.escape_sql_string(user.last_name)}, {self.escape_sql_string(user.email)}, {self.escape_sql_string(user.is_active)}, {self.escape_sql_string(user.patient_id)});"
                self.sql_statements.append(sql)

            logger.success(f"Successfully generated {len(admin_users)} admin users")
            return admin_users

        except Exception as e:
            logger.error(f"Error generating admin users: {str(e)}")
            raise

    def insert_data(self, entities: list, entity_type: str):
        """Insert data into database with batch processing"""
        try:
            batch_size = 50
            total = len(entities)

            logger.info(f"Inserting {total} {entity_type} records in batches of {batch_size}")

            for i in range(0, total, batch_size):
                batch = entities[i:i + batch_size]
                self.session.add_all(batch)
                self.session.commit()

                inserted_count = min(i + batch_size, total)
                logger.info(f"Inserted {inserted_count}/{total} {entity_type}")

            logger.success(f"Successfully inserted all {total} {entity_type} records!")

        except Exception as e:
            logger.error(f"Error inserting {entity_type}: {str(e)}")
            logger.exception("Full traceback:")
            self.session.rollback()
            raise

    def clear_existing_data(self):
        """Clear existing data for fresh generation"""
        logger.info("Clearing existing data from database")

        try:
            # Clear in reverse order due to foreign key constraints
            record_count = self.session.query(MedicalRecord).count()
            admin_count = self.session.query(AdminUser).count()
            doctor_count = self.session.query(Doctor).count()
            patient_count = self.session.query(Patient).count()

            logger.info(f"Deleting {record_count} medical records")
            self.session.query(MedicalRecord).delete()

            logger.info(f"Deleting {admin_count} admin users")
            self.session.query(AdminUser).delete()

            logger.info(f"Deleting {doctor_count} doctors")
            self.session.query(Doctor).delete()

            logger.info(f"Deleting {patient_count} patients")
            self.session.query(Patient).delete()

            self.session.commit()
            logger.success("Existing data cleared successfully!")

        except Exception as e:
            logger.error(f"Error clearing data: {str(e)}")
            self.session.rollback()
            raise

    def export_sql_file(self):
        """Export all SQL statements to a file"""
        try:
            logger.info(f"Exporting SQL statements to {self.sql_export_file}")

            with open(self.sql_export_file, 'w', encoding='utf-8') as f:
                # Write header
                f.write("-- Healthcare Security Research Platform\n")
                f.write(f"-- Sample Data SQL Export\n")
                f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-- WARNING: This data is for testing purposes only\n")
                f.write("--          Contains fake SSNs and personal information\n\n")

                f.write("-- Begin transaction\n")
                f.write("BEGIN;\n\n")

                # Write SQL statements
                f.write("-- Generated INSERT statements\n")
                for sql in self.sql_statements:
                    f.write(sql + "\n")

                f.write("\n-- Commit transaction\n")
                f.write("COMMIT;\n")

            file_size = os.path.getsize(self.sql_export_file)
            logger.success(f"SQL export complete: {self.sql_export_file} ({file_size:,} bytes)")

        except Exception as e:
            logger.error(f"Error exporting SQL file: {str(e)}")
            raise

    def generate_all_data(self, clear_existing: bool = True):
        """Generate complete dataset"""
        try:
            if clear_existing:
                self.clear_existing_data()

            logger.info("=" * 60)
            logger.info("Starting comprehensive data generation")
            logger.info("=" * 60)
            start_time = datetime.now()

            # Generate and insert patients
            logger.info("Phase 1/4: Generating patients")
            patients = self.generate_patients(150)
            self.insert_data(patients, "patients")

            # Generate and insert doctors
            logger.info("Phase 2/4: Generating doctors")
            doctors = self.generate_doctors(25)
            self.insert_data(doctors, "doctors")

            # Refresh patient and doctor IDs after insertion
            logger.info("Refreshing patient and doctor data from database")
            self.session.commit()
            patients = self.session.query(Patient).all()
            doctors = self.session.query(Doctor).all()
            logger.info(f"Loaded {len(patients)} patients and {len(doctors)} doctors from database")

            # Generate and insert medical records
            logger.info("Phase 3/4: Generating medical records")
            medical_records = self.generate_medical_records(patients, doctors, 800)
            self.insert_data(medical_records, "medical records")

            # Generate and insert admin users
            logger.info("Phase 4/4: Generating admin users")
            admin_users = self.generate_admin_users(patients)
            self.insert_data(admin_users, "admin users")

            # Export SQL file
            logger.info("Exporting data to SQL file")
            self.export_sql_file()

            end_time = datetime.now()
            duration = end_time - start_time

            logger.info("=" * 60)
            logger.success(f"Data generation completed in {duration.total_seconds():.2f} seconds!")
            logger.info("=" * 60)

            # Print summary
            self.print_data_summary()

        except Exception as e:
            logger.error(f"Error during data generation: {str(e)}")
            logger.exception("Full traceback:")
            self.session.rollback()
            raise
        finally:
            self.session.close()
            logger.info("Database session closed")

    def print_data_summary(self):
        """Print summary of generated data"""
        logger.info("\n" + "=" * 60)
        logger.info("DATA GENERATION SUMMARY")
        logger.info("=" * 60)

        try:
            patient_count = self.session.query(Patient).count()
            doctor_count = self.session.query(Doctor).count()
            record_count = self.session.query(MedicalRecord).count()
            admin_count = self.session.query(AdminUser).count()

            logger.info(f"Patients:        {patient_count:,}")
            logger.info(f"Doctors:         {doctor_count:,}")
            logger.info(f"Medical Records: {record_count:,}")
            logger.info(f"Admin Users:     {admin_count:,}")

            # Role distribution
            logger.info("\nUser Role Distribution:")
            role_counts = {}
            for user in self.session.query(AdminUser).all():
                role_counts[user.role] = role_counts.get(user.role, 0) + 1

            for role, count in sorted(role_counts.items()):
                logger.info(f"  {role:15} : {count:3}")

            logger.info("\nTest Accounts (username/password: password123):")
            test_accounts = [
                "  admin/password123          - System Administrator",
                "  dr.smith/password123       - Doctor",
                "  nurse.wilson/password123   - Nurse",
                "  test_admin/password123     - Test Administrator",
                "  test_doctor/password123    - Test Doctor",
                "  vulnerable_user/password123 - Vulnerable Test Account"
            ]
            for account in test_accounts:
                logger.info(account)

            logger.info(f"\nSQL Export File: {self.sql_export_file}")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")


def main():
    """Main function to run data generation"""
    logger.info("=" * 60)
    logger.info("Healthcare Security Research - Sample Data Generator")
    logger.info("=" * 60)

    try:
        generator = HealthcareDataGenerator()

        # Check if data already exists
        existing_patients = generator.session.query(Patient).count()

        if existing_patients > 0:
            logger.warning(f"Database contains {existing_patients} patients")
            response = input(f"\nClear existing data and regenerate? (y/N): ")
            clear_existing = response.lower() in ['y', 'yes']
        else:
            logger.info("Database is empty, proceeding with data generation")
            clear_existing = True

        generator.generate_all_data(clear_existing=clear_existing)

        logger.info("\n" + "=" * 60)
        logger.info("SECURITY TESTING NOTES")
        logger.info("=" * 60)
        notes = [
            "This data is generated for security research purposes:",
            "- All SSNs are fake and follow XXX-XX-XXXX format",
            "- All personal information is generated using Faker library",
            "- Medical conditions and treatments are realistic but anonymized",
            "- Test accounts use 'password123' for vulnerability testing",
            "- Data includes various privilege levels for access control testing",
            "- Phone numbers are formatted to fit database constraints"
        ]
        for note in notes:
            logger.info(note)
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.warning("\nData generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nFatal error: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
