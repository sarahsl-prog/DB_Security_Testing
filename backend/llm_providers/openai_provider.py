#!/usr/bin/env python3
"""
OpenAI LLM Provider

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing

Handles communication with OpenAI API for SQL generation.
"""

import time
from typing import List, Dict, Any
from loguru import logger

from .base import LLMProviderBase

# Optional import - will be checked at runtime
try:
    from openai import OpenAI, APIError, APIConnectionError, RateLimitError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class OpenAIProvider(LLMProviderBase):
    """Provider for OpenAI API (GPT-4, GPT-3.5, etc.)"""

    # Available models for reference
    AVAILABLE_MODELS = [
        'gpt-4o',
        'gpt-4o-mini',
        'gpt-4-turbo',
        'gpt-4',
        'gpt-3.5-turbo',
    ]

    def __init__(self, config):
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

        super().__init__(config)
        self.api_key = config.LLM_API_KEY
        self.base_url = config.LLM_BASE_URL

        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url if config.LLM_API_BASE else None,
            timeout=self.timeout
        )

        logger.info(f"OpenAI Provider initialized")
        logger.debug(f"OpenAI Configuration: model={self.default_model}, timeout={self.timeout}s")

    @property
    def provider_name(self) -> str:
        return "openai"

    def test_connection(self) -> bool:
        """Test connection to OpenAI API"""
        try:
            logger.info("Testing connection to OpenAI API")
            start_time = time.time()

            # Make a minimal API call to verify credentials
            response = self.client.models.list()

            elapsed_time = (time.time() - start_time) * 1000

            model_ids = [model.id for model in response.data[:10]]

            logger.success(f"OpenAI connection successful ({elapsed_time:.2f}ms)")
            logger.info(f"Available models (sample): {', '.join(model_ids[:5])}")

            return True

        except Exception as e:
            logger.error(f"OpenAI connection failed: {str(e)}")
            raise

    def get_available_models(self) -> List[str]:
        """Get list of available models from OpenAI"""
        try:
            response = self.client.models.list()
            # Filter to GPT models only
            models = [
                model.id for model in response.data
                if 'gpt' in model.id.lower()
            ]
            logger.info(f"Available OpenAI GPT models: {len(models)}")
            return sorted(models)

        except Exception as e:
            logger.error(f"Failed to get available models: {str(e)}")
            # Return known models as fallback
            return self.AVAILABLE_MODELS

    def _call_api(self, prompt: str, model: str = None) -> str:
        """Make API call to OpenAI with retry logic"""
        if model is None:
            model = self.default_model

        # Build messages for chat completion
        messages = [
            {
                "role": "system",
                "content": "You are a SQL query generator. Generate only valid SQL queries without explanations or markdown formatting."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        logger.info(f"Calling OpenAI API with model: {model}")
        logger.debug(f"Prompt length: {len(prompt)} characters")

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"OpenAI API call attempt {attempt + 1}/{self.max_retries}")
                start_time = time.time()

                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=256,
                    top_p=0.9
                )

                if not response.choices:
                    raise ValueError("Empty response from OpenAI")

                sql_response = response.choices[0].message.content.strip()

                if not sql_response:
                    raise ValueError("Empty content in OpenAI response")

                elapsed_time = time.time() - start_time
                logger.success(f"OpenAI response received in {elapsed_time:.3f}s ({len(sql_response)} characters)")
                logger.debug(f"Generated response preview: {sql_response[:100]}...")

                # Log token usage
                if response.usage:
                    logger.debug(f"Token usage - prompt: {response.usage.prompt_tokens}, "
                               f"completion: {response.usage.completion_tokens}, "
                               f"total: {response.usage.total_tokens}")

                return sql_response

            except RateLimitError as e:
                wait_time = 2 ** attempt
                logger.warning(f"OpenAI rate limit hit on attempt {attempt + 1}/{self.max_retries}")
                if attempt == self.max_retries - 1:
                    logger.error("OpenAI rate limit exceeded after all retries")
                    raise
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)

            except APIConnectionError as e:
                wait_time = 2 ** attempt
                logger.warning(f"OpenAI connection error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error("Cannot connect to OpenAI API after all retries")
                    raise ConnectionError("Cannot connect to OpenAI API")
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)

            except APIError as e:
                logger.error(f"OpenAI API error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)

        raise RuntimeError("OpenAI API call failed after all retries")

    def health_check(self) -> Dict[str, Any]:
        """Enhanced health check for OpenAI"""
        health_data = super().health_check()

        # Add OpenAI-specific info
        health_data['config']['base_url'] = self.base_url
        health_data['config']['has_api_key'] = bool(self.api_key)

        return health_data
