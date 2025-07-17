#!/usr/bin/env python3
"""Automated version bumping script for MAC Address Changer.

This script automatically updates version numbers across all relevant files
and follows semantic versioning principles.

Usage:
    python scripts/bump_version.py patch
    python scripts/bump_version.py minor
    python scripts/bump_version.py major
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Tuple, Optional
import json
from datetime import datetime


class VersionBumper:
    """Handle version bumping across multiple files."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.files_to_update = {
            "mac_changer.py": self._update_main_file,
            "setup.py": self._update_setup_file,
            "pyproject.toml": self._update_pyproject_file,
            "CLAUDE.md": self._update_claude_file,
        }

    def get_current_version(self) -> str:
        """Extract current version from mac_changer.py."""
        mac_changer_file = self.project_root / "mac_changer.py"

        if not mac_changer_file.exists():
            raise FileNotFoundError(f"mac_changer.py not found in {self.project_root}")

        content = mac_changer_file.read_text()

        # Look for __version__ = "x.y.z"
        version_match = re.search(
            r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']', content
        )
        if not version_match:
            raise ValueError("Could not find __version__ in mac_changer.py")

        return version_match.group(1)

    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse version string into major, minor, patch tuple."""
        try:
            parts = version.split(".")
            if len(parts) != 3:
                raise ValueError(f"Invalid version format: {version}")

            return int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError as e:
            raise ValueError(f"Invalid version format: {version}") from e

    def bump_version(self, version: str, bump_type: str) -> str:
        """Bump version according to semantic versioning."""
        major, minor, patch = self.parse_version(version)

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

        return f"{major}.{minor}.{patch}"

    def _update_main_file(self, content: str, new_version: str) -> str:
        """Update version in mac_changer.py."""
        # Update __version__ = "x.y.z"
        content = re.sub(
            r'(__version__\s*=\s*["\'])\d+\.\d+\.\d+(["\'])',
            f"\\g<1>{new_version}\\g<2>",
            content,
        )

        # Update version in docstring if present
        content = re.sub(r"(Version:\s*)\d+\.\d+\.\d+", f"\\g<1>{new_version}", content)

        return content

    def _update_setup_file(self, content: str, new_version: str) -> str:
        """Update version in setup.py."""
        # Update version in get_version function if it exists
        content = re.sub(
            r'(version\s*=\s*["\'])\d+\.\d+\.\d+(["\'])',
            f"\\g<1>{new_version}\\g<2>",
            content,
        )

        # Update version in setup() call
        content = re.sub(
            r"(version\s*=\s*get_version\(\))", f'version="{new_version}"', content
        )

        return content

    def _update_pyproject_file(self, content: str, new_version: str) -> str:
        """Update version in pyproject.toml."""
        content = re.sub(
            r'(version\s*=\s*["\'])\d+\.\d+\.\d+(["\'])',
            f"\\g<1>{new_version}\\g<2>",
            content,
        )
        return content

    def _update_claude_file(self, content: str, new_version: str) -> str:
        """Update version in CLAUDE.md."""
        # Update version in document
        content = re.sub(
            r"(\*\*Version\*\*:\s*)\d+\.\d+\.\d+", f"\\g<1>{new_version}", content
        )

        # Update last updated date
        current_date = datetime.now().strftime("%B %Y")
        content = re.sub(
            r"(\*\*Last Updated\*\*:\s*)[A-Za-z]+ \d{4}",
            f"\\g<1>{current_date}",
            content,
        )

        return content

    def update_files(self, new_version: str) -> None:
        """Update version in all relevant files."""
        updated_files = []

        for filename, update_func in self.files_to_update.items():
            file_path = self.project_root / filename

            if not file_path.exists():
                print(f"⚠️  Warning: {filename} not found, skipping")
                continue

            try:
                content = file_path.read_text()
                updated_content = update_func(content, new_version)

                if content != updated_content:
                    file_path.write_text(updated_content)
                    updated_files.append(filename)
                    print(f"✅ Updated {filename}")
                else:
                    print(f"ℹ️  No changes needed in {filename}")

            except Exception as e:
                print(f"❌ Error updating {filename}: {e}")
                raise

        return updated_files

    def create_changelog_entry(
        self, old_version: str, new_version: str, bump_type: str
    ) -> None:
        """Create or update changelog entry."""
        changelog_file = self.project_root / "CHANGELOG.md"

        # Create changelog if it doesn't exist
        if not changelog_file.exists():
            changelog_content = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
        else:
            changelog_content = changelog_file.read_text()

        # Create new entry
        today = datetime.now().strftime("%Y-%m-%d")
        entry = f"""## [{new_version}] - {today}

### {bump_type.capitalize()} Release

- Version bump from {old_version} to {new_version}
- Automated version update

"""

        # Insert after the header
        lines = changelog_content.split("\n")
        insert_pos = 3  # After header and blank line

        new_lines = lines[:insert_pos] + entry.split("\n") + lines[insert_pos:]

        changelog_file.write_text("\n".join(new_lines))
        print(f"✅ Updated CHANGELOG.md")

    def run_tests(self) -> bool:
        """Run tests to ensure version bump didn't break anything."""
        print("🧪 Running tests...")

        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "test_mac_changer.py", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ All tests passed")
                return True
            else:
                print(f"❌ Tests failed:\n{result.stdout}\n{result.stderr}")
                return False

        except FileNotFoundError:
            print("⚠️  pytest not found, skipping tests")
            return True
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False

    def git_operations(self, new_version: str, updated_files: list) -> None:
        """Perform git operations for version bump."""
        try:
            # Check if git is available and we're in a git repo
            subprocess.run(["git", "status"], check=True, capture_output=True)

            # Add updated files
            for file in updated_files + ["CHANGELOG.md"]:
                file_path = self.project_root / file
                if file_path.exists():
                    subprocess.run(["git", "add", str(file_path)], check=True)

            # Commit changes
            commit_message = f"bump version to {new_version}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            # Create git tag
            tag_name = f"v{new_version}"
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", f"Release version {new_version}"],
                check=True,
            )

            print(f"✅ Git commit and tag created: {tag_name}")
            print(
                f"📝 To push changes: git push origin main && git push origin {tag_name}"
            )

        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            print("Please handle git operations manually")
        except FileNotFoundError:
            print("⚠️  Git not found, skipping git operations")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Bump version following semantic versioning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/bump_version.py patch    # 1.0.0 -> 1.0.1
    python scripts/bump_version.py minor    # 1.0.0 -> 1.1.0
    python scripts/bump_version.py major    # 1.0.0 -> 2.0.0
        """,
    )

    parser.add_argument(
        "bump_type", choices=["major", "minor", "patch"], help="Type of version bump"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )

    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests after version bump",
    )

    parser.add_argument(
        "--skip-git", action="store_true", help="Skip git operations (commit and tag)"
    )

    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Initialize version bumper
    bumper = VersionBumper(project_root)

    try:
        # Get current version
        current_version = bumper.get_current_version()
        print(f"📋 Current version: {current_version}")

        # Calculate new version
        new_version = bumper.bump_version(current_version, args.bump_type)
        print(f"🎯 New version: {new_version}")

        if args.dry_run:
            print("🔍 Dry run mode - showing what would be changed:")
            print(f"  {current_version} -> {new_version}")

            for filename in bumper.files_to_update.keys():
                file_path = project_root / filename
                if file_path.exists():
                    print(f"  Would update: {filename}")
                else:
                    print(f"  Would skip: {filename} (not found)")

            return

        # Update files
        print("📝 Updating files...")
        updated_files = bumper.update_files(new_version)

        # Create changelog entry
        bumper.create_changelog_entry(current_version, new_version, args.bump_type)

        # Run tests
        if not args.skip_tests:
            if not bumper.run_tests():
                print("❌ Tests failed, aborting version bump")
                sys.exit(1)

        # Git operations
        if not args.skip_git:
            bumper.git_operations(new_version, updated_files)

        print(f"🎉 Version successfully bumped to {new_version}")
        print("\n📋 Next steps:")
        print("  1. Review the changes")
        print("  2. Push to remote: git push origin main")
        print(f"  3. Push tag: git push origin v{new_version}")
        print("  4. Create GitHub release")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
