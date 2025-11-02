"""
Termux Controller v15 - Enhanced Android Integration
Complete Termux-API integration with Android features
Storage access, notifications, system control, and device management
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

@dataclass
class DeviceInfo:
    """Android device information"""
    model: str
    android_version: str
    api_level: int
    battery_level: int
    storage_info: Dict[str, Any]
    network_info: Dict[str, Any]

@dataclass
class StorageStats:
    """Storage statistics"""
    total_space: int
    free_space: int
    used_space: int
    available_space: int

class TermuxControllerV15:
    """
    Enhanced Termux Controller with Android Integration

    Features:
    - Termux-API integration for Android features
    - Storage access and management
    - Notification system
    - Battery and system monitoring
    - Network connectivity management
    - Device information retrieval
    - Permission handling
    - Cross-platform compatibility
    """

    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger

        # Paths
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / "data" / "termux"
        self.storage_path = self.data_path / "storage"

        # Create directories
        for path in [self.data_path, self.storage_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Termux detection
        self.is_termux = self._detect_termux()
        self.api_available = False

        # Device information cache
        self.device_info = None
        self.last_update = None

        # Permission tracking
        self.permissions = {
            'storage': False,
            'camera': False,
            'location': False,
            'microphone': False,
            'telephony': False,
            'sms': False,
            'contacts': False
        }

        # Feature availability
        self.features = {
            'notifications': False,
            'tts': False,
            'stt': False,
            'telephony': False,
            'sms': False,
            'camera': False,
            'location': False,
            'wifi': False,
            'battery': False
        }

    async def initialize(self):
        """Initialize Termux controller"""
        try:
            if self.is_termux:
                # Check Termux-API availability
                await self._check_termux_api()

                if self.api_available:
                    # Initialize features
                    await self._initialize_features()

                    # Get device information
                    await self._update_device_info()

                    # Check permissions
                    await self._check_permissions()

                    self.logger.info("✅ Termux Controller v15 initialized with full Android integration")
                else:
                    self.logger.warning("⚠️ Termux-API not available, limited functionality")
            else:
                self.logger.info("ℹ️ Running in non-Termux environment")

        except Exception as e:
            self.logger.error(f"❌ Termux Controller initialization failed: {e}")
            raise

    def _detect_termux(self) -> bool:
        """Detect if running in Termux environment"""
        try:
            # Check environment variables
            termux_prefix = os.environ.get('PREFIX', '')
            com_termux_path = '/data/data/com.termux/files'

            # Multiple detection methods
            indicators = [
                'com.termux' in termux_prefix,
                os.path.exists('/data/data/com.termux'),
                os.path.exists(com_termux_path),
                'termux' in os.environ.get('SHELL', ''),
                os.environ.get('TERMUX_VERSION') is not None
            ]

            return any(indicators)

        except Exception as e:
            self.logger.debug(f"Termux detection error: {e}")
            return False

    async def _check_termux_api(self):
        """Check if Termux-API is available"""
        try:
            if not self.is_termux:
                self.api_available = False
                return

            # Check if termux-api command exists
            result = subprocess.run(
                ['which', 'termux-api'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Test API functionality
                test_result = subprocess.run(
                    ['termux-api-status'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                self.api_available = test_result.returncode == 0

                if self.api_available:
                    self.logger.info("✅ Termux-API is available and functional")
                else:
                    self.logger.warning("⚠️ Termux-API found but not functional")
            else:
                self.logger.warning("⚠️ Termux-API not installed")
                self.api_available = False

        except subprocess.TimeoutExpired:
            self.logger.warning("⚠️ Termux-API check timed out")
            self.api_available = False
        except Exception as e:
            self.logger.error(f"❌ Termux-API check failed: {e}")
            self.api_available = False

    async def _initialize_features(self):
        """Initialize available Termux features"""
        try:
            if not self.api_available:
                return

            # Test each feature
            feature_commands = {
                'notifications': ['termux-notification', '--help'],
                'tts': ['termux-tts-speak', '--help'],
                'stt': ['termux-speech-to-text', '--help'],
                'telephony': ['termux-telephony-call', '--help'],
                'sms': ['termux-sms-list', '--help'],
                'camera': ['termux-camera-photo', '--help'],
                'location': ['termux-location', '--help'],
                'wifi': ['termux-wifi-connectioninfo', '--help'],
                'battery': ['termux-battery', '--help']
            }

            for feature, command in feature_commands.items():
                try:
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    self.features[feature] = result.returncode == 0
                except Exception:
                    self.features[feature] = False

            self.logger.info(f"🔧 Features initialized: {sum(self.features.values())}/{len(self.features)} available")

        except Exception as e:
            self.logger.error(f"❌ Feature initialization failed: {e}")

    async def _update_device_info(self):
        """Update device information"""
        try:
            if not self.api_available:
                return

            # Get basic device info
            device_info = {}

            # Battery information
            if self.features['battery']:
                try:
                    result = subprocess.run(
                        ['termux-battery'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        battery_data = json.loads(result.stdout)
                        device_info['battery'] = battery_data
                except Exception as e:
                    self.logger.debug(f"Battery info failed: {e}")

            # Storage information
            storage_info = await self.get_storage_info()
            device_info['storage'] = storage_info

            # Network information
            if self.features['wifi']:
                try:
                    result = subprocess.run(
                        ['termux-wifi-connectioninfo'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        network_data = json.loads(result.stdout)
                        device_info['network'] = network_data
                except Exception as e:
                    self.logger.debug(f"Network info failed: {e}")

            # Android version info
            try:
                result = subprocess.run(
                    ['getprop', 'ro.build.version.release'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    device_info['android_version'] = result.stdout.strip()

                result = subprocess.run(
                    ['getprop', 'ro.product.model'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    device_info['model'] = result.stdout.strip()

            except Exception as e:
                self.logger.debug(f"Android version info failed: {e}")

            self.device_info = device_info
            self.last_update = datetime.now()

        except Exception as e:
            self.logger.error(f"❌ Device info update failed: {e}")

    async def _check_permissions(self):
        """Check Android permissions"""
        try:
            if not self.api_available:
                return

            # Test permissions by trying basic operations
            permission_tests = {
                'storage': self._test_storage_permission,
                'telephony': self._test_telephony_permission,
                'sms': self._test_sms_permission,
                'camera': self._test_camera_permission,
                'location': self._test_location_permission
            }

            for permission, test_func in permission_tests.items():
                try:
                    self.permissions[permission] = await test_func()
                except Exception as e:
                    self.logger.debug(f"Permission test {permission} failed: {e}")
                    self.permissions[permission] = False

        except Exception as e:
            self.logger.error(f"❌ Permission check failed: {e}")

    async def _test_storage_permission(self) -> bool:
        """Test storage permission"""
        try:
            # Try to write to shared storage
            shared_storage = Path('/storage/emulated/0')
            if shared_storage.exists():
                test_file = shared_storage / '.jarvis_test'
                test_file.write_text('test')
                test_file.unlink()
                return True
            return False
        except Exception:
            return False

    async def _test_telephony_permission(self) -> bool:
        """Test telephony permission"""
        try:
            if not self.features['telephony']:
                return False

            result = subprocess.run(
                ['termux-telephony-cellinfo'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _test_sms_permission(self) -> bool:
        """Test SMS permission"""
        try:
            if not self.features['sms']:
                return False

            result = subprocess.run(
                ['termux-sms-list', '-l', '1'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _test_camera_permission(self) -> bool:
        """Test camera permission"""
        try:
            if not self.features['camera']:
                return False

            # Just check if we can get camera info (don't take photo)
            result = subprocess.run(
                ['termux-camera-info'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _test_location_permission(self) -> bool:
        """Test location permission"""
        try:
            if not self.features['location']:
                return False

            result = subprocess.run(
                ['termux-location'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    async def send_notification(self, title: str, content: str, priority: str = 'default') -> bool:
        """Send notification via Termux-API"""
        try:
            if not self.api_available or not self.features['notifications']:
                self.logger.info(f"📱 Notification (disabled): {title} - {content}")
                return False

            command = [
                'termux-notification',
                '--title', title,
                '--content', content,
                '--priority', priority,
                '--id', f'jarvis_{int(time.time())}'
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.logger.info(f"📱 Notification sent: {title}")
                return True
            else:
                self.logger.error(f"❌ Notification failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Notification error: {e}")
            return False

    async def get_storage_info(self) -> StorageStats:
        """Get storage information"""
        try:
            if self.api_available:
                # Use Termux API if available
                result = subprocess.run(
                    ['termux-storage-info'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    storage_data = json.loads(result.stdout)
                    return StorageStats(
                        total_space=storage_data.get('total', 0),
                        free_space=storage_data.get('free', 0),
                        used_space=storage_data.get('used', 0),
                        available_space=storage_data.get('available', 0)
                    )

            # Fallback: use Python os.statvfs
            stat = os.statvfs('/')
            total_space = stat.f_blocks * stat.f_frsize
            free_space = stat.f_bavail * stat.f_frsize
            used_space = total_space - free_space

            return StorageStats(
                total_space=total_space,
                free_space=free_space,
                used_space=used_space,
                available_space=free_space
            )

        except Exception as e:
            self.logger.error(f"❌ Storage info failed: {e}")
            return StorageStats(0, 0, 0, 0)

    async def get_shared_storage_path(self) -> Optional[str]:
        """Get shared storage path"""
        try:
            # Common Android shared storage paths
            possible_paths = [
                '/storage/emulated/0',
                '/sdcard',
                '/storage/sdcard0',
                '/mnt/sdcard'
            ]

            for path in possible_paths:
                if os.path.exists(path) and os.access(path, os.W_OK):
                    return path

            return None

        except Exception as e:
            self.logger.error(f"❌ Shared storage path detection failed: {e}")
            return None

    async def setup_storage_access(self) -> bool:
        """Setup storage access permissions"""
        try:
            if not self.is_termux:
                self.logger.info("ℹ️ Not in Termux environment")
                return True

            # Check if we have storage access
            shared_path = await self.get_shared_storage_path()
            if shared_path:
                self.logger.info(f"✅ Storage access available: {shared_path}")
                return True

            # Try to setup storage access
            self.logger.warning("⚠️ Storage access not available, requesting permission...")

            # Send notification to user
            await self.send_notification(
                "JARVIS Storage Access",
                "Please grant storage permission: termux-setup-storage",
                priority='high'
            )

            # Try to run termux-setup-storage
            try:
                result = subprocess.run(
                    ['termux-setup-storage'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    # Wait a moment for permissions to take effect
                    await asyncio.sleep(2)

                    # Test again
                    shared_path = await self.get_shared_storage_path()
                    if shared_path:
                        self.logger.info(f"✅ Storage access granted: {shared_path}")
                        return True

            except Exception as e:
                self.logger.error(f"❌ Storage setup command failed: {e}")

            self.logger.error("❌ Storage access setup failed")
            return False

        except Exception as e:
            self.logger.error(f"❌ Storage access setup error: {e}")
            return False

    async def get_battery_info(self) -> Dict[str, Any]:
        """Get battery information"""
        try:
            if not self.api_available or not self.features['battery']:
                return {}

            result = subprocess.run(
                ['termux-battery'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {}

        except Exception as e:
            self.logger.error(f"❌ Battery info failed: {e}")
            return {}

    async def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            if not self.api_available or not self.features['wifi']:
                return {}

            result = subprocess.run(
                ['termux-wifi-connectioninfo'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {}

        except Exception as e:
            self.logger.error(f"❌ Network info failed: {e}")
            return {}

    async def vibrate_device(self, duration_ms: int = 500) -> bool:
        """Vibrate device"""
        try:
            if not self.api_available:
                return False

            command = ['termux-vibrate', '-d', str(duration_ms)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)

            return result.returncode == 0

        except Exception as e:
            self.logger.error(f"❌ Vibration failed: {e}")
            return False

    async def get_clipboard_content(self) -> Optional[str]:
        """Get clipboard content"""
        try:
            if not self.api_available:
                return None

            result = subprocess.run(
                ['termux-clipboard-get'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None

        except Exception as e:
            self.logger.error(f"❌ Clipboard get failed: {e}")
            return None

    async def set_clipboard_content(self, content: str) -> bool:
        """Set clipboard content"""
        try:
            if not self.api_available:
                return False

            command = ['termux-clipboard-set']
            result = subprocess.run(
                command,
                input=content,
                text=True,
                capture_output=True,
                timeout=5
            )

            return result.returncode == 0

        except Exception as e:
            self.logger.error(f"❌ Clipboard set failed: {e}")
            return False

    async def share_text(self, text: str, title: str = "Shared from JARVIS") -> bool:
        """Share text via Android share menu"""
        try:
            if not self.api_available:
                return False

            command = [
                'termux-share',
                '--title', title,
                text
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )

            return result.returncode == 0

        except Exception as e:
            self.logger.error(f"❌ Share text failed: {e}")
            return False

    async def get_device_info(self) -> DeviceInfo:
        """Get comprehensive device information"""
        try:
            if not self.device_info or (datetime.now() - self.last_update).total_seconds() > 300:
                await self._update_device_info()

            if not self.device_info:
                return DeviceInfo("", "", 0, 0, {}, {})

            battery_info = await self.get_battery_info()

            return DeviceInfo(
                model=self.device_info.get('model', 'Unknown'),
                android_version=self.device_info.get('android_version', 'Unknown'),
                api_level=self.device_info.get('api_level', 0),
                battery_level=battery_info.get('percentage', 0),
                storage_info=self.device_info.get('storage', {}),
                network_info=self.device_info.get('network', {})
            )

        except Exception as e:
            self.logger.error(f"❌ Device info retrieval failed: {e}")
            return DeviceInfo("", "", 0, 0, {}, {})

    async def check_system_requirements(self) -> Dict[str, Any]:
        """Check system requirements and capabilities"""
        try:
            requirements = {
                'termux_detected': self.is_termux,
                'api_available': self.api_available,
                'permissions': self.permissions.copy(),
                'features': self.features.copy(),
                'storage_access': bool(await self.get_shared_storage_path()),
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'available_memory': self._get_memory_info(),
                'disk_space': await self.get_storage_info()
            }

            return requirements

        except Exception as e:
            self.logger.error(f"❌ System requirements check failed: {e}")
            return {}

    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        try:
            # Try to read from /proc/meminfo
            meminfo = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemTotal:' in line or 'MemAvailable:' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            meminfo[parts[0].rstrip(':')] = int(parts[1])

            return meminfo
        except Exception:
            return {}

    async def run_termux_command(self, command: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run Termux command safely"""
        try:
            if not self.api_available and command[0].startswith('termux-'):
                return {
                    'success': False,
                    'error': 'Termux-API not available'
                }

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Command timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def get_status_report(self) -> str:
        """Get comprehensive status report"""
        try:
            device_info = await self.get_device_info()
            storage_info = await self.get_storage_info()
            network_info = await self.get_network_info()

            report = f"""
📱 Termux Controller Status Report
═══════════════════════════════════════

🔧 Environment:
   • Termux Detected: {'✅ Yes' if self.is_termux else '❌ No'}
   • API Available: {'✅ Yes' if self.api_available else '❌ No'}
   • Active Features: {sum(self.features.values())}/{len(self.features)}

📱 Device Information:
   • Model: {device_info.model}
   • Android Version: {device_info.android_version}
   • Battery Level: {device_info.battery_level}%

💾 Storage:
   • Total: {storage_info.total_space / (1024**3):.1f} GB
   • Free: {storage_info.free_space / (1024**3):.1f} GB
   • Used: {storage_info.used_space / (1024**3):.1f} GB

🌐 Network:
   • Connected: {'✅ Yes' if network_info else '❌ No'}
   • SSID: {network_info.get('ssid', 'N/A') if network_info else 'N/A'}

🔐 Permissions:
   • Storage: {'✅ Granted' if self.permissions['storage'] else '❌ Denied'}
   • Telephony: {'✅ Granted' if self.permissions['telephony'] else '❌ Denied'}
   • SMS: {'✅ Granted' if self.permissions['sms'] else '❌ Denied'}
   • Camera: {'✅ Granted' if self.permissions['camera'] else '❌ Denied'}
   • Location: {'✅ Granted' if self.permissions['location'] else '❌ Denied'}

═══════════════════════════════════════
"""
            return report.strip()

        except Exception as e:
            self.logger.error(f"❌ Status report generation failed: {e}")
            return f"Status report generation failed: {e}"

    async def shutdown(self):
        """Shutdown Termux controller"""
        try:
            # Save device info cache
            if self.device_info:
                cache_file = self.data_path / "device_cache.json"
                cache_data = {
                    'device_info': self.device_info,
                    'last_update': self.last_update.isoformat() if self.last_update else None
                }

                async with aiofiles.open(cache_file, 'w') as f:
                    await f.write(json.dumps(cache_data, indent=2, default=str))

            self.logger.info("✅ Termux Controller v15 shutdown complete")

        except Exception as e:
            self.logger.error(f"❌ Termux Controller shutdown failed: {e}")

# Import required modules
import sys
import aiofiles