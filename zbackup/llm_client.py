#!/usr/bin/env python3
"""
Enhanced LLM client with caching, retry logic, and comprehensive error handling.

This module provides a robust interface for interacting with LLM APIs
(OpenRouter.ai) with built-in caching, retry mechanisms, and proper error handling.
"""

import json
import time
import logging
from typing import Optional, Dict, Any, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import os
from config import config
from exceptions import LLMError, RateLimitError, AuthenticationError, NetworkError
from cache_manager import cached, cache_manager
from utils import RetryUtils, logger
from rate_limiter import llm_rate_limiter
from circuit_breaker import circuit_breaker
from metrics import metrics_collector

class LLMClient:
    """Enhanced LLM client with caching and retry capabilities."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize the LLM client."""
        config.validate_config()
        self.api_key = api_key or config.OPENROUTER_API_KEY
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    @cached(ttl=1800)  # Cache for 30 minutes
    @circuit_breaker(
        failure_threshold=config.CIRCUIT_BREAKER_THRESHOLD,
        recovery_timeout=config.HEALTH_CHECK_INTERVAL
    )
    def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Call the LLM API with caching and retry logic.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            model: Model to use (defaults to config.DEFAULT_MODEL)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            The LLM response text
            
        Raises:
            LLMError: If the API call fails
            RateLimitError: If rate limit is exceeded
            AuthenticationError: If authentication fails
        """
        model = model or config.DEFAULT_MODEL
        temperature = temperature or config.TEMPERATURE
        max_tokens = max_tokens or config.MAX_TOKENS
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost",
            "X-Title": "RAG Application"
        }
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request data
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        logger.debug(f"Calling LLM API with model: {model}")
        
        start_time = time.time()
        try:
            llm_rate_limiter.check_rate_limit()
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            # Handle different response codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 500:
                raise NetworkError(f"Server error: {response.status_code}")
            
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0]['message']['content']
                duration = time.time() - start_time
                metrics_collector.record_llm_call(duration)
                return content
            else:
                raise LLMError("No response content found in API response")
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            metrics_collector.record_llm_call(duration, "timeout")
            raise NetworkError("Request timeout")
        except requests.exceptions.ConnectionError:
            duration = time.time() - start_time
            metrics_collector.record_llm_call(duration, "connection_error")
            raise NetworkError("Connection error")
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            metrics_collector.record_llm_call(duration, str(e))
            raise NetworkError(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            duration = time.time() - start_time
            metrics_collector.record_llm_call(duration, "json_decode_error")
            raise LLMError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            duration = time.time() - start_time
            metrics_collector.record_llm_call(duration, str(e))
            raise LLMError(f"Unexpected error: {str(e)}")
    
    def call_llm_batch(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        Call the LLM API for multiple prompts in batch.
        
        Args:
            prompts: List of prompts
            system_prompt: Optional system prompt for all prompts
            model: Model to use
            **kwargs: Additional parameters
            
        Returns:
            List of LLM responses
        """
        model = model or config.DEFAULT_MODEL
        responses = []
        
        logger.info(f"Processing {len(prompts)} prompts in batch")
        
        for i, prompt in enumerate(prompts):
            try:
                response = self.call_llm(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=model,
                    **kwargs
                )
                responses.append(response)
                logger.debug(f"Processed prompt {i+1}/{len(prompts)}")
            except Exception as e:
                logger.error(f"Failed to process prompt {i+1}: {e}")
                responses.append(f"Error: {str(e)}")
        
        return responses
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json().get('data', [])
            
        except Exception as e:
            logger.warning(f"Failed to get available models: {e}")
            return []
    
    def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        models = self.get_available_models()
        for model_info in models:
            if model_info.get('id') == model:
                return model_info
        return None
    
    def validate_api_key(self) -> bool:
        """Validate the API key by making a test request."""
        try:
            self.call_llm(
                prompt="Test",
                max_tokens=1,
                model=config.DEFAULT_MODEL
            )
            return True
        except AuthenticationError:
            return False
        except Exception as e:
            logger.error(f"API validation failed: {e}")
            return False

# Global client instance
llm_client = LLMClient()

# Convenience functions
def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> str:
    """Convenience function to call LLM with the global client."""
    return llm_client.call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        **kwargs
    )

def call_llm_batch(
    prompts: List[str],
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> List[str]:
    """Convenience function for batch processing."""
    return llm_client.call_llm_batch(
        prompts=prompts,
        system_prompt=system_prompt,
        model=model,
        **kwargs
    )

# Export commonly used items
__all__ = [
    'LLMClient', 'llm_client', 'call_llm', 'call_llm_batch'
]