#!/bin/bash
# ========================================================================
# JARVIS v14 ULTIMATE - Silent Installation System
# ========================================================================
# Author: JARVIS Development Team
# Version: 14.0 Ultimate
# Description: Silent/Automated installation system for enterprise
#              deployment and batch installations
# ========================================================================

set -euo pipefail

# Silent mode configuration
SILENT_MODE=true
AUTO_YES=true
LOG_TO_FILE=true
PROGRESS_TRACKING=true

# Configuration
JARVIS_VERSION="14.0 Ultimate"
INSTALL_DIR="${HOME}/.jarvis_v14_ultimate"
CONFIG_DIR="${HOME}/.config/jarvis_v14_ultimate"
LOG_FILE="${INSTALL_DIR}/silent_install_$(date +%Y%m%d_%H%M%S).log"
SILENT_CONFIG_FILE="${INSTALL_DIR}/silent_config.json"
ERROR_LOG="${INSTALL_DIR}/silent_errors.log"
SUCCESS_MARKER="${INSTALL_DIR}/installation_complete.marker"

# Platform detection
PLATFORM=""
PACKAGE_MANAGER=""
SYSTEMD_AVAILABLE=false
TERMUX_AVAILABLE=false
DOCKER_AVAILABLE=false

# Installation configuration
INSTALL_TYPE="full" # full, minimal, custom
FEATURE_PROFILE="standard" # minimal, standard, enterprise, mobile
SECURITY_LEVEL="standard" # basic, standard, high, maximum
PERFORMANCE_PROFILE="balanced" # power_save, balanced, performance, maximum

# Default settings
ENABLE_MONITORING=true
ENABLE_SECURITY=true
CREATE_SERVICE=true
ENABLE_AUTO_UPDATES=true
OPTIMIZE_FOR_MOBILE=false
BACKUP_EXISTING=true
VALIDATE_INSTALLATION=true

# Package lists
CORE_PACKAGES=()
OPTIONAL_PACKAGES=()
PLATFORM_PACKAGES=()

# Progress tracking
CURRENT_STEP=0
TOTAL_STEPS=30
STEP_START_TIME=0
STEP_DURATION=0

# ========================================================================
# Utility Functions
# ========================================================================

log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    if [[ "$LOG_TO_FILE" == "true" ]]; then
        echo "[${timestamp}] [${level}] ${message}" >> "$LOG_FILE"
    fi
    
    if [[ "${SILENT_MODE}" != "true" ]]; then
        echo "[${level}] ${message}"
    fi
}

log_info() { log "INFO" "$@"; }
log_success() { log "SUCCESS" "$@"; }
log_warning() { log "WARNING" "$@"; }
log_error() { log "ERROR" "$@"; }
log_debug() { log "DEBUG" "$@"; }

init_silent_logging() {
    mkdir -p "$(dirname "$LOG_FILE")"
    log_info "Silent installation started at $(date)"
    log_info "Installation log: $LOG_FILE"
    log_info "Error log: $ERROR_LOG"
}

record_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $@" >> "$ERROR_LOG"
}

start_step() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    STEP_START_TIME=$(date +%s)
    log_info "Step $CURRENT_STEP/$TOTAL_STEPS: $1"
}

end_step() {
    local step_end_time=$(date +%s)
    STEP_DURATION=$((step_end_time - STEP_START_TIME))
    log_success "Step $CURRENT_STEP completed in ${STEP_DURATION}s: $1"
}

detect_platform() {
    log_info "Detecting platform..."
    
    if [[ -n "${TERMUX_VERSION:-}" ]]; then
        PLATFORM="termux"
        TERMUX_AVAILABLE=true
    elif [[ -f /.dockerenv ]] || grep -q docker /proc/1/cgroup 2>/dev/null; then
        PLATFORM="docker"
        DOCKER_AVAILABLE=true
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        PLATFORM="linux"
        if command -v systemctl &> /dev/null; then
            SYSTEMD_AVAILABLE=true
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        PLATFORM="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        PLATFORM="windows"
    else
        PLATFORM="unknown"
    fi
    
    log_debug "Platform detected: $PLATFORM (systemd: $SYSTEMD_AVAILABLE)"
}

detect_package_manager() {
    log_info "Detecting package manager..."
    
    case "$PLATFORM" in
        "termux")
            if command -v pkg &> /dev/null; then
                PACKAGE_MANAGER="pkg"
            elif command -v apt &> /dev/null; then
                PACKAGE_MANAGER="apt"
            fi
            ;;
        "linux")
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
            ;;
        "macos")
            if command -v brew &> /dev/null; then
                PACKAGE_MANAGER="brew"
            fi
            ;;
        "windows")
            if command -v choco &> /dev/null; then
                PACKAGE_MANAGER="choco"
            elif command -v winget &> /dev/null; then
                PACKAGE_MANAGER="winget"
            fi
            ;;
    esac
    
    log_debug "Package manager: $PACKAGE_MANAGER"
}

validate_system_requirements() {
    log_info "Validating system requirements..."
    
    # Check available disk space (minimum 3GB)
    local available_space=$(df -BG "$HOME" 2>/dev/null | awk 'NR==2 {print $4}' | sed 's/G//' || echo "0")
    if [[ $available_space -lt 3 ]]; then
        log_error "Insufficient disk space. Required: 3GB, Available: ${available_space}GB"
        return 1
    fi
    
    # Check Python availability
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        return 1
    fi
    
    # Check internet connectivity
    if ! ping -c 1 google.com &> /dev/null; then
        log_warning "No internet connectivity detected"
    fi
    
    # Check permissions
    if [[ ! -w "$HOME" ]]; then
        log_error "No write permission to home directory"
        return 1
    fi
    
    log_success "System requirements validation passed"
    return 0
}

configure_silent_installation() {
    log_info "Configuring silent installation parameters..."
    
    # Create installation configuration
    mkdir -p "$INSTALL_DIR"
    
    # Determine feature profile based on platform and resources
    if [[ "$PLATFORM" == "termux" ]] && [[ $OPTIMIZE_FOR_MOBILE == "true" ]]; then
        FEATURE_PROFILE="mobile"
        INSTALL_TYPE="minimal"
    elif [[ "$PLATFORM" == "docker" ]]; then
        INSTALL_TYPE="container"
        FEATURE_PROFILE="docker"
    elif [[ "$PLATFORM" == "linux" ]] && [[ "$SECURITY_LEVEL" == "high" ]]; then
        FEATURE_PROFILE="enterprise"
    fi
    
    log_info "Installation profile: $INSTALL_TYPE (Features: $FEATURE_PROFILE)"
}

backup_existing_installation() {
    if [[ "$BACKUP_EXISTING" == "true" ]] && ([[ -d "$INSTALL_DIR" ]] || [[ -d "$CONFIG_DIR" ]]); then
        log_info "Creating backup of existing installation..."
        
        local backup_timestamp=$(date +%Y%m%d_%H%M%S)
        local backup_dir="${HOME}/.jarvis_backup_${backup_timestamp}"
        
        mkdir -p "$backup_dir"
        
        # Backup existing installation
        [[ -d "$INSTALL_DIR" ]] && cp -r "$INSTALL_DIR" "${backup_dir}/jarvis_v14_ultimate" 2>/dev/null || true
        [[ -d "$CONFIG_DIR" ]] && cp -r "$CONFIG_DIR" "${backup_dir}/config" 2>/dev/null || true
        
        # Create backup manifest
        cat > "${backup_dir}/backup_info.json" << EOF
{
    "backup_date": "$(date -Iseconds)",
    "backup_dir": "$backup_dir",
    "original_version": "${JARVIS_VERSION}",
    "platform": "$PLATFORM",
    "reason": "silent_installation_backup"
}
EOF
        
        log_success "Backup created at: $backup_dir"
    fi
}

install_system_dependencies() {
    start_step "Installing system dependencies"
    
    case "$PACKAGE_MANAGER" in
        "apt")
            export DEBIAN_FRONTEND=noninteractive
            sudo apt update -qq
            sudo apt install -y -qq \
                python3 python3-pip python3-venv python3-dev build-essential \
                curl wget git unzip sqlite3 ffmpeg espeak-ng \
                portaudio19-dev python3-pyaudio python3-numpy python3-scipy \
                python3-matplotlib python3-pandas python3-scikit-learn \
                python3-requests python3-websockets python3-pillow \
                netcat-openbsd ssl-cert ca-certificates \
                || { record_error "Failed to install apt dependencies"; return 1; }
            ;;
        "pkg")
            pkg update -y -qq
            pkg install -y -qq \
                python build-essential curl wget git unzip sqlite \
                ffmpeg espeak portaudio \
                || { record_error "Failed to install pkg dependencies"; return 1; }
            ;;
        "brew")
            brew install python@3.11 curl wget git sqlite ffmpeg \
                portaudio numpy scipy matplotlib pandas \
                || { record_error "Failed to install brew dependencies"; return 1; }
            ;;
        *)
            log_warning "Unknown package manager: $PACKAGE_MANAGER"
            ;;
    esac
    
    end_step "System dependencies installation"
}

create_python_environment() {
    start_step "Creating Python virtual environment"
    
    # Clean existing environment if present
    [[ -d "${INSTALL_DIR}/venv" ]] && rm -rf "${INSTALL_DIR}/venv"
    
    mkdir -p "$INSTALL_DIR"
    python3 -m venv "${INSTALL_DIR}/venv"
    
    # Activate and upgrade pip
    source "${INSTALL_DIR}/venv/bin/activate"
    pip install --upgrade pip setuptools wheel --quiet
    
    end_step "Python virtual environment creation"
}

install_python_packages_silent() {
    start_step "Installing Python packages"
    
    source "${INSTALL_DIR}/venv/bin/activate"
    
    # Core packages for all profiles
    local core_packages=(
        "numpy>=1.21.0"
        "scipy>=1.7.0"
        "matplotlib>=3.5.0"
        "pandas>=1.3.0"
        "requests>=2.25.0"
        "PyYAML>=6.0"
        "psutil>=5.9.0"
        "schedule>=1.2.0"
        "pillow>=9.0"
        "certifi>=2022.0"
        "urllib3>=1.26.0"
        "charset-normalizer>=2.0.0"
        "idna>=3.0"
        "attr>=21.0"
    )
    
    # Feature-specific packages
    case "$FEATURE_PROFILE" in
        "mobile"|"minimal")
            core_packages+=(
                "scikit-learn>=1.0.0"
                "speechrecognition>=3.10.0"
                "pyttsx3>=2.90"
            )
            ;;
        "standard")
            core_packages+=(
                "scikit-learn>=1.0.0"
                "speechrecognition>=3.10.0"
                "pyttsx3>=2.90"
                "flask>=2.2.0"
                "fastapi>=0.85.0"
                "sqlalchemy>=1.4.0"
                "redis>=4.3.0"
                "celery>=5.2.0"
                "prometheus-client>=0.15.0"
            )
            ;;
        "enterprise"|"docker")
            core_packages+=(
                "scikit-learn>=1.0.0"
                "speechrecognition>=3.10.0"
                "pyttsx3>=2.90"
                "flask>=2.2.0"
                "fastapi>=0.85.0"
                "sqlalchemy>=1.4.0"
                "redis>=4.3.0"
                "celery>=5.2.0"
                "prometheus-client>=0.15.0"
                "gunicorn>=20.1.0"
                "structlog>=22.0"
                "loguru>=0.6.0"
                "pytest>=7.0.0"
                "black>=22.0.0"
                "flake8>=5.0.0"
                "mypy>=1.0.0"
            )
            ;;
    esac
    
    # Install packages in batches
    local batch_size=15
    local total_packages=${#core_packages[@]}
    
    for ((i=0; i<total_packages; i+=batch_size)); do
        local end=$((i + batch_size))
        if [[ $end -gt $total_packages ]]; then
            end=$total_packages
        fi
        
        local batch=("${core_packages[@]:$i:$((end - i))}")
        
        # Try installing with error handling
        if ! pip install "${batch[@]}" --quiet 2>> "$ERROR_LOG"; then
            log_warning "Some packages failed to install, continuing with available packages"
        fi
    done
    
    end_step "Python packages installation"
}

configure_termux_specific() {
    if [[ "$PLATFORM" == "termux" ]]; then
        start_step "Configuring Termux-specific features"
        
        # Install Termux API packages
        pkg install -y -qq termux-api termux-services || log_warning "Termux packages installation failed"
        
        # Setup storage permissions
        termux-setup-storage -q 2>/dev/null || true
        
        # Configure Termux services if enabled
        if [[ "$CREATE_SERVICE" == "true" ]]; then
            mkdir -p ~/.local/var/service/jarvis-v14-ultimate
            
            cat > ~/.local/var/service/jarvis-v14-ultimate/run << 'EOF'
#!/data/data/com.termux/files/usr/bin/sh
cd ~/.jarvis_v14_ultimate
exec ~/.jarvis_v14_ultimate/venv/bin/python ~/.jarvis_v14_ultimate/jarvis.py --daemon
EOF
            chmod +x ~/.local/var/service/jarvis-v14-ultimate/run
        fi
        
        end_step "Termux configuration"
    fi
}

create_systemd_service() {
    if [[ "$SYSTEMD_AVAILABLE" == "true" ]] && [[ "$CREATE_SERVICE" == "true" ]]; then
        start_step "Creating systemd service"
        
        sudo tee /etc/systemd/system/jarvis-v14-ultimate.service > /dev/null << EOF
[Unit]
Description=JARVIS v14 Ultimate - Silent Installation
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin:\$PATH
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/jarvis.py --daemon --silent
Restart=always
RestartSec=10
StandardOutput=append:$CONFIG_DIR/service.log
StandardError=append:$CONFIG_DIR/service_error.log

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable jarvis-v14-ultimate.service
        
        end_step "Systemd service creation"
    fi
}

setup_configuration_silent() {
    start_step "Setting up configuration"
    
    mkdir -p "$CONFIG_DIR"
    
    # Main configuration based on profile
    cat > "$CONFIG_DIR/config.json" << EOF
{
    "version": "${JARVIS_VERSION}",
    "installation_type": "$INSTALL_TYPE",
    "feature_profile": "$FEATURE_PROFILE",
    "security_level": "$SECURITY_LEVEL",
    "performance_profile": "$PERFORMANCE_PROFILE",
    "platform": "$PLATFORM",
    "package_manager": "$PACKAGE_MANAGER",
    "installation_date": "$(date -Iseconds)",
    "silent_mode": true,
    
    "paths": {
        "install_dir": "$INSTALL_DIR",
        "config_dir": "$CONFIG_DIR",
        "log_dir": "$CONFIG_DIR/logs"
    },
    
    "features": {
        "voice_control": true,
        "advanced_ai": true,
        "auto_learning": true,
        "monitoring": ${ENABLE_MONITORING},
        "auto_updates": ${ENABLE_AUTO_UPDATES},
        "security": ${ENABLE_SECURITY},
        "service": ${CREATE_SERVICE}
    },
    
    "optimization": {
        "mobile_optimization": ${OPTIMIZE_FOR_MOBILE},
        "performance_tuning": true,
        "security_hardening": ${ENABLE_SECURITY}
    }
}
EOF
    
    # Environment configuration
    cat > "$CONFIG_DIR/.env" << EOF
JARVIS_VERSION=${JARVIS_VERSION}
JARVIS_HOME=$INSTALL_DIR
JARVIS_CONFIG=$CONFIG_DIR
SILENT_MODE=true
PLATFORM=${PLATFORM}
FEATURE_PROFILE=${FEATURE_PROFILE}
SECURITY_LEVEL=${SECURITY_LEVEL}
PERFORMANCE_PROFILE=${PERFORMANCE_PROFILE}
EOF
    
    # Create log directory
    mkdir -p "$CONFIG_DIR/logs"
    
    end_step "Configuration setup"
}

apply_security_hardening() {
    if [[ "$ENABLE_SECURITY" == "true" ]]; then
        start_step "Applying security hardening"
        
        # Secure file permissions
        chmod 700 "$INSTALL_DIR"
        chmod 600 "$CONFIG_DIR"/*
        chmod 755 "$INSTALL_DIR/jarvis"
        
        # Create security configuration
        cat > "$CONFIG_DIR/security.json" << EOF
{
    "security_level": "$SECURITY_LEVEL",
    "silent_mode_security": true,
    "features": {
        "encryption": $( [[ "$SECURITY_LEVEL" == "high" ]] && echo "true" || echo "false" ),
        "authentication": $( [[ "$SECURITY_LEVEL" != "basic" ]] && echo "true" || echo "false" ),
        "audit_logging": true,
        "input_validation": true,
        "rate_limiting": $( [[ "$SECURITY_LEVEL" == "maximum" ]] && echo "true" || echo "false" )
    },
    "permissions": {
        "file_access": "restricted",
        "network_access": "controlled"
    }
}
EOF
        
        end_step "Security hardening"
    fi
}

setup_performance_optimization() {
    start_step "Applying performance optimization"
    
    # Python optimization settings
    cat > "$CONFIG_DIR/python.conf" << 'EOF'
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
PYTHONHASHSEED=random
MALLOC_ARENA_MAX=2
PYTHONMALLOC=malloc
EOF
    
    # Performance profile specific settings
    case "$PERFORMANCE_PROFILE" in
        "power_save")
            cat >> "$CONFIG_DIR/python.conf" << 'EOF'
PYTHONASYNCIODEBUG=0
PYTHONOPTIMIZE=2
EOF
            ;;
        "performance"|"maximum")
            cat >> "$CONFIG_DIR/python.conf" << 'EOF'
PYTHONOPTIMIZE=0
PYTHONDEBUG=0
EOF
            ;;
    esac
    
    # Platform-specific optimizations
    if [[ "$PLATFORM" == "linux" ]] && [[ "$SECURITY_LEVEL" != "maximum" ]]; then
        cat >> "$CONFIG_DIR/system.conf" << 'EOF'
vm.swappiness=10
vm.vfs_cache_pressure=50
net.core.rmem_max=16777216
net.core.wmem_max=16777216
EOF
    fi
    
    end_step "Performance optimization"
}

create_launcher_scripts() {
    start_step "Creating launcher scripts"
    
    # Main launcher
    cat > "$INSTALL_DIR/jarvis" << EOF
#!/bin/bash
# JARVIS v14 Ultimate Silent Launcher
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
source "\$SCRIPT_DIR/venv/bin/activate"
cd "\$SCRIPT_DIR"
source "$CONFIG_DIR/.env"
source "$CONFIG_DIR/python.conf"
exec python jarvis.py "\$@" --silent
EOF
    chmod +x "$INSTALL_DIR/jarvis"
    
    # Service control script
    if [[ "$CREATE_SERVICE" == "true" ]]; then
        cat > "$INSTALL_DIR/service_control.sh" << 'EOF'
#!/bin/bash
# JARVIS Service Control Script
SERVICE_NAME="jarvis-v14-ultimate"

case "$1" in
    start)
        if [[ "$PLATFORM" == "linux" ]]; then
            sudo systemctl start "$SERVICE_NAME"
        elif [[ -n "${TERMUX_VERSION:-}" ]]; then
            sv start jarvis-v14-ultimate
        fi
        ;;
    stop)
        if [[ "$PLATFORM" == "linux" ]]; then
            sudo systemctl stop "$SERVICE_NAME"
        elif [[ -n "${TERMUX_VERSION:-}" ]]; then
            sv stop jarvis-v14-ultimate
        fi
        ;;
    restart)
        if [[ "$PLATFORM" == "linux" ]]; then
            sudo systemctl restart "$SERVICE_NAME"
        elif [[ -n "${TERMUX_VERSION:-}" ]]; then
            sv restart jarvis-v14-ultimate
        fi
        ;;
    status)
        if [[ "$PLATFORM" == "linux" ]]; then
            sudo systemctl status "$SERVICE_NAME"
        elif [[ -n "${TERMUX_VERSION:-}" ]]; then
            sv status jarvis-v14-ultimate
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
EOF
        chmod +x "$INSTALL_DIR/service_control.sh"
    fi
    
    # Quick access script
    cat > "$INSTALL_DIR/quick_launch.sh" << 'EOF'
#!/bin/bash
# Quick JARVIS Launch
export PATH="$HOME/.jarvis_v14_ultimate:$PATH"
exec jarvis "$@"
EOF
    chmod +x "$INSTALL_DIR/quick_launch.sh"
    
    end_step "Launcher scripts creation"
}

setup_monitoring_silent() {
    if [[ "$ENABLE_MONITORING" == "true" ]]; then
        start_step "Setting up monitoring"
        
        # Create monitoring configuration
        cat > "$CONFIG_DIR/monitoring.json" << EOF
{
    "silent_mode": true,
    "retention": "7d",
    "metrics": {
        "cpu_usage": true,
        "memory_usage": true,
        "disk_usage": true,
        "response_times": true
    },
    "alerting": {
        "enabled": $( [[ "$FEATURE_PROFILE" == "enterprise" ]] && echo "true" || echo "false" ),
        "thresholds": {
            "cpu": 80,
            "memory": 85,
            "disk": 90
        }
    }
}
EOF
        
        end_step "Monitoring setup"
    fi
}

validate_silent_installation() {
    if [[ "$VALIDATE_INSTALLATION" == "true" ]]; then
        start_step "Validating installation"
        
        source "${INSTALL_DIR}/venv/bin/activate"
        cd "$INSTALL_DIR"
        
        # Test Python environment
        if ! python -c "import sys; print('Python OK')" >> "$LOG_FILE" 2>&1; then
            record_error "Python environment test failed"
            return 1
        fi
        
        # Test configuration files
        if [[ ! -f "$CONFIG_DIR/config.json" ]]; then
            record_error "Configuration file missing"
            return 1
        fi
        
        # Test launcher
        if [[ ! -x "$INSTALL_DIR/jarvis" ]]; then
            record_error "Launcher script not executable"
            return 1
        fi
        
        end_step "Installation validation"
    fi
}

create_silent_config_file() {
    log_info "Creating silent configuration reference"
    
    cat > "$SILENT_CONFIG_FILE" << EOF
{
    "silent_installation_config": {
        "version": "${JARVIS_VERSION}",
        "installation_date": "$(date -Iseconds)",
        "platform": "$PLATFORM",
        "package_manager": "$PACKAGE_MANAGER",
        "install_type": "$INSTALL_TYPE",
        "feature_profile": "$FEATURE_PROFILE",
        "security_level": "$SECURITY_LEVEL",
        "performance_profile": "$PERFORMANCE_PROFILE",
        "features_enabled": {
            "monitoring": ${ENABLE_MONITORING},
            "security": ${ENABLE_SECURITY},
            "service": ${CREATE_SERVICE},
            "auto_updates": ${ENABLE_AUTO_UPDATES},
            "mobile_optimization": ${OPTIMIZE_FOR_MOBILE}
        },
        "paths": {
            "install_dir": "$INSTALL_DIR",
            "config_dir": "$CONFIG_DIR",
            "log_file": "$LOG_FILE",
            "error_log": "$ERROR_LOG"
        }
    }
}
EOF
}

start_silent_services() {
    if [[ "$CREATE_SERVICE" == "true" ]]; then
        log_info "Starting services in silent mode..."
        
        if [[ "$SYSTEMD_AVAILABLE" == "true" ]]; then
            if sudo systemctl start jarvis-v14-ultimate.service 2>> "$ERROR_LOG"; then
                log_success "Systemd service started"
            else
                log_warning "Failed to start systemd service"
            fi
        elif [[ "$PLATFORM" == "termux" ]]; then
            if sv start jarvis-v14-ultimate 2>> "$ERROR_LOG"; then
                log_success "Termux service started"
            else
                log_warning "Failed to start Termux service"
            fi
        fi
    fi
}

create_completion_marker() {
    log_info "Creating installation completion marker"
    
    cat > "$SUCCESS_MARKER" << EOF
{
    "installation_completed": true,
    "version": "${JARVIS_VERSION}",
    "timestamp": "$(date -Iseconds)",
    "platform": "$PLATFORM",
    "install_type": "$INSTALL_TYPE",
    "feature_profile": "$FEATURE_PROFILE",
    "validation_passed": ${VALIDATE_INSTALLATION},
    "services_started": ${CREATE_SERVICE},
    "silent_mode": true,
    "paths": {
        "installation": "$INSTALL_DIR",
        "configuration": "$CONFIG_DIR",
        "logs": "$LOG_FILE"
    }
}
EOF
    
    # Make marker readable only by owner
    chmod 600 "$SUCCESS_MARKER"
}

generate_silent_install_report() {
    log_info "Generating silent installation report"
    
    local report_file="${INSTALL_DIR}/silent_install_report.json"
    
    cat > "$report_file" << EOF
{
    "silent_installation_report": {
        "installation_summary": {
            "version": "${JARVIS_VERSION}",
            "timestamp": "$(date -Iseconds)",
            "duration_seconds": $(( $(date +%s) - $(date -d "$(head -1 "$LOG_FILE" | cut -d' ' -f2- | cut -d']' -f1)" +%s 2>/dev/null || echo 0) )),
            "success": true,
            "silent_mode": true
        },
        "system_info": {
            "platform": "$PLATFORM",
            "package_manager": "$PACKAGE_MANAGER",
            "python_version": "$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')",
            "user": "$(whoami)",
            "home_directory": "$HOME"
        },
        "configuration": {
            "install_type": "$INSTALL_TYPE",
            "feature_profile": "$FEATURE_PROFILE",
            "security_level": "$SECURITY_LEVEL",
            "performance_profile": "$PERFORMANCE_PROFILE"
        },
        "features": {
            "monitoring_enabled": ${ENABLE_MONITORING},
            "security_hardening": ${ENABLE_SECURITY},
            "service_created": ${CREATE_SERVICE},
            "auto_updates": ${ENABLE_AUTO_UPDATES},
            "mobile_optimization": ${OPTIMIZE_FOR_MOBILE}
        },
        "paths": {
            "installation_directory": "$INSTALL_DIR",
            "configuration_directory": "$CONFIG_DIR",
            "main_log": "$LOG_FILE",
            "error_log": "$ERROR_LOG",
            "success_marker": "$SUCCESS_MARKER"
        },
        "next_steps": [
            "Add JARVIS to PATH: export PATH=\"$INSTALL_DIR:\$PATH\"",
            "Test installation: $INSTALL_DIR/jarvis --version",
            "View configuration: $CONFIG_DIR/config.json",
            "Check logs: $LOG_FILE"
        ]
    }
}
EOF
    
    log_success "Installation report generated: $report_file"
}

parse_silent_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --profile)
                FEATURE_PROFILE="$2"
                shift 2
                ;;
            --security)
                SECURITY_LEVEL="$2"
                shift 2
                ;;
            --performance)
                PERFORMANCE_PROFILE="$2"
                shift 2
                ;;
            --no-monitoring)
                ENABLE_MONITORING=false
                shift
                ;;
            --no-security)
                ENABLE_SECURITY=false
                shift
                ;;
            --no-service)
                CREATE_SERVICE=false
                shift
                ;;
            --no-updates)
                ENABLE_AUTO_UPDATES=false
                shift
                ;;
            --mobile-optimize)
                OPTIMIZE_FOR_MOBILE=true
                shift
                ;;
            --no-backup)
                BACKUP_EXISTING=false
                shift
                ;;
            --no-validate)
                VALIDATE_INSTALLATION=false
                shift
                ;;
            --install-type)
                INSTALL_TYPE="$2"
                shift 2
                ;;
            --help|-h)
                show_silent_help
                exit 0
                ;;
            *)
                log_warning "Unknown option: $1"
                shift
                ;;
        esac
    done
}

show_silent_help() {
    cat << EOF
JARVIS v14 Ultimate Silent Installation

USAGE:
    ./install_silent_ultimate.sh [OPTIONS]

SILENT OPTIONS:
    --profile PROFILE         Set feature profile (minimal|standard|enterprise|mobile)
    --security LEVEL         Set security level (basic|standard|high|maximum)
    --performance PROFILE    Set performance profile (power_save|balanced|performance|maximum)
    --install-type TYPE      Set installation type (full|minimal|container|custom)

FEATURE OPTIONS:
    --no-monitoring          Disable monitoring system
    --no-security           Skip security hardening
    --no-service            Don't create system service
    --no-updates            Disable auto-updates
    --mobile-optimize       Optimize for mobile devices

MAINTENANCE OPTIONS:
    --no-backup             Skip existing installation backup
    --no-validate          Skip post-installation validation
    --help, -h             Show this help message

EXAMPLES:
    ./install_silent_ultimate.sh --profile minimal
    ./install_silent_ultimate.sh --security high --no-monitoring
    ./install_silent_ultimate.sh --mobile-optimize --install-type minimal
    ./install_silent_ultimate.sh --performance maximum --profile enterprise

silent installation is designed for automated deployments and
enterprise environments where user interaction is not available.
EOF
}

main_silent_installation() {
    # Initialize
    parse_silent_arguments "$@"
    
    # Silent installation workflow
    init_silent_logging
    detect_platform
    detect_package_manager
    
    if ! validate_system_requirements; then
        record_error "System requirements validation failed"
        exit 1
    fi
    
    configure_silent_installation
    backup_existing_installation
    install_system_dependencies
    create_python_environment
    install_python_packages_silent
    configure_termux_specific
    create_systemd_service
    setup_configuration_silent
    apply_security_hardening
    setup_performance_optimization
    create_launcher_scripts
    setup_monitoring_silent
    validate_silent_installation
    create_silent_config_file
    start_silent_services
    create_completion_marker
    generate_silent_install_report
    
    log_success "Silent installation completed successfully!"
    log_info "Installation directory: $INSTALL_DIR"
    log_info "Configuration: $CONFIG_DIR"
    log_info "Main log: $LOG_FILE"
    log_info "Installation report: ${INSTALL_DIR}/silent_install_report.json"
}

# Run silent installation
main_silent_installation "$@"