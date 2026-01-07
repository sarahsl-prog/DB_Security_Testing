<div align="center">
  <img src="app-LOGO2.jpg" alt="Healthcare Database Security Testing Logo" width="200"/>

  # Healthcare Database Security Testing API

  A comprehensive Flask-based API designed for researching SQL injection vulnerabilities and defense mechanisms in healthcare database systems. This project supports both vulnerable and secure modes for educational security testing and research purposes.
</div>

## ⚠️ SECURITY NOTICE

This application is designed for **educational and research purposes only**. It contains intentionally vulnerable components for security testing. Do not use in production environments or expose to public networks.

## Architecture Overview

The system uses a distributed architecture across multiple VMs:

- **Flask API Server**: Ubuntu VM (192.168.100.20:5000)
- **LLM Service**: Ollama on Windows host (192.168.100.1:11434)
- **Database**: PostgreSQL on Ubuntu VM (192.168.100.30:5432)
- **Frontend**: Static files served by Apache2 (proxies /api/* to Flask)

## Features

### Core Functionality
- Natural language to SQL conversion using Ollama LLM
- Dual security modes (vulnerable/secure) for research
- Role-based access controls (admin, doctor, nurse, patient)
- Comprehensive audit logging and security monitoring
- Realistic healthcare database with PHI for testing

### Security Research Features
- SQL injection detection and prevention
- Prompt injection resistance testing
- Privilege escalation detection
- Data exfiltration monitoring
- Security event analysis and reporting

### API Endpoints
- `POST /api/query` - Process natural language to SQL conversion
- `GET /api/schema` - Return database schema for LLM context
- `POST /api/login` - User authentication and role assignment
- `GET /api/audit` - Security audit logs (admin only)
- `GET /api/health` - Service health check for all components
- `POST /api/validate` - Test query validation without execution

## Quick Start

### Prerequisites

1. **Python 3.12+**
2. **PostgreSQL 17+**
3. **Ollama** (running on Windows host)
4. **Git**

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd healthcare_security_api

# Create virtual environment
uv venv venv

# Activate virtual environment
# On Windows:
venv\\Scripts\\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE healthcare_security;
CREATE USER healthcare_user WITH PASSWORD 'secure_password_123';
GRANT ALL PRIVILEGES ON DATABASE healthcare_security TO healthcare_user;
\\q
```

```bash
# Run schema setup
psql -h localhost -U healthcare_user -d healthcare_security -f setup_database.sql
```

### 3. Environment Configuration

Create `.env` file:

```bash
# Database Configuration
DB_HOST=192.168.100.30
DB_PORT=5432
DB_NAME=healthcare_security
DB_USER=healthcare_user
DB_PASSWORD=secure_password_123

# LLM Service Configuration
LLM_HOST=192.168.100.1
LLM_PORT=11434
LLM_MODEL=llama3.1

# Security Configuration
SECURITY_MODE=vulnerable
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Logging
LOG_LEVEL=INFO
LOG_FILE=healthcare_security.log
AUDIT_LOG_FILE=security_audit.log
```

### 4. Generate Sample Data

```bash
python generate_sample_data.py
```

This creates:
- 150 realistic patient records
- 25 doctor profiles
- 800+ medical records
- Admin users with different roles

### 5. Start the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Security Testing

### Authentication

Default test accounts (password: `password123`):

| Username | Role | Purpose |
|----------|------|---------|
| `admin` | admin | System administration |
| `test_doctor` | doctor | Doctor role testing |
| `test_nurse` | nurse | Nurse role testing |
| `test_patient` | patient | Patient role testing |
| `vulnerable_user` | doctor | Vulnerability testing |

### Running Security Tests

```bash
# Run comprehensive security test
python attack_scenarios.py --mode compare

# Test specific mode
python attack_scenarios.py --mode vulnerable
python attack_scenarios.py --mode secure

# Custom authentication
python attack_scenarios.py --username admin --password password123
```

### Example API Usage

#### Authentication
```bash
curl -X POST http://localhost:5000/api/login \\
  -H "Content-Type: application/json" \\
  -d '{"username": "test_doctor", "password": "password123"}'
```

#### Query Processing
```bash
curl -X POST http://localhost:5000/api/query \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
  -d '{
    "question": "Show me patients with diabetes",
    "security_mode": "vulnerable"
  }'
```

#### Health Check
```bash
curl http://localhost:5000/api/health
```

## Security Modes

### Vulnerable Mode (Default)
- Minimal input validation
- Direct SQL execution from LLM
- Basic role checking only
- Limited audit logging
- Useful for demonstrating attacks

### Secure Mode
- Input sanitization and validation
- SQL query analysis and filtering
- Strict role-based access controls
- Comprehensive audit logging
- Query result filtering based on permissions

## Attack Scenarios

The system includes predefined attack scenarios for testing:

### SQL Injection Attacks
- Classic OR 1=1 injection
- UNION-based data extraction
- Comment-based query truncation
- Stacked query attempts
- Schema discovery attacks

### Privilege Escalation
- Admin table access attempts
- Cross-patient data access
- Sensitive column extraction
- Role impersonation

### Prompt Injection
- Instruction override attempts
- System prompt injection
- Task redirection
- AI model manipulation

### Data Exfiltration
- Bulk patient data extraction
- Medical records dumping
- Cross-table join attacks

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECURITY_MODE` | vulnerable or secure | vulnerable |
| `DB_HOST` | Database hostname | 192.168.100.30 |
| `LLM_HOST` | Ollama service hostname | 192.168.100.1 |
| `LOG_LEVEL` | Logging level | INFO |
| `JWT_EXPIRES_HOURS` | Token expiration | 24 |

### Security Features Toggle

```python
# In config.py
VULNERABLE_MODE_FEATURES = {
    'sql_injection_protection': False,
    'input_validation': False,
    'role_based_filtering': False,
    'comprehensive_logging': False
}

SECURE_MODE_FEATURES = {
    'sql_injection_protection': True,
    'input_validation': True,
    'role_based_filtering': True,
    'comprehensive_logging': True
}
```

## Development

### Project Structure

```
healthcare_security_api/
├── app.py                    # Main Flask application
├── config.py                 # Configuration management
├── database.py              # Database connection and queries
├── llm_client.py            # Ollama LLM integration
├── security.py              # Security validation and controls
├── models.py                # Data models and schemas
├── utils.py                 # Helper functions
├── setup_database.sql       # Database schema
├── generate_sample_data.py  # Sample data generator
├── attack_scenarios.py      # Security testing scenarios
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Running Tests

```bash
# Install development dependencies
uv pip install pytest pytest-flask pytest-cov

# Run unit tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Security analysis
bandit -r .
safety check
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check connection parameters in `.env`
   - Ensure database and user exist

2. **LLM Service Unavailable**
   - Verify Ollama is running on Windows host
   - Check network connectivity between VMs
   - Confirm model is downloaded in Ollama

3. **Authentication Failures**
   - Verify sample data was generated
   - Check username/password combinations
   - Review JWT token expiration

4. **Import Errors**
   - Ensure virtual environment is activated
   - Install all requirements: `uv pip install -r requirements.txt`
   - Check Python version compatibility

### Debugging

Enable debug mode:
```python
# In config.py
DEBUG = True
LOG_LEVEL = 'DEBUG'
```

View logs:
```bash
tail -f healthcare_security.log
tail -f security_audit.log
```

## Security Considerations

### For Research Use Only
- Contains intentional vulnerabilities
- Uses weak default passwords
- Includes realistic but fake PHI data
- Not suitable for production deployment

### Data Privacy
- All patient data is generated using Faker library
- SSNs follow proper format but are fake
- Medical conditions are realistic but anonymized
- No real patient information is included

### Network Security
- Use only in isolated network environments
- Do not expose to public internet
- Implement proper firewall rules between VMs
- Monitor all network traffic during testing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run security checks
6. Submit a pull request

## License

This project is for educational and research purposes only. See LICENSE file for details.

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review the logs for error details
3. Verify all prerequisites are met
4. Test with minimal configuration first

## Acknowledgments

- Built for security research and education
- Uses Ollama for LLM integration
- Implements OWASP security testing principles
- Designed for healthcare security research

---

**Remember**: This is a research tool with intentional vulnerabilities. Use responsibly and only in controlled environments.

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*