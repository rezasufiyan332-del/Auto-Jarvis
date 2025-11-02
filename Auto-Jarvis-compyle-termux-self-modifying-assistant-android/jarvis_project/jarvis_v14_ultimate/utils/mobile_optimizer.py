#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS v14 Ultimate Mobile Optimization Utilities
================================================

यह utility module mobile platforms (Termux/Android) के लिए automatic
optimization provide करता है।

Features:
- Automatic platform detection
- Memory limit optimization
- CPU usage optimization  
- Battery-friendly settings
- Background processing optimization
- Lightweight operation modes

Author: JARVIS Development Team
Version: 14.0.0 Ultimate
Date: 2025-11-01
"""

import os
import sys
import platform
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

# Logger setup
LOGGER = logging.getLogger(__name__)


@dataclass
class MobileOptimizationProfile:
    """Mobile optimization profile settings"""
    max_memory_mb: int
    max_cpu_percent: float
    max_threads: int
    enable_background_processing: bool
    cache_size_mb: int
    enable_heavy_operations: bool
    gc_threshold: int
    profile_name: str


class MobileOptimizer:
    """
    Mobile platform optimizer जो automatically resource limits set करता है।
    
    यह class platform को detect करता है और appropriate optimization
    profile apply करता है।
    """
    
    # Predefined optimization profiles
    PROFILES = {
        'termux': MobileOptimizationProfile(
            max_memory_mb=150,
            max_cpu_percent=50.0,
            max_threads=2,
            enable_background_processing=False,
            cache_size_mb=32,
            enable_heavy_operations=False,
            gc_threshold=50,  # MB
            profile_name='Termux Lightweight'
        ),
        'android_low': MobileOptimizationProfile(
            max_memory_mb=200,
            max_cpu_percent=60.0,
            max_threads=2,
            enable_background_processing=True,
            cache_size_mb=50,
            enable_heavy_operations=False,
            gc_threshold=80,
            profile_name='Android Low-End'
        ),
        'android_mid': MobileOptimizationProfile(
            max_memory_mb=350,
            max_cpu_percent=70.0,
            max_threads=3,
            enable_background_processing=True,
            cache_size_mb=100,
            enable_heavy_operations=True,
            gc_threshold=150,
            profile_name='Android Mid-Range'
        ),
        'android_high': MobileOptimizationProfile(
            max_memory_mb=512,
            max_cpu_percent=80.0,
            max_threads=4,
            enable_background_processing=True,
            cache_size_mb=150,
            enable_heavy_operations=True,
            gc_threshold=256,
            profile_name='Android High-End'
        ),
        'desktop': MobileOptimizationProfile(
            max_memory_mb=1024,
            max_cpu_percent=90.0,
            max_threads=8,
            enable_background_processing=True,
            cache_size_mb=256,
            enable_heavy_operations=True,
            gc_threshold=512,
            profile_name='Desktop/Server'
        )
    }
    
    def __init__(self, auto_detect: bool = True, profile_name: Optional[str] = None):
        """
        Initialize mobile optimizer
        
        Args:
            auto_detect: Automatically detect platform and apply profile
            profile_name: Specific profile to use (overrides auto-detection)
        """
        self.platform_type = self._detect_platform()
        self.system_resources = self._get_system_resources()
        
        if profile_name:
            self.profile = self.PROFILES.get(profile_name, self.PROFILES['termux'])
        elif auto_detect:
            self.profile = self._select_optimal_profile()
        else:
            self.profile = self.PROFILES['desktop']
        
        LOGGER.info(f"Mobile optimizer initialized with profile: {self.profile.profile_name}")
    
    def _detect_platform(self) -> str:
        """Detect platform type"""
        system = platform.system().lower()
        
        # Check for Termux
        if 'TERMUX_VERSION' in os.environ or os.path.exists('/data/data/com.termux'):
            return 'termux'
        
        # Check for Android (non-Termux)
        elif system == 'linux' and os.path.exists('/system/build.prop'):
            return 'android'
        
        # Standard OS
        elif system == 'linux':
            return 'linux'
        elif system == 'darwin':
            return 'macos'
        elif system == 'windows':
            return 'windows'
        else:
            return 'unknown'
    
    def _get_system_resources(self) -> Dict[str, Any]:
        """Get system resource information"""
        if not PSUTIL_AVAILABLE:
            # Fallback values when psutil is not available
            return {
                'total_memory_mb': 2048,
                'available_memory_mb': 1024,
                'memory_percent': 50.0,
                'cpu_count': 4,
                'cpu_percent': 50.0
            }
        
        try:
            mem = psutil.virtual_memory()
            cpu_count = psutil.cpu_count(logical=True)
            
            return {
                'total_memory_mb': mem.total // (1024 * 1024),
                'available_memory_mb': mem.available // (1024 * 1024),
                'memory_percent': mem.percent,
                'cpu_count': cpu_count,
                'cpu_percent': psutil.cpu_percent(interval=0.1)
            }
        except Exception as e:
            LOGGER.warning(f"Could not get system resources: {e}")
            return {
                'total_memory_mb': 2048,
                'available_memory_mb': 1024,
                'memory_percent': 50.0,
                'cpu_count': 4,
                'cpu_percent': 50.0
            }
    
    def _select_optimal_profile(self) -> MobileOptimizationProfile:
        """Select optimal profile based on platform and resources"""
        total_mem = self.system_resources.get('total_memory_mb', 2048)
        
        if self.platform_type == 'termux':
            return self.PROFILES['termux']
        
        elif self.platform_type == 'android':
            # Select based on available memory
            if total_mem < 2048:
                return self.PROFILES['android_low']
            elif total_mem < 4096:
                return self.PROFILES['android_mid']
            else:
                return self.PROFILES['android_high']
        
        else:
            # Desktop/Server
            return self.PROFILES['desktop']
    
    def get_memory_limit(self) -> int:
        """Get memory limit in MB"""
        return self.profile.max_memory_mb
    
    def get_cpu_limit(self) -> float:
        """Get CPU usage limit percentage"""
        return self.profile.max_cpu_percent
    
    def get_thread_limit(self) -> int:
        """Get maximum thread count"""
        return self.profile.max_threads
    
    def get_cache_limit(self) -> int:
        """Get cache size limit in MB"""
        return self.profile.cache_size_mb
    
    def is_heavy_operations_enabled(self) -> bool:
        """Check if heavy operations are allowed"""
        return self.profile.enable_heavy_operations
    
    def is_background_processing_enabled(self) -> bool:
        """Check if background processing is allowed"""
        return self.profile.enable_background_processing
    
    def get_gc_threshold(self) -> int:
        """Get garbage collection threshold in MB"""
        return self.profile.gc_threshold
    
    def apply_to_config(self, config: Any) -> None:
        """
        Apply mobile optimizations to configuration object
        
        Args:
            config: Configuration object to optimize
        """
        try:
            # Memory configuration
            if hasattr(config, 'memory'):
                config.memory.max_heap_size_mb = self.profile.max_memory_mb
                config.memory.young_gen_size_mb = int(self.profile.max_memory_mb * 0.25)
                config.memory.old_gen_size_mb = int(self.profile.max_memory_mb * 0.75)
                config.memory.cache_size_mb = self.profile.cache_size_mb
                LOGGER.debug(f"Applied memory limits: {self.profile.max_memory_mb} MB")
            
            # CPU configuration
            if hasattr(config, 'cpu'):
                config.cpu.max_cpu_percent = self.profile.max_cpu_percent
                config.cpu.max_threads = self.profile.max_threads
                LOGGER.debug(f"Applied CPU limits: {self.profile.max_cpu_percent}%, {self.profile.max_threads} threads")
            
            # Threading configuration
            if hasattr(config, 'threading'):
                config.threading.max_worker_threads = self.profile.max_threads
                config.threading.max_thread_pool_size = self.profile.max_threads * 2
                LOGGER.debug(f"Applied threading limits: {self.profile.max_threads} workers")
            
            # Cache configuration
            if hasattr(config, 'cache'):
                config.cache.max_cache_size_mb = self.profile.cache_size_mb
                config.cache.enable_disk_cache = False if self.platform_type == 'termux' else True
                LOGGER.debug(f"Applied cache limits: {self.profile.cache_size_mb} MB")
            
            # Background processing
            if hasattr(config, 'background'):
                config.background.enabled = self.profile.enable_background_processing
                config.background.max_background_tasks = 1 if self.platform_type == 'termux' else 5
                LOGGER.debug(f"Background processing: {self.profile.enable_background_processing}")
            
            # Battery optimization
            if hasattr(config, 'battery'):
                if self.platform_type in ('termux', 'android'):
                    config.battery.enable_battery_optimization = True
                    config.battery.optimization_level = 'aggressive'
                    LOGGER.debug("Applied battery optimizations")
            
            LOGGER.info(f"Successfully applied {self.profile.profile_name} optimizations")
            
        except Exception as e:
            LOGGER.error(f"Error applying mobile optimizations: {e}")
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get optimization summary"""
        return {
            'profile_name': self.profile.profile_name,
            'platform': self.platform_type,
            'max_memory_mb': self.profile.max_memory_mb,
            'max_cpu_percent': self.profile.max_cpu_percent,
            'max_threads': self.profile.max_threads,
            'cache_size_mb': self.profile.cache_size_mb,
            'background_processing': self.profile.enable_background_processing,
            'heavy_operations': self.profile.enable_heavy_operations,
            'gc_threshold_mb': self.profile.gc_threshold,
            'system_total_memory_mb': self.system_resources.get('total_memory_mb'),
            'system_available_memory_mb': self.system_resources.get('available_memory_mb'),
            'system_cpu_count': self.system_resources.get('cpu_count')
        }
    
    def check_memory_usage(self) -> Dict[str, Any]:
        """Check current memory usage against limits"""
        if not PSUTIL_AVAILABLE:
            return {
                'error': 'psutil not available',
                'current_mb': 0,
                'limit_mb': self.profile.max_memory_mb
            }
        
        try:
            process = psutil.Process()
            mem_info = process.memory_info()
            mem_mb = mem_info.rss // (1024 * 1024)
            
            limit = self.profile.max_memory_mb
            usage_percent = (mem_mb / limit) * 100
            
            return {
                'current_mb': mem_mb,
                'limit_mb': limit,
                'usage_percent': usage_percent,
                'within_limit': mem_mb <= limit,
                'warning': mem_mb > (limit * 0.8),
                'critical': mem_mb > (limit * 0.95)
            }
        except Exception as e:
            LOGGER.error(f"Error checking memory usage: {e}")
            return {'error': str(e)}
    
    def suggest_gc(self) -> bool:
        """Suggest if garbage collection should run"""
        mem_check = self.check_memory_usage()
        if 'current_mb' in mem_check:
            return mem_check['current_mb'] >= self.profile.gc_threshold
        return False
    
    def __str__(self) -> str:
        return f"MobileOptimizer(profile={self.profile.profile_name}, platform={self.platform_type})"
    
    def __repr__(self) -> str:
        return (f"MobileOptimizer(profile={self.profile.profile_name}, "
                f"platform={self.platform_type}, "
                f"max_mem={self.profile.max_memory_mb}MB)")


# Global optimizer instance
_global_optimizer: Optional[MobileOptimizer] = None


def get_mobile_optimizer(auto_detect: bool = True) -> MobileOptimizer:
    """
    Get global mobile optimizer instance
    
    Args:
        auto_detect: Auto-detect platform
        
    Returns:
        MobileOptimizer instance
    """
    global _global_optimizer
    
    if _global_optimizer is None:
        _global_optimizer = MobileOptimizer(auto_detect=auto_detect)
    
    return _global_optimizer


def reset_mobile_optimizer() -> MobileOptimizer:
    """Reset global mobile optimizer"""
    global _global_optimizer
    _global_optimizer = MobileOptimizer(auto_detect=True)
    return _global_optimizer


# Convenience functions
def get_memory_limit() -> int:
    """Get memory limit in MB"""
    return get_mobile_optimizer().get_memory_limit()


def get_cpu_limit() -> float:
    """Get CPU limit percentage"""
    return get_mobile_optimizer().get_cpu_limit()


def get_thread_limit() -> int:
    """Get thread limit"""
    return get_mobile_optimizer().get_thread_limit()


def is_mobile_platform() -> bool:
    """Check if running on mobile platform"""
    optimizer = get_mobile_optimizer()
    return optimizer.platform_type in ('termux', 'android')


def is_termux() -> bool:
    """Check if running on Termux"""
    return get_mobile_optimizer().platform_type == 'termux'


# Main execution for testing
if __name__ == "__main__":
    print("JARVIS v14 Ultimate - Mobile Optimization Test")
    print("=" * 50)
    
    # Create optimizer
    optimizer = MobileOptimizer()
    
    # Display optimization summary
    print("\n=== Optimization Profile ===")
    summary = optimizer.get_optimization_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Check memory usage
    print("\n=== Memory Usage Check ===")
    mem_check = optimizer.check_memory_usage()
    for key, value in mem_check.items():
        print(f"{key}: {value}")
    
    # GC suggestion
    print(f"\nSuggest GC: {optimizer.suggest_gc()}")
    
    print("\n✅ Mobile optimization test completed!")
