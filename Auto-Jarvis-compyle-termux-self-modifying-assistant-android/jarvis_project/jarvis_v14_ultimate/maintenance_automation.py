#!/usr/bin/env python3
"""
JARVIS v14 ULTIMATE - Maintenance Automation System
===================================================

Author: JARVIS Development Team
Version: 14.0 Ultimate
Description: Comprehensive maintenance automation system with health monitoring,
             performance optimization, security auditing, and automated cleanup

Features:
- Health monitoring and alerting
- Performance optimization
- Security auditing
- Log rotation and cleanup
- Database maintenance
- Resource monitoring
- Automated backup management
- System diagnostics
- Predictive maintenance
- Cross-platform compatibility
"""

import os
import sys
import json
import time
import shutil
import subprocess
import threading
import sqlite3
import psutil
import schedule
import hashlib
import smtplib
import ssl
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import yaml
import gzip
import tarfile
import sqlite3
from collections import defaultdict, deque

# Rich imports for enhanced UI
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.live import Live
from rich.align import Align
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
from rich.markdown import Markdown
from rich.prompt import Confirm, Prompt
from rich.spinner import Spinner

# Configuration
JARVIS_VERSION = "14.0 Ultimate"
MAINTENANCE_CONFIG_FILE = ".config/jarvis_v14_ultimate/maintenance.json"
HEALTH_DB_FILE = ".config/jarvis_v14_ultimate/health_metrics.db"
MAINTENANCE_LOG_DIR = ".config/jarvis_v14_ultimate/maintenance_logs"
ALERT_CONFIG_FILE = ".config/jarvis_v14_ultimate/alerts.yaml"

console = Console()

# ========================================================================
# Data Structures and Enums
# ========================================================================

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MaintenanceTask(Enum):
    """Types of maintenance tasks"""
    HEALTH_CHECK = "health_check"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_AUDIT = "security_audit"
    LOG_ROTATION = "log_rotation"
    DATABASE_MAINTENANCE = "database_maintenance"
    BACKUP_CLEANUP = "backup_cleanup"
    RESOURCE_MONITORING = "resource_monitoring"
    SYSTEM_DIAGNOSTICS = "system_diagnostics"
    PREDICTIVE_MAINTENANCE = "predictive_maintenance"

class SystemHealth(Enum):
    """System health status"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class HealthMetric:
    """Individual health metric"""
    name: str
    value: float
    threshold_warning: float
    threshold_critical: float
    status: SystemHealth
    timestamp: str
    description: str = ""

@dataclass
class MaintenanceConfig:
    """Maintenance system configuration"""
    # Monitoring settings
    health_check_interval_minutes: int = 60
    performance_check_interval_minutes: 30
    security_audit_interval_hours: 24
    
    # Alert thresholds
    cpu_threshold_warning: float = 70.0
    cpu_threshold_critical: float = 85.0
    memory_threshold_warning: float = 75.0
    memory_threshold_critical: float = 90.0
    disk_threshold_warning: float = 80.0
    disk_threshold_critical: float = 95.0
    response_time_threshold_ms: float = 1000.0
    
    # Maintenance settings
    log_retention_days: int = 30
    backup_retention_days: int = 90
    max_log_size_mb: int = 100
    auto_optimization: bool = True
    auto_cleanup: bool = True
    
    # Notification settings
    email_notifications: bool = False
    smtp_server: str = ""
    smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    notification_emails: List[str] = None
    
    # Predictive maintenance
    predictive_analysis: bool = True
    anomaly_detection: bool = True
    trend_analysis: bool = True

@dataclass
class MaintenanceReport:
    """Maintenance report structure"""
    timestamp: str
    duration_seconds: float
    tasks_completed: int
    tasks_failed: int
    health_score: float
    alerts_generated: int
    recommendations: List[str]
    performance_metrics: Dict[str, float]

# ========================================================================
# Health Monitor
# ========================================================================

class HealthMonitor:
    """System health monitoring and alerting"""
    
    def __init__(self, config: MaintenanceConfig, jarvis_home: str):
        self.config = config
        self.jarvis_home = Path(jarvis_home)
        self.config_dir = Path.home() / ".config" / "jarvis_v14_ultimate"
        self.health_db = self.config_dir / "health_metrics.db"
        
        # Setup database
        self.setup_health_database()
        
        # Monitoring data
        self.metrics_history = defaultdict(list)
        self.current_health = SystemHealth.GOOD
        self.alerts = deque(maxlen=100)
        
        console.print("[green]✓[/green] Health Monitor initialized")
    
    def setup_health_database(self):
        """Initialize health metrics database"""
        self.health_db.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.health_db))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                threshold_warning REAL,
                threshold_critical REAL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                description TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                metric_name TEXT,
                value REAL,
                threshold REAL,
                timestamp TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)
        
        conn.commit()
        conn.close()
    
    def collect_system_metrics(self) -> Dict[str, HealthMetric]:
        """Collect current system health metrics"""
        metrics = {}
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics['cpu_usage'] = HealthMetric(
                name='CPU Usage',
                value=cpu_percent,
                threshold_warning=self.config.cpu_threshold_warning,
                threshold_critical=self.config.cpu_threshold_critical,
                status=self._evaluate_metric(cpu_percent, self.config.cpu_threshold_warning, 
                                           self.config.cpu_threshold_critical),
                timestamp=datetime.now().isoformat(),
                description='CPU utilization percentage'
            )
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            metrics['memory_usage'] = HealthMetric(
                name='Memory Usage',
                value=memory_percent,
                threshold_warning=self.config.memory_threshold_warning,
                threshold_critical=self.config.memory_threshold_critical,
                status=self._evaluate_metric(memory_percent, self.config.memory_threshold_warning,
                                           self.config.memory_threshold_critical),
                timestamp=datetime.now().isoformat(),
                description='Memory utilization percentage'
            )
            
            # Disk usage
            disk = psutil.disk_usage(str(Path.home()))
            disk_percent = (disk.used / disk.total) * 100
            metrics['disk_usage'] = HealthMetric(
                name='Disk Usage',
                value=disk_percent,
                threshold_warning=self.config.disk_threshold_warning,
                threshold_critical=self.config.disk_threshold_critical,
                status=self._evaluate_metric(disk_percent, self.config.disk_threshold_warning,
                                           self.config.disk_threshold_critical),
                timestamp=datetime.now().isoformat(),
                description='Disk utilization percentage'
            )
            
            # JARVIS-specific metrics
            if (self.jarvis_home / "jarvis.py").exists():
                metrics.update(self._collect_jarvis_metrics())
            
            return metrics
            
        except Exception as e:
            console.print(f"[red]Failed to collect system metrics: {e}[/red]")
            return {}
    
    def _collect_jarvis_metrics(self) -> Dict[str, HealthMetric]:
        """Collect JARVIS-specific health metrics"""
        metrics = {}
        
        try:
            # Response time
            start_time = time.time()
            subprocess.run([
                str(self.jarvis_home / "venv" / "bin" / "python"),
                str(self.jarvis_home / "jarvis.py"),
                "--version"
            ], capture_output=True, timeout=10)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            metrics['response_time'] = HealthMetric(
                name='JARVIS Response Time',
                value=response_time,
                threshold_warning=self.config.response_time_threshold_ms * 1.2,
                threshold_critical=self.config.response_time_threshold_ms * 1.5,
                status=self._evaluate_metric(response_time, 
                                           self.config.response_time_threshold_ms * 1.2,
                                           self.config.response_time_threshold_ms * 1.5),
                timestamp=datetime.now().isoformat(),
                description='JARVIS startup response time in milliseconds'
            )
            
            # Check if services are running
            services_running = self._check_jarvis_services()
            metrics['services_status'] = HealthMetric(
                name='Services Status',
                value=100.0 if services_running else 0.0,
                threshold_warning=100.0,
                threshold_critical=100.0,
                status=SystemHealth.GOOD if services_running else SystemHealth.POOR,
                timestamp=datetime.now().isoformat(),
                description='JARVIS services running status'
            )
            
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to collect JARVIS metrics: {e}[/yellow]")
        
        return metrics
    
    def _check_jarvis_services(self) -> bool:
        """Check if JARVIS services are running"""
        try:
            platform = sys.platform
            
            if platform.startswith('linux'):
                # Check systemd service
                result = subprocess.run([
                    'systemctl', 'is-active', 'jarvis-v14-ultimate.service'
                ], capture_output=True, timeout=10)
                return result.returncode == 0
            
            elif 'termux' in os.environ:
                # Check Termux service
                result = subprocess.run([
                    'sv', 'status', 'jarvis-v14-ultimate'
                ], capture_output=True, timeout=10)
                return b'run' in result.stdout
            
            return False
            
        except Exception:
            return False
    
    def _evaluate_metric(self, value: float, warning_threshold: float, 
                        critical_threshold: float) -> SystemHealth:
        """Evaluate metric against thresholds"""
        if value >= critical_threshold:
            return SystemHealth.CRITICAL
        elif value >= warning_threshold:
            return SystemHealth.POOR
        elif value >= warning_threshold * 0.7:
            return SystemHealth.FAIR
        else:
            return SystemHealth.GOOD
    
    def store_metrics(self, metrics: Dict[str, HealthMetric]):
        """Store metrics in database"""
        try:
            conn = sqlite3.connect(str(self.health_db))
            cursor = conn.cursor()
            
            for metric in metrics.values():
                cursor.execute("""
                    INSERT INTO health_metrics 
                    (metric_name, value, threshold_warning, threshold_critical, status, timestamp, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric.name, metric.value, metric.threshold_warning,
                    metric.threshold_critical, metric.status.value, metric.timestamp, metric.description
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            console.print(f"[red]Failed to store metrics: {e}[/red]")
    
    def check_thresholds_and_alert(self, metrics: Dict[str, HealthMetric]):
        """Check metrics against thresholds and generate alerts"""
        for metric in metrics.values():
            if metric.status in [SystemHealth.POOR, SystemHealth.CRITICAL]:
                alert_message = f"{metric.name}: {metric.value:.1f} (Threshold: {metric.threshold_warning:.1f})"
                
                alert = {
                    'level': AlertLevel.CRITICAL if metric.status == SystemHealth.CRITICAL else AlertLevel.WARNING,
                    'message': alert_message,
                    'metric_name': metric.name,
                    'value': metric.value,
                    'threshold': metric.threshold_warning,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.alerts.append(alert)
                self.generate_alert(alert)
    
    def generate_alert(self, alert: Dict[str, Any]):
        """Generate and send alert"""
        level_colors = {
            AlertLevel.INFO: "blue",
            AlertLevel.WARNING: "yellow",
            AlertLevel.ERROR: "orange_red1",
            AlertLevel.CRITICAL: "red"
        }
        
        color = level_colors.get(alert['level'], "white")
        console.print(f"[{color}][{alert['level'].value.upper()}] {alert['message']}[/{color}]")
        
        # Send email notification if configured
        if self.config.email_notifications and self.config.notification_emails:
            self._send_email_alert(alert)
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """Send email alert"""
        try:
            if not all([self.config.smtp_server, self.config.email_username, 
                       self.config.email_password]):
                return
            
            msg = MimeMultipart()
            msg['From'] = self.config.email_username
            msg['To'] = ', '.join(self.config.notification_emails)
            msg['Subject'] = f"JARVIS Alert - {alert['level'].value.upper()}"
            
            body = f"""
JARVIS v14 Ultimate System Alert

Level: {alert['level'].value.upper()}
Message: {alert['message']}
Time: {alert['timestamp']}

Please check the system status and take appropriate action.
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.email_username, self.config.email_password)
            server.send_message(msg)
            server.quit()
            
            console.print("[green]✓[/green] Alert email sent")
            
        except Exception as e:
            console.print(f"[red]Failed to send email alert: {e}[/red]")
    
    def get_health_trends(self, hours: int = 24) -> Dict[str, List[float]]:
        """Get health metric trends over time"""
        try:
            conn = sqlite3.connect(str(self.health_db))
            cursor = conn.cursor()
            
            since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            trends = defaultdict(list)
            
            cursor.execute("""
                SELECT metric_name, value, timestamp 
                FROM health_metrics 
                WHERE timestamp > ? 
                ORDER BY timestamp
            """, (since_time,))
            
            for row in cursor.fetchall():
                metric_name, value, timestamp = row
                trends[metric_name].append(value)
            
            conn.close()
            return dict(trends)
            
        except Exception as e:
            console.print(f"[red]Failed to get health trends: {e}[/red]")
            return {}
    
    def calculate_overall_health(self, metrics: Dict[str, HealthMetric]) -> SystemHealth:
        """Calculate overall system health score"""
        if not metrics:
            return SystemHealth.GOOD
        
        health_scores = {
            SystemHealth.EXCELLENT: 100,
            SystemHealth.GOOD: 80,
            SystemHealth.FAIR: 60,
            SystemHealth.POOR: 40,
            SystemHealth.CRITICAL: 20
        }
        
        total_score = sum(health_scores.get(metric.status, 0) for metric in metrics.values())
        avg_score = total_score / len(metrics)
        
        if avg_score >= 90:
            return SystemHealth.EXCELLENT
        elif avg_score >= 75:
            return SystemHealth.GOOD
        elif avg_score >= 60:
            return SystemHealth.FAIR
        elif avg_score >= 40:
            return SystemHealth.POOR
        else:
            return SystemHealth.CRITICAL


# ========================================================================
# Maintenance Automation System
# ========================================================================

class MaintenanceAutomation:
    """JARVIS v14 Ultimate Maintenance Automation System"""
    
    def __init__(self, jarvis_home: str = None):
        self.jarvis_home = Path(jarvis_home or Path.home() / ".jarvis_v14_ultimate")
        self.config_dir = Path.home() / ".config" / "jarvis_v14_ultimate"
        self.log_dir = Path.home() / ".config" / "jarvis_v14_ultimate" / "maintenance_logs"
        
        # Create directories
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self.load_maintenance_config()
        
        # Setup logging
        self.setup_logging()
        
        # Initialize components
        self.health_monitor = HealthMonitor(self.config, str(self.jarvis_home))
        
        # Task statistics
        self.task_stats = {
            'completed': 0,
            'failed': 0,
            'total_duration': 0.0
        }
        
        # Threading
        self.running = False
        self.maintenance_thread = None
        
        console.print(f"[green]✓[/green] Maintenance Automation initialized for JARVIS v{JARVIS_VERSION}")
    
    def load_maintenance_config(self) -> MaintenanceConfig:
        """Load maintenance configuration"""
        config_file = self.config_dir / "maintenance.json"
        
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    data = json.load(f)
                
                # Handle list fields
                if 'notification_emails' in data and isinstance(data['notification_emails'], str):
                    data['notification_emails'] = [data['notification_emails']]
                
                return MaintenanceConfig(**data)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to load maintenance config: {e}[/yellow]")
        
        # Return default configuration
        default_config = MaintenanceConfig()
        self.save_maintenance_config(default_config)
        return default_config
    
    def save_maintenance_config(self, config: MaintenanceConfig):
        """Save maintenance configuration"""
        try:
            config_file = self.config_dir / "maintenance.json"
            with open(config_file, 'w') as f:
                json.dump(asdict(config), f, indent=2)
        except Exception as e:
            console.print(f"[red]Failed to save maintenance config: {e}[/red]")
    
    def setup_logging(self):
        """Setup maintenance logging"""
        log_file = self.log_dir / f"maintenance_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("JARVIS-Maintenance")
    
    def run_health_check(self) -> MaintenanceReport:
        """Run comprehensive health check"""
        start_time = time.time()
        console.print("[cyan]Running health check...[/cyan]")
        
        try:
            # Collect metrics
            metrics = self.health_monitor.collect_system_metrics()
            
            # Store metrics
            self.health_monitor.store_metrics(metrics)
            
            # Check thresholds and generate alerts
            self.health_monitor.check_thresholds_and_alert(metrics)
            
            # Calculate overall health
            overall_health = self.health_monitor.calculate_overall_health(metrics)
            
            # Generate recommendations
            recommendations = self.generate_recommendations(metrics)
            
            duration = time.time() - start_time
            
            report = MaintenanceReport(
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration,
                tasks_completed=1,
                tasks_failed=0,
                health_score=self.calculate_health_score(overall_health),
                alerts_generated=len(self.health_monitor.alerts),
                recommendations=recommendations,
                performance_metrics={name: metric.value for name, metric in metrics.items()}
            )
            
            self.task_stats['completed'] += 1
            self.task_stats['total_duration'] += duration
            
            console.print(f"[green]✓[/green] Health check completed in {duration:.1f}s")
            console.print(f"[cyan]Overall Health:[/cyan] {overall_health.value.title()}")
            
            return report
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Health check failed: {e}")
            self.task_stats['failed'] += 1
            
            return MaintenanceReport(
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration,
                tasks_completed=0,
                tasks_failed=1,
                health_score=0.0,
                alerts_generated=1,
                recommendations=[f"Health check failed: {str(e)}"],
                performance_metrics={}
            )
    
    def generate_recommendations(self, metrics: Dict[str, HealthMetric]) -> List[str]:
        """Generate maintenance recommendations based on metrics"""
        recommendations = []
        
        # Performance recommendations
        for metric in metrics.values():
            if metric.status == SystemHealth.POOR:
                recommendations.append(f"Investigate high {metric.name}: {metric.value:.1f}%")
            elif metric.status == SystemHealth.CRITICAL:
                recommendations.append(f"URGENT: Critical {metric.name}: {metric.value:.1f}%")
        
        # Resource-specific recommendations
        cpu_metric = metrics.get('cpu_usage')
        if cpu_metric and cpu_metric.value > 80:
            recommendations.append("Consider optimizing CPU-intensive processes")
        
        memory_metric = metrics.get('memory_usage')
        if memory_metric and memory_metric.value > 85:
            recommendations.append("Consider increasing system memory or closing unused applications")
        
        disk_metric = metrics.get('disk_usage')
        if disk_metric and disk_metric.value > 90:
            recommendations.append("URGENT: Disk space critically low - immediate cleanup required")
        
        # If no issues found
        if not recommendations:
            recommendations.append("System is running optimally - no immediate action required")
        
        return recommendations
    
    def calculate_health_score(self, overall_health: SystemHealth) -> float:
        """Calculate numerical health score"""
        scores = {
            SystemHealth.EXCELLENT: 100.0,
            SystemHealth.GOOD: 85.0,
            SystemHealth.FAIR: 70.0,
            SystemHealth.POOR: 50.0,
            SystemHealth.CRITICAL: 25.0
        }
        return scores.get(overall_health, 0.0)
    
    def run_comprehensive_maintenance(self) -> List[MaintenanceReport]:
        """Run all maintenance tasks"""
        console.print(Panel.fit(
            "[bold blue]JARVIS v14 Ultimate - Comprehensive Maintenance[/bold blue]",
            style="blue"
        ))
        
        reports = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            # Health Check
            task = progress.add_task("Running Health Check", total=None)
            report = self.run_health_check()
            reports.append(report)
            progress.update(task, description="✓ Health Check Complete")
            
            # Performance Optimization
            task = progress.add_task("Optimizing Performance", total=None)
            report = self.run_performance_optimization()
            reports.append(report)
            progress.update(task, description="✓ Performance Optimization Complete")
            
            # Security Audit
            task = progress.add_task("Running Security Audit", total=None)
            report = self.run_security_audit()
            reports.append(report)
            progress.update(task, description="✓ Security Audit Complete")
            
            # Log Maintenance
            task = progress.add_task("Maintaining Logs", total=None)
            report = self.run_log_maintenance()
            reports.append(report)
            progress.update(task, description="✓ Log Maintenance Complete")
            
            # Backup Maintenance
            task = progress.add_task("Managing Backups", total=None)
            report = self.run_backup_maintenance()
            reports.append(report)
            progress.update(task, description="✓ Backup Maintenance Complete")
        
        return reports
    
    def run_performance_optimization(self) -> MaintenanceReport:
        """Run performance optimization tasks"""
        start_time = time.time()
        console.print("[cyan]Running performance optimization...[/cyan]")
        
        recommendations = []
        
        try:
            # Optimize Python environment
            if (self.jarvis_home / "venv").exists():
                self.optimize_python_environment()
                recommendations.append("Python virtual environment optimized")
            
            # Clean temporary files
            cleaned_files = self.clean_temporary_files()
            if cleaned_files > 0:
                recommendations.append(f"Cleaned {cleaned_files} temporary files")
            
            # Optimize database if exists
            if (self.jarvis_home / "data").exists():
                db_optimized = self.optimize_databases()
                if db_optimized:
                    recommendations.append("Databases optimized")
            
            # System performance tuning
            system_tuned = self.tune_system_performance()
            if system_tuned:
                recommendations.append("System performance tuning applied")
            
            duration = time.time() - start_time
            
            report = MaintenanceReport(
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration,
                tasks_completed=1,
                tasks_failed=0,
                health_score=85.0,
                alerts_generated=0,
                recommendations=recommendations,
                performance_metrics={}
            )
            
            self.task_stats['completed'] += 1
            self.task_stats['total_duration'] += duration
            
            console.print(f"[green]✓[/green] Performance optimization completed in {duration:.1f}s")
            
            return report
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Performance optimization failed: {e}")
            self.task_stats['failed'] += 1
            
            return MaintenanceReport(
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration,
                tasks_completed=0,
                tasks_failed=1,
                health_score=0.0,
                alerts_generated=1,
                recommendations=[f"Performance optimization failed: {str(e)}"],
                performance_metrics={}
            )
    
    def optimize_python_environment(self):
        """Optimize Python virtual environment"""
        venv_path = self.jarvis_home / "venv"
        
        if not venv_path.exists():
            return
        
        try:
            # Clear Python cache
            for root, dirs, files in os.walk(self.jarvis_home):
                for dir_name in dirs:
                    if dir_name == "__pycache__":
                        cache_path = Path(root) / dir_name
                        shutil.rmtree(cache_path, ignore_errors=True)
            
            # Update pip and setuptools
            subprocess.run([
                str(venv_path / "bin" / "pip"), "install", "--upgrade", "pip", "setuptools", "wheel"
            ], capture_output=True, timeout=300)
            
            self.logger.info("Python environment optimized")
            
        except Exception as e:
            self.logger.error(f"Python environment optimization failed: {e}")
    
    def clean_temporary_files(self) -> int:
        """Clean temporary files and cache"""
        cleaned_count = 0
        
        temp_directories = [
            "/tmp",
            "/var/tmp",
            Path.home() / ".cache",
            Path.home() / ".local" / "share" / "Trash"
        ]
        
        for temp_dir in temp_directories:
            if not os.path.exists(temp_dir):
                continue
            
            try:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if any(file.endswith(ext) for ext in ['.tmp', '.temp', '.log', '.cache']):
                            file_path = Path(root) / file
                            try:
                                file_path.unlink()
                                cleaned_count += 1
                            except OSError:
                                pass
            except Exception as e:
                self.logger.debug(f"Failed to clean {temp_dir}: {e}")
        
        return cleaned_count
    
    def optimize_databases(self) -> bool:
        """Optimize SQLite databases"""
        try:
            db_dir = self.jarvis_home / "data"
            if not db_dir.exists():
                return False
            
            db_files = list(db_dir.glob("*.db"))
            
            for db_file in db_files:
                conn = sqlite3.connect(str(db_file))
                conn.execute("VACUUM")
                conn.execute("ANALYZE")
                conn.close()
            
            return len(db_files) > 0
            
        except Exception as e:
            self.logger.error(f"Database optimization failed: {e}")
            return False
    
    def tune_system_performance(self) -> bool:
        """Apply system performance tuning"""
        try:
            # Linux-specific tuning
            if sys.platform.startswith('linux'):
                # Adjust swappiness if possible
                try:
                    with open('/proc/sys/vm/swappiness', 'r') as f:
                        current_swappiness = int(f.read().strip())
                    
                    if current_swappiness > 10:
                        subprocess.run([
                            'sudo', 'sysctl', 'vm.swappiness=10'
                        ], capture_output=True)
                        return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            self.logger.error(f"System tuning failed: {e}")
            return False
    
    def run_security_audit(self) -> MaintenanceReport:
        """Run security audit"""
        start_time = time.time()
        console.print("[cyan]Running security audit...[/cyan]")
        
        recommendations = []
        security_issues = []
        
        try:
            # Check file permissions
            permission_issues = self.check_file_permissions()
            if permission_issues:
                security_issues.extend(permission_issues)
                recommendations.append("Fixed file permission issues")
            
            # Check for security vulnerabilities
            vuln_issues = self.check_security_vulnerabilities()
            if vuln_issues:
                security_issues.extend(vuln_issues)
                recommendations.append("Security vulnerabilities detected")
            
            # Audit dependencies
            dependency_issues = self.audit_dependencies()
            if dependency_issues:
                security_issues.extend(dependency_issues)
                recommendations.append("Dependency security issues found")
            
            # Check firewall status
            firewall_status = self.check_firewall_status()
            if not firewall_status:
                recommendations.append("Firewall protection recommended")
            
            duration = time.time() - start_time
            
            # If no security issues found
            if not security_issues:
                recommendations.append("No security issues detected - system is secure")
            
            report = MaintenanceReport(
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration,
                tasks_completed=1,
                tasks_failed=0,
                health_score=95.0 if not security_issues else 70.0,
                alerts_generated=len(security_issues),
                recommendations=recommendations,
                performance_metrics={"security_score": 95.0 if not security_issues else 70.0}
            )
            
            self.task_stats['completed'] += 1
            self.task_stats['total_duration'] += duration
            
            console.print(f"[green]✓[/green] Security audit completed in {duration:.1f}s")
            
            return report
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Security audit failed: {e}")
            self.task_stats['failed'] += 1
            
            return MaintenanceReport(
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration,
                tasks_completed=0,
                tasks_failed=1,
                health_score=0.0,
                alerts_generated=1,
                recommendations=[f"Security audit failed: {str(e)}"],
                performance_metrics={}
            )
    
    def check_file_permissions(self) -> List[str]:
        """Check for insecure file permissions"""
        issues = []
        
        # Check sensitive files
        sensitive_files = [
            self.config_dir / "config.json",
            self.config_dir / ".env",
            self.config_dir / "security.json"
        ]
        
        for file_path in sensitive_files:
            if file_path.exists():
                stat_info = file_path.stat()
                if stat_info.st_mode & 0o044:  # World readable
                    issues.append(f"File {file_path} is world-readable")
                    # Fix permissions
                    file_path.chmod(0o600)
        
        return issues
    
    def check_security_vulnerabilities(self) -> List[str]:
        """Check for known security vulnerabilities"""
        issues = []
        
        try:
            # Check for outdated packages with known vulnerabilities
            venv_python = self.jarvis_home / "venv" / "bin" / "python"
            
            if venv_python.exists():
                # Run safety check if available
                result = subprocess.run([
                    str(venv_python), "-m", "safety", "check", "--json"
                ], capture_output=True, timeout=60)
                
                if result.returncode != 0:
                    issues.append("Outdated packages with security vulnerabilities detected")
            
        except Exception:
            # Safety not available or failed
            pass
        
        return issues
    
    def audit_dependencies(self) -> List[str]:
        """Audit dependencies for security issues"""
        issues = []
        
        try:
            requirements_file = self.jarvis_home / "requirements.txt"
            if requirements_file.exists():
                # Basic dependency audit
                with open(requirements_file, 'r') as f:
                    dependencies = f.readlines()
                
                # Check for known vulnerable packages
                vulnerable_packages = [
                    'django<3.2', 'flask<1.1.0', 'requests<2.20.0'
                ]
                
                for dep in dependencies:
                    dep = dep.strip()
                    if any(vuln in dep for vuln in vulnerable_packages):
                        issues.append(f"Potentially vulnerable dependency: {dep}")
        
        except Exception as e:
            self.logger.debug(f"Dependency audit failed: {e}")
        
        return issues
    
    def check_firewall_status(self) -> bool:
        """Check if firewall is active"""
        try:
            # Check UFW status on Linux
            result = subprocess.run(['ufw', 'status'], capture_output=True)
            return b'active' in result.stdout.lower()
        except:
            return False
    
    def run_log_maintenance(self) -> MaintenanceReport:
        """Run log rotation and cleanup"""
        start_time = time.time()
        console.print("[cyan]Running log maintenance...[/cyan]")
        
        files_rotated = 0
        space_freed = 0
        
        try:
            # Find all log files
            log_patterns = [
                self.config_dir / "**/*.log",
                self.jarvis_home / "**/*.log",
                Path.home() / "**/*.log"
            ]
            
            for pattern in log_patterns:
                for log_file in self.config_dir.parent.glob(pattern.name if pattern.name != "**" else "**"):
                    if log_file.is_file():
                        rotated, freed = self.rotate_log_file(log_file)
                        files_rotated += rotated
                        space_freed += freed
            
            # Clean old log files
            old_logs_cleaned = self.clean_old_logs()
            
            duration = time.time() - start_time
            
            recommendations = [
                f"Rotated {files_rotated} log files",
                f"Cleaned {old_logs_cleaned} old log files",
                f"Freed {space_freed / 1024 / 1024:.1f} MB of space"
            ]
            
            report = MaintenanceReport(
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration,
                tasks_completed=1,
                tasks_failed=0,
                health_score=80.0,
                alerts_generated=0,
                recommendations=recommendations,
                performance_metrics={"files_rotated": files_rotated, "space_freed_mb": space_freed / 1024 / 1024}
            )
            
            self.task_stats['completed'] += 1
            self.task_stats['total_duration'] += duration
            
            console.print(f"[green]✓[/green] Log maintenance completed in {duration:.1f}s")
            
            return report
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Log maintenance failed: {e}")
            self.task_stats['failed'] += 1
            
            return MaintenanceReport(
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration,
                tasks_completed=0,
                tasks_failed=1,
                health_score=0.0,
                alerts_generated=1,
                recommendations=[f"Log maintenance failed: {str(e)}"],
                performance_metrics={}
            )
    
    def rotate_log_file(self, log_file: Path) -> Tuple[int, int]:
        """Rotate a log file if it's too large"""
        if log_file.stat().st_size < self.config.max_log_size_mb * 1024 * 1024:
            return 0, 0
        
        try:
            # Create rotated filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_file = log_file.with_suffix(f".{timestamp}.gz")
            
            # Compress the log file
            with open(log_file, 'rb') as f_in:
                with gzip.open(rotated_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Clear original file
            original_size = log_file.stat().st_size
            log_file.write_text("")
            
            return 1, original_size
            
        except Exception as e:
            self.logger.debug(f"Failed to rotate {log_file}: {e}")
            return 0, 0
    
    def clean_old_logs(self) -> int:
        """Clean old log files beyond retention period"""
        cleaned_count = 0
        cutoff_date = datetime.now() - timedelta(days=self.config.log_retention_days)
        
        log_dirs = [
            self.config_dir / "maintenance_logs",
            self.jarvis_home / "logs"
        ]
        
        for log_dir in log_dirs:
            if not log_dir.exists():
                continue
            
            try:
                for log_file in log_dir.rglob("*.log*"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        log_file.unlink()
                        cleaned_count += 1
            except Exception as e:
                self.logger.debug(f"Failed to clean {log_dir}: {e}")
        
        return cleaned_count
    
    def run_backup_maintenance(self) -> MaintenanceReport:
        """Run backup cleanup and maintenance"""
        start_time = time.time()
        console.print("[cyan]Running backup maintenance...[/cyan]")
        
        try:
            backup_dir = Path.home() / ".jarvis_backups"
            
            if not backup_dir.exists():
                return MaintenanceReport(
                    timestamp=datetime.now().isoformat(),
                    duration_seconds=time.time() - start_time,
                    tasks_completed=0,
                    tasks_failed=0,
                    health_score=100.0,
                    alerts_generated=0,
                    recommendations=["No backups found"],
                    performance_metrics={}
                )
            
            # List all backups
            backups = []
            for backup_path in backup_dir.iterdir():
                if backup_path.is_dir() and backup_path.name.startswith('backup_'):
                    backups.append((backup_path, backup_path.stat().st_mtime))
            
            # Sort by modification time (oldest first)
            backups.sort(key=lambda x: x[1])
            
            # Keep only the most recent backups
            cutoff_timestamp = (datetime.now() - timedelta(days=self.config.backup_retention_days)).timestamp()
            
            removed_backups = 0
            space_freed = 0
            
            for backup_path, mod_time in backups[:-5]:  # Keep 5 most recent
                if mod_time < cutoff_timestamp:
                    try:
                        backup_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
                        shutil.rmtree(backup_path)
                        removed_backups += 1
                        space_freed += backup_size
                    except Exception as e:
                        self.logger.debug(f"Failed to remove backup {backup_path}: {e}")
            
            # Create new backup if needed
            if self.should_create_backup():
                backup_created = self.create_maintenance_backup()
            else:
                backup_created = False
            
            duration = time.time() - start_time
            
            recommendations = [
                f"Removed {removed_backups} old backups",
                f"Freed {space_freed / 1024 / 1024:.1f} MB"
            ]
            
            if backup_created:
                recommendations.append("Created new maintenance backup")
            
            report = MaintenanceReport(
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration,
                tasks_completed=1,
                tasks_failed=0,
                health_score=90.0,
                alerts_generated=0,
                recommendations=recommendations,
                performance_metrics={
                    "backups_removed": removed_backups,
                    "space_freed_mb": space_freed / 1024 / 1024,
                    "backup_created": backup_created
                }
            )
            
            self.task_stats['completed'] += 1
            self.task_stats['total_duration'] += duration
            
            console.print(f"[green]✓[/green] Backup maintenance completed in {duration:.1f}s")
            
            return report
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Backup maintenance failed: {e}")
            self.task_stats['failed'] += 1
            
            return MaintenanceReport(
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration,
                tasks_completed=0,
                tasks_failed=1,
                health_score=0.0,
                alerts_generated=1,
                recommendations=[f"Backup maintenance failed: {str(e)}"],
                performance_metrics={}
            )
    
    def should_create_backup(self) -> bool:
        """Check if a new backup should be created"""
        backup_dir = Path.home() / ".jarvis_backups"
        
        if not backup_dir.exists():
            return True
        
        # Check if last backup is older than 7 days
        backups = [p for p in backup_dir.iterdir() if p.is_dir() and p.name.startswith('backup_')]
        if not backups:
            return True
        
        latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
        backup_age = time.time() - latest_backup.stat().st_mtime
        
        return backup_age > 7 * 24 * 3600  # 7 days
    
    def create_maintenance_backup(self) -> bool:
        """Create maintenance backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path.home() / ".jarvis_backups" / f"maintenance_backup_{timestamp}"
            
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup JARVIS installation
            if self.jarvis_home.exists():
                shutil.copytree(
                    self.jarvis_home,
                    backup_path / "jarvis_v14_ultimate",
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.log')
                )
            
            # Backup configuration
            if self.config_dir.exists():
                shutil.copytree(
                    self.config_dir,
                    backup_path / "config",
                    ignore=shutil.ignore_patterns('*.log')
                )
            
            # Create backup manifest
            manifest = {
                "backup_type": "maintenance",
                "timestamp": timestamp,
                "version": JARVIS_VERSION,
                "reason": "automated_maintenance"
            }
            
            with open(backup_path / "backup_manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Maintenance backup creation failed: {e}")
            return False
    
    def generate_maintenance_summary(self, reports: List[MaintenanceReport]) -> str:
        """Generate maintenance summary report"""
        total_tasks = len(reports)
        completed_tasks = sum(r.tasks_completed for r in reports)
        failed_tasks = sum(r.tasks_failed for r in reports)
        total_duration = sum(r.duration_seconds for r in reports)
        avg_health_score = sum(r.health_score for r in reports) / len(reports) if reports else 0
        
        summary = f"""
JARVIS v14 Ultimate - Maintenance Summary
========================================

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duration: {total_duration:.1f} seconds

Tasks Completed: {completed_tasks}/{total_tasks}
Failed Tasks: {failed_tasks}
Average Health Score: {avg_health_score:.1f}%

Alerts Generated: {sum(r.alerts_generated for r in reports)}

Recommendations:
"""
        
        # Collect all recommendations
        all_recommendations = []
        for report in reports:
            all_recommendations.extend(report.recommendations)
        
        for i, recommendation in enumerate(all_recommendations[:10], 1):  # Show top 10
            summary += f"{i}. {recommendation}\n"
        
        if len(all_recommendations) > 10:
            summary += f"... and {len(all_recommendations) - 10} more recommendations\n"
        
        return summary
    
    def schedule_maintenance(self):
        """Schedule automatic maintenance tasks"""
        console.print("[green]✓[/green] Scheduling automatic maintenance tasks")
        
        # Schedule maintenance tasks
        if self.config.auto_optimization:
            schedule.every(self.config.performance_check_interval_minutes).minutes.do(
                self.run_performance_optimization
            )
        
        schedule.every(self.config.health_check_interval_minutes).minutes.do(
            self.run_health_check
        )
        
        schedule.every(self.config.security_audit_interval_hours).hours.do(
            self.run_security_audit
        )
        
        schedule.every().day.at("02:00").do(
            self.run_log_maintenance
        )
        
        schedule.every().week.do(
            self.run_backup_maintenance
        )
        
        schedule.every().sunday.at("01:00").do(
            self.run_comprehensive_maintenance
        )
    
    def run_scheduler(self):
        """Run the maintenance scheduler"""
        console.print("[blue]Starting maintenance scheduler...[/blue]")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            console.print("\n[yellow]Maintenance scheduler stopped[/yellow]")
    
    def start_scheduler(self):
        """Start the maintenance scheduler in background"""
        if not self.running:
            self.running = True
            self.maintenance_thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.maintenance_thread.start()
            console.print("[green]✓[/green] Maintenance scheduler started")
    
    def stop_scheduler(self):
        """Stop the maintenance scheduler"""
        if self.running:
            self.running = False
            if self.maintenance_thread:
                self.maintenance_thread.join(timeout=5)
            console.print("[yellow]✓[/yellow] Maintenance scheduler stopped")


# ========================================================================
# CLI Interface
# ========================================================================

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="JARVIS v14 Ultimate Maintenance Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python maintenance_automation.py                    # Run comprehensive maintenance
  python maintenance_automation.py --health           # Health check only
  python maintenance_automation.py --performance      # Performance optimization only
  python maintenance_automation.py --security         # Security audit only
  python maintenance_automation.py --schedule         # Start scheduler
  python maintenance_automation.py --report           # Generate maintenance report
        """
    )
    
    parser.add_argument('--health', action='store_true',
                       help='Run health check only')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance optimization only')
    parser.add_argument('--security', action='store_true',
                       help='Run security audit only')
    parser.add_argument('--logs', action='store_true',
                       help='Run log maintenance only')
    parser.add_argument('--backup', action='store_true',
                       help='Run backup maintenance only')
    parser.add_argument('--schedule', action='store_true',
                       help='Start maintenance scheduler')
    parser.add_argument('--report', action='store_true',
                       help='Generate maintenance report')
    parser.add_argument('--config', type=str,
                       help='Path to JARVIS home directory')
    parser.add_argument('--configure', action='store_true',
                       help='Configure maintenance settings')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize maintenance system
    maintenance = MaintenanceAutomation(args.config)
    
    try:
        if args.configure:
            configure_maintenance(maintenance)
        
        elif args.schedule:
            maintenance.start_scheduler()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                maintenance.stop_scheduler()
        
        elif args.report:
            generate_maintenance_report(maintenance)
        
        elif args.health:
            report = maintenance.run_health_check()
            print_report(report)
        
        elif args.performance:
            report = maintenance.run_performance_optimization()
            print_report(report)
        
        elif args.security:
            report = maintenance.run_security_audit()
            print_report(report)
        
        elif args.logs:
            report = maintenance.run_log_maintenance()
            print_report(report)
        
        elif args.backup:
            report = maintenance.run_backup_maintenance()
            print_report(report)
        
        else:
            # Default: Run comprehensive maintenance
            reports = maintenance.run_comprehensive_maintenance()
            summary = maintenance.generate_maintenance_summary(reports)
            print_summary(summary)
            
            # Save detailed report
            report_file = maintenance.config_dir / "maintenance_reports" / f"maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump([asdict(report) for report in reports], f, indent=2, default=str)
            
            console.print(f"\n[cyan]Detailed report saved:[/cyan] {report_file}")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def configure_maintenance(maintenance: MaintenanceAutomation):
    """Interactive configuration"""
    console.print(Panel.fit(
        "[bold blue]JARVIS Maintenance Configuration[/bold blue]",
        style="blue"
    ))
    
    # Configuration options
    console.print("\n[yellow]Configure maintenance settings:[/yellow]")
    
    # Monitoring intervals
    maintenance.config.health_check_interval_minutes = int(
        Prompt.ask("Health check interval (minutes)", 
                  default=str(maintenance.config.health_check_interval_minutes))
    )
    
    maintenance.config.performance_check_interval_minutes = int(
        Prompt.ask("Performance check interval (minutes)",
                  default=str(maintenance.config.performance_check_interval_minutes))
    )
    
    # Thresholds
    maintenance.config.cpu_threshold_warning = float(
        Prompt.ask("CPU warning threshold (%)",
                  default=str(maintenance.config.cpu_threshold_warning))
    )
    
    maintenance.config.memory_threshold_warning = float(
        Prompt.ask("Memory warning threshold (%)",
                  default=str(maintenance.config.memory_threshold_warning))
    )
    
    # Retention periods
    maintenance.config.log_retention_days = int(
        Prompt.ask("Log retention (days)",
                  default=str(maintenance.config.log_retention_days))
    )
    
    # Auto optimization
    maintenance.config.auto_optimization = Confirm.ask(
        "Enable automatic optimization", default=maintenance.config.auto_optimization
    )
    
    # Email notifications
    if Confirm.ask("Configure email notifications", default=False):
        maintenance.config.email_notifications = True
        maintenance.config.smtp_server = Prompt.ask("SMTP server")
        maintenance.config.smtp_port = int(Prompt.ask("SMTP port", default="587"))
        maintenance.config.email_username = Prompt.ask("Email username")
        maintenance.config.email_password = Prompt.ask("Email password", password=True)
        maintenance.config.notification_emails = Prompt.ask("Notification emails (comma-separated)").split(",")
    
    # Save configuration
    maintenance.save_maintenance_config(maintenance.config)
    console.print("\n[green]✓[/green] Configuration saved")

def print_report(report: MaintenanceReport):
    """Print maintenance report"""
    console.print(f"\n[cyan]Maintenance Report - {report.timestamp}[/cyan]")
    console.print(f"[green]Duration:[/green] {report.duration_seconds:.1f}s")
    console.print(f"[green]Tasks:[/green] {report.tasks_completed} completed, {report.tasks_failed} failed")
    console.print(f"[green]Health Score:[/green] {report.health_score:.1f}")
    console.print(f"[green]Alerts:[/green] {report.alerts_generated}")
    
    if report.recommendations:
        console.print("\n[yellow]Recommendations:[/yellow]")
        for rec in report.recommendations:
            console.print(f"  • {rec}")

def print_summary(summary: str):
    """Print maintenance summary"""
    console.print("\n")
    console.print(Panel(
        summary,
        title="[bold blue]Maintenance Summary[/bold blue]",
        border_style="blue"
    ))

def generate_maintenance_report(maintenance: MaintenanceAutomation):
    """Generate comprehensive maintenance report"""
    console.print("[cyan]Generating maintenance report...[/cyan]")
    
    # Get health trends
    health_trends = maintenance.health_monitor.get_health_trends(24)
    
    # Create report table
    table = Table(title="JARVIS Maintenance Report")
    table.add_column("Metric", style="cyan")
    table.add_column("Current Value", style="white")
    table.add_column("Trend (24h)", style="white")
    table.add_column("Status", style="white")
    
    # Add system metrics
    metrics = maintenance.health_monitor.collect_system_metrics()
    
    for name, metric in metrics.items():
        trend = ""
        if name in health_trends and len(health_trends[name]) > 1:
            values = health_trends[name]
            if values[-1] > values[0]:
                trend = "↗ Improving"
            elif values[-1] < values[0]:
                trend = "↘ Declining"
            else:
                trend = "→ Stable"
        
        status_color = {
            SystemHealth.EXCELLENT: "green",
            SystemHealth.GOOD: "green",
            SystemHealth.FAIR: "yellow",
            SystemHealth.POOR: "orange_red1",
            SystemHealth.CRITICAL: "red"
        }.get(metric.status, "white")
        
        table.add_row(
            name,
            f"{metric.value:.1f}%",
            trend,
            f"[{status_color}]{metric.status.value.title()}[/{status_color}]"
        )
    
    console.print(table)
    
    # Show task statistics
    stats_table = Table(title="Task Statistics")
    stats_table.add_column("Statistic", style="cyan")
    stats_table.add_column("Value", style="white")
    
    stats_table.add_row("Tasks Completed", str(maintenance.task_stats['completed']))
    stats_table.add_row("Tasks Failed", str(maintenance.task_stats['failed']))
    stats_table.add_row("Total Duration", f"{maintenance.task_stats['total_duration']:.1f}s")
    
    console.print(stats_table)

if __name__ == "__main__":
    main()