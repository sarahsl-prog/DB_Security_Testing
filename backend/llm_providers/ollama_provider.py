#!/usr/bin/env python3
"""
Ollama LLM Provider

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing

Handles communication with local or remote Ollama LLM service.
"""

import requests
import time
from typing import List
from urllib.parse import urljoin
from loguru import logger

from .base import LLMProviderBase


class OllamaProvider(LLMProviderBase):
    """Provider for Ollama LLM service (local or remote)"""

    def __init__(self, config):
        super().__init__(config)
        self.base_url = config.LLM_BASE_URL
        logger.info(f"Ollama Provider initialized for {self.base_url}")
        logger.debug(f"Ollama Configuration: model={self.default_model}, timeout={self.timeout}s")

    @property
    def provider_name(self) -> str:
        return "ollama"

    def test_connection(self) -> bool:
        """Test connection to Ollama service"""
        try:
            logger.info(f"Testing connection to Ollama LLM service at {self.base_url}")
            start_time = time.time()

            response = requests.get(
                urljoin(self.base_url, '/api/tags'),
                timeout=5
            )
            response.raise_for_status()

            elapsed_time = (time.time() - start_time) * 1000

            models = response.json().get('models', [])
            model_names = [model.get('name', 'unknown') for model in models]

            logger.success(f"Ollama connection successful ({elapsed_time:.2f}ms)")
            logger.info(f"Available models ({len(models)}): {', '.join(model_names[:5])}")

            if self.default_model not in model_names:
                logger.warning(f"Default model '{self.default_model}' not found in available models")

            return True

        except requests.exceptions.Timeout:
            logger.error(f"Ollama connection timeout after 5s to {self.base_url}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ollama connection failed - Cannot reach {self.base_url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Ollama connection failed: {str(e)}")
            raise

    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama"""
        try:
            response = requests.get(
                urljoin(self.base_url, '/api/tags'),
                timeout=self.timeout
            )
            response.raise_for_status()

            models_data = response.json().get('models', [])
            models = [model['name'] for model in models_data]

            logger.info(f"Available Ollama models: {models}")
            return models

        except Exception as e:
            logger.error(f"Failed to get available models: {str(e)}")
            return []

    def _call_api(self, prompt: str, model: str = None) -> str:
        """Make API call to Ollama service with retry logic"""
        if model is None:
            model = self.default_model

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 256
            }
        }

        logger.info(f"Calling Ollama API with model: {model}")
        logger.debug(f"Prompt length: {len(prompt)} characters")

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Ollama API call attempt {attempt + 1}/{self.max_retries}")
                start_time = time.time()

                response = requests.post(
                    urljoin(self.base_url, '/api/generate'),
                    json=payload,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )

                response.raise_for_status()

                result = response.json()

                if 'response' not in result:
                    raise ValueError("Invalid response format from Ollama")

                sql_response = result['response'].strip()

                if not sql_response:
                    raise ValueError("Empty response from Ollama")

                elapsed_time = time.time() - start_time
                logger.success(f"Ollama response received in {elapsed_time:.3f}s ({len(sql_response)} characters)")
                logger.debug(f"Generated response preview: {sql_response[:100]}...")

                return sql_response

            except requests.exceptions.Timeout:
                wait_time = 2 ** attempt
                logger.warning(f"Ollama API timeout on attempt {attempt + 1}/{self.max_retries}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Ollama API timeout after all {self.max_retries} retries")
                    raise TimeoutError("Ollama API timeout after all retries")
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)

            except requests.exceptions.ConnectionError as e:
                wait_time = 2 ** attempt
                logger.warning(f"Ollama connection error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Cannot connect to Ollama service after {self.max_retries} retries")
                    raise ConnectionError("Cannot connect to Ollama service")
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)

            except Exception as e:
                logger.error(f"Ollama API error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)

        raise RuntimeError("Ollama API call failed after all retries")
