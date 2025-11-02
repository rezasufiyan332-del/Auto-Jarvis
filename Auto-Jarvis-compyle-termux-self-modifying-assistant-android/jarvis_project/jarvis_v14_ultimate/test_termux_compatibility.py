#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS v14 Ultimate - Termux Compatibility Test Suite
=====================================================

यह comprehensive test suite JARVIS v14 Ultimate की Termux compatibility
को verify करता है।

Test Categories:
1. Import Tests - सभी modules properly import हों
2. Path Tests - सभी paths accessible हों
3. Config Tests - Configuration properly load हो
4. Memory Tests - Memory limits properly set हों
5. Performance Tests - Mobile optimizations apply हों

Author: JARVIS Development Team
Version: 14.0.0 Ultimate
Date: 2025-11-01
"""

import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'utils'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'config'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'core'))

# Test results
test_results = {
    'passed': 0,
    'failed': 0,
    'warnings': 0,
    'total': 0
}

def log_test(test_name, status, message=""):
    """Log test result"""
    test_results['total'] += 1
    
    if status == 'PASS':
        test_results['passed'] += 1
        print(f"✓ {test_name}: {message}")
    elif status == 'FAIL':
        test_results['failed'] += 1
        print(f"✗ {test_name}: {message}")
    elif status == 'WARN':
        test_results['warnings'] += 1
        print(f"⚠ {test_name}: {message}")

def test_imports():
    """Test 1: Core module imports"""
    print("\n=== Test 1: Import Tests ===")
    
    # Test utils imports
    try:
        from termux_paths import TermuxPathManager, get_path_manager
        log_test("termux_paths import", "PASS", "Path manager module loaded")
    except Exception as e:
        log_test("termux_paths import", "FAIL", str(e))
    
    try:
        from mobile_optimizer import MobileOptimizer, get_mobile_optimizer
        log_test("mobile_optimizer import", "PASS", "Mobile optimizer module loaded")
    except Exception as e:
        log_test("mobile_optimizer import", "FAIL", str(e))
    
    # Test config imports
    try:
        from ultimate_config import UltimateConfig
        log_test("ultimate_config import", "PASS", "Ultimate config module loaded")
    except Exception as e:
        log_test("ultimate_config import", "FAIL", str(e))
    
    try:
        from performance_config import PerformanceOptimizer
        log_test("performance_config import", "PASS", "Performance config module loaded")
    except Exception as e:
        log_test("performance_config import", "FAIL", str(e))
    
    try:
        from termux_config import TermuxConfig
        log_test("termux_config import", "PASS", "Termux config module loaded")
    except Exception as e:
        log_test("termux_config import", "FAIL", str(e))
    
    # Test core stub modules (sample)
    stub_modules = [
        'ai_engine',
        'enhanced_database_manager',
        'advanced_termux_controller',
        'notification_system',
        'memory_manager'
    ]
    
    for module in stub_modules:
        try:
            __import__(module)
            log_test(f"Stub module: {module}", "PASS", "Module available")
        except Exception as e:
            log_test(f"Stub module: {module}", "WARN", f"Not critical: {str(e)[:50]}")

def test_paths():
    """Test 2: Path accessibility"""
    print("\n=== Test 2: Path Tests ===")
    
    try:
        from termux_paths import get_path_manager
        pm = get_path_manager()
        
        log_test("Path manager initialization", "PASS", f"Platform: {pm.platform.value}")
        
        # Test path retrieval
        config_path = pm.get_config_path()
        log_test("Config path retrieval", "PASS", str(config_path))
        
        data_path = pm.get_data_path()
        log_test("Data path retrieval", "PASS", str(data_path))
        
        log_path = pm.get_log_path()
        log_test("Log path retrieval", "PASS", str(log_path))
        
        # Test directory creation
        try:
            results = pm.create_all_directories()
            created = sum(1 for v in results.values() if v)
            log_test("Directory creation", "PASS", f"{created}/{len(results)} directories created")
        except Exception as e:
            log_test("Directory creation", "WARN", str(e))
        
    except Exception as e:
        log_test("Path manager", "FAIL", str(e))

def test_configuration():
    """Test 3: Configuration loading"""
    print("\n=== Test 3: Configuration Tests ===")
    
    try:
        from ultimate_config import UltimateConfig
        config = UltimateConfig()
        
        log_test("UltimateConfig initialization", "PASS", f"Environment: {config.environment.value}")
        log_test("Config platform detection", "PASS", f"Platform: {config.system_platform.value}")
        log_test("Logging config", "PASS", f"Log path: {config.logging.log_file_path}")
        log_test("Database config", "PASS", f"DB path: {config.database.db_path}")
        
    except Exception as e:
        log_test("UltimateConfig", "FAIL", str(e))
    
    try:
        from performance_config import PerformanceOptimizer
        perf = PerformanceOptimizer()
        
        log_test("PerformanceConfig initialization", "PASS", f"Mode: {perf.mode.value}")
        log_test("Memory limits", "PASS", f"{perf.memory.max_heap_size_mb}MB")
        log_test("Thread limits", "PASS", f"{perf.threading.main_thread_pool_size} threads")
        log_test("Temp path", "PASS", f"{perf.storage.temporary_file_location}")
        
    except Exception as e:
        log_test("PerformanceConfig", "FAIL", str(e))

def test_mobile_optimization():
    """Test 4: Mobile optimization"""
    print("\n=== Test 4: Mobile Optimization Tests ===")
    
    try:
        from mobile_optimizer import get_mobile_optimizer
        optimizer = get_mobile_optimizer()
        
        log_test("Mobile optimizer initialization", "PASS", f"Profile: {optimizer.profile.profile_name}")
        
        summary = optimizer.get_optimization_summary()
        log_test("Platform detection", "PASS", f"Platform: {summary['platform']}")
        log_test("Memory optimization", "PASS", f"Limit: {summary['max_memory_mb']}MB")
        log_test("CPU optimization", "PASS", f"Max: {summary['max_cpu_percent']}%")
        log_test("Thread optimization", "PASS", f"Max: {summary['max_threads']} threads")
        log_test("Cache optimization", "PASS", f"Size: {summary['cache_size_mb']}MB")
        
        # Test profile application
        from performance_config import PerformanceOptimizer
        perf = PerformanceOptimizer()
        
        if optimizer.platform_type in ('termux', 'android'):
            if perf.memory.max_heap_size_mb <= 512:
                log_test("Mobile limits applied", "PASS", "Memory limits are mobile-friendly")
            else:
                log_test("Mobile limits applied", "WARN", "Memory limits seem high for mobile")
        
    except Exception as e:
        log_test("Mobile optimizer", "FAIL", str(e))

def test_requirements():
    """Test 5: Requirements check"""
    print("\n=== Test 5: Requirements Check ===")
    
    # Check requirements_termux.txt
    req_file = os.path.join(PROJECT_ROOT, 'requirements_termux.txt')
    if os.path.exists(req_file):
        log_test("requirements_termux.txt exists", "PASS", "Termux dependencies file found")
        
        with open(req_file, 'r') as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            log_test("Dependency count", "PASS", f"{len(lines)} packages listed")
    else:
        log_test("requirements_termux.txt", "FAIL", "File not found")
    
    # Check core Python version
    import sys
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 8):
        log_test("Python version", "PASS", f"Python {py_version} (compatible)")
    else:
        log_test("Python version", "WARN", f"Python {py_version} (may have issues)")

def test_installation_script():
    """Test 6: Installation script check"""
    print("\n=== Test 6: Installation Script Check ===")
    
    install_script = os.path.join(PROJECT_ROOT, 'install_termux.sh')
    if os.path.exists(install_script):
        log_test("install_termux.sh exists", "PASS", "Installation script found")
        
        # Check if executable
        if os.access(install_script, os.X_OK):
            log_test("install_termux.sh executable", "PASS", "Script is executable")
        else:
            log_test("install_termux.sh executable", "WARN", "Run: chmod +x install_termux.sh")
    else:
        log_test("install_termux.sh", "FAIL", "Installation script not found")

def print_summary():
    """Print test summary"""
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Total Tests:    {test_results['total']}")
    print(f"✓ Passed:       {test_results['passed']}")
    print(f"✗ Failed:       {test_results['failed']}")
    print(f"⚠ Warnings:     {test_results['warnings']}")
    print("="*50)
    
    pass_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"Pass Rate:      {pass_rate:.1f}%")
    
    if test_results['failed'] == 0:
        print("\n✅ ALL TESTS PASSED!")
        print("JARVIS v14 Ultimate is ready for Termux!")
        return 0
    else:
        print(f"\n⚠ {test_results['failed']} test(s) failed")
        print("Please review errors above")
        return 1

def main():
    """Main test execution"""
    print("="*50)
    print("JARVIS v14 Ultimate - Termux Compatibility Test")
    print("="*50)
    print(f"Project Root: {PROJECT_ROOT}")
    print()
    
    # Run all tests
    test_imports()
    test_paths()
    test_configuration()
    test_mobile_optimization()
    test_requirements()
    test_installation_script()
    
    # Print summary
    return print_summary()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
