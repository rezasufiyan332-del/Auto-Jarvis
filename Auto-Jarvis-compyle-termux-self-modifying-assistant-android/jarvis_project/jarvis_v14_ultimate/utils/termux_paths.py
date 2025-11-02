#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS v14 Ultimate Termux Path Utilities
=========================================

यह utility module Termux और अन्य platforms के लिए proper paths provide करता है।
यह automatically platform detect करता है और appropriate paths return करता है।

Features:
- Automatic platform detection (Termux/Linux/Windows/macOS)
- Platform-specific path generation
- Path validation and creation
- Fallback mechanisms for path access
- Cross-platform compatibility

Author: JARVIS Development Team
Version: 14.0.0 Ultimate
Date: 2025-11-01
"""

import os
import sys
import platform
from pathlib import Path
from typing import Dict, Optional, Union
from enum import Enum
import logging

# Logger setup
LOGGER = logging.getLogger(__name__)


class PlatformType(Enum):
    """Supported platform types"""
    TERMUX = "termux"
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"
    ANDROID = "android"
    UNKNOWN = "unknown"


class TermuxPathManager:
    """
    Termux-aware path manager जो platform-specific paths provide करता है।
    
    यह class automatically detect करता है कि application कहाँ run हो रहा है
    और appropriate paths generate करता है।
    """
    
    def __init__(self):
        """Initialize path manager with platform detection"""
        self.platform = self._detect_platform()
        self._base_paths = self._initialize_base_paths()
        
        LOGGER.info(f"Path manager initialized for platform: {self.platform.value}")
    
    def _detect_platform(self) -> PlatformType:
        """
        Detect current platform
        
        Returns:
            Detected platform type
        """
        system = platform.system().lower()
        
        # Check for Termux-specific indicators
        if self._is_termux():
            return PlatformType.TERMUX
        
        # Check for Android (non-Termux)
        elif self._is_android():
            return PlatformType.ANDROID
        
        # Standard OS detection
        elif system == "linux":
            return PlatformType.LINUX
        elif system == "darwin":
            return PlatformType.MACOS
        elif system == "windows":
            return PlatformType.WINDOWS
        else:
            return PlatformType.UNKNOWN
    
    def _is_termux(self) -> bool:
        """
        Check if running in Termux environment
        
        Returns:
            True if running in Termux
        """
        # Check for Termux-specific environment variables
        if 'TERMUX_VERSION' in os.environ:
            return True
        
        # Check for Termux directory structure
        if os.path.exists('/data/data/com.termux'):
            return True
        
        # Check PREFIX environment variable (Termux-specific)
        if os.environ.get('PREFIX', '').startswith('/data/data/com.termux'):
            return True
        
        return False
    
    def _is_android(self) -> bool:
        """
        Check if running on Android (non-Termux)
        
        Returns:
            True if running on Android
        """
        return (platform.system().lower() == "linux" and 
                os.path.exists('/system/build.prop'))
    
    def _initialize_base_paths(self) -> Dict[str, Path]:
        """
        Initialize platform-specific base paths
        
        Returns:
            Dictionary of base paths
        """
        paths = {}
        
        if self.platform == PlatformType.TERMUX:
            # Termux-specific paths
            prefix = os.environ.get('PREFIX', '/data/data/com.termux/files/usr')
            home = os.environ.get('HOME', '/data/data/com.termux/files/home')
            
            paths['home'] = Path(home)
            paths['prefix'] = Path(prefix)
            paths['app_data'] = Path(home) / '.jarvis'
            paths['config'] = Path(home) / '.jarvis' / 'config'
            paths['data'] = Path(home) / '.jarvis' / 'data'
            paths['logs'] = Path(home) / '.jarvis' / 'logs'
            paths['cache'] = Path(home) / '.jarvis' / 'cache'
            paths['temp'] = Path(prefix) / 'tmp'
            paths['backups'] = Path(home) / '.jarvis' / 'backups'
            paths['models'] = Path(home) / '.jarvis' / 'models'
            paths['plugins'] = Path(home) / '.jarvis' / 'plugins'
            
        elif self.platform == PlatformType.ANDROID:
            # Generic Android paths (non-Termux)
            app_dir = '/data/data/com.jarvis.ultimate'
            paths['home'] = Path(app_dir)
            paths['app_data'] = Path(app_dir)
            paths['config'] = Path(app_dir) / 'config'
            paths['data'] = Path(app_dir) / 'data'
            paths['logs'] = Path(app_dir) / 'logs'
            paths['cache'] = Path(app_dir) / 'cache'
            paths['temp'] = Path(app_dir) / 'temp'
            paths['backups'] = Path(app_dir) / 'backups'
            paths['models'] = Path(app_dir) / 'models'
            paths['plugins'] = Path(app_dir) / 'plugins'
            
        elif self.platform == PlatformType.LINUX:
            # Standard Linux paths
            home = Path.home()
            paths['home'] = home
            paths['app_data'] = home / '.jarvis'
            paths['config'] = home / '.config' / 'jarvis'
            paths['data'] = home / '.local' / 'share' / 'jarvis'
            paths['logs'] = home / '.local' / 'share' / 'jarvis' / 'logs'
            paths['cache'] = home / '.cache' / 'jarvis'
            paths['temp'] = Path('/tmp') / 'jarvis'
            paths['backups'] = home / '.local' / 'share' / 'jarvis' / 'backups'
            paths['models'] = home / '.local' / 'share' / 'jarvis' / 'models'
            paths['plugins'] = home / '.local' / 'share' / 'jarvis' / 'plugins'
            
        elif self.platform == PlatformType.WINDOWS:
            # Windows paths
            home = Path.home()
            appdata = Path(os.environ.get('APPDATA', home / 'AppData' / 'Roaming'))
            localappdata = Path(os.environ.get('LOCALAPPDATA', home / 'AppData' / 'Local'))
            
            paths['home'] = home
            paths['app_data'] = appdata / 'JARVIS'
            paths['config'] = appdata / 'JARVIS' / 'config'
            paths['data'] = localappdata / 'JARVIS' / 'data'
            paths['logs'] = localappdata / 'JARVIS' / 'logs'
            paths['cache'] = localappdata / 'JARVIS' / 'cache'
            paths['temp'] = Path(os.environ.get('TEMP', home / 'AppData' / 'Local' / 'Temp')) / 'jarvis'
            paths['backups'] = appdata / 'JARVIS' / 'backups'
            paths['models'] = localappdata / 'JARVIS' / 'models'
            paths['plugins'] = appdata / 'JARVIS' / 'plugins'
            
        elif self.platform == PlatformType.MACOS:
            # macOS paths
            home = Path.home()
            paths['home'] = home
            paths['app_data'] = home / 'Library' / 'Application Support' / 'JARVIS'
            paths['config'] = home / 'Library' / 'Application Support' / 'JARVIS' / 'config'
            paths['data'] = home / 'Library' / 'Application Support' / 'JARVIS' / 'data'
            paths['logs'] = home / 'Library' / 'Logs' / 'JARVIS'
            paths['cache'] = home / 'Library' / 'Caches' / 'JARVIS'
            paths['temp'] = Path('/tmp') / 'jarvis'
            paths['backups'] = home / 'Library' / 'Application Support' / 'JARVIS' / 'backups'
            paths['models'] = home / 'Library' / 'Application Support' / 'JARVIS' / 'models'
            paths['plugins'] = home / 'Library' / 'Application Support' / 'JARVIS' / 'plugins'
        
        else:
            # Fallback for unknown platforms - use current directory
            current = Path.cwd()
            paths['home'] = current
            paths['app_data'] = current / '.jarvis'
            paths['config'] = current / '.jarvis' / 'config'
            paths['data'] = current / '.jarvis' / 'data'
            paths['logs'] = current / '.jarvis' / 'logs'
            paths['cache'] = current / '.jarvis' / 'cache'
            paths['temp'] = current / '.jarvis' / 'temp'
            paths['backups'] = current / '.jarvis' / 'backups'
            paths['models'] = current / '.jarvis' / 'models'
            paths['plugins'] = current / '.jarvis' / 'plugins'
        
        return paths
    
    def get_path(self, path_type: str, create: bool = True) -> Path:
        """
        Get platform-specific path
        
        Args:
            path_type: Type of path (config, data, logs, cache, temp, etc.)
            create: Create directory if it doesn't exist
            
        Returns:
            Path object for requested path type
        """
        if path_type not in self._base_paths:
            raise ValueError(f"Unknown path type: {path_type}. Valid types: {list(self._base_paths.keys())}")
        
        path = self._base_paths[path_type]
        
        if create:
            try:
                path.mkdir(parents=True, exist_ok=True)
                LOGGER.debug(f"Created directory: {path}")
            except PermissionError:
                LOGGER.warning(f"Permission denied creating directory: {path}")
            except Exception as e:
                LOGGER.error(f"Error creating directory {path}: {e}")
        
        return path
    
    def get_config_path(self, filename: str = "ultimate_config.json") -> Path:
        """Get configuration file path"""
        return self.get_path('config') / filename
    
    def get_data_path(self, filename: str = "main.db") -> Path:
        """Get data file path"""
        return self.get_path('data') / filename
    
    def get_log_path(self, filename: str = "jarvis.log") -> Path:
        """Get log file path"""
        return self.get_path('logs') / filename
    
    def get_cache_path(self, filename: Optional[str] = None) -> Path:
        """Get cache directory or file path"""
        if filename:
            return self.get_path('cache') / filename
        return self.get_path('cache')
    
    def get_temp_path(self, filename: Optional[str] = None) -> Path:
        """Get temp directory or file path"""
        if filename:
            return self.get_path('temp') / filename
        return self.get_path('temp')
    
    def get_backup_path(self, filename: Optional[str] = None) -> Path:
        """Get backup directory or file path"""
        if filename:
            return self.get_path('backups') / filename
        return self.get_path('backups')
    
    def get_model_path(self, filename: Optional[str] = None) -> Path:
        """Get model directory or file path"""
        if filename:
            return self.get_path('models') / filename
        return self.get_path('models')
    
    def get_plugin_path(self, filename: Optional[str] = None) -> Path:
        """Get plugin directory or file path"""
        if filename:
            return self.get_path('plugins') / filename
        return self.get_path('plugins')
    
    def create_all_directories(self) -> Dict[str, bool]:
        """
        Create all standard directories
        
        Returns:
            Dictionary with creation status for each directory
        """
        results = {}
        for path_type in self._base_paths.keys():
            try:
                self.get_path(path_type, create=True)
                results[path_type] = True
            except Exception as e:
                LOGGER.error(f"Failed to create {path_type} directory: {e}")
                results[path_type] = False
        
        return results
    
    def validate_permissions(self) -> Dict[str, Dict[str, bool]]:
        """
        Validate read/write permissions for all paths
        
        Returns:
            Dictionary with permission status for each path
        """
        results = {}
        
        for path_type, path in self._base_paths.items():
            results[path_type] = {
                'exists': path.exists(),
                'readable': os.access(path, os.R_OK) if path.exists() else False,
                'writable': os.access(path, os.W_OK) if path.exists() else False,
                'executable': os.access(path, os.X_OK) if path.exists() else False
            }
        
        return results
    
    def get_platform_info(self) -> Dict[str, str]:
        """
        Get detailed platform information
        
        Returns:
            Dictionary with platform details
        """
        info = {
            'platform_type': self.platform.value,
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'home_directory': str(self._base_paths.get('home', 'unknown')),
            'app_data_directory': str(self._base_paths.get('app_data', 'unknown'))
        }
        
        # Add Termux-specific info
        if self.platform == PlatformType.TERMUX:
            info['termux_version'] = os.environ.get('TERMUX_VERSION', 'unknown')
            info['termux_prefix'] = os.environ.get('PREFIX', 'unknown')
            info['termux_android_version'] = os.environ.get('TERMUX_ANDROID_VERSION', 'unknown')
        
        return info
    
    def __str__(self) -> str:
        return f"TermuxPathManager(platform={self.platform.value})"
    
    def __repr__(self) -> str:
        return f"TermuxPathManager(platform={self.platform.value}, paths={len(self._base_paths)})"


# Global path manager instance (Singleton)
_global_path_manager: Optional[TermuxPathManager] = None


def get_path_manager() -> TermuxPathManager:
    """
    Get global path manager instance (Singleton)
    
    Returns:
        Global TermuxPathManager instance
    """
    global _global_path_manager
    
    if _global_path_manager is None:
        _global_path_manager = TermuxPathManager()
    
    return _global_path_manager


def reset_path_manager() -> TermuxPathManager:
    """
    Reset global path manager
    
    Returns:
        New TermuxPathManager instance
    """
    global _global_path_manager
    _global_path_manager = TermuxPathManager()
    return _global_path_manager


# Convenience functions for common path operations
def get_config_path(filename: str = "ultimate_config.json") -> Path:
    """Get configuration file path"""
    return get_path_manager().get_config_path(filename)


def get_data_path(filename: str = "main.db") -> Path:
    """Get data file path"""
    return get_path_manager().get_data_path(filename)


def get_log_path(filename: str = "jarvis.log") -> Path:
    """Get log file path"""
    return get_path_manager().get_log_path(filename)


def get_cache_path(filename: Optional[str] = None) -> Path:
    """Get cache directory or file path"""
    return get_path_manager().get_cache_path(filename)


def get_temp_path(filename: Optional[str] = None) -> Path:
    """Get temp directory or file path"""
    return get_path_manager().get_temp_path(filename)


def is_termux() -> bool:
    """Check if running in Termux"""
    return get_path_manager().platform == PlatformType.TERMUX


def is_android() -> bool:
    """Check if running on Android"""
    return get_path_manager().platform in (PlatformType.TERMUX, PlatformType.ANDROID)


def get_platform() -> PlatformType:
    """Get current platform type"""
    return get_path_manager().platform


# Main execution for testing
if __name__ == "__main__":
    print("JARVIS v14 Ultimate - Termux Path Utilities Test")
    print("=" * 50)
    
    # Create path manager
    pm = TermuxPathManager()
    
    # Display platform info
    print("\n=== Platform Information ===")
    info = pm.get_platform_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # Display paths
    print("\n=== Platform-Specific Paths ===")
    for path_type, path in pm._base_paths.items():
        print(f"{path_type:15s}: {path}")
    
    # Test path creation
    print("\n=== Creating Directories ===")
    creation_results = pm.create_all_directories()
    for path_type, success in creation_results.items():
        status = "✓" if success else "✗"
        print(f"{status} {path_type}")
    
    # Test permissions
    print("\n=== Validating Permissions ===")
    permissions = pm.validate_permissions()
    for path_type, perms in permissions.items():
        if perms['exists']:
            r = "R" if perms['readable'] else "-"
            w = "W" if perms['writable'] else "-"
            x = "X" if perms['executable'] else "-"
            print(f"{path_type:15s}: {r}{w}{x}")
        else:
            print(f"{path_type:15s}: NOT EXISTS")
    
    # Test convenience functions
    print("\n=== Testing Convenience Functions ===")
    print(f"Config path: {get_config_path()}")
    print(f"Data path: {get_data_path()}")
    print(f"Log path: {get_log_path()}")
    print(f"Cache path: {get_cache_path()}")
    print(f"Temp path: {get_temp_path()}")
    print(f"Is Termux: {is_termux()}")
    print(f"Is Android: {is_android()}")
    print(f"Platform: {get_platform().value}")
    
    print("\n✅ Path utilities test completed!")
