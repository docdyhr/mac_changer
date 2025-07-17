#!/usr/bin/env python3
"""MAC Address Backup and Restore System.

This script provides comprehensive backup and restore functionality for MAC addresses,
ensuring safe MAC address changes with the ability to restore original configurations.

Features:
- Automatic backup before any MAC address change
- Restore original MAC addresses
- Backup validation and integrity checks
- Multiple backup storage formats
- Rollback procedures for failed changes

Usage:
    python scripts/backup_restore.py backup
    python scripts/backup_restore.py restore
    python scripts/backup_restore.py list
    python scripts/backup_restore.py verify
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import shutil


class MACBackupError(Exception):
    """Custom exception for MAC backup operations."""

    pass


class MACBackupManager:
    """Manage MAC address backups and restoration."""

    def __init__(self, backup_dir: Optional[Path] = None):
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = backup_dir or self.project_root / "backups" / "mac_addresses"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.config = {
            "backup_retention_days": 30,
            "max_backups": 100,
            "backup_format": "json",
            "verify_checksums": True,
            "auto_backup": True,
        }

        # Load configuration if exists
        self.config_file = self.backup_dir / "config.json"
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                print(f"Warning: Could not load config: {e}")

    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")

    def get_system_info(self) -> Dict:
        """Get system information for backup metadata."""
        return {
            "hostname": platform.node(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "timestamp": datetime.now().isoformat(),
            "timezone": time.tzname,
        }

    def run_command(self, cmd: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """Run command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -2, "", str(e)

    def get_interface_mac(self, interface: str) -> Optional[str]:
        """Get MAC address for a specific interface."""
        returncode, stdout, stderr = self.run_command(["ifconfig", interface])

        if returncode != 0:
            return None

        # Parse MAC address from ifconfig output
        import re

        mac_match = re.search(r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}", stdout)
        if mac_match:
            return mac_match.group(0).lower()
        return None

    def get_all_interfaces(self) -> Dict[str, Dict]:
        """Get all network interfaces and their MAC addresses."""
        interfaces = {}

        # Get list of interfaces
        returncode, stdout, stderr = self.run_command(["ifconfig", "-a"])
        if returncode != 0:
            raise MACBackupError(f"Failed to get interfaces: {stderr}")

        # Parse interfaces
        import re

        current_interface = None

        for line in stdout.split("\n"):
            line = line.strip()
            if not line:
                continue

            # New interface
            if not line.startswith(" ") and ":" in line:
                interface_name = line.split(":")[0].strip()
                current_interface = interface_name
                interfaces[interface_name] = {
                    "name": interface_name,
                    "mac_address": None,
                    "status": "unknown",
                    "type": self._guess_interface_type(interface_name),
                    "ip_address": None,
                }

                # Check status
                if "UP" in line:
                    interfaces[interface_name]["status"] = "up"
                else:
                    interfaces[interface_name]["status"] = "down"

            # Parse MAC address
            elif current_interface and ("ether" in line or "HWaddr" in line):
                mac_match = re.search(r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}", line)
                if mac_match:
                    interfaces[current_interface]["mac_address"] = mac_match.group(
                        0
                    ).lower()

            # Parse IP address
            elif current_interface and "inet " in line:
                ip_match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", line)
                if ip_match:
                    interfaces[current_interface]["ip_address"] = ip_match.group(1)

        return interfaces

    def _guess_interface_type(self, interface_name: str) -> str:
        """Guess interface type from name."""
        name_lower = interface_name.lower()

        if name_lower.startswith(("eth", "en")):
            return "ethernet"
        elif name_lower.startswith(("wlan", "wl", "wifi")):
            return "wireless"
        elif name_lower.startswith("lo"):
            return "loopback"
        elif name_lower.startswith("br"):
            return "bridge"
        elif name_lower.startswith("tun"):
            return "tunnel"
        elif name_lower.startswith("docker"):
            return "container"
        else:
            return "unknown"

    def calculate_checksum(self, data: str) -> str:
        """Calculate SHA-256 checksum of data."""
        return hashlib.sha256(data.encode()).hexdigest()

    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of all current MAC addresses."""
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"mac_backup_{timestamp}"

        print(f"Creating MAC address backup: {backup_name}")

        # Get all interfaces
        try:
            interfaces = self.get_all_interfaces()
        except Exception as e:
            raise MACBackupError(f"Failed to get interfaces: {e}")

        # Create backup data
        backup_data = {
            "backup_name": backup_name,
            "timestamp": datetime.now().isoformat(),
            "system_info": self.get_system_info(),
            "interfaces": interfaces,
            "backup_version": "1.0",
            "tool_version": "1.0.0",
        }

        # Calculate checksums
        interface_checksums = {}
        for interface_name, interface_info in interfaces.items():
            if interface_info.get("mac_address"):
                checksum_data = f"{interface_name}:{interface_info['mac_address']}"
                interface_checksums[interface_name] = self.calculate_checksum(
                    checksum_data
                )

        backup_data["checksums"] = interface_checksums

        # Save backup
        backup_file = self.backup_dir / f"{backup_name}.json"
        try:
            with open(backup_file, "w") as f:
                json.dump(backup_data, f, indent=2)

            print(f"✅ Backup created successfully: {backup_file}")
            print(
                f"   Backed up {len([i for i in interfaces.values() if i.get('mac_address')])} interfaces"
            )

            # Clean up old backups
            self.cleanup_old_backups()

            return str(backup_file)

        except Exception as e:
            raise MACBackupError(f"Failed to save backup: {e}")

    def list_backups(self) -> List[Dict]:
        """List all available backups."""
        backups = []

        for backup_file in self.backup_dir.glob("*.json"):
            if backup_file.name == "config.json":
                continue

            try:
                with open(backup_file, "r") as f:
                    backup_data = json.load(f)

                backup_info = {
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "name": backup_data.get("backup_name", backup_file.stem),
                    "timestamp": backup_data.get("timestamp"),
                    "system_info": backup_data.get("system_info", {}),
                    "interface_count": len(backup_data.get("interfaces", {})),
                    "file_size": backup_file.stat().st_size,
                    "valid": True,
                }

                backups.append(backup_info)

            except Exception as e:
                # Invalid backup file
                backup_info = {
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "name": backup_file.stem,
                    "timestamp": None,
                    "system_info": {},
                    "interface_count": 0,
                    "file_size": backup_file.stat().st_size,
                    "valid": False,
                    "error": str(e),
                }
                backups.append(backup_info)

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return backups

    def load_backup(self, backup_name: str) -> Dict:
        """Load a specific backup."""
        backup_file = self.backup_dir / f"{backup_name}.json"

        if not backup_file.exists():
            # Try to find backup by partial name
            matching_backups = [
                b for b in self.list_backups() if backup_name in b["name"]
            ]
            if matching_backups:
                backup_file = Path(matching_backups[0]["path"])
            else:
                raise MACBackupError(f"Backup not found: {backup_name}")

        try:
            with open(backup_file, "r") as f:
                backup_data = json.load(f)

            # Verify backup integrity
            if not self.verify_backup_integrity(backup_data):
                raise MACBackupError("Backup integrity check failed")

            return backup_data

        except json.JSONDecodeError as e:
            raise MACBackupError(f"Invalid backup file format: {e}")
        except Exception as e:
            raise MACBackupError(f"Failed to load backup: {e}")

    def verify_backup_integrity(self, backup_data: Dict) -> bool:
        """Verify backup data integrity."""
        if not self.config["verify_checksums"]:
            return True

        interfaces = backup_data.get("interfaces", {})
        checksums = backup_data.get("checksums", {})

        for interface_name, interface_info in interfaces.items():
            if interface_info.get("mac_address"):
                checksum_data = f"{interface_name}:{interface_info['mac_address']}"
                expected_checksum = self.calculate_checksum(checksum_data)

                if interface_name in checksums:
                    if checksums[interface_name] != expected_checksum:
                        print(f"❌ Checksum mismatch for {interface_name}")
                        return False

        return True

    def restore_from_backup(
        self,
        backup_name: str,
        interfaces: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> bool:
        """Restore MAC addresses from backup."""
        print(f"Restoring from backup: {backup_name}")

        # Load backup
        try:
            backup_data = self.load_backup(backup_name)
        except Exception as e:
            print(f"❌ Failed to load backup: {e}")
            return False

        # Get interfaces to restore
        backup_interfaces = backup_data.get("interfaces", {})
        if interfaces:
            # Filter to specific interfaces
            restore_interfaces = {
                k: v for k, v in backup_interfaces.items() if k in interfaces
            }
        else:
            # Restore all interfaces with MAC addresses
            restore_interfaces = {
                k: v for k, v in backup_interfaces.items() if v.get("mac_address")
            }

        if not restore_interfaces:
            print("❌ No interfaces to restore")
            return False

        print(f"Will restore {len(restore_interfaces)} interfaces:")
        for interface_name, interface_info in restore_interfaces.items():
            print(f"  {interface_name}: {interface_info.get('mac_address', 'No MAC')}")

        if dry_run:
            print("🔍 Dry run mode - no changes will be made")
            return True

        # Confirm restoration
        if not self._confirm_restore():
            print("❌ Restoration cancelled by user")
            return False

        # Create backup before restoration
        if self.config["auto_backup"]:
            try:
                pre_restore_backup = f"pre_restore_{int(time.time())}"
                self.create_backup(pre_restore_backup)
                print(f"📋 Created pre-restore backup: {pre_restore_backup}")
            except Exception as e:
                print(f"⚠️  Warning: Could not create pre-restore backup: {e}")

        # Restore each interface
        success_count = 0
        failed_interfaces = []

        for interface_name, interface_info in restore_interfaces.items():
            mac_address = interface_info.get("mac_address")
            if not mac_address:
                continue

            try:
                if self._restore_interface_mac(interface_name, mac_address):
                    print(f"✅ Restored {interface_name} to {mac_address}")
                    success_count += 1
                else:
                    print(f"❌ Failed to restore {interface_name}")
                    failed_interfaces.append(interface_name)
            except Exception as e:
                print(f"❌ Error restoring {interface_name}: {e}")
                failed_interfaces.append(interface_name)

        # Summary
        print(f"\n📊 Restoration Summary:")
        print(f"   Successfully restored: {success_count}")
        print(f"   Failed: {len(failed_interfaces)}")

        if failed_interfaces:
            print(f"   Failed interfaces: {', '.join(failed_interfaces)}")

        return len(failed_interfaces) == 0

    def _confirm_restore(self) -> bool:
        """Confirm restoration with user."""
        try:
            response = input("Are you sure you want to restore MAC addresses? (y/N): ")
            return response.lower() in ["y", "yes"]
        except (KeyboardInterrupt, EOFError):
            return False

    def _restore_interface_mac(self, interface: str, mac_address: str) -> bool:
        """Restore MAC address for a specific interface."""
        try:
            # Add project root to Python path for import
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))

            import mac_changer

            # Create MAC changer instance
            mac_changer_instance = mac_changer.MACChanger()

            # Validate MAC address
            validated_mac = mac_changer_instance.validate_mac_address(mac_address)

            # Change MAC address
            return mac_changer_instance.change_mac_address(interface, validated_mac)

        except Exception as e:
            print(f"Error in _restore_interface_mac: {e}")
            return False

    def verify_backup(self, backup_name: str) -> bool:
        """Verify a backup file."""
        try:
            backup_data = self.load_backup(backup_name)

            print(f"📋 Verifying backup: {backup_name}")
            print(f"   Timestamp: {backup_data.get('timestamp', 'Unknown')}")
            print(
                f"   System: {backup_data.get('system_info', {}).get('system', 'Unknown')}"
            )
            print(
                f"   Hostname: {backup_data.get('system_info', {}).get('hostname', 'Unknown')}"
            )

            interfaces = backup_data.get("interfaces", {})
            interfaces_with_mac = {
                k: v for k, v in interfaces.items() if v.get("mac_address")
            }

            print(f"   Interfaces: {len(interfaces_with_mac)}")

            for interface_name, interface_info in interfaces_with_mac.items():
                print(
                    f"     {interface_name}: {interface_info.get('mac_address')} ({interface_info.get('type', 'unknown')})"
                )

            # Verify checksums
            if self.config["verify_checksums"]:
                if self.verify_backup_integrity(backup_data):
                    print("✅ Backup integrity verified")
                else:
                    print("❌ Backup integrity check failed")
                    return False

            return True

        except Exception as e:
            print(f"❌ Backup verification failed: {e}")
            return False

    def cleanup_old_backups(self) -> None:
        """Clean up old backups based on retention policy."""
        if self.config["backup_retention_days"] <= 0:
            return

        cutoff_time = time.time() - (
            self.config["backup_retention_days"] * 24 * 60 * 60
        )
        backups = self.list_backups()

        removed_count = 0
        for backup in backups:
            try:
                backup_file = Path(backup["path"])
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    removed_count += 1
            except Exception as e:
                print(f"Warning: Could not remove old backup {backup['filename']}: {e}")

        # Also limit total number of backups
        if len(backups) > self.config["max_backups"]:
            backups_to_remove = sorted(backups, key=lambda x: x.get("timestamp", ""))[
                : -self.config["max_backups"]
            ]
            for backup in backups_to_remove:
                try:
                    Path(backup["path"]).unlink()
                    removed_count += 1
                except Exception as e:
                    print(f"Warning: Could not remove backup {backup['filename']}: {e}")

        if removed_count > 0:
            print(f"🧹 Cleaned up {removed_count} old backups")

    def export_backup(self, backup_name: str, export_path: str) -> bool:
        """Export backup to external location."""
        try:
            backup_data = self.load_backup(backup_name)
            export_file = Path(export_path)

            # Ensure export directory exists
            export_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy backup file
            backup_file = self.backup_dir / f"{backup_name}.json"
            shutil.copy2(backup_file, export_file)

            print(f"✅ Backup exported to: {export_file}")
            return True

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False

    def import_backup(self, import_path: str) -> bool:
        """Import backup from external location."""
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                raise MACBackupError(f"Import file not found: {import_path}")

            # Load and verify backup
            with open(import_file, "r") as f:
                backup_data = json.load(f)

            if not self.verify_backup_integrity(backup_data):
                raise MACBackupError("Imported backup failed integrity check")

            # Copy to backup directory
            backup_name = backup_data.get("backup_name", import_file.stem)
            backup_file = self.backup_dir / f"{backup_name}.json"

            shutil.copy2(import_file, backup_file)

            print(f"✅ Backup imported: {backup_name}")
            return True

        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="MAC Address Backup and Restore System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python backup_restore.py backup
    python backup_restore.py backup --name my_backup
    python backup_restore.py restore --name my_backup
    python backup_restore.py restore --name my_backup --interface eth0
    python backup_restore.py list
    python backup_restore.py verify --name my_backup
    python backup_restore.py cleanup
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create MAC address backup")
    backup_parser.add_argument("--name", type=str, help="Backup name")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore MAC addresses")
    restore_parser.add_argument("--name", type=str, required=True, help="Backup name")
    restore_parser.add_argument(
        "--interface", type=str, action="append", help="Specific interface to restore"
    )
    restore_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be restored"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List available backups")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify backup integrity")
    verify_parser.add_argument("--name", type=str, required=True, help="Backup name")

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old backups")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export backup")
    export_parser.add_argument("--name", type=str, required=True, help="Backup name")
    export_parser.add_argument(
        "--output", type=str, required=True, help="Output file path"
    )

    # Import command
    import_parser = subparsers.add_parser("import", help="Import backup")
    import_parser.add_argument(
        "--file", type=str, required=True, help="Backup file path"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        # Create backup manager
        backup_manager = MACBackupManager()

        if args.command == "backup":
            backup_manager.create_backup(args.name)

        elif args.command == "restore":
            success = backup_manager.restore_from_backup(
                args.name, interfaces=args.interface, dry_run=args.dry_run
            )
            if not success:
                sys.exit(1)

        elif args.command == "list":
            backups = backup_manager.list_backups()
            if not backups:
                print("No backups found")
            else:
                print(f"Found {len(backups)} backup(s):")
                for backup in backups:
                    status = "✅" if backup["valid"] else "❌"
                    print(f"  {status} {backup['name']}")
                    print(f"      Timestamp: {backup.get('timestamp', 'Unknown')}")
                    print(f"      Interfaces: {backup['interface_count']}")
                    print(f"      Size: {backup['file_size']} bytes")
                    if not backup["valid"]:
                        print(f"      Error: {backup.get('error', 'Unknown')}")
                    print()

        elif args.command == "verify":
            success = backup_manager.verify_backup(args.name)
            if not success:
                sys.exit(1)

        elif args.command == "cleanup":
            backup_manager.cleanup_old_backups()

        elif args.command == "export":
            success = backup_manager.export_backup(args.name, args.output)
            if not success:
                sys.exit(1)

        elif args.command == "import":
            success = backup_manager.import_backup(args.file)
            if not success:
                sys.exit(1)

    except MACBackupError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
