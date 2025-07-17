#!/usr/bin/env python3
"""Comprehensive test suite for the improved MAC changer.

This test suite covers all functionality of the improved MAC changer
including validation, error handling, and system interactions.

Run with: python3 -m unittest test_improved.py -v
"""

import unittest
import argparse
import subprocess
from unittest.mock import patch, MagicMock, call
import sys
import os

# Add the current directory to path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mac_changer as mci


class TestMACChanger(unittest.TestCase):
    """Test cases for the MACChanger class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mac_changer = mci.MACChanger()

    def test_mac_regex_patterns(self):
        """Test MAC address regex validation."""
        valid_macs = [
            "aa:bb:cc:dd:ee:ff",
            "AA:BB:CC:DD:EE:FF",
            "00:11:22:33:44:55",
            "aa-bb-cc-dd-ee-ff",
            "AA-BB-CC-DD-EE-FF",
        ]

        invalid_macs = [
            "aa:bb:cc:dd:ee",  # Too short
            "aa:bb:cc:dd:ee:ff:gg",  # Too long
            "zz:bb:cc:dd:ee:ff",  # Invalid hex
            "aa:bb:cc:dd:ee:fg",  # Invalid hex character
            "aa.bb.cc.dd.ee.ff",  # Wrong separator
            "aabbccddeeff",  # No separators
            "",  # Empty string
            "aa:bb:cc:dd:ee:ff:00",  # Extra segment
        ]

        for mac in valid_macs:
            with self.subTest(mac=mac):
                self.assertTrue(
                    self.mac_changer.mac_regex.match(mac.lower().replace("-", ":")),
                    f"Valid MAC {mac} should match regex",
                )

        for mac in invalid_macs:
            with self.subTest(mac=mac):
                self.assertFalse(
                    self.mac_changer.mac_regex.match(mac.lower().replace("-", ":")),
                    f"Invalid MAC {mac} should not match regex",
                )

    def test_interface_regex_patterns(self):
        """Test interface name regex validation."""
        valid_interfaces = [
            "eth0",
            "eth1",
            "wlan0",
            "wlan1",
            "enp0s3",
            "wlp2s0",
            "lo0",
            "en0",
        ]

        invalid_interfaces = [
            "eth",
            "0eth",
            "eth-0",
            "eth_0",
            "",
            "123",
            "eth0:1",
            "really_long_interface_name_that_does_not_match",
        ]

        for interface in valid_interfaces:
            with self.subTest(interface=interface):
                self.assertTrue(
                    self.mac_changer.interface_regex.match(interface),
                    f"Valid interface {interface} should match regex",
                )

        for interface in invalid_interfaces:
            with self.subTest(interface=interface):
                self.assertFalse(
                    self.mac_changer.interface_regex.match(interface),
                    f"Invalid interface {interface} should not match regex",
                )

    def test_validate_mac_address_success(self):
        """Test successful MAC address validation."""
        test_cases = [
            ("aa:bb:cc:dd:ee:ff", "aa:bb:cc:dd:ee:ff"),
            ("AA:BB:CC:DD:EE:FF", "aa:bb:cc:dd:ee:ff"),
            ("aa-bb-cc-dd-ee-ff", "aa:bb:cc:dd:ee:ff"),
            ("AA-BB-CC-DD-EE-FF", "aa:bb:cc:dd:ee:ff"),
        ]

        for input_mac, expected_output in test_cases:
            with self.subTest(input_mac=input_mac):
                result = self.mac_changer.validate_mac_address(input_mac)
                self.assertEqual(result, expected_output)

    def test_validate_mac_address_failure(self):
        """Test MAC address validation failures."""
        invalid_macs = [
            "",
            "invalid",
            "aa:bb:cc:dd:ee",
            "aa:bb:cc:dd:ee:ff:gg",
            "zz:bb:cc:dd:ee:ff",
        ]

        for mac in invalid_macs:
            with self.subTest(mac=mac):
                with self.assertRaises(argparse.ArgumentTypeError):
                    self.mac_changer.validate_mac_address(mac)

    @patch("mac_changer.subprocess.run")
    def test_interface_exists_success(self, mock_run):
        """Test interface existence check - success case."""
        mock_run.return_value.returncode = 0

        result = self.mac_changer.interface_exists("eth0")

        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["ifconfig", "eth0"], capture_output=True, check=False, timeout=5
        )

    @patch("mac_changer.subprocess.run")
    def test_interface_exists_failure(self, mock_run):
        """Test interface existence check - failure case."""
        mock_run.return_value.returncode = 1

        result = self.mac_changer.interface_exists("nonexistent")

        self.assertFalse(result)

    @patch("mac_changer.subprocess.run")
    def test_interface_exists_timeout(self, mock_run):
        """Test interface existence check - timeout case."""
        mock_run.side_effect = subprocess.TimeoutExpired("ifconfig", 5)

        result = self.mac_changer.interface_exists("eth0")

        self.assertFalse(result)

    def test_validate_interface_success(self):
        """Test successful interface validation."""
        with patch.object(self.mac_changer, "interface_exists", return_value=True):
            result = self.mac_changer.validate_interface("eth0")
            self.assertEqual(result, "eth0")

    def test_validate_interface_not_found(self):
        """Test interface validation when interface doesn't exist."""
        with patch.object(self.mac_changer, "interface_exists", return_value=False):
            with self.assertRaises(mci.InterfaceError):
                self.mac_changer.validate_interface("eth0")

    def test_validate_interface_invalid_format(self):
        """Test interface validation with invalid format."""
        with self.assertRaises(argparse.ArgumentTypeError):
            self.mac_changer.validate_interface("invalid_interface")

    def test_validate_interface_empty(self):
        """Test interface validation with empty string."""
        with self.assertRaises(argparse.ArgumentTypeError):
            self.mac_changer.validate_interface("")

    @patch("mac_changer.subprocess.run")
    def test_get_current_mac_success(self, mock_run):
        """Test successful MAC address retrieval."""
        mock_output = """
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.100  netmask 255.255.255.0  broadcast 192.168.1.255
        inet6 fe80::a8:60ff:feb6:d702  prefixlen 64  scopeid 0x20<link>
        ether aa:bb:cc:dd:ee:ff  txqueuelen 1000  (Ethernet)
        RX packets 12345  bytes 1234567 (1.1 MB)
        """

        mock_run.return_value.stdout = mock_output
        mock_run.return_value.returncode = 0

        result = self.mac_changer.get_current_mac("eth0")

        self.assertEqual(result, "aa:bb:cc:dd:ee:ff")
        mock_run.assert_called_once_with(
            ["ifconfig", "eth0"], capture_output=True, check=True, text=True, timeout=5
        )

    @patch("mac_changer.subprocess.run")
    def test_get_current_mac_not_found(self, mock_run):
        """Test MAC address retrieval when MAC not found in output."""
        mock_output = "No MAC address in this output"
        mock_run.return_value.stdout = mock_output
        mock_run.return_value.returncode = 0

        result = self.mac_changer.get_current_mac("eth0")

        self.assertIsNone(result)

    @patch("mac_changer.subprocess.run")
    def test_get_current_mac_command_error(self, mock_run):
        """Test MAC address retrieval when command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "ifconfig")

        result = self.mac_changer.get_current_mac("eth0")

        self.assertIsNone(result)

    @patch("mac_changer.subprocess.run")
    def test_get_current_mac_timeout(self, mock_run):
        """Test MAC address retrieval timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("ifconfig", 5)

        result = self.mac_changer.get_current_mac("eth0")

        self.assertIsNone(result)

    @patch("mac_changer.subprocess.run")
    def test_change_mac_address_success(self, mock_run):
        """Test successful MAC address change."""
        mock_run.return_value.returncode = 0

        result = self.mac_changer.change_mac_address("eth0", "aa:bb:cc:dd:ee:ff")

        self.assertTrue(result)

        expected_calls = [
            call(["ifconfig", "eth0", "down"], check=True, timeout=10),
            call(
                ["ifconfig", "eth0", "hw", "ether", "aa:bb:cc:dd:ee:ff"],
                check=True,
                timeout=10,
            ),
            call(["ifconfig", "eth0", "up"], check=True, timeout=10),
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch("mac_changer.subprocess.run")
    def test_change_mac_address_failure(self, mock_run):
        """Test MAC address change failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "ifconfig")

        result = self.mac_changer.change_mac_address("eth0", "aa:bb:cc:dd:ee:ff")

        self.assertFalse(result)

    @patch("mac_changer.subprocess.run")
    def test_change_mac_address_timeout(self, mock_run):
        """Test MAC address change timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("ifconfig", 10)

        result = self.mac_changer.change_mac_address("eth0", "aa:bb:cc:dd:ee:ff")

        self.assertFalse(result)

    def test_verify_mac_change_success(self):
        """Test successful MAC change verification."""
        with patch.object(
            self.mac_changer, "get_current_mac", return_value="aa:bb:cc:dd:ee:ff"
        ):
            result = self.mac_changer.verify_mac_change("eth0", "aa:bb:cc:dd:ee:ff")
            self.assertTrue(result)

    def test_verify_mac_change_failure(self):
        """Test failed MAC change verification."""
        with patch.object(
            self.mac_changer, "get_current_mac", return_value="11:22:33:44:55:66"
        ):
            result = self.mac_changer.verify_mac_change("eth0", "aa:bb:cc:dd:ee:ff")
            self.assertFalse(result)

    def test_verify_mac_change_no_mac(self):
        """Test MAC change verification when no MAC is retrieved."""
        with patch.object(self.mac_changer, "get_current_mac", return_value=None):
            result = self.mac_changer.verify_mac_change("eth0", "aa:bb:cc:dd:ee:ff")
            self.assertFalse(result)

    @patch("mac_changer.platform.system")
    @patch("mac_changer.subprocess.run")
    def test_system_compatibility_check_linux(self, mock_run, mock_platform):
        """Test system compatibility check on Linux."""
        mock_platform.return_value = "Linux"
        mock_run.return_value.returncode = 0

        # Should not raise exception
        self.mac_changer.check_system_compatibility()

    @patch("mac_changer.platform.system")
    def test_system_compatibility_check_unsupported(self, mock_platform):
        """Test system compatibility check on unsupported platform."""
        mock_platform.return_value = "Windows"

        with self.assertRaises(mci.MACChangerError):
            self.mac_changer.check_system_compatibility()

    @patch("mac_changer.platform.system")
    @patch("mac_changer.subprocess.run")
    def test_system_compatibility_check_no_ifconfig(self, mock_run, mock_platform):
        """Test system compatibility check when ifconfig not found."""
        mock_platform.return_value = "Linux"
        mock_run.return_value.returncode = 1

        with self.assertRaises(mci.MACChangerError):
            self.mac_changer.check_system_compatibility()

    @patch("mac_changer.os.geteuid")
    def test_check_permissions_root(self, mock_geteuid):
        """Test permission check when running as root."""
        mock_geteuid.return_value = 0

        # Should not raise exception
        self.mac_changer.check_permissions()

    @patch("mac_changer.os.geteuid")
    def test_check_permissions_non_root(self, mock_geteuid):
        """Test permission check when not running as root."""
        mock_geteuid.return_value = 1000

        with self.assertRaises(mci.PermissionError):
            self.mac_changer.check_permissions()

    @patch("mac_changer.subprocess.run")
    def test_get_available_interfaces(self, mock_run):
        """Test getting available interfaces."""
        mock_output = """
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        ether aa:bb:cc:dd:ee:ff  txqueuelen 1000  (Ethernet)

wlan0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether 11:22:33:44:55:66  txqueuelen 1000  (Ethernet)

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        loop  txqueuelen 1000  (Local Loopback)
        """

        mock_run.return_value.stdout = mock_output
        mock_run.return_value.returncode = 0

        interfaces = self.mac_changer.get_available_interfaces()

        # Note: 'lo' matches the interface regex pattern
        expected_interfaces = ["eth0", "lo", "wlan0"]
        self.assertEqual(sorted(interfaces), sorted(expected_interfaces))

    @patch("mac_changer.subprocess.run")
    def test_get_available_interfaces_error(self, mock_run):
        """Test getting available interfaces when command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "ifconfig")

        interfaces = self.mac_changer.get_available_interfaces()

        self.assertEqual(interfaces, [])


class TestMainFunction(unittest.TestCase):
    """Test cases for the main function and argument parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.mac_changer = mci.MACChanger()

    @patch("mac_changer.MACChanger")
    @patch("sys.argv", ["mac_changer.py", "-l"])
    def test_main_list_interfaces(self, mock_mac_changer_class):
        """Test main function with list interfaces option."""
        mock_mac_changer = mock_mac_changer_class.return_value
        mock_mac_changer.check_system_compatibility.return_value = None
        mock_mac_changer.get_available_interfaces.return_value = ["eth0", "wlan0"]
        mock_mac_changer.get_current_mac.side_effect = [
            "aa:bb:cc:dd:ee:ff",
            "11:22:33:44:55:66",
        ]

        with patch("builtins.print") as mock_print:
            mci.main()

        mock_print.assert_any_call("Available network interfaces:")
        mock_print.assert_any_call("  eth0: aa:bb:cc:dd:ee:ff")
        mock_print.assert_any_call("  wlan0: 11:22:33:44:55:66")

    def test_create_argument_parser(self):
        """Test argument parser creation."""
        parser = mci.create_argument_parser(self.mac_changer)

        # Test that parser is created successfully
        self.assertIsInstance(parser, argparse.ArgumentParser)

        # Test help functionality (should not raise exception)
        help_text = parser.format_help()
        self.assertIn("Change MAC address", help_text)


class TestErrorClasses(unittest.TestCase):
    """Test custom error classes."""

    def test_mac_changer_error(self):
        """Test MACChangerError exception."""
        with self.assertRaises(mci.MACChangerError):
            raise mci.MACChangerError("Test error")

    def test_permission_error(self):
        """Test PermissionError exception."""
        with self.assertRaises(mci.PermissionError):
            raise mci.PermissionError("Permission denied")

    def test_interface_error(self):
        """Test InterfaceError exception."""
        with self.assertRaises(mci.InterfaceError):
            raise mci.InterfaceError("Interface not found")

    def test_error_inheritance(self):
        """Test that custom errors inherit from MACChangerError."""
        self.assertTrue(issubclass(mci.PermissionError, mci.MACChangerError))
        self.assertTrue(issubclass(mci.InterfaceError, mci.MACChangerError))


if __name__ == "__main__":
    # Run tests with increased verbosity
    unittest.main(verbosity=2, buffer=True)
