#!/usr/bin/env python3
"""
Setup Script for Healthcare Security Research API

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing

Automates the installation and configuration process for the healthcare
database security research environment.
"""

import os
import sys
import subprocess
import shutil
import getpass
from pathlib import Path


class HealthcareSecuritySetup:
    """Setup manager for the healthcare security research environment"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.env_file = self.project_root / ".env"
        
    def print_header(self, message):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"{message}")
        print(f"{'='*60}")
    
    def print_step(self, step_num, message):
        """Print formatted step"""
        print(f"\n[Step {step_num}] {message}")
        print("-" * 40)
    
    def run_command(self, command, shell=True, check=True):
        """Run system command with error handling"""
        try:
            result = subprocess.run(
                command, 
                shell=shell, 
                check=check, 
                capture_output=True, 
                text=True
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
    
    def check_prerequisites(self):
        """Check system prerequisites"""
        self.print_step(1, "Checking Prerequisites")
        
        prerequisites = {
            'python': 'python --version',
            'pip': 'pip --version',
            'git': 'git --version'
        }
        
        missing = []
        
        for tool, command in prerequisites.items():
            success, stdout, stderr = self.run_command(command, check=False)
            if success:
                version = stdout.strip().split('\n')[0]
                print(f"✓ {tool}: {version}")
            else:
                print(f"✗ {tool}: Not found")
                missing.append(tool)
        
        if missing:
            print(f"\nMissing prerequisites: {', '.join(missing)}")
            print("Please install missing tools and run setup again.")
            return False
        
        # Check Python version
        if sys.version_info < (3, 12):
            print("✗ Python 3.12+ or higher is required")
            return False
        
        print("✓ All prerequisites met")
        return True
    
    def setup_virtual_environment(self):
        """Create and setup virtual environment"""
        self.print_step(2, "Setting up Virtual Environment")
        
        if self.venv_path.exists():
            response = input("Virtual environment exists. Recreate? (y/N): ")
            if response.lower() in ['y', 'yes']:
                shutil.rmtree(self.venv_path)
            else:
                print("Using existing virtual environment")
                return True
        
        print("Creating virtual environment...")
        success, stdout, stderr = self.run_command(f"uv venv {self.venv_path}")
        
        if not success:
            print(f"✗ Failed to create virtual environment: {stderr}")
            return False
        
        print("✓ Virtual environment created")
        
        # Get activation command
        if os.name == 'nt':  # Windows
            activate_cmd = f"{self.venv_path}\\Scripts\\activate.bat"
            pip_cmd = "uv pip"
        else:  # Unix-like
            activate_cmd = f"source {self.venv_path}/bin/activate"
            pip_cmd = "uv pip"

        print(f"Virtual environment activation command: {activate_cmd}")

        # Install requirements
        print("Installing Python dependencies...")
        requirements_file = self.project_root / "requirements.txt"

        if requirements_file.exists():
            success, stdout, stderr = self.run_command(f"{pip_cmd} install -r {requirements_file}")
            if success:
                print("✓ Dependencies installed successfully")
            else:
                print(f"✗ Failed to install dependencies: {stderr}")
                return False
        else:
            print("⚠ requirements.txt not found, skipping dependency installation")
        
        return True
    
    def configure_environment(self):
        """Configure environment variables"""
        self.print_step(3, "Environment Configuration")
        
        if self.env_file.exists():
            response = input(".env file exists. Overwrite? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("Using existing .env file")
                return True
        
        print("Configuring environment variables...")
        
        # Gather configuration
        config = {}
        
        print("\nDatabase Configuration:")
        config['DB_HOST'] = input("Database host [192.168.100.30]: ") or "192.168.100.30"
        config['DB_PORT'] = input("Database port [5432]: ") or "5432"
        config['DB_NAME'] = input("Database name [healthcare_security]: ") or "healthcare_security"
        config['DB_USER'] = input("Database user [healthcare_user]: ") or "healthcare_user"
        config['DB_PASSWORD'] = getpass.getpass("Database password [secure_password_123]: ") or "secure_password_123"
        
        print("\nLLM Service Configuration:")
        config['LLM_HOST'] = input("LLM host [192.168.100.1]: ") or "192.168.100.1"
        config['LLM_PORT'] = input("LLM port [11434]: ") or "11434"
        config['LLM_MODEL'] = input("LLM model [llama3.1]: ") or "llama3.1"
        
        print("\nSecurity Configuration:")
        config['SECURITY_MODE'] = input("Security mode [vulnerable]: ") or "vulnerable"
        config['SECRET_KEY'] = input("Secret key [auto-generate]: ") or self.generate_secret_key()
        config['JWT_SECRET_KEY'] = input("JWT secret key [use SECRET_KEY]: ") or config['SECRET_KEY']
        
        print("\nLogging Configuration:")
        config['LOG_LEVEL'] = input("Log level [INFO]: ") or "INFO"
        config['LOG_FILE'] = input("Log file [healthcare_security.log]: ") or "healthcare_security.log"
        config['AUDIT_LOG_FILE'] = input("Audit log file [security_audit.log]: ") or "security_audit.log"
        
        # Write .env file
        with open(self.env_file, 'w') as f:
            f.write("# Healthcare Security Research API Configuration\n")
            f.write("# Generated by setup script\n\n")
            
            f.write("# Database Configuration\n")
            f.write(f"DB_HOST={config['DB_HOST']}\n")
            f.write(f"DB_PORT={config['DB_PORT']}\n")
            f.write(f"DB_NAME={config['DB_NAME']}\n")
            f.write(f"DB_USER={config['DB_USER']}\n")
            f.write(f"DB_PASSWORD={config['DB_PASSWORD']}\n\n")
            
            f.write("# LLM Service Configuration\n")
            f.write(f"LLM_HOST={config['LLM_HOST']}\n")
            f.write(f"LLM_PORT={config['LLM_PORT']}\n")
            f.write(f"LLM_MODEL={config['LLM_MODEL']}\n\n")
            
            f.write("# Security Configuration\n")
            f.write(f"SECURITY_MODE={config['SECURITY_MODE']}\n")
            f.write(f"SECRET_KEY={config['SECRET_KEY']}\n")
            f.write(f"JWT_SECRET_KEY={config['JWT_SECRET_KEY']}\n\n")
            
            f.write("# Logging Configuration\n")
            f.write(f"LOG_LEVEL={config['LOG_LEVEL']}\n")
            f.write(f"LOG_FILE={config['LOG_FILE']}\n")
            f.write(f"AUDIT_LOG_FILE={config['AUDIT_LOG_FILE']}\n")
        
        print("✓ Environment configuration saved to .env")
        return True
    
    def generate_secret_key(self):
        """Generate a random secret key"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def setup_database(self):
        """Setup database schema"""
        self.print_step(4, "Database Setup")
        
        schema_file = self.project_root / "setup_database.sql"
        if not schema_file.exists():
            print("✗ setup_database.sql not found")
            return False
        
        # Load environment variables to get DB config
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME', 'healthcare_security')
        db_user = os.environ.get('DB_USER', 'healthcare_user')
        db_password = os.environ.get('DB_PASSWORD', 'secure_password_123')
        
        print(f"Connecting to database: {db_user}@{db_host}:{db_port}/{db_name}")
        
        # Check if psql is available
        success, _, _ = self.run_command("psql --version", check=False)
        if not success:
            print("⚠ psql not found. Please run the schema manually:")
            print(f"psql -h {db_host} -p {db_port} -U {db_user} -d {db_name} -f {schema_file}")
            return True
        
        # Set password environment variable for psql
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password
        
        # Run schema setup
        command = f"psql -h {db_host} -p {db_port} -U {db_user} -d {db_name} -f {schema_file}"
        
        print("Running database schema setup...")
        process = subprocess.Popen(
            command,
            shell=True,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print("✓ Database schema created successfully")
            print("✓ Sample data inserted")
            return True
        else:
            print(f"✗ Database setup failed: {stderr}")
            print(f"Command output: {stdout}")
            return False
    
    def generate_sample_data(self):
        """Generate sample data"""
        self.print_step(5, "Sample Data Generation")
        
        data_script = self.project_root / "generate_sample_data.py"
        if not data_script.exists():
            print("✗ generate_sample_data.py not found")
            return False
        
        response = input("Generate sample data? (Y/n): ")
        if response.lower() in ['n', 'no']:
            print("Skipping sample data generation")
            return True
        
        # Get python command for virtual environment
        if os.name == 'nt':  # Windows
            python_cmd = f"{self.venv_path}\\Scripts\\python.exe"
        else:  # Unix-like
            python_cmd = f"{self.venv_path}/bin/python"
        
        print("Generating sample data...")
        success, stdout, stderr = self.run_command(f"{python_cmd} {data_script}")
        
        if success:
            print("✓ Sample data generated successfully")
            return True
        else:
            print(f"✗ Sample data generation failed: {stderr}")
            return False
    
    def verify_installation(self):
        """Verify the installation"""
        self.print_step(6, "Installation Verification")
        
        print("Verifying installation...")
        
        # Check files
        required_files = [
            'app.py', 'config.py', 'database.py', 'llm_client.py',
            'security.py', 'models.py', 'utils.py', '.env'
        ]
        
        missing_files = []
        for file in required_files:
            if (self.project_root / file).exists():
                print(f"✓ {file}")
            else:
                print(f"✗ {file}")
                missing_files.append(file)
        
        if missing_files:
            print(f"Missing files: {', '.join(missing_files)}")
            return False
        
        # Test database connection (if possible)
        try:
            if os.name == 'nt':  # Windows
                python_cmd = f"{self.venv_path}\\Scripts\\python.exe"
            else:  # Unix-like
                python_cmd = f"{self.venv_path}/bin/python"
            
            test_script = '''
import sys
sys.path.append(".")
try:
    from database import DatabaseManager
    db = DatabaseManager()
    db.test_connection()
    print("✓ Database connection successful")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
'''
            
            with open('test_connection.py', 'w') as f:
                f.write(test_script)
            
            success, stdout, stderr = self.run_command(f"{python_cmd} test_connection.py")
            print(stdout.strip())
            
            os.remove('test_connection.py')
            
        except Exception as e:
            print(f"⚠ Could not test database connection: {e}")
        
        print("✓ Installation verification complete")
        return True
    
    def print_completion_message(self):
        """Print setup completion message"""
        self.print_header("Setup Complete!")
        
        print("Your Healthcare Security Research API is ready!")
        print("\nNext steps:")
        print("1. Activate the virtual environment:")
        
        if os.name == 'nt':  # Windows
            print(f"   {self.venv_path}\\Scripts\\activate.bat")
        else:  # Unix-like
            print(f"   source {self.venv_path}/bin/activate")
        
        print("\n2. Start the application:")
        print("   python app.py")
        
        print("\n3. Access the API:")
        print("   http://localhost:5000")
        
        print("\n4. Run security tests:")
        print("   python attack_scenarios.py --mode compare")
        
        print("\nDefault test accounts (password: password123):")
        print("   admin - System administrator")
        print("   test_doctor - Doctor role testing")
        print("   test_nurse - Nurse role testing")
        print("   vulnerable_user - Vulnerability testing")
        
        print("\nFor more information, see README.md")
        print("\n⚠️  Remember: This is for research purposes only!")
    
    def run_full_setup(self):
        """Run complete setup process"""
        self.print_header("Healthcare Security Research API Setup")
        
        steps = [
            self.check_prerequisites,
            self.setup_virtual_environment,
            self.configure_environment,
            self.setup_database,
            self.generate_sample_data,
            self.verify_installation
        ]
        
        for i, step in enumerate(steps, 1):
            try:
                if not step():
                    print(f"\n✗ Setup failed at step {i}")
                    return False
            except KeyboardInterrupt:
                print("\n\nSetup interrupted by user")
                return False
            except Exception as e:
                print(f"\n✗ Unexpected error in step {i}: {e}")
                return False
        
        self.print_completion_message()
        return True


def main():
    """Main setup function"""
    setup = HealthcareSecuritySetup()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--quick':
            # Quick setup with defaults
            if (setup.check_prerequisites() and 
                setup.setup_virtual_environment() and
                setup.configure_environment() and
                setup.verify_installation()):
                setup.print_completion_message()
        elif sys.argv[1] == '--help':
            print("Healthcare Security Research API Setup")
            print("Usage:")
            print("  python setup.py         - Full interactive setup")
            print("  python setup.py --quick - Quick setup with defaults")
            print("  python setup.py --help  - Show this help")
    else:
        # Full interactive setup
        setup.run_full_setup()


if __name__ == "__main__":
    main()