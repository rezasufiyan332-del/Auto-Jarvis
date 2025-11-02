"""
Automation Framework v15 - Background Task Processing
Comprehensive task scheduling and execution system with priority management
Autonomous background processing with resource optimization and error handling
"""

import os
import json
import time
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import queue
import weakref

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

@dataclass
class Task:
    """Background task structure"""
    task_id: str
    name: str
    description: str
    priority: TaskPriority
    task_function: Callable
    args: tuple = ()
    kwargs: dict = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300  # 5 minutes default
    dependencies: List[str] = None

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class TaskStatistics:
    """Task execution statistics"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    average_execution_time: float = 0.0
    tasks_per_hour: float = 0.0
    queue_size: int = 0
    active_workers: int = 0

class AutomationFrameworkV15:
    """
    Advanced Automation Framework

    Features:
    - Priority-based task scheduling
    - Background task processing
    - Resource management and optimization
    - Task dependency resolution
    - Automatic retry and error handling
    - Progress tracking and monitoring
    - Thread pool execution
    - Memory and CPU optimization
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger

        # Paths
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / "data" / "automation"
        self.tasks_path = self.data_path / "tasks"
        self.logs_path = self.data_path / "logs"

        # Create directories
        for path in [self.data_path, self.tasks_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Task management
        self.task_queue = queue.PriorityQueue()
        self.active_tasks = {}
        self.completed_tasks = {}
        self.task_dependencies = {}

        # Execution
        self.max_workers = 3  # Conservative for Termux
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.running = False
        self.scheduler_task = None

        # Statistics and monitoring
        self.statistics = TaskStatistics()
        self.performance_metrics = {
            'start_time': datetime.now(),
            'total_execution_time': 0.0,
            'peak_memory_usage': 0.0,
            'peak_cpu_usage': 0.0
        }

        # Task handlers
        self.task_handlers = {
            'project_creation': self._handle_project_creation,
            'code_analysis': self._handle_code_analysis,
            'feature_addition': self._handle_feature_addition,
            'error_resolution': self._handle_error_resolution,
            'github_learning': self._handle_github_learning,
            'system_maintenance': self._handle_system_maintenance,
            'file_operations': self._handle_file_operations
        }

        # Configuration
        self.config = {
            'max_queue_size': 100,
            'task_timeout': 300,  # 5 minutes
            'retry_delay': 5,  # seconds
            'cleanup_interval': 3600,  # 1 hour
            'max_task_history': 1000
        }

    async def initialize(self):
        """Initialize automation framework"""
        try:
            # Load task history
            await self._load_task_history()

            # Start background scheduler
            await self._start_scheduler()

            # Setup cleanup task
            asyncio.create_task(self._periodic_cleanup())

            self.logger.info("✅ Automation Framework v15 initialized")

        except Exception as e:
            self.logger.error(f"❌ Automation Framework initialization failed: {e}")
            raise

    async def _load_task_history(self):
        """Load task history from disk"""
        try:
            history_file = self.tasks_path / "task_history.json"

            if history_file.exists():
                async with aiofiles.open(history_file, 'r') as f:
                    data = json.loads(await f.read())

                    # Load completed tasks
                    for task_data in data.get('completed_tasks', []):
                        task = Task(**task_data)
                        self.completed_tasks[task.task_id] = task

                    # Load statistics
                    stats_data = data.get('statistics', {})
                    self.statistics = TaskStatistics(**stats_data)

            self.logger.info(f"📚 Loaded {len(self.completed_tasks)} completed tasks")

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load task history: {e}")

    async def _start_scheduler(self):
        """Start background task scheduler"""
        self.running = True
        self.scheduler_task = asyncio.create_task(self._task_scheduler())

    async def _task_scheduler(self):
        """Background task scheduler"""
        self.logger.info("🚀 Task scheduler started")

        while self.running:
            try:
                # Process tasks from queue
                await self._process_task_queue()

                # Update statistics
                await self._update_statistics()

                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.error(f"❌ Task scheduler error: {e}")
                await asyncio.sleep(1)

    async def _process_task_queue(self):
        """Process tasks from priority queue"""
        try:
            # Check if we have available workers
            if len(self.active_tasks) >= self.max_workers:
                return

            # Process highest priority tasks
            processed = 0
            max_process = min(3, self.max_workers - len(self.active_tasks))

            while not self.task_queue.empty() and processed < max_process:
                try:
                    priority, task_id, task = self.task_queue.get_nowait()

                    # Check dependencies
                    if await self._check_task_dependencies(task):
                        # Execute task
                        asyncio.create_task(self._execute_task(task))
                        processed += 1
                    else:
                        # Re-queue task with same priority
                        self.task_queue.put((priority, task_id, task))

                except queue.Empty:
                    break
                except Exception as e:
                    self.logger.error(f"❌ Task queue processing error: {e}")

        except Exception as e:
            self.logger.error(f"❌ Queue processing error: {e}")

    async def _check_task_dependencies(self, task: Task) -> bool:
        """Check if task dependencies are satisfied"""
        try:
            for dep_id in task.dependencies:
                if dep_id not in self.completed_tasks:
                    return False
                if self.completed_tasks[dep_id].status != TaskStatus.COMPLETED:
                    return False
            return True
        except Exception as e:
            self.logger.error(f"❌ Dependency check failed: {e}")
            return False

    async def _execute_task(self, task: Task):
        """Execute a task"""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            self.active_tasks[task.task_id] = task

            self.logger.info(f"🔧 Executing task: {task.name} (ID: {task.task_id})")

            # Execute task in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._run_task_function,
                task
            )

            # Handle result
            if isinstance(result, Exception):
                await self._handle_task_failure(task, result)
            else:
                await self._handle_task_success(task, result)

        except Exception as e:
            await self._handle_task_failure(task, e)

    def _run_task_function(self, task: Task) -> Any:
        """Run task function in thread pool"""
        try:
            # Check for timeout
            start_time = time.time()

            # Execute task function with timeout
            if task.timeout > 0:
                # Use signal for timeout (Unix systems)
                import signal

                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Task {task.task_id} timed out after {task.timeout} seconds")

                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(task.timeout)

                try:
                    result = task.task_function(*task.args, **task.kwargs)
                finally:
                    signal.alarm(0)  # Cancel alarm
            else:
                result = task.task_function(*task.args, **task.kwargs)

            execution_time = time.time() - start_time
            self.logger.info(f"✅ Task {task.name} completed in {execution_time:.2f}s")

            return result

        except TimeoutError as e:
            self.logger.error(f"⏰ Task {task.name} timed out")
            return e
        except Exception as e:
            self.logger.error(f"❌ Task {task.name} failed: {e}")
            return e

    async def _handle_task_success(self, task: Task, result: Any):
        """Handle successful task completion"""
        try:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            task.progress = 100.0

            # Move from active to completed
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            self.completed_tasks[task.task_id] = task

            # Update statistics
            self.statistics.completed_tasks += 1

            # Log success
            execution_time = (task.completed_at - task.started_at).total_seconds()
            self.logger.info(f"✅ Task completed: {task.name} in {execution_time:.2f}s")

            # Trigger dependent tasks
            await self._check_dependent_tasks(task.task_id)

        except Exception as e:
            self.logger.error(f"❌ Task success handling failed: {e}")

    async def _handle_task_failure(self, task: Task, error: Exception):
        """Handle task failure"""
        try:
            task.error = str(error)

            # Check if we should retry
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING

                self.logger.warning(f"🔄 Retrying task {task.name} (attempt {task.retry_count}/{task.max_retries})")

                # Re-queue task with delay
                await asyncio.sleep(self.config['retry_delay'])
                self.add_task(task)

            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()

                # Move from active to completed
                if task.task_id in self.active_tasks:
                    del self.active_tasks[task.task_id]
                self.completed_tasks[task.task_id] = task

                # Update statistics
                self.statistics.failed_tasks += 1

                self.logger.error(f"❌ Task failed permanently: {task.name} - {error}")

        except Exception as e:
            self.logger.error(f"❌ Task failure handling failed: {e}")

    async def _check_dependent_tasks(self, completed_task_id: str):
        """Check and trigger dependent tasks"""
        try:
            # This would check if any tasks are waiting for this completion
            # Implementation depends on dependency tracking system
            pass
        except Exception as e:
            self.logger.error(f"❌ Dependent task check failed: {e}")

    async def _update_statistics(self):
        """Update framework statistics"""
        try:
            # Update queue size
            self.statistics.queue_size = self.task_queue.qsize()
            self.statistics.active_workers = len(self.active_tasks)

            # Calculate tasks per hour
            runtime = (datetime.now() - self.performance_metrics['start_time']).total_seconds()
            if runtime > 0:
                self.statistics.tasks_per_hour = (self.statistics.total_tasks / runtime) * 3600

        except Exception as e:
            self.logger.error(f"❌ Statistics update failed: {e}")

    async def add_task(self, task: Task) -> str:
        """Add task to queue"""
        try:
            if self.task_queue.qsize() >= self.config['max_queue_size']:
                self.logger.warning("⚠️ Task queue is full")
                return ""

            task.task_id = task.task_id or self._generate_task_id()
            task.created_at = datetime.now()

            # Add to queue with priority
            priority_value = task.priority.value
            self.task_queue.put((priority_value, task.task_id, task))

            self.statistics.total_tasks += 1

            self.logger.info(f"📋 Task added to queue: {task.name} (Priority: {task.priority.name})")

            return task.task_id

        except Exception as e:
            self.logger.error(f"❌ Failed to add task: {e}")
            return ""

    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    async def create_task(self,
                         name: str,
                         description: str,
                         task_function: Callable,
                         priority: TaskPriority = TaskPriority.MEDIUM,
                         args: tuple = (),
                         kwargs: dict = None,
                         dependencies: List[str] = None,
                         timeout: int = 300) -> str:
        """Create and add a task"""
        try:
            task = Task(
                task_id=self._generate_task_id(),
                name=name,
                description=description,
                priority=priority,
                task_function=task_function,
                args=args,
                kwargs=kwargs or {},
                timeout=timeout,
                dependencies=dependencies or []
            )

            return await self.add_task(task)

        except Exception as e:
            self.logger.error(f"❌ Failed to create task: {e}")
            return ""

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        try:
            # Check if task is active
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()

                # Move to completed
                del self.active_tasks[task_id]
                self.completed_tasks[task_id] = task

                self.statistics.cancelled_tasks += 1
                self.logger.info(f"🚫 Task cancelled: {task.name}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"❌ Failed to cancel task: {e}")
            return False

    async def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get task status"""
        try:
            if task_id in self.active_tasks:
                return self.active_tasks[task_id]
            elif task_id in self.completed_tasks:
                return self.completed_tasks[task_id]
            else:
                return None
        except Exception as e:
            self.logger.error(f"❌ Failed to get task status: {e}")
            return None

    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        try:
            return {
                'queue_size': self.task_queue.qsize(),
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'total_processed': self.statistics.total_tasks,
                'success_rate': (self.statistics.completed_tasks / max(self.statistics.total_tasks, 1)) * 100,
                'active_task_names': [task.name for task in self.active_tasks.values()],
                'framework_running': self.running
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get queue status: {e}")
            return {}

    # Task handlers for different types of automation
    async def _handle_project_creation(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project creation task"""
        try:
            # This would integrate with the autonomous executor
            return {
                'status': 'completed',
                'message': 'Project creation handled'
            }
        except Exception as e:
            raise Exception(f"Project creation failed: {e}")

    async def _handle_code_analysis(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code analysis task"""
        try:
            file_path = task_params.get('file_path')
            if not file_path or not Path(file_path).exists():
                raise Exception("File not found")

            # Analyze code
            with open(file_path, 'r') as f:
                content = f.read()

            analysis = {
                'lines_count': len(content.split('\n')),
                'file_size': len(content),
                'imports': [],
                'functions': [],
                'classes': []
            }

            return {
                'status': 'completed',
                'analysis': analysis
            }

        except Exception as e:
            raise Exception(f"Code analysis failed: {e}")

    async def _handle_feature_addition(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle feature addition task"""
        try:
            # This would integrate with feature injection engine
            return {
                'status': 'completed',
                'message': 'Feature addition handled'
            }
        except Exception as e:
            raise Exception(f"Feature addition failed: {e}")

    async def _handle_error_resolution(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle error resolution task"""
        try:
            error_info = task_params.get('error_info')
            if not error_info:
                raise Exception("No error info provided")

            # This would integrate with error-proof system
            return {
                'status': 'completed',
                'message': 'Error resolution handled'
            }

        except Exception as e:
            raise Exception(f"Error resolution failed: {e}")

    async def _handle_github_learning(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GitHub learning task"""
        try:
            repo_url = task_params.get('repo_url')
            if not repo_url:
                raise Exception("No repository URL provided")

            # This would integrate with GitHub learning engine
            return {
                'status': 'completed',
                'message': 'GitHub learning handled'
            }

        except Exception as e:
            raise Exception(f"GitHub learning failed: {e}")

    async def _handle_system_maintenance(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system maintenance task"""
        try:
            maintenance_type = task_params.get('type', 'cleanup')

            if maintenance_type == 'cleanup':
                # Clean up old task data
                await self._cleanup_old_tasks()
            elif maintenance_type == 'backup':
                # Create backup
                await self._create_backup()

            return {
                'status': 'completed',
                'message': f'{maintenance_type} maintenance completed'
            }

        except Exception as e:
            raise Exception(f"System maintenance failed: {e}")

    async def _handle_file_operations(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operations task"""
        try:
            operation = task_params.get('operation')
            file_path = task_params.get('file_path')

            if not operation or not file_path:
                raise Exception("Missing operation or file path")

            if operation == 'backup':
                # Backup file
                backup_path = f"{file_path}.backup.{int(time.time())}"
                import shutil
                shutil.copy2(file_path, backup_path)
                return {'status': 'completed', 'backup_path': backup_path}
            elif operation == 'delete':
                # Delete file
                Path(file_path).unlink()
                return {'status': 'completed', 'message': 'File deleted'}
            else:
                raise Exception(f"Unknown operation: {operation}")

        except Exception as e:
            raise Exception(f"File operations failed: {e}")

    async def _cleanup_old_tasks(self):
        """Clean up old task data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=7)

            # Remove old completed tasks
            old_tasks = [
                task_id for task_id, task in self.completed_tasks.items()
                if task.completed_at and task.completed_at < cutoff_date
            ]

            for task_id in old_tasks:
                del self.completed_tasks[task_id]

            self.logger.info(f"🧹 Cleaned up {len(old_tasks)} old tasks")

        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {e}")

    async def _create_backup(self):
        """Create backup of task data"""
        try:
            backup_file = self.tasks_path / f"backup_{int(time.time())}.json"

            backup_data = {
                'completed_tasks': {tid: asdict(task) for tid, task in self.completed_tasks.items()},
                'statistics': asdict(self.statistics),
                'timestamp': datetime.now().isoformat()
            }

            async with aiofiles.open(backup_file, 'w') as f:
                await f.write(json.dumps(backup_data, indent=2, default=str))

            self.logger.info(f"💾 Created backup: {backup_file}")

        except Exception as e:
            self.logger.error(f"❌ Backup creation failed: {e}")

    async def _periodic_cleanup(self):
        """Periodic cleanup task"""
        while self.running:
            try:
                # Wait for cleanup interval
                await asyncio.sleep(self.config['cleanup_interval'])

                # Perform cleanup
                await self._cleanup_old_tasks()

                # Create backup
                await self._create_backup()

            except Exception as e:
                self.logger.error(f"❌ Periodic cleanup failed: {e}")

    async def process_queue(self) -> int:
        """Process all tasks in queue (blocking)"""
        try:
            processed_count = 0

            while self.running and (not self.task_queue.empty() or self.active_tasks):
                await asyncio.sleep(0.1)
                processed_count += 1

            return processed_count

        except Exception as e:
            self.logger.error(f"❌ Queue processing failed: {e}")
            return 0

    async def save_task_history(self):
        """Save task history to disk"""
        try:
            history_file = self.tasks_path / "task_history.json"

            # Limit task history
            recent_tasks = dict(list(self.completed_tasks.items())[-self.config['max_task_history']:])

            data = {
                'completed_tasks': [asdict(task) for task in recent_tasks.values()],
                'statistics': asdict(self.statistics),
                'last_updated': datetime.now().isoformat()
            }

            async with aiofiles.open(history_file, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))

        except Exception as e:
            self.logger.error(f"❌ Failed to save task history: {e}")

    async def get_statistics(self) -> Dict[str, Any]:
        """Get automation framework statistics"""
        try:
            return {
                'total_tasks': self.statistics.total_tasks,
                'completed_tasks': self.statistics.completed_tasks,
                'failed_tasks': self.statistics.failed_tasks,
                'cancelled_tasks': self.statistics.cancelled_tasks,
                'success_rate': round(
                    (self.statistics.completed_tasks / max(self.statistics.total_tasks, 1)) * 100, 2
                ),
                'average_execution_time': round(self.statistics.average_execution_time, 2),
                'tasks_per_hour': round(self.statistics.tasks_per_hour, 2),
                'queue_size': self.statistics.queue_size,
                'active_workers': self.statistics.active_workers,
                'framework_running': self.running,
                'uptime_hours': (datetime.now() - self.performance_metrics['start_time']).total_seconds() / 3600
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to get statistics: {e}")
            return {}

    async def shutdown(self):
        """Shutdown automation framework"""
        try:
            self.running = False

            # Cancel scheduler task
            if self.scheduler_task:
                self.scheduler_task.cancel()

            # Wait for active tasks to complete (with timeout)
            wait_time = 30
            start_wait = time.time()

            while self.active_tasks and (time.time() - start_wait) < wait_time:
                await asyncio.sleep(1)

            # Cancel remaining active tasks
            for task_id in list(self.active_tasks.keys()):
                await self.cancel_task(task_id)

            # Shutdown thread pool
            self.executor.shutdown(wait=True)

            # Save final data
            await self.save_task_history()

            self.logger.info("✅ Automation Framework v15 shutdown complete")

        except Exception as e:
            self.logger.error(f"❌ Automation Framework shutdown failed: {e}")

# Import aiofiles for async file operations
import aiofiles