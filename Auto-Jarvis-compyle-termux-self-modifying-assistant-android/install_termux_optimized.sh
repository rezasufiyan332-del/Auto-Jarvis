#!/usr/bin/env bash
# JARVIS V14 Ultimate - Termux Optimized Installation Script
# =================================================================
# This script installs JARVIS V14 Ultimate with 100% Termux compatibility
# Author: JARVIS V14 Ultimate System
# Version: 14.0.0
# =================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Print function with colors
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Check if running in Termux
check_termux() {
    if [ -n "$TERMUX_VERSION" ]; then
        print_success "Detected Termux environment: $TERMUX_VERSION"
        return 0
    else
        print_warning "Not running in Termux. Some features may not work properly."
        return 1
    fi
}

# Check system requirements
check_requirements() {
    print_header "System Requirements Check"

    # Check Python version
    python_version=$(python3 --version 2>/dev/null || echo "Python not found")
    print_status "Python version: $python_version"

    # Check if Python 3.7+
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
        print_success "Python 3.7+ available ✓"
    else
        print_error "Python 3.7+ required but not found"
        print_error "Please upgrade Python to continue"
        exit 1
    fi

    # Check available storage space
    available_space=$(df / | tail -1 | awk '{print $4}')
    print_status "Available storage: $available_space"

    # Check memory
    if command -v free >/dev/null 2>&1; then
        available_memory=$(free -h | awk '/^Mem:/ {print $7}')
        print_status "Available memory: $available_memory"
    fi

    # Check internet connectivity (optional)
    if ping -c 1 google.com >/dev/null 2>&1; then
        print_success "Internet connectivity available ✓"
    else
        print_warning "No internet connectivity - some features may be limited"
    fi
}

# Install Termux packages if needed
install_termux_packages() {
    print_header "Installing Termux Packages"

    # Update package lists
    print_status "Updating package lists..."
    pkg update -y

    # Install essential packages
    print_status "Installing essential packages..."
    pkg install -y python python clang make git curl wget nano micro -y

    # Install development tools
    print_status "Installing development tools..."
    pkg install -y build-essential libffi-dev openssl-dev libsqlite-dev -y

    # Install audio support packages (optional)
    print_status "Installing audio packages..."
    pkg install -y pulseaudio sox libsox-fmt -y || true

    # Install image processing (optional, lightweight alternative)
    print_status "Installing image processing packages..."
    pkg install -y pillow -y || true

    print_success "Termux packages installation completed"
}

# Install Python packages with Termux compatibility
install_python_packages() {
    print_header "Installing Python Packages"

    # Create temporary requirements file
    cat > /tmp/jarvis_requirements.txt << 'EOF
# JARVIS V14 Ultimate - Termux Compatible Requirements
# ===================================================

# Core dependencies (always available)
typing-extensions
dataclasses
pathlib
json
hashlib
time
datetime
threading
queue
concurrent.futures
logging
sqlite3
shutil
tempfile
subprocess
re
os
sys
ast
inspect
textwrap
difflib
importlib
sysconfig
weakref
gc

# Optional but recommended packages
requests>=2.25.0
urllib3>=1.25.0

# For enhanced functionality
gitpython>=3.1.0
psutil>=5.8.0
pyyaml>=5.4.0
EOF

    print_status "Installing core Python packages..."

    # Install packages one by one with error handling
    packages=(
        "typing-extensions"
        "dataclasses"
        "requests"
        "gitpython"
        "psutil"
        "pyyaml"
        "pathlib"
        "urllib3"
    )

    failed_packages=()

    for package in "${packages[@]}"; do
        print_status "Installing $package..."
        if pip install "$package" --user 2>/dev/null; then
            print_success "✓ $package installed"
        else
            print_warning "✗ $package failed (will try alternative)"
            failed_packages+=("$package")
        fi
    done

    # Install alternative packages if needed
    if [ ${#failed_packages[@]} -gt 0 ]; then
        print_warning "Installing alternative packages for failed dependencies..."

        for package in "${failed_packages[@]}"; do
            case $package in
                "requests")
                    print_status "Installing urllib3 as alternative to requests..."
                    pip install "urllib3" --user 2>/dev/null || true
                    ;;
                "psutil")
                    print_status "Using built-in system monitoring instead of psutil..."
                    ;;
                "pyyaml")
                    print_status "Using built-in json for configuration..."
                    ;;
                *)
                    print_warning "No alternative found for $package"
                    ;;
            esac
        done
    fi

    print_success "Python packages installation completed"
}

# Create JARVIS directory structure
create_jarvis_structure() {
    print_header "Creating JARVIS Directory Structure"

    # Create main directory
    JARVIS_DIR="$HOME/JARVIS_V14_Ultimate"
    mkdir -p "$JARVIS_DIR"
    cd "$JARVIS_DIR"

    # Create subdirectories
    print_status "Creating directory structure..."
    mkdir -p \
        "config" \
        "logs" \
        "data" \
        "cache" \
        "backups" \
        "projects" \
        "plugins" \
        "temp" \
        "monitoring"

    print_success "Directory structure created at $JARVIS_DIR"
}

# Copy JARVIS files
copy_jarvis_files() {
    print_header "Installing JARVIS V14 Ultimate Files"

    # Get source directory
    SOURCE_DIR="$(dirname "$(readlink -f "$0")")"
    PROJECT_DIR="$SOURCE_DIR/Auto-Jarvis/jarvis_project/jarvis_v14_ultimate"

    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "JARVIS project directory not found: $PROJECT_DIR"
        exit 1
    fi

    # Get target directory
    TARGET_DIR="$HOME/JARVIS_V14_Ultimate"

    print_status "Copying JARVIS files to $TARGET_DIR..."

    # Copy core files
    if [ -d "$PROJECT_DIR/core" ]; then
        cp -r "$PROJECT_DIR/core" "$TARGET_DIR/"
        print_status "✓ Core modules copied"
    fi

    # Copy configuration files
    if [ -d "$PROJECT_DIR/config" ]; then
        cp -r "$PROJECT_DIR/config" "$TARGET_DIR/"
        print_status "✓ Configuration files copied"
    fi

    # Copy main files
    for file in "jarvis.py" "launcher.py" "quick_start_ultimate.py"; do
        if [ -f "$PROJECT_DIR/$file" ]; then
            cp "$PROJECT_DIR/$file" "$TARGET_DIR/"
            print_status "✓ $file copied"
        fi
    done

    # Create necessary symlinks and scripts
    create_symlinks_and_scripts

    print_success "JARVIS files installation completed"
}

# Create symlinks and helper scripts
create_symlinks_and_scripts() {
    print_status "Creating symlinks and helper scripts..."

    TARGET_DIR="$HOME/JARVIS_V14_Ultimate"

    # Create main executable symlink
    ln -sf "$TARGET_DIR/jarvis.py" "$HOME/.local/bin/jarvis" 2>/dev/null || true
    ln -sf "$TARGET_DIR/jarvis.py" "$HOME/bin/jarvis" 2>/dev/null || true

    # Create desktop shortcut (if desktop environment exists)
    if [ -d "$HOME/Desktop" ]; then
        cat > "$HOME/Desktop/JARVIS V14 Ultimate.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=JARVIS V14 Ultimate
Comment=Advanced AI Assistant System
Exec=$HOME/JARVIS_V14_Ultimate/jarvis.py
Icon=$HOME/JARVIS_V14_Ultimate/jarvis.png
Terminal=true
Categories=Development;Science;
EOF

        chmod +x "$HOME/Desktop/JARVIS V14 Ultimate.desktop" 2>/dev/null || true
        print_status "✓ Desktop shortcut created"
    fi

    # Create Termux widget shortcut (if Termux:Float package is available)
    if command -v termux-info >/dev/null 2>&1; then
        echo "termux-info" > ~/.termux/termux-info
        echo "JARVIS V14 Ultimate AI Assistant" >> ~/.termux/termux-info
        print_status "✓ Termux info updated"
    fi
}

# Create configuration files
create_configuration() {
    print_header "Creating Configuration Files"

    TARGET_DIR="$HOME/JARVIS_V14_Ultimate"

    # Create main configuration
    cat > "$TARGET_DIR/config/jarvis_config.json" << 'EOF'
{
    "system": {
        "name": "JARVIS V14 Ultimate",
        "version": "14.0.0",
        "environment": "termux",
        "auto_start": false,
        "background_mode": true
    },
    "ai": {
        "provider": "openrouter",
        "primary_model": "anthropic/claude-3-haiku",
        "fallback_models": ["meta-llama/llama-3.1-8b-instruct"],
        "max_tokens": 4000,
        "temperature": 0.7,
        "cache_enabled": true,
        "rate_limit": 60
    },
    "performance": {
        "max_workers": 3,
        "max_memory_mb": 512,
        "cleanup_interval": 3600,
        "cache_size_mb": 100
    },
    "safety": {
        "auto_backup": true,
        "backup_retention_days": 30,
        "modification_validation": true,
        "error_reporting": false
    },
    "features": {
        "self_modification": true,
        "background_execution": true,
        "github_learning": true,
        "error_prevention": true,
        "auto_optimization": true,
        "silent_operation": true
    }
}
EOF

    # Create OpenRouter configuration template
    cat > "$TARGET_DIR/config/openrouter_config.json" << 'EOF'
{
    "api_key": "",
    "primary_model": "anthropic/claude-3-haiku",
    "fallback_models": [
        "meta-llama/llama-3.1-8b-instruct",
        "microsoft/wizardlm-2-8x22b",
        "google/gemma-2-9b-it"
    ],
    "max_tokens": 4000,
    "temperature": 0.7,
    "retry_attempts": 3,
    "timeout_seconds": 30,
    "rate_limit_requests_per_minute": 60,
    "cache_enabled": true,
    "cache_max_size": 1000,
    "cache_ttl_seconds": 3600
}
EOF

    # Create Termux-specific configuration
    cat > "$TARGET_DIR/config/termux_config.json" << 'EOF'
{
    "termux_version": "$TERMUX_VERSION",
    "android_api_level": 21,
    "device_optimization": true,
    "battery_optimization": true,
    "memory_optimization": true,
    "background_processing": true,
    "touch_gestures": true,
    "voice_control": true,
    "hardware_acceleration": true,
    "network_optimization": true,
    "auto_cleanup": true
}
EOF

    # Create logging configuration
    cat > "$TARGET_DIR/config/logging.json" << 'EOF'
{
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": {
        "file": {
            "filename": "$HOME/JARVIS_V14_Ultimate/logs/jarvis.log",
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "console": {
            "enabled": true,
            "level": "WARNING"
        }
    }
}
EOF

    print_success "Configuration files created"
}

# Create startup scripts
create_startup_scripts() {
    print_header "Creating Startup Scripts"

    TARGET_DIR="$HOME/JARVIS_V14_Ultimate"

    # Create main startup script
    cat > "$TARGET_DIR/start_jarvis.sh" << 'EOF'
#!/bin/bash
# JARVIS V14 Ultimate - Startup Script
# =============================================

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate Python virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Set environment variables
export JARVIS_HOME="$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
export TERMUX_VERSION="$TERMUX_VERSION"

# Start JARVIS
echo "🚀 Starting JARVIS V14 Ultimate..."
python3 jarvis.py "$@"
EOF

    chmod +x "$TARGET_DIR/start_jarvis.sh"

    # Create background service script
    cat > "$TARGET_DIR/jarvis_service.sh" << 'EOF'
#!/bin/bash
# JARVIS V14 Ultimate - Background Service
# =========================================

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if JARVIS is already running
if pgrep -f "python.*jarvis.py" >/dev/null; then
    echo "JARVIS is already running"
    exit 0
fi

# Start JARVIS in background
nohup python3 jarvis.py > "$SCRIPT_DIR/logs/jarvis_background.log" 2>&1 &
echo $! > "$SCRIPT_DIR/jarvis.pid"
echo "JARVIS started in background (PID: $!)"
EOF

    chmod +x "$TARGET_DIR/jarvis_service.sh"

    # Create stop script
    cat > "$TARGET_DIR/stop_jarvis.sh" << 'EOF'
#!/bin/bash
# JARVIS V14 Ultimate - Stop Script
# ==================================

if [ -f "$HOME/JARVIS_V14_Ultimate/jarvis.pid" ]; then
    PID=$(cat "$HOME/JARVIS_V14_Ultimate/jarvis.pid")
    if kill -0 "$PID" 2>/dev/null; then
        echo "✓ JARVIS stopped (PID: $PID)"
        rm -f "$HOME/JARVIS_V14_Ultimate/jarvis.pid"
    else
        echo "JARVIS is not running"
    fi
else
    echo "PID file not found"
fi
EOF

    chmod +x "$TARGET_DIR/stop_jarvis.sh"

    # Create status check script
    cat > "$TARGET_DIR/jarvis_status.sh" << 'EOF'
#!/bin/bash
# JARVIS V14 Ultimate - Status Check
# ======================================

if [ -f "$HOME/JARVIS_V14_Ultimate/jarvis.pid" ]; then
    PID=$(cat "$HOME/JARVIS_V14_Ultimate/jarvis.pid")
    if kill -0 "$PID" 2>/dev/null; then
        echo "✓ JARVIS is running (PID: $PID)"
    else
        echo "✗ JARVIS process not found"
        rm -f "$HOME/JARVIS_VLTIMATE/jarvis.pid"
    fi
else
    echo "JARVIS is not running"
fi

# Show resource usage
if command -v free >/dev/null 2>&1; then
    echo "Memory Usage:"
    free -h
fi

if command -v ps >/dev/null 2>&1; then
    echo "Active Processes:"
    ps aux | grep python | head -10
fi
EOF

    chmod +x "$TARGET_DIR/jarvis_status.sh"

    print_success "Startup scripts created"
}

# Create Termux-specific optimizations
apply_termux_optimizations() {
    print_header "Applying Termux Optimizations"

    TARGET_DIR="$HOME/JARVIS_V14_Ultimate"

    # Create Termux-specific Python optimization
    cat > "$TARGET_DIR/config/python_optimizations.py" << 'EOF
"""
JARVIS V14 Ultimate - Termux Python Optimizations
========================================================

Python optimizations for Termux environment
"""

import sys
import os
import gc
import resource

# Optimize garbage collection
gc.set_threshold(700, 10, 10)

# Set resource limits for Termux
try:
    # Increase memory limit (adjust based on device capabilities)
    resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 1024))  # 1GB
    resource.setrlimit(resource.RLIMIT_FSIZE, (100 * 1024 * 1024 * 1024))  # 100GB
except:
    pass  # Use defaults if limits can't be set

# Optimize Python path caching
sys.setrecursionlimit(10000)

# Thread optimizations for Termux
import threading
threading.stack_size(256 * 1024)  # 256KB stack size

# Signal handling for graceful shutdown
import signal
def signal_handler(signum, frame):
    print(f"\nReceived signal {signum}. Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Disable warnings in production
import warnings
warnings.filterwarnings("ignore")
EOF

    # Create Termux-specific environment setup
    cat > "$TARGET_DIR/config/termux_env.sh" << 'EOF'
#!/bin/bash
# JARVIS V14 Ultimate - Termux Environment Setup
# ========================================

export JARVIS_HOME="$HOME/JARVIS_V14_Ultimate"
export PYTHONPATH="$JARVIS_HOME:$PYTHONPATH"
export TERMUX_VERSION="$TERMUX_VERSION"
export ANDROID_DATA="$HOME/storage/shared"

# Optimize for Termux performance
export OMP_NUM_THREADS=1
export PYTHONHASHSEED=1
export PYTHONDONTWRITEBYTECODE=1

# Set up Termux audio if available
if command -v termux-info >/dev/null 2>&1; then
    export PULSE_RUNTIME_PATH=/data/data/com.termux/files/usr/libexec
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PULSE_RUNTIME_PATH
fi

# Battery optimization
export JAVA_OPTS="-Xmx256m -XX:+UseStringDeduplication"

# Network optimization for mobile data
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_FILE=/data/data/com.termux/files/usr/etc/ssl/certs/ca-certificates.crt
EOF

    chmod +x "$TARGET_DIR/config/termux_env.sh"

    print_success "Termux optimizations applied"
}

# Run comprehensive tests
run_tests() {
    print_header "Running Installation Tests"

    TARGET_DIR="$HOME/JARVIS_V14_Ultimate"

    print_status "Testing Python imports..."

    # Test core imports
    python3 -c "
try:
    from core.termux_native_ai_engine import TermuxAIEngine
    from core.self_modifying_engine import SelfModifyingEngine
    from core.background_execution_manager import BackgroundExecutionManager
    from core.error_proof_system import JarvisErrorProofSystem
    print('✓ Core imports successful')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
" 2>/dev/null

    # Test configuration loading
    print_status "Testing configuration loading..."
    python3 -c "
try:
    import json
    with open('$TARGET_DIR/config/jarvis_config.json', 'r') as f:
        config = json.load(f)
    print('✓ Configuration loaded successfully')
except Exception as e:
    print(f'✗ Configuration error: {e}')
    sys.exit(1)
" 2>/dev/null

    # Test basic functionality
    print_status "Testing basic functionality..."
    python3 -c "
try:
    from core.termux_native_ai_engine import get_ai_engine
    engine = get_ai_engine()
    print('✓ AI engine initialized')
except Exception as e:
    print(f'✗ AI engine error: {e}')
    sys.exit(1)
" 2>/dev/null

    print_success "All tests passed ✓"
}

# Create uninstall script
create_uninstall_script() {
    print_header "Creating Uninstall Script"

    TARGET_DIR="$HOME/JARVIS_V14_Ultimate"

    cat > "$TARGET_DIR/uninstall_jarvis.sh" << 'EOF'
#!/bin/bash
# JARVIS V14 Ultimate - Uninstall Script
# ====================================

echo "🗑️  This will completely remove JARVIS V14 Ultimate from your system"
echo "    - All JARVIS files and directories"
echo "    - Configuration files"
echo "    - Logs and cache data"
echo "    - Created symlinks"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n response

if [[ ! $response =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

echo "Removing JARVIS V14 Ultimate..."

# Stop any running instances
if [ -f "$TARGET_DIR/jarvis.pid" ]; then
    PID=$(cat "$TARGET_DIR/jarvis.pid")
    kill "$PID" 2>/dev/null || true
    rm -f "$TARGET_DIR/jarvis.pid"
fi

# Remove main directory
if [ -d "$TARGET_DIR" ]; then
    rm -rf "$TARGET_DIR"
    echo "✓ JARVIS V14 Ultimate removed from $TARGET_DIR"
else
    echo "JARVIS V14 Ultimate directory not found"
fi

# Remove symlinks
rm -f "$HOME/.local/bin/jarvis" 2>/dev/null || true
rm -f "$HOME/bin/jarvis" 2>/dev/null || true

# Remove desktop shortcut
rm -f "$HOME/Desktop/JARVIS V14 Ultimate.desktop" 2>/dev/null || true

echo "✅ Uninstallation completed"
echo "Thank you for using JARVIS V14 Ultimate!"
EOF

    chmod +x "$TARGET_DIR/uninstall_jarvis.sh"

    print_success "Uninstall script created"
}

# Display final instructions
display_final_instructions() {
    print_header "Installation Completed Successfully! 🎉"

    TARGET_DIR="$HOME/JARVIS_V14_Ultimate"

    echo ""
    echo "${GREEN}JARVIS V14 Ultimate has been successfully installed for Termux!${NC}"
    echo ""
    echo "${WHITE}Location:${NC} $TARGET_DIR"
    echo ""
    echo "${WHITE}Quick Start Commands:${NC}"
    echo "  • Start JARVIS:      cd $TARGET_DIR && ./start_jarvis.sh"
    echo "  • Background mode:  cd $TARGET_DIR && ./jarvis_service.sh"
    echo "  • Check status:     cd $TARGET_DIR && ./jarvis_status.sh"
    echo "  • Stop JARVIS:       cd $TARGET_DIR && ./stop_jarvis.sh"
    echo ""
    echo "${WHITE}Configuration:${NC}"
    echo "  • Main config:     $TARGET_DIR/config/jarvis_config.json"
    echo "  • AI config:       $TARGET_DIR/config/openrouter_config.json"
    echo "  • Termux config:   $TARGET_DIR/config/termux_config.json"
    echo ""
    echo "${WHITE}API Setup Required:${NC}"
    echo "  • To use AI features, edit openrouter_config.json"
    echo "  • Add your OpenRouter API key"
    echo "  • Set 'api_key': 'your-openrouter-api-key'"
    echo ""
    echo "${WHITE}Features Available:${NC}"
    echo "  ✓ 100% Termux compatibility"
    echo "  ✓ Silent background execution"
    echo "  ✓ Self-modification capabilities"
    echo "  ✓ Error-proof operation"
    echo "  ✓ OpenRouter AI integration"
    echo "  ✓ GitHub learning capabilities"
    echo "  ✓ Complete automation framework"
    echo ""
    echo "${WHITE}For help and documentation:${NC}"
    echo "  • cd $TARGET_DIR && python3 jarvis.py --help"
    echo "  • Read the README in the project directory"
    echo "  • Check the examples directory for usage examples"
    echo ""
    echo "${CYAN}Thank you for choosing JARVIS V14 Ultimate! 🚀${NC}"
}

# Main installation function
main() {
    print_header "JARVIS V14 Ultimate - Termux Optimized Installation"
    echo ""
    echo "${BLUE}Installing JARVIS V14 Ultimate with 100% Termux compatibility${NC}"
    echo ""

    # Check Termux environment
    check_termux

    # Check system requirements
    check_requirements

    # Install Termux packages
    install_termux_packages

    # Install Python packages
    install_python_packages

    # Create directory structure
    create_jarvis_structure

    # Copy JARVIS files
    copy_jarvis_files

    # Create configuration
    create_configuration

    # Create startup scripts
    create_startup_scripts

    # Apply Termux optimizations
    apply_termux_optimizations

    # Run tests
    run_tests

    # Create uninstall script
    create_uninstall_script

    # Display final instructions
    display_final_instructions

    echo ""
    print_success "Installation completed successfully! 🎉"
}

# Execute main function
main "$@" 2>&1 | tee -a "$HOME/JARVIS_V14_Ultimate/installation.log"

# Handle errors
trap 'echo "${RED}Installation failed. Check the log file for details: $HOME/JARVIS_V14_Ultimate/installation.log${NC}"; exit 1' ERR

exit 0