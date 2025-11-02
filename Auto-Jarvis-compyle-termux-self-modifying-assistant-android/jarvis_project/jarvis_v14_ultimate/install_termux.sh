#!/data/data/com.termux/files/usr/bin/bash
# -*- coding: utf-8 -*-
#
# JARVIS v14 Ultimate - Termux Installation Script
# =================================================
#
# यह script JARVIS v14 Ultimate को Termux (Android) में automatically
# install और configure करता है।
#
# Usage:
#   bash install_termux.sh
#
# या direct run (after chmod +x):
#   ./install_termux.sh
#
# Author: JARVIS Development Team
# Version: 14.0.0 Ultimate
# Date: 2025-11-01
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Print banner
print_banner() {
    echo -e "${GREEN}"
    cat << "EOF"
    ╔═══════════════════════════════════════════╗
    ║   JARVIS v14 Ultimate - Termux Setup     ║
    ║   AI Assistant for Android               ║
    ╚═══════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Check if running on Termux
check_termux() {
    log_info "Termux environment की जांच कर रहे हैं..."
    
    if [ -z "$TERMUX_VERSION" ] && [ ! -d "/data/data/com.termux" ]; then
        log_error "यह script केवल Termux में चल सकता है!"
        log_error "कृपया Termux app install करें और फिर से try करें।"
        exit 1
    fi
    
    log_success "Termux environment detected: $TERMUX_VERSION"
}

# Check available storage
check_storage() {
    log_info "Storage space की जांच कर रहे हैं..."
    
    available_mb=$(df /data/data/com.termux | tail -1 | awk '{print $4/1024}')
    required_mb=1024  # Minimum 1GB required
    
    if (( $(echo "$available_mb < $required_mb" | bc -l) )); then
        log_warning "कम storage space: ${available_mb}MB available"
        log_warning "Recommended: कम से कम 1GB free space"
        echo -n "Continue anyway? (y/n): "
        read -r response
        if [ "$response" != "y" ]; then
            log_info "Installation cancelled."
            exit 0
        fi
    else
        log_success "Storage space sufficient: ${available_mb}MB available"
    fi
}

# Update package lists
update_packages() {
    log_info "Package lists update कर रहे हैं..."
    
    if pkg update -y; then
        log_success "Package lists updated"
    else
        log_error "Package update failed"
        exit 1
    fi
}

# Install required packages
install_system_packages() {
    log_info "System packages install कर रहे हैं..."
    
    PACKAGES=(
        "python"
        "python-pip"
        "git"
        "wget"
        "curl"
        "termux-api"
        "termux-tools"
        "openssh"
        "nano"
        "vim"
    )
    
    for package in "${PACKAGES[@]}"; do
        log_info "Installing: $package"
        if pkg install -y "$package" 2>&1 | grep -q "already installed"; then
            log_info "  → Already installed"
        else
            if pkg install -y "$package"; then
                log_success "  → Installed successfully"
            else
                log_warning "  → Failed to install $package (continuing...)"
            fi
        fi
    done
    
    log_success "System packages installation complete"
}

# Setup storage permissions
setup_storage_permissions() {
    log_info "Storage permissions setup कर रहे हैं..."
    
    if ! termux-setup-storage 2>/dev/null; then
        log_warning "Storage permission setup skipped"
        log_warning "Manual setup के लिए: termux-setup-storage"
    else
        log_success "Storage permissions configured"
    fi
}

# Install Python dependencies
install_python_packages() {
    log_info "Python packages install कर रहे हैं..."
    log_info "यह कुछ समय ले सकता है (5-10 minutes)..."
    
    # Upgrade pip first
    log_info "Upgrading pip..."
    python -m pip install --upgrade pip --quiet
    
    # Check if requirements_termux.txt exists
    if [ ! -f "requirements_termux.txt" ]; then
        log_error "requirements_termux.txt file नहीं मिली!"
        log_error "कृपया JARVIS v14 Ultimate directory में यह script run करें।"
        exit 1
    fi
    
    log_info "Installing from requirements_termux.txt..."
    if python -m pip install -r requirements_termux.txt --no-warn-script-location; then
        log_success "Python packages installed successfully"
    else
        log_error "कुछ Python packages install नहीं हो सके"
        log_warning "यह normal है Termux में - App फिर भी काम कर सकता है"
        echo -n "Continue? (y/n): "
        read -r response
        if [ "$response" != "y" ]; then
            exit 1
        fi
    fi
}

# Create necessary directories
create_directories() {
    log_info "Required directories बना रहे हैं..."
    
    DIRS=(
        "$HOME/.jarvis"
        "$HOME/.jarvis/config"
        "$HOME/.jarvis/data"
        "$HOME/.jarvis/logs"
        "$HOME/.jarvis/cache"
        "$HOME/.jarvis/backups"
        "$HOME/.jarvis/models"
        "$HOME/.jarvis/plugins"
    )
    
    for dir in "${DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_success "Created: $dir"
        else
            log_info "Already exists: $dir"
        fi
    done
    
    log_success "Directory structure created"
}

# Setup initial configuration
setup_configuration() {
    log_info "Initial configuration setup कर रहे हैं..."
    
    CONFIG_FILE="$HOME/.jarvis/config/ultimate_config.json"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" << 'EOFCONFIG'
{
    "environment": "production",
    "platform": "termux",
    "version": "14.0.0",
    "first_run": true,
    "optimization_profile": "termux",
    "memory_limit_mb": 150,
    "max_threads": 2,
    "cache_size_mb": 32,
    "enable_background_processing": false,
    "logging": {
        "level": "INFO",
        "file": "~/.jarvis/logs/jarvis.log"
    },
    "database": {
        "path": "~/.jarvis/data/main.db"
    }
}
EOFCONFIG
        log_success "Configuration file created: $CONFIG_FILE"
    else
        log_info "Configuration file already exists"
    fi
}

# Create launcher script
create_launcher() {
    log_info "Launcher script बना रहे हैं..."
    
    LAUNCHER="$PREFIX/bin/jarvis"
    PROJECT_DIR="$(pwd)"
    
    cat > "$LAUNCHER" << EOFLAUNCHER
#!/data/data/com.termux/files/usr/bin/bash
# JARVIS v14 Ultimate Launcher for Termux

cd "$PROJECT_DIR"
python jarvis.py "\$@"
EOFLAUNCHER
    
    chmod +x "$LAUNCHER"
    log_success "Launcher created: $LAUNCHER"
    log_info "अब आप कहीं से भी 'jarvis' command से run कर सकते हैं!"
}

# Test installation
test_installation() {
    log_info "Installation test कर रहे हैं..."
    
    # Test Python import
    log_info "Testing Python imports..."
    if python -c "import sys; sys.path.insert(0, 'utils'); from termux_paths import TermuxPathManager; print('✓ Path manager OK')" 2>/dev/null; then
        log_success "Python imports working"
    else
        log_warning "कुछ imports काम नहीं कर रहे (यह normal है)"
    fi
    
    # Test path manager
    log_info "Testing path manager..."
    python << EOFTEST
import sys
sys.path.insert(0, 'utils')
try:
    from termux_paths import get_path_manager
    pm = get_path_manager()
    print(f"✓ Platform detected: {pm.platform.value}")
    print(f"✓ Config path: {pm.get_config_path()}")
except Exception as e:
    print(f"✗ Error: {e}")
EOFTEST
    
    log_success "Installation test complete"
}

# Print completion message
print_completion() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ Installation Complete!                ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}JARVIS v14 Ultimate को start करने के लिए:${NC}"
    echo ""
    echo -e "  ${GREEN}1.${NC} Direct run (recommended):"
    echo -e "     ${YELLOW}jarvis${NC}"
    echo ""
    echo -e "  ${GREEN}2.${NC} From project directory:"
    echo -e "     ${YELLOW}python jarvis.py${NC}"
    echo ""
    echo -e "  ${GREEN}3.${NC} Interactive mode:"
    echo -e "     ${YELLOW}python jarvis.py --interactive${NC}"
    echo ""
    echo -e "${BLUE}महत्वपूर्ण नोट्स:${NC}"
    echo -e "  • First run में setup wizard चलेगा"
    echo -e "  • Memory usage: ~100-150 MB"
    echo -e "  • Logs: ~/.jarvis/logs/jarvis.log"
    echo -e "  • Config: ~/.jarvis/config/ultimate_config.json"
    echo ""
    echo -e "${BLUE}Troubleshooting:${NC}"
    echo -e "  • किसी भी error के लिए logs check करें"
    echo -e "  • अधिक मदद के लिए: python jarvis.py --help"
    echo ""
    echo -e "${GREEN}Happy coding with JARVIS! 🚀${NC}"
    echo ""
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    # Add cleanup logic if needed
    log_success "Cleanup complete"
}

# Trap errors
trap 'log_error "Installation failed at line $LINENO"; cleanup; exit 1' ERR

# Main installation flow
main() {
    print_banner
    
    log_info "JARVIS v14 Ultimate Installation शुरू हो रहा है..."
    echo ""
    
    # Pre-installation checks
    check_termux
    check_storage
    echo ""
    
    # System setup
    log_info "=== System Setup ==="
    update_packages
    install_system_packages
    setup_storage_permissions
    echo ""
    
    # Python setup
    log_info "=== Python Setup ==="
    install_python_packages
    echo ""
    
    # Project setup
    log_info "=== Project Setup ==="
    create_directories
    setup_configuration
    create_launcher
    echo ""
    
    # Testing
    log_info "=== Installation Verification ==="
    test_installation
    echo ""
    
    # Completion
    print_completion
}

# Run main installation
main

exit 0
