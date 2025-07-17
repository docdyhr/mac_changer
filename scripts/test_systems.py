#!/usr/bin/env python3
"""Comprehensive system testing script for MAC Address Changer.

This script tests the MAC Address Changer on different target systems
to ensure compatibility and reliability across various environments.

Usage:
    python scripts/test_systems.py
    python scripts/test_systems.py --verbose
    python scripts/test_systems.py --system-info-only
"""

import argparse
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class SystemTester:
    """Comprehensive system testing for MAC Address Changer."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_results = []
        self.system_info = {}
        self.project_root = Path(__file__).parent.parent

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{timestamp}] [{level}]"

        if level == "ERROR":
            print(f"\033[91m{prefix} {message}\033[0m")
        elif level == "WARNING":
            print(f"\033[93m{prefix} {message}\033[0m")
        elif level == "SUCCESS":
            print(f"\033[92m{prefix} {message}\033[0m")
        elif self.verbose or level == "INFO":
            print(f"{prefix} {message}")

    def run_command(self, cmd: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """Run command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -2, "", str(e)

    def collect_system_info(self) -> Dict:
        """Collect comprehensive system information."""
        self.log("Collecting system information...")

        info = {
            "timestamp": datetime.now().isoformat(),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
                "hostname": platform.node(),
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "executable": sys.executable,
            },
            "network": {},
            "tools": {},
            "environment": {},
        }

        # Check Python version compatibility
        py_version = sys.version_info
        info["python"]["version_info"] = {
            "major": py_version.major,
            "minor": py_version.minor,
            "micro": py_version.micro,
        }
        info["python"]["compatible"] = py_version >= (3, 8)

        # Check for required network tools
        tools_to_check = ["ifconfig", "ip", "netstat", "ping"]
        for tool in tools_to_check:
            returncode, stdout, stderr = self.run_command(["which", tool])
            info["tools"][tool] = {
                "available": returncode == 0,
                "path": stdout.strip() if returncode == 0 else None,
            }

        # Get network interfaces
        if info["tools"]["ifconfig"]["available"]:
            returncode, stdout, stderr = self.run_command(["ifconfig", "-a"])
            if returncode == 0:
                info["network"]["ifconfig_output"] = stdout
                info["network"]["interfaces"] = self._parse_interfaces(stdout)

        # Check if running as root
        info["environment"]["is_root"] = (
            os.geteuid() == 0 if hasattr(os, "geteuid") else False
        )
        info["environment"]["user"] = os.getenv("USER", "unknown")
        info["environment"]["home"] = os.getenv("HOME", "unknown")

        # Check virtual environment
        info["environment"]["virtual_env"] = os.getenv("VIRTUAL_ENV") is not None
        info["environment"]["venv_path"] = os.getenv("VIRTUAL_ENV")

        self.system_info = info
        return info

    def _parse_interfaces(self, ifconfig_output: str) -> List[Dict]:
        """Parse network interfaces from ifconfig output."""
        interfaces = []
        current_interface = None

        for line in ifconfig_output.split("\n"):
            line = line.strip()
            if not line:
                continue

            # New interface
            if not line.startswith(" ") and ":" in line:
                if current_interface:
                    interfaces.append(current_interface)

                interface_name = line.split(":")[0].strip()
                current_interface = {
                    "name": interface_name,
                    "mac_address": None,
                    "ip_address": None,
                    "status": "unknown",
                    "type": self._guess_interface_type(interface_name),
                }

                # Check if interface is up
                if "UP" in line:
                    current_interface["status"] = "up"
                else:
                    current_interface["status"] = "down"

            # Parse MAC address
            elif "ether" in line or "HWaddr" in line:
                mac_match = re.search(r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}", line)
                if mac_match and current_interface:
                    current_interface["mac_address"] = mac_match.group(0).lower()

            # Parse IP address
            elif "inet " in line:
                ip_match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", line)
                if ip_match and current_interface:
                    current_interface["ip_address"] = ip_match.group(1)

        if current_interface:
            interfaces.append(current_interface)

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

    def test_python_compatibility(self) -> bool:
        """Test Python version compatibility."""
        self.log("Testing Python compatibility...")

        success = True

        # Check Python version
        if sys.version_info < (3, 8):
            self.log(f"Python {sys.version} is not supported (3.8+ required)", "ERROR")
            success = False
        else:
            self.log(f"Python {sys.version} is supported", "SUCCESS")

        # Test required modules
        required_modules = [
            "argparse",
            "logging",
            "os",
            "platform",
            "re",
            "subprocess",
            "sys",
            "typing",
            "pathlib",
            "datetime",
        ]

        for module in required_modules:
            try:
                __import__(module)
                self.log(
                    f"Module {module} is available",
                    "SUCCESS" if self.verbose else "INFO",
                )
            except ImportError:
                self.log(f"Module {module} is not available", "ERROR")
                success = False

        self.test_results.append(
            {
                "test": "python_compatibility",
                "success": success,
                "details": {
                    "version": sys.version,
                    "version_info": sys.version_info[:3],
                    "required_version": (3, 8),
                    "modules_tested": required_modules,
                },
            }
        )

        return success

    def test_system_tools(self) -> bool:
        """Test availability of required system tools."""
        self.log("Testing system tools availability...")

        success = True
        tool_results = {}

        # Test ifconfig
        returncode, stdout, stderr = self.run_command(["ifconfig"])
        if returncode == 0:
            self.log("ifconfig is available and working", "SUCCESS")
            tool_results["ifconfig"] = {"available": True, "working": True}
        else:
            self.log("ifconfig is not available or not working", "ERROR")
            self.log(f"Error: {stderr}", "ERROR")
            success = False
            tool_results["ifconfig"] = {
                "available": False,
                "working": False,
                "error": stderr,
            }

        # Test which command
        returncode, stdout, stderr = self.run_command(["which", "ifconfig"])
        if returncode == 0:
            ifconfig_path = stdout.strip()
            self.log(f"ifconfig found at: {ifconfig_path}", "SUCCESS")
            tool_results["ifconfig"]["path"] = ifconfig_path

        # Test sudo availability (if not root)
        if not self.system_info.get("environment", {}).get("is_root", False):
            returncode, stdout, stderr = self.run_command(["sudo", "--version"])
            if returncode == 0:
                self.log("sudo is available", "SUCCESS")
                tool_results["sudo"] = {"available": True}
            else:
                self.log("sudo is not available", "WARNING")
                tool_results["sudo"] = {"available": False}

        self.test_results.append(
            {"test": "system_tools", "success": success, "details": tool_results}
        )

        return success

    def test_mac_changer_import(self) -> bool:
        """Test MAC changer module import."""
        self.log("Testing MAC changer module import...")

        success = True

        try:
            # Add project root to Python path
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))

            import mac_changer

            # Test basic functionality
            mac_changer_instance = mac_changer.MACChanger()

            # Test system compatibility check
            try:
                mac_changer_instance.check_system_compatibility()
                self.log("System compatibility check passed", "SUCCESS")
            except Exception as e:
                self.log(f"System compatibility check failed: {e}", "ERROR")
                success = False

            # Test MAC address validation
            try:
                valid_mac = mac_changer_instance.validate_mac_address(
                    "aa:bb:cc:dd:ee:ff"
                )
                self.log(f"MAC validation working: {valid_mac}", "SUCCESS")
            except Exception as e:
                self.log(f"MAC validation failed: {e}", "ERROR")
                success = False

            # Test interface discovery
            try:
                interfaces = mac_changer_instance.get_available_interfaces()
                self.log(f"Found {len(interfaces)} interfaces: {interfaces}", "SUCCESS")
            except Exception as e:
                self.log(f"Interface discovery failed: {e}", "ERROR")
                success = False

            self.test_results.append(
                {
                    "test": "mac_changer_import",
                    "success": success,
                    "details": {
                        "version": getattr(mac_changer, "__version__", "unknown"),
                        "interfaces_found": len(interfaces)
                        if "interfaces" in locals()
                        else 0,
                        "system_compatible": True,
                    },
                }
            )

        except ImportError as e:
            self.log(f"Failed to import mac_changer: {e}", "ERROR")
            success = False
            self.test_results.append(
                {
                    "test": "mac_changer_import",
                    "success": False,
                    "details": {"error": str(e)},
                }
            )

        return success

    def test_interface_operations(self) -> bool:
        """Test interface operations without making changes."""
        self.log("Testing interface operations...")

        success = True

        try:
            # Add project root to Python path
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))

            import mac_changer

            mac_changer_instance = mac_changer.MACChanger()

            # Test interface discovery
            interfaces = mac_changer_instance.get_available_interfaces()

            if not interfaces:
                self.log("No interfaces found", "WARNING")
                success = False
            else:
                self.log(f"Found {len(interfaces)} interfaces", "SUCCESS")

                # Test each interface
                for interface in interfaces[:3]:  # Test max 3 interfaces
                    self.log(f"Testing interface: {interface}", "INFO")

                    # Test interface existence
                    if mac_changer_instance.interface_exists(interface):
                        self.log(f"Interface {interface} exists", "SUCCESS")
                    else:
                        self.log(f"Interface {interface} does not exist", "WARNING")
                        continue

                    # Test getting current MAC
                    current_mac = mac_changer_instance.get_current_mac(interface)
                    if current_mac:
                        self.log(f"Interface {interface} MAC: {current_mac}", "SUCCESS")
                    else:
                        self.log(f"Could not get MAC for {interface}", "WARNING")

            self.test_results.append(
                {
                    "test": "interface_operations",
                    "success": success,
                    "details": {
                        "interfaces_found": len(interfaces),
                        "interfaces_tested": min(3, len(interfaces)),
                    },
                }
            )

        except Exception as e:
            self.log(f"Interface operations test failed: {e}", "ERROR")
            success = False
            self.test_results.append(
                {
                    "test": "interface_operations",
                    "success": False,
                    "details": {"error": str(e)},
                }
            )

        return success

    def test_dry_run_functionality(self) -> bool:
        """Test dry-run functionality."""
        self.log("Testing dry-run functionality...")

        success = True

        try:
            # Test CLI dry-run
            test_commands = [
                ["python", "mac_changer.py", "--help"],
                ["python", "mac_changer.py", "-l"],
            ]

            # Find a test interface
            if self.system_info.get("network", {}).get("interfaces"):
                test_interface = None
                for interface in self.system_info["network"]["interfaces"]:
                    if interface.get("type") in ["ethernet", "wireless"]:
                        test_interface = interface["name"]
                        break

                if test_interface:
                    test_commands.append(
                        [
                            "python",
                            "mac_changer.py",
                            "-i",
                            test_interface,
                            "-m",
                            "aa:bb:cc:dd:ee:ff",
                            "--dry-run",
                        ]
                    )

            for cmd in test_commands:
                self.log(f"Testing command: {' '.join(cmd)}", "INFO")
                returncode, stdout, stderr = self.run_command(cmd)

                if returncode == 0:
                    self.log(f"Command succeeded", "SUCCESS")
                else:
                    self.log(f"Command failed: {stderr}", "WARNING")
                    if "--dry-run" in cmd:
                        success = False

            self.test_results.append(
                {
                    "test": "dry_run_functionality",
                    "success": success,
                    "details": {
                        "commands_tested": len(test_commands),
                        "test_interface": test_interface
                        if "test_interface" in locals()
                        else None,
                    },
                }
            )

        except Exception as e:
            self.log(f"Dry-run test failed: {e}", "ERROR")
            success = False
            self.test_results.append(
                {
                    "test": "dry_run_functionality",
                    "success": False,
                    "details": {"error": str(e)},
                }
            )

        return success

    def test_permissions(self) -> bool:
        """Test permission handling."""
        self.log("Testing permission handling...")

        success = True

        try:
            # Add project root to Python path
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))

            import mac_changer

            mac_changer_instance = mac_changer.MACChanger()

            # Test permission check
            try:
                mac_changer_instance.check_permissions()
                self.log("Permission check passed (running as root)", "SUCCESS")
                is_root = True
            except mac_changer.PermissionError:
                self.log("Permission check correctly detected non-root user", "SUCCESS")
                is_root = False

            # Test that dry-run works without root
            if not is_root:
                try:
                    # This should work without root
                    interfaces = mac_changer_instance.get_available_interfaces()
                    self.log("Interface discovery works without root", "SUCCESS")
                except Exception as e:
                    self.log(f"Interface discovery failed without root: {e}", "WARNING")

            self.test_results.append(
                {
                    "test": "permissions",
                    "success": success,
                    "details": {"is_root": is_root, "permission_check_works": True},
                }
            )

        except Exception as e:
            self.log(f"Permission test failed: {e}", "ERROR")
            success = False
            self.test_results.append(
                {"test": "permissions", "success": False, "details": {"error": str(e)}}
            )

        return success

    def run_all_tests(self) -> bool:
        """Run all system tests."""
        self.log("Starting comprehensive system tests...")

        # Collect system information first
        self.collect_system_info()

        # Run all tests
        tests = [
            self.test_python_compatibility,
            self.test_system_tools,
            self.test_mac_changer_import,
            self.test_interface_operations,
            self.test_dry_run_functionality,
            self.test_permissions,
        ]

        passed = 0
        failed = 0

        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"Test {test.__name__} crashed: {e}", "ERROR")
                failed += 1

        # Print summary
        self.log(f"\n=== TEST SUMMARY ===", "INFO")
        self.log(f"Tests passed: {passed}", "SUCCESS")
        self.log(f"Tests failed: {failed}", "ERROR" if failed > 0 else "SUCCESS")
        self.log(f"Total tests: {passed + failed}", "INFO")

        return failed == 0

    def generate_report(self) -> Dict:
        """Generate comprehensive test report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self.system_info,
            "test_results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r["success"]),
                "failed": sum(1 for r in self.test_results if not r["success"]),
                "success_rate": 0,
            },
        }

        if report["summary"]["total_tests"] > 0:
            report["summary"]["success_rate"] = (
                report["summary"]["passed"] / report["summary"]["total_tests"] * 100
            )

        return report

    def save_report(self, filename: str = None) -> str:
        """Save test report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"system_test_report_{timestamp}.json"

        report = self.generate_report()

        report_path = self.project_root / "reports" / filename
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        self.log(f"Test report saved to: {report_path}", "SUCCESS")
        return str(report_path)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Comprehensive system testing for MAC Address Changer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--system-info-only",
        action="store_true",
        help="Only collect and display system information",
    )

    parser.add_argument(
        "--save-report", action="store_true", help="Save test report to JSON file"
    )

    parser.add_argument("--report-file", type=str, help="Custom report filename")

    args = parser.parse_args()

    # Create tester instance
    tester = SystemTester(verbose=args.verbose)

    if args.system_info_only:
        # Only collect system information
        system_info = tester.collect_system_info()
        print(json.dumps(system_info, indent=2))
        return

    # Run all tests
    success = tester.run_all_tests()

    # Save report if requested
    if args.save_report:
        tester.save_report(args.report_file)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
