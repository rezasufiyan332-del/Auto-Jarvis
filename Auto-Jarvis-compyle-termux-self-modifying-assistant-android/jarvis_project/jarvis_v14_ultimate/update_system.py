#!/usr/bin/env python3
"""
JARVIS v14 ULTIMATE - Auto-Update System
=========================================

Author: JARVIS Development Team
Version: 14.0 Ultimate
Description: Advanced auto-update system with rollback capabilities,
             version management, and cross-platform support

Features:
- Automatic version checking
- Incremental updates
- Rollback on failure
- Backup before update
- Update scheduling
- Progress tracking
- Cross-platform compatibility
"""

import os
import sys
import json
import time
import shutil
import subprocess
import threading
import hashlib
import tempfile
import requests
import zipfile
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import schedule
import yaml
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm, Prompt
from rich.markdown import Markdown
from rich.tree import Tree
from rich.live import Live
from rich.align import Align

# Configuration
JARVIS_VERSION = "14.0 Ultimate"
UPDATE_CONFIG_FILE = ".jarvis_v14_ultimate/updates.json"
BACKUP_DIR_FORMAT = ".jarvis_backups/backup_{timestamp}"
UPDATE_CHANNEL = "stable"  # stable, beta, dev
UPDATE_SERVER = "https://api.jarvis-v14-ultimate.com"
UPDATE_TIMEOUT = 300  # 5 minutes
MAX_RETRIES = 3
CHUNK_SIZE = 8192

console = Console()

# ========================================================================
# Data Structures
# ========================================================================

class UpdateStatus(Enum):
    """Update status enumeration"""
    IDLE = "idle"
    CHECKING = "checking"
    DOWNLOADING = "downloading"
    INSTALLING = "installing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"

class UpdateType(Enum):
    """Types of updates"""
    PATCH = "patch"        # Bug fixes, small changes
    MINOR = "minor"        # New features, improvements
    MAJOR = "major"        # Breaking changes, major overhaul
    SECURITY = "security"  # Security updates
    HOTFIX = "hotfix"      # Critical fixes

@dataclass
class VersionInfo:
    """Version information structure"""
    version: str
    release_date: str
    update_type: UpdateType
    description: str
    size_bytes: int
    checksum: str
    download_url: str
    changelog: List[str]
    dependencies: List[str]
    breaking_changes: List[str]

@dataclass
class UpdateProgress:
    """Update progress tracking"""
    status: UpdateStatus
    current_step: str
    total_steps: int
    current_step_num: int
    percentage: float
    speed_mbps: float = 0.0
    eta_seconds: float = 0.0
    error_message: Optional[str] = None

@dataclass
class UpdateConfig:
    """Update system configuration"""
    auto_check: bool = True
    auto_download: bool = False
    auto_install: bool = False
    check_interval_hours: int = 24
    backup_before_update: bool = True
    rollback_on_failure: bool = True
    max_backups: int = 10
    update_channel: str = "stable"
    update_server: str = UPDATE_SERVER
    timeout_seconds: int = UPDATE_TIMEOUT
    max_retries: int = MAX_RETRIES

# ========================================================================
# Update System Core
# ========================================================================

class UpdateSystem:
    """JARVIS v14 Ultimate Auto-Update System"""
    
    def __init__(self, jarvis_home: str = None):
        self.jarvis_home = Path(jarvis_home or Path.home() / ".jarvis_v14_ultimate")
        self.config_dir = Path.home() / ".config" / "jarvis_v14_ultimate"
        self.backup_dir = Path.home() / ".jarvis_backups"
        self.update_config_file = self.config_dir / "updates.json"
        self.log_file = self.config_dir / "update_logs" / f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Create directories
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        (self.config_dir / "update_logs").mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self.load_update_config()
        self.current_version = JARVIS_VERSION
        
        # Setup logging
        self.setup_logging()
        
        # State tracking
        self.current_progress = UpdateProgress(
            status=UpdateStatus.IDLE,
            current_step="",
            total_steps=0,
            current_step_num=0,
            percentage=0.0
        )
        
        self.update_lock = threading.Lock()
        self.is_updating = False
        
        # Network session with retry logic
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        console.print(f"[green]✓[/green] Update System initialized for JARVIS v{JARVIS_VERSION}")
    
    def setup_logging(self):
        """Setup comprehensive logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("JARVIS-UpdateSystem")
    
    def load_update_config(self) -> UpdateConfig:
        """Load update system configuration"""
        try:
            if self.update_config_file.exists():
                with open(self.update_config_file, 'r') as f:
                    data = json.load(f)
                return UpdateConfig(**data)
        except Exception as e:
            self.logger.error(f"Failed to load update config: {e}")
        
        # Return default configuration
        return UpdateConfig()
    
    def save_update_config(self):
        """Save update system configuration"""
        try:
            with open(self.update_config_file, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save update config: {e}")
    
    def check_for_updates(self) -> Optional[VersionInfo]:
        """Check for available updates"""
        with self.update_lock:
            if self.is_updating:
                self.logger.warning("Update already in progress")
                return None
            
            self.update_progress(UpdateStatus.CHECKING, "Checking for updates", 4, 1)
            
            try:
                # Prepare request
                params = {
                    'current_version': self.current_version,
                    'channel': self.config.update_channel,
                    'platform': self.detect_platform(),
                    'arch': self.detect_architecture()
                }
                
                headers = {
                    'User-Agent': f'JARVIS-v{JARVIS_VERSION}-UpdateSystem',
                    'Accept': 'application/json'
                }
                
                self.logger.info("Checking for updates...")
                response = self.session.get(
                    f"{self.config.update_server}/api/check-update",
                    params=params,
                    headers=headers,
                    timeout=self.config.timeout_seconds
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('update_available', False):
                        update_info = VersionInfo(**data['update_info'])
                        self.logger.info(f"Update available: {update_info.version}")
                        return update_info
                    else:
                        self.logger.info("No updates available")
                        return None
                        
                else:
                    self.logger.error(f"Update check failed: HTTP {response.status_code}")
                    return None
                    
            except Exception as e:
                self.logger.error(f"Failed to check for updates: {e}")
                return None
            
            finally:
                self.update_progress(UpdateStatus.IDLE, "", 0, 0)
    
    def detect_platform(self) -> str:
        """Detect current platform"""
        import platform
        system = platform.system().lower()
        
        if system == "linux":
            # Check for Termux
            if os.environ.get('TERMUX_VERSION'):
                return "termux"
            else:
                return "linux"
        elif system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"
    
    def detect_architecture(self) -> str:
        """Detect system architecture"""
        import platform
        arch = platform.machine().lower()
        
        if arch in ['x86_64', 'amd64']:
            return 'x86_64'
        elif arch in ['arm64', 'aarch64']:
            return 'arm64'
        elif arch in ['armv7l', 'armv6l']:
            return 'arm'
        else:
            return arch
    
    def download_update(self, update_info: VersionInfo) -> bool:
        """Download update package with progress tracking"""
        with self.update_lock:
            if self.is_updating:
                return False
            
            self.is_updating = True
            
            try:
                self.update_progress(
                    UpdateStatus.DOWNLOADING,
                    "Downloading update",
                    5,
                    2,
                    0.0
                )
                
                # Create temporary download directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    update_file = temp_path / f"jarvis_update_{update_info.version}.zip"
                    
                    # Download with progress
                    self.logger.info(f"Downloading update from {update_info.download_url}")
                    
                    response = self.session.get(
                        update_info.download_url,
                        stream=True,
                        timeout=self.config.timeout_seconds
                    )
                    
                    response.raise_for_status()
                    
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    with open(update_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                if total_size > 0:
                                    percentage = (downloaded / total_size) * 100
                                    speed = self.calculate_speed(downloaded)
                                    self.update_progress(
                                        UpdateStatus.DOWNLOADING,
                                        "Downloading update",
                                        5,
                                        2,
                                        percentage,
                                        speed
                                    )
                    
                    # Verify checksum
                    if not self.verify_checksum(update_file, update_info.checksum):
                        raise ValueError("Checksum verification failed")
                    
                    # Extract update
                    self.update_progress(
                        UpdateStatus.DOWNLOADING,
                        "Extracting update",
                        5,
                        3,
                        100.0
                    )
                    
                    extract_dir = temp_path / "extracted"
                    self.extract_update(update_file, extract_dir)
                    
                    # Install update
                    return self.install_update(extract_dir, update_info)
                    
            except Exception as e:
                self.logger.error(f"Update download failed: {e}")
                self.update_progress(
                    UpdateStatus.FAILED,
                    f"Download failed: {str(e)}",
                    5,
                    2,
                    0.0,
                    error_message=str(e)
                )
                return False
            
            finally:
                self.is_updating = False
    
    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            actual_checksum = sha256_hash.hexdigest()
            self.logger.info(f"Expected checksum: {expected_checksum}")
            self.logger.info(f"Actual checksum: {actual_checksum}")
            
            return actual_checksum == expected_checksum
            
        except Exception as e:
            self.logger.error(f"Checksum verification failed: {e}")
            return False
    
    def extract_update(self, archive_path: Path, extract_dir: Path):
        """Extract update archive"""
        extract_dir.mkdir(exist_ok=True)
        
        if archive_path.suffix.lower() == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif archive_path.suffix.lower() in ['.tar', '.gz', '.bz2']:
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_dir)
        else:
            raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
    
    def install_update(self, extract_dir: Path, update_info: VersionInfo) -> bool:
        """Install the downloaded update"""
        try:
            self.update_progress(
                UpdateStatus.INSTALLING,
                "Creating backup",
                6,
                4,
                10.0
            )
            
            # Create backup before update
            if self.config.backup_before_update:
                if not self.create_backup():
                    self.logger.error("Failed to create backup")
                    return False
            
            self.update_progress(
                UpdateStatus.INSTALLING,
                "Installing files",
                6,
                5,
                30.0
            )
            
            # Install update files
            if not self.copy_update_files(extract_dir):
                raise RuntimeError("Failed to copy update files")
            
            self.update_progress(
                UpdateStatus.INSTALLING,
                "Updating configuration",
                6,
                6,
                70.0
            )
            
            # Update configuration
            self.update_configuration(update_info)
            
            self.update_progress(
                UpdateStatus.COMPLETED,
                "Update completed successfully",
                6,
                6,
                100.0
            )
            
            # Post-update tasks
            self.post_update_tasks(update_info)
            
            self.logger.info("Update installation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Update installation failed: {e}")
            
            if self.config.rollback_on_failure:
                self.update_progress(
                    UpdateStatus.ROLLING_BACK,
                    "Rolling back changes",
                    6,
                    5,
                    50.0
                )
                self.rollback_update()
            
            self.update_progress(
                UpdateStatus.FAILED,
                f"Installation failed: {str(e)}",
                6,
                5,
                0.0,
                error_message=str(e)
            )
            return False
    
    def create_backup(self) -> bool:
        """Create backup of current installation"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"
            
            self.logger.info(f"Creating backup at {backup_path}")
            
            # Copy installation directory
            if self.jarvis_home.exists():
                shutil.copytree(
                    self.jarvis_home,
                    backup_path / "jarvis_v14_ultimate",
                    ignore=shutil.ignore_patterns(
                        '__pycache__',
                        '*.pyc',
                        '*.pyo',
                        '*.log',
                        '.git'
                    )
                )
            
            # Copy configuration
            if self.config_dir.exists():
                shutil.copytree(
                    self.config_dir,
                    backup_path / "config",
                    ignore=shutil.ignore_patterns('*.log')
                )
            
            # Create backup manifest
            manifest = {
                "timestamp": timestamp,
                "version": self.current_version,
                "backup_type": "pre_update",
                "platform": self.detect_platform(),
                "files_backed_up": True
            }
            
            with open(backup_path / "backup_manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            self.logger.info(f"Backup created successfully: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove old backups to save space"""
        try:
            backup_dirs = sorted(
                [d for d in self.backup_dir.iterdir() if d.is_dir() and d.name.startswith('backup_')],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Keep only max_backups most recent
            for old_backup in backup_dirs[self.config.max_backups:]:
                shutil.rmtree(old_backup)
                self.logger.info(f"Removed old backup: {old_backup}")
                
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {e}")
    
    def copy_update_files(self, extract_dir: Path) -> bool:
        """Copy update files to installation directory"""
        try:
            # Find main JARVIS directory in extract
            jarvis_dir = None
            for item in extract_dir.iterdir():
                if item.is_dir() and item.name == "jarvis_v14_ultimate":
                    jarvis_dir = item
                    break
            
            if not jarvis_dir:
                # Try direct copy if no subdirectory
                jarvis_dir = extract_dir
            
            # Stop services if running
            self.stop_services()
            
            # Copy files
            for item in jarvis_dir.iterdir():
                if item.name in ['jarvis.py', 'core', 'config', 'requirements.txt']:
                    target = self.jarvis_home / item.name
                    
                    if item.is_dir():
                        if target.exists():
                            shutil.rmtree(target)
                        shutil.copytree(item, target)
                    else:
                        shutil.copy2(item, target)
            
            self.logger.info("Update files copied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to copy update files: {e}")
            return False
    
    def stop_services(self):
        """Stop JARVIS services before update"""
        try:
            platform = self.detect_platform()
            
            if platform == "linux":
                subprocess.run(
                    ["sudo", "systemctl", "stop", "jarvis-v14-ultimate"],
                    capture_output=True,
                    timeout=30
                )
            elif platform == "termux":
                subprocess.run(
                    ["sv", "stop", "jarvis-v14-ultimate"],
                    capture_output=True,
                    timeout=30
                )
            
            self.logger.info("Services stopped for update")
            
        except Exception as e:
            self.logger.warning(f"Failed to stop services: {e}")
    
    def start_services(self):
        """Start JARVIS services after update"""
        try:
            platform = self.detect_platform()
            
            if platform == "linux":
                subprocess.run(
                    ["sudo", "systemctl", "start", "jarvis-v14-ultimate"],
                    capture_output=True,
                    timeout=30
                )
            elif platform == "termux":
                subprocess.run(
                    ["sv", "start", "jarvis-v14-ultimate"],
                    capture_output=True,
                    timeout=30
                )
            
            self.logger.info("Services started after update")
            
        except Exception as e:
            self.logger.warning(f"Failed to start services: {e}")
    
    def update_configuration(self, update_info: VersionInfo):
        """Update configuration files"""
        try:
            # Update version in config
            config_file = self.config_dir / "config.json"
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                config['version'] = update_info.version
                config['last_update'] = datetime.now().isoformat()
                config['update_type'] = update_info.update_type.value
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
            
            self.logger.info("Configuration updated")
            
        except Exception as e:
            self.logger.error(f"Configuration update failed: {e}")
    
    def post_update_tasks(self, update_info: VersionInfo):
        """Perform post-update tasks"""
        try:
            # Restart services
            self.start_services()
            
            # Update Python packages if needed
            if update_info.dependencies:
                self.update_dependencies(update_info.dependencies)
            
            # Run migration scripts if present
            self.run_migration_scripts()
            
            # Update current version
            self.current_version = update_info.version
            
            # Create success marker
            success_marker = self.config_dir / "last_update_success.json"
            with open(success_marker, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "version": update_info.version,
                    "update_type": update_info.update_type.value,
                    "successful": True
                }, f, indent=2)
            
            self.logger.info("Post-update tasks completed")
            
        except Exception as e:
            self.logger.error(f"Post-update tasks failed: {e}")
    
    def update_dependencies(self, dependencies: List[str]):
        """Update Python dependencies"""
        try:
            venv_python = self.jarvis_home / "venv" / "bin" / "python"
            
            if venv_python.exists():
                subprocess.run(
                    [str(venv_python), "-m", "pip", "install"] + dependencies,
                    capture_output=True,
                    timeout=300
                )
                
                self.logger.info("Dependencies updated")
            
        except Exception as e:
            self.logger.error(f"Dependency update failed: {e}")
    
    def run_migration_scripts(self):
        """Run database/migrations scripts if present"""
        try:
            migration_dir = self.jarvis_home / "migrations"
            
            if migration_dir.exists():
                # Run Python migrations
                for script in migration_dir.glob("*.py"):
                    subprocess.run(
                        [sys.executable, str(script)],
                        cwd=str(self.jarvis_home),
                        timeout=60
                    )
                
                self.logger.info("Migration scripts executed")
            
        except Exception as e:
            self.logger.error(f"Migration execution failed: {e}")
    
    def rollback_update(self) -> bool:
        """Rollback to previous version"""
        try:
            self.logger.info("Starting rollback process")
            
            # Find most recent backup
            backup_dirs = sorted(
                [d for d in self.backup_dir.iterdir() if d.is_dir() and d.name.startswith('backup_')],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            if not backup_dirs:
                self.logger.error("No backup found for rollback")
                return False
            
            latest_backup = backup_dirs[0]
            self.logger.info(f"Rolling back to backup: {latest_backup}")
            
            # Stop services
            self.stop_services()
            
            # Restore files
            backup_jarvis = latest_backup / "jarvis_v14_ultimate"
            if backup_jarvis.exists():
                if self.jarvis_home.exists():
                    shutil.rmtree(self.jarvis_home)
                shutil.copytree(backup_jarvis, self.jarvis_home)
            
            backup_config = latest_backup / "config"
            if backup_config.exists():
                if self.config_dir.exists():
                    shutil.rmtree(self.config_dir)
                shutil.copytree(backup_config, self.config_dir)
            
            # Restart services
            self.start_services()
            
            # Create rollback marker
            rollback_marker = self.config_dir / "last_rollback.json"
            with open(rollback_marker, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "backup_used": str(latest_backup),
                    "rollback_successful": True
                }, f, indent=2)
            
            self.logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
    
    def update_progress(self, status: UpdateStatus, current_step: str, 
                       total_steps: int, current_step_num: int, percentage: float,
                       speed_mbps: float = 0.0, eta_seconds: float = 0.0,
                       error_message: Optional[str] = None):
        """Update current progress"""
        self.current_progress = UpdateProgress(
            status=status,
            current_step=current_step,
            total_steps=total_steps,
            current_step_num=current_step_num,
            percentage=percentage,
            speed_mbps=speed_mbps,
            eta_seconds=eta_seconds,
            error_message=error_message
        )
    
    def calculate_speed(self, bytes_downloaded: int) -> float:
        """Calculate download speed in MB/s"""
        # This is a simplified calculation
        # In a real implementation, you'd track time intervals
        return bytes_downloaded / (1024 * 1024)  # Convert to MB
    
    def schedule_updates(self):
        """Schedule automatic update checks"""
        if self.config.auto_check:
            schedule.every(self.config.check_interval_hours).hours.do(self.background_update_check)
            
            console.print("[green]✓[/green] Auto-update scheduler started")
            
            # Run initial check
            self.background_update_check()
    
    def background_update_check(self):
        """Background update check task"""
        try:
            update_info = self.check_for_updates()
            
            if update_info:
                self.logger.info(f"Update found: {update_info.version}")
                
                # Auto-download if enabled
                if self.config.auto_download:
                    if self.download_update(update_info):
                        self.logger.info("Update auto-downloaded successfully")
                    else:
                        self.logger.error("Auto-download failed")
                
                # Auto-install if enabled (not recommended for production)
                if self.config.auto_install:
                    console.print(f"[yellow]⚠[/yellow] Auto-install not recommended in production")
                    console.print(f"[yellow]⚠[/yellow] Manual intervention required for update installation")
        except Exception as e:
            self.logger.error(f"Background update check failed: {e}")
    
    def run_scheduler(self):
        """Run the update scheduler"""
        console.print("[blue]Starting update scheduler...[/blue]")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            console.print("\n[yellow]Update scheduler stopped[/yellow]")
    
    def get_update_status(self) -> Dict[str, Any]:
        """Get current update status"""
        return {
            "current_version": self.current_version,
            "is_updating": self.is_updating,
            "progress": asdict(self.current_progress),
            "config": asdict(self.config),
            "last_check": getattr(self, 'last_check_time', None)
        }
    
    def show_update_interface(self):
        """Show interactive update interface"""
        with Live(console=console, refresh_per_second=2) as live:
            while True:
                status = self.get_update_status()
                panel = self.create_status_panel(status)
                live.update(panel)
                
                if not self.is_updating:
                    time.sleep(5)
                else:
                    time.sleep(1)
    
    def create_status_panel(self, status: Dict[str, Any]) -> Panel:
        """Create status display panel"""
        progress = status['progress']
        
        # Progress bar
        progress_bar = f"[green]{'█' * int(progress['percentage'] / 5)}[/green]" + \
                      f"[dim]{'░' * int((100 - progress['percentage']) / 5)}[/dim]"
        
        status_text = f"""
[bold]JARVIS v14 Ultimate - Update System[/bold]

[cyan]Current Version:[/cyan] {status['current_version']}
[cyan]Status:[/cyan] {progress['status'].value.upper()}
[cyan]Step:[/cyan] {progress['current_step']}
[cyan]Progress:[/cyan] {progress['percentage']:.1f}%

{progress_bar}

[cyan]Configuration:[/cyan]
  Auto-check: {status['config']['auto_check']}
  Auto-download: {status['config']['auto_download']}
  Auto-install: {status['config']['auto_install']}
  Update channel: {status['config']['update_channel']}
        """
        
        if progress.get('error_message'):
            status_text += f"\n[red]Error:[/red] {progress['error_message']}"
        
        return Panel(
            Align.left(status_text),
            title="[bold blue]JARVIS Update System[/bold blue]",
            border_style="blue"
        )
    
    def interactive_update(self):
        """Interactive update interface"""
        console.print(Panel.fit(
            "[bold blue]JARVIS v14 Ultimate - Update System[/bold blue]",
            style="blue"
        ))
        
        # Check for updates
        console.print("[yellow]Checking for updates...[/yellow]")
        update_info = self.check_for_updates()
        
        if not update_info:
            console.print("[green]✓[/green] JARVIS is already up to date!")
            return
        
        # Show update information
        table = Table(title="Available Update")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Version", update_info.version)
        table.add_row("Type", update_info.update_type.value.upper())
        table.add_row("Size", f"{update_info.size_bytes / 1024 / 1024:.1f} MB")
        table.add_row("Release Date", update_info.release_date)
        table.add_row("Description", update_info.description)
        
        console.print(table)
        
        # Show changelog if available
        if update_info.changelog:
            console.print("\n[bold]Changelog:[/bold]")
            for change in update_info.changelog[:5]:  # Show first 5 changes
                console.print(f"  • {change}")
            
            if len(update_info.changelog) > 5:
                console.print(f"  ... and {len(update_info.changelog) - 5} more changes")
        
        # Show breaking changes warning
        if update_info.breaking_changes:
            console.print("\n[red]⚠ WARNING: Breaking Changes Detected[/red]")
            for change in update_info.breaking_changes:
                console.print(f"  • {change}")
        
        # Ask for confirmation
        if Confirm.ask("\nDo you want to install this update?"):
            # Confirm for breaking changes
            if update_info.breaking_changes:
                if not Confirm.ask("This update contains breaking changes. Continue?"):
                    console.print("[yellow]Update cancelled[/yellow]")
                    return
            
            # Download and install
            console.print("[yellow]Starting update process...[/yellow]")
            
            if self.download_update(update_info):
                console.print("[green]✓[/green] Update completed successfully!")
                console.print(f"[green]JARVIS is now at version {update_info.version}[/green]")
            else:
                console.print("[red]✗[/red] Update failed. Check logs for details.")
        else:
            console.print("[yellow]Update cancelled[/yellow]")


# ========================================================================
# CLI Interface
# ========================================================================

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="JARVIS v14 Ultimate Update System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update_system.py                    # Interactive update interface
  python update_system.py --check            # Check for updates only
  python update_system.py --auto             # Auto-update if available
  python update_system.py --schedule         # Start update scheduler
  python update_system.py --status           # Show current status
  python update_system.py --rollback         # Rollback to previous version
        """
    )
    
    parser.add_argument('--check', action='store_true',
                       help='Check for updates without downloading')
    parser.add_argument('--auto', action='store_true',
                       help='Automatically update if available')
    parser.add_argument('--schedule', action='store_true',
                       help='Start update scheduler service')
    parser.add_argument('--status', action='store_true',
                       help='Show current update status')
    parser.add_argument('--rollback', action='store_true',
                       help='Rollback to previous version')
    parser.add_argument('--config', type=str,
                       help='Path to JARVIS home directory')
    parser.add_argument('--channel', choices=['stable', 'beta', 'dev'],
                       default='stable', help='Update channel')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize update system
    update_system = UpdateSystem(args.config)
    
    # Set update channel
    if args.channel:
        update_system.config.update_channel = args.channel
        update_system.save_update_config()
    
    try:
        if args.check:
            update_info = update_system.check_for_updates()
            if update_info:
                console.print(f"[green]Update available: {update_info.version}[/green]")
                console.print(f"[yellow]{update_info.description}[/yellow]")
            else:
                console.print("[green]No updates available[/green]")
        
        elif args.auto:
            update_info = update_system.check_for_updates()
            if update_info:
                console.print(f"[yellow]Installing update {update_info.version}...[/yellow]")
                if update_system.download_update(update_info):
                    console.print("[green]✓ Update completed![/green]")
                else:
                    console.print("[red]✗ Update failed[/red]")
                    sys.exit(1)
            else:
                console.print("[green]JARVIS is up to date[/green]")
        
        elif args.schedule:
            update_system.schedule_updates()
            update_system.run_scheduler()
        
        elif args.status:
            status = update_system.get_update_status()
            console.print(json.dumps(status, indent=2, default=str))
        
        elif args.rollback:
            if Confirm.ask("Are you sure you want to rollback?"):
                if update_system.rollback_update():
                    console.print("[green]✓ Rollback completed[/green]")
                else:
                    console.print("[red]✗ Rollback failed[/red]")
                    sys.exit(1)
            else:
                console.print("[yellow]Rollback cancelled[/yellow]")
        
        else:
            # Default: Interactive interface
            update_system.interactive_update()
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()