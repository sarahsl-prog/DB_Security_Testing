#!/usr/bin/env python3
"""
Login Diagnostic Tool for Healthcare Security API

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing

This script checks:
1. Database connectivity
2. Admin users exist
3. Password hashing works
4. Sample data is loaded
5. API authentication works

Run this when login fails to diagnose the issue.
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import DatabaseManager
    from models import AdminUser, Patient
    import bcrypt
    import requests
    from sqlalchemy import text
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("\nPlease run: pip install -r requirements.txt")
    sys.exit(1)


class LoginDiagnostic:
    """Diagnose login issues"""

    def __init__(self):
        self.db_manager = None
        self.issues = []
        self.warnings = []

    def print_header(self, text):
        print(f"\n{'='*70}")
        print(f"{text.center(70)}")
        print(f"{'='*70}\n")

    def print_check(self, check_name, passed, details=""):
        symbol = "✓" if passed else "✗"
        status = "PASS" if passed else "FAIL"
        print(f"{symbol} {check_name:<50} [{status}]")
        if details:
            print(f"  → {details}")
        if not passed:
            self.issues.append(f"{check_name}: {details}")

    def print_warning(self, message):
        print(f"⚠ WARNING: {message}")
        self.warnings.append(message)

    def check_database_connection(self):
        """Check database connectivity"""
        self.print_header("DATABASE CONNECTIVITY CHECK")

        try:
            self.db_manager = DatabaseManager()
            connection_ok = self.db_manager.test_connection()
            self.print_check("Database Connection", connection_ok,
                           "Successfully connected to PostgreSQL")
            return connection_ok
        except Exception as e:
            self.print_check("Database Connection", False, str(e))
            return False

    def check_admin_users_exist(self):
        """Check if admin users table exists and has data"""
        self.print_header("ADMIN USERS CHECK")

        try:
            session = self.db_manager.get_session()

            # Check if table exists
            result = session.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables "
                "WHERE table_name = 'admin_users')"
            ))
            table_exists = result.scalar()

            self.print_check("Admin Users Table Exists", table_exists)

            if not table_exists:
                self.print_warning("Run: python generate_sample_data.py")
                return False

            # Check if there are any users
            user_count = session.query(AdminUser).count()
            self.print_check("Admin Users Exist", user_count > 0,
                           f"Found {user_count} users in database")

            if user_count == 0:
                self.print_warning("No users found. Run: python generate_sample_data.py")
                return False

            # List available users
            print("\n  Available Users:")
            users = session.query(AdminUser).limit(10).all()
            for user in users:
                print(f"    • {user.username:<20} (Role: {user.role})")

            session.close()
            return user_count > 0

        except Exception as e:
            self.print_check("Admin Users Check", False, str(e))
            return False

    def check_sample_data(self):
        """Check if sample data is loaded"""
        self.print_header("SAMPLE DATA CHECK")

        try:
            session = self.db_manager.get_session()

            # Check patients
            patient_count = session.query(Patient).count()
            self.print_check("Patients Loaded", patient_count > 0,
                           f"Found {patient_count} patients")

            # Check if specific test users exist
            test_users = ['admin', 'dr.smith', 'nurse.wilson']
            for username in test_users:
                user = session.query(AdminUser).filter(
                    AdminUser.username == username
                ).first()
                exists = user is not None
                self.print_check(f"User '{username}' exists", exists,
                               f"Role: {user.role}" if exists else "Not found")

            session.close()
            return True

        except Exception as e:
            self.print_check("Sample Data Check", False, str(e))
            return False

    def test_password_verification(self):
        """Test password hashing and verification"""
        self.print_header("PASSWORD VERIFICATION TEST")

        try:
            # Test password hashing
            test_password = "password123"
            hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())

            # Test verification
            verify_correct = bcrypt.checkpw(test_password.encode('utf-8'), hashed)
            self.print_check("Password Hashing Works", verify_correct,
                           "bcrypt is functioning correctly")

            verify_wrong = bcrypt.checkpw("wrongpassword".encode('utf-8'), hashed)
            self.print_check("Password Rejection Works", not verify_wrong,
                           "Incorrect passwords are rejected")

            # Test with actual user
            session = self.db_manager.get_session()
            admin_user = session.query(AdminUser).filter(
                AdminUser.username == 'admin'
            ).first()

            if admin_user:
                can_auth = bcrypt.checkpw(
                    test_password.encode('utf-8'),
                    admin_user.password_hash.encode('utf-8')
                )
                self.print_check("Admin User Password", can_auth,
                               "password123" if can_auth else "Password mismatch")

            session.close()
            return True

        except Exception as e:
            self.print_check("Password Verification", False, str(e))
            return False

    def test_api_authentication(self, api_url="http://localhost:5000"):
        """Test actual API authentication"""
        self.print_header("API AUTHENTICATION TEST")

        try:
            # Test with admin credentials
            response = requests.post(
                f"{api_url}/api/login",
                json={"username": "admin", "password": "password123"},
                timeout=10
            )

            success = response.status_code == 200
            if success:
                data = response.json()
                has_token = 'token' in data
                self.print_check("API Login Success", has_token,
                               f"Token received: {data['token'][:20]}..." if has_token else "No token")
            else:
                self.print_check("API Login", False,
                               f"HTTP {response.status_code}: {response.text[:100]}")

            return success

        except requests.exceptions.ConnectionError:
            self.print_check("API Connection", False,
                           f"Cannot connect to {api_url} - Is the API running?")
            return False
        except Exception as e:
            self.print_check("API Authentication", False, str(e))
            return False

    def print_summary(self):
        """Print diagnostic summary"""
        self.print_header("DIAGNOSTIC SUMMARY")

        if not self.issues and not self.warnings:
            print("✅ All checks passed! Login should work correctly.\n")
            print("Test login with:")
            print("  Username: admin")
            print("  Password: password123")
            return True

        if self.warnings:
            print("⚠ WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()

        if self.issues:
            print("❌ ISSUES FOUND:")
            for issue in self.issues:
                print(f"  • {issue}")
            print()

            print("RECOMMENDED FIXES:")

            if any("Database" in issue for issue in self.issues):
                print("\n1. Check database is running:")
                print("   psql -h 192.168.100.30 -U healthcare_user -d healthcare_security")

            if any("users" in issue.lower() for issue in self.issues):
                print("\n2. Load sample data:")
                print("   python generate_sample_data.py")

            if any("API" in issue for issue in self.issues):
                print("\n3. Start the API server:")
                print("   python app.py")

            return False

    def run_all_diagnostics(self):
        """Run all diagnostic checks"""
        print("\n" + "="*70)
        print("HEALTHCARE SECURITY API - LOGIN DIAGNOSTIC TOOL".center(70))
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(70))
        print("="*70)

        # Run checks in order
        db_ok = self.check_database_connection()

        if db_ok:
            self.check_admin_users_exist()
            self.check_sample_data()
            self.test_password_verification()

        self.test_api_authentication()

        # Print summary
        success = self.print_summary()

        return success


def main():
    """Main entry point"""
    diagnostic = LoginDiagnostic()
    success = diagnostic.run_all_diagnostics()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
