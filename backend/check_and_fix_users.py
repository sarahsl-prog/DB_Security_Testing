#!/usr/bin/env python3
"""
Script to check and fix database users for Healthcare Security Research Platform
"""

import sys
import os
import bcrypt

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import DatabaseManager
    from models import AdminUser
    from datetime import datetime

    print("=" * 60)
    print("Healthcare Database User Check & Fix")
    print("=" * 60)

    db = DatabaseManager()
    session = db.get_session()

    # Check existing users
    print("\n[1] Checking existing users...")
    existing_users = session.query(AdminUser).all()

    if existing_users:
        print(f"\n✓ Found {len(existing_users)} existing users:")
        for user in existing_users:
            print(f"  - {user.username} ({user.role}) - Active: {user.is_active}")
    else:
        print("\n✗ No users found in database!")

    # Define demo users that should exist
    demo_users = [
        {
            'username': 'admin',
            'password': 'password123',
            'role': 'admin',
            'first_name': 'System',
            'last_name': 'Administrator',
            'email': 'admin@hospital.com',
            'patient_id': None
        },
        {
            'username': 'testuser',
            'password': 'password123',
            'role': 'doctor',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@hospital.com',
            'patient_id': None
        },
        {
            'username': 'dr.johnson',
            'password': 'password123',
            'role': 'doctor',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'email': 'sarah.johnson@hospital.com',
            'patient_id': None
        },
        {
            'username': 'nurse.smith',
            'password': 'password123',
            'role': 'nurse',
            'first_name': 'Emily',
            'last_name': 'Smith',
            'email': 'emily.smith@hospital.com',
            'patient_id': None
        },
        {
            'username': 'patient.john',
            'password': 'password123',
            'role': 'patient',
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@email.com',
            'patient_id': 1
        },
        {
            'username': 'dr.chen',
            'password': 'password123',
            'role': 'doctor',
            'first_name': 'Michael',
            'last_name': 'Chen',
            'email': 'michael.chen@hospital.com',
            'patient_id': None
        },
        {
            'username': 'nurse.brown',
            'password': 'password123',
            'role': 'nurse',
            'first_name': 'Laura',
            'last_name': 'Brown',
            'email': 'laura.brown@hospital.com',
            'patient_id': None
        },
        {
            'username': 'patient.mary',
            'password': 'password123',
            'role': 'patient',
            'first_name': 'Mary',
            'last_name': 'Johnson',
            'email': 'mary.johnson@email.com',
            'patient_id': 2
        }
    ]

    print("\n[2] Checking for missing demo users...")
    existing_usernames = {user.username for user in existing_users}
    missing_users = [u for u in demo_users if u['username'] not in existing_usernames]

    if missing_users:
        print(f"\n✗ Found {len(missing_users)} missing users:")
        for user in missing_users:
            print(f"  - {user['username']} ({user['role']})")

        response = input("\nWould you like to add these users? (yes/no): ").lower()

        if response in ['yes', 'y']:
            print("\n[3] Adding missing users...")
            for user_data in missing_users:
                # Hash the password
                password_hash = bcrypt.hashpw(
                    user_data['password'].encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')

                # Create new user
                new_user = AdminUser(
                    username=user_data['username'],
                    password_hash=password_hash,
                    role=user_data['role'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    patient_id=user_data['patient_id'],
                    is_active=True,
                    failed_login_attempts=0
                )

                session.add(new_user)
                print(f"  ✓ Added {user_data['username']}")

            session.commit()
            print("\n✓ All users added successfully!")
        else:
            print("\nSkipping user addition.")
    else:
        print("\n✓ All demo users already exist!")

    # Test authentication for each demo user
    print("\n[4] Testing authentication for demo users...")
    test_results = []

    for user_data in demo_users:
        user = db.authenticate_user(user_data['username'], user_data['password'])
        if user:
            test_results.append((user_data['username'], '✓ PASS', user.role))
        else:
            test_results.append((user_data['username'], '✗ FAIL', '-'))

    print("\nAuthentication Test Results:")
    print("-" * 60)
    for username, status, role in test_results:
        print(f"  {username:20s} {status:10s} {role:10s}")

    passed = sum(1 for _, status, _ in test_results if '✓' in status)
    total = len(test_results)

    print("-" * 60)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n✓ All authentication tests passed!")
        print("\n" + "=" * 60)
        print("Demo Credentials (copy to frontend):")
        print("=" * 60)
        for user_data in demo_users[:5]:  # Show first 5
            print(f"  {user_data['username']} / {user_data['password']}")
        print("=" * 60)
    else:
        print("\n✗ Some authentication tests failed!")
        print("Please check the database and password hashing.")

    session.close()

except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
