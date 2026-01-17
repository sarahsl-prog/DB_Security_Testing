<div align="center">
  <img src="docs\images\logo-trnsp.png" alt="Healthcare Database Security Testing Logo" width="200"/>

</div>

# Documentation Installation Guide

## Overview

This project uses **MkDocs** with the **Material theme** to provide comprehensive, searchable documentation for the Healthcare Database Security Testing Lab. The documentation includes 52+ markdown files organized across 13 sections covering setup, architecture, security testing, troubleshooting, and more.

## Current Status

### ✓ What's Already There
- **52 Markdown files** organized in structured directories
- **mkdocs.yml** - Complete configuration file
- **Material theme** configured with dark/light mode
- **Advanced features**: Search, syntax highlighting, tabs, emoji support, Mermaid diagrams

### ✗ What's Missing
MkDocs dependencies are **NOT currently installed**:
- ❌ `mkdocs-material` - Material theme package
- ❌ `pymdown-extensions` - Markdown extensions
- ⚠️ `mkdocs` is installed globally but dependencies are missing

**Result**: Running `mkdocs serve` or `mkdocs build` will fail with:
```
Error: MkDocs encountered an error parsing the configuration file:
cannot find module 'material.extensions.emoji' (No module named 'material')
```

## Why Documentation is Important for Training

This is a **training environment** for database security research. Good documentation is critical because:

1. **Onboarding**: New researchers/students need to understand the system quickly
2. **Architecture Understanding**: Complex distributed system with 4 components
3. **Security Testing**: Step-by-step guides for testing both vulnerable and secure modes
4. **Troubleshooting**: Common issues and solutions readily available
5. **Reference**: API endpoints, configuration options, command references
6. **Research Context**: Methodology, objectives, and analysis frameworks

## Installation Options

I've identified **4 different approaches** for installing the documentation system. Each has trade-offs:

### Option 1: Separate Virtual Environment (RECOMMENDED for Training)
**Best for: Training environments, clean separation, multiple users**

```bash
cd LabDocumentation
./install-docs.sh --venv
```

**Pros:**
✅ Complete isolation from backend/frontend
✅ No conflicts with other Python packages
✅ Easy to remove/recreate
✅ Students can install docs-only without backend/frontend
✅ Can be used on instructor machine to host docs separately

**Cons:**
❌ Need to activate venv before using
❌ Separate environment to manage

**After installation:**
```bash
# Activate docs environment
source activate-docs.sh

# Serve documentation
mkdocs serve

# Build for deployment
mkdocs build
```

### Option 2: User Installation
**Best for: Individual developers, simple setup**

```bash
cd LabDocumentation
./install-docs.sh --user
```

**Pros:**
✅ No sudo required
✅ No virtual environment to manage
✅ mkdocs command available globally for your user
✅ Simple and fast

**Cons:**
❌ Installs in ~/.local/bin (might need PATH update)
❌ Could conflict with other user Python packages
❌ Each user must install separately

**After installation:**
```bash
# If needed, add to PATH:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Use mkdocs
mkdocs serve
```

### Option 3: Global System Installation
**Best for: Dedicated documentation server, system-wide access**

```bash
cd LabDocumentation
./install-docs.sh --global
```

**Pros:**
✅ Available to all users on the system
✅ One installation for everyone
✅ Good for dedicated docs server

**Cons:**
❌ Requires sudo/root access
❌ Could interfere with system packages
❌ Not recommended for shared development machines

### Option 4: Include in Backend Environment
**Best for: All-in-one development setup**

```bash
cd backend
uv pip install -r requirements.txt -r requirements-dev.txt
uv pip install mkdocs mkdocs-material pymdown-extensions
```

**Pros:**
✅ Everything in one environment
✅ Simple for solo developers
✅ Already have backend venv

**Cons:**
❌ Bloats backend environment with docs tools
❌ Can't run docs-only without full backend
❌ Confuses separation of concerns

## Recommended Setup for Training Environment

For a **training/lab environment**, I recommend a **hybrid approach**:

### Instructor/Server Setup
```bash
# On instructor machine or dedicated docs server
cd LabDocumentation
./install-docs.sh --venv
source activate-docs.sh
mkdocs serve --dev-addr 0.0.0.0:8000
```

**Result**: Documentation accessible at `http://<server-ip>:8000` for all students

### Student Setup (Optional)
Students who want local docs:
```bash
# Option 1: Just clone repo and use instructor's hosted docs
# (no installation needed)

# Option 2: Install docs locally
cd LabDocumentation
./install-docs.sh --user
mkdocs serve
```

### CI/CD or GitHub Pages
Build and deploy static docs:
```bash
cd LabDocumentation
./install-docs.sh --venv
source docs-venv/bin/activate
mkdocs build
# Upload 'site/' directory to web server or GitHub Pages
```

## Quick Installation

### For Documentation Only
```bash
# Clone repository (if not already)
git clone <repo-url>
cd LabDocumentation

# Install docs (creates virtual environment)
./install-docs.sh --venv

# Activate and serve
source activate-docs.sh
mkdocs serve
```

Access at: http://localhost:8000

### For Full Development Setup
```bash
# Backend
cd backend
uv pip install -r requirements.txt -r requirements-dev.txt

# Frontend
cd frontend
npm install

# Documentation (separate venv)
cd LabDocumentation
./install-docs.sh --venv
```

## What Gets Installed

### Core Dependencies
```
mkdocs>=1.5.0          # Core documentation generator
mkdocs-material>=9.0.0 # Material theme with modern UI
pymdown-extensions>=10.0  # Advanced markdown features
```

### Total Size
- ~50MB of Python packages
- Includes all dependencies

## Documentation Structure

```
LabDocumentation/
├── mkdocs.yml              # Configuration
├── requirements-docs.txt   # Python dependencies
├── install-docs.sh         # Installation script
├── activate-docs.sh        # Quick activation (after venv install)
├── docs/
│   ├── index.md           # Homepage
│   ├── getting-started/   # Setup guides
│   ├── hosts/             # Host configuration docs
│   ├── architecture/      # System architecture
│   ├── database/          # Database documentation
│   ├── security/          # Security controls
│   ├── testing/           # Security testing guides
│   ├── api/               # API reference
│   ├── troubleshooting/   # Common issues
│   ├── research/          # Research methodology
│   └── reference/         # Quick references
├── diagrams/              # Architecture diagrams
└── images/                # Images and screenshots
```

## Features Configured

### Material Theme Features
- ✅ Light/Dark mode toggle
- ✅ Navigation tabs and sections
- ✅ Search with suggestions
- ✅ Code syntax highlighting
- ✅ Code copy buttons
- ✅ Admonitions (notes, warnings, tips)
- ✅ Content tabs
- ✅ Emoji support
- ✅ Mermaid diagram support
- ✅ Table of contents with permalinks

### Markdown Extensions
- ✅ Task lists with checkboxes
- ✅ Definition lists
- ✅ Footnotes
- ✅ Abbreviations
- ✅ Smart symbols
- ✅ Highlight, mark, keys
- ✅ Mathematical expressions
- ✅ Custom fences for code blocks

## Usage

### Development Server
```bash
mkdocs serve
```
- Hot reload on file changes
- Access at http://localhost:8000
- Perfect for writing/editing docs

### Build Static Site
```bash
mkdocs build
```
- Outputs to `site/` directory
- Deploy to any static hosting
- GitHub Pages, Netlify, etc.

### Build for Production
```bash
mkdocs build --clean
```
- Clean build without cache
- Optimized for deployment

## Deployment Options

### 1. Local Development Server
```bash
mkdocs serve --dev-addr 0.0.0.0:8000
```
Great for LAN access in training labs

### 2. GitHub Pages (Free Hosting)
```bash
mkdocs gh-deploy
```
Automatically builds and deploys to GitHub Pages

### 3. Static File Hosting
```bash
mkdocs build
# Upload site/ directory to:
# - Netlify, Vercel, AWS S3, nginx server, etc.
```

### 4. Docker Container
```dockerfile
FROM squidfunk/mkdocs-material
COPY . /docs
EXPOSE 8000
CMD ["mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]
```

## Troubleshooting

### Issue: `mkdocs: command not found`
**Solution**: Activate environment or add to PATH
```bash
# If using venv:
source activate-docs.sh

# If user install:
export PATH="$HOME/.local/bin:$PATH"
```

### Issue: `No module named 'material'`
**Solution**: Install dependencies
```bash
uv pip install -r requirements-docs.txt
```

### Issue: Build errors about missing pages
**Solution**: Some pages in mkdocs.yml navigation may not exist yet
- Comment out missing pages in `mkdocs.yml`
- Or create stub pages in docs/

### Issue: Port 8000 already in use
**Solution**: Use different port
```bash
mkdocs serve --dev-addr localhost:8001
```

## Maintenance

### Update MkDocs
```bash
# If using venv:
source activate-docs.sh
uv pip install --upgrade mkdocs mkdocs-material pymdown-extensions

# If user/global:
uv pip install --user --upgrade mkdocs mkdocs-material pymdown-extensions
```

### Add New Pages
1. Create markdown file in appropriate docs/ subdirectory
2. Add to `mkdocs.yml` navigation section
3. Rebuild/refresh

### Customize Theme
Edit `mkdocs.yml`:
- Change colors in `theme.palette`
- Add/remove features in `theme.features`
- Modify navigation structure

## Recommendations

### For This Project (Training Environment)

**Recommended Approach**: **Separate Virtual Environment (Option 1)**

**Rationale**:
1. ✅ **Clean Separation**: Docs are separate from backend/frontend
2. ✅ **Easy to Install**: Students can install just docs if needed
3. ✅ **Instructor Hosting**: Run docs server separately from app server
4. ✅ **No Conflicts**: Won't interfere with backend Python environment
5. ✅ **Easy Removal**: `rm -rf docs-venv/` to uninstall

**Implementation**:
```bash
# One-time setup
cd LabDocumentation
./install-docs.sh --venv

# Daily use
source activate-docs.sh
mkdocs serve

# Or host for class
mkdocs serve --dev-addr 0.0.0.0:8000
```

### Additional Recommendations

1. **Add to Installation Guide**: Include docs setup in main INSTALL.md
2. **Create README in LabDocumentation**: Quick reference for docs setup
3. **Consider GitHub Pages**: Free hosting for static docs
4. **Add to .gitignore**: Add `site/` and `docs-venv/` to .gitignore
5. **Documentation Sprint**: Fill in any missing pages referenced in mkdocs.yml

## Next Steps

1. ✅ **Install Documentation System**
   ```bash
   cd LabDocumentation
   ./install-docs.sh --venv
   ```

2. ✅ **Test Documentation Build**
   ```bash
   source activate-docs.sh
   mkdocs build
   ```

3. ✅ **Serve Locally**
   ```bash
   mkdocs serve
   ```
   Visit http://localhost:8000

4. ⚠️ **Fill Missing Pages** (optional)
   Some pages in mkdocs.yml may need to be created

5. 🚀 **Deploy** (optional)
   - GitHub Pages: `mkdocs gh-deploy`
   - Or: Build and upload to web server

## Summary

| Aspect | Status |
|--------|--------|
| **Documentation Files** | ✅ 52 markdown files exist |
| **Configuration** | ✅ mkdocs.yml properly configured |
| **Dependencies** | ❌ Not installed (install-docs.sh created) |
| **Installation** | ✅ Multiple options available |
| **Recommended** | Virtual environment (--venv) |
| **For Training** | ✅ Perfect - separate install, easy to host |

**Bottom Line**: Documentation system is well-designed but dependencies need installation. Use `./install-docs.sh --venv` for clean, isolated setup perfect for training environments.
