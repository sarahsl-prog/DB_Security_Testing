<div align="center">
  <img src="../images/logo-trnsp.png" alt="Healthcare Database Security Testing Lab Logo" width="150"/>
</div>

# LLM Host Setup

!!! warning "**DRAFT** - This documentation is a work in progress"

!!! info "Host Information"
    **Hostname:** llm-01
    **IP Address:** 192.168.1.12
    **Operating System:** Ubuntu 24.04 LTS
    **Virtualization:** Physical Machine
    **Hardware:** 32GB RAM, Intel Core Ultra 5 CPU, 1TB Storage

    **Services:**

    - Ollama 0.12.3 (LLM Inference Engine)
    - qwen2.5-coder (Language Model)
    - Nginx 1.26 (Reverse Proxy - Optional)

!!! note "Example IP Addresses"
    The IP addresses in this guide (192.168.1.12, 192.168.1.10, etc.) are **examples only**. For actual deployment:

    - **Docker (Recommended):** No manual IP configuration needed - see [Docker Deployment](../DOCKER_QUICKSTART.md)
    - **Manual Setup:** Replace example IPs with your actual network addresses
    - **Environment Variables:** Use `.env` files to configure your specific IPs

---

## Quick Links

- [Installation Steps](#installation-steps)
- [Ollama Configuration](#ollama-configuration)
- [Model Management](#model-management)
- [Performance Optimization](#performance-optimization)
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
sudo apt install -y build-essential curl git wget vim

# Install monitoring tools
sudo apt install -y htop nvtop
```

### 2. Install Ollama

```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Check if Ollama service is running
sudo systemctl status ollama

# Enable Ollama to start on boot
sudo systemctl enable ollama
```

!!! tip "Installation Notes"
    Ollama automatically:
    
    - Creates a systemd service
    - Listens on localhost:11434 by default
    - Stores models in `/usr/share/ollama/.ollama/models`

### 3. Install Nginx (Optional - for reverse proxy)

```bash
# Install Nginx
sudo apt install -y nginx

# Verify version
nginx -v

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

---

## Ollama Configuration

### 1. Configure Ollama Service

Edit the Ollama systemd service to accept connections from the network:

```bash
# Create override directory
sudo mkdir -p /etc/systemd/system/ollama.service.d

# Create override configuration
sudo nano /etc/systemd/system/ollama.service.d/override.conf
```

Add the following configuration:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_ORIGINS=*"
Environment="OLLAMA_NUM_PARALLEL=2"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
```

Apply the changes:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Restart Ollama
sudo systemctl restart ollama

# Verify it's listening on all interfaces
sudo netstat -tulpn | grep 11434
# Should show: 0.0.0.0:11434
```

### 2. Ollama Environment Variables

Key environment variables for Ollama:

| Variable | Default | Purpose | Recommended |
|----------|---------|---------|-------------|
| `OLLAMA_HOST` | 127.0.0.1:11434 | Listen address | 0.0.0.0:11434 (vulnerable)<br>192.168.1.12:11434 (secure) |
| `OLLAMA_ORIGINS` | localhost | CORS origins | * (vulnerable)<br>192.168.1.10 (secure) |
| `OLLAMA_NUM_PARALLEL` | 1 | Parallel requests | 2-4 based on workload |
| `OLLAMA_MAX_LOADED_MODELS` | 1 | Models in memory | 1 for this lab |
| `OLLAMA_MODELS` | (default) | Models directory | /usr/share/ollama/.ollama/models |

---

## Model Management

### 1. Pull the qwen2.5-coder Model

```bash
# Pull the qwen2.5-coder model
ollama pull qwen2.5-coder

# Verify the model is downloaded
ollama list

# Expected output:
# NAME                     ID              SIZE     MODIFIED
# qwen2.5-coder:latest     xxxxxxxxxx      1.5 GB   X minutes ago
```

!!! note "Model Size"
    The qwen2.5-coder model is approximately 1.5 GB in size. With 32GB RAM, this leaves plenty of memory for inference operations.

### 2. Create a new model using a custom Model File

Create a model file to use to customize the qwen2.5-coder model

```bash
sudo vim /usr/share/ollama/.ollama/ModelFile_qwen25-coder.txt
```
Add the following information:

```bash
FROM qwen2.5-coder

PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER top_k 10
PARAMETER num_ctx 16384
PARAMETER num_predict 512
PARAMETER num_keep 100

SYSTEM """You are a SQL query generator for our specific database. Generate accurate, efficient SQL queries based on natural language requests.

DATABASE SCHEMA:
```
Put the complete schema here...

```bash
GUIDELINES:
- Always use proper table and column names from the schema above
- Include appropriate WHERE clauses for filtering
- Use JOINs when querying multiple tables
- Consider performance with indexes
- Return only the SQL query, no explanation unless asked
- Use standard SQL syntax compatible with PostgreSQL"""
```

Create a model using the model file

``` bash
sudo ollama create qwen-coder-sql -f /usr/share/ollama/.ollama/ModelFile_qwen25-coder.txt

```
# Test SQL generation (relevant to your research)

```bash
ollama run qwen-coder-sql "Generate SQL to select all patients from a patients table"
```

### 3. Test the Model

```bash
# Test with a simple prompt
ollama run qwen-coder-sql "Write a Python function to calculate factorial"

# Test SQL generation (relevant to your research)
ollama run qwen-coder-sql "Generate SQL to select all patients from a patients table"
```

### 4. Model Management Commands

```bash
# List all downloaded models
ollama list

# Show model information
ollama show qwen2.5-coder

# Remove a model (if needed)
ollama rm qwen2.5-coder

# Pull a different model
ollama pull codellama:7b

# Check running models
ollama ps
```

---

## Nginx Configuration (Optional)

If you want to use Nginx as a reverse proxy in front of Ollama:

### Configure Nginx Reverse Proxy

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/ollama
```

Add the following:

```nginx
server {
    listen 80;
    server_name llm-01 192.168.1.12;

    # Increase timeout for LLM inference
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;

    location / {
        proxy_pass http://localhost:11434;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable the configuration:

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/ollama /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

!!! warning "Direct vs Proxied Access"
    For this lab, you can use Ollama directly on port 11434 or through Nginx on port 80. The Flask application connects directly to port 11434.

---

## Performance Optimization

### 1. System Resource Monitoring

Monitor Ollama resource usage:

```bash
# Monitor CPU and memory usage
htop

# Monitor Ollama logs in real-time
sudo journalctl -u ollama -f

# Check system resources
free -h
df -h
```

### 2. Performance Tuning

For optimal performance with qwen2.5-coder:

```bash
# Edit Ollama service override
sudo nano /etc/systemd/system/ollama.service.d/override.conf
```

Adjust based on your workload:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_ORIGINS=*"

# Number of parallel requests (2-4 for 32GB RAM)
Environment="OLLAMA_NUM_PARALLEL=2"

# Keep only one model in memory
Environment="OLLAMA_MAX_LOADED_MODELS=1"

# GPU settings (if you have a GPU)
# Environment="OLLAMA_GPU_OVERHEAD=0"
# Environment="OLLAMA_NUM_GPU=1"
```

Restart to apply:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### 3. Model Context Window

The qwen2.5-coder model has a context window of approximately 4096 tokens. For your research use case (SQL generation), this is sufficient.

---

## API Testing

### 1. Test Ollama API

Test the generation endpoint:

```bash
# Simple generation test
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder",
  "prompt": "Write SQL to select all patients",
  "stream": false
}'

# Test from remote host (Frontend/Backend)
curl http://192.168.1.12:11434/api/generate -d '{
  "model": "qwen2.5-coder",
  "prompt": "SELECT * FROM patients",
  "stream": false
}'
```

### 2. Test Chat Endpoint

```bash
# Chat completion test
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5-coder",
  "messages": [
    {
      "role": "system",
      "content": "You are a SQL expert."
    },
    {
      "role": "user",
      "content": "Generate SQL to find all patients with last name Smith"
    }
  ],
  "stream": false
}'
```

### 3. Check Model Status

```bash
# List available models
curl http://localhost:11434/api/tags

# Show running models
curl http://localhost:11434/api/ps

# Model information
curl http://localhost:11434/api/show -d '{
  "name": "qwen2.5-coder"
}'
```

---

## Verification

### Test Each Component

**1. Test Ollama Service:**

```bash
# Check if Ollama is running
sudo systemctl status ollama

# Verify it's listening on correct port
sudo netstat -tulpn | grep 11434

# Check Ollama logs
sudo journalctl -u ollama -n 50
```

**2. Test Model Inference:**

```bash
# Quick inference test
time ollama run qwen2.5-coder "def factorial(n):"

# This should return a Python function and show execution time
```

**3. Test Network Accessibility:**

From the Frontend/Backend host:

```bash
# Test connectivity
curl http://192.168.1.12:11434/api/tags

# Test generation
curl http://192.168.1.12:11434/api/generate -d '{
  "model": "qwen2.5-coder",
  "prompt": "Hello",
  "stream": false
}'
```

**4. Performance Benchmarking:**

```bash
# Benchmark simple prompt
time curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder",
  "prompt": "Write a hello world program",
  "stream": false
}'

# Benchmark SQL generation (your use case)
time curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder",
  "prompt": "Generate SQL to select all records from patients table",
  "stream": false
}'
```

---

## Configuration Files

### Download Configuration Files

- [:material-download: Ollama Service Override](../config-files/ollama.service) - Systemd service configuration
- [:material-download: Nginx Ollama Config](../config-files/nginx-ollama.conf) - Nginx reverse proxy (optional)
- [:material-download: Ollama API Examples](../config-files/ollama-api-examples.sh) - API testing scripts
- [:material-download: Ollama Model File](../config-files/ModelFile_qwen25-coder.txt) - Ollama Model File to create a specific qwen2.5-coder model

### View Configuration Files

=== "Ollama Service"

    ```ini title="/etc/systemd/system/ollama.service.d/override.conf"
    [Service]
    # Listen on all interfaces (vulnerable mode)
    Environment="OLLAMA_HOST=0.0.0.0:11434"
    
    # For secure mode, bind to specific IP:
    # Environment="OLLAMA_HOST=192.168.1.12:11434"
    
    # Allow all origins (vulnerable mode)
    Environment="OLLAMA_ORIGINS=*"
    
    # For secure mode, specify frontend/backend IP:
    # Environment="OLLAMA_ORIGINS=http://192.168.1.10"
    
    # Performance settings
    Environment="OLLAMA_NUM_PARALLEL=2"
    Environment="OLLAMA_MAX_LOADED_MODELS=1"
    ```

=== "Nginx Config"

    ```nginx title="/etc/nginx/sites-available/ollama"
    server {
        listen 80;
        server_name llm-01 192.168.1.12;

        # Increase timeout for LLM inference
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;

        location / {
            proxy_pass http://localhost:11434;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
    ```

=== "API Test Script"

    ```bash title="ollama-test.sh"
    #!/bin/bash
    
    OLLAMA_HOST="http://192.168.1.12:11434"
    
    # Test 1: List models
    echo "=== Test 1: List Models ==="
    curl $OLLAMA_HOST/api/tags | jq .
    
    # Test 2: Simple generation
    echo -e "\n=== Test 2: Simple Generation ==="
    curl $OLLAMA_HOST/api/generate -d '{
      "model": "qwen2.5-coder",
      "prompt": "SELECT * FROM",
      "stream": false
    }' | jq .
    
    # Test 3: SQL generation with context
    echo -e "\n=== Test 3: SQL Generation ==="
    curl $OLLAMA_HOST/api/generate -d '{
      "model": "qwen2.5-coder",
      "prompt": "Generate SQL to select patient name and date of birth from patients table",
      "stream": false
    }' | jq .
    ```

---

## Firewall Configuration

### Vulnerable Mode

Allow Ollama access from any IP:

```bash
# Allow Ollama port
sudo ufw allow 11434/tcp

# Allow Nginx (if using)
sudo ufw allow 80/tcp

# Allow SSH
sudo ufw allow ssh

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Secure Mode

Restrict Ollama to Frontend/Backend host only:

```bash
# Remove allow all rule
sudo ufw delete allow 11434/tcp

# Allow Ollama only from frontend/backend
sudo ufw allow from 192.168.1.10 to any port 11434 proto tcp

# Allow SSH
sudo ufw allow ssh

# Enable firewall
sudo ufw enable

# Verify rules
sudo ufw status numbered
```

---

## Troubleshooting

!!! bug "Common Issues"

    **Ollama service won't start:**
    ```bash
    # Check service status
    sudo systemctl status ollama
    
    # View detailed logs
    sudo journalctl -u ollama -n 100 --no-pager
    
    # Verify Ollama binary
    which ollama
    ollama --version
    
    # Restart service
    sudo systemctl restart ollama
    ```

    **Model not found:**
    ```bash
    # List downloaded models
    ollama list
    
    # If model is missing, pull it again
    ollama pull qwen2.5-coder
    
    # Check model storage location
    ls -lh /usr/share/ollama/.ollama/models
    ```

    **Slow inference:**
    ```bash
    # Check system resources
    htop
    free -h
    
    # Monitor Ollama during inference
    sudo journalctl -u ollama -f
    
    # Check if model is loaded in memory
    ollama ps
    
    # Reduce concurrent requests
    # Edit: /etc/systemd/system/ollama.service.d/override.conf
    # Set: OLLAMA_NUM_PARALLEL=1
    ```

    **Cannot connect from Frontend/Backend:**
    ```bash
    # Verify Ollama is listening on network interface
    sudo netstat -tulpn | grep 11434
    # Should show: 0.0.0.0:11434, not 127.0.0.1:11434
    
    # Test locally first
    curl http://localhost:11434/api/tags
    
    # Test from remote host
    curl http://192.168.1.12:11434/api/tags
    
    # Check firewall
    sudo ufw status
    
    # Verify OLLAMA_HOST setting
    sudo systemctl cat ollama | grep OLLAMA_HOST
    ```

    **High memory usage:**
    ```bash
    # Check memory usage
    free -h
    
    # Unload model from memory
    ollama stop qwen2.5-coder
    
    # Adjust max loaded models
    # Set OLLAMA_MAX_LOADED_MODELS=1
    ```

---

## Performance Monitoring

### Monitor Inference Performance

Create a monitoring script:

```bash
nano monitor-ollama.sh
```

```bash
#!/bin/bash

echo "=== Ollama Performance Monitor ==="
echo ""

# System resources
echo "Memory Usage:"
free -h | grep Mem

echo ""
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'

echo ""
echo "Disk Usage:"
df -h | grep -E '^/dev/'

echo ""
echo "Ollama Process:"
ps aux | grep ollama | grep -v grep

echo ""
echo "Running Models:"
ollama ps

echo ""
echo "Recent Ollama Logs:"
sudo journalctl -u ollama -n 5 --no-pager
```

Make it executable and run:

```bash
chmod +x monitor-ollama.sh
./monitor-ollama.sh
```

### Log Analysis

```bash
# View inference timing logs
sudo journalctl -u ollama | grep "generated"

# Count requests by hour
sudo journalctl -u ollama --since "1 hour ago" | grep "POST /api" | wc -l

# Monitor real-time requests
sudo journalctl -u ollama -f | grep "POST /api"
```

---

## Model Selection Guide

For your research project, qwen2.5-coder is appropriate because:

✅ **Reasonable size (~1.5GB)** - Loads quickly, low memory overhead  
✅ **Code-focused** - Trained specifically for code generation including SQL  
✅ **Fast inference** - Suitable for interactive research testing  
✅ **Fits in memory** - Even with multiple concurrent requests on 32GB RAM

### Alternative Models (if needed)

| Model | Size | Use Case | Pros | Cons |
|-------|------|----------|------|------|
| codellama:7b | 3.8GB | More complex SQL | Better accuracy | Slower |
| mistral:7b | 4.1GB | General purpose | Versatile | More memory |
| llama3:8b | 4.7GB | Latest architecture | State-of-art | Slower |

To switch models:

```bash
# Pull alternative model
ollama pull codellama:7b

# Update Flask application to use new model
# Edit .env file: LLM_MODEL=codellama:7b
```

---

## Security Hardening Checklist

- [x] Ollama installed and configured
- [x] qwen2.5-coder model downloaded
- [x] Service listening on network interface
- [ ] Firewall configured to allow only frontend/backend (secure mode)
- [ ] OLLAMA_HOST restricted to specific IP (secure mode)
- [ ] OLLAMA_ORIGINS restricted to frontend/backend (secure mode)
- [ ] Performance monitoring configured
- [ ] Regular model updates scheduled
- [ ] Backup of model directory configured

---

## Backup Model Directory

```bash
# Backup models directory
sudo tar -czf ollama-models-backup-$(date +%Y%m%d).tar.gz \
  /usr/share/ollama/.ollama/models

# Restore models
sudo tar -xzf ollama-models-backup-20250101.tar.gz -C /
```

---

## Related Documentation

- [Frontend/Backend Host Setup](frontend-backend.md)
- [Database Host Setup](database-host.md)
- [API Documentation](../api/endpoints.md)
- [Security Testing Guide](../security/security-testing.md)

---

*Last Updated: [Date]*  
*Lab Version: 1.0*
