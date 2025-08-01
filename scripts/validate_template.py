#!/usr/bin/env python3
"""Template workspace validation and status check."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return Path(file_path).exists()


def check_directory_exists(dir_path: str) -> bool:
    """Check if a directory exists."""
    return Path(dir_path).is_dir()


def validate_template_structure() -> Tuple[List[str], List[str]]:
    """Validate the template structure."""
    required_files = [
        "pyproject.toml",
        "Makefile", 
        ".pre-commit-config.yaml",
        ".env.doppler.template",
        ".env.DOPPLER_REQUIRED",
        ".gitignore",
        ".secrets.baseline",
        "README.md",
        "mkdocs.yml",
        "TEMPLATE_SUMMARY.md",
    ]
    
    required_directories = [
        "src",
        "src/project_name",
        "tests",
        "scripts",
        "docs",
        ".github",
        ".github/workflows",
        "config",
    ]
    
    script_files = [
        "scripts/setup_project.sh",
        "scripts/customize_template.py",
        "scripts/backup.sh",
        "scripts/finalize_template.sh",
    ]
    
    workflow_files = [
        ".github/workflows/ci.yml",
        ".github/workflows/health-monitor.yml", 
        ".github/workflows/lint-repair-validation.yml",
    ]
    
    source_files = [
        "src/project_name/__init__.py",
        "src/project_name/main.py",
        "src/project_name/cli.py",
    ]
    
    test_files = [
        "tests/__init__.py",
        "tests/test_main.py",
    ]
    
    doc_files = [
        "docs/index.md",
        "docs/installation.md",
        "docs/quickstart.md",
    ]
    
    all_files = (required_files + script_files + workflow_files + 
                source_files + test_files + doc_files)
    all_dirs = required_directories
    
    missing_files = []
    missing_dirs = []
    
    for file_path in all_files:
        if not check_file_exists(file_path):
            missing_files.append(file_path)
    
    for dir_path in all_dirs:
        if not check_directory_exists(dir_path):
            missing_dirs.append(dir_path)
    
    return missing_files, missing_dirs


def count_lines_in_file(file_path: str) -> int:
    """Count lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except Exception:
        return 0


def validate_script_lengths() -> Dict[str, int]:
    """Validate that scripts are under 400 lines."""
    scripts = [
        "scripts/setup_project.sh",
        "scripts/customize_template.py",
        "scripts/backup.sh",
        "scripts/finalize_template.sh",
    ]
    
    script_lengths = {}
    for script in scripts:
        if check_file_exists(script):
            lines = count_lines_in_file(script)
            script_lengths[script] = lines
    
    return script_lengths


def check_placeholders() -> List[str]:
    """Check for template placeholders in key files."""
    placeholders = [
        "project_name",
        "PROJECT_NAME", 
        "Your Name",
        "your.email@example.com",
        "your-username",
    ]
    
    files_to_check = [
        "pyproject.toml",
        "README.md",
        "src/project_name/__init__.py",
    ]
    
    found_placeholders = []
    
    for file_path in files_to_check:
        if check_file_exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for placeholder in placeholders:
                        if placeholder in content:
                            found_placeholders.append(f"{placeholder} in {file_path}")
            except Exception:
                pass
    
    return found_placeholders


def main():
    """Main validation function."""
    print("🔍 Python Project Template - Validation Report")
    print("=" * 50)
    print()
    
    # Check if we're in the right directory
    if not check_file_exists("pyproject.toml"):
        print("❌ Error: Not in template workspace root directory")
        print("   Expected to find pyproject.toml")
        sys.exit(1)
    
    # Validate structure
    print("📁 Checking template structure...")
    missing_files, missing_dirs = validate_template_structure()
    
    if not missing_files and not missing_dirs:
        print("✅ All required files and directories present")
    else:
        if missing_files:
            print("❌ Missing files:")
            for file_path in missing_files:
                print(f"   - {file_path}")
        if missing_dirs:
            print("❌ Missing directories:")
            for dir_path in missing_dirs:
                print(f"   - {dir_path}")
    
    print()
    
    # Check script lengths (must be under 400 lines)
    print("📏 Checking script lengths (requirement: <400 lines)...")
    script_lengths = validate_script_lengths()
    
    all_under_limit = True
    for script, lines in script_lengths.items():
        status = "✅" if lines < 400 else "❌"
        print(f"   {status} {script}: {lines} lines")
        if lines >= 400:
            all_under_limit = False
    
    if all_under_limit:
        print("✅ All scripts under 400 line limit")
    
    print()
    
    # Check for template placeholders
    print("🎯 Checking template placeholders...")
    placeholders = check_placeholders()
    
    if placeholders:
        print("✅ Template placeholders found (ready for customization):")
        for placeholder in placeholders[:5]:  # Show first 5
            print(f"   - {placeholder}")
        if len(placeholders) > 5:
            print(f"   ... and {len(placeholders) - 5} more")
    else:
        print("⚠️  No template placeholders found (may be already customized)")
    
    print()
    
    # Feature summary
    print("🚀 Template Features Summary:")
    print("   ✅ Python 3.12.10 targeting")
    print("   ✅ UV package management")
    print("   ✅ Minimal but comprehensive dependencies")
    print("   ✅ Interactive setup scripts")
    print("   ✅ GitHub Actions workflows")
    print("   ✅ Doppler secrets management")
    print("   ✅ Security scanning tools")
    print("   ✅ Pre-commit hooks")
    print("   ✅ Documentation framework")
    print("   ✅ Comprehensive Makefile")
    
    print()
    
    # Usage instructions
    print("📋 Next Steps:")
    print("1. Copy template: cp -r template_workspace/ my_project/")
    print("2. Run setup: ./scripts/setup_project.sh")
    print("3. Or customize: python scripts/customize_template.py")
    print("4. Install deps: make install")
    print("5. Start coding: make run")
    
    print()
    
    # Status summary
    total_issues = len(missing_files) + len(missing_dirs)
    if total_issues == 0 and all_under_limit:
        print("🎉 Template validation PASSED! Ready for use.")
        sys.exit(0)
    else:
        print(f"⚠️  Template validation found {total_issues} issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
