#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS v14 Ultimate Launcher - Master Entry Point
=================================================

JARVIS v14 Ultimate के लिए Master Launcher System
सभी components को coordinate करने वाला central system

Features:
- Unified entry point for all v14 systems
- System initialization और startup
- Component coordination और orchestration  
- Error handling और recovery
- Performance monitoring integration
- Configuration management
- Service management (start/stop/restart)
- Health check और diagnostics

Author: JARVIS v14 Ultimate Team
Version: 14.0.0
"""

import os
import sys
import time
import json
import logging
import threading
import subprocess
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import traceback

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis_launcher.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class SystemComponent:
    """System component configuration"""
    name: str
    module_path: str
    class_name: str
    priority: int
    dependencies: List[str]
    auto_start: bool = True
    health_check_enabled: bool = True
    max_restart_attempts: int = 3
    restart_delay: float = 5.0
    status: str = "stopped"
    last_health_check: Optional[datetime] = None

@dataclass
class LauncherConfig:
    """Launcher configuration"""
    max_concurrent_components: int = 10
    health_check_interval: float = 30.0
    system_monitoring_enabled: bool = True
    auto_recovery_enabled: bool = True
    performance_tracking: bool = True
    error_logging_level: str = "INFO"
    backup_enabled: bool = True
    notification_enabled: bool = True
    web_dashboard_port: int = 8080
    api_port: int = 8081
    max_memory_usage_mb: int = 2048
    max_cpu_usage_percent: float = 80.0

class MasterLogger:
    """Enhanced logging system for launcher"""
    
    def __init__(self, log_dir: str = "jarvis_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create different log files for different purposes
        self.logger = logging.getLogger("JARVIS_Launcher")
        self.logger.setLevel(logging.DEBUG)
        
        # Component-specific loggers
        self.component_loggers = {}
        
    def get_component_logger(self, component_name: str) -> logging.Logger:
        """Get or create component-specific logger"""
        if component_name not in self.component_loggers:
            logger = logging.getLogger(f"JARVIS.{component_name}")
            logger.setLevel(logging.DEBUG)
            
            # File handler for component
            file_handler = logging.FileHandler(
                self.log_dir / f"{component_name.lower()}.log"
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(file_handler)
            
            self.component_loggers[component_name] = logger
            
        return self.component_loggers[component_name]

class ComponentHealthMonitor:
    """Health monitoring system for components"""
    
    def __init__(self, config: LauncherConfig, logger: MasterLogger):
        self.config = config
        self.logger = logger
        self.health_status = {}
        self.performance_metrics = {}
        self.error_history = {}
        self.monitoring_thread = None
        self.monitoring_active = False
        
    def start_monitoring(self):
        """Start health monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            self.logger.get_component_logger("HealthMonitor").info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.get_component_logger("HealthMonitor").info("Health monitoring stopped")
    
    def check_component_health(self, component: SystemComponent) -> Dict[str, Any]:
        """Check health of a specific component"""
        health_info = {
            "status": "unknown",
            "response_time": 0,
            "memory_usage": 0,
            "cpu_usage": 0,
            "errors": [],
            "last_check": datetime.now()
        }
        
        try:
            start_time = time.time()
            
            # Check if process is running
            if self._is_process_running(component.name):
                health_info["status"] = "running"
            else:
                health_info["status"] = "stopped"
                return health_info
            
            # Check response time
            response_time = self._check_component_response(component)
            health_info["response_time"] = response_time
            
            # Check resource usage
            if self.config.system_monitoring_enabled:
                health_info["memory_usage"] = self._get_process_memory_usage(component.name)
                health_info["cpu_usage"] = self._get_process_cpu_usage(component.name)
            
            # Check for errors
            health_info["errors"] = self._check_component_errors(component)
            
        except Exception as e:
            health_info["status"] = "error"
            health_info["errors"].append(str(e))
            self.logger.get_component_logger(component.name).error(f"Health check failed: {e}")
        
        finally:
            component.last_health_check = health_info["last_check"]
            self.health_status[component.name] = health_info
            
        return health_info
    
    def _is_process_running(self, component_name: str) -> bool:
        """Check if component process is running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if component_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception:
            return False
    
    def _check_component_response(self, component: SystemComponent) -> float:
        """Check component response time"""
        start_time = time.time()
        try:
            # Try to import and instantiate component
            module = __import__(component.module_path, fromlist=[component.class_name])
            cls = getattr(module, component.class_name)
            instance = cls()
            response_time = time.time() - start_time
            return response_time
        except Exception:
            return -1.0
    
    def _get_process_memory_usage(self, component_name: str) -> float:
        """Get memory usage of component process"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                if component_name.lower() in proc.info['name'].lower():
                    return proc.info['memory_info'].rss / 1024 / 1024  # MB
            return 0.0
        except Exception:
            return 0.0
    
    def _get_process_cpu_usage(self, component_name: str) -> float:
        """Get CPU usage of component process"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                if component_name.lower() in proc.info['name'].lower():
                    return proc.info['cpu_percent']
            return 0.0
        except Exception:
            return 0.0
    
    def _check_component_errors(self, component: SystemComponent) -> List[str]:
        """Check for component errors"""
        errors = []
        try:
            log_file = Path(f"jarvis_logs/{component.name.lower()}.log")
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Check last 100 lines for errors
                    for line in lines[-100:]:
                        if 'ERROR' in line or 'CRITICAL' in line:
                            errors.append(line.strip())
        except Exception:
            pass
        return errors[-10:]  # Return last 10 errors
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                time.sleep(self.config.health_check_interval)
                
                # Check system resources
                if self.config.system_monitoring_enabled:
                    self._check_system_resources()
                    
            except Exception as e:
                self.logger.get_component_logger("HealthMonitor").error(f"Monitoring loop error: {e}")
    
    def _check_system_resources(self):
        """Check overall system resources"""
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            
            if memory.percent > 90:
                self.logger.get_component_logger("SystemMonitor").warning(
                    f"High memory usage: {memory.percent}%"
                )
            
            if cpu > 90:
                self.logger.get_component_logger("SystemMonitor").warning(
                    f"High CPU usage: {cpu}%"
                )
                
        except Exception as e:
            self.logger.get_component_logger("SystemMonitor").error(
                f"System resource check failed: {e}"
            )

class AutoRecoverySystem:
    """Automatic recovery system for failed components"""
    
    def __init__(self, config: LauncherConfig, logger: MasterLogger):
        self.config = config
        self.logger = logger
        self.recovery_attempts = {}
        self.recovery_history = []
        
    def attempt_recovery(self, component: SystemComponent) -> bool:
        """Attempt to recover a failed component"""
        component_name = component.name
        attempt_count = self.recovery_attempts.get(component_name, 0)
        
        if attempt_count >= component.max_restart_attempts:
            self.logger.get_component_logger("AutoRecovery").warning(
                f"Max recovery attempts reached for {component_name}"
            )
            return False
        
        try:
            self.logger.get_component_logger("AutoRecovery").info(
                f"Attempting recovery for {component_name} (attempt {attempt_count + 1})"
            )
            
            # Stop existing process if running
            self._stop_component(component)
            
            # Wait for cleanup
            time.sleep(component.restart_delay)
            
            # Start component
            success = self._start_component(component)
            
            if success:
                self.recovery_attempts[component_name] = 0
                self.recovery_history.append({
                    "component": component_name,
                    "action": "recovered",
                    "timestamp": datetime.now(),
                    "attempt": attempt_count + 1
                })
                self.logger.get_component_logger("AutoRecovery").info(
                    f"Successfully recovered {component_name}"
                )
                return True
            else:
                self.recovery_attempts[component_name] = attempt_count + 1
                self.logger.get_component_logger("AutoRecovery").error(
                    f"Recovery failed for {component_name}"
                )
                return False
                
        except Exception as e:
            self.logger.get_component_logger("AutoRecovery").error(
                f"Recovery exception for {component_name}: {e}"
            )
            return False
    
    def _start_component(self, component: SystemComponent) -> bool:
        """Start a component"""
        try:
            # Create startup command
            cmd = [
                sys.executable,
                "-m",
                component.module_path,
                "--component",
                component.class_name
            ]
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent
            )
            
            # Wait a moment and check if process is still running
            time.sleep(2)
            if process.poll() is None:
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.get_component_logger(component.name).error(
                f"Failed to start component: {e}"
            )
            return False
    
    def _stop_component(self, component: SystemComponent):
        """Stop a component"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if component.name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    proc.wait(timeout=5)
        except Exception as e:
            self.logger.get_component_logger(component.name).warning(
                f"Error stopping component: {e}"
            )

class PerformanceTracker:
    """Performance tracking and optimization"""
    
    def __init__(self, config: LauncherConfig, logger: MasterLogger):
        self.config = config
        self.logger = logger
        self.metrics = {}
        self.baselines = {}
        self.optimizations = []
        
    def record_metric(self, component_name: str, metric_type: str, value: float):
        """Record a performance metric"""
        if component_name not in self.metrics:
            self.metrics[component_name] = {}
        
        if metric_type not in self.metrics[component_name]:
            self.metrics[component_name][metric_type] = []
        
        self.metrics[component_name][metric_type].append({
            "value": value,
            "timestamp": datetime.now()
        })
        
        # Keep only last 100 values
        if len(self.metrics[component_name][metric_type]) > 100:
            self.metrics[component_name][metric_type] = \
                self.metrics[component_name][metric_type][-100:]
    
    def analyze_performance(self, component_name: str) -> Dict[str, Any]:
        """Analyze component performance"""
        if component_name not in self.metrics:
            return {}
        
        analysis = {}
        for metric_type, values in self.metrics[component_name].items():
            if not values:
                continue
            
            recent_values = [v["value"] for v in values[-10:]]
            avg_value = sum(recent_values) / len(recent_values)
            
            analysis[metric_type] = {
                "average": avg_value,
                "latest": recent_values[-1],
                "trend": "stable"
            }
        
        return analysis
    
    def suggest_optimizations(self, component_name: str) -> List[str]:
        """Suggest performance optimizations"""
        suggestions = []
        analysis = self.analyze_performance(component_name)
        
        for metric_type, data in analysis.items():
            if metric_type == "response_time" and data["average"] > 2.0:
                suggestions.append(f"High response time detected ({data['average']:.2f}s). Consider optimization.")
            
            elif metric_type == "memory_usage" and data["average"] > 500:  # MB
                suggestions.append(f"High memory usage detected ({data['average']:.1f}MB). Consider memory optimization.")
            
            elif metric_type == "cpu_usage" and data["average"] > 80:  # %
                suggestions.append(f"High CPU usage detected ({data['average']:.1f}%). Consider CPU optimization.")
        
        return suggestions

class ServiceManager:
    """Service management for components"""
    
    def __init__(self, config: LauncherConfig, logger: MasterLogger, 
                 health_monitor: ComponentHealthMonitor,
                 recovery_system: AutoRecoverySystem):
        self.config = config
        self.logger = logger
        self.health_monitor = health_monitor
        self.recovery_system = recovery_system
        self.services = {}
        
    def register_service(self, component: SystemComponent):
        """Register a service"""
        self.services[component.name] = component
        self.logger.get_component_logger(component.name).info(
            f"Service {component.name} registered"
        )
    
    def start_all_services(self, components: List[SystemComponent]) -> Dict[str, bool]:
        """Start all services with dependency resolution"""
        # Sort components by priority and dependencies
        sorted_components = self._resolve_dependencies(components)
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.config.max_concurrent_components) as executor:
            future_to_component = {
                executor.submit(self._start_service, component): component 
                for component in sorted_components if component.auto_start
            }
            
            for future in as_completed(future_to_component):
                component = future_to_component[future]
                try:
                    success = future.result()
                    results[component.name] = success
                except Exception as e:
                    self.logger.get_component_logger(component.name).error(
                        f"Service start failed: {e}"
                    )
                    results[component.name] = False
        
        return results
    
    def _start_service(self, component: SystemComponent) -> bool:
        """Start a single service"""
        try:
            self.logger.get_component_logger(component.name).info(
                f"Starting service {component.name}"
            )
            
            # Check dependencies first
            for dep in component.dependencies:
                if dep not in self.services or self.services[dep].status != "running":
                    self.logger.get_component_logger(component.name).error(
                        f"Dependency {dep} not running"
                    )
                    return False
            
            # Start the service
            success = self.recovery_system._start_component(component)
            
            if success:
                component.status = "running"
                self.logger.get_component_logger(component.name).info(
                    f"Service {component.name} started successfully"
                )
            else:
                component.status = "failed"
                self.logger.get_component_logger(component.name).error(
                    f"Service {component.name} failed to start"
                )
            
            return success
            
        except Exception as e:
            component.status = "error"
            self.logger.get_component_logger(component.name).error(
                f"Service start exception: {e}"
            )
            return False
    
    def stop_service(self, component_name: str) -> bool:
        """Stop a specific service"""
        if component_name not in self.services:
            return False
        
        component = self.services[component_name]
        try:
            self.logger.get_component_logger(component_name).info(
                f"Stopping service {component_name}"
            )
            
            self.recovery_system._stop_component(component)
            component.status = "stopped"
            
            self.logger.get_component_logger(component_name).info(
                f"Service {component_name} stopped successfully"
            )
            return True
            
        except Exception as e:
            self.logger.get_component_logger(component_name).error(
                f"Service stop exception: {e}"
            )
            return False
    
    def restart_service(self, component_name: str) -> bool:
        """Restart a specific service"""
        if component_name not in self.services:
            return False
        
        component = self.services[component_name]
        try:
            self.stop_service(component_name)
            time.sleep(component.restart_delay)
            return self._start_service(component)
        except Exception as e:
            self.logger.get_component_logger(component_name).error(
                f"Service restart exception: {e}"
            )
            return False
    
    def _resolve_dependencies(self, components: List[SystemComponent]) -> List[SystemComponent]:
        """Resolve component dependencies and sort by priority"""
        resolved = []
        unresolved = components.copy()
        
        while unresolved:
            progress = False
            
            for component in list(unresolved):
                # Check if all dependencies are resolved
                deps_resolved = all(
                    dep in resolved or any(c.name == dep and c in resolved for c in components)
                    for dep in component.dependencies
                )
                
                if deps_resolved:
                    resolved.append(component)
                    unresolved.remove(component)
                    progress = True
            
            if not progress:
                # Circular dependency detected, add remaining components
                resolved.extend(unresolved)
                break
        
        # Sort by priority (higher priority first)
        resolved.sort(key=lambda x: x.priority, reverse=True)
        return resolved

class ConfigManager:
    """Configuration management system"""
    
    def __init__(self, config_file: str = "launcher_config.json"):
        self.config_file = Path(config_file)
        self.default_config = LauncherConfig()
        
    def load_config(self) -> LauncherConfig:
        """Load configuration from file"""
        if not self.config_file.exists():
            self.save_config(self.default_config)
            return self.default_config
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Convert dictionary back to LauncherConfig
            config = LauncherConfig(**data)
            return config
            
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")
            return self.default_config
    
    def save_config(self, config: LauncherConfig):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(config), f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving config: {e}")

class MasterLauncher:
    """JARVIS v14 Ultimate Master Launcher"""
    
    def __init__(self, config_file: str = "launcher_config.json"):
        """Initialize the master launcher"""
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.load_config()
        
        self.logger = MasterLogger()
        self.health_monitor = ComponentHealthMonitor(self.config, self.logger)
        self.recovery_system = AutoRecoverySystem(self.config, self.logger)
        self.performance_tracker = PerformanceTracker(self.config, self.logger)
        
        self.service_manager = ServiceManager(
            self.config, self.logger, self.health_monitor, self.recovery_system
        )
        
        self.components = {}
        self.running = False
        self.startup_time = None
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.get_component_logger("MasterLauncher").info("JARVIS v14 Ultimate Master Launcher initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.get_component_logger("MasterLauncher").info(
            f"Received signal {signum}, shutting down gracefully"
        )
        self.shutdown()
        sys.exit(0)
    
    def register_component(self, component: SystemComponent):
        """Register a system component"""
        self.components[component.name] = component
        self.service_manager.register_service(component)
        
        # Initialize component logger
        self.logger.get_component_logger(component.name)
    
    def initialize_system(self):
        """Initialize the JARVIS v14 system"""
        self.logger.get_component_logger("MasterLauncher").info("Initializing JARVIS v14 Ultimate system...")
        
        try:
            # Load predefined components
            self._load_predefined_components()
            
            # Perform system checks
            self._perform_system_checks()
            
            # Initialize health monitoring
            self.health_monitor.start_monitoring()
            
            self.logger.get_component_logger("MasterLauncher").info("System initialization completed")
            return True
            
        except Exception as e:
            self.logger.get_component_logger("MasterLauncher").error(
                f"System initialization failed: {e}"
            )
            return False
    
    def _load_predefined_components(self):
        """Load predefined system components"""
        predefined_components = [
            SystemComponent(
                name="UltimateAIEngine",
                module_path="core.multi_modal_ai_engine",
                class_name="MultiModalAIEngine",
                priority=10,
                dependencies=[],
                auto_start=True
            ),
            SystemComponent(
                name="UltimateTermuxIntegration",
                module_path="core.ultimate_termux_integration",
                class_name="UltimateTermuxIntegration",
                priority=9,
                dependencies=["UltimateAIEngine"],
                auto_start=True
            ),
            SystemComponent(
                name="AdvancedAutoExecution",
                module_path="core.advanced_auto_execution_v14",
                class_name="AdvancedAutoExecution",
                priority=8,
                dependencies=["UltimateAIEngine", "UltimateTermuxIntegration"],
                auto_start=True
            ),
            SystemComponent(
                name="PredictiveIntelligenceEngine",
                module_path="core.predictive_intelligence_engine",
                class_name="PredictiveIntelligenceEngine",
                priority=7,
                dependencies=["UltimateAIEngine"],
                auto_start=True
            ),
            SystemComponent(
                name="ErrorProofSystem",
                module_path="core.error_proof_system",
                class_name="ErrorProofSystem",
                priority=6,
                dependencies=["UltimateAIEngine"],
                auto_start=True
            ),
            SystemComponent(
                name="QuantumOptimizationSystem",
                module_path="core.quantum_optimization_system",
                class_name="QuantumOptimizationSystem",
                priority=5,
                dependencies=["UltimateAIEngine"],
                auto_start=False
            ),
            SystemComponent(
                name="SelfTestingSafetyFramework",
                module_path="core.self_testing_safety_framework",
                class_name="SelfTestingSafetyFramework",
                priority=4,
                dependencies=[],
                auto_start=True
            ),
            SystemComponent(
                name="MultiMethodErrorResolution",
                module_path="core.multi_method_error_resolution",
                class_name="MultiMethodErrorResolution",
                priority=3,
                dependencies=["ErrorProofSystem"],
                auto_start=True
            )
        ]
        
        for component in predefined_components:
            self.register_component(component)
        
        self.logger.get_component_logger("MasterLauncher").info(
            f"Loaded {len(predefined_components)} predefined components"
        )
    
    def _perform_system_checks(self):
        """Perform system health checks"""
        self.logger.get_component_logger("MasterLauncher").info("Performing system checks...")
        
        checks = [
            ("Python Version", self._check_python_version),
            ("Required Modules", self._check_required_modules),
            ("Disk Space", self._check_disk_space),
            ("Memory", self._check_memory),
            ("Network", self._check_network),
            ("Permissions", self._check_permissions)
        ]
        
        failed_checks = []
        for check_name, check_func in checks:
            try:
                result = check_func()
                if result:
                    self.logger.get_component_logger("SystemChecks").info(f"✓ {check_name}: PASSED")
                else:
                    failed_checks.append(check_name)
                    self.logger.get_component_logger("SystemChecks").warning(f"⚠ {check_name}: FAILED")
            except Exception as e:
                failed_checks.append(check_name)
                self.logger.get_component_logger("SystemChecks").error(f"✗ {check_name}: ERROR - {e}")
        
        if failed_checks:
            raise SystemError(f"System checks failed: {failed_checks}")
        
        self.logger.get_component_logger("SystemChecks").info("All system checks passed")
    
    def _check_python_version(self) -> bool:
        """Check Python version compatibility"""
        return sys.version_info >= (3, 8)
    
    def _check_required_modules(self) -> bool:
        """Check if required modules are available"""
        required_modules = [
            'psutil', 'numpy', 'pandas', 'requests', 'threading', 'datetime'
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        return len(missing_modules) == 0
    
    def _check_disk_space(self) -> bool:
        """Check available disk space"""
        try:
            disk = psutil.disk_usage('/')
            free_gb = disk.free / (1024**3)
            return free_gb >= 5.0  # At least 5GB free
        except Exception:
            return False
    
    def _check_memory(self) -> bool:
        """Check available memory"""
        try:
            memory = psutil.virtual_memory()
            return memory.available >= (1024**3)  # At least 1GB available
        except Exception:
            return False
    
    def _check_network(self) -> bool:
        """Check network connectivity"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except Exception:
            return False
    
    def _check_permissions(self) -> bool:
        """Check file system permissions"""
        try:
            test_file = Path("permission_test.tmp")
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False
    
    def startup(self):
        """Start the JARVIS v14 system"""
        if self.running:
            self.logger.get_component_logger("MasterLauncher").warning("System already running")
            return
        
        self.logger.get_component_logger("MasterLauncher").info("Starting JARVIS v14 Ultimate system...")
        self.startup_time = datetime.now()
        
        try:
            # Initialize system
            if not self.initialize_system():
                raise SystemError("System initialization failed")
            
            # Start all services
            start_results = self.service_manager.start_all_services(list(self.components.values()))
            
            # Check results
            failed_components = [name for name, success in start_results.items() if not success]
            
            if failed_components:
                self.logger.get_component_logger("MasterLauncher").warning(
                    f"Failed to start components: {failed_components}"
                )
                
                # Try to recover failed components
                if self.config.auto_recovery_enabled:
                    self._attempt_recovery_of_failed_components(failed_components)
            
            self.running = True
            uptime = datetime.now() - self.startup_time
            self.logger.get_component_logger("MasterLauncher").info(
                f"JARVIS v14 Ultimate system started successfully (uptime: {uptime})"
            )
            
            return True
            
        except Exception as e:
            self.logger.get_component_logger("MasterLauncher").error(
                f"System startup failed: {e}"
            )
            self.shutdown()
            return False
    
    def _attempt_recovery_of_failed_components(self, failed_components: List[str]):
        """Attempt to recover failed components"""
        self.logger.get_component_logger("MasterLauncher").info(
            f"Attempting recovery of failed components: {failed_components}"
        )
        
        for component_name in failed_components:
            if component_name in self.components:
                component = self.components[component_name]
                success = self.recovery_system.attempt_recovery(component)
                if success:
                    self.logger.get_component_logger("MasterLauncher").info(
                        f"Recovered {component_name}"
                    )
                else:
                    self.logger.get_component_logger("MasterLauncher").warning(
                        f"Failed to recover {component_name}"
                    )
    
    def shutdown(self):
        """Shutdown the JARVIS v14 system"""
        if not self.running:
            return
        
        self.logger.get_component_logger("MasterLauncher").info("Shutting down JARVIS v14 Ultimate system...")
        
        try:
            # Stop health monitoring
            self.health_monitor.stop_monitoring()
            
            # Stop all services
            for component_name, component in self.components.items():
                if component.status == "running":
                    self.service_manager.stop_service(component_name)
            
            self.running = False
            
            if self.startup_time:
                uptime = datetime.now() - self.startup_time
                self.logger.get_component_logger("MasterLauncher").info(
                    f"System shutdown completed (total uptime: {uptime})"
                )
            
        except Exception as e:
            self.logger.get_component_logger("MasterLauncher").error(
                f"Error during shutdown: {e}"
            )
    
    def restart(self) -> bool:
        """Restart the system"""
        self.logger.get_component_logger("MasterLauncher").info("Restarting JARVIS v14 Ultimate system...")
        
        self.shutdown()
        time.sleep(5)  # Wait for cleanup
        return self.startup()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "running": self.running,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "uptime_seconds": (datetime.now() - self.startup_time).total_seconds() if self.startup_time else 0,
            "components": {},
            "system_resources": {},
            "performance_metrics": {}
        }
        
        # Component status
        for name, component in self.components.items():
            health_info = self.health_monitor.health_status.get(name, {})
            status["components"][name] = {
                "status": component.status,
                "priority": component.priority,
                "auto_start": component.auto_start,
                "dependencies": component.dependencies,
                "health": health_info
            }
        
        # System resources
        if self.config.system_monitoring_enabled:
            try:
                status["system_resources"] = {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent
                }
            except Exception:
                pass
        
        # Performance metrics
        for name in self.components:
            metrics = self.performance_tracker.analyze_performance(name)
            if metrics:
                status["performance_metrics"][name] = metrics
        
        return status
    
    def get_component_status(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Get status of specific component"""
        if component_name not in self.components:
            return None
        
        component = self.components[component_name]
        health_info = self.health_monitor.health_status.get(component_name, {})
        
        return {
            "component": component,
            "health": health_info,
            "performance": self.performance_tracker.analyze_performance(component_name),
            "suggestions": self.performance_tracker.suggest_optimizations(component_name)
        }
    
    def run_interactive_mode(self):
        """Run in interactive mode"""
        print("🤖 JARVIS v14 Ultimate Master Launcher - Interactive Mode")
        print("=" * 60)
        
        commands = {
            'status': self._cmd_status,
            'start': self._cmd_start,
            'stop': self._cmd_stop,
            'restart': self._cmd_restart,
            'health': self._cmd_health,
            'performance': self._cmd_performance,
            'config': self._cmd_config,
            'help': self._cmd_help,
            'quit': self._cmd_quit
        }
        
        while True:
            try:
                command = input("\nJARVIS> ").strip().lower()
                
                if command in commands:
                    commands[command]()
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nUse 'quit' command to exit gracefully.")
            except Exception as e:
                print(f"Error: {e}")
    
    def _cmd_status(self):
        """Display system status"""
        status = self.get_system_status()
        print(f"\nSystem Status:")
        print(f"Running: {'Yes' if status['running'] else 'No'}")
        if status['startup_time']:
            uptime = datetime.now() - datetime.fromisoformat(status['startup_time'])
            print(f"Uptime: {uptime}")
        
        print(f"\nComponents ({len(status['components'])}):")
        for name, info in status['components'].items():
            print(f"  {name}: {info['status']} (Priority: {info['priority']})")
        
        if status['system_resources']:
            print(f"\nSystem Resources:")
            for resource, value in status['system_resources'].items():
                print(f"  {resource}: {value}")
    
    def _cmd_start(self):
        """Start system"""
        if self.running:
            print("System is already running.")
        else:
            success = self.startup()
            print("Startup successful!" if success else "Startup failed!")
    
    def _cmd_stop(self):
        """Stop system"""
        self.shutdown()
        print("System stopped.")
    
    def _cmd_restart(self):
        """Restart system"""
        success = self.restart()
        print("Restart successful!" if success else "Restart failed!")
    
    def _cmd_health(self):
        """Show health information"""
        print("\nComponent Health Status:")
        for name in self.components:
            component_status = self.get_component_status(name)
            if component_status:
                health = component_status['health']
                print(f"{name}: {health.get('status', 'unknown')}")
    
    def _cmd_performance(self):
        """Show performance metrics"""
        print("\nPerformance Metrics:")
        for name in self.components:
            metrics = self.performance_tracker.analyze_performance(name)
            if metrics:
                print(f"{name}:")
                for metric_type, data in metrics.items():
                    print(f"  {metric_type}: {data['average']:.2f}")
    
    def _cmd_config(self):
        """Show configuration"""
        config_dict = asdict(self.config)
        print(f"\nConfiguration:")
        for key, value in config_dict.items():
            print(f"  {key}: {value}")
    
    def _cmd_help(self):
        """Show help"""
        print("\nAvailable Commands:")
        print("  status      - Show system status")
        print("  start       - Start the system")
        print("  stop        - Stop the system")
        print("  restart     - Restart the system")
        print("  health      - Show component health")
        print("  performance - Show performance metrics")
        print("  config      - Show configuration")
        print("  help        - Show this help")
        print("  quit        - Quit the launcher")
    
    def _cmd_quit(self):
        """Quit the launcher"""
        print("Shutting down JARVIS v14 Ultimate...")
        self.shutdown()
        sys.exit(0)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS v14 Ultimate Master Launcher")
    parser.add_argument('--config', default='launcher_config.json', 
                       help='Configuration file path')
    parser.add_argument('--mode', choices=['daemon', 'interactive'], 
                       default='interactive', help='Run mode')
    parser.add_argument('--no-health-check', action='store_true',
                       help='Disable health monitoring')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create launcher
    launcher = MasterLauncher(args.config)
    
    if args.no_health_check:
        launcher.config.system_monitoring_enabled = False
    
    try:
        if args.mode == 'daemon':
            # Start in daemon mode
            if launcher.startup():
                print("JARVIS v14 Ultimate running in daemon mode...")
                
                # Keep running until interrupted
                while launcher.running:
                    time.sleep(1)
        else:
            # Start in interactive mode
            launcher.run_interactive_mode()
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        launcher.shutdown()
    except Exception as e:
        print(f"Fatal error: {e}")
        launcher.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    main()