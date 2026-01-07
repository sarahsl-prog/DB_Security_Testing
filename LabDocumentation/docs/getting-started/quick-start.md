<div align="center">
  <img src="../images/logo-trnsp.png" alt="Healthcare Database Security Testing Lab Logo" width="150"/>
</div>

# Quick Start Guide

Get your Healthcare Database Security Testing Lab up and running quickly.

## Deployment Options

!!! tip "Choose the Best Method for You"
    **For Beginners:** Use [Docker Deployment](../DOCKER_QUICKSTART.md) - Single command, 10-15 minutes

    **For Intermediate Users:** Use [Automated Scripts](../QUICKSTART.md) - Interactive wizard, 20-30 minutes

    **For Advanced Users:** Use manual setup below - Full control, 4-6 hours

## Overview

This guide covers **manual VM-based setup**. For faster deployment, see options above.

## Time Estimate

**Manual Setup (This Guide):**
- **Initial Setup:** 4-6 hours
- **Testing:** 2-3 hours
- **Total:** 6-9 hours for complete lab setup

**Alternative: Docker Setup:**
- **Total:** 10-15 minutes (see [Docker Quick Start](../DOCKER_QUICKSTART.md))

## Step-by-Step Setup

### Step 1: Prepare Your Environment

1. Ensure you have [all prerequisites](prerequisites.md) met
2. Download Ubuntu ISO files:
   - Ubuntu 24.04 LTS
   - Ubuntu 25.04
3. Prepare VMware Workstation or your chosen hypervisor

### Step 2: Set Up Hosts

Follow these guides in order:

1. **[Frontend/Backend Host](../hosts/frontend-backend.md)** (2-3 hours)
   - Install Ubuntu 24.04
   - Configure Nginx and Flask
   - Deploy Vite frontend

2. **[Database Host](../hosts/database-host.md)** (1-2 hours)
   - Install Ubuntu 25.04
   - Configure PostgreSQL 17
   - Load healthcare schema

3. **[LLM Host](../hosts/llm-host.md)** (1-2 hours)
   - Install Ollama
   - Pull deepseek-coder model
   - Configure network access

### Step 3: Configure Networking

!!! note "Example IP Addresses"
    The IPs below are examples. Use your actual network configuration or let Docker handle networking automatically.

1. Set static IP addresses (manual setup example):
   - Frontend/Backend: 192.168.1.10 *(example)*
   - Database: 192.168.1.11 *(example)*
   - LLM: 192.168.1.12 *(example)*

2. Test connectivity between hosts

See [Network Configuration Guide](../hosts/network-config.md) for details.

### Step 4: Verify Installation

Run verification tests for each component:

```bash
# Test Frontend/Backend
curl http://192.168.1.10/api/health

# Test Database
psql -h 192.168.1.11 -U healthcare_user -d healthcare_research

# Test LLM
curl http://192.168.1.12:11434/api/tags
```

### Step 5: Run Initial Tests

1. Navigate to [Testing Documentation](../testing/test-cases.md)
2. Execute vulnerable mode tests first
3. Document your results

## Next Steps

Once your lab is operational:

- Review [Security Controls](../security/overview.md)
- Plan your research approach using [Research Documentation](../research/research-readme.md)
- Begin [Security Testing](../testing/test-cases.md)

## Troubleshooting

If you encounter issues, check:

- [Common Issues](../troubleshooting/common-issues.md)
- Individual host troubleshooting guides
- Network connectivity between hosts

## Getting Help

For detailed setup instructions, refer to the specific host setup guides or the troubleshooting section.

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
