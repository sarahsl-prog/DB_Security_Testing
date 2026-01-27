#!/usr/bin/env python3
"""
LLM Providers Package

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing

Factory module for instantiating LLM providers based on configuration.
"""

from loguru import logger

from .base import LLMProviderBase
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider, OPENAI_AVAILABLE
from .anthropic_provider import AnthropicProvider, ANTHROPIC_AVAILABLE


# Registry of available providers
PROVIDERS = {
    'ollama': OllamaProvider,
    'openai': OpenAIProvider,
    'anthropic': AnthropicProvider,
}


def get_llm_provider(config) -> LLMProviderBase:
    """
    Factory function to create the appropriate LLM provider based on configuration.

    Args:
        config: Configuration object with LLM_PROVIDER setting

    Returns:
        An instance of the appropriate LLM provider

    Raises:
        ValueError: If the specified provider is not supported
        ImportError: If required dependencies are not installed
    """
    provider_name = config.LLM_PROVIDER.lower()

    if provider_name not in PROVIDERS:
        available = ', '.join(PROVIDERS.keys())
        raise ValueError(
            f"Unknown LLM provider: '{provider_name}'. "
            f"Available providers: {available}"
        )

    # Check for required dependencies
    if provider_name == 'openai' and not OPENAI_AVAILABLE:
        raise ImportError(
            "OpenAI provider requires the 'openai' package. "
            "Install with: pip install openai"
        )

    if provider_name == 'anthropic' and not ANTHROPIC_AVAILABLE:
        raise ImportError(
            "Anthropic provider requires the 'anthropic' package. "
            "Install with: pip install anthropic"
        )

    logger.info(f"Initializing LLM provider: {provider_name}")

    provider_class = PROVIDERS[provider_name]
    return provider_class(config)


def get_available_providers() -> dict:
    """
    Get information about available LLM providers.

    Returns:
        Dictionary with provider names and their availability status
    """
    return {
        'ollama': {
            'available': True,
            'description': 'Local or remote Ollama LLM service',
            'requires_api_key': False,
        },
        'openai': {
            'available': OPENAI_AVAILABLE,
            'description': 'OpenAI API (GPT-4, GPT-3.5, etc.)',
            'requires_api_key': True,
            'install_command': 'pip install openai' if not OPENAI_AVAILABLE else None,
        },
        'anthropic': {
            'available': ANTHROPIC_AVAILABLE,
            'description': 'Anthropic API (Claude models)',
            'requires_api_key': True,
            'install_command': 'pip install anthropic' if not ANTHROPIC_AVAILABLE else None,
        },
    }


__all__ = [
    'LLMProviderBase',
    'OllamaProvider',
    'OpenAIProvider',
    'AnthropicProvider',
    'get_llm_provider',
    'get_available_providers',
    'PROVIDERS',
]
