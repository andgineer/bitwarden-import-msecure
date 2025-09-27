# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python CLI tool that converts mSecure password manager exports to Bitwarden-compatible formats. The tool organizes secrets into meaningful folders instead of placing each secret in a separate folder like the built-in Bitwarden import tool.

## Development Commands

This project uses [invoke](https://docs.pyinvoke.org/en/stable/) for task management. Install with `pipx install invoke`.

### Essential Commands
- `invoke --list` - Show all available tasks
- `pytest` - Run tests (includes doctests via pytest.ini configuration)
- `invoke pre` - Run pre-commit checks (linting, formatting, etc.)
- `invoke reqs` - Upgrade requirements and install development dependencies
- `invoke compile-requirements` - Update requirements.txt files from .in files

### Testing
- `pytest` - Run all tests
- `pytest tests/test_specific.py` - Run specific test file
- `pytest -k "test_pattern"` - Run tests matching pattern

### Version Management
- `invoke version` - Show current version
- `invoke ver-release` - Bump release version
- `invoke ver-bug` - Bump bug fix version
- `invoke ver-feature` - Bump feature version

### Documentation
- `invoke docs-en` - Preview English documentation
- `invoke docs-ru` - Preview Russian documentation

## Architecture

### Core Components

**Entry Point**: `src/bitwarden_import_msecure/main.py`
- CLI interface using rich-click
- Handles command-line arguments and file validation
- Supports both CSV and JSON output formats
- Includes patching functionality for existing Bitwarden exports

**Conversion Logic**: `src/bitwarden_import_msecure/msecure_to_bitwarden.py`
- Main conversion orchestration
- Patch functionality for updating existing Bitwarden exports
- Format-agnostic conversion interface

**mSecure Parser**: `src/bitwarden_import_msecure/msecure.py`
- Parses mSecure CSV export format
- Handles different record types (login, card, note)
- Extracts fields, credentials, and organizes into folders
- Special handling for bank records and credit cards

**Output Writers**:
- `src/bitwarden_import_msecure/bitwarden_json.py` - JSON format (recommended)
- `src/bitwarden_import_msecure/bitwarden_csv.py` - CSV format (legacy)

### Data Flow

1. mSecure CSV export → `msecure.py` → parsed record dict
2. Parsed records → output writer (JSON/CSV) → Bitwarden-compatible file
3. Patch mode: existing Bitwarden export + mSecure data → updated export

### Key Features

- **Folder Organization**: Groups secrets by type/category instead of individual folders
- **Multiple Output Formats**: JSON (full features) and CSV (legacy)
- **Patch Mode**: Updates existing Bitwarden exports with missing data
- **Field Mapping**: Handles custom fields as either Bitwarden custom fields or notes
- **Type Detection**: Automatically categorizes as login, card, or note based on content

### Configuration Files

- `pyproject.toml` - Main project configuration, dependencies, and tool settings
- `pytest.ini` - Test configuration with doctest support
- `invoke.yml` - Invoke task runner configuration
- Requirements managed via `.in` files and compiled to `.txt` files

### Important Notes

- The tool is designed to handle edge cases in mSecure exports
- Patch functionality specifically addresses issues in older versions (pre-1.5.0)
- Uses UUID generation for Bitwarden compatibility
- Multilingual documentation support (English/Russian)
