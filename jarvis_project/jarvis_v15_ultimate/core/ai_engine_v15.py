"""
AI Engine v15 - Enhanced Intelligence Processing
Advanced OpenRouter integration with multi-model fallback and intelligent caching
Optimized for Termux/Android with minimal resource usage
"""

import os
import json
import time
import asyncio
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from dataclasses import dataclass, asdict
import aiohttp
import aiofiles
from pathlib import Path

@dataclass
class AIModel:
    """AI Model configuration"""
    name: str
    provider: str
    max_tokens: int
    cost_per_token: float
    speed: str  # fast, medium, slow
    capabilities: List[str]
    available: bool = True

@dataclass
class AIRequest:
    """AI request structure"""
    prompt: str
    context: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    stream: bool = False
    cache_key: Optional[str] = None

@dataclass
class AIResponse:
    """AI response structure"""
    content: str
    model_used: str
    tokens_used: int
    cost: float
    response_time: float
    cached: bool = False
    error: Optional[str] = None

class AIEngineV15:
    """
    Enhanced AI Engine with OpenRouter Integration

    Features:
    - Multi-model intelligent fallback
    - Context caching and optimization
    - Real-time response streaming
    - Built-in safety validation
    - Cost optimization
    - Rate limiting and retry logic
    - Mobile-optimized for Termux
    """

    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.base_path = Path(__file__).parent.parent

        # API Configuration
        self.api_key = self._get_api_key()
        self.base_url = "https://openrouter.ai/api/v1"

        # Model configuration
        self.models = self._initialize_models()
        self.primary_model = "anthropic/claude-3-haiku"
        self.fallback_models = [
            "meta-llama/llama-3.1-8b-instruct",
            "microsoft/wizardlm-2-8x22b",
            "google/gemma-2-9b-it"
        ]

        # Performance tracking
        self.request_count = 0
        self.total_cost = 0.0
        self.total_tokens = 0
        self.error_count = 0

        # Caching system
        self.cache_dir = self.base_path / "data" / "ai_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(hours=24)

        # Rate limiting
        self.rate_limit_window = 60  # seconds
        self.max_requests_per_window = 60
        self.request_times = []

        # Session management
        self.session = None
        self.context_cache = {}
        self.max_context_size = 50  # messages

        # Safety validation
        self.safety_filters = [
            self._validate_content_safety,
            self._validate_request_format,
            self._check_resource_limits
        ]

    async def initialize(self):
        """Initialize AI engine"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"Authorization": f"Bearer {self.api_key}"}
            )

            # Test API connectivity
            await self._test_api_connection()

            # Load cached responses
            await self._load_cache_index()

            self.logger.info("✅ AI Engine v15 initialized successfully")

        except Exception as e:
            self.logger.error(f"❌ AI Engine initialization failed: {e}")
            raise

    def _get_api_key(self) -> str:
        """Get OpenRouter API key from environment or config"""
        # Try environment variable first
        api_key = os.getenv('OPENROUTER_API_KEY')

        if not api_key:
            # Try config file
            config_file = self.base_path / "data" / "openrouter_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    api_key = config_data.get('api_key')

        if not api_key:
            raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable or configure in settings.")

        return api_key

    def _initialize_models(self) -> Dict[str, AIModel]:
        """Initialize available AI models"""
        return {
            "anthropic/claude-3-haiku": AIModel(
                name="Claude 3 Haiku",
                provider="Anthropic",
                max_tokens=4000,
                cost_per_token=0.00025,
                speed="fast",
                capabilities=["text", "analysis", "coding", "reasoning"]
            ),
            "meta-llama/llama-3.1-8b-instruct": AIModel(
                name="Llama 3.1 8B",
                provider="Meta",
                max_tokens=8000,
                cost_per_token=0.00018,
                speed="medium",
                capabilities=["text", "coding", "reasoning"]
            ),
            "microsoft/wizardlm-2-8x22b": AIModel(
                name="WizardLM 2 8x22B",
                provider="Microsoft",
                max_tokens=6000,
                cost_per_token=0.00065,
                speed="slow",
                capabilities=["text", "analysis", "coding", "complex_reasoning"]
            ),
            "google/gemma-2-9b-it": AIModel(
                name="Gemma 2 9B",
                provider="Google",
                max_tokens=8000,
                cost_per_token=0.00027,
                speed="medium",
                capabilities=["text", "coding", "reasoning"]
            )
        }

    async def _test_api_connection(self):
        """Test API connectivity with simple request"""
        try:
            test_request = AIRequest(
                prompt="Respond with 'OK' if you can read this.",
                max_tokens=10,
                model=self.primary_model
            )

            response = await self._make_api_request(test_request)

            if response.error:
                raise Exception(f"API test failed: {response.error}")

            self.logger.info("✅ OpenRouter API connection verified")

        except Exception as e:
            self.logger.error(f"❌ API connection test failed: {e}")
            raise

    async def _load_cache_index(self):
        """Load cache index for response caching"""
        cache_file = self.cache_dir / "cache_index.json"

        try:
            if cache_file.exists():
                async with aiofiles.open(cache_file, 'r') as f:
                    self.cache_index = json.loads(await f.read())
            else:
                self.cache_index = {}

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load cache index: {e}")
            self.cache_index = {}

    async def _save_cache_index(self):
        """Save cache index"""
        cache_file = self.cache_dir / "cache_index.json"

        try:
            async with aiofiles.open(cache_file, 'w') as f:
                await f.write(json.dumps(self.cache_index, indent=2))
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to save cache index: {e}")

    def _generate_cache_key(self, request: AIRequest) -> str:
        """Generate cache key for request"""
        cache_data = {
            'prompt': request.prompt,
            'context': request.context,
            'model': request.model or self.primary_model,
            'max_tokens': request.max_tokens,
            'temperature': request.temperature
        }

        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()

    async def _get_cached_response(self, cache_key: str) -> Optional[AIResponse]:
        """Get cached response if available and not expired"""
        try:
            if cache_key not in self.cache_index:
                return None

            cache_entry = self.cache_index[cache_key]
            cache_time = datetime.fromisoformat(cache_entry['timestamp'])

            # Check if cache is expired
            if datetime.now() - cache_time > self.cache_duration:
                del self.cache_index[cache_key]
                await self._save_cache_index()
                return None

            # Load cached response
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                async with aiofiles.open(cache_file, 'r') as f:
                    data = json.loads(await f.read())

                return AIResponse(
                    content=data['content'],
                    model_used=data['model_used'],
                    tokens_used=data['tokens_used'],
                    cost=data['cost'],
                    response_time=data['response_time'],
                    cached=True
                )

        except Exception as e:
            self.logger.warning(f"⚠️ Cache retrieval failed: {e}")

        return None

    async def _cache_response(self, cache_key: str, response: AIResponse):
        """Cache response for future use"""
        try:
            # Save response data
            cache_file = self.cache_dir / f"{cache_key}.json"
            data = {
                'content': response.content,
                'model_used': response.model_used,
                'tokens_used': response.tokens_used,
                'cost': response.cost,
                'response_time': response.response_time,
                'timestamp': datetime.now().isoformat()
            }

            async with aiofiles.open(cache_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))

            # Update cache index
            self.cache_index[cache_key] = {
                'timestamp': datetime.now().isoformat(),
                'tokens_used': response.tokens_used
            }

            await self._save_cache_index()

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to cache response: {e}")

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = time.time()

        # Remove old requests outside the window
        self.request_times = [req_time for req_time in self.request_times if now - req_time < self.rate_limit_window]

        # Check if we can make a request
        if len(self.request_times) >= self.max_requests_per_window:
            return False

        self.request_times.append(now)
        return True

    async def _validate_request(self, request: AIRequest) -> bool:
        """Validate request using safety filters"""
        for filter_func in self.safety_filters:
            if not await filter_func(request):
                return False
        return True

    async def _validate_content_safety(self, request: AIRequest) -> bool:
        """Validate content safety"""
        # Basic content safety checks
        prohibited_patterns = [
            'hack', 'exploit', 'malware', 'virus', 'illegal'
        ]

        prompt_lower = request.prompt.lower()
        for pattern in prohibited_patterns:
            if pattern in prompt_lower:
                self.logger.warning(f"⚠️ Prohibited content detected: {pattern}")
                return False

        return True

    async def _validate_request_format(self, request: AIRequest) -> bool:
        """Validate request format"""
        if not request.prompt or len(request.prompt.strip()) == 0:
            return False

        if len(request.prompt) > 10000:  # Reasonable limit
            self.logger.warning("⚠️ Prompt too long")
            return False

        return True

    async def _check_resource_limits(self, request: AIRequest) -> bool:
        """Check resource limits"""
        # Check memory usage (basic check for Termux)
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent

            if memory_percent > 80:  # If memory usage is high
                self.logger.warning("⚠️ High memory usage, limiting request size")
                if request.max_tokens and request.max_tokens > 2000:
                    request.max_tokens = 2000
        except ImportError:
            # psutil not available, skip check
            pass

        return True

    async def _make_api_request(self, request: AIRequest) -> AIResponse:
        """Make API request to OpenRouter"""
        start_time = time.time()

        # Determine which model to use
        model = request.model or self.primary_model
        if model not in self.models:
            model = self.primary_model

        # Prepare request payload
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens or self.models[model].max_tokens,
            "temperature": request.temperature or 0.7
        }

        # Add context if provided
        if request.context:
            payload["messages"].insert(0, {"role": "system", "content": request.context})

        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:

                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")

                data = await response.json()

                # Extract response
                content = data['choices'][0]['message']['content']
                tokens_used = data.get('usage', {}).get('total_tokens', 0)

                # Calculate cost
                cost = tokens_used * self.models[model].cost_per_token
                response_time = time.time() - start_time

                # Update statistics
                self.request_count += 1
                self.total_cost += cost
                self.total_tokens += tokens_used

                return AIResponse(
                    content=content,
                    model_used=model,
                    tokens_used=tokens_used,
                    cost=cost,
                    response_time=response_time,
                    cached=False
                )

        except Exception as e:
            self.error_count += 1
            self.logger.error(f"❌ API request failed: {e}")

            return AIResponse(
                content="",
                model_used=model,
                tokens_used=0,
                cost=0.0,
                response_time=time.time() - start_time,
                error=str(e)
            )

    async def _try_fallback_models(self, request: AIRequest) -> AIResponse:
        """Try fallback models if primary fails"""
        for model_name in self.fallback_models:
            if model_name not in self.models:
                continue

            self.logger.info(f"🔄 Trying fallback model: {model_name}")

            fallback_request = AIRequest(
                prompt=request.prompt,
                context=request.context,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                model=model_name,
                stream=request.stream
            )

            response = await self._make_api_request(fallback_request)

            if not response.error:
                self.logger.info(f"✅ Fallback model {model_name} succeeded")
                return response

        # All fallbacks failed
        return AIResponse(
            content="All models are currently unavailable. Please try again later.",
            model_used="none",
            tokens_used=0,
            cost=0.0,
            response_time=0.0,
            error="All models failed"
        )

    async def process_command(self, command: str, context: Optional[str] = None) -> str:
        """
        Process user command with AI intelligence

        Args:
            command: User command in natural language
            context: Optional context for the command

        Returns:
            AI response as string
        """
        try:
            # Check rate limits
            if not self._check_rate_limit():
                return "⚠️ Rate limit exceeded. Please wait a moment before trying again."

            # Create request
            request = AIRequest(
                prompt=self._enhance_command_prompt(command),
                context=context or self._get_system_context(),
                max_tokens=2000,
                temperature=0.7
            )

            # Validate request
            if not await self._validate_request(request):
                return "❌ Invalid request. Please check your input and try again."

            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_response = await self._get_cached_response(cache_key)

            if cached_response:
                self.logger.info(f"📋 Cache hit for command: {command[:50]}...")
                return cached_response.content

            # Make API request
            response = await self._make_api_request(request)

            # Try fallbacks if primary fails
            if response.error:
                self.logger.warning(f"⚠️ Primary model failed: {response.error}")
                response = await self._try_fallback_models(request)

            if response.error:
                return f"❌ AI processing failed: {response.error}"

            # Cache successful response
            await self._cache_response(cache_key, response)

            # Update context
            self._update_context(command, response.content)

            self.logger.info(f"✅ Command processed in {response.response_time:.2f}s using {response.model_used}")

            return response.content

        except Exception as e:
            self.logger.error(f"❌ Command processing failed: {e}")
            return f"❌ Processing failed: {str(e)}"

    def _enhance_command_prompt(self, command: str) -> str:
        """Enhance command prompt with JARVIS context"""
        enhanced_prompt = f"""You are JARVIS v15 Ultimate, an advanced AI assistant with real-time self-modification capabilities, 100% Termux compatibility, and autonomous learning.

Current capabilities:
- Instant feature addition and self-modification
- Voice interaction and calling via Termux-API
- GitHub learning and autonomous improvement
- Error-proof operation with automatic fixing
- Background automation and task processing
- Project creation and management

User command: {command}

Please respond as JARVIS v15 Ultimate, being helpful, capable, and concise. If the user requests a feature, explain that you can add it instantly using your self-modification capabilities."""

        return enhanced_prompt

    def _get_system_context(self) -> str:
        """Get current system context"""
        return f"""JARVIS v15 Ultimate System Context:
- Version: 15 Ultimate
- Platform: Termux/Android Optimized
- Status: All systems operational
- Capabilities: Self-modification, voice, calling, automation, GitHub learning
- Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    def _update_context(self, command: str, response: str):
        """Update conversation context"""
        context_key = f"conv_{int(time.time() // 300)}"  # Reset every 5 minutes

        if context_key not in self.context_cache:
            self.context_cache[context_key] = []

        self.context_cache[context_key].append({
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'response': response
        })

        # Keep only recent context
        if len(self.context_cache[context_key]) > self.max_context_size:
            self.context_cache[context_key] = self.context_cache[context_key][-self.max_context_size:]

    async def stream_response(self, command: str) -> AsyncGenerator[str, None]:
        """Stream AI response in real-time"""
        # For Termux optimization, we'll implement simple chunked responses
        # since full streaming might be resource intensive

        response = await self.process_command(command)

        # Split response into chunks for streaming effect
        words = response.split()
        current_chunk = ""

        for i, word in enumerate(words):
            current_chunk += word + " "

            # Send chunk every 5 words or at the end
            if (i + 1) % 5 == 0 or i == len(words) - 1:
                yield current_chunk.strip()
                await asyncio.sleep(0.1)  # Small delay for streaming effect
                current_chunk = ""

    async def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code and provide insights"""
        try:
            prompt = f"""Analyze this {language} code and provide:
1. Code quality assessment
2. Potential issues or bugs
3. Optimization suggestions
4. Security concerns
5. Best practices recommendations

Code to analyze:
```{language}
{code}
```"""

            response = await self.process_command(prompt)

            return {
                'analysis': response,
                'language': language,
                'code_length': len(code),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"❌ Code analysis failed: {e}")
            return {
                'analysis': f"Analysis failed: {str(e)}",
                'error': True
            }

    async def generate_code(self, description: str, language: str = "python") -> str:
        """Generate code based on description"""
        try:
            prompt = f"""Generate {language} code for the following description:

{description}

Requirements:
- Make the code error-free and functional
- Include proper error handling
- Add comments where necessary
- Follow best practices
- Ensure Termux compatibility if relevant

Generate only the code without explanations:"""

            response = await self.process_command(prompt)

            # Extract code block if present
            if "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end != -1:
                    return response[start:end].strip()

            return response

        except Exception as e:
            self.logger.error(f"❌ Code generation failed: {e}")
            return f"// Code generation failed: {str(e)}"

    async def get_statistics(self) -> Dict[str, Any]:
        """Get AI engine statistics"""
        return {
            'requests_processed': self.request_count,
            'total_cost_usd': round(self.total_cost, 4),
            'total_tokens_used': self.total_tokens,
            'error_count': self.error_count,
            'success_rate': round((self.request_count - self.error_count) / max(self.request_count, 1) * 100, 2),
            'average_response_time': round(self.total_cost / max(self.request_count, 1), 3),
            'cache_size': len(self.cache_index),
            'models_available': len(self.models),
            'primary_model': self.primary_model
        }

    async def clear_cache(self):
        """Clear response cache"""
        try:
            # Remove cache files
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file.name != "cache_index.json":
                    cache_file.unlink()

            # Clear cache index
            self.cache_index = {}
            await self._save_cache_index()

            self.logger.info("✅ AI cache cleared")

        except Exception as e:
            self.logger.error(f"❌ Failed to clear cache: {e}")

    async def shutdown(self):
        """Shutdown AI engine"""
        try:
            if self.session:
                await self.session.close()

            # Save final statistics
            stats = await self.get_statistics()
            stats_file = self.cache_dir / "ai_stats.json"

            async with aiofiles.open(stats_file, 'w') as f:
                await f.write(json.dumps(stats, indent=2))

            self.logger.info("✅ AI Engine v15 shutdown complete")

        except Exception as e:
            self.logger.error(f"❌ AI Engine shutdown failed: {e}")