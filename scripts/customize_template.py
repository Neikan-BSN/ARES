#!/usr/bin/env python3
"""Template customization script for Python projects."""

import sys
from pathlib import Path


def get_user_input() -> dict[str, str]:
    """Get project customization information from user."""
    print("🎨 Python Project Template Customization")
    print("=" * 40)
    print()

    config = {}

    config["ares"] = input("📦 Project name (snake_case): ").strip()
    if not config["ares"]:
        print("❌ Project name is required!")
        sys.exit(1)

    config["project_display"] = input("📋 Project display name: ").strip()
    if not config["project_display"]:
        config["project_display"] = config["ares"].replace("_", " ").title()

    config["description"] = input("📝 Project description: ").strip()
    if not config["description"]:
        config["description"] = "A modern Python project"

    config["author_name"] = input("👤 Author name: ").strip()
    if not config["author_name"]:
        config["author_name"] = "ARES Development Team"

    config["author_email"] = input("📧 Author email: ").strip()
    if not config["author_email"]:
        config["author_email"] = "dev@ares.local"

    config["github_user"] = input("🐙 GitHub username: ").strip()
    if not config["github_user"]:
        config["github_user"] = "ares-team"

    return config


def find_files_to_update() -> list[Path]:
    """Find all files that need template replacement."""
    files_to_update = []

    # Common file extensions and specific files
    patterns = ["*.py", "*.toml", "*.yaml", "*.yml", "*.md", "*.txt", "*.sh"]

    # Specific files
    specific_files = ["Makefile", ".env.doppler.template", ".env.DOPPLER_REQUIRED"]

    # Find files by pattern
    for pattern in patterns:
        files_to_update.extend(Path(".").rglob(pattern))

    # Add specific files
    for file_name in specific_files:
        file_path = Path(file_name)
        if file_path.exists():
            files_to_update.append(file_path)

    # Filter out unwanted directories
    excluded_dirs = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        ".pytest_cache",
        ".mypy_cache",
    }
    filtered_files = []

    for file_path in files_to_update:
        if not any(excluded_dir in file_path.parts for excluded_dir in excluded_dirs):
            filtered_files.append(file_path)

    return filtered_files


def update_file_content(file_path: Path, replacements: dict[str, str]) -> bool:
    """Update file content with replacements."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply replacements
        for old_value, new_value in replacements.items():
            content = content.replace(old_value, new_value)

        # Only write if content changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def rename_directories(config: dict[str, str]) -> None:
    """Rename template directories to match project name."""
    old_src_dir = Path("src/ares")
    new_src_dir = Path(f"src/{config['ares']}")

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
    if confirm not in ["y", "yes"]:
        print("❌ Customization cancelled")
        return

    # Define replacements
    replacements = {
        "ares": config["ares"],
        "Agent Reliability Enforcement System": config["project_display"],
        "Agent Reliability Enforcement System - Production-ready multi-agent coordination with MCP integration": config[
            "description"
        ],
        "ARES Development Team": config["author_name"],
        "dev@ares.local": config["author_email"],
        "ares-team": config["github_user"],
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
    print("🎉 Customization complete!")
    print(f"  📝 Updated {updated_count} files")
    print(f"  📦 Project: {config['project_display']}")
    print("  🚀 Ready for development!")

    print()
    print("Next steps:")
    print(
        "1. Set up Doppler: doppler setup --project",
        config["ares"],
        "--config development",
    )
    print("2. Install dependencies: make install")
    print("3. Start coding!")


if __name__ == "__main__":
    main()
