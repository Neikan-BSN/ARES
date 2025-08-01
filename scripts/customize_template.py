#!/usr/bin/env python3
"""Template customization script for Python projects."""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List


def get_user_input() -> Dict[str, str]:
    """Get project customization information from user."""
    print("🎨 Python Project Template Customization")
    print("=" * 40)
    print()
    
    config = {}
    
    config['project_name'] = input("📦 Project name (snake_case): ").strip()
    if not config['project_name']:
        print("❌ Project name is required!")
        sys.exit(1)
    
    config['project_display'] = input("📋 Project display name: ").strip()
    if not config['project_display']:
        config['project_display'] = config['project_name'].replace('_', ' ').title()
    
    config['description'] = input("📝 Project description: ").strip()
    if not config['description']:
        config['description'] = "A modern Python project"
    
    config['author_name'] = input("👤 Author name: ").strip()
    if not config['author_name']:
        config['author_name'] = "Your Name"
    
    config['author_email'] = input("📧 Author email: ").strip()
    if not config['author_email']:
        config['author_email'] = "your.email@example.com"
    
    config['github_user'] = input("🐙 GitHub username: ").strip()
    if not config['github_user']:
        config['github_user'] = "your-username"
    
    return config


def find_files_to_update() -> List[Path]:
    """Find all files that need template replacement."""
    files_to_update = []
    
    # Common file extensions and specific files
    patterns = [
        "*.py", "*.toml", "*.yaml", "*.yml", "*.md", "*.txt", "*.sh"
    ]
    
    # Specific files
    specific_files = [
        "Makefile",
        ".env.doppler.template",
        ".env.DOPPLER_REQUIRED"
    ]
    
    # Find files by pattern
    for pattern in patterns:
        files_to_update.extend(Path('.').rglob(pattern))
    
    # Add specific files
    for file_name in specific_files:
        file_path = Path(file_name)
        if file_path.exists():
            files_to_update.append(file_path)
    
    # Filter out unwanted directories
    excluded_dirs = {'.git', '__pycache__', '.venv', 'venv', '.pytest_cache', '.mypy_cache'}
    filtered_files = []
    
    for file_path in files_to_update:
        if not any(excluded_dir in file_path.parts for excluded_dir in excluded_dirs):
            filtered_files.append(file_path)
    
    return filtered_files


def update_file_content(file_path: Path, replacements: Dict[str, str]) -> bool:
    """Update file content with replacements."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply replacements
        for old_value, new_value in replacements.items():
            content = content.replace(old_value, new_value)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def rename_directories(config: Dict[str, str]) -> None:
    """Rename template directories to match project name."""
    old_src_dir = Path('src/project_name')
    new_src_dir = Path(f"src/{config['project_name']}")
    
    if old_src_dir.exists() and old_src_dir != new_src_dir:
        try:
            old_src_dir.rename(new_src_dir)
            print(f"✅ Renamed {old_src_dir} → {new_src_dir}")
        except Exception as e:
            print(f"❌ Error renaming directory: {e}")


def main() -> None:
    """Main customization function."""
    print("Starting template customization...")
    print()
    
    # Get user configuration
    config = get_user_input()
    
    print()
    print("📋 Configuration Summary:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print()
    confirm = input("✅ Proceed with customization? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Customization cancelled")
        return
    
    # Define replacements
    replacements = {
        'project_name': config['project_name'],
        'PROJECT_NAME': config['project_display'],
        'A modern Python project template with best practices': config['description'],
        'Your Name': config['author_name'],
        'your.email@example.com': config['author_email'],
        'your-username': config['github_user'],
    }
    
    print()
    print("🔄 Customizing template files...")
    
    # Find and update files
    files_to_update = find_files_to_update()
    updated_count = 0
    
    for file_path in files_to_update:
        if update_file_content(file_path, replacements):
            print(f"  ✅ Updated {file_path}")
            updated_count += 1
    
    # Rename directories
    rename_directories(config)
    
    print()
    print(f"🎉 Customization complete!")
    print(f"  📝 Updated {updated_count} files")
    print(f"  📦 Project: {config['project_display']}")
    print(f"  🚀 Ready for development!")
    
    print()
    print("Next steps:")
    print("1. Set up Doppler: doppler setup --project", config['project_name'], "--config development")
    print("2. Install dependencies: make install")
    print("3. Start coding!")


if __name__ == "__main__":
    main()
