"""
GitHub Learning Engine v15 - Autonomous Improvement System
Continuously learns from GitHub repositories to improve capabilities
Autonomous pattern extraction, feature discovery, and safe integration
"""

import os
import json
import time
import asyncio
import logging
import hashlib
import re
import aiohttp
import aiofiles
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
import ast
import subprocess
from urllib.parse import urlparse

@dataclass
class Repository:
    """GitHub repository information"""
    url: str
    owner: str
    name: str
    description: str
    stars: int
    language: str
    updated_at: datetime
    cloned_path: Optional[str] = None
    analyzed: bool = False
    learning_score: float = 0.0

@dataclass
class CodePattern:
    """Discovered code pattern"""
    pattern_type: str  # function, class, algorithm, optimization
    pattern_code: str
    description: str
    usage_count: int
    repositories: List[str]
    quality_score: float
    tags: List[str]

@dataclass
class LearningInsight:
    """Learning insight from repository analysis"""
    insight_type: str  # optimization, new_feature, bug_fix, pattern
    description: str
    code_example: str
    benefit: str
    implementation_difficulty: str  # easy, medium, hard
    applicable_files: List[str]

@dataclass
class LearningSession:
    """Learning session results"""
    session_id: str
    repositories_analyzed: int
    patterns_discovered: int
    insights_generated: int
    improvements_applied: int
    session_duration: float
    timestamp: datetime

class GitHubLearningEngineV15:
    """
    Autonomous GitHub Learning Engine

    Features:
    - Repository analysis and pattern extraction
    - Automatic feature discovery and integration
    - Bug fix learning and application
    - Performance optimization discovery
    - Safe integration with existing codebase
    - Continuous autonomous learning
    - Quality assessment and filtering
    """

    def __init__(self, self_modifying_engine, logger: logging.Logger):
        self.self_modifying_engine = self_modifying_engine
        self.logger = logger

        # Paths
        self.base_path = Path(__file__).parent.parent
        self.learning_data_path = self.base_path / "data" / "github_learning"
        self.repositories_path = self.learning_data_path / "repositories"
        self.patterns_path = self.learning_data_path / "patterns"
        self.insights_path = self.learning_data_path / "insights"

        # Create directories
        for path in [self.learning_data_path, self.repositories_path, self.patterns_path, self.insights_path]:
            path.mkdir(parents=True, exist_ok=True)

        # GitHub API configuration
        self.github_api_base = "https://api.github.com"
        self.github_token = os.getenv('GITHUB_TOKEN')  # Optional for higher rate limits
        self.session = None

        # Learning configuration
        self.learning_enabled = True
        self.max_repositories_per_session = 5
        self.max_file_size_mb = 1  # Limit file size for analysis
        self.supported_languages = {'python', 'javascript', 'typescript', 'shell'}

        # Quality thresholds
        self.min_stars_for_learning = 10
        self.min_pattern_quality_score = 0.7
        self.max_insight_difficulty = 'medium'

        # Learning data
        self.known_patterns = []
        self.learning_history = []
        self.blacklisted_repos = set()
        self.preferred_repos = [
            'python-telegram-bot/python-telegram-bot',
            'psf/requests',
            'pallets/flask',
            'ansible/ansible',
            'home-assistant/core',
            'octocat/Hello-World',
            'torvalds/linux',
            'microsoft/vscode',
            'facebook/react',
            'tensorflow/tensorflow'
        ]

        # Analysis metrics
        self.metrics = {
            'total_repositories_analyzed': 0,
            'total_patterns_discovered': 0,
            'total_insights_generated': 0,
            'total_improvements_applied': 0,
            'learning_sessions': 0,
            'last_learning_session': None
        }

    async def initialize(self):
        """Initialize GitHub learning engine"""
        try:
            # Create HTTP session
            headers = {'User-Agent': 'JARVIS-v15-Learning-Engine/1.0'}
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'

            self.session = aiohttp.ClientSession(headers=headers)

            # Load existing learning data
            await self._load_learning_data()

            # Load known patterns
            await self._load_known_patterns()

            self.logger.info("✅ GitHub Learning Engine v15 initialized")

        except Exception as e:
            self.logger.error(f"❌ GitHub Learning Engine initialization failed: {e}")
            raise

    async def _load_learning_data(self):
        """Load existing learning data"""
        try:
            # Load learning history
            history_file = self.learning_data_path / "learning_history.json"
            if history_file.exists():
                async with aiofiles.open(history_file, 'r') as f:
                    data = json.loads(await f.read())
                    self.learning_history = [LearningSession(**session) for session in data.get('sessions', [])]
                    self.metrics = data.get('metrics', self.metrics)

            # Load blacklisted repos
            blacklist_file = self.learning_data_path / "blacklisted_repos.txt"
            if blacklist_file.exists():
                async with aiofiles.open(blacklist_file, 'r') as f:
                    self.blacklisted_repos = set((await f.read()).strip().split('\n'))

            self.logger.info(f"📚 Loaded {len(self.learning_history)} learning sessions")

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load learning data: {e}")

    async def _load_known_patterns(self):
        """Load known code patterns"""
        try:
            patterns_file = self.patterns_path / "known_patterns.json"
            if patterns_file.exists():
                async with aiofiles.open(patterns_file, 'r') as f:
                    data = json.loads(await f.read())
                    self.known_patterns = [CodePattern(**pattern) for pattern in data.get('patterns', [])]

            self.logger.info(f"🔍 Loaded {len(self.known_patterns)} known patterns")

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load known patterns: {e}")

    async def continuous_learning(self):
        """Continuous background learning process"""
        while True:
            try:
                if self.learning_enabled:
                    await self.autonomous_learning_session()

                # Wait 1 hour between sessions
                await asyncio.sleep(3600)

            except Exception as e:
                self.logger.error(f"❌ Continuous learning error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def autonomous_learning_session(self) -> LearningSession:
        """Execute autonomous learning session"""
        session_id = hashlib.md5(f"session_{time.time()}".encode()).hexdigest()[:8]
        start_time = time.time()

        self.logger.info(f"🎓 Starting autonomous learning session {session_id}")

        try:
            # Step 1: Select repositories to analyze
            repositories = await self._select_repositories_for_learning()

            # Step 2: Analyze repositories
            patterns = []
            insights = []

            for repo in repositories:
                try:
                    repo_patterns, repo_insights = await self._analyze_repository(repo)
                    patterns.extend(repo_patterns)
                    insights.extend(repo_insights)

                    self.metrics['total_repositories_analyzed'] += 1

                except Exception as e:
                    self.logger.error(f"❌ Failed to analyze repository {repo.url}: {e}")

            # Step 3: Process and filter patterns
            quality_patterns = await self._filter_quality_patterns(patterns)

            # Step 4: Generate actionable insights
            actionable_insights = await self._generate_actionable_insights(insights, quality_patterns)

            # Step 5: Apply improvements
            improvements_applied = await self._apply_learning_improvements(actionable_insights)

            # Step 6: Update learning data
            await self._update_learning_data(quality_patterns, actionable_insights)

            # Create session result
            session = LearningSession(
                session_id=session_id,
                repositories_analyzed=len(repositories),
                patterns_discovered=len(quality_patterns),
                insights_generated=len(actionable_insights),
                improvements_applied=improvements_applied,
                session_duration=time.time() - start_time,
                timestamp=datetime.now()
            )

            # Save session
            self.learning_history.append(session)
            self.metrics['learning_sessions'] += 1
            self.metrics['total_patterns_discovered'] += len(quality_patterns)
            self.metrics['total_insights_generated'] += len(actionable_insights)
            self.metrics['total_improvements_applied'] += improvements_applied
            self.metrics['last_learning_session'] = session.timestamp.isoformat()

            await self._save_learning_data()

            self.logger.info(f"✅ Learning session {session_id} completed: "
                           f"{len(repositories)} repos, {len(quality_patterns)} patterns, "
                           f"{improvements_applied} improvements")

            return session

        except Exception as e:
            self.logger.error(f"❌ Learning session {session_id} failed: {e}")
            raise

    async def _select_repositories_for_learning(self) -> List[Repository]:
        """Select repositories for learning based on criteria"""
        repositories = []

        try:
            # Search for relevant repositories
            search_queries = [
                'python automation',
                'ai assistant python',
                'termux tools',
                'voice recognition python',
                'api integration python',
                'self-modifying code',
                'automation framework'
            ]

            for query in search_queries:
                try:
                    # Search GitHub repositories
                    search_url = f"{self.github_api_base}/search/repositories"
                    params = {
                        'q': f'{query} stars:>{self.min_stars_for_learning}',
                        'sort': 'stars',
                        'per_page': 10
                    }

                    async with self.session.get(search_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            items = data.get('items', [])

                            for item in items:
                                repo = Repository(
                                    url=item['html_url'],
                                    owner=item['owner']['login'],
                                    name=item['name'],
                                    description=item.get('description', ''),
                                    stars=item['stargazers_count'],
                                    language=item.get('language', '').lower(),
                                    updated_at=datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
                                )

                                # Skip if already analyzed or blacklisted
                                repo_identifier = f"{repo.owner}/{repo.name}"
                                if (repo_identifier not in self.blacklisted_repos and
                                    repo.language in self.supported_languages and
                                    len(repositories) < self.max_repositories_per_session):

                                    repositories.append(repo)

                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to search for '{query}': {e}")

            # If no repositories found, use preferred ones
            if not repositories:
                for repo_url in self.preferred_repos[:3]:
                    try:
                        repo_data = await self._get_repository_info(repo_url)
                        if repo_data:
                            repositories.append(repo_data)
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to get repo info for {repo_url}: {e}")

            return repositories

        except Exception as e:
            self.logger.error(f"❌ Repository selection failed: {e}")
            return []

    async def _get_repository_info(self, repo_identifier: str) -> Optional[Repository]:
        """Get repository information from GitHub API"""
        try:
            url = f"{self.github_api_base}/repos/{repo_identifier}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    item = await response.json()
                    return Repository(
                        url=item['html_url'],
                        owner=item['owner']['login'],
                        name=item['name'],
                        description=item.get('description', ''),
                        stars=item['stargazers_count'],
                        language=item.get('language', '').lower(),
                        updated_at=datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
                    )
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get repository info for {repo_identifier}: {e}")

        return None

    async def _analyze_repository(self, repository: Repository) -> Tuple[List[CodePattern], List[LearningInsight]]:
        """Analyze repository for patterns and insights"""
        patterns = []
        insights = []

        try:
            self.logger.info(f"🔍 Analyzing repository: {repository.owner}/{repository.name}")

            # Clone repository
            repo_path = await self._clone_repository(repository)

            if not repo_path:
                return patterns, insights

            # Analyze Python files
            py_files = list(Path(repo_path).rglob("*.py"))

            for py_file in py_files:
                try:
                    # Skip large files
                    if py_file.stat().st_size > self.max_file_size_mb * 1024 * 1024:
                        continue

                    file_patterns, file_insights = await self._analyze_python_file(py_file, repository)
                    patterns.extend(file_patterns)
                    insights.extend(file_insights)

                except Exception as e:
                    self.logger.debug(f"⚠️ Failed to analyze {py_file}: {e}")

            # Cleanup cloned repository
            await self._cleanup_repository(repo_path)

            repository.analyzed = True
            self.logger.info(f"✅ Analyzed {repository.owner}/{repository.name}: "
                           f"{len(patterns)} patterns, {len(insights)} insights")

        except Exception as e:
            self.logger.error(f"❌ Repository analysis failed: {e}")

        return patterns, insights

    async def _clone_repository(self, repository: Repository) -> Optional[str]:
        """Clone repository for analysis"""
        try:
            repo_name = f"{repository.owner}_{repository.name}"
            clone_path = self.repositories_path / repo_name

            # Remove existing directory
            if clone_path.exists():
                shutil.rmtree(clone_path)

            # Clone repository (shallow clone for speed)
            clone_url = repository.url.replace('https://github.com/', 'https://github.com/')
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', clone_url, str(clone_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                repository.cloned_path = str(clone_path)
                return str(clone_path)
            else:
                self.logger.warning(f"⚠️ Failed to clone repository: {result.stderr}")

        except Exception as e:
            self.logger.error(f"❌ Repository cloning failed: {e}")

        return None

    async def _cleanup_repository(self, repo_path: str):
        """Clean up cloned repository"""
        try:
            shutil.rmtree(repo_path)
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to cleanup repository: {e}")

    async def _analyze_python_file(self, file_path: Path, repository: Repository) -> Tuple[List[CodePattern], List[LearningInsight]]:
        """Analyze individual Python file"""
        patterns = []
        insights = []

        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()

            # Parse AST
            tree = ast.parse(content)

            # Analyze different node types
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_patterns, func_insights = await self._analyze_function(node, content, repository)
                    patterns.extend(func_patterns)
                    insights.extend(func_insights)

                elif isinstance(node, ast.ClassDef):
                    class_patterns, class_insights = await self._analyze_class(node, content, repository)
                    patterns.extend(class_patterns)
                    insights.extend(class_insights)

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_patterns, import_insights = await self._analyze_imports(node, content, repository)
                    patterns.extend(import_patterns)
                    insights.extend(import_insights)

            # Look for specific patterns in content
            content_patterns, content_insights = await self._analyze_content_patterns(content, repository)
            patterns.extend(content_patterns)
            insights.extend(content_insights)

        except Exception as e:
            self.logger.debug(f"⚠️ Failed to analyze file {file_path}: {e}")

        return patterns, insights

    async def _analyze_function(self, node: ast.FunctionDef, content: str, repository: Repository) -> Tuple[List[CodePattern], List[LearningInsight]]:
        """Analyze function definition"""
        patterns = []
        insights = []

        try:
            # Extract function source
            func_source = ast.get_source_segment(content, node)
            if not func_source:
                return patterns, insights

            # Check for async functions
            if isinstance(node, ast.AsyncFunctionDef):
                pattern = CodePattern(
                    pattern_type='async_function',
                    pattern_code=func_source,
                    description=f"Async function '{node.name}' with proper async/await usage",
                    usage_count=1,
                    repositories=[repository.url],
                    quality_score=0.8,
                    tags=['async', 'concurrency']
                )
                patterns.append(pattern)

            # Check for error handling patterns
            for child in ast.walk(node):
                if isinstance(child, (ast.Try, ast.ExceptHandler)):
                    pattern = CodePattern(
                        pattern_type='error_handling',
                        pattern_code=func_source,
                        description=f"Function '{node.name}' with proper error handling",
                        usage_count=1,
                        repositories=[repository.url],
                        quality_score=0.9,
                        tags=['error_handling', 'robustness']
                    )
                    patterns.append(pattern)
                    break

            # Check for decorators
            if node.decorator_list:
                decorator_names = [self._get_decorator_name(dec) for dec in node.decorator_list]
                pattern = CodePattern(
                    pattern_type='decorator_pattern',
                    pattern_code=func_source,
                    description=f"Function '{node.name}' with decorators: {', '.join(decorator_names)}",
                    usage_count=1,
                    repositories=[repository.url],
                    quality_score=0.7,
                    tags=['decorators'] + decorator_names
                )
                patterns.append(pattern)

            # Generate insights
            if len(node.args.args) > 5:
                insights.append(LearningInsight(
                    insight_type='optimization',
                    description=f"Function '{node.name}' has many parameters - consider using dataclass or configuration object",
                    code_example=func_source,
                    benefit="Improved readability and maintainability",
                    implementation_difficulty='easy',
                    applicable_files=['any_function_file.py']
                ))

        except Exception as e:
            self.logger.debug(f"⚠️ Function analysis failed: {e}")

        return patterns, insights

    async def _analyze_class(self, node: ast.ClassDef, content: str, repository: Repository) -> Tuple[List[CodePattern], List[LearningInsight]]:
        """Analyze class definition"""
        patterns = []
        insights = []

        try:
            # Extract class source
            class_source = ast.get_source_segment(content, node)
            if not class_source:
                return patterns, insights

            # Check for dataclass patterns
            if any(self._is_dataclass_method(child) for child in node.body):
                pattern = CodePattern(
                    pattern_type='dataclass_pattern',
                    pattern_code=class_source,
                    description=f"Class '{node.name}' with dataclass-like methods",
                    usage_count=1,
                    repositories=[repository.url],
                    quality_score=0.8,
                    tags=['dataclass', 'structured_data']
                )
                patterns.append(pattern)

            # Check for inheritance patterns
            if node.bases:
                base_names = [self._get_name(base) for base in node.bases]
                pattern = CodePattern(
                    pattern_type='inheritance_pattern',
                    pattern_code=class_source,
                    description=f"Class '{node.name}' inheriting from: {', '.join(base_names)}",
                    usage_count=1,
                    repositories=[repository.url],
                    quality_score=0.7,
                    tags=['inheritance', 'oop']
                )
                patterns.append(pattern)

        except Exception as e:
            self.logger.debug(f"⚠️ Class analysis failed: {e}")

        return patterns, insights

    async def _analyze_imports(self, node, content: str, repository: Repository) -> Tuple[List[CodePattern], List[LearningInsight]]:
        """Analyze import statements"""
        patterns = []
        insights = []

        try:
            if isinstance(node, ast.ImportFrom):
                module_name = node.module or ''

                # Check for interesting imports
                interesting_modules = {
                    'asyncio': 'async_programming',
                    'aiohttp': 'async_http',
                    'dataclasses': 'modern_python',
                    'pathlib': 'modern_path_handling',
                    'typing': 'type_hints',
                    'logging': 'logging_patterns'
                }

                if module_name in interesting_modules:
                    pattern = CodePattern(
                        pattern_type='import_pattern',
                        pattern_code=ast.unparse(node),
                        description=f"Import of '{module_name}' - {interesting_modules[module_name]}",
                        usage_count=1,
                        repositories=[repository.url],
                        quality_score=0.6,
                        tags=[interesting_modules[module_name], 'imports']
                    )
                    patterns.append(pattern)

        except Exception as e:
            self.logger.debug(f"⚠️ Import analysis failed: {e}")

        return patterns, insights

    async def _analyze_content_patterns(self, content: str, repository: Repository) -> Tuple[List[CodePattern], List[LearningInsight]]:
        """Analyze content for specific patterns"""
        patterns = []
        insights = []

        try:
            # Check for async/await patterns
            if 'async def' in content and 'await' in content:
                pattern = CodePattern(
                    pattern_type='async_await_pattern',
                    pattern_code='# Async/await usage detected',
                    description="Consistent use of async/await patterns",
                    usage_count=content.count('async def'),
                    repositories=[repository.url],
                    quality_score=0.8,
                    tags=['async', 'await', 'concurrency']
                )
                patterns.append(pattern)

            # Check for logging patterns
            if 'logging.' in content:
                pattern = CodePattern(
                    pattern_type='logging_pattern',
                    pattern_code='# Logging usage detected',
                    description="Proper logging implementation",
                    usage_count=content.count('logging.'),
                    repositories=[repository.url],
                    quality_score=0.7,
                    tags=['logging', 'debugging']
                )
                patterns.append(pattern)

            # Check for type hints
            if '-> ' in content and ':' in content:
                pattern = CodePattern(
                    pattern_type='type_hints',
                    pattern_code='# Type hints detected',
                    description="Type hints for better code documentation",
                    usage_count=content.count('-> '),
                    repositories=[repository.url],
                    quality_score=0.8,
                    tags=['type_hints', 'documentation']
                )
                patterns.append(pattern)

            # Check for docstrings
            if '"""' in content:
                pattern = CodePattern(
                    pattern_type='docstrings',
                    pattern_code='# Docstrings detected',
                    description="Proper docstring documentation",
                    usage_count=content.count('"""'),
                    repositories=[repository.url],
                    quality_score=0.9,
                    tags=['documentation', 'docstrings']
                )
                patterns.append(pattern)

        except Exception as e:
            self.logger.debug(f"⚠️ Content pattern analysis failed: {e}")

        return patterns, insights

    def _get_decorator_name(self, decorator) -> str:
        """Get decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        return 'unknown'

    def _is_dataclass_method(self, node) -> bool:
        """Check if method is typical of dataclass"""
        if isinstance(node, ast.FunctionDef):
            return node.name in ['__init__', '__post_init__', '__repr__', '__eq__']
        return False

    def _get_name(self, node) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return 'unknown'

    async def _filter_quality_patterns(self, patterns: List[CodePattern]) -> List[CodePattern]:
        """Filter patterns based on quality thresholds"""
        quality_patterns = []

        for pattern in patterns:
            if pattern.quality_score >= self.min_pattern_quality_score:
                # Check if pattern is already known
                is_duplicate = False
                for known in self.known_patterns:
                    if (pattern.pattern_type == known.pattern_type and
                        hash(pattern.pattern_code) == hash(known.pattern_code)):
                        is_duplicate = True
                        break

                if not is_duplicate:
                    quality_patterns.append(pattern)

        return quality_patterns

    async def _generate_actionable_insights(self, insights: List[LearningInsight], patterns: List[CodePattern]) -> List[LearningInsight]:
        """Generate actionable insights from patterns and raw insights"""
        actionable_insights = []

        # Add insights from high-quality patterns
        for pattern in patterns:
            if pattern.quality_score >= 0.8:
                insight = LearningInsight(
                    insight_type='pattern_adoption',
                    description=f"Adopt {pattern.pattern_type} pattern for better code quality",
                    code_example=pattern.pattern_code,
                    benefit=f"Improves {', '.join(pattern.tags)}",
                    implementation_difficulty='easy',
                    applicable_files=['relevant_files.py']
                )
                actionable_insights.append(insight)

        # Filter insights by difficulty
        for insight in insights:
            if insight.implementation_difficulty in ['easy', 'medium']:
                actionable_insights.append(insight)

        return actionable_insights

    async def _apply_learning_improvements(self, insights: List[LearningInsight]) -> int:
        """Apply learning improvements using self-modifying engine"""
        improvements_applied = 0

        try:
            for insight in insights[:3]:  # Apply top 3 insights
                try:
                    # Generate modification based on insight
                    modification = await self._generate_modification_from_insight(insight)

                    if modification and self.self_modifying_engine:
                        result = await self.self_modifying_engine.modify_code_realtime(
                            modification['file_path'],
                            modification
                        )

                        if result.success:
                            improvements_applied += 1
                            self.logger.info(f"✅ Applied learning improvement: {insight.description}")

                except Exception as e:
                    self.logger.error(f"❌ Failed to apply insight {insight.description}: {e}")

        except Exception as e:
            self.logger.error(f"❌ Learning improvements application failed: {e}")

        return improvements_applied

    async def _generate_modification_from_insight(self, insight: LearningInsight) -> Optional[Dict[str, Any]]:
        """Generate modification from learning insight"""
        try:
            # Find appropriate file to modify
            target_file = await self._find_target_file_for_insight(insight)

            if not target_file:
                return None

            # Generate modification based on insight type
            if insight.insight_type == 'pattern_adoption':
                return {
                    'file_path': target_file,
                    'type': 'add',
                    'new_code': f"\n# {insight.description}\n{insight.code_example}\n",
                    'description': f"Apply learning insight: {insight.description}"
                }
            elif insight.insight_type == 'optimization':
                return {
                    'file_path': target_file,
                    'type': 'replace',
                    'old_code': await self._find_code_to_optimize(target_file, insight),
                    'new_code': insight.code_example,
                    'description': f"Apply optimization: {insight.description}"
                }

        except Exception as e:
            self.logger.error(f"❌ Failed to generate modification from insight: {e}")

        return None

    async def _find_target_file_for_insight(self, insight: LearningInsight) -> Optional[str]:
        """Find appropriate target file for applying insight"""
        try:
            # Look for relevant files in the codebase
            for py_file in self.base_path.rglob("*.py"):
                if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'temp']):
                    continue

                # Simple heuristic: return first Python file that's not the main file
                if py_file.name != 'jarvis.py':
                    return str(py_file)

            return str(self.base_path / "jarvis.py")

        except Exception as e:
            self.logger.error(f"❌ Failed to find target file: {e}")
            return None

    async def _find_code_to_optimize(self, file_path: str, insight: LearningInsight) -> str:
        """Find code to optimize in target file"""
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()

            # Simple placeholder - in real implementation, would be more sophisticated
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'def ' in line and 'optimization' in insight.description.lower():
                    # Find the function to optimize
                    func_lines = [line]
                    j = i + 1
                    indent_level = len(line) - len(line.lstrip())

                    while j < len(lines):
                        current_line = lines[j]
                        if current_line.strip() == '':
                            j += 1
                            continue
                        if len(current_line) - len(current_line.lstrip()) <= indent_level and current_line.strip():
                            break
                        func_lines.append(current_line)
                        j += 1

                    return '\n'.join(func_lines)

            return "# Code to optimize"

        except Exception as e:
            self.logger.error(f"❌ Failed to find code to optimize: {e}")
            return "# Code to optimize"

    async def _update_learning_data(self, patterns: List[CodePattern], insights: List[LearningInsight]):
        """Update learning data with new patterns and insights"""
        try:
            # Add new patterns to known patterns
            self.known_patterns.extend(patterns)

            # Save patterns
            patterns_file = self.patterns_path / "known_patterns.json"
            patterns_data = {
                'patterns': [asdict(pattern) for pattern in self.known_patterns],
                'last_updated': datetime.now().isoformat()
            }

            async with aiofiles.open(patterns_file, 'w') as f:
                await f.write(json.dumps(patterns_data, indent=2, default=str))

            # Save insights
            insights_file = self.insights_path / f"insights_{int(time.time())}.json"
            insights_data = {
                'insights': [asdict(insight) for insight in insights],
                'timestamp': datetime.now().isoformat()
            }

            async with aiofiles.open(insights_file, 'w') as f:
                await f.write(json.dumps(insights_data, indent=2))

        except Exception as e:
            self.logger.error(f"❌ Failed to update learning data: {e}")

    async def _save_learning_data(self):
        """Save learning history and metrics"""
        try:
            history_file = self.learning_data_path / "learning_history.json"
            history_data = {
                'sessions': [asdict(session) for session in self.learning_history[-50:]],  # Keep last 50
                'metrics': self.metrics,
                'last_updated': datetime.now().isoformat()
            }

            async with aiofiles.open(history_file, 'w') as f:
                await f.write(json.dumps(history_data, indent=2, default=str))

        except Exception as e:
            self.logger.error(f"❌ Failed to save learning data: {e}")

    async def learn_from_repository(self, repo_url: str) -> str:
        """Learn from a specific repository"""
        try:
            self.logger.info(f"🎓 Learning from repository: {repo_url}")

            # Extract owner and name from URL
            parsed = urlparse(repo_url)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2:
                repo_identifier = f"{path_parts[0]}/{path_parts[1]}"
            else:
                return "❌ Invalid repository URL"

            # Get repository info
            repo = await self._get_repository_info(repo_identifier)
            if not repo:
                return f"❌ Could not access repository: {repo_identifier}"

            # Analyze repository
            patterns, insights = await self._analyze_repository(repo)

            # Process and apply improvements
            quality_patterns = await self._filter_quality_patterns(patterns)
            actionable_insights = await self._generate_actionable_insights(insights, quality_patterns)
            improvements_applied = await self._apply_learning_improvements(actionable_insights)

            # Update learning data
            await self._update_learning_data(quality_patterns, actionable_insights)

            result = (f"📚 Learning completed from {repo_identifier}\n"
                     f"🔍 Patterns discovered: {len(quality_patterns)}\n"
                     f"💡 Insights generated: {len(actionable_insights)}\n"
                     f"✅ Improvements applied: {improvements_applied}")

            self.logger.info(result)
            return result

        except Exception as e:
            error_msg = f"❌ Learning from repository failed: {e}"
            self.logger.error(error_msg)
            return error_msg

    async def get_learning_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        return {
            'total_repositories_analyzed': self.metrics['total_repositories_analyzed'],
            'total_patterns_discovered': self.metrics['total_patterns_discovered'],
            'total_insights_generated': self.metrics['total_insights_generated'],
            'total_improvements_applied': self.metrics['total_improvements_applied'],
            'learning_sessions': self.metrics['learning_sessions'],
            'known_patterns_count': len(self.known_patterns),
            'blacklisted_repositories': len(self.blacklisted_repos),
            'last_learning_session': self.metrics['last_learning_session'],
            'learning_enabled': self.learning_enabled
        }

    async def shutdown(self):
        """Shutdown GitHub learning engine"""
        try:
            if self.session:
                await self.session.close()

            # Save final learning data
            await self._save_learning_data()

            self.logger.info("✅ GitHub Learning Engine v15 shutdown complete")

        except Exception as e:
            self.logger.error(f"❌ GitHub Learning Engine shutdown failed: {e}")