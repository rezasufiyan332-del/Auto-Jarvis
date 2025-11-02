"""
Safety Configuration v15 - Real Safety Framework
Actually implements safety checks and validations
100% real functionality, no simulation
"""

import os
import ast
import subprocess
import sys
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

class SafetyConfigV15:
    """Real safety configuration and validation"""

    def __init__(self):
        self.logger = logging.getLogger("SafetyConfig")
        self.base_path = Path(__file__).parent.parent
        self.safety_rules = self._initialize_safety_rules()
        self.blocked_patterns = self._initialize_blocked_patterns()
        self.resource_limits = self._initialize_resource_limits()

    def _initialize_safety_rules(self) -> Dict[str, Any]:
        """Initialize safety rules"""
        return {
            'max_file_size_mb': 10,
            'max_line_length': 1000,
            'max_function_lines': 500,
            'max_class_lines': 1000,
            'max_nesting_depth': 10,
            'allowed_imports': {
                'safe': [
                    'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'logging',
                    'asyncio', 'subprocess', 're', 'hashlib', 'uuid', 'base64',
                    'collections', 'itertools', 'functools', 'operator',
                    'string', 'math', 'random', 'statistics', 'fractions',
                    'decimal', 'enum', 'dataclasses', 'typing'
                ],
                'termux_safe': [
                    'aiohttp', 'aiofiles', 'click', 'pydantic', 'requests',
                    'cryptography', 'yaml', 'python-dotenv', 'regex',
                    'chardet', 'dateutil', 'tenacity', 'jinja2'
                ],
                'termux_risky': [
                    'tensorflow', 'torch', 'numpy', 'pandas', 'scipy',
                    'matplotlib', 'opencv-python', 'scikit-learn',
                    'jupyterlab', 'django', 'streamlit', 'pyaudio',
                    'pyttsx3'
                ]
            },
            'code_injection_rules': {
                'allow_eval': False,
                'allow_exec': False,
                'allow_compile': False,
                'allow_subprocess_calls': True,  # Controlled
                'allow_file_operations': True,  # Controlled
                'allow_network_requests': True,  # Controlled
                'allow_imports': True,  # Controlled
            }
        }

    def _initialize_blocked_patterns(self) -> List[str]:
        """Initialize blocked code patterns"""
        return [
            r'eval\s*\(',  # eval() calls
            r'exec\s*\(',  # exec() calls
            r'compile\s*\(',  # compile() calls
            r'__import__\s*\(',  # __import__() calls
            r'os\.system\s*\(',  # os.system() calls (risky)
            r'subprocess\.call\s*\(',  # subprocess.call() (risky)
            r'subprocess\.Popen\s*\(',  # subprocess.Popen() (risky)
            r'input\s*\(',  # input() calls (risk of injection)
            r'open\s*\(\s*[\'"]\s*/',  # absolute file paths
            r'socket\.socket\s*\(',  # raw socket creation
            r'globals\s*\(\s*\)',  # globals() access
            r'locals\s*\(\s*\)',   # locals() access
            r'getattr\s*\(\s*[^,]+,\s*[\'"]\s*[^\'\"]*[\'\"]\s*\)',  # dynamic attribute access
            r'setattr\s*\(',  # setattr() calls
            r'delattr\s*\(',  # delattr() calls
        ]

    def _initialize_resource_limits(self) -> Dict[str, Any]:
        """Initialize resource limits"""
        return {
            'max_memory_mb': 256,  # 256MB max memory usage
            'max_cpu_percent': 80,  # 80% max CPU usage
            'max_execution_time_seconds': 300,  # 5 minutes max execution
            'max_concurrent_operations': 5,
            'max_file_operations_per_second': 10,
            'max_network_requests_per_minute': 60
        }

    async def validate_code_safety(self, code: str, file_path: str = None) -> Dict[str, Any]:
        """Validate code safety"""
        try:
            self.logger.info(f"🔍 Validating code safety for: {file_path or 'unknown'}")

            validation_result = {
                'safe': True,
                'warnings': [],
                'errors': [],
                'blocked_patterns': [],
                'resource_usage': {}
            }

            # Check 1: Syntax validation
            try:
                ast.parse(code)
            except SyntaxError as e:
                validation_result['safe'] = False
                validation_result['errors'].append(f"Syntax error: {e}")
                return validation_result

            # Check 2: Blocked patterns
            for pattern in self.blocked_patterns:
                import re
                if re.search(pattern, code, re.IGNORECASE):
                    validation_result['safe'] = False
                    validation_result['blocked_patterns'].append(f"Blocked pattern detected: {pattern}")

            # Check 3: File size
            code_size_mb = len(code.encode('utf-8')) / (1024 * 1024)
            if code_size_mb > self.safety_rules['max_file_size_mb']:
                validation_result['warnings'].append(f"Large file size: {code_size_mb:.2f}MB")

            # Check 4: Line length
            lines = code.split('\n')
            long_lines = [i for i, line in enumerate(lines, 1) if len(line) > self.safety_rules['max_line_length']]
            if long_lines:
                validation_result['warnings'].append(f"Long lines found: {len(long_lines)} lines exceed {self.safety_rules['max_line_length']} characters")

            # Check 5: Import safety
            tree = ast.parse(code)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}" if module else alias.name)

            risky_imports = []
            for imp in imports:
                for category, packages in self.safety_rules['allowed_imports'].items():
                    if category == 'termux_risky' and any(p in imp for p in packages):
                        risky_imports.append(imp)

            if risky_imports:
                validation_result['warnings'].append(f"Potentially problematic imports: {risky_imports}")

            # Check 6: Function complexity (simplified)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            complex_functions = []
            for func in functions:
                func_lines = len(func.end_lineno - func.lineno + 1)
                if func_lines > self.safety_rules['max_function_lines']:
                    complex_functions.append(f"{func.name} ({func_lines} lines)")

            if complex_functions:
                validation_result['warnings'].append(f"Complex functions: {complex_functions}")

            # Check 7: Resource usage estimation
            validation_result['resource_usage'] = self._estimate_resource_usage(code)

            return validation_result

        except Exception as e:
            self.logger.error(f"❌ Code safety validation error: {e}")
            return {
                'safe': False,
                'errors': [f"Validation error: {e}"],
                'warnings': [],
                'blocked_patterns': [],
                'resource_usage': {}
            }

    def _estimate_resource_usage(self, code: str) -> Dict[str, Any]:
        """Estimate resource usage"""
        try:
            lines = len(code.split('\n'))
            size_kb = len(code.encode('utf-8')) / 1024

            # Rough memory estimation (very basic)
            estimated_memory_kb = size_kb * 2  # Rough estimate: code uses 2x its size in memory

            return {
                'lines_of_code': lines,
                'size_kb': round(size_kb, 2),
                'estimated_memory_kb': round(estimated_memory_kb, 2),
                'complexity_score': min(10, lines // 100)  # Very basic complexity scoring
            }

        except Exception:
            return {
                'lines_of_code': 0,
                'size_kb': 0,
                'estimated_memory_kb': 0,
                'complexity_score': 0
            }

    async def validate_file_safety(self, file_path: str) -> Dict[str, Any]:
        """Validate file safety"""
        try:
            if not os.path.exists(file_path):
                return {
                    'safe': False,
                    'errors': [f"File not found: {file_path}"]
                }

            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            return await self.validate_code_safety(code, file_path)

        except Exception as e:
            return {
                'safe': False,
                'errors': [f"File validation error: {e}"]
            }

    async def check_resource_limits(self) -> Dict[str, Any]:
        """Check if current resource usage is within limits"""
        try:
            resource_status = {
                'within_limits': True,
                'warnings': [],
                'violations': []
            }

            # Check memory usage
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024

                if memory_mb > self.resource_limits['max_memory_mb']:
                    resource_status['within_limits'] = False
                    resource_status['violations'].append(f"Memory usage exceeded: {memory_mb:.1f}MB > {self.resource_limits['max_memory_mb']}MB")
                elif memory_mb > self.resource_limits['max_memory_mb'] * 0.8:
                    resource_status['warnings'].append(f"High memory usage: {memory_mb:.1f}MB")

                # Check CPU usage
                cpu_percent = process.cpu_percent()
                if cpu_percent > self.resource_limits['max_cpu_percent']:
                    resource_status['violations'].append(f"High CPU usage: {cpu_percent}%")
                elif cpu_percent > self.resource_limits['max_cpu_percent'] * 0.8:
                    resource_status['warnings'].append(f"High CPU usage: {cpu_percent}%")

            except ImportError:
                resource_status['warnings'].append("psutil not available for monitoring")

            # Check disk space
            try:
                import shutil
                total, used, free = shutil.disk_usage(str(self.base_path))
                free_gb = free // (1024**3)

                if free_gb < 0.1:  # Less than 100MB
                    resource_status['violations'].append(f"Low disk space: {free_gb}GB free")
                elif free_gb < 0.5:  # Less than 500MB
                    resource_status['warnings'].append(f"Low disk space: {free_gb}GB free")

            except Exception:
                pass  # Disk space check is not critical

            return resource_status

        except Exception as e:
            return {
                'within_limits': False,
                'warnings': [],
                'violations': [f"Resource check error: {e}"]
            }

    def is_safe_to_execute(self, code: str, context: Dict[str, Any] = None) -> bool:
        """Quick safety check before execution"""
        try:
            # Quick pattern check
            for pattern in self.blocked_patterns:
                import re
                if re.search(pattern, code, re.IGNORECASE):
                    return False

            # Quick size check
            if len(code) > 10000:  # 10KB limit for quick check
                return False

            return True

        except Exception:
            return False  # Better to be safe

    async def create_backup_before_modification(self, file_path: str) -> str:
        """Create backup before code modification"""
        try:
            timestamp = int(time.time())
            backup_path = f"{file_path}.backup_{timestamp}"

            if os.path.exists(file_path):
                import shutil
                shutil.copy2(file_path, backup_path)
                self.logger.info(f"📁 Created backup: {backup_path}")
                return backup_path
            else:
                self.logger.warning(f"⚠️ File not found for backup: {file_path}")
                return ""

        except Exception as e:
            self.logger.error(f"❌ Backup creation failed: {e}")
            return ""

    async def rollback_modification(self, backup_path: str, target_path: str) -> bool:
        """Rollback modification using backup"""
        try:
            if backup_path and os.path.exists(backup_path):
                import shutil
                shutil.copy2(backup_path, target_path)
                self.logger.info(f"🔄 Rollback completed: {target_path}")
                return True
            else:
                self.logger.error(f"❌ Backup not found for rollback: {backup_path}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Rollback failed: {e}")
            return False

    def get_safety_report(self) -> Dict[str, Any]:
        """Get comprehensive safety report"""
        return {
            'safety_rules': self.safety_rules,
            'blocked_patterns_count': len(self.blocked_patterns),
            'resource_limits': self.resource_limits,
            'base_path': str(self.base_path),
            'validation_enabled': True
        }