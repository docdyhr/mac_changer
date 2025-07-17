#!/bin/bash
# MAC Address Changer - Installation Script
# This script installs the MAC Address Changer with all development tools

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Check if running on supported OS
check_os() {
    OS=$(uname -s)
    case $OS in
        Linux*)
            print_status "Detected Linux system"
            ;;
        Darwin*)
            print_status "Detected macOS system"
            ;;
        *)
            print_error "Unsupported operating system: $OS"
            print_error "This tool only supports Linux and macOS"
            exit 1
            ;;
    esac
}

# Check if Python is installed
check_python() {
    # First try to use Python 3.12 if available
    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD="python3.12"
        print_status "Using Python 3.12 (optimal version)"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        print_status "Using default Python 3"
    else
        print_error "Python 3 is not installed"
        print_error "Please install Python 3.12 or higher"
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_status "Found Python $PYTHON_VERSION"

    # Check if version is 3.12 or higher (now required), but allow 3.8+ for compatibility
    if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_error "Python 3.8 or higher is required for compatibility"
        print_error "Current version: $PYTHON_VERSION"
        exit 1
    fi
    
    # Warn if not using Python 3.12+
    if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)"; then
        print_warning "Python 3.12+ is now the target version for this project"
        print_warning "Current version: $PYTHON_VERSION"
        print_warning "For best performance, please upgrade to Python 3.12+"
    fi
}

# Check if ifconfig is available
check_ifconfig() {
    if ! command -v ifconfig &> /dev/null; then
        print_warning "ifconfig not found"
        case $OS in
            Linux*)
                print_status "Installing net-tools..."
                if command -v apt-get &> /dev/null; then
                    sudo apt-get update && sudo apt-get install -y net-tools
                elif command -v yum &> /dev/null; then
                    sudo yum install -y net-tools
                elif command -v dnf &> /dev/null; then
                    sudo dnf install -y net-tools
                elif command -v pacman &> /dev/null; then
                    sudo pacman -S net-tools
                else
                    print_error "Could not install net-tools automatically"
                    print_error "Please install net-tools package manually"
                    exit 1
                fi
                ;;
            Darwin*)
                print_error "ifconfig should be available on macOS by default"
                print_error "Please check your system installation"
                exit 1
                ;;
        esac
    else
        print_status "ifconfig is available"
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."

    if [ -d ".venv" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf .venv
        else
            print_status "Using existing virtual environment"
            return
        fi
    fi

    $PYTHON_CMD -m venv .venv
    print_status "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source .venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip
    print_status "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."

    # Install development dependencies
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
        print_status "Development dependencies installed"
    else
        print_warning "requirements-dev.txt not found, installing basic dependencies"
        pip install pytest black flake8 mypy bandit safety
    fi

    # Install the package in development mode
    pip install -e .
    print_status "Package installed in development mode"
}

# Set up pre-commit hooks
setup_precommit() {
    print_status "Setting up pre-commit hooks..."

    if [ -f ".pre-commit-config.yaml" ]; then
        pre-commit install
        print_status "Pre-commit hooks installed"
    else
        print_warning ".pre-commit-config.yaml not found, skipping pre-commit setup"
    fi
}

# Run tests
run_tests() {
    print_status "Running tests..."

    if [ -f "test_mac_changer.py" ]; then
        python -m pytest test_mac_changer.py -v
        print_status "Tests completed successfully"
    else
        print_warning "test_mac_changer.py not found, skipping tests"
    fi
}

# Check installation
check_installation() {
    print_status "Checking installation..."

    # Test import
    python -c "import mac_changer; print(f'✅ MAC Changer v{mac_changer.__version__} imported successfully')"

    # Test CLI
    python mac_changer.py --help > /dev/null
    print_status "CLI interface working"

    # Test console script if available
    if command -v mac-changer &> /dev/null; then
        mac-changer --help > /dev/null
        print_status "Console script working"
    fi
}

# Main installation function
main() {
    print_header "MAC Address Changer - Installation Script"
    print_header "========================================="

    # Check prerequisites
    check_os
    check_python
    check_ifconfig

    # Install
    create_venv
    activate_venv
    install_dependencies
    setup_precommit

    # Verify installation
    run_tests
    check_installation

    print_header "Installation Complete!"
    print_header "====================="
    print_status "To use the MAC Address Changer:"
    echo "  1. Activate virtual environment: source .venv/bin/activate"
    echo "  2. Run the tool: python mac_changer.py --help"
    echo "  3. Or use console script: mac-changer --help"
    echo ""
    print_status "To contribute to development:"
    echo "  1. Make changes to the code"
    echo "  2. Run tests: python -m pytest test_mac_changer.py -v"
    echo "  3. Check code quality: black mac_changer.py && flake8 mac_changer.py"
    echo "  4. Commit changes (pre-commit hooks will run automatically)"
    echo ""
    print_warning "Remember: MAC address changes require root privileges"
    print_warning "Use 'sudo' when actually changing MAC addresses"
}

# Parse command line arguments
SKIP_TESTS=false
SKIP_PRECOMMIT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-precommit)
            SKIP_PRECOMMIT=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-tests      Skip running tests after installation"
            echo "  --skip-precommit  Skip setting up pre-commit hooks"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Modify functions based on arguments
if [ "$SKIP_TESTS" = true ]; then
    run_tests() {
        print_status "Skipping tests (--skip-tests flag)"
    }
fi

if [ "$SKIP_PRECOMMIT" = true ]; then
    setup_precommit() {
        print_status "Skipping pre-commit setup (--skip-precommit flag)"
    }
fi

# Run main function
main
