#!/usr/bin/env python3
"""
JARVIS v15 Ultimate - Automated Termux Setup Script
One-click installation and configuration for Android/Termux environment
100% automated setup with error handling and verification
"""

import os
import sys
import json
import time
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_logo():
    """Print JARVIS logo"""
    logo = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    █─▄▄▄▄█▄─▄▄─█─▄▄▄▄─█─▄─▄─█─▄▄▄─█─▄▄▄▄─█─▄▄▄▄█          ║
    ║    █─█▄─██─█─██─█─██▄▀─██─█─█─█─██▄▀─██▄▄▄─█─█▄─██          ║
    ║    █─▄▄▄▄▄█─▄▄▄─█─▀▀▀▄─██▄▀▀─█─▀▀▀▄─█▄▄▄▄─█─▄▄▄▄▄█          ║
    ║                                                              ║
    ║                     JARVIS v15 ULTIMATE                      ║
    ║               100x Advanced AI Assistant                    ║
    ║            100% Termux Compatible • Error Proof              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(f"{Colors.OKCYAN}{logo}{Colors.ENDC}")

def print_step(step: str, description: str):
    """Print step header"""
    print(f"\n{Colors.HEADER}📋 Step: {step}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{description}{Colors.ENDC}")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")

class JarvisSetup:
    """JARVIS Setup Manager"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.start_time = time.time()
        self.setup_log = []
        self.issues_found = []

    def log_step(self, step: str, status: str, details: str = ""):
        """Log setup step"""
        log_entry = {
            'step': step,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.setup_log.append(log_entry)

    def run_command(self, command: List[str], description: str, timeout: int = 60, critical: bool = True) -> Tuple[bool, str]:
        """Run command with error handling"""
        try:
            print(f"🔧 Running: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                print_success(f"{description} completed")
                return True, result.stdout
            else:
                error_msg = f"{description} failed: {result.stderr}"
                if critical:
                    print_error(error_msg)
                else:
                    print_warning(error_msg)
                return False, error_msg

        except subprocess.TimeoutExpired:
            error_msg = f"{description} timed out"
            if critical:
                print_error(error_msg)
            else:
                print_warning(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"{description} error: {e}"
            if critical:
                print_error(error_msg)
            else:
                print_warning(error_msg)
            return False, error_msg

    def check_termux_environment(self) -> bool:
        """Check if running in Termux environment"""
        print_step("Environment Check", "Checking Termux environment")

        # Check for Termux indicators
        termux_indicators = [
            'com.termux' in os.environ.get('PREFIX', ''),
            os.path.exists('/data/data/com.termux'),
            os.path.exists('/data/data/com.termux/files/usr'),
            'termux' in os.environ.get('SHELL', ''),
            os.environ.get('TERMUX_VERSION') is not None
        ]

        is_termux = any(termux_indicators)

        if is_termux:
            print_success("Termux environment detected")
            self.log_step("Environment Check", "SUCCESS", "Termux detected")
        else:
            print_warning("Non-Termux environment detected (development mode)")
            self.log_step("Environment Check", "WARNING", "Non-Termux environment")
            self.issues_found.append("Running in non-Termux environment")

        return True

    def check_python_version(self) -> bool:
        """Check Python version compatibility"""
        print_step("Python Check", "Checking Python version")

        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        if version >= (3, 8):
            print_success(f"Python {version_str} (compatible)")
            self.log_step("Python Check", "SUCCESS", f"Python {version_str}")
            return True
        else:
            print_error(f"Python {version_str} is not supported (requires 3.8+)")
            self.log_step("Python Check", "FAILED", f"Python {version_str}")
            return False

    def update_termux_packages(self) -> bool:
        """Update Termux packages"""
        print_step("Package Update", "Updating Termux packages")

        commands = [
            (['pkg', 'update', '-y'], "Updating package lists"),
            (['pkg', 'upgrade', '-y'], "Upgrading packages")
        ]

        for command, description in commands:
            success, output = self.run_command(command, description, timeout=300)
            if not success:
                self.log_step("Package Update", "FAILED", description)
                return False

        print_success("Termux packages updated")
        self.log_step("Package Update", "SUCCESS", "All packages updated")
        return True

    def install_system_dependencies(self) -> bool:
        """Install system dependencies"""
        print_step("System Dependencies", "Installing required system packages")

        packages = [
            'python', 'termux-api', 'libxml2', 'libxslt', 'clang', 'make', 'git', 'curl', 'wget'
        ]

        # Check if packages are already installed
        missing_packages = []
        for package in packages:
            success, _ = self.run_command(['which', package], f"Checking {package}", timeout=5, critical=False)
            if not success:
                missing_packages.append(package)

        if missing_packages:
            command = ['pkg', 'install', '-y'] + missing_packages
            success, output = self.run_command(command, f"Installing {', '.join(missing_packages)}", timeout=600)
            if not success:
                self.log_step("System Dependencies", "FAILED", f"Failed to install: {missing_packages}")
                return False
        else:
            print_success("All system packages already installed")

        print_success("System dependencies installed")
        self.log_step("System Dependencies", "SUCCESS", f"Installed packages: {packages}")
        return True

    def setup_storage_access(self) -> bool:
        """Setup storage access"""
        print_step("Storage Access", "Setting up storage access")

        # Try to setup storage access
        success, output = self.run_command(
            ['termux-setup-storage'],
            "Setting up storage access",
            timeout=30,
            critical=False
        )

        if success:
            # Check if storage is accessible
            storage_paths = ['/storage/emulated/0', '/sdcard']
            storage_accessible = any(os.path.exists(path) and os.access(path, os.W_OK) for path in storage_paths)

            if storage_accessible:
                print_success("Storage access granted")
                self.log_step("Storage Access", "SUCCESS", "Storage accessible")
                return True
            else:
                print_warning("Storage setup completed but access not verified")
                self.log_step("Storage Access", "PARTIAL", "Setup completed but access not verified")
                self.issues_found.append("Storage access not fully functional")
                return True
        else:
            print_warning("Storage setup failed - manual setup required")
            self.log_step("Storage Access", "FAILED", "Setup command failed")
            self.issues_found.append("Storage access not available")
            return True  # Continue without storage access

    def upgrade_pip(self) -> bool:
        """Upgrade pip to latest version"""
        print_step("Pip Upgrade", "Upgrading pip to latest version")

        success, output = self.run_command(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
            "Upgrading pip",
            timeout=120
        )

        if success:
            print_success("pip upgraded successfully")
            self.log_step("Pip Upgrade", "SUCCESS", "pip upgraded")
            return True
        else:
            print_error("pip upgrade failed")
            self.log_step("Pip Upgrade", "FAILED", "pip upgrade failed")
            return False

    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        print_step("Python Dependencies", "Installing Python packages")

        requirements_file = self.base_path / "requirements_termux_v15.txt"

        if not requirements_file.exists():
            print_error("requirements_termux_v15.txt not found")
            return False

        success, output = self.run_command(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
            "Installing Python dependencies",
            timeout=600  # 10 minutes
        )

        if success:
            print_success("Python dependencies installed")
            self.log_step("Python Dependencies", "SUCCESS", "All dependencies installed")
            return True
        else:
            print_error("Python dependencies installation failed")
            self.log_step("Python Dependencies", "FAILED", "Dependency installation failed")
            return False

    def verify_installation(self) -> bool:
        """Verify installation"""
        print_step("Installation Verification", "Verifying JARVIS installation")

        # Test critical imports
        critical_modules = [
            'aiohttp',
            'asyncio',
            'click',
            'pydantic',
            'cryptography',
            'aiofiles',
            'yaml',
            'dotenv'
        ]

        failed_modules = []
        for module in critical_modules:
            try:
                __import__(module)
                print_success(f"✓ {module}")
            except ImportError as e:
                print_error(f"✗ {module}: {e}")
                failed_modules.append(module)

        if failed_modules:
            print_error(f"Failed to import: {', '.join(failed_modules)}")
            self.log_step("Installation Verification", "FAILED", f"Failed modules: {failed_modules}")
            return False

        # Test Termux-API if available
        success, _ = self.run_command(['which', 'termux-api'], "Checking Termux-API", timeout=5, critical=False)
        if success:
            print_success("Termux-API is available")
        else:
            print_warning("Termux-API not found (optional)")

        print_success("Installation verification completed")
        self.log_step("Installation Verification", "SUCCESS", "All critical modules available")
        return True

    def create_directories(self) -> bool:
        """Create necessary directories"""
        print_step("Directory Setup", "Creating JARVIS directories")

        directories = [
            'data',
            'data/config',
            'data/logs',
            'data/github_learning',
            'data/voice_calling',
            'data/automation',
            'data/features',
            'data/error_proof',
            'backups',
            'temp'
        ]

        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created: {directory}")

        print_success("Directory structure created")
        self.log_step("Directory Setup", "SUCCESS", f"Created {len(directories)} directories")
        return True

    def setup_configuration(self) -> bool:
        """Setup initial configuration"""
        print_step("Configuration Setup", "Setting up JARVIS configuration")

        # Create basic configuration
        config = {
            'jarvis_v15_ultimate': {
                'version': '15.0.0',
                'setup_completed': datetime.now().isoformat(),
                'environment': 'termux' if self.check_termux_environment() else 'development',
                'first_run': True
            },
            'ai_settings': {
                'primary_model': 'anthropic/claude-3-haiku',
                'fallback_models': [
                    'meta-llama/llama-3.1-8b-instruct',
                    'microsoft/wizardlm-2-8x22b',
                    'google/gemma-2-9b-it'
                ],
                'max_tokens': 4000,
                'temperature': 0.7
            },
            'termux_settings': {
                'optimized_for_mobile': True,
                'battery_optimization': True,
                'memory_limit_mb': 256
            }
        }

        config_file = self.base_path / "data" / "config" / "jarvis_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            print_success("Configuration file created")
            self.log_step("Configuration Setup", "SUCCESS", "Basic configuration created")
            return True

        except Exception as e:
            print_error(f"Configuration creation failed: {e}")
            self.log_step("Configuration Setup", "FAILED", str(e))
            return False

    def test_jarvis_startup(self) -> bool:
        """Test JARVIS startup"""
        print_step("Startup Test", "Testing JARVIS startup")

        jarvis_file = self.base_path / "jarvis.py"

        if not jarvis_file.exists():
            print_error("jarvis.py not found")
            return False

        # Try to import and test basic functionality
        try:
            # Test syntax
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', str(jarvis_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print_success("JARVIS syntax check passed")
                self.log_step("Startup Test", "SUCCESS", "Syntax check passed")
                return True
            else:
                print_error(f"JARVIS syntax error: {result.stderr}")
                self.log_step("Startup Test", "FAILED", f"Syntax error: {result.stderr}")
                return False

        except Exception as e:
            print_error(f"JARVIS startup test failed: {e}")
            self.log_step("Startup Test", "FAILED", str(e))
            return False

    def generate_setup_report(self) -> str:
        """Generate setup completion report"""
        end_time = time.time()
        duration = end_time - self.start_time

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    JARVIS v15 Setup Report                     ║
╚══════════════════════════════════════════════════════════════╝

📊 Setup Summary:
   • Duration: {duration:.1f} seconds
   • Status: {'✅ SUCCESS' if not self.issues_found else '⚠️  COMPLETED WITH ISSUES'}
   • Environment: {'Termux' if self.check_termux_environment() else 'Development'}
   • Python: {sys.version.split()[0]}

📋 Steps Completed:
"""

        for log_entry in self.setup_log:
            status_icon = "✅" if log_entry['status'] == "SUCCESS" else "⚠️" if log_entry['status'] == "WARNING" else "❌"
            report += f"   {status_icon} {log_entry['step']}\n"

        if self.issues_found:
            report += "\n⚠️  Issues Found:\n"
            for issue in self.issues_found:
                report += f"   • {issue}\n"

        report += f"""
🚀 Next Steps:
   1. Set your OpenRouter API key:
      export OPENROUTER_API_KEY="your_api_key_here"

   2. Run JARVIS:
      python jarvis.py

   3. Enjoy your 100x advanced AI assistant!

💡 Tips:
   • Grant storage permission: termux-setup-storage
   • Check system status: python jarvis.py status
   • Add features: jarvis> add voice feature
   • Get help: jarvis> help

📁 Important Files:
   • Main program: jarvis.py
   • Configuration: data/config/jarvis_config.json
   • Requirements: requirements_termux_v15.txt
   • Logs: data/logs/

═══════════════════════════════════════════════════════════════
"""

        return report

    def save_setup_log(self):
        """Save setup log"""
        try:
            log_file = self.base_path / "data" / "setup_log.json"
            log_data = {
                'setup_log': self.setup_log,
                'issues_found': self.issues_found,
                'setup_duration': time.time() - self.start_time,
                'timestamp': datetime.now().isoformat()
            }

            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2, default=str)

        except Exception as e:
            print_warning(f"Failed to save setup log: {e}")

    def run_setup(self) -> bool:
        """Run complete setup process"""
        print_logo()
        print_info("Starting JARVIS v15 Ultimate setup...")

        setup_steps = [
            (self.check_termux_environment, "Environment Check"),
            (self.check_python_version, "Python Version Check"),
            (self.update_termux_packages, "Package Update"),
            (self.install_system_dependencies, "System Dependencies"),
            (self.setup_storage_access, "Storage Setup"),
            (self.upgrade_pip, "Pip Upgrade"),
            (self.install_python_dependencies, "Python Dependencies"),
            (self.create_directories, "Directory Setup"),
            (self.setup_configuration, "Configuration Setup"),
            (self.verify_installation, "Installation Verification"),
            (self.test_jarvis_startup, "Startup Test")
        ]

        failed_steps = []

        for step_func, step_name in setup_steps:
            try:
                if not step_func():
                    if step_name in ["Python Version Check", "Python Dependencies", "Startup Test"]:
                        # Critical steps
                        print_error(f"Critical step failed: {step_name}")
                        failed_steps.append(step_name)
                        break
                    else:
                        # Non-critical steps
                        print_warning(f"Non-critical step failed: {step_name}")
            except Exception as e:
                print_error(f"Step {step_name} raised exception: {e}")
                if step_name in ["Python Version Check", "Python Dependencies", "Startup Test"]:
                    failed_steps.append(step_name)
                    break

        # Save setup log
        self.save_setup_log()

        # Generate and display report
        report = self.generate_setup_report()
        print(report)

        # Save report
        try:
            report_file = self.base_path / "SETUP_REPORT.txt"
            with open(report_file, 'w') as f:
                f.write(report)
            print_info(f"Setup report saved to: {report_file}")
        except Exception as e:
            print_warning(f"Failed to save setup report: {e}")

        return len(failed_steps) == 0

def main():
    """Main setup function"""
    setup = JarvisSetup()

    try:
        success = setup.run_setup()

        if success:
            print_success("\n🎉 JARVIS v15 Ultimate setup completed successfully!")
            print_info("Run 'python jarvis.py' to start your AI assistant")
        else:
            print_error("\n❌ JARVIS setup failed. Please check the errors above.")
            sys.exit(1)

    except KeyboardInterrupt:
        print_error("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()