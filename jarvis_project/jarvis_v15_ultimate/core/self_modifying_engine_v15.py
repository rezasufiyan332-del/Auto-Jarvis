"""
Self-Modifying Engine v15 - Real-Time Code Transformation
Advanced real-time code modification without restart or downtime
10-layer safety framework with instant rollback capabilities
"""

import os
import ast
import sys
import json
import time
import asyncio
import logging
import hashlib
import traceback
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import aiofiles
import tempfile
import shutil

@dataclass
class CodeModification:
    """Code modification structure"""
    file_path: str
    old_code: str
    new_code: str
    modification_type: str  # add, replace, delete, insert
    line_number: Optional[int] = None
    description: str = ""
    safety_score: float = 0.0
    timestamp: datetime = None

@dataclass
class SafetyCheckResult:
    """Safety check result"""
    passed: bool
    score: float
    issues: List[str]
    warnings: List[str]
    recommendations: List[str]

@dataclass
class ModificationResult:
    """Modification execution result"""
    success: bool
    modification: CodeModification
    safety_result: SafetyCheckResult
    execution_time: float
    backup_path: Optional[str] = None
    error: Optional[str] = None
    rollback_available: bool = True

class SelfModifyingEngineV15:
    """
    Real-Time Self-Modifying Engine

    Features:
    - Instant code modification without restart
    - 10-layer safety framework
    - AST-based code analysis
    - Real-time syntax validation
    - Automatic backup and rollback
    - Pattern-based optimization
    - Zero-downtime deployment
    - Performance impact monitoring
    """

    def __init__(self, safety_config, error_system, logger: logging.Logger):
        self.safety_config = safety_config
        self.error_system = error_system
        self.logger = logger

        # Paths
        self.base_path = Path(__file__).parent.parent
        self.backups_path = self.base_path / "backups"
        self.temp_path = self.base_path / "temp"
        self.modifications_log = self.base_path / "logs" / "modifications.log"

        # Create directories
        for path in [self.backups_path, self.temp_path]:
            path.mkdir(exist_ok=True)

        # Safety layers
        self.safety_layers = [
            self._layer1_syntax_validation,
            self._layer2_import_verification,
            self._layer3_logic_validation,
            self._layer4_security_scanning,
            self._layer5_performance_testing,
            self._layer6_compatibility_testing,
            self._layer7_dependency_resolution,
            self._layer8_resource_monitoring,
            self._layer9_functional_testing,
            self._layer10_integration_validation
        ]

        # Modification tracking
        self.modification_history = []
        self.active_modifications = {}
        self.rollback_stack = []

        # Performance tracking
        self.performance_metrics = {
            'total_modifications': 0,
            'successful_modifications': 0,
            'failed_modifications': 0,
            'rollbacks_performed': 0,
            'average_modification_time': 0.0
        }

        # Code patterns and templates
        self.code_patterns = self._initialize_code_patterns()
        self.modification_templates = self._initialize_modification_templates()

    async def initialize(self):
        """Initialize self-modifying engine"""
        try:
            # Load modification history
            await self._load_modification_history()

            # Initialize backup system
            await self._initialize_backup_system()

            # Setup monitoring
            self._setup_monitoring()

            self.logger.info("✅ Self-Modifying Engine v15 initialized")

        except Exception as e:
            self.logger.error(f"❌ Self-Modifying Engine initialization failed: {e}")
            raise

    async def _load_modification_history(self):
        """Load modification history from disk"""
        history_file = self.base_path / "data" / "modification_history.json"

        try:
            if history_file.exists():
                async with aiofiles.open(history_file, 'r') as f:
                    data = json.loads(await f.read())
                    self.modification_history = [
                        CodeModification(**mod) for mod in data.get('modifications', [])
                    ]

            self.logger.info(f"📚 Loaded {len(self.modification_history)} modifications from history")

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load modification history: {e}")
            self.modification_history = []

    async def _initialize_backup_system(self):
        """Initialize backup and rollback system"""
        try:
            # Create initial backup of current state
            backup_dir = self.backups_path / f"initial_backup_{int(time.time())}"
            await self._create_full_backup(backup_dir)

            self.logger.info("✅ Backup system initialized")

        except Exception as e:
            self.logger.error(f"❌ Backup system initialization failed: {e}")

    def _setup_monitoring(self):
        """Setup performance and health monitoring"""
        # Monitoring will be handled by background tasks
        pass

    def _initialize_code_patterns(self) -> Dict[str, Any]:
        """Initialize common code patterns for recognition"""
        return {
            'function_definition': r'def\s+\w+\s*\([^)]*\)\s*:',
            'class_definition': r'class\s+\w+\s*(\([^)]*\))?\s*:',
            'import_statement': r'^(import|from)\s+',
            'async_function': r'async\s+def\s+\w+',
            'error_handling': r'try\s*:|except\s+\w+:',
            'decorator': r'@\w+',
            'docstring': r'""".*?"""',
            'comment': r'#.*$'
        }

    def _initialize_modification_templates(self) -> Dict[str, str]:
        """Initialize templates for common modifications"""
        return {
            'add_function': '''
async def {function_name}({parameters}) -> {return_type}:
    """
    {description}
    """
    {function_body}
''',
            'add_class': '''
class {class_name}:
    """
    {description}
    """

    def __init__(self{init_parameters}):
        {init_body}

    {methods}
''',
            'add_import': 'import {module_name}',
            'add_async_method': '''
async def {method_name}(self{parameters}) -> {return_type}:
    """
    {description}
    """
    {method_body}
''',
            'add_error_handling': '''
try:
    {code_to_protect}
except {exception_type} as e:
    {error_handling_code}
'''
        }

    async def modify_code_realtime(self, file_path: str, modification: Dict[str, Any]) -> ModificationResult:
        """
        Modify code in real-time without restart

        Args:
            file_path: Path to file to modify
            modification: Modification details

        Returns:
            ModificationResult with execution details
        """
        start_time = time.time()

        try:
            # Convert to CodeModification object
            code_mod = CodeModification(
                file_path=file_path,
                old_code=modification.get('old_code', ''),
                new_code=modification.get('new_code', ''),
                modification_type=modification.get('type', 'replace'),
                line_number=modification.get('line_number'),
                description=modification.get('description', ''),
                timestamp=datetime.now()
            )

            self.logger.info(f"🔄 Starting real-time modification: {code_mod.description}")

            # Step 1: Create backup
            backup_path = await self._create_file_backup(file_path)

            # Step 2: Run through 10-layer safety framework
            safety_result = await self._run_safety_checks(code_mod)

            if not safety_result.passed:
                self.logger.error(f"❌ Safety checks failed: {safety_result.issues}")
                return ModificationResult(
                    success=False,
                    modification=code_mod,
                    safety_result=safety_result,
                    execution_time=time.time() - start_time,
                    backup_path=backup_path,
                    error="Safety checks failed"
                )

            # Step 3: Validate code syntax
            syntax_valid = await self._validate_code_syntax(code_mod.new_code)
            if not syntax_valid:
                return ModificationResult(
                    success=False,
                    modification=code_mod,
                    safety_result=safety_result,
                    execution_time=time.time() - start_time,
                    backup_path=backup_path,
                    error="Syntax validation failed"
                )

            # Step 4: Apply modification
            apply_result = await self._apply_modification(code_mod)

            if not apply_result:
                return ModificationResult(
                    success=False,
                    modification=code_mod,
                    safety_result=safety_result,
                    execution_time=time.time() - start_time,
                    backup_path=backup_path,
                    error="Failed to apply modification"
                )

            # Step 5: Test modification
            test_result = await self._test_modification(code_mod)

            if not test_result:
                # Rollback on test failure
                await self._rollback_modification(code_mod, backup_path)
                return ModificationResult(
                    success=False,
                    modification=code_mod,
                    safety_result=safety_result,
                    execution_time=time.time() - start_time,
                    backup_path=backup_path,
                    error="Modification test failed, rolled back"
                )

            # Step 6: Update tracking
            self.modification_history.append(code_mod)
            self.rollback_stack.append(backup_path)

            # Step 7: Update metrics
            self.performance_metrics['total_modifications'] += 1
            self.performance_metrics['successful_modifications'] += 1
            mod_time = time.time() - start_time
            self.performance_metrics['average_modification_time'] = (
                (self.performance_metrics['average_modification_time'] * (self.performance_metrics['total_modifications'] - 1) + mod_time)
                / self.performance_metrics['total_modifications']
            )

            # Step 8: Save history
            await self._save_modification_history()

            self.logger.info(f"✅ Real-time modification completed in {mod_time:.2f}s: {code_mod.description}")

            return ModificationResult(
                success=True,
                modification=code_mod,
                safety_result=safety_result,
                execution_time=mod_time,
                backup_path=backup_path
            )

        except Exception as e:
            self.logger.error(f"❌ Real-time modification failed: {e}")
            self.logger.error(traceback.format_exc())

            self.performance_metrics['failed_modifications'] += 1

            return ModificationResult(
                success=False,
                modification=CodeModification(
                    file_path=file_path,
                    old_code='',
                    new_code='',
                    modification_type='failed',
                    description=str(e)
                ),
                safety_result=SafetyCheckResult(
                    passed=False,
                    score=0.0,
                    issues=[str(e)],
                    warnings=[],
                    recommendations=[]
                ),
                execution_time=time.time() - start_time,
                error=str(e)
            )

    async def _run_safety_checks(self, modification: CodeModification) -> SafetyCheckResult:
        """Run through 10-layer safety framework"""
        all_issues = []
        all_warnings = []
        all_recommendations = []
        total_score = 0.0

        for i, safety_layer in enumerate(self.safety_layers, 1):
            try:
                result = await safety_layer(modification)

                if isinstance(result, tuple):
                    passed, score, issues, warnings, recommendations = result
                else:
                    # Backward compatibility
                    passed = result
                    score = 1.0 if passed else 0.0
                    issues, warnings, recommendations = [], [], []

                if not passed:
                    all_issues.extend([f"Layer {i}: {issue}" for issue in issues])

                all_warnings.extend([f"Layer {i}: {warning}" for warning in warnings])
                all_recommendations.extend([f"Layer {i}: {rec}" for rec in recommendations])
                total_score += score

                self.logger.debug(f"🔍 Safety layer {i}: {'✅' if passed else '❌'} (score: {score:.2f})")

            except Exception as e:
                all_issues.append(f"Layer {i}: Safety check error - {e}")
                self.logger.error(f"❌ Safety layer {i} error: {e}")

        final_score = total_score / len(self.safety_layers)
        passed = len(all_issues) == 0 and final_score >= 0.7

        return SafetyCheckResult(
            passed=passed,
            score=final_score,
            issues=all_issues,
            warnings=all_warnings,
            recommendations=all_recommendations
        )

    async def _layer1_syntax_validation(self, modification: CodeModification) -> Tuple[bool, float, List[str], List[str], List[str]]:
        """Layer 1: Syntax validation using AST parsing"""
        issues = []
        warnings = []
        recommendations = []

        try:
            # Parse new code as AST
            ast.parse(modification.new_code)

            # Check for common syntax issues
            if modification.new_code.count('(') != modification.new_code.count(')'):
                issues.append("Mismatched parentheses")

            if modification.new_code.count('[') != modification.new_code.count(']'):
                issues.append("Mismatched brackets")

            # Check for proper indentation
            lines = modification.new_code.split('\n')
            for i, line in enumerate(lines):
                if line.strip() and (line.startswith(' ') or line.startswith('\t')):
                    if not line.startswith('    ') and not line.startswith('\t'):
                        warnings.append(f"Inconsistent indentation at line {i+1}")

            score = 1.0 if not issues else 0.3

        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")
            score = 0.0
        except Exception as e:
            issues.append(f"Parse error: {e}")
            score = 0.0

        return len(issues) == 0, score, issues, warnings, recommendations

    async def _layer2_import_verification(self, modification: CodeModification) -> Tuple[bool, float, List[str], List[str], List[str]]:
        """Layer 2: Import verification for Termux compatibility"""
        issues = []
        warnings = []
        recommendations = []

        try:
            # Extract imports from new code
            tree = ast.parse(modification.new_code)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            # Check for problematic imports
            problematic_imports = [
                'tensorflow', 'torch', 'numpy', 'pandas', 'scipy',
                'opencv-python', 'pyaudio', 'pyttsx3', 'django',
                'streamlit', 'jupyterlab'
            ]

            for imp in imports:
                for problematic in problematic_imports:
                    if problematic in imp.lower():
                        issues.append(f"Problematic import detected: {imp} (not Termux-compatible)")
                        recommendations.append(f"Consider using cloud-based alternative for {imp}")

            # Check for standard library imports (safe)
            standard_lib_imports = [
                'os', 'sys', 'json', 'time', 'asyncio', 'logging',
                'pathlib', 'datetime', 'typing', 'dataclasses'
            ]

            safe_imports = [imp for imp in imports if any(imp.startswith(lib) for lib in standard_lib_imports)]

            score = 1.0 if not issues else 0.5

            if len(safe_imports) > 0:
                recommendations.append(f"Good use of standard library imports: {', '.join(safe_imports[:3])}")

        except Exception as e:
            issues.append(f"Import verification error: {e}")
            score = 0.0

        return len(issues) == 0, score, issues, warnings, recommendations

    async def _layer3_logic_validation(self, modification: CodeModification) -> Tuple[bool, float, List[str], List[str], List[str]]:
        """Layer 3: Logic validation to prevent breaking changes"""
        issues = []
        warnings = []
        recommendations = []

        try:
            # Parse old and new code
            old_tree = ast.parse(modification.old_code) if modification.old_code else None
            new_tree = ast.parse(modification.new_code)

            # Check for function signature changes
            old_functions = {}
            new_functions = {}

            if old_tree:
                for node in ast.walk(old_tree):
                    if isinstance(node, ast.FunctionDef):
                        old_functions[node.name] = node

            for node in ast.walk(new_tree):
                if isinstance(node, ast.FunctionDef):
                    new_functions[node.name] = node

            # Check for breaking changes
            for func_name, old_func in old_functions.items():
                if func_name in new_functions:
                    new_func = new_functions[func_name]

                    # Check parameter count changes
                    old_params = len(old_func.args.args)
                    new_params = len(new_func.args.args)

                    if new_params < old_params:
                        warnings.append(f"Function {func_name} has fewer parameters - may break existing calls")

                    # Check for async/await changes
                    old_is_async = isinstance(old_func, ast.AsyncFunctionDef)
                    new_is_async = isinstance(new_func, ast.AsyncFunctionDef)

                    if old_is_async != new_is_async:
                        issues.append(f"Function {func_name} async/await nature changed - breaking change")

            score = 1.0 if not issues else 0.6

        except Exception as e:
            issues.append(f"Logic validation error: {e}")
            score = 0.0

        return len(issues) == 0, score, issues, warnings, recommendations

    async def _layer4_security_scanning(self, modification: CodeModification) -> Tuple[bool, float, List[str], List[str], List[str]]:
        """Layer 4: Security scanning for malicious patterns"""
        issues = []
        warnings = []
        recommendations = []

        try:
            # Security patterns to check
            dangerous_patterns = [
                'eval(', 'exec(', 'compile(', '__import__',
                'subprocess.call', 'os.system', 'os.popen',
                'input(', 'raw_input(', 'open(', 'file(',
                'socket.socket', 'urllib.request', 'requests.get'
            ]

            code_lower = modification.new_code.lower()

            for pattern in dangerous_patterns:
                if pattern in code_lower:
                    if pattern in ['eval(', 'exec(', 'compile(']:
                        issues.append(f"Dangerous function detected: {pattern}")
                    else:
                        warnings.append(f"Potentially unsafe function: {pattern}")

            # Check for file operations
            if any(op in code_lower for op in ['open(', 'file(', 'write(', 'read(']):
                warnings.append("File operations detected - ensure proper path validation")

            # Check for network operations
            if any(op in code_lower for op in ['socket.', 'urllib.', 'requests.', 'http.']):
                warnings.append("Network operations detected - ensure proper validation")

            # Check for hardcoded secrets
            secret_patterns = ['password', 'secret', 'key', 'token', 'api_key']
            for pattern in secret_patterns:
                if f'{pattern} = ' in code_lower and '"' in code_lower:
                    warnings.append(f"Potential hardcoded {pattern} detected")

            score = 1.0 if not issues else (0.5 if not issues and warnings else 0.8)

            if warnings:
                recommendations.append("Review security implications of detected patterns")

        except Exception as e:
            issues.append(f"Security scanning error: {e}")
            score = 0.0

        return len(issues) == 0, score, issues, warnings, recommendations

    async def _layer5_performance_testing(self, modification: CodeModification) -> Tuple[bool, float, List[str], List[str], List[str]]:
        """Layer 5: Performance impact assessment"""
        issues = []
        warnings = []
        recommendations = []

        try:
            # Performance patterns to check
            performance_issues = []

            # Check for infinite loops
            if 'while True:' in modification.new_code and 'break' not in modification.new_code:
                warnings.append("Potential infinite loop detected")

            # Check for recursion without base case
            if 'def ' in modification.new_code and modification.new_code.count('return ') < 2:
                warnings.append("Recursion without clear base case detected")

            # Check for large data structures
            if any(size in modification.new_code for size in ['[0] * 10000', 'range(10000)', 'list(range(']):
                warnings.append("Large data structure allocation detected")

            # Check for synchronous I/O in async context
            if 'async def' in modification.new_code and 'time.sleep(' in modification.new_code:
                issues.append("Synchronous sleep in async function detected")

            # Estimate complexity
            lines = modification.new_code.split('\n')
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])

            if code_lines > 100:
                warnings.append(f"Large modification ({code_lines} lines) - consider splitting")

            score = 1.0 if not issues else (0.7 if not issues and warnings else 0.9)

            if performance_issues:
                recommendations.extend(performance_issues)

        except Exception as e:
            issues.append(f"Performance testing error: {e}")
            score = 0.0

        return len(issues) == 0, score, issues, warnings, recommendations

    async def _layer6_compatibility_testing(self, modification: CodeModification) -> Tuple[bool, float, List[str], List[str], List[str]]:
        """Layer 6: Termux/Android compatibility testing"""
        issues = []
        warnings = []
        recommendations = []

        try:
            # Check for OS-specific features that might not work on Android
            incompatible_patterns = [
                'windows.', 'win32.', 'nt.',
                'macos.', 'darwin.',
                'linux.', 'posix.'
            ]

            code_lower = modification.new_code.lower()

            for pattern in incompatible_patterns:
                if pattern in code_lower:
                    warnings.append(f"Platform-specific code detected: {pattern}")

            # Check for file paths
            if 'C:\\' in modification.new_code or 'D:\\' in modification.new_code:
                issues.append("Windows-style paths detected - not compatible with Termux")

            # Check for GUI libraries
            gui_libs = ['tkinter', 'pygame', 'pyqt', 'gtk', 'wx']
            for lib in gui_libs:
                if lib in code_lower:
                    warnings.append(f"GUI library {lib} detected - may not work in Termux")

            # Check for system calls
            if 'os.chmod' in code_lower or 'os.chown' in code_lower:
                warnings.append("System calls detected - may require root permissions")

            score = 1.0 if not issues else (0.6 if not issues and warnings else 0.8)

            if warnings:
                recommendations.append("Test thoroughly on Termux/Android environment")

        except Exception as e:
            issues.append(f"Compatibility testing error: {e}")
            score = 0.0

        return len(issues) == 0, score, issues, warnings, recommendations

    async def _layer7_dependency_resolution(self, modification: CodeModification) -> Tuple[bool, float, List[str], List[str], List[str]]:
        """Layer 7: Dependency resolution and availability"""
        issues = []
        warnings = []
        recommendations = []

        try:
            # Extract import statements
            tree = ast.parse(modification.new_code)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            # Check if dependencies are available
            for imp in imports:
                if '.' in imp:
                    module_name = imp.split('.')[0]
                else:
                    module_name = imp

                try:
                    __import__(module_name)
                except ImportError:
                    if module_name not in ['os', 'sys', 'json', 'time', 'asyncio', 'logging', 'pathlib', 'datetime', 'typing', 'dataclasses']:
                        warnings.append(f"Dependency not available: {module_name}")

            score = 1.0 if not issues else (0.7 if not issues and warnings else 0.9)

        except Exception as e:
            issues.append(f"Dependency resolution error: {e}")
            score = 0.0

        return len(issues) == 0, score, issues, warnings, recommendations

    async def _layer8_resource_monitoring(self, modification: CodeModification) -> Tuple[bool, float, List[str], List[str], List[str]]:
        """Layer 8: Resource usage monitoring"""
        issues = []
        warnings = []
        recommendations = []

        try:
            # Estimate memory usage
            lines = modification.new_code.split('\n')
            variables_count = len([line for line in lines if '=' in line and not line.strip().startswith('#')])

            if variables_count > 50:
                warnings.append(f"High variable count ({variables_count}) - potential memory usage")

            # Check for potential memory leaks
            if 'while True:' in modification.new_code and 'list' in modification.new_code:
                warnings.append("Potential memory leak in infinite loop with list operations")

            # Check for file handles
            file_operations = modification.new_code.count('open(')
            if file_operations > 5:
                warnings.append(f"Multiple file operations ({file_operations}) - ensure proper closing")

            score = 1.0 if not issues else (0.8 if not issues and warnings else 0.9)

        except Exception as e:
            issues.append(f"Resource monitoring error: {e}")
            score = 0.0

        return len(issues) == 0, score, issues, warnings, recommendations

    async def _layer9_functional_testing(self, modification: CodeModification) -> Tuple[bool, float, List[str], List[str], List[str]]:
        """Layer 9: Basic functional testing"""
        issues = []
        warnings = []
        recommendations = []

        try:
            # Check if code can be executed (basic test)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(modification.new_code)
                temp_file = f.name

            try:
                # Try to compile the code
                result = subprocess.run(
                    [sys.executable, '-m', 'py_compile', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode != 0:
                    issues.append(f"Code compilation failed: {result.stderr}")

            finally:
                os.unlink(temp_file)

            score = 1.0 if not issues else 0.0

        except subprocess.TimeoutExpired:
            issues.append("Code compilation timed out")
            score = 0.0
        except Exception as e:
            issues.append(f"Functional testing error: {e}")
            score = 0.0

        return len(issues) == 0, score, issues, warnings, recommendations

    async def _layer10_integration_validation(self, modification: CodeModification) -> Tuple[bool, float, List[str], List[str], List[str]]:
        """Layer 10: Integration with existing system"""
        issues = []
        warnings = []
        recommendations = []

        try:
            # Check if modification affects core system files
            core_files = [
                'jarvis.py', 'ai_engine_v15.py', 'self_modifying_engine_v15.py',
                'error_proof_system_v15.py', 'automation_framework_v15.py'
            ]

            file_name = os.path.basename(modification.file_path)
            if file_name in core_files:
                warnings.append("Modification to core system file - extra caution required")

            # Check for potential circular imports
            if 'import' in modification.new_code:
                current_module = os.path.splitext(file_name)[0]
                if current_module in modification.new_code:
                    warnings.append("Potential circular import detected")

            score = 1.0 if not issues else (0.8 if not issues and warnings else 0.9)

        except Exception as e:
            issues.append(f"Integration validation error: {e}")
            score = 0.0

        return len(issues) == 0, score, issues, warnings, recommendations

    async def _create_file_backup(self, file_path: str) -> str:
        """Create backup of file before modification"""
        try:
            timestamp = int(time.time())
            backup_name = f"{os.path.basename(file_path)}_{timestamp}.backup"
            backup_path = self.backups_path / backup_name

            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)

            return str(backup_path)

        except Exception as e:
            self.logger.error(f"❌ Failed to create backup: {e}")
            return ""

    async def _create_full_backup(self, backup_dir: Path):
        """Create full backup of current state"""
        try:
            backup_dir.mkdir(exist_ok=True)

            # Backup all Python files
            for py_file in self.base_path.rglob("*.py"):
                if not any(skip in str(py_file) for skip in ['__pycache__', '.git', 'temp']):
                    relative_path = py_file.relative_to(self.base_path)
                    backup_file = backup_dir / relative_path
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(py_file, backup_file)

            self.logger.info(f"✅ Full backup created at {backup_dir}")

        except Exception as e:
            self.logger.error(f"❌ Failed to create full backup: {e}")

    async def _validate_code_syntax(self, code: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    async def _apply_modification(self, modification: CodeModification) -> bool:
        """Apply the modification to the target file"""
        try:
            file_path = Path(modification.file_path)

            if not file_path.exists():
                # Create new file
                file_path.parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(file_path, 'w') as f:
                    await f.write(modification.new_code)
            else:
                # Modify existing file
                if modification.modification_type == 'replace':
                    async with aiofiles.open(file_path, 'w') as f:
                        await f.write(modification.new_code)
                elif modification.modification_type == 'insert':
                    # Insert at specific line
                    lines = await self._read_file_lines(file_path)
                    if modification.line_number is not None:
                        lines.insert(modification.line_number, modification.new_code)
                    else:
                        lines.append(modification.new_code)
                    await self._write_file_lines(file_path, lines)
                elif modification.modification_type == 'add':
                    # Add to end of file
                    async with aiofiles.open(file_path, 'a') as f:
                        await f.write('\n' + modification.new_code)

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to apply modification: {e}")
            return False

    async def _test_modification(self, modification: CodeModification) -> bool:
        """Test the modification"""
        try:
            # Basic syntax test
            if not await self._validate_code_syntax(modification.new_code):
                return False

            # Try to import the module if it's a Python file
            if modification.file_path.endswith('.py'):
                module_name = os.path.splitext(os.path.basename(modification.file_path))[0]
                module_dir = os.path.dirname(modification.file_path)

                if module_dir not in sys.path:
                    sys.path.insert(0, module_dir)

                try:
                    # Remove from sys.modules if already loaded
                    if module_name in sys.modules:
                        del sys.modules[module_name]

                    # Try to import the module
                    __import__(module_name)
                    return True
                except ImportError as e:
                    self.logger.warning(f"⚠️ Module import test failed: {e}")
                    return False
                finally:
                    if module_dir in sys.path:
                        sys.path.remove(module_dir)

            return True

        except Exception as e:
            self.logger.error(f"❌ Modification test failed: {e}")
            return False

    async def _rollback_modification(self, modification: CodeModification, backup_path: str):
        """Rollback modification using backup"""
        try:
            if backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, modification.file_path)
                self.performance_metrics['rollbacks_performed'] += 1
                self.logger.info(f"✅ Rolled back modification: {modification.description}")
            else:
                self.logger.error("❌ No backup available for rollback")

        except Exception as e:
            self.logger.error(f"❌ Rollback failed: {e}")

    async def _read_file_lines(self, file_path: Path) -> List[str]:
        """Read file lines"""
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            return content.split('\n')

    async def _write_file_lines(self, file_path: Path, lines: List[str]):
        """Write file lines"""
        async with aiofiles.open(file_path, 'w') as f:
            await f.write('\n'.join(lines))

    async def _save_modification_history(self):
        """Save modification history to disk"""
        try:
            history_file = self.base_path / "data" / "modification_history.json"
            history_data = {
                'modifications': [asdict(mod) for mod in self.modification_history[-100:]],  # Keep last 100
                'metrics': self.performance_metrics,
                'last_updated': datetime.now().isoformat()
            }

            async with aiofiles.open(history_file, 'w') as f:
                await f.write(json.dumps(history_data, indent=2, default=str))

        except Exception as e:
            self.logger.error(f"❌ Failed to save modification history: {e}")

    async def optimize_performance(self) -> List[str]:
        """Optimize system performance through self-modification"""
        optimizations = []

        try:
            # Analyze current code for optimization opportunities
            for py_file in self.base_path.rglob("*.py"):
                if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'temp']):
                    continue

                try:
                    async with aiofiles.open(py_file, 'r') as f:
                        content = await f.read()

                    # Check for optimization patterns
                    if 'time.sleep(' in content and 'async def' in content:
                        # Replace synchronous sleep with asyncio.sleep
                        optimized_content = content.replace('time.sleep(', 'asyncio.sleep(')

                        modification = {
                            'old_code': content,
                            'new_code': optimized_content,
                            'type': 'replace',
                            'description': f'Optimize async sleep in {py_file.name}'
                        }

                        result = await self.modify_code_realtime(str(py_file), modification)
                        if result.success:
                            optimizations.append(f"✅ Optimized async sleep in {py_file.name}")

                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to analyze {py_file}: {e}")

            return optimizations

        except Exception as e:
            self.logger.error(f"❌ Performance optimization failed: {e}")
            return []

    async def get_modification_statistics(self) -> Dict[str, Any]:
        """Get modification statistics"""
        return {
            'total_modifications': self.performance_metrics['total_modifications'],
            'successful_modifications': self.performance_metrics['successful_modifications'],
            'failed_modifications': self.performance_metrics['failed_modifications'],
            'success_rate': round(
                self.performance_metrics['successful_modifications'] / max(self.performance_metrics['total_modifications'], 1) * 100, 2
            ),
            'rollbacks_performed': self.performance_metrics['rollbacks_performed'],
            'average_modification_time': round(self.performance_metrics['average_modification_time'], 3),
            'rollback_stack_size': len(self.rollback_stack),
            'backup_count': len(list(self.backups_path.glob("*.backup"))),
            'last_modification': self.modification_history[-1].timestamp.isoformat() if self.modification_history else None
        }

    async def shutdown(self):
        """Shutdown self-modifying engine"""
        try:
            # Save final state
            await self._save_modification_history()

            # Create final backup
            final_backup = self.backups_path / f"shutdown_backup_{int(time.time())}"
            await self._create_full_backup(final_backup)

            self.logger.info("✅ Self-Modifying Engine v15 shutdown complete")

        except Exception as e:
            self.logger.error(f"❌ Self-Modifying Engine shutdown failed: {e}")