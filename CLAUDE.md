# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python and Angular hybrid project (based on .gitignore configuration). The project is in its initial setup phase.

## Project Structure

The project is being set up to support:
- **Python backend**: Likely using a web framework (FastAPI, Flask, Django, or similar)
- **Angular frontend**: Modern Angular application

## Development Guidelines

### Python Standards
- **Package Manager**: Use `uv` for all Python dependency management (NOT pip or poetry)
- **Data Models**: Use `pydantic` models instead of standard dataclasses
- **Code Formatting**: **MANDATORY** - After every modification to a Python file, run `ruff format <file>` before completing the task
- **Best Practices**: Always follow Python best practices:
  - Type hints for all functions and variables
  - Proper error handling with specific exceptions
  - Comprehensive docstrings (Google or NumPy style)
  - PEP 8 compliance for code style
  - Single Responsibility Principle for functions and classes

### Code Organization
- **File Length**: Keep files under 1000 lines maximum - split if exceeding this limit
- **Module Structure**: Split large modules into smaller, focused files
- **Project Structure**: Follow framework-specific best practices and conventional project layouts
- **Separation of Concerns**: Maintain clear boundaries between layers (API, business logic, data access)

## Development Setup

### Python Environment
```bash
# Install uv (if not already installed)
# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/Mac:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project with uv
uv venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Add dependencies (uv manages pyproject.toml automatically)
uv add package-name

# Add dev dependencies
uv add --dev package-name

# Install all dependencies from pyproject.toml
uv sync

# Remove a dependency
uv remove package-name

# Install ruff for code formatting (mandatory)
uv pip install ruff
```

### Code Formatting Workflow
```bash
# Format a Python file after any modification
ruff format path/to/file.py

# Format entire project
ruff format .
```

### Angular Environment
```bash
# Install dependencies (once package.json is created)
npm install

# Start development server
ng serve

# Build for production
ng build --configuration production
```

## Notes for Future Development

As this project develops, update this file with:
- Specific backend framework being used and its architecture
- API endpoints and routing structure
- Database configuration and migration commands
- Frontend component architecture and routing
- Authentication/authorization patterns
- Build and deployment procedures
- Testing commands and coverage requirements
