#!/usr/bin/env python3
"""Improved MAC address changer with enhanced error handling and security.

This tool provides a secure and robust way to change MAC addresses on network
interfaces using ifconfig. Includes comprehensive validation, error handling,
and security checks.

Author: Thomas Juul Dyhr <thomas@dyhr.com>
Version: 2.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Thomas Juul Dyhr"
__email__ = "thomas@dyhr.com"
__license__ = "MIT"

import argparse
import logging
import os
import platform
import re
import subprocess
import sys
from typing import Optional, List


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MACChangerError(Exception):
    """Custom exception for MAC changer operations.

    Attributes:
        message: Error message describing what went wrong
        error_code: Optional error code for programmatic handling
    """

    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class PermissionError(MACChangerError):
    """Raised when insufficient permissions are detected.

    This exception is raised when the user attempts to perform
    operations that require elevated privileges without having them.
    """

    def __init__(self, message: str = "Insufficient privileges for this operation"):
        super().__init__(message, "PERMISSION_DENIED")


class InterfaceError(MACChangerError):
    """Raised when interface-related errors occur.

    This includes cases where the specified network interface
    doesn't exist, is invalid, or cannot be accessed.
    """

    def __init__(self, message: str, interface_name: Optional[str] = None):
        self.interface_name = interface_name
        super().__init__(message, "INTERFACE_ERROR")


class MACChanger:
    """Main MAC address changer class."""

    def __init__(self):
        self.supported_platforms = ["linux", "darwin"]  # darwin = macOS
        self.mac_regex = re.compile(r"^([0-9a-f]{2}[:-]){5}[0-9a-f]{2}$", re.IGNORECASE)
        self.interface_regex = re.compile(
            r"^(eth[0-9]+|wlan[0-9]+|en[a-z]?[0-9]+|wl[a-z]?[0-9]+|lo[0-9]*|[a-z]{2,4}[0-9]+([a-z][0-9]+)?)$",
            re.IGNORECASE,
        )

    def check_system_compatibility(self) -> None:
        """Check if the current system is supported."""
        current_platform = platform.system().lower()

        if current_platform not in self.supported_platforms:
            raise MACChangerError(
                f"Unsupported platform: {platform.system()}. "
                f"Supported platforms: {', '.join(self.supported_platforms)}"
            )

        # Check if ifconfig is available
        try:
            result = subprocess.run(
                ["which", "ifconfig"], capture_output=True, check=False
            )
            if result.returncode != 0:
                raise MACChangerError(
                    "ifconfig command not found. Please install net-tools package."
                )
        except FileNotFoundError:
            raise MACChangerError("System commands not available.")

        logger.info(f"System compatibility check passed: {platform.system()}")

    def check_permissions(self) -> None:
        """Check if running with sufficient privileges."""
        if os.geteuid() != 0:
            raise PermissionError(
                "Root privileges required to change MAC addresses. "
                "Please run with sudo."
            )
        logger.info("Permission check passed: running with root privileges")

    def validate_interface(self, interface: str) -> str:
        """Validate network interface name."""
        if not interface:
            raise argparse.ArgumentTypeError("Interface name cannot be empty")

        if not self.interface_regex.match(interface):
            raise argparse.ArgumentTypeError(
                f"Invalid interface name: '{interface}'. "
                f"Expected format: eth0, wlan0, etc."
            )

        # Check if interface exists
        if not self.interface_exists(interface):
            raise InterfaceError(
                f"Network interface '{interface}' not found", interface_name=interface
            )

        return interface

    def validate_mac_address(self, mac_addr: str) -> str:
        """Validate MAC address format."""
        if not mac_addr:
            raise argparse.ArgumentTypeError("MAC address cannot be empty")

        # Normalize MAC address (convert to lowercase, use colons)
        normalized_mac = mac_addr.lower().replace("-", ":")

        if not self.mac_regex.match(normalized_mac):
            raise argparse.ArgumentTypeError(
                f"Invalid MAC address: '{mac_addr}'. "
                f"Expected format: aa:bb:cc:dd:ee:ff or aa-bb-cc-dd-ee-ff"
            )

        return normalized_mac

    def interface_exists(self, interface: str) -> bool:
        """Check if network interface exists."""
        try:
            result = subprocess.run(
                ["ifconfig", interface], capture_output=True, check=False, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_available_interfaces(self) -> List[str]:
        """Get list of available network interfaces."""
        try:
            result = subprocess.run(
                ["ifconfig", "-a"],
                capture_output=True,
                check=True,
                text=True,
                timeout=10,
            )

            interfaces = []
            for line in result.stdout.split("\n"):
                if line and not line.startswith(" ") and not line.startswith("\t"):
                    # Extract interface name (first word before colon)
                    interface_name = line.split(":")[0].split()[0]
                    if self.interface_regex.match(interface_name):
                        interfaces.append(interface_name)

            return sorted(set(interfaces))
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            logger.warning("Could not retrieve interface list")
            return []

    def get_current_mac(self, interface: str) -> Optional[str]:
        """Get current MAC address of the specified interface."""
        try:
            result = subprocess.run(
                ["ifconfig", interface],
                capture_output=True,
                check=True,
                text=True,
                timeout=5,
            )

            # Search for MAC address pattern in output
            mac_match = re.search(
                r"([0-9a-f]{2}[:-]){5}[0-9a-f]{2}", result.stdout, re.IGNORECASE
            )

            if mac_match:
                return mac_match.group(0).lower()
            else:
                logger.error(f"Could not find MAC address for interface {interface}")
                return None

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get MAC address for {interface}: {e}")
            return None
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while getting MAC address for {interface}")
            return None

    def change_mac_address(self, interface: str, new_mac: str) -> bool:
        """Change MAC address of the specified interface."""
        try:
            logger.info(f"Changing MAC address for {interface} to {new_mac}")

            # Bring interface down
            subprocess.run(["ifconfig", interface, "down"], check=True, timeout=10)
            logger.debug(f"Interface {interface} brought down")

            # Change MAC address
            subprocess.run(
                ["ifconfig", interface, "hw", "ether", new_mac], check=True, timeout=10
            )
            logger.debug(f"MAC address changed to {new_mac}")

            # Bring interface up
            subprocess.run(["ifconfig", interface, "up"], check=True, timeout=10)
            logger.debug(f"Interface {interface} brought up")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to change MAC address: {e}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("Timeout during MAC address change operation")
            return False

    def verify_mac_change(self, interface: str, expected_mac: str) -> bool:
        """Verify that MAC address was successfully changed."""
        current_mac = self.get_current_mac(interface)
        if current_mac and current_mac.replace("-", ":") == expected_mac:
            logger.info(f"MAC address successfully changed to {current_mac}")
            return True
        else:
            logger.error("MAC address change verification failed")
            return False


def create_argument_parser(mac_changer: MACChanger) -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Change MAC address for network interfaces",
        epilog="Example: sudo python3 mac_changer.py -i eth0 -m aa:bb:cc:dd:ee:ff",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--interface",
        type=mac_changer.validate_interface,
        help="Network interface name (e.g., eth0, wlan0)",
    )

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-m",
        "--mac",
        type=mac_changer.validate_mac_address,
        help="New MAC address (format: aa:bb:cc:dd:ee:ff)",
    )
    group.add_argument(
        "-c", "--current", action="store_true", help="Display current MAC address"
    )

    parser.add_argument(
        "-l", "--list", action="store_true", help="List available network interfaces"
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    return parser


def main():
    """Main function."""
    mac_changer = MACChanger()

    try:
        # System compatibility check
        mac_changer.check_system_compatibility()

        # Create argument parser
        parser = create_argument_parser(mac_changer)
        args = parser.parse_args()

        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Handle list interfaces option
        if args.list:
            interfaces = mac_changer.get_available_interfaces()
            if interfaces:
                print("Available network interfaces:")
                for interface in interfaces:
                    current_mac = mac_changer.get_current_mac(interface)
                    if current_mac:
                        print(f"  {interface}: {current_mac}")
                    else:
                        print(f"  {interface}: (MAC not available)")
            else:
                print("No network interfaces found")
            return

        # Check that interface and action are provided for operations that need them
        if not args.interface:
            parser.error("Interface (-i/--interface) is required for this operation")
        if not (args.mac or args.current):
            parser.error("Either -m/--mac or -c/--current is required")

        # Handle current MAC display
        if args.current:
            current_mac = mac_changer.get_current_mac(args.interface)
            if current_mac:
                print(f"Current MAC address for {args.interface}: {current_mac}")
            else:
                print(f"Could not retrieve MAC address for {args.interface}")
                sys.exit(1)
            return

        # Handle MAC address change
        if args.mac:
            if args.dry_run:
                current_mac = mac_changer.get_current_mac(args.interface)
                print(f"DRY RUN: Would change MAC address for {args.interface}")
                print(f"  From: {current_mac or 'unknown'}")
                print(f"  To:   {args.mac}")
                return

            # Check permissions for actual changes
            mac_changer.check_permissions()

            # Get current MAC for comparison
            current_mac = mac_changer.get_current_mac(args.interface)
            if current_mac:
                print(f"Current MAC address: {current_mac}")

            # Perform MAC address change
            success = mac_changer.change_mac_address(args.interface, args.mac)

            if success:
                # Verify the change
                if mac_changer.verify_mac_change(args.interface, args.mac):
                    print(f"✅ MAC address successfully changed to {args.mac}")
                else:
                    print("❌ MAC address change failed verification")
                    sys.exit(1)
            else:
                print("❌ Failed to change MAC address")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except PermissionError as e:
        print(f"❌ Permission Error: {e.message}")
        sys.exit(1)
    except InterfaceError as e:
        print(f"❌ Interface Error: {e.message}")
        if e.interface_name:
            print(f"Interface '{e.interface_name}' not found.")
        interfaces = mac_changer.get_available_interfaces()
        if interfaces:
            print("Available interfaces:", ", ".join(interfaces))
        sys.exit(1)
    except MACChangerError as e:
        print(f"❌ Error: {e.message}")
        if e.error_code:
            logger.error(f"Error code: {e.error_code}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
