"""
Termux Configuration v15 - Android/Termux Optimization
Complete Android environment configuration and optimization
Performance tuning, permission management, and system integration
"""

import os
import json
import time
import asyncio
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import aiofiles

@dataclass
class TermuxEnvironment:
    """Termux environment information"""
    is_termux: bool
    termux_version: str
    android_version: str
    api_level: int
    architecture: str
    cpu_cores: int
    memory_mb: int
    storage_gb: float
    termux_prefix: str

@dataclass
class PerformanceSettings:
    """Performance optimization settings"""
    max_concurrent_tasks: int
    ai_request_timeout: int
    background_workers: int
    memory_limit_mb: int
    cache_size_mb: int
    enable_compression: bool
    enable_caching: bool

@dataclass
class PermissionConfig:
    """Permission configuration"""
    storage_access: bool
    camera_access: bool
    location_access: bool
    microphone_access: bool
    telephony_access: bool
    sms_access: bool
    contacts_access: bool
    notification_access: bool

class TermuxConfigV15:
    """
    Termux Configuration Management

    Features:
    - Android environment detection and optimization
    - Performance tuning for mobile devices
    - Permission management and setup
    - Resource usage optimization
    - Cross-platform compatibility
    - System integration configuration
    """

    def __init__(self):
        self.logger = logging.getLogger("TermuxConfig")

        # Paths
        self.base_path = Path(__file__).parent.parent
        self.config_path = self.base_path / "data" / "config"
        self.config_file = self.config_path / "termux_config_v15.json"

        # Create directories
        self.config_path.mkdir(parents=True, exist_ok=True)

        # Environment information
        self.environment = None
        self.performance_settings = None
        self.permission_config = None

        # Optimization flags
        self.is_optimized = False
        self.setup_completed = False

    async def initialize(self):
        """Initialize Termux configuration"""
        try:
            # Detect environment
            await self._detect_environment()

            # Load or create configuration
            await self._load_configuration()

            # Apply optimizations
            await self._apply_optimizations()

            # Setup permissions
            await self._setup_permissions()

            self.logger.info("✅ Termux configuration initialized successfully")

        except Exception as e:
            self.logger.error(f"❌ Termux configuration initialization failed: {e}")
            raise

    async def _detect_environment(self):
        """Detect Termux environment and system information"""
        try:
            # Check if running in Termux
            is_termux = self._detect_termux()

            if is_termux:
                # Get Termux information
                termux_version = os.environ.get('TERMUX_VERSION', 'Unknown')
                termux_prefix = os.environ.get('PREFIX', '/data/data/com.termux/files/usr')

                # Get Android information
                android_version = self._get_android_version()
                api_level = self._get_api_level()

                # Get system information
                architecture = self._get_architecture()
                cpu_cores = self._get_cpu_cores()
                memory_mb = self._get_memory_mb()
                storage_gb = self._get_storage_gb()

                self.environment = TermuxEnvironment(
                    is_termux=is_termux,
                    termux_version=termux_version,
                    android_version=android_version,
                    api_level=api_level,
                    architecture=architecture,
                    cpu_cores=cpu_cores,
                    memory_mb=memory_mb,
                    storage_gb=storage_gb,
                    termux_prefix=termux_prefix
                )

                self.logger.info(f"📱 Termux Environment: Android {android_version}, {memory_mb}MB RAM, {storage_gb}GB storage")
            else:
                # Non-Termux environment (development/testing)
                self.environment = TermuxEnvironment(
                    is_termux=False,
                    termux_version="N/A",
                    android_version="N/A",
                    api_level=0,
                    architecture=self._get_architecture(),
                    cpu_cores=self._get_cpu_cores(),
                    memory_mb=self._get_memory_mb(),
                    storage_gb=self._get_storage_gb(),
                    termux_prefix=""
                )

                self.logger.info("💻 Non-Termux environment detected")

        except Exception as e:
            self.logger.error(f"❌ Environment detection failed: {e}")
            # Set default values
            self.environment = TermuxEnvironment(
                is_termux=False, termux_version="Unknown", android_version="Unknown",
                api_level=0, architecture="unknown", cpu_cores=1, memory_mb=1024,
                storage_gb=1.0, termux_prefix=""
            )

    def _detect_termux(self) -> bool:
        """Detect if running in Termux"""
        try:
            # Multiple detection methods
            indicators = [
                'com.termux' in os.environ.get('PREFIX', ''),
                os.path.exists('/data/data/com.termux'),
                os.path.exists('/data/data/com.termux/files/usr'),
                'termux' in os.environ.get('SHELL', ''),
                os.environ.get('TERMUX_VERSION') is not None,
                os.path.exists('/system/bin/app_process') and 'com.termux' in os.environ.get('ANDROID_DATA', '')
            ]

            return any(indicators)

        except Exception:
            return False

    def _get_android_version(self) -> str:
        """Get Android version"""
        try:
            result = subprocess.run(
                ['getprop', 'ro.build.version.release'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        # Try reading from build.prop
        try:
            with open('/system/build.prop', 'r') as f:
                for line in f:
                    if 'ro.build.version.release=' in line:
                        return line.split('=')[1].strip()
        except Exception:
            pass

        return "Unknown"

    def _get_api_level(self) -> int:
        """Get Android API level"""
        try:
            result = subprocess.run(
                ['getprop', 'ro.build.version.sdk'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        except Exception:
            pass

        return 0

    def _get_architecture(self) -> str:
        """Get system architecture"""
        try:
            import platform
            return platform.machine()
        except Exception:
            return "unknown"

    def _get_cpu_cores(self) -> int:
        """Get CPU core count"""
        try:
            import os
            return os.cpu_count() or 1
        except Exception:
            return 1

    def _get_memory_mb(self) -> int:
        """Get available memory in MB"""
        try:
            # Try reading from /proc/meminfo (Linux/Android)
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemTotal:' in line:
                        # Value is in KB
                        kb = int(line.split()[1])
                        return kb // 1024
        except Exception:
            pass

        # Fallback estimate
        return 2048  # 2GB default

    def _get_storage_gb(self) -> float:
        """Get available storage in GB"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            return free // (1024**3)  # GB
        except Exception:
            return 1.0

    async def _load_configuration(self):
        """Load configuration from file or create defaults"""
        try:
            if self.config_file.exists():
                async with aiofiles.open(self.config_file, 'r') as f:
                    data = json.loads(await f.read())

                    # Load performance settings
                    if 'performance' in data:
                        self.performance_settings = PerformanceSettings(**data['performance'])

                    # Load permission config
                    if 'permissions' in data:
                        self.permission_config = PermissionConfig(**data['permissions'])

            # Create default settings if not loaded
            if not self.performance_settings:
                self.performance_settings = self._get_default_performance_settings()

            if not self.permission_config:
                self.permission_config = PermissionConfig(
                    storage_access=False, camera_access=False, location_access=False,
                    microphone_access=False, telephony_access=False, sms_access=False,
                    contacts_access=False, notification_access=False
                )

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load configuration: {e}")
            self.performance_settings = self._get_default_performance_settings()
            self.permission_config = PermissionConfig(
                storage_access=False, camera_access=False, location_access=False,
                microphone_access=False, telephony_access=False, sms_access=False,
                contacts_access=False, notification_access=False
            )

    def _get_default_performance_settings(self) -> PerformanceSettings:
        """Get default performance settings based on environment"""
        if self.environment and self.environment.is_termux:
            # Conservative settings for mobile
            return PerformanceSettings(
                max_concurrent_tasks=min(3, self.environment.cpu_cores),
                ai_request_timeout=30,  # Shorter timeout for mobile
                background_workers=2,
                memory_limit_mb=min(512, self.environment.memory_mb // 2),
                cache_size_mb=50,
                enable_compression=True,
                enable_caching=True
            )
        else:
            # More liberal settings for desktop
            return PerformanceSettings(
                max_concurrent_tasks=5,
                ai_request_timeout=60,
                background_workers=4,
                memory_limit_mb=1024,
                cache_size_mb=200,
                enable_compression=False,
                enable_caching=True
            )

    async def _apply_optimizations(self):
        """Apply performance optimizations"""
        try:
            if self.environment and self.environment.is_termux:
                # Apply Android-specific optimizations
                await self._optimize_android_environment()

                # Set process priority
                await self._set_process_priority()

                # Configure Python for mobile
                await self._configure_python_mobile()

            self.is_optimized = True
            self.logger.info("⚡ Performance optimizations applied")

        except Exception as e:
            self.logger.error(f"❌ Optimization application failed: {e}")

    async def _optimize_android_environment(self):
        """Optimize Android environment"""
        try:
            # Set environment variables for better performance
            optimizations = {
                'PYTHONHASHSEED': '0',  # Consistent hash randomization
                'PYTHONUNBUFFERED': '1',  # Unbuffered output
                'PYTHONDONTWRITEBYTECODE': '1',  # Disable bytecode caching
                'OMP_NUM_THREADS': str(min(4, self.environment.cpu_cores)),  # Limit OpenMP threads
                'MKL_NUM_THREADS': '1',  # Limit MKL threads
                'OPENBLAS_NUM_THREADS': '1',  # Limit OpenBLAS threads
            }

            for var, value in optimizations.items():
                os.environ[var] = value

        except Exception as e:
            self.logger.error(f"❌ Android environment optimization failed: {e}")

    async def _set_process_priority(self):
        """Set process priority for better responsiveness"""
        try:
            if self.environment.is_termux:
                # Try to set nice level (lower priority = more CPU)
                subprocess.run(['renice', '+10', str(os.getpid())], capture_output=True)
        except Exception:
            pass  # Nice command may not be available

    async def _configure_python_mobile(self):
        """Configure Python for mobile environment"""
        try:
            # Configure garbage collection for mobile
            import gc
            gc.set_threshold(700, 10, 10)  # More aggressive GC

            # Configure asyncio for mobile
            if hasattr(asyncio, 'set_event_loop_policy'):
                # Use default event loop policy
                asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

        except Exception as e:
            self.logger.error(f"❌ Python mobile configuration failed: {e}")

    async def _setup_permissions(self):
        """Setup and check permissions"""
        try:
            if not self.environment or not self.environment.is_termux:
                return

            # Check storage access
            self.permission_config.storage_access = await self._check_storage_permission()

            # Check other permissions if Termux-API is available
            if await self._check_termux_api():
                await self._check_android_permissions()

            self.setup_completed = True
            self.logger.info("🔐 Permission setup completed")

        except Exception as e:
            self.logger.error(f"❌ Permission setup failed: {e}")

    async def _check_storage_permission(self) -> bool:
        """Check storage permission"""
        try:
            # Test write access to shared storage
            shared_paths = ['/storage/emulated/0', '/sdcard', '/storage/sdcard0']

            for path in shared_paths:
                if os.path.exists(path) and os.access(path, os.W_OK):
                    return True

            return False
        except Exception:
            return False

    async def _check_termux_api(self) -> bool:
        """Check if Termux-API is available"""
        try:
            result = subprocess.run(
                ['which', 'termux-api'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _check_android_permissions(self):
        """Check Android permissions via Termux-API"""
        try:
            # Test various permissions
            permission_tests = {
                'camera_access': ['termux-camera-info'],
                'location_access': ['termux-location'],
                'telephony_access': ['termux-telephony-cellinfo'],
                'sms_access': ['termux-sms-list', '-l', '1'],
                'contacts_access': ['termux-contact-list'],
                'notification_access': ['termux-notification', '--help']
            }

            for permission, command in permission_tests.items():
                try:
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    setattr(self.permission_config, permission, result.returncode == 0)
                except Exception:
                    setattr(self.permission_config, permission, False)

        except Exception as e:
            self.logger.error(f"❌ Android permissions check failed: {e}")

    async def request_storage_permission(self) -> bool:
        """Request storage permission"""
        try:
            if not self.environment or not self.environment.is_termux:
                return True

            # Run termux-setup-storage
            result = subprocess.run(
                ['termux-setup-storage'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Wait for permission to take effect
                await asyncio.sleep(2)

                # Re-check permission
                self.permission_config.storage_access = await self._check_storage_permission()

                if self.permission_config.storage_access:
                    self.logger.info("✅ Storage permission granted")
                    return True

            self.logger.error("❌ Storage permission request failed")
            return False

        except Exception as e:
            self.logger.error(f"❌ Storage permission request error: {e}")
            return False

    async def save_configuration(self):
        """Save current configuration"""
        try:
            config_data = {
                'environment': asdict(self.environment) if self.environment else None,
                'performance': asdict(self.performance_settings) if self.performance_settings else None,
                'permissions': asdict(self.permission_config) if self.permission_config else None,
                'is_optimized': self.is_optimized,
                'setup_completed': self.setup_completed,
                'last_updated': datetime.now().isoformat()
            }

            async with aiofiles.open(self.config_file, 'w') as f:
                await f.write(json.dumps(config_data, indent=2, default=str))

        except Exception as e:
            self.logger.error(f"❌ Configuration save failed: {e}")

    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        recommendations = []

        if self.environment:
            if self.environment.is_termux:
                if self.environment.memory_mb < 2048:
                    recommendations.append("💾 Low memory detected - consider reducing AI model context windows")
                    recommendations.append("🧹 Enable aggressive cleanup of temporary files")

                if self.environment.storage_gb < 2:
                    recommendations.append("💿 Low storage space - limit cache size and clear old data")
                    recommendations.append("📦 Use external storage for large files")

                if self.environment.cpu_cores < 4:
                    recommendations.append("⚙️ Limited CPU cores - reduce concurrent operations")

                if not self.permission_config.storage_access:
                    recommendations.append("📁 Grant storage permission for full functionality")

                recommendations.append("🔋 Monitor battery usage during long operations")
                recommendations.append("📱 Consider using 'Do Not Disturb' mode during background tasks")
            else:
                recommendations.append("💻 Running in development environment - performance may differ from Android")

        return recommendations

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            status = {
                'environment': {
                    'is_termux': self.environment.is_termux if self.environment else False,
                    'android_version': self.environment.android_version if self.environment else 'N/A',
                    'memory_mb': self.environment.memory_mb if self.environment else 0,
                    'storage_gb': self.environment.storage_gb if self.environment else 0,
                    'cpu_cores': self.environment.cpu_cores if self.environment else 1
                },
                'optimization': {
                    'is_optimized': self.is_optimized,
                    'setup_completed': self.setup_completed,
                    'max_concurrent_tasks': self.performance_settings.max_concurrent_tasks if self.performance_settings else 0,
                    'memory_limit_mb': self.performance_settings.memory_limit_mb if self.performance_settings else 0
                },
                'permissions': asdict(self.permission_config) if self.permission_config else {}
            }

            return status

        except Exception as e:
            self.logger.error(f"❌ System status retrieval failed: {e}")
            return {}

    async def update_performance_settings(self, **kwargs):
        """Update performance settings"""
        try:
            if self.performance_settings:
                for key, value in kwargs.items():
                    if hasattr(self.performance_settings, key):
                        setattr(self.performance_settings, key, value)
                        self.logger.info(f"⚙️ Updated {key}: {value}")

                await self.save_configuration()

        except Exception as e:
            self.logger.error(f"❌ Performance settings update failed: {e}")

    async def get_mobile_optimizations(self) -> Dict[str, Any]:
        """Get mobile-specific optimizations"""
        try:
            if not self.environment or not self.environment.is_termux:
                return {}

            optimizations = {
                'battery_optimization': {
                    'reduced_background_processing': True,
                    'adaptive_timeout': True,
                    'power_saving_mode': False
                },
                'memory_optimization': {
                    'aggressive_gc': True,
                    'cache_limiting': True,
                    'compression_enabled': self.performance_settings.enable_compression
                },
                'network_optimization': {
                    'request_timeout': self.performance_settings.ai_request_timeout,
                    'retry_logic': True,
                    'offline_mode_available': True
                },
                'ui_optimization': {
                    'progressive_loading': True,
                    'minimal_animations': True,
                    'text_based_interface': True
                }
            }

            return optimizations

        except Exception as e:
            self.logger.error(f"❌ Mobile optimizations retrieval failed: {e}")
            return {}

    async def shutdown(self):
        """Shutdown Termux configuration"""
        try:
            # Save configuration
            await self.save_configuration()

            self.logger.info("✅ Termux configuration shutdown complete")

        except Exception as e:
            self.logger.error(f"❌ Termux configuration shutdown failed: {e}")