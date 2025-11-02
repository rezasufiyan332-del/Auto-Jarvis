"""
OpenRouter Configuration v15 - Enhanced AI API Management
Intelligent model selection, cost optimization, and performance monitoring
Multi-model fallback with automatic failover and caching
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import aiofiles

@dataclass
class AIModel:
    """AI model configuration"""
    model_id: str
    name: str
    provider: str
    max_tokens: int
    cost_per_input_token: float
    cost_per_output_token: float
    speed: str  # fast, medium, slow
    capabilities: List[str]
    context_window: int
    recommended_for: List[str]
    fallback_rank: int

@dataclass
class APIKeyConfig:
    """API key configuration"""
    primary_key: str
    fallback_keys: List[str]
    rate_limit_per_minute: int
    daily_limit: int
    cost_limit_per_day: float

@dataclass
class UsageStatistics:
    """Usage statistics tracking"""
    total_requests: int = 0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    model_usage: Dict[str, int] = None
    daily_usage: Dict[str, float] = None
    error_count: int = 0
    success_count: int = 0

    def __post_init__(self):
        if self.model_usage is None:
            self.model_usage = {}
        if self.daily_usage is None:
            self.daily_usage = {}

class OpenRouterConfigV15:
    """
    Enhanced OpenRouter Configuration Management

    Features:
    - Multi-model intelligent selection
    - Cost optimization and budget management
    - Automatic fallback and failover
    - Rate limiting and quota management
    - Performance monitoring and analytics
    - Context window optimization
    - Model capability matching
    """

    def __init__(self):
        self.logger = logging.getLogger("OpenRouterConfig")

        # Paths
        self.base_path = Path(__file__).parent.parent
        self.config_path = self.base_path / "data" / "config"
        self.api_keys_file = self.config_path / "api_keys.json"
        self.usage_file = self.config_path / "usage_stats.json"

        # Create directories
        self.config_path.mkdir(parents=True, exist_ok=True)

        # Initialize models
        self.models = self._initialize_models()

        # API configuration
        self.api_config = None
        self.current_api_key = None
        self.api_key_index = 0

        # Usage tracking
        self.usage_stats = UsageStatistics()

        # Rate limiting
        self.request_times = []
        self.daily_requests = 0
        self.last_reset_date = datetime.now().date()

        # Model selection strategy
        self.selection_strategy = "intelligent"  # intelligent, cost_optimized, speed_optimized

    def _initialize_models(self) -> Dict[str, AIModel]:
        """Initialize available AI models with optimized configurations for Termux"""
        return {
            "anthropic/claude-3-haiku": AIModel(
                model_id="anthropic/claude-3-haiku",
                name="Claude 3 Haiku",
                provider="Anthropic",
                max_tokens=4000,
                cost_per_input_token=0.00025,
                cost_per_output_token=0.00125,
                speed="fast",
                capabilities=["text", "analysis", "coding", "reasoning", "conversation"],
                context_window=200000,
                recommended_for=["general_conversation", "quick_responses", "code_analysis"],
                fallback_rank=1
            ),
            "meta-llama/llama-3.1-8b-instruct": AIModel(
                model_id="meta-llama/llama-3.1-8b-instruct",
                name="Llama 3.1 8B Instruct",
                provider="Meta",
                max_tokens=8000,
                cost_per_input_token=0.00018,
                cost_per_output_token=0.00018,
                speed="medium",
                capabilities=["text", "coding", "reasoning", "conversation"],
                context_window=128000,
                recommended_for=["cost_sensitive_tasks", "general_purpose"],
                fallback_rank=2
            ),
            "microsoft/wizardlm-2-8x22b": AIModel(
                model_id="microsoft/wizardlm-2-8x22b",
                name="WizardLM 2 8x22B",
                provider="Microsoft",
                max_tokens=6000,
                cost_per_input_token=0.00065,
                cost_per_output_token=0.00065,
                speed="slow",
                capabilities=["text", "analysis", "coding", "complex_reasoning"],
                context_window=65536,
                recommended_for=["complex_analysis", "detailed_explanations"],
                fallback_rank=3
            ),
            "google/gemma-2-9b-it": AIModel(
                model_id="google/gemma-2-9b-it",
                name="Gemma 2 9B IT",
                provider="Google",
                max_tokens=8000,
                cost_per_input_token=0.00027,
                cost_per_output_token=0.00027,
                speed="medium",
                capabilities=["text", "coding", "reasoning"],
                context_window=8192,
                recommended_for=["balanced_performance", "coding_tasks"],
                fallback_rank=4
            ),
            "anthropic/claude-3.5-sonnet": AIModel(
                model_id="anthropic/claude-3.5-sonnet",
                name="Claude 3.5 Sonnet",
                provider="Anthropic",
                max_tokens=4000,
                cost_per_input_token=0.000003,
                cost_per_output_token=0.000015,
                speed="medium",
                capabilities=["text", "analysis", "coding", "reasoning", "conversation"],
                context_window=200000,
                recommended_for=["high_quality_responses", "complex_tasks"],
                fallback_rank=0  # Premium option
            )
        }

    async def initialize(self):
        """Initialize configuration"""
        try:
            # Load API keys
            await self._load_api_keys()

            # Load usage statistics
            await self._load_usage_stats()

            # Set current API key
            await self._set_current_api_key()

            # Validate API key
            if await self._validate_api_key():
                self.logger.info("✅ OpenRouter configuration initialized successfully")
            else:
                self.logger.error("❌ OpenRouter API key validation failed")

        except Exception as e:
            self.logger.error(f"❌ OpenRouter configuration initialization failed: {e}")
            raise

    async def _load_api_keys(self):
        """Load API keys from environment or file"""
        try:
            # Try environment variable first
            primary_key = os.getenv('OPENROUTER_API_KEY')
            fallback_keys = []

            if not primary_key:
                # Try loading from file
                if self.api_keys_file.exists():
                    async with aiofiles.open(self.api_keys_file, 'r') as f:
                        data = json.loads(await f.read())
                        primary_key = data.get('primary_key')
                        fallback_keys = data.get('fallback_keys', [])

            if not primary_key:
                raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable or configure in api_keys.json")

            self.api_config = APIKeyConfig(
                primary_key=primary_key,
                fallback_keys=fallback_keys,
                rate_limit_per_minute=60,
                daily_limit=1000,
                cost_limit_per_day=5.0
            )

            self.logger.info(f"🔑 API keys loaded: primary + {len(fallback_keys)} fallbacks")

        except Exception as e:
            self.logger.error(f"❌ Failed to load API keys: {e}")
            raise

    async def _load_usage_stats(self):
        """Load usage statistics"""
        try:
            if self.usage_file.exists():
                async with aiofiles.open(self.usage_file, 'r') as f:
                    data = json.loads(await f.read())
                    self.usage_stats = UsageStatistics(**data)

            # Reset daily usage if new day
            today = datetime.now().date()
            if today != self.last_reset_date:
                self.usage_stats.daily_usage = {}
                self.daily_requests = 0
                self.last_reset_date = today

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load usage stats: {e}")
            self.usage_stats = UsageStatistics()

    async def _save_usage_stats(self):
        """Save usage statistics"""
        try:
            data = asdict(self.usage_stats)
            data['last_updated'] = datetime.now().isoformat()

            async with aiofiles.open(self.usage_file, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))

        except Exception as e:
            self.logger.error(f"❌ Failed to save usage stats: {e}")

    async def _set_current_api_key(self):
        """Set current API key"""
        try:
            if self.api_key_index == 0:
                self.current_api_key = self.api_config.primary_key
            elif self.api_key_index - 1 < len(self.api_config.fallback_keys):
                self.current_api_key = self.api_config.fallback_keys[self.api_key_index - 1]
            else:
                raise Exception("No available API keys")

            self.logger.info(f"🔑 Using API key index: {self.api_key_index}")

        except Exception as e:
            self.logger.error(f"❌ Failed to set API key: {e}")
            raise

    async def _validate_api_key(self) -> bool:
        """Validate current API key"""
        try:
            import aiohttp

            headers = {
                'Authorization': f'Bearer {self.current_api_key}',
                'Content-Type': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://openrouter.ai/api/v1/models',
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200

        except Exception as e:
            self.logger.error(f"❌ API key validation failed: {e}")
            return False

    def select_model(self, task_type: str, context_length: int = 0, priority: str = "balanced") -> str:
        """
        Select optimal model based on task requirements

        Args:
            task_type: Type of task (coding, analysis, conversation, etc.)
            context_length: Required context window size
            priority: Priority level (speed, cost, quality)

        Returns:
            Selected model ID
        """
        try:
            # Filter models by requirements
            suitable_models = []

            for model in self.models.values():
                # Check context window requirement
                if context_length > 0 and model.context_window < context_length:
                    continue

                # Check capability requirements
                if task_type and not any(cap in task_type.lower() for cap in model.capabilities):
                    # Still consider if model is general purpose
                    if not any(cap in model.capabilities for cap in ['conversation', 'reasoning']):
                        continue

                suitable_models.append(model)

            if not suitable_models:
                # Fallback to primary model
                return "anthropic/claude-3-haiku"

            # Sort by priority
            if priority == "speed":
                suitable_models.sort(key=lambda m: m.speed == "fast")
            elif priority == "cost":
                suitable_models.sort(key=lambda m: m.cost_per_input_token + m.cost_per_output_token)
            elif priority == "quality":
                suitable_models.sort(key=lambda m: m.fallback_rank)
            else:  # balanced
                # Intelligent selection based on task type
                if task_type:
                    for model in suitable_models:
                        if any(rec in task_type.lower() for rec in model.recommended_for):
                            return model.model_id

            # Return first suitable model
            return suitable_models[0].model_id

        except Exception as e:
            self.logger.error(f"❌ Model selection failed: {e}")
            return "anthropic/claude-3-haiku"  # Safe fallback

    def get_fallback_models(self, primary_model: str, max_fallbacks: int = 3) -> List[str]:
        """Get fallback models in order of preference"""
        try:
            if primary_model not in self.models:
                return ["anthropic/claude-3-haiku"]

            primary = self.models[primary_model]
            fallbacks = []

            # Get models with similar capabilities
            for model in self.models.values():
                if model.model_id == primary_model:
                    continue

                # Check for capability overlap
                capability_overlap = set(primary.capabilities) & set(model.capabilities)
                if capability_overlap:
                    fallbacks.append((model.model_id, len(capability_overlap), model.fallback_rank))

            # Sort by capability overlap and fallback rank
            fallbacks.sort(key=lambda x: (-x[1], x[2]))

            return [model[0] for model in fallbacks[:max_fallbacks]]

        except Exception as e:
            self.logger.error(f"❌ Fallback model selection failed: {e}")
            return ["anthropic/claude-3-haiku"]

    async def check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        try:
            now = time.time()

            # Clean old request times (outside 1-minute window)
            self.request_times = [req_time for req_time in self.request_times if now - req_time < 60]

            # Check rate limit
            if len(self.request_times) >= self.api_config.rate_limit_per_minute:
                return False

            # Check daily limit
            if self.daily_requests >= self.api_config.daily_limit:
                return False

            # Check cost limit
            today = datetime.now().date().isoformat()
            daily_cost = self.usage_stats.daily_usage.get(today, 0.0)
            if daily_cost >= self.api_config.cost_limit_per_day:
                return False

            # Add current request time
            self.request_times.append(now)
            self.daily_requests += 1

            return True

        except Exception as e:
            self.logger.error(f"❌ Rate limit check failed: {e}")
            return True  # Allow request on error

    async def record_usage(self, model: str, input_tokens: int, output_tokens: int, cost: float, success: bool = True):
        """Record API usage"""
        try:
            # Update total statistics
            self.usage_stats.total_requests += 1
            self.usage_stats.total_tokens_used += input_tokens + output_tokens
            self.usage_stats.total_cost += cost

            # Update model usage
            if model not in self.usage_stats.model_usage:
                self.usage_stats.model_usage[model] = 0
            self.usage_stats.model_usage[model] += 1

            # Update daily usage
            today = datetime.now().date().isoformat()
            if today not in self.usage_stats.daily_usage:
                self.usage_stats.daily_usage[today] = 0.0
            self.usage_stats.daily_usage[today] += cost

            # Update success/error counts
            if success:
                self.usage_stats.success_count += 1
            else:
                self.usage_stats.error_count += 1

            # Save periodically
            if self.usage_stats.total_requests % 10 == 0:
                await self._save_usage_stats()

        except Exception as e:
            self.logger.error(f"❌ Usage recording failed: {e}")

    async def switch_api_key(self) -> bool:
        """Switch to next available API key"""
        try:
            self.api_key_index += 1

            if self.api_key_index > len(self.api_config.fallback_keys):
                self.logger.error("❌ No more API keys available")
                return False

            await self._set_current_api_key()

            # Validate new key
            if await self._validate_api_key():
                self.logger.info(f"✅ Switched to fallback API key #{self.api_key_index}")
                return True
            else:
                self.logger.error(f"❌ Fallback API key #{self.api_key_index} is invalid")
                return await self.switch_api_key()  # Try next key

        except Exception as e:
            self.logger.error(f"❌ API key switch failed: {e}")
            return False

    async def reset_api_key(self):
        """Reset to primary API key"""
        try:
            self.api_key_index = 0
            await self._set_current_api_key()
            self.logger.info("🔄 Reset to primary API key")

        except Exception as e:
            self.logger.error(f"❌ API key reset failed: {e}")

    def get_current_api_key(self) -> str:
        """Get current API key"""
        return self.current_api_key

    def get_model_info(self, model_id: str) -> Optional[AIModel]:
        """Get model information"""
        return self.models.get(model_id)

    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return list(self.models.keys())

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary"""
        try:
            today = datetime.now().date().isoformat()
            daily_cost = self.usage_stats.daily_usage.get(today, 0.0)

            success_rate = 0.0
            if self.usage_stats.total_requests > 0:
                success_rate = (self.usage_stats.success_count / self.usage_stats.total_requests) * 100

            return {
                'total_requests': self.usage_stats.total_requests,
                'total_tokens_used': self.usage_stats.total_tokens_used,
                'total_cost': round(self.usage_stats.total_cost, 4),
                'today_cost': round(daily_cost, 4),
                'success_rate': round(success_rate, 2),
                'most_used_model': max(self.usage_stats.model_usage.items(), key=lambda x: x[1])[0] if self.usage_stats.model_usage else None,
                'api_key_index': self.api_key_index,
                'remaining_requests': self.api_config.daily_limit - self.daily_requests,
                'remaining_daily_budget': round(self.api_config.cost_limit_per_day - daily_cost, 4)
            }

        except Exception as e:
            self.logger.error(f"❌ Usage summary failed: {e}")
            return {}

    def get_cost_estimate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Get cost estimate for request"""
        try:
            model_info = self.models.get(model)
            if not model_info:
                return 0.0

            input_cost = input_tokens * model_info.cost_per_input_token
            output_cost = output_tokens * model_info.cost_per_output_token

            return input_cost + output_cost

        except Exception as e:
            self.logger.error(f"❌ Cost estimate failed: {e}")
            return 0.0

    def optimize_for_termux(self) -> Dict[str, Any]:
        """Get optimization settings for Termux environment"""
        try:
            return {
                'max_concurrent_requests': 2,  # Conservative for mobile
                'request_timeout': 30,  # Shorter timeout for mobile
                'cache_enabled': True,
                'preferred_models': [
                    "anthropic/claude-3-haiku",  # Fastest
                    "meta-llama/llama-3.1-8b-instruct",  # Good balance
                    "google/gemma-2-9b-it"  # Lightweight
                ],
                'context_optimization': True,
                'batch_requests': False,  # No batching on mobile
                'retry_attempts': 2,
                'retry_delay': 1.0
            }

        except Exception as e:
            self.logger.error(f"❌ Termux optimization failed: {e}")
            return {}

    async def save_config(self):
        """Save current configuration"""
        try:
            config_file = self.config_path / "openrouter_config.json"

            config_data = {
                'api_config': asdict(self.api_config) if self.api_config else None,
                'selection_strategy': self.selection_strategy,
                'usage_stats': asdict(self.usage_stats),
                'api_key_index': self.api_key_index,
                'last_updated': datetime.now().isoformat()
            }

            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(config_data, indent=2, default=str))

        except Exception as e:
            self.logger.error(f"❌ Config save failed: {e}")

    async def shutdown(self):
        """Shutdown configuration manager"""
        try:
            # Save final usage statistics
            await self._save_usage_stats()

            # Save configuration
            await self.save_config()

            self.logger.info("✅ OpenRouter configuration shutdown complete")

        except Exception as e:
            self.logger.error(f"❌ OpenRouter configuration shutdown failed: {e}")