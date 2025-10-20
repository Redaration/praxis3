#!/usr/bin/env python3
"""
Health check system for monitoring service health.
"""

import time
import requests
import logging
from typing import Dict, Any, List, Callable
from datetime import datetime

from config import config
from exceptions import ServiceUnavailableError
from circuit_breaker import health_checker
from llm_client import llm_client
from image_client import image_client
from utils import logger

class HealthCheck:
    """Individual health check."""
    
    def __init__(self, name: str, check_func: Callable[[], bool], timeout: int = 10):
        self.name = name
        self.check_func = check_func
        self.timeout = timeout
        self.last_check = None
        self.last_result = None
    
    def check(self) -> bool:
        """Perform health check."""
        try:
            self.last_result = self.check_func()
            self.last_check = datetime.now()
            return self.last_result
        except Exception as e:
            logger.error(f"Health check {self.name} failed: {e}")
            self.last_result = False
            self.last_check = datetime.now()
            return False

class HealthCheckManager:
    """Manages all health checks."""
    
    def __init__(self):
        self.checks: Dict[str, HealthCheck] = {}
        self.setup_default_checks()
    
    def setup_default_checks(self):
        """Setup default health checks."""
        
        # API Key validation
        self.add_check(
            "api_keys",
            self._check_api_keys,
            timeout=5
        )
        
        # LLM service health
        self.add_check(
            "llm_service",
            self._check_llm_service,
            timeout=15
        )
        
        # Image service health
        self.add_check(
            "image_service",
            self._check_image_service,
            timeout=15
        )
        
        # Network connectivity
        self.add_check(
            "network",
            self._check_network,
            timeout=10
        )
        
        # Disk space
        self.add_check(
            "disk_space",
            self._check_disk_space,
            timeout=5
        )
        
        # Memory usage
        self.add_check(
            "memory",
            self._check_memory,
            timeout=5
        )
    
    def add_check(self, name: str, check_func: Callable[[], bool], timeout: int = 10):
        """Add a new health check."""
        self.checks[name] = HealthCheck(name, check_func, timeout)
        health_checker.register_check(name, check_func)
    
    def _check_api_keys(self) -> bool:
        """Check if API keys are configured."""
        try:
            config.validate_config()
            return bool(config.OPENROUTER_API_KEY and config.RUNWARE_API_KEY)
        except Exception:
            return False
    
    def _check_llm_service(self) -> bool:
        """Check LLM service availability."""
        try:
            return llm_client.validate_api_key()
        except Exception:
            return False
    
    def _check_image_service(self) -> bool:
        """Check image service availability."""
        try:
            return image_client.validate_api_key()
        except Exception:
            return False
    
    def _check_network(self) -> bool:
        """Check network connectivity."""
        try:
            response = requests.get("https://httpbin.org/status/200", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _check_disk_space(self) -> bool:
        """Check available disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            # Alert if less than 1GB free
            return free > 1024 * 1024 * 1024
        except Exception:
            return True  # Skip if can't check
    
    def _check_memory(self) -> bool:
        """Check memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            # Alert if memory usage > 90%
            return memory.percent < 90
        except Exception:
            return True
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {
            "status": "healthy",
            "checks": {},
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - config.start_time if hasattr(config, 'start_time') else 0
        }
        
        all_healthy = True
        
        for name, check in self.checks.items():
            is_healthy = check.check()
            results["checks"][name] = {
                "healthy": is_healthy,
                "last_check": check.last_check.isoformat() if check.last_check else None
            }
            
            if not is_healthy:
                all_healthy = False
        
        results["status"] = "healthy" if all_healthy else "unhealthy"
        return results
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed health status."""
        basic_status = self.run_all_checks()
        
        # Add system information
        try:
            import psutil
            import os
            
            # System info
            basic_status["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "process_count": len(psutil.pids()),
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
            
            # Process info
            process = psutil.Process()
            basic_status["process"] = {
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_percent": process.cpu_percent(),
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections())
            }
            
        except ImportError:
            basic_status["system"] = {"info": "psutil not available"}
            basic_status["process"] = {"info": "psutil not available"}
        
        return basic_status
    
    def is_healthy(self) -> bool:
        """Quick health check."""
        return self.run_all_checks()["status"] == "healthy"

# Global health check manager
health_manager = HealthCheckManager()

# Convenience functions
def check_health() -> Dict[str, Any]:
    """Run health checks."""
    return health_manager.run_all_checks()

def is_healthy() -> bool:
    """Quick health check."""
    return health_manager.is_healthy()

def get_health_status() -> Dict[str, Any]:
    """Get detailed health status."""
    return health_manager.get_detailed_status()

# Add startup time to config
config.start_time = time.time()

# Register health checks with circuit breaker
health_checker.register_check("api_keys", health_manager._check_api_keys)
health_checker.register_check("llm_service", health_manager._check_llm_service)
health_checker.register_check("image_service", health_manager._check_image_service)
health_checker.register_check("network", health_manager._check_network)