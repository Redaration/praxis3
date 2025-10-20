#!/usr/bin/env python3
"""
Metrics collection and monitoring for the AI course generator.
"""

import time
import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime

try:
    from prometheus_client import Counter, Histogram, Gauge, Info
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from config import config
from utils import logger

@dataclass
class MetricsData:
    """Data class for metrics collection."""
    api_calls: int = 0
    api_errors: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_processing_time: float = 0.0
    image_generation_count: int = 0
    image_generation_errors: int = 0
    llm_calls: int = 0
    llm_errors: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'api_calls': self.api_calls,
            'api_errors': self.api_errors,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_processing_time': self.total_processing_time,
            'image_generation_count': self.image_generation_count,
            'image_generation_errors': self.image_generation_errors,
            'llm_calls': self.llm_calls,
            'llm_errors': self.llm_errors,
            'error_rate': self.error_rate,
            'cache_hit_rate': self.cache_hit_rate,
            'average_processing_time': self.average_processing_time
        }
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        total = self.api_calls + self.llm_calls + self.image_generation_count
        errors = self.api_errors + self.llm_errors + self.image_generation_errors
        return errors / total if total > 0 else 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0
    
    @property
    def average_processing_time(self) -> float:
        """Calculate average processing time."""
        total_ops = self.api_calls + self.llm_calls + self.image_generation_count
        return self.total_processing_time / total_ops if total_ops > 0 else 0.0

class MetricsCollector:
    """Metrics collection and reporting."""
    
    def __init__(self):
        self.metrics = MetricsData()
        self.start_time = time.time()
        
        # Prometheus metrics
        if PROMETHEUS_AVAILABLE and config.ENABLE_METRICS:
            self._setup_prometheus_metrics()
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics if available."""
        if not PROMETHEUS_AVAILABLE:
            return
            
        self.api_calls_counter = Counter(
            'api_calls_total',
            'Total API calls',
            ['service', 'endpoint']
        )
        
        self.api_errors_counter = Counter(
            'api_errors_total',
            'Total API errors',
            ['service', 'endpoint', 'error_type']
        )
        
        self.request_duration = Histogram(
            'request_duration_seconds',
            'Request duration in seconds',
            ['service', 'operation']
        )
        
        self.cache_hits_counter = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_type']
        )
        
        self.cache_misses_counter = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_type']
        )
        
        self.active_requests = Gauge(
            'active_requests',
            'Number of active requests',
            ['service']
        )
        
        self.system_info = Info(
            'system_info',
            'System information'
        )
        
        self.system_info.info({
            'version': '1.0.0',
            'environment': os.getenv('ENVIRONMENT', 'development')
        })
    
    def record_api_call(self, service: str, endpoint: str, duration: float, error: Optional[str] = None):
        """Record API call metrics."""
        self.metrics.api_calls += 1
        
        if PROMETHEUS_AVAILABLE and config.ENABLE_METRICS:
            self.api_calls_counter.labels(service=service, endpoint=endpoint).inc()
            self.request_duration.labels(service=service, operation='api_call').observe(duration)
            
            if error:
                self.api_errors_counter.labels(
                    service=service,
                    endpoint=endpoint,
                    error_type=type(error).__name__
                ).inc()
                self.metrics.api_errors += 1
    
    def record_cache_hit(self, cache_type: str = "default"):
        """Record cache hit."""
        self.metrics.cache_hits += 1
        if PROMETHEUS_AVAILABLE and config.ENABLE_METRICS:
            self.cache_hits_counter.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str = "default"):
        """Record cache miss."""
        self.metrics.cache_misses += 1
        if PROMETHEUS_AVAILABLE and config.ENABLE_METRICS:
            self.cache_misses_counter.labels(cache_type=cache_type).inc()
    
    def record_image_generation(self, duration: float, error: Optional[str] = None):
        """Record image generation metrics."""
        self.metrics.image_generation_count += 1
        self.metrics.total_processing_time += duration
        
        if PROMETHEUS_AVAILABLE and config.ENABLE_METRICS:
            self.request_duration.labels(
                service='image_generation',
                operation='generate'
            ).observe(duration)
            
            if error:
                self.metrics.image_generation_errors += 1
    
    def record_llm_call(self, duration: float, error: Optional[str] = None):
        """Record LLM call metrics."""
        self.metrics.llm_calls += 1
        self.metrics.total_processing_time += duration
        
        if PROMETHEUS_AVAILABLE and config.ENABLE_METRICS:
            self.request_duration.labels(
                service='llm',
                operation='generate'
            ).observe(duration)
            
            if error:
                self.metrics.llm_errors += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        uptime = time.time() - self.start_time
        metrics_dict = self.metrics.to_dict()
        metrics_dict.update({
            'uptime_seconds': uptime,
            'uptime_formatted': str(datetime.fromtimestamp(self.start_time)),
            'timestamp': datetime.now().isoformat()
        })
        return metrics_dict
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics = MetricsData()
        self.start_time = time.time()

# Global metrics collector
metrics_collector = MetricsCollector()

@contextmanager
def timer_context(service: str, operation: str):
    """Context manager for timing operations."""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        metrics_collector.request_duration.labels(
            service=service,
            operation=operation
        ).observe(duration)

# Convenience functions
def record_api_call(service: str, endpoint: str, duration: float, error: Optional[str] = None):
    """Record API call."""
    metrics_collector.record_api_call(service, endpoint, duration, error)

def record_cache_hit(cache_type: str = "default"):
    """Record cache hit."""
    metrics_collector.record_cache_hit(cache_type)

def record_cache_miss(cache_type: str = "default"):
    """Record cache miss."""
    metrics_collector.record_cache_miss(cache_type)

def get_metrics() -> Dict[str, Any]:
    """Get current metrics."""
    return metrics_collector.get_metrics()

# Export for use
__all__ = [
    'MetricsCollector',
    'metrics_collector',
    'record_api_call',
    'record_cache_hit',
    'record_cache_miss',
    'get_metrics',
    'timer_context'
]