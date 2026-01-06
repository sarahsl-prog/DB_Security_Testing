# Healthcare Database Security Research Test Lab

A distributed research platform for studying SQL injection vulnerabilities and defense mechanisms in healthcare database systems. This test lab supports both vulnerable and secure operational modes for comprehensive security testing and analysis.

## Purpose

This test lab was developed for academic research into database security vulnerabilities, specifically examining how natural language to SQL systems can be exploited and how various security controls can mitigate these risks in healthcare contexts.

## System Architecture

The test lab consists of four distributed components:

```
User → Frontend Host → Backend Host (Flask API) → Database Host (PostgreSQL)
                              ↓
                         LLM Host (Ollama)
```

See `/docs/diagrams/` for detailed architecture and authentication flow diagrams.

## System Components

| Component | OS | Hardware | Software | Network | Role |
|-----------|-----|----------|----------|---------|------|
| Frontend Host | TBD | TBD | Vite (Vanilla JS), Nginx | Port 80/443 | Web interface for query submission |
| Backend Host | TBD | 8GB RAM, 4 vCPU | Flask, Python 3.11 | Port 5000 | API server, authentication, security controls |
| Database Host | TBD | TBD | PostgreSQL | Port 5432 | Healthcare data storage, user management |
| LLM Host | TBD | TBD | Ollama | Port 11434 | Natural language to SQL generation |

## Key Features

### Authentication & Authorization
- JWT-based authentication with HS256 signing
- 24-hour token expiration
- Role-based access control (Admin, Doctor, Nurse, Patient)
- Session tracking and audit logging

### Security Modes
- **Vulnerable Mode**: Minimal security controls for testing attack vectors
- **Secure Mode**: Full security controls including input validation, SQL filtering, and result sanitization

### API Endpoints
- `POST /api/login` - User authentication and JWT generation
- `GET /api/verify` - Token verification
- `POST /api/query` - Natural language query processing
- `GET /api/schema` - Database schema information
- `POST /api/validate` - Query validation without execution
- `GET /api/audit` - Security audit logs (admin only)

## Request Flow

1. **Authentication**: User credentials → Flask backend → PostgreSQL validation → JWT generation
2. **Query Processing**: 
   - User submits natural language query
   - Frontend sends authenticated request with JWT
   - Backend validates token and extracts user role
   - Backend fetches database schema context
   - Ollama LLM generates SQL from natural language
   - Backend executes SQL (with security filtering in secure mode)
   - Results returned to frontend
   - Audit log entry created

See `/docs/diagrams/authentication-flow.mmd` for detailed sequence diagram.

## Installation & Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 17+
- Ollama (with appropriate model installed)
- Node.js 22+ (for frontend)

### Backend Setup
```bash
# Clone repository
git clone [repository-url]
cd [repository-name]

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database and Ollama connection details

# Initialize database
python database.py

# Run Flask backend
python app.py
```

### Database Setup
```bash
# Create PostgreSQL database
createdb healthcare_research

# Run schema migrations
psql healthcare_research < schema.sql

# Generate sample data
python generate_sample_data.py
```

### LLM Setup
```bash
# Install and run Ollama
# See: https://ollama.ai

# Pull required model
ollama pull [model-name]

# Verify Ollama is running on port 11434
curl http://localhost:11434/api/tags
```

## Testing

### Test User Accounts
The system includes test accounts for each role:
- Admin: `admin` / `[password]`
- Doctor: `doctor1` / `[password]`
- Nurse: `nurse1` / `[password]`
- Patient: `patient1` / `[password]`

### Security Testing Scenarios
The system includes predefined attack scenarios accessible via:
```bash
GET /api/attack/scenarios
```

Test both vulnerable and secure modes to observe security control effectiveness.

## Research Use

### Data Collection
All queries are logged in the audit table with:
- User ID and role
- Generated SQL query
- Execution status
- Security mode
- Timestamp

### Experimental Variables
- Security mode (vulnerable vs. secure)
- User role (admin, doctor, nurse, patient)
- Query complexity
- Attack vector type

### Metrics Tracked
- Query execution time
- LLM processing time
- Success/failure rates
- Security control effectiveness
- False positive/negative rates

## Security Considerations

**IMPORTANT**: This is a research test lab only. Do not use in production or with real patient data.

- All passwords should be changed from defaults
- System should be isolated on a private network
- Audit logs should be reviewed regularly
- Test data should not contain real PHI/PII

## Documentation

- Architecture diagrams: `/docs/diagrams/`
- API documentation: `/docs/api.md`
- Security testing guide: `/docs/security-testing.md`
- Research methodology: See associated research paper

## Technology Stack

- **Backend**: Flask (Python 3.11), JWT, Loguru
- **Database**: PostgreSQL 15
- **LLM**: Ollama (port 11434)
- **Frontend**: Vite (Vanilla JavaScript), Nginx
- **Security**: Role-based access control, input validation, SQL sanitization

## Contributing

This is a research project. For questions or collaboration inquiries, contact [your contact information].

## License

[Your license information]

## Citation

If you use this test lab in your research, please cite:

```
[Your citation format]
```

## Acknowledgments

[Any acknowledgments for funding, collaboration, etc.]