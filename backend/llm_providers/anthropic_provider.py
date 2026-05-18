#!/usr/bin/env python3
"""
Anthropic LLM Provider

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing

Handles communication with Anthropic API for SQL generation.
"""

import time
from typing import List, Dict, Any
from loguru import logger

from .base import LLMProviderBase

# Optional import - will be checked at runtime
try:
    import anthropic
    from anthropic import APIError, APIConnectionError, RateLimitError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None


class AnthropicProvider(LLMProviderBase):
    """Provider for Anthropic API (Claude models)"""

    # Available models for reference
    AVAILABLE_MODELS = [
        'claude-3-5-sonnet-20241022',
        'claude-3-5-haiku-20241022',
        'claude-3-opus-20240229',
        'claude-3-sonnet-20240229',
        'claude-3-haiku-20240307',
    ]

    def __init__(self, config):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )

        super().__init__(config)
        self.api_key = config.LLM_API_KEY
        self.base_url = config.LLM_BASE_URL

        # Initialize Anthropic client
        client_kwargs = {
            'api_key': self.api_key,
            'timeout': self.timeout
        }

        # Only set base_url if custom endpoint is configured
        if config.LLM_API_BASE:
            client_kwargs['base_url'] = self.base_url

        self.client = anthropic.Anthropic(**client_kwargs)

        logger.info(f"Anthropic Provider initialized")
        logger.debug(f"Anthropic Configuration: model={self.default_model}, timeout={self.timeout}s")

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def test_connection(self) -> bool:
        """Test connection to Anthropic API"""
        try:
            logger.info("Testing connection to Anthropic API")
            start_time = time.time()

            # Make a minimal API call to verify credentials
            # Anthropic doesn't have a models.list endpoint, so we make a small request
            response = self.client.messages.create(
                model=self.default_model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )

            elapsed_time = (time.time() - start_time) * 1000

            logger.success(f"Anthropic connection successful ({elapsed_time:.2f}ms)")
            logger.info(f"Using model: {self.default_model}")

            return True

        except Exception as e:
            logger.error(f"Anthropic connection failed: {str(e)}")
            raise

    def get_available_models(self) -> List[str]:
        """Get list of available models from Anthropic"""
        # Anthropic doesn't have a models listing endpoint
        # Return known models
        logger.info(f"Available Anthropic Claude models: {len(self.AVAILABLE_MODELS)}")
        return self.AVAILABLE_MODELS

    def _call_api(self, prompt: str, model: str = None) -> str:
        """Make API call to Anthropic with retry logic"""
        if model is None:
            model = self.default_model

        logger.info(f"Calling Anthropic API with model: {model}")
        logger.debug(f"Prompt length: {len(prompt)} characters")

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Anthropic API call attempt {attempt + 1}/{self.max_retries}")
                start_time = time.time()

                response = self.client.messages.create(
                    model=model,
                    max_tokens=256,
                    system="You are a SQL query generator. Generate only valid SQL queries without explanations or markdown formatting.",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,
                    top_p=0.9
                )

                if not response.content:
                    raise ValueError("Empty response from Anthropic")

                # Extract text from response content blocks
                sql_response = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        sql_response += block.text

                sql_response = sql_response.strip()

                if not sql_response:
                    raise ValueError("Empty content in Anthropic response")

                elapsed_time = time.time() - start_time
                logger.success(f"Anthropic response received in {elapsed_time:.3f}s ({len(sql_response)} characters)")
                logger.debug(f"Generated response preview: {sql_response[:100]}...")

                # Log token usage
                if response.usage:
                    logger.debug(f"Token usage - input: {response.usage.input_tokens}, "
                               f"output: {response.usage.output_tokens}")

                return sql_response

            except RateLimitError as e:
                wait_time = 2 ** attempt
                logger.warning(f"Anthropic rate limit hit on attempt {attempt + 1}/{self.max_retries}")
                if attempt == self.max_retries - 1:
                    logger.error("Anthropic rate limit exceeded after all retries")
                    raise
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)

            except APIConnectionError as e:
                wait_time = 2 ** attempt
                logger.warning(f"Anthropic connection error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error("Cannot connect to Anthropic API after all retries")
                    raise ConnectionError("Cannot connect to Anthropic API")
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)

            except APIError as e:
                logger.error(f"Anthropic API error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)

        raise RuntimeError("Anthropic API call failed after all retries")

    def health_check(self) -> Dict[str, Any]:
        """Enhanced health check for Anthropic"""
        health_data = super().health_check()

        # Add Anthropic-specific info
        health_data['config']['base_url'] = self.base_url
        health_data['config']['has_api_key'] = bool(self.api_key)

        return health_data
