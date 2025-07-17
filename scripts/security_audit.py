#!/usr/bin/env python3
"""Comprehensive Security Audit Script for MAC Address Changer.

This script performs a thorough security audit of the MAC Address Changer project,
checking for vulnerabilities, security best practices, and potential attack vectors.

Features:
- Code security scanning
- Dependency vulnerability checking
- Permission and privilege analysis
- Input validation testing
- Attack vector simulation
- Security compliance checking
- Hardening recommendations

Usage:
    python scripts/security_audit.py
    python scripts/security_audit.py --verbose
    python scripts/security_audit.py --report security_report.json
"""

import argparse
import ast
import json
import os
import platform
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import tempfile
import shutil


class SecurityAuditError(Exception):
    """Custom exception for security audit operations."""

    pass


class SecurityAuditor:
    """Comprehensive security auditor for MAC Address Changer."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.project_root = Path(__file__).parent.parent
        self.audit_results = []
        self.security_issues = []
        self.recommendations = []

        # Security patterns to check
        self.security_patterns = {
            "command_injection": [
                r"subprocess\.call\([^)]*shell\s*=\s*True",
                r"os\.system\(",
                r"subprocess\.run\([^)]*shell\s*=\s*True",
                r"subprocess\.Popen\([^)]*shell\s*=\s*True",
                r"eval\(",
                r"exec\(",
            ],
            "hardcoded_secrets": [
                r"password\s*=\s*['\"][^'\"]+['\"]",
                r"secret\s*=\s*['\"][^'\"]+['\"]",
                r"api_key\s*=\s*['\"][^'\"]+['\"]",
                r"token\s*=\s*['\"][^'\"]+['\"]",
                r"key\s*=\s*['\"][^'\"]+['\"]",
            ],
            "path_traversal": [
                r"\.\.\/",
                r"\.\.\\",
                r"os\.path\.join\([^)]*\.\.\/?",
            ],
            "unsafe_file_operations": [
                r"open\([^)]*mode\s*=\s*['\"]w['\"]",
                r"pickle\.loads?\(",
                r"yaml\.load\(",
                r"subprocess\.call\([^)]*executable\s*=",
            ],
            "network_vulnerabilities": [
                r"ssl\.[^(]*CERT_NONE",
                r"ssl\.[^(]*verify\s*=\s*False",
                r"requests\.[^(]*verify\s*=\s*False",
            ],
            "logging_vulnerabilities": [
                r"logging\.[^(]*\([^)]*\%[^)]*\)",
                r"print\([^)]*\%[^)]*\)",
            ],
        }

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
        elif level == "SECURITY":
            print(f"\033[95m{prefix} {message}\033[0m")
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

    def scan_code_for_vulnerabilities(self) -> Dict[str, List[Dict]]:
        """Scan code files for security vulnerabilities."""
        self.log("Scanning code for security vulnerabilities...")

        vulnerabilities = {pattern: [] for pattern in self.security_patterns.keys()}

        # Get all Python files
        python_files = list(self.project_root.glob("*.py"))
        python_files.extend(self.project_root.glob("scripts/*.py"))

        for file_path in python_files:
            if file_path.name.startswith("."):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check each security pattern
                for pattern_name, patterns in self.security_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.MULTILINE)
                        for match in matches:
                            # Find line number
                            line_num = content[: match.start()].count("\n") + 1

                            vulnerability = {
                                "file": str(file_path.relative_to(self.project_root)),
                                "line": line_num,
                                "pattern": pattern,
                                "match": match.group(0),
                                "severity": self._get_severity(pattern_name),
                                "description": self._get_vulnerability_description(
                                    pattern_name
                                ),
                            }
                            vulnerabilities[pattern_name].append(vulnerability)

            except Exception as e:
                self.log(f"Error scanning {file_path}: {e}", "ERROR")

        return vulnerabilities

    def _get_severity(self, pattern_name: str) -> str:
        """Get severity level for vulnerability pattern."""
        severity_map = {
            "command_injection": "CRITICAL",
            "hardcoded_secrets": "HIGH",
            "path_traversal": "HIGH",
            "unsafe_file_operations": "MEDIUM",
            "network_vulnerabilities": "MEDIUM",
            "logging_vulnerabilities": "LOW",
        }
        return severity_map.get(pattern_name, "MEDIUM")

    def _get_vulnerability_description(self, pattern_name: str) -> str:
        """Get description for vulnerability pattern."""
        descriptions = {
            "command_injection": "Potential command injection vulnerability",
            "hardcoded_secrets": "Hardcoded secret or credential found",
            "path_traversal": "Potential path traversal vulnerability",
            "unsafe_file_operations": "Unsafe file operation detected",
            "network_vulnerabilities": "Insecure network configuration",
            "logging_vulnerabilities": "Potential logging injection",
        }
        return descriptions.get(pattern_name, "Security vulnerability detected")

    def check_dependencies(self) -> Dict[str, Any]:
        """Check for vulnerable dependencies."""
        self.log("Checking dependencies for vulnerabilities...")

        results = {
            "safety_scan": None,
            "outdated_packages": [],
            "security_advisories": [],
        }

        # Run safety check if available
        returncode, stdout, stderr = self.run_command(["safety", "check", "--json"])
        if returncode == 0:
            try:
                safety_results = json.loads(stdout)
                results["safety_scan"] = safety_results
                if safety_results:
                    self.log(
                        f"Found {len(safety_results)} security vulnerabilities in dependencies",
                        "SECURITY",
                    )
                else:
                    self.log("No dependency vulnerabilities found", "SUCCESS")
            except json.JSONDecodeError:
                self.log("Safety check output is not valid JSON", "WARNING")
        else:
            self.log("Safety check not available or failed", "WARNING")

        # Check for outdated packages
        returncode, stdout, stderr = self.run_command(
            ["pip", "list", "--outdated", "--format=json"]
        )
        if returncode == 0:
            try:
                outdated = json.loads(stdout)
                results["outdated_packages"] = outdated
                if outdated:
                    self.log(f"Found {len(outdated)} outdated packages", "WARNING")
            except json.JSONDecodeError:
                pass

        return results

    def analyze_permissions(self) -> Dict[str, Any]:
        """Analyze file permissions and privilege requirements."""
        self.log("Analyzing permissions and privileges...")

        results = {
            "file_permissions": {},
            "executable_files": [],
            "world_writable": [],
            "suid_sgid": [],
            "requires_root": False,
        }

        # Check file permissions
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    mode = oct(stat.st_mode)[-3:]

                    results["file_permissions"][
                        str(file_path.relative_to(self.project_root))
                    ] = {
                        "mode": mode,
                        "owner": stat.st_uid,
                        "group": stat.st_gid,
                        "size": stat.st_size,
                    }

                    # Check for executable files
                    if stat.st_mode & 0o111:
                        results["executable_files"].append(
                            str(file_path.relative_to(self.project_root))
                        )

                    # Check for world-writable files
                    if stat.st_mode & 0o002:
                        results["world_writable"].append(
                            str(file_path.relative_to(self.project_root))
                        )
                        self.log(f"World-writable file found: {file_path}", "WARNING")

                    # Check for SUID/SGID
                    if stat.st_mode & (0o4000 | 0o2000):
                        results["suid_sgid"].append(
                            str(file_path.relative_to(self.project_root))
                        )
                        self.log(f"SUID/SGID file found: {file_path}", "SECURITY")

                except Exception as e:
                    self.log(
                        f"Error checking permissions for {file_path}: {e}", "ERROR"
                    )

        # Check if root privileges are required
        results["requires_root"] = self._check_root_requirement()

        return results

    def _check_root_requirement(self) -> bool:
        """Check if the application requires root privileges."""
        # Look for privilege checking code
        try:
            with open(self.project_root / "mac_changer.py", "r") as f:
                content = f.read()
                if "geteuid" in content or "check_permissions" in content:
                    return True
        except:
            pass
        return False

    def test_input_validation(self) -> Dict[str, Any]:
        """Test input validation mechanisms."""
        self.log("Testing input validation...")

        results = {
            "mac_validation": {},
            "interface_validation": {},
            "command_injection_tests": [],
            "path_traversal_tests": [],
        }

        # Test MAC address validation
        test_macs = [
            "aa:bb:cc:dd:ee:ff",  # Valid
            "AA:BB:CC:DD:EE:FF",  # Valid uppercase
            "aa-bb-cc-dd-ee-ff",  # Valid dash format
            "invalid",  # Invalid
            "",  # Empty
            "aa:bb:cc:dd:ee:fg",  # Invalid character
            "../etc/passwd",  # Path traversal
            "; rm -rf /",  # Command injection
            'aa:bb:cc:dd:ee:ff; echo "pwned"',  # Command injection
        ]

        for test_mac in test_macs:
            results["mac_validation"][test_mac] = self._test_mac_validation(test_mac)

        # Test interface validation
        test_interfaces = [
            "eth0",  # Valid
            "wlan0",  # Valid
            "invalid_interface",  # Invalid
            "",  # Empty
            "../etc/passwd",  # Path traversal
            "; rm -rf /",  # Command injection
            'eth0; echo "pwned"',  # Command injection
        ]

        for test_interface in test_interfaces:
            results["interface_validation"][test_interface] = (
                self._test_interface_validation(test_interface)
            )

        return results

    def _test_mac_validation(self, mac_address: str) -> Dict[str, Any]:
        """Test MAC address validation."""
        try:
            # Add project root to Python path
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))

            import mac_changer

            mac_changer_instance = mac_changer.MACChanger()

            try:
                result = mac_changer_instance.validate_mac_address(mac_address)
                return {
                    "valid": True,
                    "result": result,
                    "error": None,
                    "potential_vulnerability": self._check_potential_vulnerability(
                        mac_address
                    ),
                }
            except Exception as e:
                return {
                    "valid": False,
                    "result": None,
                    "error": str(e),
                    "potential_vulnerability": self._check_potential_vulnerability(
                        mac_address
                    ),
                }
        except Exception as e:
            return {
                "valid": False,
                "result": None,
                "error": f"Import error: {e}",
                "potential_vulnerability": False,
            }

    def _test_interface_validation(self, interface: str) -> Dict[str, Any]:
        """Test interface validation."""
        try:
            # Add project root to Python path
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))

            import mac_changer

            mac_changer_instance = mac_changer.MACChanger()

            try:
                result = mac_changer_instance.validate_interface(interface)
                return {
                    "valid": True,
                    "result": result,
                    "error": None,
                    "potential_vulnerability": self._check_potential_vulnerability(
                        interface
                    ),
                }
            except Exception as e:
                return {
                    "valid": False,
                    "result": None,
                    "error": str(e),
                    "potential_vulnerability": self._check_potential_vulnerability(
                        interface
                    ),
                }
        except Exception as e:
            return {
                "valid": False,
                "result": None,
                "error": f"Import error: {e}",
                "potential_vulnerability": False,
            }

    def _check_potential_vulnerability(self, input_string: str) -> bool:
        """Check if input string contains potential attack vectors."""
        attack_patterns = [
            r"[;&|`$]",  # Command injection
            r"\.\.\/|\.\.\\",  # Path traversal
            r"<script|javascript:",  # XSS
            r"union\s+select|drop\s+table",  # SQL injection
            r"eval\(|exec\(",  # Code injection
        ]

        for pattern in attack_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                return True

        return False

    def check_subprocess_usage(self) -> Dict[str, Any]:
        """Check subprocess usage for security issues."""
        self.log("Checking subprocess usage...")

        results = {
            "subprocess_calls": [],
            "shell_usage": [],
            "command_construction": [],
        }

        # Analyze subprocess usage in code
        python_files = list(self.project_root.glob("*.py"))
        python_files.extend(self.project_root.glob("scripts/*.py"))

        for file_path in python_files:
            if file_path.name.startswith("."):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse AST to find subprocess calls
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            if (
                                isinstance(node.func.value, ast.Name)
                                and node.func.value.id == "subprocess"
                            ):
                                call_info = {
                                    "file": str(
                                        file_path.relative_to(self.project_root)
                                    ),
                                    "line": node.lineno,
                                    "function": node.func.attr,
                                    "shell_usage": self._check_shell_usage(node),
                                    "command_construction": self._analyze_command_construction(
                                        node
                                    ),
                                }

                                results["subprocess_calls"].append(call_info)

                                if call_info["shell_usage"]:
                                    results["shell_usage"].append(call_info)
                                    self.log(
                                        f"Shell usage found in {file_path}:{node.lineno}",
                                        "WARNING",
                                    )

            except Exception as e:
                self.log(f"Error analyzing {file_path}: {e}", "ERROR")

        return results

    def _check_shell_usage(self, node: ast.Call) -> bool:
        """Check if subprocess call uses shell=True."""
        for keyword in node.keywords:
            if keyword.arg == "shell":
                if (
                    isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                ):
                    return True
        return False

    def _analyze_command_construction(self, node: ast.Call) -> Dict[str, Any]:
        """Analyze how commands are constructed."""
        if not node.args:
            return {"safe": True, "issues": []}

        first_arg = node.args[0]
        issues = []

        # Check if command is constructed with user input
        if isinstance(first_arg, ast.BinOp):
            issues.append("Command constructed with string concatenation")
        elif isinstance(first_arg, ast.JoinedStr):
            issues.append("Command constructed with f-string")
        elif isinstance(first_arg, ast.Call):
            if (
                isinstance(first_arg.func, ast.Attribute)
                and first_arg.func.attr == "format"
            ):
                issues.append("Command constructed with .format()")

        return {
            "safe": len(issues) == 0,
            "issues": issues,
        }

    def check_error_handling(self) -> Dict[str, Any]:
        """Check error handling for information disclosure."""
        self.log("Checking error handling...")

        results = {
            "exception_handling": [],
            "information_disclosure": [],
            "logging_issues": [],
        }

        python_files = list(self.project_root.glob("*.py"))
        python_files.extend(self.project_root.glob("scripts/*.py"))

        for file_path in python_files:
            if file_path.name.startswith("."):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for broad exception catching
                if re.search(r"except\s*:", content):
                    results["exception_handling"].append(
                        {
                            "file": str(file_path.relative_to(self.project_root)),
                            "issue": "Broad exception handling found",
                            "risk": "May hide security issues",
                        }
                    )

                # Check for exception information disclosure
                if re.search(
                    r"print\([^)]*\bexception\b|\bstr\(e\)", content, re.IGNORECASE
                ):
                    results["information_disclosure"].append(
                        {
                            "file": str(file_path.relative_to(self.project_root)),
                            "issue": "Exception details may be disclosed",
                            "risk": "Information disclosure",
                        }
                    )

                # Check for logging sensitive information
                if re.search(
                    r"log[^(]*\([^)]*password|secret|key", content, re.IGNORECASE
                ):
                    results["logging_issues"].append(
                        {
                            "file": str(file_path.relative_to(self.project_root)),
                            "issue": "Potential sensitive information logging",
                            "risk": "Information disclosure",
                        }
                    )

            except Exception as e:
                self.log(f"Error analyzing {file_path}: {e}", "ERROR")

        return results

    def check_file_operations(self) -> Dict[str, Any]:
        """Check file operations for security issues."""
        self.log("Checking file operations...")

        results = {
            "file_operations": [],
            "temp_file_usage": [],
            "path_validation": [],
        }

        python_files = list(self.project_root.glob("*.py"))
        python_files.extend(self.project_root.glob("scripts/*.py"))

        for file_path in python_files:
            if file_path.name.startswith("."):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for file operations
                file_ops = re.findall(r"open\([^)]+\)", content)
                for op in file_ops:
                    results["file_operations"].append(
                        {
                            "file": str(file_path.relative_to(self.project_root)),
                            "operation": op,
                            "potential_issue": "File operation without path validation",
                        }
                    )

                # Check for temporary file usage
                if "tempfile" in content:
                    results["temp_file_usage"].append(
                        {
                            "file": str(file_path.relative_to(self.project_root)),
                            "usage": "Temporary file usage detected",
                            "risk": "Potential race condition or cleanup issues",
                        }
                    )

                # Check for path validation
                if re.search(r"\.\.\/|\.\.\\", content):
                    results["path_validation"].append(
                        {
                            "file": str(file_path.relative_to(self.project_root)),
                            "issue": "Path traversal patterns found",
                            "risk": "Path traversal vulnerability",
                        }
                    )

            except Exception as e:
                self.log(f"Error analyzing {file_path}: {e}", "ERROR")

        return results

    def generate_security_recommendations(
        self, audit_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate security recommendations based on audit results."""
        recommendations = []

        # Check code vulnerabilities
        if audit_results.get("code_vulnerabilities"):
            for vuln_type, vulns in audit_results["code_vulnerabilities"].items():
                if vulns:
                    recommendations.append(
                        {
                            "category": "Code Security",
                            "priority": "HIGH",
                            "issue": f"{vuln_type.replace('_', ' ').title()} vulnerabilities found",
                            "count": len(vulns),
                            "recommendation": self._get_vulnerability_recommendation(
                                vuln_type
                            ),
                        }
                    )

        # Check dependency vulnerabilities
        if audit_results.get("dependencies", {}).get("safety_scan"):
            safety_results = audit_results["dependencies"]["safety_scan"]
            if safety_results:
                recommendations.append(
                    {
                        "category": "Dependencies",
                        "priority": "HIGH",
                        "issue": "Vulnerable dependencies found",
                        "count": len(safety_results),
                        "recommendation": "Update vulnerable dependencies immediately",
                    }
                )

        # Check permissions
        if audit_results.get("permissions", {}).get("world_writable"):
            world_writable = audit_results["permissions"]["world_writable"]
            if world_writable:
                recommendations.append(
                    {
                        "category": "File Permissions",
                        "priority": "MEDIUM",
                        "issue": "World-writable files found",
                        "count": len(world_writable),
                        "recommendation": "Restrict file permissions to prevent unauthorized access",
                    }
                )

        # Check subprocess usage
        if audit_results.get("subprocess_usage", {}).get("shell_usage"):
            shell_usage = audit_results["subprocess_usage"]["shell_usage"]
            if shell_usage:
                recommendations.append(
                    {
                        "category": "Subprocess Security",
                        "priority": "HIGH",
                        "issue": "Shell usage in subprocess calls",
                        "count": len(shell_usage),
                        "recommendation": "Avoid shell=True in subprocess calls, use argument lists instead",
                    }
                )

        # General security recommendations
        recommendations.extend(
            [
                {
                    "category": "Input Validation",
                    "priority": "HIGH",
                    "issue": "Ensure comprehensive input validation",
                    "recommendation": "Implement strict input validation for all user inputs",
                },
                {
                    "category": "Error Handling",
                    "priority": "MEDIUM",
                    "issue": "Secure error handling",
                    "recommendation": "Avoid disclosing sensitive information in error messages",
                },
                {
                    "category": "Logging",
                    "priority": "MEDIUM",
                    "issue": "Secure logging practices",
                    "recommendation": "Implement secure logging without sensitive information",
                },
                {
                    "category": "Authentication",
                    "priority": "HIGH",
                    "issue": "Privilege checking",
                    "recommendation": "Ensure proper privilege checking for administrative operations",
                },
            ]
        )

        return recommendations

    def _get_vulnerability_recommendation(self, vuln_type: str) -> str:
        """Get recommendation for specific vulnerability type."""
        recommendations = {
            "command_injection": "Avoid shell=True in subprocess calls, use argument lists and proper escaping",
            "hardcoded_secrets": "Move secrets to environment variables or secure configuration files",
            "path_traversal": "Validate and sanitize file paths, use Path.resolve() for normalization",
            "unsafe_file_operations": "Validate file operations and use secure file handling practices",
            "network_vulnerabilities": "Use proper SSL/TLS verification and secure network configurations",
            "logging_vulnerabilities": "Avoid user input in logging format strings, use proper logging practices",
        }
        return recommendations.get(vuln_type, "Review and fix security vulnerability")

    def run_security_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit."""
        self.log("Starting comprehensive security audit...")

        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "platform": platform.system(),
                "python_version": sys.version,
                "hostname": platform.node(),
            },
            "code_vulnerabilities": {},
            "dependencies": {},
            "permissions": {},
            "input_validation": {},
            "subprocess_usage": {},
            "error_handling": {},
            "file_operations": {},
            "recommendations": [],
        }

        try:
            # Run all security checks
            audit_results["code_vulnerabilities"] = self.scan_code_for_vulnerabilities()
            audit_results["dependencies"] = self.check_dependencies()
            audit_results["permissions"] = self.analyze_permissions()
            audit_results["input_validation"] = self.test_input_validation()
            audit_results["subprocess_usage"] = self.check_subprocess_usage()
            audit_results["error_handling"] = self.check_error_handling()
            audit_results["file_operations"] = self.check_file_operations()

            # Generate recommendations
            audit_results["recommendations"] = self.generate_security_recommendations(
                audit_results
            )

            # Calculate security score
            audit_results["security_score"] = self.calculate_security_score(
                audit_results
            )

            self.log("Security audit completed", "SUCCESS")

        except Exception as e:
            self.log(f"Security audit failed: {e}", "ERROR")
            audit_results["error"] = str(e)

        return audit_results

    def calculate_security_score(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall security score."""
        total_issues = 0
        critical_issues = 0
        high_issues = 0
        medium_issues = 0
        low_issues = 0

        # Count code vulnerabilities
        for vuln_type, vulns in audit_results.get("code_vulnerabilities", {}).items():
            for vuln in vulns:
                total_issues += 1
                severity = vuln.get("severity", "MEDIUM")
                if severity == "CRITICAL":
                    critical_issues += 1
                elif severity == "HIGH":
                    high_issues += 1
                elif severity == "MEDIUM":
                    medium_issues += 1
                else:
                    low_issues += 1

        # Count dependency vulnerabilities
        safety_results = audit_results.get("dependencies", {}).get("safety_scan", [])
        if safety_results:
            for vuln in safety_results:
                total_issues += 1
                high_issues += 1  # Consider all dependency vulnerabilities as high

        # Calculate score (0-100)
        score = 100
        score -= critical_issues * 25
        score -= high_issues * 15
        score -= medium_issues * 10
        score -= low_issues * 5

        score = max(0, score)  # Ensure score doesn't go below 0

        return {
            "score": score,
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "low_issues": low_issues,
            "grade": self._get_security_grade(score),
        }

    def _get_security_grade(self, score: int) -> str:
        """Get security grade based on score."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def save_audit_report(
        self, audit_results: Dict[str, Any], filename: str = None
    ) -> str:
        """Save audit report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"security_audit_{timestamp}.json"

        report_path = self.project_root / "reports" / filename
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(audit_results, f, indent=2)

        self.log(f"Security audit report saved to: {report_path}", "SUCCESS")
        return str(report_path)

    def print_audit_summary(self, audit_results: Dict[str, Any]) -> None:
        """Print audit summary."""
        print("\n" + "=" * 60)
        print("SECURITY AUDIT SUMMARY")
        print("=" * 60)

        # Security score
        score_info = audit_results.get("security_score", {})
        score = score_info.get("score", 0)
        grade = score_info.get("grade", "F")

        print(f"Security Score: {score}/100 (Grade: {grade})")
        print(f"Total Issues: {score_info.get('total_issues', 0)}")
        print(f"  Critical: {score_info.get('critical_issues', 0)}")
        print(f"  High: {score_info.get('high_issues', 0)}")
        print(f"  Medium: {score_info.get('medium_issues', 0)}")
        print(f"  Low: {score_info.get('low_issues', 0)}")

        # Top recommendations
        recommendations = audit_results.get("recommendations", [])
        if recommendations:
            print("\nTop Security Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"{i}. [{rec['priority']}] {rec['issue']}")
                print(f"   {rec['recommendation']}")

        print("\n" + "=" * 60)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Security Audit for MAC Address Changer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--report", "-r", type=str, help="Save audit report to specified file"
    )

    parser.add_argument(
        "--summary-only", action="store_true", help="Only show audit summary"
    )

    args = parser.parse_args()

    # Create security auditor
    auditor = SecurityAuditor(verbose=args.verbose)

    # Run security audit
    audit_results = auditor.run_security_audit()

    # Save report if requested
    if args.report:
        auditor.save_audit_report(audit_results, args.report)

    # Print summary
    auditor.print_audit_summary(audit_results)

    # Print full results if not summary-only
    if not args.summary_only and args.verbose:
        print("\nFull audit results:")
        print(json.dumps(audit_results, indent=2))

    # Exit with appropriate code based on security score
    score = audit_results.get("security_score", {}).get("score", 0)
    if score < 70:
        sys.exit(1)  # Fail if security score is too low
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
