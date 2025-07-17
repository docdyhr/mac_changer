#!/usr/bin/env python
"""Change MAC address for a given interface with ifconfig.

7. Jan 2022 thomas@dyhr.com
version 0.5
"""

import argparse
import platform
import re
import subprocess
import sys


def system_check():
    """Check System OS."""
    system_os = platform.system()
    if system_os.lower() != "Linux".lower():
        try:
            check_ipconfig = subprocess.call(["type", "ifconfig"])
            if check_ipconfig == 0:
                return
        except Exception:
            pass
        else:
            print("[-] System OS: " + system_os)
            print("[-] This script only works on Linux Systems ... Quitting!")
            sys.exit()


def validate_interface(network_interface):
    """Validate network interface for argparse"""
    # regex = re.compile(r'([a-z]{2,})([0-9][:])') # [:] could be optional
    regex = re.compile(r"([a-z]{2,})([0-9])")

    if re.match(regex, network_interface) is not None:
        return network_interface
    msg = f"[-] Invalid network interface name: '{network_interface}'"
    raise argparse.ArgumentTypeError(msg)


def validate_mac_addr(mac_addr):
    """Validate MAC Address for argparse"""
    regex = re.compile(
        r"^((([a-f0-9]{2}:){5})|(([a-f0-9]{2}-){5}))[a-f0-9]{2}$", re.IGNORECASE
    )

    if re.match(regex, mac_addr) is not None:
        return mac_addr
    msg = f"[-] Invalid MAC address: '{mac_addr}'"
    raise argparse.ArgumentTypeError(msg)


def get_args():
    """Get get network interface and MAC address"""
    parser = argparse.ArgumentParser(description="Change MAC address.")
    parser.add_argument(
        "-i",
        "--interface",
        type=validate_interface,
        nargs=1,
        action="store",
        help="Network interface ex.: 'eth0'",
    )
    parser.add_argument(
        "-m",
        "--macaddress",
        type=validate_mac_addr,
        nargs=1,
        action="store",
        help="Input a valid MAC address ex.: 'aa:10:bb:20:cc:30'",
    )
    parser.add_argument(
        "-c",
        "--current",
        action="store_true",
        help="Show current MAC address ex.: '00:15:73:b9:9e:61'",
    )

    args = parser.parse_args()
    # DEBUG:
    # print(f'DEBUG: {vars(args) = }')

    if not args.interface:
        parser.error("[-] Please specify an interface, use --help for more info.")
    elif not (args.macaddress or args.current):
        parser.error("[-] Please include option -m or -c, use --help for more info.")
    return args


def change_mac(interface, new_macaddress):
    """Change MAC address."""
    print("[+] Changing MAC adddress for " + interface + " to " + new_macaddress)
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", new_macaddress])
    subprocess.call(["ifconfig", interface, "up"])


def get_current_mac(interface):
    """Get current MAC address."""
    ifconfig_result = subprocess.check_output(["ifconfig", interface])
    ifconfig_result = ifconfig_result.decode(
        "utf-8"
    )  # change bytecode object to string
    mac_address_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", ifconfig_result)

    if mac_address_result:
        return mac_address_result.group(0)

    print("[-] Could not read MAC address. ")


def main():
    """Change MAC Address with ipconfig."""
    system_check()
    options = get_args()
    # DEBUG:
    # print(f'DEBUG: {vars(options) = }')

    if options.interface:
        if options.macaddress:
            current_mac = get_current_mac(options.interface[0])
            if current_mac:
                print("Current Mac address = " + current_mac)
            else:
                print("[-] Could not read current MAC address.")
                return
            change_mac(options.interface[0], options.macaddress[0])
            current_mac = get_current_mac(options.interface[0])
            if current_mac and current_mac == options.macaddress[0]:
                print("[+] MAC address was successfully changed to " + current_mac)
            else:
                print("[-] MAC address did not get changed.")
        elif options.current:
            current_mac = get_current_mac(options.interface[0])
            if current_mac:
                print("Current Mac address = " + current_mac)
            else:
                print("[-] Could not read current MAC address.")


if __name__ == "__main__":
    main()
