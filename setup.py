#!/usr/bin/env python3
"""Setup script for MAC Address Changer.

This script allows for easy installation of the MAC changer tool
as a system-wide command or in a virtual environment.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


# Read version from the main module
def get_version():
    """Extract version from mac_changer.py"""
    version_line = None
    with open(os.path.join(this_directory, "mac_changer.py"), "r") as f:
        for line in f:
            if line.startswith("version"):
                version_line = line
                break

    if version_line:
        # Extract version number from line like "version 0.5"
        version = version_line.split()[-1]
        return version.strip("\"'")
    return "0.5"


setup(
    name="mac-address-changer",
    version=get_version(),
    author="Thomas Juul Dyhr",
    author_email="thomas@dyhr.com",
    description="A Python tool for changing MAC addresses on network interfaces",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mac_changer",
    py_modules=["mac_changer"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Security",
    ],
    keywords="mac address changer network interface ifconfig security",
    python_requires=">=3.12",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mac-changer=mac_changer:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/yourusername/mac_changer/issues",
        "Source": "https://github.com/yourusername/mac_changer",
        "Documentation": "https://github.com/yourusername/mac_changer/blob/main/README.md",
    },
)
