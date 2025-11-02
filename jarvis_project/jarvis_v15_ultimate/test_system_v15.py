#!/usr/bin/env python3
"""
JARVIS v15 Ultimate - Comprehensive Testing Suite
Complete system testing for Termux compatibility and functionality
Automated testing with validation and reporting
"""

import os
import sys
import time
import asyncio
import json
import logging
import subprocess
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'termux_native'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(title: str):
    print(f"\n{Colors.HEADER}🧪 {title}{Colors.ENDC}")

def print_test_result(test_name: str, passed: bool, details: str = ""):
    status = "✅ PASS" if passed else "❌ FAIL"
    color = Colors.OKGREEN if passed else Colors.FAIL
    print(f"  {color}{status} {test_name}{Colors.ENDC}")
    if details:
        print(f"    {details}")

class TestResult:
    """Test result tracking"""
    def __init__(self, name: str, passed: bool, duration: float, details: str = "", error: str = ""):
        self.name = name
        self.passed = passed
        self.duration = duration
        self.details = details
        self.error = error
        self.timestamp = datetime.now()

class SystemTester:
    """Comprehensive system tester"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.test_results = []
        self.start_time = time.time()

        # Setup logging
        logging.basicConfig(level=logging.ERROR)
        self.logger = logging.getLogger("SystemTester")

    def add_result(self, name: str, passed: bool, duration: float, details: str = "", error: str = ""):
        """Add test result"""
        result = TestResult(name, passed, duration, details, error)
        self.test_results.append(result)
        print_test_result(name, passed, details or error)

    def run_test(self, test_name: str, test_func, *args, **kwargs) -> bool:
        """Run a test function"""
        start_time = time.time()
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            if isinstance(result, tuple):
                passed, details = result
            else:
                passed = result
                details = ""
            self.add_result(test_name, passed, duration, details)
            return passed
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"{type(e).__name__}: {e}"
            self.add_result(test_name, False, duration, "", error_msg)
            return False

    def test_imports(self) -> bool:
        """Test critical module imports"""
        print_test_header("Import Tests")

        critical_imports = [
            ('asyncio', 'asyncio'),
            ('aiohttp', 'aiohttp'),
            ('click', 'click'),
            ('pydantic', 'pydantic'),
            ('cryptography', 'cryptography'),
            ('yaml', 'yaml'),
            ('dotenv', 'dotenv'),
            ('json', 'json'),
            ('pathlib', 'pathlib'),
            ('datetime', 'datetime')
        ]

        all_passed = True
        for module_name, import_name in critical_imports:
            try:
                __import__(import_name)
                print_test_result(f"Import {module_name}", True)
            except ImportError as e:
                print_test_result(f"Import {module_name}", False, str(e))
                all_passed = False

        return all_passed

    def test_file_structure(self) -> bool:
        """Test file structure"""
        print_test_header("File Structure Tests")

        required_files = [
            'jarvis.py',
            'requirements_termux_v15.txt',
            'setup_termux_v15.py'
        ]

        required_dirs = [
            'core',
            'config',
            'termux_native',
            'utils'
        ]

        all_passed = True

        for file_name in required_files:
            file_path = self.base_path / file_name
            passed = file_path.exists()
            self.add_result(f"File: {file_name}", passed, 0.0, "Exists" if passed else "Missing")
            if not passed:
                all_passed = False

        for dir_name in required_dirs:
            dir_path = self.base_path / dir_name
            passed = dir_path.exists() and dir_path.is_dir()
            self.add_result(f"Directory: {dir_name}", passed, 0.0, "Exists" if passed else "Missing")
            if not passed:
                all_passed = False

        return all_passed

    def test_python_syntax(self) -> bool:
        """Test Python syntax in core files"""
        print_test_header("Syntax Tests")

        python_files = list(self.base_path.rglob("*.py"))
        syntax_errors = []

        for py_file in python_files:
            if '__pycache__' in str(py_file):
                continue

            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'py_compile', str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                passed = result.returncode == 0
                details = "Valid syntax" if passed else result.stderr
                self.add_result(f"Syntax: {py_file.name}", passed, 0.0, details)

                if not passed:
                    syntax_errors.append(str(py_file))

            except subprocess.TimeoutExpired:
                self.add_result(f"Syntax: {py_file.name}", False, 0.0, "", "Compilation timeout")
                syntax_errors.append(str(py_file))
            except Exception as e:
                self.add_result(f"Syntax: {py_file.name}", False, 0.0, "", str(e))
                syntax_errors.append(str(py_file))

        return len(syntax_errors) == 0

    def test_configuration_files(self) -> bool:
        """Test configuration files"""
        print_test_header("Configuration Tests")

        config_tests = []

        # Test requirements file
        req_file = self.base_path / "requirements_termux_v15.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    content = f.read()
                has_deps = 'aiohttp' in content and 'pydantic' in content
                config_tests.append(("Requirements file content", has_deps, "Contains dependencies" if has_deps else "Missing dependencies"))
            except Exception as e:
                config_tests.append(("Requirements file read", False, "", str(e)))
        else:
            config_tests.append(("Requirements file exists", False, "File not found"))

        # Test main jarvis.py structure
        jarvis_file = self.base_path / "jarvis.py"
        if jarvis_file.exists():
            try:
                with open(jarvis_file, 'r') as f:
                    content = f.read()
                has_main = 'if __name__ == "__main__":' in content
                has_class = 'class' in content
                config_tests.append(("Main file structure", has_main and has_class, "Contains main entry point"))
            except Exception as e:
                config_tests.append(("Main file read", False, "", str(e)))

        all_passed = True
        for test_name, passed, details, *error in config_tests:
            error_msg = error[0] if error else ""
            self.add_result(test_name, passed, 0.0, details, error_msg)
            if not passed:
                all_passed = False

        return all_passed

    def test_termux_environment(self) -> bool:
        """Test Termux environment"""
        print_test_header("Environment Tests")

        env_tests = []

        # Check Termux indicators
        termux_indicators = [
            ('TERMUX_VERSION', os.environ.get('TERMUX_VERSION')),
            ('PREFIX', os.environ.get('PREFIX', '')),
            ('SHELL', os.environ.get('SHELL', ''))
        ]

        is_termux = any('termux' in str(value).lower() for _, value in termux_indicators)
        env_tests.append(("Termux environment", is_termux, "Termux detected" if is_termux else "Non-Termux environment"))

        # Check system commands
        system_commands = ['python', 'pkg', 'git']
        for cmd in system_commands:
            try:
                result = subprocess.run(['which', cmd], capture_output=True, text=True, timeout=5)
                exists = result.returncode == 0
                env_tests.append((f"Command: {cmd}", exists, "Available" if exists else "Not found"))
            except Exception:
                env_tests.append((f"Command: {cmd}", False, "", "Command check failed"))

        # Check Termux-API
        try:
            result = subprocess.run(['which', 'termux-api'], capture_output=True, text=True, timeout=5)
            api_available = result.returncode == 0
            env_tests.append(("Termux-API", api_available, "Available" if api_available else "Not installed"))
        except Exception:
            env_tests.append(("Termux-API", False, "", "Check failed"))

        all_passed = True
        for test_name, passed, details, *error in env_tests:
            error_msg = error[0] if error else ""
            self.add_result(test_name, passed, 0.0, details, error_msg)
            if not passed and test_name != "Termux environment":  # Non-Termux is OK
                all_passed = False

        return all_passed

    def test_core_functionality(self) -> bool:
        """Test core functionality"""
        print_test_header("Core Functionality Tests")

        functionality_tests = []

        # Test basic async functionality
        try:
            async def test_async():
                await asyncio.sleep(0.1)
                return True

            result = asyncio.run(test_async())
            functionality_tests.append(("Async functionality", result, "Async operations work"))
        except Exception as e:
            functionality_tests.append(("Async functionality", False, "", str(e)))

        # Test JSON operations
        try:
            test_data = {"test": "data", "number": 42}
            json_str = json.dumps(test_data)
            parsed = json.loads(json_str)
            json_works = parsed == test_data
            functionality_tests.append(("JSON operations", json_works, "JSON serialization works"))
        except Exception as e:
            functionality_tests.append(("JSON operations", False, "", str(e)))

        # Test file operations
        try:
            test_file = self.base_path / "test_write.tmp"
            test_file.write_text("test content")
            content = test_file.read_text()
            test_file.unlink()
            file_works = content == "test content"
            functionality_tests.append(("File operations", file_works, "File I/O works"))
        except Exception as e:
            functionality_tests.append(("File operations", False, "", str(e)))

        all_passed = True
        for test_name, passed, details, *error in functionality_tests:
            error_msg = error[0] if error else ""
            self.add_result(test_name, passed, 0.0, details, error_msg)
            if not passed:
                all_passed = False

        return all_passed

    def test_memory_usage(self) -> bool:
        """Test memory usage"""
        print_test_header("Performance Tests")

        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            # Check if memory usage is reasonable (< 100MB for basic system)
            memory_ok = memory_mb < 100
            self.add_result("Memory usage", memory_ok, 0.0, f"{memory_mb:.1f}MB")

            return memory_ok

        except ImportError:
            self.add_result("Memory monitoring", False, 0.0, "", "psutil not available")
            return True  # Not critical
        except Exception as e:
            self.add_result("Memory monitoring", False, 0.0, "", str(e))
            return False

    def test_error_handling(self) -> bool:
        """Test error handling"""
        print_test_header("Error Handling Tests")

        error_tests = []

        # Test import error handling
        try:
            try:
                __import__("nonexistent_module_xyz")
                error_tests.append(("Import error handling", False, "", "Should have raised ImportError"))
            except ImportError:
                error_tests.append(("Import error handling", True, "ImportError properly caught"))
        except Exception as e:
            error_tests.append(("Import error handling", False, "", str(e)))

        # Test file error handling
        try:
            try:
                with open("/nonexistent/path/file.xyz", 'r') as f:
                    pass
                error_tests.append(("File error handling", False, "", "Should have raised FileNotFoundError"))
            except FileNotFoundError:
                error_tests.append(("File error handling", True, "FileNotFoundError properly caught"))
        except Exception as e:
            error_tests.append(("File error handling", False, "", str(e)))

        all_passed = True
        for test_name, passed, details, *error in error_tests:
            error_msg = error[0] if error else ""
            self.add_result(test_name, passed, 0.0, details, error_msg)
            if not passed:
                all_passed = False

        return all_passed

    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        end_time = time.time()
        duration = end_time - self.start_time

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                JARVIS v15 Test Report                          ║
╚══════════════════════════════════════════════════════════════╝

📊 Test Summary:
   • Total Tests: {total_tests}
   • Passed: {passed_tests} ({success_rate:.1f}%)
   • Failed: {failed_tests}
   • Duration: {duration:.1f} seconds
   • Status: {'✅ ALL TESTS PASSED' if failed_tests == 0 else '⚠️  SOME TESTS FAILED'}

📋 Test Results:
"""

        for result in self.test_results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            report += f"   {status} {result.name}"
            if result.details:
                report += f" - {result.details}"
            if result.error:
                report += f" ({result.error})"
            report += "\n"

        if failed_tests > 0:
            report += f"\n⚠️  Failed Tests Details:\n"
            for result in self.test_results:
                if not result.passed:
                    report += f"   • {result.name}: {result.error or result.details}\n"

        report += f"""
💡 Recommendations:
"""

        if failed_tests == 0:
            report += "   • All systems ready for deployment\n"
            report += "   • Run 'python jarvis.py' to start JARVIS\n"
        else:
            report += "   • Fix failed tests before deployment\n"
            report += "   • Check error messages above for details\n"
            report += "   • Ensure all dependencies are properly installed\n"

        report += f"""
🔧 System Information:
   • Python: {sys.version.split()[0]}
   • Platform: {platform.system()} {platform.release()}
   • Architecture: {platform.machine()}
   • Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

═══════════════════════════════════════════════════════════════
"""

        return report

    def save_test_report(self):
        """Save test report"""
        try:
            report = self.generate_test_report()
            report_file = self.base_path / "TEST_REPORT.txt"

            with open(report_file, 'w') as f:
                f.write(report)

            print(f"📄 Test report saved to: {report_file}")

            # Also save JSON data
            json_file = self.base_path / "test_results.json"
            json_data = {
                'summary': {
                    'total_tests': len(self.test_results),
                    'passed_tests': sum(1 for r in self.test_results if r.passed),
                    'failed_tests': sum(1 for r in self.test_results if not r.passed),
                    'duration': time.time() - self.start_time,
                    'timestamp': datetime.now().isoformat()
                },
                'results': [
                    {
                        'name': r.name,
                        'passed': r.passed,
                        'duration': r.duration,
                        'details': r.details,
                        'error': r.error,
                        'timestamp': r.timestamp.isoformat()
                    }
                    for r in self.test_results
                ]
            }

            with open(json_file, 'w') as f:
                json.dump(json_data, f, indent=2)

        except Exception as e:
            print(f"⚠️  Failed to save test report: {e}")

    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("🧪 Starting JARVIS v15 Comprehensive Testing Suite")
        print("=" * 60)

        # Test categories
        test_categories = [
            ("File Structure", self.test_file_structure),
            ("Python Syntax", self.test_python_syntax),
            ("Configuration", self.test_configuration_files),
            ("Module Imports", self.test_imports),
            ("Environment", self.test_termux_environment),
            ("Core Functionality", self.test_core_functionality),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_memory_usage)
        ]

        all_passed = True

        for category_name, test_func in test_categories:
            try:
                category_passed = self.run_test(category_name, test_func)
                if not category_passed:
                    all_passed = False
            except Exception as e:
                print(f"❌ Test category '{category_name}' crashed: {e}")
                self.add_result(f"Category: {category_name}", False, 0.0, "", str(e))
                all_passed = False

        # Generate and display report
        report = self.generate_test_report()
        print(report)

        # Save report
        self.save_test_report()

        return all_passed

def main():
    """Main test function"""
    tester = SystemTester()

    try:
        all_passed = tester.run_all_tests()

        if all_passed:
            print("\n🎉 All tests passed! JARVIS v15 is ready for deployment.")
            return 0
        else:
            print("\n⚠️  Some tests failed. Please review the report above.")
            return 1

    except KeyboardInterrupt:
        print("\n🛑 Testing cancelled by user")
        return 1
    except Exception as e:
        print(f"\n💥 Testing suite crashed: {e}")
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    import platform
    sys.exit(main())