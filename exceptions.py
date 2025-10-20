#!/usr/bin/env python3
"""
Custom exception classes for the AI-powered course content generation system.

This module provides a comprehensive set of exception classes for handling
various error scenarios in the application.
"""

class CourseGeneratorException(Exception):
    """Base exception for all course generator related errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

class ConfigurationError(CourseGeneratorException):
    """Raised when there's an issue with configuration."""
    pass

class APIError(CourseGeneratorException):
    """Base exception for API-related errors."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}

class LLMError(APIError):
    """Raised when there's an error with LLM API calls."""
    
    def __init__(self, message: str, model: str = None, prompt: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.model = model
        self.prompt = prompt

class ImageGenerationError(APIError):
    """Raised when there's an error generating images."""
    
    def __init__(self, message: str, prompt: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.prompt = prompt

class FileOperationError(CourseGeneratorException):
    """Raised when there's an error with file operations."""
    pass

class ValidationError(CourseGeneratorException):
    """Raised when input validation fails."""
    pass

class CacheError(CourseGeneratorException):
    """Raised when there's an error with caching operations."""
    pass

class DatabaseError(CourseGeneratorException):
    """Raised when there's an error with database operations."""
    pass

class RAGError(DatabaseError):
    """Raised when there's an error with RAG database operations."""
    pass

class TemplateError(CourseGeneratorException):
    """Raised when there's an error with template processing."""
    pass

class PresentationError(CourseGeneratorException):
    """Raised when there's an error with presentation generation."""
    pass

class AudioGenerationError(CourseGeneratorException):
    """Raised when there's an error with audio generation."""
    pass

class VideoGenerationError(CourseGeneratorException):
    """Raised when there's an error with video generation."""
    pass

class DependencyError(CourseGeneratorException):
    """Raised when required dependencies are missing."""
    pass

class TimeoutError(CourseGeneratorException):
    """Raised when operations timeout."""
    pass

class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    pass

class AuthenticationError(APIError):
    """Raised when API authentication fails."""
    pass

class NetworkError(APIError):
    """Raised when network operations fail."""
    pass

class ParseError(CourseGeneratorException):
    """Raised when parsing operations fail."""
    pass

class UnsupportedFormatError(CourseGeneratorException):
    """Raised when an unsupported file format is encountered."""
    pass

class ResourceNotFoundError(CourseGeneratorException):
    """Raised when required resources are not found."""
    pass

class ConcurrentModificationError(CourseGeneratorException):
    """Raised when concurrent modifications are detected."""
    pass

class QuotaExceededError(CourseGeneratorException):
    """Raised when resource quotas are exceeded."""
    pass

class RetryableError(CourseGeneratorException):
    """Base exception for errors that can be retried."""
    
    def __init__(self, message: str, max_retries: int = 3, retry_delay: float = 1.0, **kwargs):
        super().__init__(message, **kwargs)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

class TransientError(RetryableError):
    """Raised for transient errors that should be retried."""
    pass

class ServiceUnavailableError(RetryableError):
    """Raised when a service is temporarily unavailable."""
    pass

class ErrorHandler:
    """Utility class for handling and logging errors."""
    
    @staticmethod
    def handle_exception(exception: Exception, context: str = None, logger=None) -> None:
        """Handle an exception with appropriate logging and user feedback."""
        if logger:
            logger.error(f"Error in {context}: {str(exception)}", exc_info=True)
        else:
            print(f"Error in {context}: {str(exception)}")
    
    @staticmethod
    def is_retryable(exception: Exception) -> bool:
        """Check if an exception is retryable."""
        return isinstance(exception, RetryableError) or isinstance(exception, TransientError)
    
    @staticmethod
    def get_error_context(exception: Exception) -> dict:
        """Get context information about an exception."""
        context = {
            "type": type(exception).__name__,
            "message": str(exception),
            "retryable": ErrorHandler.is_retryable(exception)
        }
        
        if hasattr(exception, 'error_code'):
            context['error_code'] = exception.error_code
        
        if hasattr(exception, 'details'):
            context['details'] = exception.details
        
        return context