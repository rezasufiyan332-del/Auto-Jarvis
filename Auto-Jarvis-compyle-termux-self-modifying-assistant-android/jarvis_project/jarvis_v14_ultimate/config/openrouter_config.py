#!/usr/bin/env python3
"""
JARVIS V14 Ultimate OpenRouter Configuration
==========================================

Configuration management for OpenRouter API integration

Author: JARVIS V14 Ultimate System
Version: 14.0.0
"""

import os
import json
from typing import Dict, Any, Optional

class OpenRouterConfig:
    """OpenRouter API configuration manager"""

    # Default configuration
    DEFAULT_CONFIG = {
        "api_key": "",
        "primary_model": "anthropic/claude-3-haiku",
        "fallback_models": [
            "meta-llama/llama-3.1-8b-instruct",
            "microsoft/wizardlm-2-8x22b",
            "google/gemma-2-9b-it"
        ],
        "max_tokens": 4000,
        "temperature": 0.7,
        "retry_attempts": 3,
        "timeout_seconds": 30,
        "rate_limit_requests_per_minute": 60,
        "cache_enabled": True,
        "cache_max_size": 1000,
        "cache_ttl_seconds": 3600
    }

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        # Try home directory first, then current directory
        home_dir = os.path.expanduser("~")
        possible_paths = [
            os.path.join(home_dir, ".jarvis", "openrouter_config.json"),
            os.path.join(os.getcwd(), "openrouter_config.json"),
            os.path.join(os.path.dirname(__file__), "openrouter_user_config.json")
        ]

        for path in possible_paths:
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                return path
            except:
                continue

        return os.path.join(os.getcwd(), "openrouter_config.json")

    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
        except Exception:
            pass  # Use defaults if loading fails

        # Load API key from environment if not in config
        if not self.config.get('api_key'):
            self.config['api_key'] = os.environ.get('OPENROUTER_API_KEY', '')

    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value

    def get_api_key(self) -> str:
        """Get API key"""
        return self.config.get('api_key', '')

    def set_api_key(self, api_key: str):
        """Set API key"""
        self.config['api_key'] = api_key
        self.save_config()

    def is_configured(self) -> bool:
        """Check if API is properly configured"""
        return bool(self.config.get('api_key'))

    def get_headers(self) -> Dict[str, str]:
        """Get API headers"""
        return {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/jarvis-ai",
            "X-Title": "JARVIS V14 Ultimate"
        }

    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []

        # Check API key
        if not self.config.get('api_key'):
            issues.append("API key is required")
        elif len(self.config['api_key']) < 10:
            issues.append("API key seems too short")

        # Check numeric values
        if self.config.get('max_tokens', 0) <= 0:
            issues.append("max_tokens must be positive")
        if not 0 <= self.config.get('temperature', 1) <= 2:
            issues.append("temperature must be between 0 and 2")
        if self.config.get('retry_attempts', 0) <= 0:
            issues.append("retry_attempts must be positive")
        if self.config.get('timeout_seconds', 0) <= 0:
            issues.append("timeout_seconds must be positive")
        if self.config.get('rate_limit_requests_per_minute', 0) <= 0:
            issues.append("rate_limit_requests_per_minute must be positive")

        # Check model lists
        if not self.config.get('primary_model'):
            issues.append("primary_model is required")
        if not self.config.get('fallback_models'):
            issues.append("fallback_models cannot be empty")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "configured": self.is_configured()
        }

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about configured models"""
        return {
            "primary_model": self.config.get('primary_model'),
            "fallback_models": self.config.get('fallback_models', []),
            "total_models": 1 + len(self.config.get('fallback_models', []))
        }

    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return self.config.copy()

    def from_dict(self, config_dict: Dict[str, Any]):
        """Load configuration from dictionary"""
        self.config.update(config_dict)
        self.save_config()

# Global configuration instance
_global_config = None

def get_config(config_file: Optional[str] = None) -> OpenRouterConfig:
    """Get global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = OpenRouterConfig(config_file)
    return _global_config

def setup_api_key(api_key: str, config_file: Optional[str] = None) -> bool:
    """Setup API key and save configuration"""
    config = get_config(config_file)
    config.set_api_key(api_key)
    return config.is_configured()

def is_configured(config_file: Optional[str] = None) -> bool:
    """Check if API is configured"""
    config = get_config(config_file)
    return config.is_configured()

# Quick setup functions
def quick_setup(api_key: str, model: str = None, config_file: Optional[str] = None) -> Dict[str, Any]:
    """Quick setup with minimal parameters"""
    config = get_config(config_file)

    # Set API key
    config.set_api_key(api_key)

    # Set model if provided
    if model:
        config.set('primary_model', model)

    # Save and validate
    config.save_config()
    validation = config.validate_config()

    return {
        "success": validation['valid'],
        "configured": config.is_configured(),
        "issues": validation['issues'],
        "model_info": config.get_model_info()
    }

# Environment setup
def setup_from_environment(config_file: Optional[str] = None) -> bool:
    """Setup from environment variables"""
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if api_key:
        return setup_api_key(api_key, config_file)
    return False

if __name__ == "__main__":
    # Configuration testing
    print("JARVIS V14 Ultimate OpenRouter Configuration")
    print("=" * 50)

    config = get_config()

    # Show current configuration status
    validation = config.validate_config()
    print(f"Configuration valid: {validation['valid']}")
    print(f"API configured: {validation['configured']}")

    if validation['issues']:
        print("Issues found:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    else:
        print("✅ Configuration is valid")

    # Show model information
    model_info = config.get_model_info()
    print(f"\nPrimary model: {model_info['primary_model']}")
    print(f"Fallback models: {len(model_info['fallback_models'])}")
    print(f"Total models: {model_info['total_models']}")

    # Show configuration file path
    print(f"\nConfiguration file: {config.config_file}")
    print(f"File exists: {os.path.exists(config.config_file)}")

    # Setup instructions if not configured
    if not validation['configured']:
        print("\n⚠️  OpenRouter API not configured")
        print("To setup:")
        print("1. Get API key from https://openrouter.ai/")
        print("2. Set environment variable: export OPENROUTER_API_KEY='your-key'")
        print("3. Or call setup_api_key('your-key')")
        print("4. Or edit the configuration file directly")