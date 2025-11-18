#!/usr/bin/env python3
"""
Pre-flight Check Script
Validates the system is ready to run before processing PDFs
"""

import sys
import os
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print a section header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} (need 3.8+)")
        return False

def check_imports():
    """Check required imports"""
    required = {
        'PyPDF2': 'PyPDF2',
        'langchain': 'langchain',
        'langchain_openai': 'langchain-openai',
        'langchain_core': 'langchain-core',
        'pydantic': 'pydantic',
        'openai': 'openai',
        'dotenv': 'python-dotenv'
    }
    
    all_ok = True
    for module, package in required.items():
        try:
            __import__(module)
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - Run: pip install {package}")
            all_ok = False
    
    return all_ok

def check_directories():
    """Check required directories exist"""
    base_dir = Path(__file__).parent
    required_dirs = {
        'data': base_dir / 'data',
        'src': base_dir / 'src',
        'database': base_dir / 'database',
        'outputs': base_dir / 'outputs'
    }
    
    all_ok = True
    for name, path in required_dirs.items():
        if path.exists():
            print_success(f"{name}/ directory")
        else:
            print_error(f"{name}/ directory missing")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Check .env file and API key"""
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print_error(".env file not found")
        print_warning("Create .env file: cp .env.example .env")
        return False
    
    print_success(".env file exists")
    
    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY', '')
    if api_key and api_key != 'your-openai-api-key-here':
        print_success("OPENAI_API_KEY is set")
        return True
    else:
        print_error("OPENAI_API_KEY not configured in .env")
        return False

def check_pdf_files():
    """Check for PDF files"""
    data_dir = Path(__file__).parent / 'data'
    pdf_files = list(data_dir.glob('*.pdf')) + list(data_dir.glob('*.PDF'))
    
    if pdf_files:
        print_success(f"Found {len(pdf_files)} PDF file(s)")
        return True
    else:
        print_warning("No PDF files found in data/ folder")
        print_warning("Add PDF files before running extraction")
        return False

def check_src_modules():
    """Check source modules can be imported"""
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    
    modules = [
        ('config', 'Configuration'),
        ('pdf_extractor', 'PDF Extractor'),
        ('llm_extractor', 'LLM Extractor'),
        ('database', 'Database Manager'),
        ('main', 'Main Pipeline')
    ]
    
    all_ok = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print_success(f"{display_name}")
        except Exception as e:
            print_error(f"{display_name} - {str(e)[:50]}")
            all_ok = False
    
    return all_ok

def main():
    """Run all checks"""
    print_header("IDE Index - Pre-flight System Check")
    
    checks = []
    
    # Python version
    print(f"\n{BLUE}Checking Python Version...{RESET}")
    checks.append(check_python_version())
    
    # Required packages
    print(f"\n{BLUE}Checking Required Packages...{RESET}")
    checks.append(check_imports())
    
    # Directories
    print(f"\n{BLUE}Checking Directory Structure...{RESET}")
    checks.append(check_directories())
    
    # Environment file
    print(f"\n{BLUE}Checking Configuration...{RESET}")
    env_ok = check_env_file()
    checks.append(env_ok)
    
    # PDF files
    print(f"\n{BLUE}Checking PDF Files...{RESET}")
    pdf_ok = check_pdf_files()
    # Don't fail if no PDFs, just warn
    
    # Source modules
    print(f"\n{BLUE}Checking Source Modules...{RESET}")
    checks.append(check_src_modules())
    
    # Summary
    print_header("Pre-flight Check Summary")
    
    if all(checks):
        print_success("All critical checks passed!")
        if not env_ok:
            print_warning("\nNote: Set OPENAI_API_KEY in .env before running")
        if not pdf_ok:
            print_warning("Note: Add PDF files to data/ folder before running")
        
        print(f"\n{GREEN}Ready to run:{RESET}")
        print("  python src/main.py --max-chunks 5  (test run)")
        print("  python src/main.py                 (full extraction)")
        print("\nOr see QUICKSTART.md for detailed instructions")
        return 0
    else:
        print_error("\nSome checks failed. Please fix the issues above.")
        print("\nFor help:")
        print("  - See FIXES.md for recent fixes")
        print("  - See QUICKSTART.md for setup instructions")
        print("  - Run: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
