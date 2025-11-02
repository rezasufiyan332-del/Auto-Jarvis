"""
Dependency Manager v15 - Real Termux Dependency Management
Actually manages and fixes dependencies for Termux environment
100% real functionality, no simulation
"""

import os
import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

class DependencyManagerV15:
    """Real dependency management for Termux"""

    def __init__(self):
        self.logger = logging.getLogger("DependencyManager")
        self.installed_packages = set()
        self.failed_packages = set()

    async def check_and_install_dependencies(self) -> Dict[str, Any]:
        """Check and install all required dependencies"""
        try:
            self.logger.info("🔍 Checking and installing dependencies...")

            results = {
                'checked': [],
                'installed': [],
                'failed': [],
                'already_available': []
            }

            # Essential dependencies for JARVIS v15
            essential_deps = {
                'aiohttp': '3.8.0',  # Async HTTP
                'aiofiles': '23.0.0',  # Async file operations
                'click': '8.0.0',  # CLI interface
                'pydantic': '2.0.0',  # Data validation
                'requests': '2.28.0',  # HTTP requests
                'cryptography': '40.0.0',  # Security
                'pyyaml': '6.0',  # YAML parsing
                'python-dotenv': '1.0.0',  # Environment variables
                'regex': '2023.6.0',  # Advanced regex
                'chardet': '5.1.0',  # Encoding detection
                'dateutil': '2.8.0',  # Date handling
            }

            # Optional dependencies (install if possible)
            optional_deps = {
                'psutil': '5.9.0',  # System monitoring
                'httpx': '0.24.0',  # Alternative HTTP client
                'tenacity': '8.2.0',  # Retry logic
                'fuzzywuzzy': '0.18.0',  # Fuzzy string matching
                'jinja2': '3.1.0',  # Template engine
            }

            # Check essential dependencies
            for package, version in essential_deps.items():
                status = await self._check_package(package, version)
                results['checked'].append(package)

                if status['available']:
                    results['already_available'].append(package)
                    self.logger.info(f"✅ {package} already available")
                else:
                    install_result = await self._install_package(package, version)
                    if install_result['success']:
                        results['installed'].append(package)
                        self.logger.info(f"✅ {package} installed successfully")
                    else:
                        results['failed'].append(package)
                        self.failed_packages.add(package)
                        self.logger.error(f"❌ {package} installation failed")

            # Check optional dependencies (non-critical)
            for package, version in optional_deps.items():
                status = await self._check_package(package, version)
                if not status['available']:
                    install_result = await self._install_package(package, version, critical=False)
                    if install_result['success']:
                        results['installed'].append(package)
                        self.logger.info(f"✅ Optional {package} installed")

            return results

        except Exception as e:
            self.logger.error(f"❌ Dependency management failed: {e}")
            return {'error': str(e)}

    async def _check_package(self, package_name: str, min_version: str = None) -> Dict[str, Any]:
        """Check if package is available and meets version requirements"""
        try:
            # Try to import the package
            if package_name == 'python-dotenv':
                import_name = 'dotenv'
            elif package_name == 'chardet':
                import_name = package_name
            elif package_name == 'dateutil':
                import_name = 'python_dateutil'
            elif package_name == 'regex':
                import_name = 're'  # Built-in, always available
            else:
                import_name = package_name.replace('-', '_')

            try:
                module = __import__(import_name)

                # Check version if required
                if min_version and hasattr(module, '__version__'):
                    installed_version = module.__version__
                    if self._version_satisfies(installed_version, min_version):
                        return {'available': True, 'version': installed_version}
                    else:
                        return {'available': False, 'installed_version': installed_version, 'required_version': min_version}
                else:
                    return {'available': True, 'version': 'unknown'}

            except ImportError:
                return {'available': False}

        except Exception as e:
            self.logger.debug(f"Error checking {package_name}: {e}")
            return {'available': False}

    def _version_satisfies(self, installed: str, required: str) -> bool:
        """Check if installed version satisfies requirement"""
        try:
            # Simple version comparison
            installed_parts = [int(x) for x in installed.split('.') if x.isdigit()]
            required_parts = [int(x) for x in required.split('.') if x.isdigit()]

            # Pad shorter version
            while len(installed_parts) < len(required_parts):
                installed_parts.append(0)

            return installed_parts >= required_parts

        except Exception:
            return True  # Assume satisfied if can't compare

    async def _install_package(self, package_name: str, version: str = None, critical: bool = True) -> Dict[str, Any]:
        """Install package using pip"""
        try:
            install_spec = package_name
            if version:
                install_spec = f"{package_name}>={version}"

            cmd = [sys.executable, '-m', 'pip', 'install', install_spec]

            self.logger.info(f"📦 Installing {install_spec}...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180 if critical else 120
            )

            if result.returncode == 0:
                self.installed_packages.add(package_name)
                return {'success': True, 'package': package_name}
            else:
                error_msg = result.stderr or result.stdout
                self.logger.error(f"Failed to install {package_name}: {error_msg}")
                return {'success': False, 'package': package_name, 'error': error_msg}

        except subprocess.TimeoutExpired:
            error_msg = f"Installation of {package_name} timed out"
            self.logger.error(error_msg)
            return {'success': False, 'package': package_name, 'error': error_msg}
        except Exception as e:
            error_msg = f"Installation error for {package_name}: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'package': package_name, 'error': error_msg}

    async def setup_termux_packages(self) -> Dict[str, Any]:
        """Setup Termux-specific packages via pkg"""
        try:
            if not self._is_termux():
                return {'status': 'not_termux', 'message': 'Not running in Termux'}

            self.logger.info("📱 Setting up Termux packages...")

            results = {
                'installed': [],
                'failed': [],
                'skipped': []
            }

            # Essential Termux packages
            termux_packages = [
                'python',
                'termux-api',
                'libxml2',
                'libxslt',
                'clang',
                'make',
                'git',
                'curl',
                'wget'
            ]

            for package in termux_packages:
                if await self._check_termux_package(package):
                    results['skipped'].append(package)
                    self.logger.info(f"✅ {package} already available")
                else:
                    install_result = await self._install_termux_package(package)
                    if install_result['success']:
                        results['installed'].append(package)
                    else:
                        results['failed'].append(package)

            return results

        except Exception as e:
            self.logger.error(f"❌ Termux package setup failed: {e}")
            return {'error': str(e)}

    def _is_termux(self) -> bool:
        """Check if running in Termux"""
        indicators = [
            'com.termux' in os.environ.get('PREFIX', ''),
            os.path.exists('/data/data/com.termux'),
            os.path.exists('/data/data/com.termux/files/usr'),
            'termux' in os.environ.get('SHELL', ''),
            os.environ.get('TERMUX_VERSION') is not None
        ]
        return any(indicators)

    async def _check_termux_package(self, package_name: str) -> bool:
        """Check if Termux package is installed"""
        try:
            result = subprocess.run(
                ['which', package_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _install_termux_package(self, package_name: str) -> Dict[str, Any]:
        """Install Termux package"""
        try:
            self.logger.info(f"📦 Installing Termux package: {package_name}")

            result = subprocess.run(
                ['pkg', 'install', '-y', package_name],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return {'success': True, 'package': package_name}
            else:
                error_msg = result.stderr or result.stdout
                return {'success': False, 'package': package_name, 'error': error_msg}

        except Exception as e:
            return {'success': False, 'package': package_name, 'error': str(e)}

    async def fix_common_issues(self) -> List[str]:
        """Fix common Termux/Python issues"""
        fixes_applied = []

        try:
            # Fix 1: Upgrade pip
            self.logger.info("🔧 Upgrading pip...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
            ], capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                fixes_applied.append("Upgraded pip to latest version")

            # Fix 2: Set environment variables for better performance
            os.environ['PYTHONHASHSEED'] = '0'
            os.environ['PYTHONUNBUFFERED'] = '1'
            fixes_applied.append("Set Python environment variables for performance")

            # Fix 3: Create necessary directories
            dirs_to_create = [
                self.base_path / "data",
                self.base_path / "logs",
                self.base_path / "backups",
                self.base_path / "temp"
            ]

            for dir_path in dirs_to_create:
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    fixes_applied.append(f"Created directory: {dir_path}")

            # Fix 4: Setup storage access if in Termux
            if self._is_termux():
                self.logger.info("🔧 Setting up storage access...")
                result = subprocess.run(
                    ['termux-setup-storage'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    fixes_applied.append("Setup storage access")

            return fixes_applied

        except Exception as e:
            self.logger.error(f"❌ Error fixing common issues: {e}")
            return fixes_applied

    def get_dependency_report(self) -> Dict[str, Any]:
        """Get comprehensive dependency report"""
        return {
            'installed_packages': list(self.installed_packages),
            'failed_packages': list(self.failed_packages),
            'is_termux': self._is_termux(),
            'python_version': sys.version,
            'platform': sys.platform
        }

    @property
    def base_path(self) -> Path:
        """Get base path"""
        return Path(__file__).parent.parent