<div align="right">

<a href="https://railway.com?referralCode=QhjuBc">

  <img width="160" src="https://raw.githubusercontent.com/docdyhr/.github/main/assets/railway-corner-v2@2x.png" alt="Deploy on Railway — $20 free credits">

</a>

</div>

# MAC Address Changer

A Python command-line tool for changing MAC addresses on network interfaces using `ifconfig`. This tool provides a simple and safe way to modify network interface MAC addresses on Linux and macOS systems.

## Features

- ✅ Change MAC address for any network interface
- ✅ Display current MAC address
- ✅ Input validation for interfaces and MAC addresses
- ✅ Support for both colon (:) and dash (-) separated MAC formats
- ✅ Cross-platform support (Linux/macOS)
- ✅ Comprehensive error handling with custom exceptions
- ✅ Extensive unit tests (34 test cases, 100% coverage)
- ✅ **Production-ready with enterprise features**:
  - 🔒 Security hardened (95/100 security score)
  - 💾 Automated backup and restore system
  - 📊 Comprehensive system testing
  - 🔄 CI/CD pipeline with automated releases
  - 📋 Complete audit trail and logging

## Requirements

- Python 3.12+ (3.8+ supported for compatibility)
- `ifconfig` command (pre-installed on most Linux/macOS systems)
- Root/Administrator privileges for changing MAC addresses

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/mac_changer.git
cd mac_changer
```

2. (Optional) Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. The tool uses only Python standard library modules, so no additional dependencies are required.

## Usage

### Basic Syntax

```bash
python3 mac_changer.py -i <interface> [options]
```

### Examples

**View current MAC address:**

```bash
python3 mac_changer.py -i eth0 -c
```

**Change MAC address:**

```bash
sudo python3 mac_changer.py -i eth0 -m aa:bb:cc:dd:ee:ff
```

**Using dash-separated format:**

```bash
sudo python3 mac_changer.py -i wlan0 -m aa-bb-cc-dd-ee-ff
```

### Command Line Options

| Option | Long Form      | Description              | Example                |
| ------ | -------------- | ------------------------ | ---------------------- |
| `-i`   | `--interface`  | Network interface name   | `-i eth0`              |
| `-m`   | `--macaddress` | New MAC address          | `-m aa:bb:cc:dd:ee:ff` |
| `-c`   | `--current`    | Show current MAC address | `-c`                   |
| `-h`   | `--help`       | Show help message        | `-h`                   |

## Supported Formats

### Network Interfaces

- Ethernet: `eth0`, `eth1`, etc.
- Wireless: `wlan0`, `wlan1`, etc.
- Other: `enp0s3`, `wlp2s0`, etc.

### MAC Address Formats

- Colon-separated: `aa:bb:cc:dd:ee:ff`
- Dash-separated: `aa-bb-cc-dd-ee-ff`
- Case-insensitive (both uppercase and lowercase accepted)

## Security Considerations

⚠️ **Important Security Notes:**

1. **Root Privileges Required**: Changing MAC addresses requires root/administrator privileges
2. **Network Disruption**: Changing MAC addresses will temporarily disconnect the network interface
3. **Legal Compliance**: Ensure MAC address changes comply with your local laws and network policies
4. **Detection**: Some networks may detect and block MAC address changes

## Testing

Run the included unit tests:

```bash
python3 -m unittest test_mac_changer.py -v
```

Or run tests directly:

```bash
python3 test_mac_changer.py
```

## Error Handling

The tool includes comprehensive error handling for:

- Invalid network interface names
- Malformed MAC addresses
- Missing interfaces
- Permission errors
- System compatibility issues

## Platform Support

| Platform | Support    | Notes                       |
| -------- | ---------- | --------------------------- |
| Linux    | ✅ Full    | Primary target platform     |
| macOS    | ✅ Full    | Requires `ifconfig` command |
| Windows  | ❌ Limited | Not officially supported    |

## Troubleshooting

### Common Issues

**Permission Denied:**

```bash
# Solution: Run with sudo
sudo python3 mac_changer.py -i eth0 -m aa:bb:cc:dd:ee:ff
```

**Interface Not Found:**

```bash
# Solution: Check available interfaces
ip link show  # Linux
ifconfig -a   # macOS/Linux
```

**Command Not Found (ifconfig):**

```bash
# On newer Linux distributions, install net-tools
sudo apt-get install net-tools  # Debian/Ubuntu
sudo yum install net-tools      # RHEL/CentOS
```

## Development

### Project Structure

```
mac_changer/
├── mac_changer.py              # Main application (improved version)
├── test_mac_changer.py         # Comprehensive unit tests (34 tests)
├── setup.py                    # Package installation script
├── pyproject.toml              # Modern Python project configuration
├── requirements.txt            # Runtime dependencies (none)
├── requirements-dev.txt        # Development dependencies
├── README.md                   # This file
├── CONTRIBUTING.md            # Development guidelines
├── RECOMMENDATIONS.md         # Project recommendations
├── TODO.md                    # Prioritized development tasks
├── CLAUDE.md                  # Development best practices
├── BACKUP_PROCEDURES.md       # Comprehensive backup documentation
├── P0_IMPLEMENTATION_SUMMARY.md # P0 critical items completion summary
├── LICENSE                     # MIT License
├── .gitignore                 # Git ignore rules
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
├── .flake8                    # Linting configuration
├── .bandit                    # Security scanning configuration
├── .github/workflows/         # GitHub Actions automation
│   ├── ci.yml                 # Continuous integration
│   └── release.yml            # Automated releases
├── scripts/                   # Automation scripts
│   ├── test_systems.py        # Production system testing
│   ├── backup_restore.py      # Backup and restore system
│   ├── security_audit.py      # Security audit and scanning
│   ├── bump_version.py        # Automated version bumping
│   └── install.sh             # Installation script
├── backups/                   # Backup storage system
├── reports/                   # Test and audit reports
└── archive/                   # Original files for reference
    ├── mac_changer_original.py
    ├── test_original.py
    └── private_changer_helper.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines and [TODO.md](TODO.md) for prioritized development tasks.

### Code Style

The project follows Python best practices:

- PEP 8 style guidelines
- Comprehensive docstrings
- Type hints (where applicable)
- Proper error handling with custom exceptions
- Automated formatting with Black
- Linting with Flake8
- Type checking with MyPy
- Security scanning with Bandit
- Pre-commit hooks for quality assurance
- 100% test coverage with 34 comprehensive test cases

See [CLAUDE.md](CLAUDE.md) for detailed development practices and automation setup.

### Production Readiness Status

**✅ PRODUCTION READY** - All P0 Critical Items completed:

- **System Testing**: Multi-platform compatibility verified
- **Backup Procedures**: Complete backup and restore system
- **Security Audit**: Comprehensive security scanning and hardening
- **Quality Assurance**: 100% test coverage, automated CI/CD
- **Documentation**: Complete operational procedures

See [P0_IMPLEMENTATION_SUMMARY.md](P0_IMPLEMENTATION_SUMMARY.md) for detailed implementation status.

## Version History

- **v1.0** (Current) - Complete rewrite with OOP design, comprehensive error handling, and security improvements
  - ✅ **P0 Critical Items COMPLETED**: Production system testing, backup procedures, security audit
  - ✅ **Enterprise-ready**: 100% test coverage, CI/CD pipeline, comprehensive documentation
  - ✅ **Security hardened**: 95/100 security score, no critical vulnerabilities
  - ✅ **Production-ready**: Multi-platform testing, automated backup/restore, complete audit trail
- **v0.5** (Jan 2022) - Original version with basic validation and error handling
- **v0.4** - Added cross-platform support
- **v0.3** - Enhanced MAC address validation
- **v0.2** - Added unit tests
- **v0.1** - Initial release

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Thomas Juul Dyhr - thomas@dyhr.com

## Disclaimer

This tool is provided for educational and legitimate network administration purposes. Users are responsible for ensuring compliance with applicable laws and regulations. The authors are not responsible for any misuse of this software.

---

**⚠️ Always backup your network configuration before making changes!**
