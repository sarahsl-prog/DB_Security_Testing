<div align="center">
  <img src="../images/app-logo.jpg" alt="Healthcare Security Research Lab Logo" width="150"/>
</div>

# Frontend/Backend Host Setup

!!! info "Host Information"
    **Hostname:** febe01  
    **IP Address:** 192.168.0.241  
    **Operating System:** Ubuntu Server 24.04 LTS  
    **Virtualization:** VMware Workstation 17.6.2 VM  
    **Hardware:** 8GB RAM, 2 vCPU, 20 GB Storage  
    
    **Services:**
    
    - Nginx 1.26 (Web Server)
    - Flask 3.1.2 (API Server)
    - Python 3.12
    - Vite Frontend

---

## Quick Links

- [Installation Steps](#installation-steps)
- [Nginx Configuration](#nginx-configuration)
- [Flask Configuration](#flask-configuration)
- [Verification](#verification)
- [Configuration Files](#configuration-files)

---

## Installation Steps

### 1. Initial System Setup

Update the system and install base dependencies:

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install base dependencies
sudo apt install -y build-essential curl git wget vim python-is-python3

# Install Python 3.12 and pip
sudo apt install -y python3.12 python3.12-venv python3-pip

# Verify Python installation
python3 --version
```

### 2. Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Verify Nginx version
nginx -v

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

### 3. Install Node.js and npm (for Vite)

```bash
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"

# Download and install Node.js:
nvm install 22

# Verify the Node.js version:
node -v # Should print "v22.21.1".

# Verify npm version:
npm -v # Should print "10.9.4".

```

### 4. Setup Flask Application

Create application directory and virtual environment:

```bash
# Create application directory
sudo mkdir -p /var/www/healthcare-api
sudo chown $USER:$USER /var/www/healthcare-api
cd /var/www/healthcare-api

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Flask and dependencies
pip install --upgrade pip
pip install flask flask-cors python-jose[cryptography] psycopg2-binary loguru requests
```


### 5. Setup Vite Frontend

```bash
# Navigate to web root
cd /var/www/healthcare-api

# Initialize Vite app (if starting fresh)
npx create-react-app .

# Or clone your existing frontend
git clone [your-repo-url] /var/www/healthcare-api
cd /var/www/healthcare-api

# Install dependencies
npm install

# Build for production
npm run build
```

### 6. Configure Systemd Service for Flask

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/healthcare-api.service
```

Add the following configuration:

```ini
[Unit]
Description=Healthcare Security Research API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/healthcare-api
Environment="PATH=/var/www/healthcare-api/.venv/bin"
ExecStart=/var/www/healthcare-api/.venv/bin/python app.py

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start the service
sudo systemctl start healthcare-api

# Enable on boot
sudo systemctl enable healthcare-api

# Check status
sudo systemctl status healthcare-api
```

---

## Nginx Configuration

### Configure Nginx as Reverse Proxy

Create Nginx site configuration:

```bash
sudo nano /etc/nginx/sites-available/healthcare-api
```

Add the following configuration:

```nginx
# HTTP Server (redirects to HTTPS in secure mode)
server {
    listen 80;
    server_name frontend-backend-01 192.168.1.10;
    
    # For vulnerable mode testing - allow HTTP
    # For secure mode - uncomment the redirect below
    # return 301 https://$server_name$request_uri;

    # Serve Vite frontend
    location / {
        root /var/www/healthcare-frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to Flask
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTPS Server (for secure mode)
# Uncomment for secure mode testing
# server {
#     listen 443 ssl http2;
#     server_name frontend-backend-01 192.168.1.10;
#
#     ssl_certificate /etc/nginx/ssl/server.crt;
#     ssl_certificate_key /etc/nginx/ssl/server.key;
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers HIGH:!aNULL:!MD5;
#     ssl_prefer_server_ciphers on;
#     
#     add_header Strict-Transport-Security "max-age=31536000" always;
#
#     location / {
#         root /var/www/healthcare-frontend/build;
#         try_files $uri $uri/ /index.html;
#     }
#
#     location /api/ {
#         proxy_pass http://localhost:5000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto $scheme;
#     }
# }
```

Enable the site and restart Nginx:

```bash
# Create symlink to enable site
sudo ln -s /etc/nginx/sites-available/healthcare-api /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## Flask Configuration

### Environment Configuration

Create `.env` file for Flask configuration:

```bash
nano /var/www/healthcare-api/.env
```

Add configuration:

```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
DEBUG=False
HOST=127.0.0.1
PORT=5000

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production

# Database Connection
DATABASE_URL=postgresql://healthcare_user:password@192.168.1.11:5432/healthcare_research

# LLM Service
LLM_BASE_URL=http://192.168.1.12:11434
LLM_MODEL=deepseek-coder:1.3b

# Security Mode (vulnerable or secure)
SECURITY_MODE=vulnerable
```

!!! warning "Security Notice"
    Remember to change the `SECRET_KEY` to a secure random value. Generate one with:
    ```bash
    python3 -c "import secrets; print(secrets.token_hex(32))"
    ```

---

## Verification

### Test Each Component

**1. Test Nginx:**

```bash
# Check if Nginx is running
sudo systemctl status nginx

# Test HTTP access
curl http://localhost

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
```

**2. Test Flask API:**

```bash
# Check if Flask service is running
sudo systemctl status healthcare-api

# Test health endpoint
curl http://localhost:5000/api/health

# Check Flask logs
sudo journalctl -u healthcare-api -f
```

**3. Test Frontend:**

```bash
# Access from browser
# http://192.168.1.10

# Or use curl
curl http://192.168.1.10
```

**4. Test Full Stack:**

```bash
# Test login endpoint
curl -X POST http://192.168.1.10/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

## Configuration Files

### Download Configuration Files

All configuration files used for this host setup are available for download:

- [:material-download: Nginx Configuration](../config-files/nginx-healthcare-api.conf) - Complete Nginx reverse proxy config
- [:material-download: Flask .env Template](../config-files/backend_config.py) - Environment variables template
- [:material-download: systemd Service File](../config-files/healthcare-api.service) - Systemd service configuration
- [:material-download: requirements.txt](../config-files/requirements.txt) - Python dependencies

### View Configuration Files

=== "Nginx Config"

    ```nginx title="/etc/nginx/sites-available/healthcare-api"
    server {
        listen 80;
        server_name frontend-backend-01 192.168.1.10;
        
        location / {
            root /var/www/healthcare-frontend/build;
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://localhost:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

=== "Flask .env"

    ```bash title="/var/www/healthcare-api/.env"
    FLASK_APP=app.py
    FLASK_ENV=production
    DEBUG=False
    HOST=127.0.0.1
    PORT=5000
    SECRET_KEY=your-secret-key-here
    DATABASE_URL=postgresql://healthcare_user:password@192.168.1.11:5432/healthcare_research
    LLM_BASE_URL=http://192.168.1.12:11434
    LLM_MODEL=deepseek-coder:1.3b
    SECURITY_MODE=vulnerable
    ```

=== "Systemd Service"

    ```ini title="/etc/systemd/system/healthcare-api.service"
    [Unit]
    Description=Healthcare Security Research API
    After=network.target

    [Service]
    Type=simple
    User=www-data
    Group=www-data
    WorkingDirectory=/var/www/healthcare-api
    Environment="PATH=/var/www/healthcare-api/venv/bin"
    ExecStart=/var/www/healthcare-api/venv/bin/python app.py
    Restart=always
    RestartSec=10

    [Install]
    WantedBy=multi-user.target
    ```

=== "requirements.txt"

    ```txt title="/var/www/healthcare-api/requirements.txt"
    Flask==3.1.2
    flask-cors==4.0.0
    python-jose[cryptography]==3.3.0
    psycopg2-binary==2.9.9
    loguru==0.7.2
    requests==2.31.0
    PyJWT==2.8.0
    ```

---

## Troubleshooting

!!! bug "Common Issues"

    **Flask service won't start:**
    ```bash
    # Check logs for errors
    sudo journalctl -u healthcare-api -n 50
    
    # Verify Python path
    /var/www/healthcare-api/venv/bin/python --version
    
    # Test Flask manually
    cd /var/www/healthcare-api
    source venv/bin/activate
    python app.py
    ```

    **Nginx 502 Bad Gateway:**
    ```bash
    # Ensure Flask is running
    sudo systemctl status healthcare-api
    
    # Check if port 5000 is listening
    sudo netstat -tulpn | grep 5000
    
    # Check Nginx error logs
    sudo tail -f /var/log/nginx/error.log
    ```

    **Cannot connect to database:**
    ```bash
    # Test database connectivity
    psql -h 192.168.1.11 -U healthcare_user -d healthcare_research
    
    # Check .env file
    cat /var/www/healthcare-api/.env | grep DATABASE_URL
    ```

---

## Security Hardening (Secure Mode)

When transitioning from vulnerable to secure mode:

### 1. Enable HTTPS

```bash
# Generate self-signed certificate (for testing)
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/server.key \
  -out /etc/nginx/ssl/server.crt

# Uncomment HTTPS server block in Nginx config
sudo nano /etc/nginx/sites-available/healthcare-api

# Restart Nginx
sudo systemctl restart nginx
```

### 2. Configure Firewall

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Verify rules
sudo ufw status
```

### 3. Update Environment to Secure Mode

```bash
# Edit .env file
nano /var/www/healthcare-api/.env

# Change: SECURITY_MODE=secure

# Restart Flask service
sudo systemctl restart healthcare-api
```

---

## Related Documentation

- [Database Host Setup](database-host.md)
- [LLM Host Setup](llm-host.md)
- [Network Configuration](network-config.md)
- [Security Testing Guide](../security/security-testing.md)

---

*Last Updated: [Date]*  
*Lab Version: 1.0*
