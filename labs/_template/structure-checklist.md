# Lab Structure Checklist

Use this checklist when creating a new lab:

## Directory Structure

- [ ] `labs/lab-XX-[name]/`
  - [ ] `README.md` - Lab-specific guide
  - [ ] `ADR.md` - Architecture decisions (if applicable)
  - [ ] `app/`
    - [ ] `src/[package_name]/` - Main application code
      - [ ] `__init__.py`
      - [ ] `[main_module].py`
      - [ ] `lambda_handler.py` (if Lambda-based)
      - [ ] `utils/` (if needed)
    - [ ] `tests/` - Test files
    - [ ] `requirements.txt` - Python dependencies
    - [ ] `.env.example` - Environment variable template
    - [ ] `main.py` - CLI entrypoint
  - [ ] `infra/`
    - [ ] `terraform/` - Terraform configuration
      - [ ] `main.tf`
      - [ ] `variables.tf`
      - [ ] `outputs.tf`
      - [ ] `README.md`
      - [ ] `.gitignore`
  - [ ] `data/` - Test data and samples
  - [ ] `diagrams/` - Architecture diagrams (if applicable)

## Code Requirements

- [ ] All imports use relative or package imports (no hardcoded paths)
- [ ] Configuration via environment variables or CLI args
- [ ] Lambda handler separated from core logic
- [ ] Proper Python package structure with `__init__.py` files

## Documentation

- [ ] Lab README with scenario, architecture, prerequisites, quick start
- [ ] ADR.md with architectural decisions (if applicable)
- [ ] Code comments and docstrings
- [ ] Updated root README.md with lab entry

## Testing

- [ ] Local execution works
- [ ] Terraform deployment works
- [ ] End-to-end test documented

