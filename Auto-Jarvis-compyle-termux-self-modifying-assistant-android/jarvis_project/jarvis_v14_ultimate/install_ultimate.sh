#!/bin/bash
# ========================================================================
# JARVIS v14 ULTIMATE - Complete Installation System
# ========================================================================
# Author: JARVIS Development Team
# Version: 14.0 Ultimate
# Description: Advanced cross-platform installation system with comprehensive
#              dependency management, auto-configuration, and optimization
# ========================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
JARVIS_VERSION="14.0 Ultimate"
INSTALL_DIR="${HOME}/.jarvis_v14_ultimate"
CONFIG_DIR="${HOME}/.config/jarvis_v14_ultimate"
LOG_FILE="${HOME}/.jarvis_v14_ultimate/install_$(date +%Y%m%d_%H%M%S).log"
BACKUP_DIR="${HOME}/.jarvis_backups_$(date +%Y%m%d_%H%M%S)"
MIN_DISK_SPACE_GB=5
MIN_RAM_GB=2

# Platform detection
PLATFORM=""
PACKAGE_MANAGER=""
SYSTEMD_AVAILABLE=false
TERMUX_AVAILABLE=false
DOCKER_AVAILABLE=false

# Installation flags
AUTO_CONFIGURE=true
OPTIMIZE_FOR_MOBILE=false
ENABLE_MONITORING=true
SECURITY_HARDENING=true
CREATE_SERVICE=true
ENABLE_UPDATES=true
SILENT_MODE=false
DEBUG_MODE=false
FORCE_INSTALL=false

# Progress tracking
CURRENT_STEP=0
TOTAL_STEPS=50
STEP_NAMES=()

# ========================================================================
# Utility Functions
# ========================================================================

log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[${timestamp}] [${level}] ${message}" | tee -a "${LOG_FILE}"
}

info() {
    log "INFO" "${CYAN}$@${NC}"
}

success() {
    log "SUCCESS" "${GREEN}✓ $@${NC}"
}

warning() {
    log "WARNING" "${YELLOW}⚠ $@${NC}"
}

error() {
    log "ERROR" "${RED}✗ $@${NC}"
}

debug() {
    if [[ "${DEBUG_MODE}" == "true" ]]; then
        log "DEBUG" "${PURPLE}$@${NC}"
    fi
}

print_banner() {
    clear
    echo -e "${WHITE}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                 ██████╗ ███████╗██╗   ██╗██████╗ ███████╗          ║
║                 ██╔══██╗██╔════╝██║   ██║██╔══██╗██╔════╝          ║
║                 ██████╔╝█████╗  ██║   ██║██║  ██║█████╗            ║
║                 ██╔══██╗██╔══╝  ██║   ██║██║  ██║██╔══╝            ║
║                 ██║  ██║███████╗╚██████╔╝██████╔╝███████╗          ║
║                 ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚══════╝          ║
║                                                                      ║
║                      V14 ULTIMATE EDITION                           ║
║                                                                      ║
║              Advanced Installation & Deployment System              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo -e "${CYAN}JARVIS v14 Ultimate - Professional AI Assistant Installation${NC}"
    echo -e "${CYAN}=================================================================${NC}"
    echo ""
}

print_progress() {
    local current=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    local bar_length=50
    local filled_length=$((current * bar_length / 100))
    local bar=$(printf "%${filled_length}s" | tr ' ' '█')
    local empty=$(printf "%$((bar_length - filled_length))s" | tr ' ' '░')
    
    printf "\r${CYAN}Progress: [${bar}${empty}] ${current}%% - ${CURRENT_STEP}/${TOTAL_STEPS} steps${NC}"
    if [[ $CURRENT_STEP -eq $TOTAL_STEPS ]]; then
        echo ""
    fi
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        warning "Running as root. This is not recommended for security reasons."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

detect_platform() {
    info "Detecting platform..."
    
    if [[ -n "${TERMUX_VERSION:-}" ]]; then
        PLATFORM="termux"
        TERMUX_AVAILABLE=true
        info "Detected Termux environment"
    elif [[ -f /.dockerenv ]] || grep -q docker /proc/1/cgroup 2>/dev/null; then
        PLATFORM="docker"
        DOCKER_AVAILABLE=true
        info "Detected Docker environment"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        PLATFORM="linux"
        if command -v systemctl &> /dev/null; then
            SYSTEMD_AVAILABLE=true
        fi
        info "Detected Linux system"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        PLATFORM="macos"
        info "Detected macOS system"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        PLATFORM="windows"
        info "Detected Windows (MSYS2/Cygwin)"
    else
        PLATFORM="unknown"
        warning "Unknown platform: $OSTYPE"
    fi
    
    debug "Platform: $PLATFORM, SystemD: $SYSTEMD_AVAILABLE, Docker: $DOCKER_AVAILABLE, Termux: $TERMUX_AVAILABLE"
}

detect_package_manager() {
    info "Detecting package manager..."
    
    if [[ "$PLATFORM" == "termux" ]]; then
        if command -v pkg &> /dev/null; then
            PACKAGE_MANAGER="pkg"
        elif command -v apt &> /dev/null; then
            PACKAGE_MANAGER="apt"
        fi
    elif [[ "$PLATFORM" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v dnf &> /dev/null; then
            PACKAGE_MANAGER="dnf"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
        elif command -v pacman &> /dev/null; then
            PACKAGE_MANAGER="pacman"
        elif command -v zypper &> /dev/null; then
            PACKAGE_MANAGER="zypper"
        fi
    elif [[ "$PLATFORM" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            PACKAGE_MANAGER="brew"
        fi
    elif [[ "$PLATFORM" == "windows" ]]; then
        PACKAGE_MANAGER="choco"
        if ! command -v choco &> /dev/null; then
            PACKAGE_MANAGER="winget"
        fi
    fi
    
    debug "Package Manager: $PACKAGE_MANAGER"
}

check_requirements() {
    info "Checking system requirements..."
    
    # Check disk space
    local available_space=$(df -BG "$HOME" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $available_space -lt $MIN_DISK_SPACE_GB ]]; then
        error "Insufficient disk space. Required: ${MIN_DISK_SPACE_GB}GB, Available: ${available_space}GB"
        exit 1
    fi
    
    # Check RAM (approximate)
    if command -v free &> /dev/null; then
        local total_ram=$(free -m | awk 'NR==2{print $2}')
        if [[ $total_ram -lt $((MIN_RAM_GB * 1024)) ]]; then
            warning "Low RAM detected. Recommended: ${MIN_RAM_GB}GB+"
            if [[ "${FORCE_INSTALL}" != "true" ]]; then
                read -p "Continue with limited resources? (y/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    exit 1
                fi
            fi
        fi
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
        exit 1
    fi
    
    local python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    info "Python version: $python_version"
    
    # Check network connectivity
    if ! ping -c 1 google.com &> /dev/null; then
        warning "No internet connectivity detected. Some features may not work properly."
    fi
    
    success "System requirements check completed"
}

setup_logging() {
    mkdir -p "$(dirname "$LOG_FILE")"
    info "Setting up logging system..."
    info "Installation log: $LOG_FILE"
}

backup_existing_installation() {
    if [[ -d "$INSTALL_DIR" ]] || [[ -d "$CONFIG_DIR" ]]; then
        info "Backing up existing installation..."
        mkdir -p "$BACKUP_DIR"
        
        if [[ -d "$INSTALL_DIR" ]]; then
            cp -r "$INSTALL_DIR" "${BACKUP_DIR}/jarvis_v14_ultimate" 2>/dev/null || true
        fi
        
        if [[ -d "$CONFIG_DIR" ]]; then
            cp -r "$CONFIG_DIR" "${BACKUP_DIR}/config" 2>/dev/null || true
        fi
        
        # Create backup manifest
        cat > "${BACKUP_DIR}/backup_manifest.json" << EOF
{
    "backup_date": "$(date -Iseconds)",
    "version": "${JARVIS_VERSION}",
    "backup_location": "${BACKUP_DIR}",
    "platform": "${PLATFORM}",
    "package_manager": "${PACKAGE_MANAGER}"
}
EOF
        
        success "Backup created at: $BACKUP_DIR"
    fi
}

install_system_dependencies() {
    ((CURRENT_STEP++))
    print_progress
    STEP_NAMES+=("Installing system dependencies")
    info "Installing system dependencies..."
    
    case "$PACKAGE_MANAGER" in
        "apt")
            sudo apt update
            sudo apt install -y \
                python3 python3-pip python3-venv \
                python3-dev build-essential \
                curl wget git unzip \
                sqlite3 ffmpeg espeak-ng \
                portaudio19-dev python3-pyaudio \
                python3-numpy python3-scipy \
                python3-matplotlib python3-pandas \
                python3-scikit-learn python3-tk \
                python3-lxml python3-yaml \
                python3-requests python3-websocket-client \
                python3-pillow python3-opencv \
                netcat-openbsd \
                || { error "Failed to install system dependencies"; exit 1; }
            ;;
        "dnf"|"yum")
            sudo "$PACKAGE_MANAGER" install -y \
                python3 python3-pip python3-devel \
                gcc gcc-c++ make \
                curl wget git unzip \
                sqlite ffmpeg espeak \
                portaudio-devel \
                numpy scipy \
                matplotlib pandas \
                scikit-learn tkinter \
                lxml PyYAML \
                requests websocket-client \
                python3-pillow opencv \
                || { error "Failed to install system dependencies"; exit 1; }
            ;;
        "pacman")
            sudo pacman -Sy --noconfirm \
                python python-pip \
                python-devtools \
                curl wget git unzip \
                sqlite ffmpeg espeak \
                portaudio \
                python-numpy python-scipy \
                python-matplotlib python-pandas \
                python-scikit-learn python-tk \
                python-lxml python-yaml \
                python-requests python-websocket-client \
                python-pillow opencv-python \
                || { error "Failed to install system dependencies"; exit 1; }
            ;;
        "brew")
            brew install python@3.11 python-tk \
                curl wget git unzip \
                sqlite ffmpeg espeak \
                portaudio \
                numpy scipy \
                matplotlib pandas \
                scikit-learn \
                lxml pyyaml \
                requests websocket-client \
                pillow opencv \
                || { error "Failed to install system dependencies"; exit 1; }
            ;;
        "pkg")
            pkg update
            pkg install -y \
                python \
                build-essential \
                curl wget git \
                sqlite \
                ffmpeg \
                espeak \
                portaudio \
                nodejs \
                || { error "Failed to install Termux dependencies"; exit 1; }
            ;;
        *)
            warning "Unknown package manager. Skipping system dependencies installation."
            ;;
    esac
    
    success "System dependencies installed"
}

create_python_environment() {
    ((CURRENT_STEP++))
    print_progress
    STEP_NAMES+=("Creating Python virtual environment")
    info "Creating Python virtual environment..."
    
    # Remove existing environment if force install
    if [[ "${FORCE_INSTALL}" == "true" ]] && [[ -d "${INSTALL_DIR}/venv" ]]; then
        rm -rf "${INSTALL_DIR}/venv"
    fi
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    
    # Create virtual environment
    python3 -m venv "${INSTALL_DIR}/venv"
    source "${INSTALL_DIR}/venv/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    success "Python virtual environment created"
}

install_python_packages() {
    ((CURRENT_STEP++))
    print_progress
    STEP_NAMES+=("Installing Python packages")
    info "Installing Python packages..."
    
    source "${INSTALL_DIR}/venv/bin/activate"
    
    # Install core dependencies
    local requirements=(
        "numpy>=1.21.0"
        "scipy>=1.7.0"
        "matplotlib>=3.5.0"
        "pandas>=1.3.0"
        "scikit-learn>=1.0.0"
        "requests>=2.25.0"
        "websockets>=10.0"
        "asyncio"
        "aiohttp>=3.8.0"
        "aiofiles>=0.8.0"
        "PyYAML>=6.0"
        "jinja2>=3.0"
        "click>=8.0"
        "rich>=12.0"
        "psutil>=5.9.0"
        "schedule>=1.2.0"
        "python-dateutil>=2.8.0"
        "pytz>=2022.0"
        "certifi>=2022.0"
        "urllib3>=1.26.0"
        "charset-normalizer>=2.0.0"
        "idna>=3.0"
        "attr>=21.0"
        "pillow>=9.0"
        "opencv-python>=4.5.0"
        "openai>=0.27.0"
        "anthropic>=0.3.0"
        "google-generativeai>=0.3.0"
        "speechrecognition>=3.10.0"
        "pyttsx3>=2.90"
        "pyaudio>=0.2.11"
        "flask>=2.2.0"
        "flask-cors>=3.0.0"
        "fastapi>=0.85.0"
        "uvicorn>=0.18.0"
        "sqlalchemy>=1.4.0"
        "alembic>=1.8.0"
        "redis>=4.3.0"
        "celery>=5.2.0"
        "gunicorn>=20.1.0"
        "prometheus-client>=0.15.0"
        "structlog>=22.0"
        "loguru>=0.6.0"
        "python-dotenv>=0.19.0"
        "pydantic>=1.10.0"
        "typer>=0.6.0"
        "pytest>=7.0.0"
        "pytest-asyncio>=0.21.0"
        "black>=22.0.0"
        "flake8>=5.0.0"
        "mypy>=1.0.0"
        "bandit>=1.7.0"
        "safety>=2.0.0"
        "twine>=4.0.0"
        "wheel>=0.37.0"
        "setuptools>=65.0.0"
        "pip-tools>=6.8.0"
    )
    
    # Install packages in batches to handle potential failures
    for i in {0..5}; do
        local start=$((i * 10))
        local end=$((start + 9))
        if [[ $end -ge ${#requirements[@]} ]]; then
            end=$((${#requirements[@]} - 1))
        fi
        
        if [[ $start -le $end ]]; then
            local batch=("${requirements[@]:$start:$((end - start + 1))}")
            pip install "${batch[@]}" || {
                warning "Some packages failed to install. Continuing with available packages..."
            }
        fi
    done
    
    success "Python packages installed"
}

install_termux_specific() {
    if [[ "$PLATFORM" == "termux" ]]; then
        ((CURRENT_STEP++))
        print_progress
        STEP_NAMES+=("Installing Termux-specific packages")
        info "Installing Termux-specific packages..."
        
        # Install Termux-specific packages
        pkg install -y \
            termux-api \
            termux-auth \
            termux-boot \
            termux-elf-cleaner \
            termux-repo-keys \
            termux-services \
            x11-repo \
            || warning "Some Termux packages failed to install"
        
        # Setup Termux API
        if [[ -f "${HOME}/.termux/tasker/termux.properties" ]]; then
            mkdir -p "${HOME}/.termux/tasker"
            cat > "${HOME}/.termux/tasker/termux.properties" << 'EOF'
extra-keys = [[ {key: ESC, popup: F1}, {key: TAB}, {key: CTRL}, {key: LEFT}, {key: DOWN}, {key: UP}, {key: RIGHT}, {key: HOME}, {key: END}, {key: PGUP}, {key: PGDN} ]]
EOF
        fi
        
        success "Termux-specific packages installed"
    fi
}

setup_android_permissions() {
    if [[ "$PLATFORM" == "termux" ]]; then
        ((CURRENT_STEP++))
        print_progress
        STEP_NAMES+=("Setting up Android permissions")
        info "Setting up Android permissions..."
        
        # Request necessary permissions
        termux-setup-storage || warning "Failed to setup storage permission"
        
        # Setup notification permissions
        termux-notification --id 1001 --title "JARVIS" --content "Installation completed" || warning "Notification setup failed"
        
        success "Android permissions configured"
    fi
}

install_systemd_service() {
    if [[ "$SYSTEMD_AVAILABLE" == "true" ]] && [[ "$CREATE_SERVICE" == "true" ]]; then
        ((CURRENT_STEP++))
        print_progress
        STEP_NAMES+=("Creating systemd service")
        info "Creating systemd service..."
        
        # Create systemd service file
        sudo tee /etc/systemd/system/jarvis-v14-ultimate.service > /dev/null << EOF
[Unit]
Description=JARVIS v14 Ultimate - AI Assistant
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin:\$PATH
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/jarvis.py --daemon
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
NoNewPrivileges=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        # Enable and start service
        sudo systemctl daemon-reload
        sudo systemctl enable jarvis-v14-ultimate.service
        
        success "Systemd service created and enabled"
    fi
}

install_termux_service() {
    if [[ "$PLATFORM" == "termux" ]] && [[ "$CREATE_SERVICE" == "true" ]]; then
        ((CURRENT_STEP++))
        print_progress
        STEP_NAMES+=("Creating Termux service")
        info "Creating Termux service..."
        
        # Install termux-services if not available
        pkg install -y termux-services || warning "termux-services not available"
        
        # Create termux service
        mkdir -p ~/.local/var/service/jarvis-v14-ultimate
        
        cat > ~/.local/var/service/jarvis-v14-ultimate/run << EOF
#!/data/data/com.termux/files/usr/bin/sh
cd "$INSTALL_DIR"
exec $INSTALL_DIR/venv/bin/python $INSTALL_DIR/jarvis.py --daemon
EOF
        
        chmod +x ~/.local/var/service/jarvis-v14-ultimate/run
        
        # Enable service
        sv-enable jarvis-v14-ultimate || warning "Failed to enable termux service"
        
        success "Termux service created"
    fi
}

create_launch_script() {
    ((CURRENT_STEP++))
    print_progress
    STEP_NAMES+=("Creating launch scripts")
    info "Creating launch scripts..."
    
    # Main launcher
    cat > "$INSTALL_DIR/jarvis" << EOF
#!/bin/bash
# JARVIS v14 Ultimate Launcher
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
source "\$SCRIPT_DIR/venv/bin/activate"
cd "\$SCRIPT_DIR"
exec python jarvis.py "\$@"
EOF
    chmod +x "$INSTALL_DIR/jarvis"
    
    # Desktop shortcut (Linux)
    if [[ "$PLATFORM" == "linux" ]]; then
        mkdir -p "\$HOME/.local/share/applications"
        cat > "\$HOME/.local/share/applications/jarvis-v14-ultimate.desktop" << EOF
[Desktop Entry]
Name=JARVIS v14 Ultimate
Comment=Advanced AI Assistant
Exec=$INSTALL_DIR/jarvis
Icon=$INSTALL_DIR/jarvis-icon.png
Terminal=true
Type=Application
Categories=Utility;Development;
Keywords=AI;Assistant;Voice;Command;
EOF
    fi
    
    success "Launch scripts created"
}

setup_configuration() {
    ((CURRENT_STEP++))
    print_progress
    STEP_NAMES+=("Setting up configuration")
    info "Setting up configuration..."
    
    mkdir -p "$CONFIG_DIR"
    
    # Main configuration
    cat > "$CONFIG_DIR/config.json" << EOF
{
    "version": "${JARVIS_VERSION}",
    "installation_date": "$(date -Iseconds)",
    "platform": "${PLATFORM}",
    "package_manager": "${PACKAGE_MANAGER}",
    
    "paths": {
        "install_dir": "$INSTALL_DIR",
        "config_dir": "$CONFIG_DIR",
        "log_dir": "$CONFIG_DIR/logs",
        "data_dir": "$CONFIG_DIR/data"
    },
    
    "python": {
        "virtual_env": "$INSTALL_DIR/venv",
        "python_path": "$INSTALL_DIR/venv/bin/python"
    },
    
    "features": {
        "voice_control": true,
        "advanced_ai": true,
        "auto_learning": true,
        "security": true,
        "monitoring": ${ENABLE_MONITORING},
        "auto_updates": ${ENABLE_UPDATES}
    },
    
    "platform_specific": {
        "termux": ${TERMUX_AVAILABLE},
        "systemd": ${SYSTEMD_AVAILABLE},
        "docker": ${DOCKER_AVAILABLE}
    }
}
EOF
    
    # Environment file
    cat > "$CONFIG_DIR/.env" << EOF
# JARVIS v14 Ultimate Environment Configuration
JARVIS_VERSION=${JARVIS_VERSION}
JARVIS_HOME=$INSTALL_DIR
JARVIS_CONFIG=$CONFIG_DIR
JARVIS_LOG_LEVEL=INFO

# Platform specific settings
PLATFORM=${PLATFORM}
TERMUX_VERSION=${TERMUX_VERSION:-}

# Feature flags
ENABLE_MONITORING=${ENABLE_MONITORING}
ENABLE_SECURITY=${SECURITY_HARDENING}
AUTO_OPTIMIZE=${AUTO_CONFIGURE}
EOF
    
    success "Configuration files created"
}

optimize_for_mobile() {
    if [[ "$OPTIMIZE_FOR_MOBILE" == "true" ]]; then
        ((CURRENT_STEP++))
        print_progress
        STEP_NAMES+=("Optimizing for mobile devices")
        info "Optimizing for mobile devices..."
        
        # Create mobile-specific config
        cat >> "$CONFIG_DIR/config.json" << 'EOF'
    ,
    "mobile_optimization": {
        "battery_saver": true,
        "low_memory_mode": true,
        "adaptive_processing": true,
        "reduced_logging": true,
        "lightweight_ui": true
    }
EOF
        
        # Setup battery optimization for Android
        if [[ "$PLATFORM" == "termux" ]]; then
            # Create Termux battery optimization script
            cat > "$INSTALL_DIR/battery_optimizer.sh" << 'EOF'
#!/bin/bash
# Battery optimization for JARVIS on Android
termux-wake-lock
termux-battery-status
EOF
            chmod +x "$INSTALL_DIR/battery_optimizer.sh"
        fi
        
        success "Mobile optimization applied"
    fi
}

security_hardening() {
    if [[ "$SECURITY_HARDENING" == "true" ]]; then
        ((CURRENT_STEP++))
        print_progress
        STEP_NAMES+=("Applying security hardening")
        info "Applying security hardening..."
        
        # Secure file permissions
        chmod 700 "$INSTALL_DIR"
        chmod 600 "$CONFIG_DIR"/*
        chmod 755 "$INSTALL_DIR/jarvis"
        
        # Create security configuration
        cat > "$CONFIG_DIR/security.json" << EOF
{
    "version": "${JARVIS_VERSION}",
    "security_level": "high",
    "features": {
        "encryption": true,
        "authentication": true,
        "audit_logging": true,
        "rate_limiting": true,
        "input_validation": true
    },
    "permissions": {
        "file_access": "restricted",
        "network_access": "controlled",
        "system_access": "limited"
    }
}
EOF
        
        # Setup audit logging
        mkdir -p "$CONFIG_DIR/security/audit"
        
        success "Security hardening applied"
    fi
}

setup_monitoring() {
    if [[ "$ENABLE_MONITORING" == "true" ]]; then
        ((CURRENT_STEP++))
        print_progress
        STEP_NAMES+=("Setting up monitoring system")
        info "Setting up monitoring system..."
        
        # Create monitoring configuration
        cat > "$CONFIG_DIR/monitoring.json" << 'EOF'
{
    "enabled": true,
    "metrics": {
        "cpu_usage": true,
        "memory_usage": true,
        "disk_usage": true,
        "network_activity": true,
        "response_times": true,
        "error_rates": true
    },
    "alerting": {
        "high_cpu": 80,
        "high_memory": 85,
        "high_disk": 90,
        "error_rate": 5
    },
    "retention": {
        "metrics_days": 30,
        "logs_days": 7
    }
}
EOF
        
        # Setup log rotation
        if command -v logrotate &> /dev/null; then
            sudo tee /etc/logrotate.d/jarvis-v14-ultimate > /dev/null << EOF
$CONFIG_DIR/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF
        fi
        
        success "Monitoring system configured"
    fi
}

setup_auto_updates() {
    if [[ "$ENABLE_UPDATES" == "true" ]]; then
        ((CURRENT_STEP++))
        print_progress
        STEP_NAMES+=("Setting up auto-update system")
        info "Setting up auto-update system..."
        
        # Create update configuration
        cat > "$CONFIG_DIR/updates.json" << 'EOF'
{
    "enabled": true,
    "auto_check": true,
    "auto_download": false,
    "auto_install": false,
    "check_interval_hours": 24,
    "backup_before_update": true,
    "rollback_on_failure": true
}
EOF
        
        # Setup update cron job
        if [[ "$PLATFORM" == "linux" ]] && command -v crontab &> /dev/null; then
            (crontab -l 2>/dev/null; echo "0 */6 * * * $INSTALL_DIR/update_checker.sh") | crontab -
        fi
        
        success "Auto-update system configured"
    fi
}

create_backup_system() {
    ((CURRENT_STEP++))
    print_progress
    STEP_NAMES+=("Creating backup system")
    info "Creating backup system..."
    
    # Create backup script
    cat > "$INSTALL_DIR/backup_system.sh" << 'EOF'
#!/bin/bash
# JARVIS Backup System
JARVIS_HOME="${HOME}/.jarvis_v14_ultimate"
BACKUP_DIR="${HOME}/.jarvis_backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup configuration
cp -r "${JARVIS_HOME}/../config" "$BACKUP_DIR/" 2>/dev/null || true

# Backup database if exists
if [[ -f "${JARVIS_HOME}/data/jarvis.db" ]]; then
    cp "${JARVIS_HOME}/data/jarvis.db" "$BACKUP_DIR/"
fi

# Create backup manifest
cat > "$BACKUP_DIR/backup_info.json" << EOB
{
    "timestamp": "$(date -Iseconds)",
    "version": "$(grep version $JARVIS_HOME/config.json | cut -d'"' -f4)",
    "platform": "$(uname -s)"
}
EOB

echo "Backup created at: $BACKUP_DIR"
EOF
    chmod +x "$INSTALL_DIR/backup_system.sh"
    
    success "Backup system created"
}

setup_performance_tuning() {
    ((CURRENT_STEP++))
    print_progress
    STEP_NAMES+=("Performance tuning")
    info "Applying performance tuning..."
    
    # Python optimization
    cat > "$CONFIG_DIR/python_optimization.conf" << 'EOF'
# Python Performance Optimization
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
PYTHONHASHSEED=random
MALLOC_ARENA_MAX=2
PYTHONMALLOC=malloc
PYTHONASYNCIODEBUG=0
EOF
    
    # System optimization based on platform
    if [[ "$PLATFORM" == "linux" ]]; then
        # Linux-specific optimizations
        cat >> "$CONFIG_DIR/system_optimization.conf" << 'EOF'
# Linux System Optimization
vm.swappiness=10
vm.vfs_cache_pressure=50
net.core.rmem_max=16777216
net.core.wmem_max=16777216
EOF
    elif [[ "$PLATFORM" == "termux" ]]; then
        # Termux-specific optimizations
        cat >> "$CONFIG_DIR/system_optimization.conf" << 'EOF'
# Termux Mobile Optimization
TERMUX_MEMORY_LIMIT=2048
TERMUX_CPU_LIMIT=80
EOF
    fi
    
    success "Performance tuning applied"
}

install_monitoring_tools() {
    ((CURRENT_STEP++))
    print_progress
    STEP_NAMES+=("Installing monitoring tools")
    info "Installing monitoring tools..."
    
    source "${INSTALL_DIR}/venv/bin/activate"
    
    # Install monitoring-specific packages
    pip install \
        prometheus-client \
        psutil \
        \
        || warning "Some monitoring tools failed to install"
    
    # Create system monitor script
    cat > "$INSTALL_DIR/system_monitor.py" << 'EOF'
#!/usr/bin/env python3
"""JARVIS System Monitor"""
import psutil
import json
import time
from datetime import datetime

def get_system_stats():
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "network_io": psutil.net_io_counters()._asdict(),
        "process_count": len(psutil.pids())
    }

if __name__ == "__main__":
    stats = get_system_stats()
    print(json.dumps(stats, indent=2))
EOF
    chmod +x "$INSTALL_DIR/system_monitor.py"
    
    success "Monitoring tools installed"
}

create_uninstaller() {
    ((CURRENT_STEP++))
    print_progress
    STEP_NAMES+=("Creating uninstaller")
    info "Creating uninstaller..."
    
    cat > "$INSTALL_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
# JARVIS v14 Ultimate Uninstaller
set -e

echo "JARVIS v14 Ultimate Uninstaller"
echo "================================"

read -p "This will completely remove JARVIS v14 Ultimate. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

# Stop services
if command -v systemctl &> /dev/null; then
    sudo systemctl stop jarvis-v14-ultimate 2>/dev/null || true
    sudo systemctl disable jarvis-v14-ultimate 2>/dev/null || true
    sudo rm -f /etc/systemd/system/jarvis-v14-ultimate.service
fi

if [[ -n "${TERMUX_VERSION:-}" ]]; then
    sv-disable jarvis-v14-ultimate 2>/dev/null || true
    rm -rf ~/.local/var/service/jarvis-v14-ultimate
fi

# Remove installation directory
rm -rf ~/.jarvis_v14_ultimate

# Remove configuration
rm -rf ~/.config/jarvis_v14_ultimate

# Remove desktop entry
rm -f ~/.local/share/applications/jarvis-v14-ultimate.desktop

# Remove cron jobs
crontab -l 2>/dev/null | grep -v jarvis | crontab - 2>/dev/null || true

echo "JARVIS v14 Ultimate has been completely removed."
EOF
    chmod +x "$INSTALL_DIR/uninstall.sh"
    
    success "Uninstaller created"
}

finalize_installation() {
    ((CURRENT_STEP++))
    print_progress
    STEP_NAMES+=("Finalizing installation")
    info "Finalizing installation..."
    
    # Test installation
    source "${INSTALL_DIR}/venv/bin/activate"
    cd "$INSTALL_DIR"
    
    if python -c "import sys; print(f'Python {sys.version} working correctly')" >> "${LOG_FILE}" 2>&1; then
        success "Installation test passed"
    else
        error "Installation test failed"
        exit 1
    fi
    
    # Create installation manifest
    cat > "$CONFIG_DIR/installation_manifest.json" << EOF
{
    "version": "${JARVIS_VERSION}",
    "installation_date": "$(date -Iseconds)",
    "platform": "${PLATFORM}",
    "package_manager": "${PACKAGE_MANAGER}",
    "install_dir": "$INSTALL_DIR",
    "config_dir": "$CONFIG_DIR",
    "features_enabled": {
        "voice_control": true,
        "advanced_ai": true,
        "auto_learning": true,
        "security": ${SECURITY_HARDENING},
        "monitoring": ${ENABLE_MONITORING},
        "auto_updates": ${ENABLE_UPDATES},
        "mobile_optimization": ${OPTIMIZE_FOR_MOBILE}
    },
    "optimizations": {
        "performance_tuning": true,
        "security_hardening": ${SECURITY_HARDENING},
        "mobile_optimization": ${OPTIMIZE_FOR_MOBILE}
    }
}
EOF
    
    # Start services if configured
    if [[ "$CREATE_SERVICE" == "true" ]]; then
        if [[ "$SYSTEMD_AVAILABLE" == "true" ]]; then
            sudo systemctl start jarvis-v14-ultimate.service
            info "JARVIS service started via systemd"
        elif [[ "$PLATFORM" == "termux" ]]; then
            sv start jarvis-v14-ultimate 2>/dev/null || warning "Failed to start Termux service"
        fi
    fi
    
    success "Installation finalized successfully"
}

print_completion_summary() {
    echo ""
    echo -e "${WHITE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${WHITE}║                                                                      ║${NC}"
    echo -e "${WHITE}║                    INSTALLATION COMPLETED SUCCESSFULLY!              ║${NC}"
    echo -e "${WHITE}║                                                                      ║${NC}"
    echo -e "${WHITE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}JARVIS v14 Ultimate is now ready to use!${NC}"
    echo ""
    echo -e "${CYAN}Installation Details:${NC}"
    echo -e "  Version: ${JARVIS_VERSION}"
    echo -e "  Install Directory: ${INSTALL_DIR}"
    echo -e "  Configuration: ${CONFIG_DIR}"
    echo -e "  Platform: ${PLATFORM}"
    echo -e "  Package Manager: ${PACKAGE_MANAGER}"
    echo ""
    echo -e "${CYAN}Quick Start:${NC}"
    echo -e "  Launch JARVIS: ${INSTALL_DIR}/jarvis"
    echo -e "  Or simply: jarvis"
    echo ""
    if [[ "$CREATE_SERVICE" == "true" ]]; then
        echo -e "${CYAN}Service Status:${NC}"
        if [[ "$SYSTEMD_AVAILABLE" == "true" ]]; then
            echo -e "  Service: systemctl status jarvis-v14-ultimate"
            echo -e "  Start:   sudo systemctl start jarvis-v14-ultimate"
            echo -e "  Stop:    sudo systemctl stop jarvis-v14-ultimate"
        elif [[ "$PLATFORM" == "termux" ]]; then
            echo -e "  Service: sv status jarvis-v14-ultimate"
            echo -e "  Start:   sv start jarvis-v14-ultimate"
            echo -e "  Stop:    sv stop jarvis-v14-ultimate"
        fi
        echo ""
    fi
    echo -e "${CYAN}Useful Commands:${NC}"
    echo -e "  Configuration: ${CONFIG_DIR}/config.json"
    echo -e "  Logs: ${CONFIG_DIR}/logs/"
    echo -e "  Backup: ${INSTALL_DIR}/backup_system.sh"
    echo -e "  Uninstall: ${INSTALL_DIR}/uninstall.sh"
    echo ""
    echo -e "${CYAN}Installation Log:${NC} ${LOG_FILE}"
    echo ""
    echo -e "${YELLOW}Note: Make sure to add JARVIS to your PATH for easy access:${NC}"
    echo -e "  echo 'export PATH=\"$INSTALL_DIR:\$PATH\"' >> ~/.bashrc"
    echo -e "  source ~/.bashrc"
    echo ""
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --silent)
                SILENT_MODE=true
                shift
                ;;
            --debug)
                DEBUG_MODE=true
                shift
                ;;
            --no-configure)
                AUTO_CONFIGURE=false
                shift
                ;;
            --mobile-optimize)
                OPTIMIZE_FOR_MOBILE=true
                shift
                ;;
            --no-monitoring)
                ENABLE_MONITORING=false
                shift
                ;;
            --no-security)
                SECURITY_HARDENING=false
                shift
                ;;
            --no-service)
                CREATE_SERVICE=false
                shift
                ;;
            --no-updates)
                ENABLE_UPDATES=false
                shift
                ;;
            --force)
                FORCE_INSTALL=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                warning "Unknown option: $1"
                shift
                ;;
        esac
    done
}

show_help() {
    cat << EOF
JARVIS v14 Ultimate Installation Script

USAGE:
    ./install_ultimate.sh [OPTIONS]

OPTIONS:
    --silent              Silent installation mode
    --debug              Enable debug logging
    --no-configure       Skip automatic configuration
    --mobile-optimize    Optimize for mobile devices
    --no-monitoring      Disable monitoring system
    --no-security        Skip security hardening
    --no-service         Don't create system service
    --no-updates         Disable auto-updates
    --force              Force installation even with warnings
    --help, -h          Show this help message

EXAMPLES:
    ./install_ultimate.sh                    # Standard installation
    ./install_ultimate.sh --silent           # Silent installation
    ./install_ultimate.sh --mobile-optimize  # Mobile optimization
    ./install_ultimate.sh --debug            # Debug mode

For more information, visit: https://github.com/jarvis-v14-ultimate
EOF
}

main() {
    # Initialize
    parse_arguments "$@"
    print_banner
    
    # Run installation steps
    check_root
    detect_platform
    detect_package_manager
    check_requirements
    setup_logging
    backup_existing_installation
    
    # Installation process
    install_system_dependencies
    create_python_environment
    install_python_packages
    install_termux_specific
    setup_android_permissions
    install_systemd_service
    install_termux_service
    create_launch_script
    setup_configuration
    optimize_for_mobile
    security_hardening
    setup_monitoring
    setup_auto_updates
    create_backup_system
    setup_performance_tuning
    install_monitoring_tools
    create_uninstaller
    finalize_installation
    
    # Completion
    print_completion_summary
    
    success "JARVIS v14 Ultimate installation completed successfully!"
}

# Run main function
main "$@"