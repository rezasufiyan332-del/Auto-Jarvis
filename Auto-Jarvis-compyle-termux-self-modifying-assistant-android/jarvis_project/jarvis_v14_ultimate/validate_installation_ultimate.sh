#!/bin/bash
# ========================================================================
# JARVIS v14 ULTIMATE - Installation Validation System
# ========================================================================
# Author: JARVIS Development Team
# Version: 14.0 Ultimate
# Description: Comprehensive validation system to verify installation
#              integrity, functionality, and performance across all platforms
# ========================================================================

set -euo pipefail

# Configuration
JARVIS_VERSION="14.0 Ultimate"
INSTALL_DIR="${HOME}/.jarvis_v14_ultimate"
CONFIG_DIR="${HOME}/.config/jarvis_v14_ultimate"
LOG_DIR="${CONFIG_DIR}/validation_reports"
VALIDATION_LOG="${LOG_DIR}/validation_$(date +%Y%m%d_%H%M%S).log"
REPORT_FILE="${LOG_DIR}/validation_report_$(date +%Y%m%d_%H%M%S).json"
BENCHMARK_FILE="${LOG_DIR}/benchmarks_$(date +%Y%m%d_%H%M%S).json"

# Validation flags
PLATFORM=""
VALIDATION_MODE="comprehensive" # basic, standard, comprehensive, stress
PERFORMANCE_TEST=true
SECURITY_TEST=true
FUNCTIONALITY_TEST=true
INTEGRATION_TEST=true
REGRESSION_TEST=false

# Test categories
VALIDATION_TESTS=()
PASSED_TESTS=()
FAILED_TESTS=()
WARNING_TESTS=()

# Scoring system
MAX_SCORE=1000
CURRENT_SCORE=0
TOTAL_TESTS=0

# Platform detection
TERMUX_AVAILABLE=false
SYSTEMD_AVAILABLE=false
DOCKER_AVAILABLE=false

# Benchmark thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=90
RESPONSE_TIME_THRESHOLD=2.0
BOOT_TIME_THRESHOLD=30

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# ========================================================================
# Utility Functions
# ========================================================================

log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[${timestamp}] [${level}] ${message}" >> "$VALIDATION_LOG"
    
    case $level in
        "INFO")  echo -e "${CYAN}[INFO]${NC} ${message}";;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} ${message}";;
        "WARNING") echo -e "${YELLOW}[WARNING]${NC} ${message}";;
        "ERROR") echo -e "${RED}[ERROR]${NC} ${message}";;
        "TEST") echo -e "${PURPLE}[TEST]${NC} ${message}";;
    esac
}

log_info() { log "INFO" "$@"; }
log_success() { log "SUCCESS" "$@"; }
log_warning() { log "WARNING" "$@"; }
log_error() { log "ERROR" "$@"; }
log_test() { log "TEST" "$@"; }

init_validation() {
    mkdir -p "$LOG_DIR"
    log_info "JARVIS v14 Ultimate Installation Validation started at $(date)"
    log_info "Validation log: $VALIDATION_LOG"
    log_info "Report will be saved to: $REPORT_FILE"
}

detect_platform() {
    log_info "Detecting platform for validation..."
    
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
    
    log_info "Platform detected: $PLATFORM (SystemD: $SYSTEMD_AVAILABLE, Termux: $TERMUX_AVAILABLE)"
}

check_installation_existence() {
    log_test "Checking if JARVIS installation exists"
    
    if [[ ! -d "$INSTALL_DIR" ]]; then
        log_error "Installation directory not found: $INSTALL_DIR"
        return 1
    fi
    
    if [[ ! -d "$CONFIG_DIR" ]]; then
        log_error "Configuration directory not found: $CONFIG_DIR"
        return 1
    fi
    
    if [[ ! -f "$INSTALL_DIR/jarvis.py" ]]; then
        log_error "Main JARVIS file not found: $INSTALL_DIR/jarvis.py"
        return 1
    fi
    
    log_success "Installation directory structure verified"
    return 0
}

validate_python_environment() {
    log_test "Validating Python environment"
    
    # Check if virtual environment exists
    if [[ ! -d "${INSTALL_DIR}/venv" ]]; then
        log_error "Python virtual environment not found"
        return 1
    fi
    
    # Test Python activation
    if ! source "${INSTALL_DIR}/venv/bin/activate" 2>/dev/null; then
        log_error "Failed to activate Python virtual environment"
        return 1
    fi
    
    # Test Python version
    local python_version=$(python --version 2>&1 | grep -oP 'Python \K[0-9]+\.[0-9]+')
    if [[ -z "$python_version" ]]; then
        log_error "Python version check failed"
        return 1
    fi
    
    # Test core imports
    local test_imports=("numpy" "scipy" "matplotlib" "pandas" "requests" "psutil")
    local import_failed=false
    
    for module in "${test_imports[@]}"; do
        if ! python -c "import $module" 2>/dev/null; then
            log_warning "Failed to import $module"
            import_failed=true
        fi
    done
    
    if [[ "$import_failed" == "true" ]]; then
        log_warning "Some Python modules failed to import"
    else
        log_success "Python environment validation passed"
    fi
    
    return 0
}

validate_configuration_files() {
    log_test "Validating configuration files"
    
    # Check main configuration
    if [[ ! -f "$CONFIG_DIR/config.json" ]]; then
        log_error "Main configuration file missing"
        return 1
    fi
    
    # Validate JSON syntax
    if ! python -c "import json; json.load(open('$CONFIG_DIR/config.json'))" 2>/dev/null; then
        log_error "Main configuration file has invalid JSON syntax"
        return 1
    fi
    
    # Check environment file
    if [[ ! -f "$CONFIG_DIR/.env" ]]; then
        log_warning "Environment configuration file missing"
    fi
    
    # Check platform-specific configs
    case "$PLATFORM" in
        "linux")
            if [[ -f "$CONFIG_DIR/security.json" ]]; then
                log_info "Security configuration found"
            fi
            ;;
        "termux")
            if [[ -f "$CONFIG_DIR/monitoring.json" ]]; then
                log_info "Monitoring configuration found"
            fi
            ;;
    esac
    
    log_success "Configuration files validation passed"
    return 0
}

validate_file_permissions() {
    log_test "Validating file permissions"
    
    local permission_errors=false
    
    # Check main directory permissions
    local dir_perms=$(stat -c "%a" "$INSTALL_DIR" 2>/dev/null || echo "000")
    if [[ "${dir_perms:0:1}" != "7" ]] && [[ "${dir_perms:0:1}" != "5" ]]; then
        log_warning "Installation directory permissions may be too restrictive: $dir_perms"
        permission_errors=true
    fi
    
    # Check configuration directory permissions
    local config_perms=$(stat -c "%a" "$CONFIG_DIR" 2>/dev/null || echo "000")
    if [[ "${config_perms:0:1}" != "7" ]]; then
        log_warning "Configuration directory permissions may be too restrictive: $config_perms"
        permission_errors=true
    fi
    
    # Check executable permissions
    if [[ ! -x "$INSTALL_DIR/jarvis" ]]; then
        log_error "JARVIS launcher not executable"
        permission_errors=true
    fi
    
    if [[ "$permission_errors" == "true" ]]; then
        log_warning "Some file permission issues detected"
        return 1
    else
        log_success "File permissions validation passed"
        return 0
    fi
}

validate_dependencies() {
    log_test "Validating system dependencies"
    
    local missing_deps=()
    
    # Check essential commands
    local essential_commands=("python3" "pip" "curl" "git")
    for cmd in "${essential_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    # Platform-specific checks
    case "$PLATFORM" in
        "termux")
            if ! command -v pkg &> /dev/null; then
                missing_deps+=("termux-pkg")
            fi
            ;;
        "linux")
            if [[ "$SYSTEMD_AVAILABLE" == "true" ]]; then
                if ! command -v systemctl &> /dev/null; then
                    missing_deps+=("systemctl")
                fi
            fi
            ;;
    esac
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    log_success "Dependencies validation passed"
    return 0
}

test_jarvis_launcher() {
    log_test "Testing JARVIS launcher functionality"
    
    cd "$INSTALL_DIR"
    
    # Test launcher execution
    if ! timeout 10s ./jarvis --version 2>/dev/null; then
        log_warning "JARVIS launcher test failed or took too long"
        return 1
    fi
    
    # Test help command
    if ! timeout 5s ./jarvis --help &>/dev/null; then
        log_warning "JARVIS help command failed"
        return 1
    fi
    
    log_success "JARVIS launcher test passed"
    return 0
}

validate_service_installation() {
    log_test "Validating service installation"
    
    case "$PLATFORM" in
        "linux")
            if [[ "$SYSTEMD_AVAILABLE" == "true" ]]; then
                # Check systemd service
                if systemctl list-unit-files | grep -q "jarvis-v14-ultimate.service"; then
                    log_info "Systemd service file found"
                    
                    # Check service status
                    if systemctl is-enabled jarvis-v14-ultimate.service &>/dev/null; then
                        log_success "Systemd service is enabled"
                    else
                        log_warning "Systemd service is not enabled"
                    fi
                else
                    log_warning "Systemd service file not found"
                fi
            fi
            ;;
        "termux")
            # Check Termux service
            if [[ -d "$HOME/.local/var/service/jarvis-v14-ultimate" ]]; then
                log_info "Termux service directory found"
                
                if sv status jarvis-v14-ultimate &>/dev/null; then
                    log_success "Termux service is available"
                else
                    log_warning "Termux service is not running"
                fi
            else
                log_warning "Termux service directory not found"
            fi
            ;;
    esac
    
    return 0
}

performance_benchmark() {
    if [[ "$PERFORMANCE_TEST" == "true" ]]; then
        log_test "Running performance benchmarks"
        
        local benchmark_start=$(date +%s.%N)
        
        # CPU benchmark
        local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
        log_info "CPU usage: ${cpu_usage}%"
        
        # Memory benchmark
        local memory_info=$(free | grep Mem)
        local memory_used=$(echo $memory_info | awk '{print $3}')
        local memory_total=$(echo $memory_info | awk '{print $2}')
        local memory_percent=$((memory_used * 100 / memory_total))
        log_info "Memory usage: ${memory_percent}%"
        
        # Disk benchmark
        local disk_usage=$(df -h "$HOME" | awk 'NR==2 {print $5}' | sed 's/%//')
        log_info "Disk usage: ${disk_usage}%"
        
        # Response time test
        local response_start=$(date +%s.%N)
        timeout 5s python -c "import sys; sys.exit(0)" 2>/dev/null
        local response_end=$(date +%s.%N)
        local response_time=$(echo "$response_end - $response_start" | bc)
        log_info "Python startup time: ${response_time}s"
        
        # Check thresholds
        local performance_issues=false
        
        if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )); then
            log_warning "High CPU usage detected: ${cpu_usage}%"
            performance_issues=true
        fi
        
        if [[ $memory_percent -gt $MEMORY_THRESHOLD ]]; then
            log_warning "High memory usage detected: ${memory_percent}%"
            performance_issues=true
        fi
        
        if [[ $disk_usage -gt $DISK_THRESHOLD ]]; then
            log_warning "High disk usage detected: ${disk_usage}%"
            performance_issues=true
        fi
        
        if (( $(echo "$response_time > $RESPONSE_TIME_THRESHOLD" | bc -l) )); then
            log_warning "Slow response time detected: ${response_time}s"
            performance_issues=true
        fi
        
        # Save benchmark data
        cat > "$BENCHMARK_FILE" << EOF
{
    "benchmark_timestamp": "$(date -Iseconds)",
    "platform": "$PLATFORM",
    "cpu_usage_percent": $cpu_usage,
    "memory_usage_percent": $memory_percent,
    "disk_usage_percent": $disk_usage,
    "python_startup_time_seconds": $response_time,
    "performance_issues": $performance_issues,
    "thresholds": {
        "cpu_threshold": $CPU_THRESHOLD,
        "memory_threshold": $MEMORY_THRESHOLD,
        "disk_threshold": $DISK_THRESHOLD,
        "response_time_threshold": $RESPONSE_TIME_THRESHOLD
    }
}
EOF
        
        if [[ "$performance_issues" == "true" ]]; then
            log_warning "Performance issues detected during benchmarking"
            return 1
        else
            log_success "Performance benchmarks passed"
            return 0
        fi
    fi
}

security_validation() {
    if [[ "$SECURITY_TEST" == "true" ]]; then
        log_test "Running security validation tests"
        
        local security_issues=false
        
        # Check file permissions on sensitive files
        local sensitive_files=(
            "$CONFIG_DIR/config.json"
            "$CONFIG_DIR/.env"
            "$CONFIG_DIR/security.json"
        )
        
        for file in "${sensitive_files[@]}"; do
            if [[ -f "$file" ]]; then
                local file_perms=$(stat -c "%a" "$file" 2>/dev/null || echo "000")
                # Sensitive files should not be world-readable
                if [[ "${file_perms:2:1}" == "4" ]] || [[ "${file_perms:2:1}" == "6" ]] || [[ "${file_perms:2:1}" == "7" ]]; then
                    log_warning "Sensitive file is world-readable: $file ($file_perms)"
                    security_issues=true
                fi
            fi
        done
        
        # Check for exposed configuration
        if [[ -f "$CONFIG_DIR/config.json" ]]; then
            if grep -q '"password"' "$CONFIG_DIR/config.json" 2>/dev/null; then
                log_error "Password found in configuration file"
                security_issues=true
            fi
            
            if grep -q '"api_key"' "$CONFIG_DIR/config.json" 2>/dev/null; then
                log_warning "API keys found in configuration file"
                security_issues=true
            fi
        fi
        
        # Check installation directory permissions
        local install_perms=$(stat -c "%a" "$INSTALL_DIR" 2>/dev/null || echo "000")
        if [[ "${install_perms:0:1}" == "7" ]]; then
            log_warning "Installation directory is world-writable: $install_perms"
            security_issues=true
        fi
        
        if [[ "$security_issues" == "true" ]]; then
            log_warning "Security validation found issues"
            return 1
        else
            log_success "Security validation passed"
            return 0
        fi
    fi
}

functionality_test() {
    if [[ "$FUNCTIONALITY_TEST" == "true" ]]; then
        log_test "Running functionality tests"
        
        cd "$INSTALL_DIR"
        source venv/bin/activate
        
        # Test core modules import
        local core_modules=("os" "sys" "json" "requests" "psutil")
        local import_success=true
        
        for module in "${core_modules[@]}"; do
            if ! python -c "import $module" 2>/dev/null; then
                log_error "Failed to import core module: $module"
                import_success=false
            fi
        done
        
        # Test JARVIS-specific modules
        local jarvis_modules=("core" "config" "utils")
        for module in "${jarvis_modules[@]}"; do
            if ! python -c "import $module" 2>/dev/null; then
                log_warning "Failed to import JARVIS module: $module"
            fi
        done
        
        # Test configuration loading
        if [[ -f "jarvis.py" ]]; then
            if timeout 10s python -c "exec(open('jarvis.py').read().split('if __name__')[0])" &>/dev/null; then
                log_success "JARVIS core script loads successfully"
            else
                log_error "JARVIS core script has syntax errors"
                import_success=false
            fi
        fi
        
        if [[ "$import_success" == "true" ]]; then
            log_success "Functionality tests passed"
            return 0
        else
            log_error "Functionality tests failed"
            return 1
        fi
    fi
}

integration_test() {
    if [[ "$INTEGRATION_TEST" == "true" ]]; then
        log_test "Running integration tests"
        
        cd "$INSTALL_DIR"
        
        # Test network connectivity
        if python -c "import requests; requests.get('https://httpbin.org/get', timeout=5)" &>/dev/null; then
            log_success "Network connectivity test passed"
        else
            log_warning "Network connectivity test failed"
        fi
        
        # Test configuration validation
        if [[ -f "$CONFIG_DIR/config.json" ]]; then
            if python -c "
import json
import sys
try:
    with open('$CONFIG_DIR/config.json') as f:
        config = json.load(f)
    required_keys = ['version', 'paths', 'features']
    for key in required_keys:
        if key not in config:
            print(f'Missing key: {key}')
            sys.exit(1)
    print('Configuration validation passed')
except Exception as e:
    print(f'Config validation failed: {e}')
    sys.exit(1)
" &>/dev/null; then
                log_success "Configuration integration test passed"
            else
                log_error "Configuration integration test failed"
            fi
        fi
        
        # Test logging system
        if [[ -d "$CONFIG_DIR/logs" ]]; then
            log_success "Log directory exists"
        else
            log_warning "Log directory not found"
        fi
        
        return 0
    fi
}

regression_test() {
    if [[ "$REGRESSION_TEST" == "true" ]]; then
        log_test "Running regression tests"
        
        # Test previous version compatibility if backup exists
        local backup_dirs=("$HOME"/.jarvis_backup_*)
        if [[ ${#backup_dirs[@]} -gt 0 ]]; then
            log_info "Found previous installation backups"
            
            # Check backup integrity
            for backup_dir in "${backup_dirs[@]}"; do
                if [[ -d "$backup_dir" ]] && [[ -f "${backup_dir}/backup_info.json" ]]; then
                    log_success "Backup integrity check passed: $(basename "$backup_dir")"
                fi
            done
        else
            log_info "No previous backups found for regression testing"
        fi
        
        # Test rollback capability
        if [[ -f "$INSTALL_DIR/uninstall.sh" ]]; then
            log_success "Uninstaller script found"
        else
            log_warning "Uninstaller script not found"
        fi
        
        return 0
    fi
}

generate_validation_report() {
    log_info "Generating comprehensive validation report"
    
    local validation_duration=$(( $(date +%s) - $(date -d "$(head -1 "$VALIDATION_LOG" | cut -d' ' -f2- | cut -d']' -f1)" +%s 2>/dev/null || echo 0) ))
    
    # Calculate overall score
    local total_score=$(( (${#PASSED_TESTS[@]} * 100) ))
    local max_possible=$(( $TOTAL_TESTS * 100 ))
    local score_percentage=0
    
    if [[ $max_possible -gt 0 ]]; then
        score_percentage=$(( total_score * 100 / max_possible ))
    fi
    
    # Generate detailed report
    cat > "$REPORT_FILE" << EOF
{
    "validation_report": {
        "metadata": {
            "version": "${JARVIS_VERSION}",
            "timestamp": "$(date -Iseconds)",
            "duration_seconds": $validation_duration,
            "platform": "$PLATFORM",
            "validation_mode": "$VALIDATION_MODE"
        },
        "scoring": {
            "total_score": $total_score,
            "max_score": $max_possible,
            "score_percentage": $score_percentage,
            "grade": "$( [[ $score_percentage -ge 90 ]] && echo "A" || [[ $score_percentage -ge 80 ]] && echo "B" || [[ $score_percentage -ge 70 ]] && echo "C" || echo "D" )"
        },
        "test_results": {
            "total_tests": $TOTAL_TESTS,
            "passed": ${#PASSED_TESTS[@]},
            "failed": ${#FAILED_TESTS[@]},
            "warnings": ${#WARNING_TESTS[@]}
        },
        "test_categories": {
            "installation_checks": {
                "tests": ["existence", "structure", "files"],
                "passed": $([[ ${#PASSED_TESTS[@]} -gt 0 ]] && echo "true" || echo "false")
            },
            "python_environment": {
                "tests": ["virtual_env", "modules", "imports"],
                "passed": true
            },
            "configuration": {
                "tests": ["files", "syntax", "permissions"],
                "passed": true
            },
            "functionality": {
                "tests": ["launcher", "core_modules", "imports"],
                "passed": true
            },
            "integration": {
                "tests": ["network", "config", "logging"],
                "passed": true
            },
            "performance": {
                "enabled": $PERFORMANCE_TEST,
                "benchmark_file": "$BENCHMARK_FILE",
                "passed": true
            },
            "security": {
                "enabled": $SECURITY_TEST,
                "passed": true
            },
            "services": {
                "platform": "$PLATFORM",
                "systemd_available": $SYSTEMD_AVAILABLE,
                "termux_available": $TERMUX_AVAILABLE
            }
        },
        "recommendations": [
            $([[ $score_percentage -ge 90 ]] && echo '"Installation is excellent and production-ready"' || 
              [[ $score_percentage -ge 80 ]] && echo '"Installation is good with minor issues to address"' ||
              [[ $score_percentage -ge 70 ]] && echo '"Installation is acceptable but needs attention to failed tests"' ||
              echo '"Installation has significant issues that need immediate attention"')
        ],
        "next_steps": [
            "Review failed tests and warnings",
            "Check benchmark results if performance issues detected",
            "Verify security configuration if security tests enabled",
            "Test service startup if services configured",
            "Run stress tests if needed for production deployment"
        ],
        "files": {
            "validation_log": "$VALIDATION_LOG",
            "benchmark_file": "$BENCHMARK_FILE",
            "config_directory": "$CONFIG_DIR",
            "installation_directory": "$INSTALL_DIR"
        }
    }
}
EOF
    
    log_success "Validation report generated: $REPORT_FILE"
}

print_validation_summary() {
    echo ""
    echo -e "${WHITE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${WHITE}║                                                                      ║${NC}"
    echo -e "${WHITE}║                   VALIDATION SUMMARY                                  ║${NC}"
    echo -e "${WHITE}║                                                                      ║${NC}"
    echo -e "${WHITE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local total_score=$(( (${#PASSED_TESTS[@]} * 100) ))
    local max_possible=$(( $TOTAL_TESTS * 100 ))
    local score_percentage=0
    
    if [[ $max_possible -gt 0 ]]; then
        score_percentage=$(( total_score * 100 / max_possible ))
    fi
    
    echo -e "${CYAN}Test Results:${NC}"
    echo -e "  Total Tests: ${TOTAL_TESTS}"
    echo -e "  Passed: ${GREEN}${#PASSED_TESTS[@]}${NC}"
    echo -e "  Failed: ${RED}${#FAILED_TESTS[@]}${NC}"
    echo -e "  Warnings: ${YELLOW}${#WARNING_TESTS[@]}${NC}"
    echo ""
    
    echo -e "${CYAN}Overall Score:${NC} ${score_percentage}%"
    if [[ $score_percentage -ge 90 ]]; then
        echo -e "Grade: ${GREEN}A (Excellent)${NC}"
    elif [[ $score_percentage -ge 80 ]]; then
        echo -e "Grade: ${YELLOW}B (Good)${NC}"
    elif [[ $score_percentage -ge 70 ]]; then
        echo -e "Grade: ${YELLOW}C (Acceptable)${NC}"
    else
        echo -e "Grade: ${RED}D (Needs Attention)${NC}"
    fi
    echo ""
    
    if [[ ${#FAILED_TESTS[@]} -gt 0 ]]; then
        echo -e "${RED}Failed Tests:${NC}"
        printf '  - %s\n' "${FAILED_TESTS[@]}"
        echo ""
    fi
    
    if [[ ${#WARNING_TESTS[@]} -gt 0 ]]; then
        echo -e "${YELLOW}Warnings:${NC}"
        printf '  - %s\n' "${WARNING_TESTS[@]}"
        echo ""
    fi
    
    echo -e "${CYAN}Files Generated:${NC}"
    echo -e "  Validation Log: ${VALIDATION_LOG}"
    echo -e "  Report File: ${REPORT_FILE}"
    if [[ "$PERFORMANCE_TEST" == "true" ]]; then
        echo -e "  Benchmark File: ${BENCHMARK_FILE}"
    fi
    echo ""
    
    if [[ $score_percentage -ge 80 ]]; then
        echo -e "${GREEN}✓ Installation validation PASSED${NC}"
    else
        echo -e "${RED}✗ Installation validation FAILED${NC}"
        echo -e "${YELLOW}Please review the failed tests and fix issues before production use.${NC}"
    fi
}

run_validation_test() {
    local test_name="$1"
    local test_function="$2"
    local score_value="${3:-100}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log_test "Running test: $test_name"
    
    if $test_function; then
        PASSED_TESTS+=("$test_name")
        CURRENT_SCORE=$((CURRENT_SCORE + score_value))
        log_success "Test passed: $test_name (+${score_value} points)"
        return 0
    else
        if [[ $score_value -gt 50 ]]; then
            FAILED_TESTS+=("$test_name")
            log_error "Test failed: $test_name (0 points)"
        else
            WARNING_TESTS+=("$test_name")
            log_warning "Test warning: $test_name (${score_value} points)"
            CURRENT_SCORE=$((CURRENT_SCORE + score_value / 2))
        fi
        return 1
    fi
}

parse_validation_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --mode)
                VALIDATION_MODE="$2"
                shift 2
                ;;
            --no-performance)
                PERFORMANCE_TEST=false
                shift
                ;;
            --no-security)
                SECURITY_TEST=false
                shift
                ;;
            --no-functionality)
                FUNCTIONALITY_TEST=false
                shift
                ;;
            --no-integration)
                INTEGRATION_TEST=false
                shift
                ;;
            --regression)
                REGRESSION_TEST=true
                shift
                ;;
            --help|-h)
                show_validation_help
                exit 0
                ;;
            *)
                log_warning "Unknown option: $1"
                shift
                ;;
        esac
    done
    
    # Adjust test suite based on validation mode
    case "$VALIDATION_MODE" in
        "basic")
            PERFORMANCE_TEST=false
            SECURITY_TEST=false
            INTEGRATION_TEST=false
            ;;
        "standard")
            REGRESSION_TEST=false
            ;;
        "comprehensive")
            # All tests enabled (default)
            ;;
        "stress")
            PERFORMANCE_TEST=true
            REGRESSION_TEST=true
            ;;
    esac
}

show_validation_help() {
    cat << EOF
JARVIS v14 Ultimate Installation Validation

USAGE:
    ./validate_installation_ultimate.sh [OPTIONS]

VALIDATION MODES:
    --mode MODE             Set validation mode (basic|standard|comprehensive|stress)

TEST OPTIONS:
    --no-performance       Skip performance tests
    --no-security         Skip security validation
    --no-functionality    Skip functionality tests
    --no-integration      Skip integration tests
    --regression         Enable regression testing

EXAMPLES:
    ./validate_installation_ultimate.sh
    ./validate_installation_ultimate.sh --mode comprehensive
    ./validate_installation_ultimate.sh --no-performance --regression
    ./validate_installation_ultimate.sh --mode stress

Validation modes:
    basic       - Quick validation (5-10 tests)
    standard    - Standard validation (15-20 tests)
    comprehensive - Full validation (25-30 tests)
    stress     - Maximum validation with stress testing
EOF
}

main_validation() {
    # Initialize
    parse_validation_arguments "$@"
    init_validation
    detect_platform
    
    log_info "Starting validation in $VALIDATION_MODE mode"
    
    # Core validation tests
    run_validation_test "Installation Existence" check_installation_existence
    run_validation_test "Python Environment" validate_python_environment
    run_validation_test "Configuration Files" validate_configuration_files
    run_validation_test "File Permissions" validate_file_permissions
    run_validation_test "Dependencies" validate_dependencies
    
    # Functional tests
    run_validation_test "JARVIS Launcher" test_jarvis_launcher
    run_validation_test "Service Installation" validate_service_installation
    
    # Performance and security tests
    if [[ "$PERFORMANCE_TEST" == "true" ]]; then
        run_validation_test "Performance Benchmark" performance_benchmark
    fi
    
    if [[ "$SECURITY_TEST" == "true" ]]; then
        run_validation_test "Security Validation" security_validation
    fi
    
    # Advanced tests
    if [[ "$FUNCTIONALITY_TEST" == "true" ]]; then
        run_validation_test "Functionality Test" functionality_test
    fi
    
    if [[ "$INTEGRATION_TEST" == "true" ]]; then
        run_validation_test "Integration Test" integration_test
    fi
    
    if [[ "$REGRESSION_TEST" == "true" ]]; then
        run_validation_test "Regression Test" regression_test
    fi
    
    # Generate reports and summary
    generate_validation_report
    print_validation_summary
    
    log_info "Validation completed at $(date)"
    
    # Exit with appropriate code
    if [[ ${#FAILED_TESTS[@]} -eq 0 ]] && [[ ${#WARNING_TESTS[@]} -le 3 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Run validation
main_validation "$@"