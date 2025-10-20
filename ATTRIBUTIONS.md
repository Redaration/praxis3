# Third-Party Library Attributions and References

This document provides proper attribution for all third-party libraries, APIs, and resources used in this AI-Powered Course Content Generation System. This project is being submitted as part of doctoral research and adheres to academic integrity standards.

## Project Overview

This system generates educational course content using AI, including PowerPoint presentations, images, quizzes, and multimedia materials. It integrates multiple AI services and follows best practices for production-grade software development.

---

## Core AI Services

### OpenRouter API
- **Purpose**: Large Language Model (LLM) API aggregation service
- **Usage**: Text generation for course content, outlines, quizzes, and explanations
- **Website**: https://openrouter.ai/
- **Documentation**: https://openrouter.ai/docs
- **License**: Commercial API service (requires API key)
- **Attribution**: All LLM-generated content is powered by models accessed through OpenRouter
- **Implementation**: Used in `llm_client.py` for all text generation tasks

### Runware API
- **Purpose**: AI image generation service
- **Usage**: Generating educational images, slide backgrounds, and visual content
- **Website**: https://runware.ai/
- **Documentation**: https://docs.runware.ai/
- **Library**: `runware` Python SDK
- **License**: Commercial API service (requires API key)
- **Attribution**: All AI-generated images are created using Runware's API
- **Implementation**: Used in `image_client.py` and `arunware_image_generator.py`

---

## Python Libraries

### Standard Library
The following Python standard library modules are used extensively:
- `os`, `sys`, `pathlib` - File system operations
- `json`, `pickle` - Data serialization
- `time`, `datetime` - Time and date handling
- `hashlib` - Cryptographic hashing for cache keys
- `logging` - Application logging
- `typing` - Type annotations
- `functools` - Higher-order functions and decorators
- `dataclasses` - Data structure definitions
- `enum` - Enumeration types
- `collections` - Specialized container datatypes
- `contextlib` - Context management utilities
- `unittest`, `pytest` - Testing frameworks
- `tempfile`, `shutil` - Temporary files and file operations
- `re` - Regular expressions
- `glob` - File pattern matching
- `asyncio`, `aiofiles`, `aiohttp` - Asynchronous I/O operations

### Third-Party Python Packages

#### Web and HTTP Libraries
- **requests**
  - Purpose: HTTP library for API calls
  - License: Apache 2.0
  - PyPI: https://pypi.org/project/requests/
  - Used in: `llm_client.py`, `image_client.py`

- **urllib3**
  - Purpose: HTTP client with retry mechanisms
  - License: MIT
  - PyPI: https://pypi.org/project/urllib3/
  - Used in: HTTP adapter configuration in `llm_client.py`

#### Document Generation
- **python-pptx**
  - Purpose: Creating and editing PowerPoint presentations
  - License: MIT
  - PyPI: https://pypi.org/project/python-pptx/
  - Documentation: https://python-pptx.readthedocs.io/
  - Used in: PowerPoint generation modules (`a05_CREATE_POWERPOINT.py`)

#### Environment and Configuration
- **python-dotenv**
  - Purpose: Loading environment variables from .env files
  - License: BSD-3-Clause
  - PyPI: https://pypi.org/project/python-dotenv/
  - Used in: `config.py` for secure API key management

#### AI/ML Service SDKs
- **runware**
  - Purpose: Official Runware API Python SDK
  - License: Proprietary/Commercial
  - PyPI: https://pypi.org/project/runware/
  - Documentation: https://docs.runware.ai/
  - Used in: `arunware_image_generator.py`, `image_client.py`

#### Monitoring and Metrics (Optional)
- **prometheus_client**
  - Purpose: Metrics collection and monitoring
  - License: Apache 2.0
  - PyPI: https://pypi.org/project/prometheus-client/
  - Used in: `metrics.py` (optional, gracefully degrades if not installed)

- **psutil**
  - Purpose: System and process monitoring
  - License: BSD-3-Clause
  - PyPI: https://pypi.org/project/psutil/
  - Used in: `utils.py` for memory usage tracking (optional)

---

## Design Patterns and Architectural Concepts

This project implements several well-established software engineering patterns:

### Circuit Breaker Pattern
- **Purpose**: Fault tolerance and graceful degradation
- **Reference**: Michael Nygard, "Release It!" (2007)
- **Implementation**: `circuit_breaker.py`
- **Description**: Prevents cascade failures by temporarily disabling failing services

### Rate Limiting (Token Bucket Algorithm)
- **Purpose**: API throttling and cost control
- **Reference**: Standard rate limiting algorithms
- **Implementation**: `rate_limiter.py`
- **Description**: Sliding window rate limiter for API call management

### Caching Strategy
- **Purpose**: Performance optimization and API cost reduction
- **Implementation**: `cache_manager.py`
- **Description**: TTL-based caching with automatic expiration and cleanup

### Retry Logic with Exponential Backoff
- **Purpose**: Resilient API communication
- **Reference**: AWS Architecture Blog - Exponential Backoff and Jitter
- **Implementation**: `utils.py` (RetryUtils class)
- **Description**: Automatic retry with increasing delays for transient failures

---

## Academic and Research Context

### Doctoral Research
This project is submitted as part of a doctoral program (Praxis). Key considerations:

1. **Original Work**: All custom code, architecture, and integration logic is original
2. **AI-Generated Content Disclosure**: Content generated by AI models is clearly marked
3. **Third-Party Attribution**: All libraries and services are properly attributed
4. **Reproducibility**: Environment configuration is documented for research validation
5. **Ethical AI Use**: AI services are used for educational content generation only

### Educational Framework
The course generation methodology is based on:
- Bloom's Taxonomy for learning objectives
- ADDIE instructional design model
- Multimodal learning principles

---

## File Structure Attribution

### Core Application Files
- `app.py` - Main application runner (original work)
- `run_app.py` - Simplified application runner (original work)
- `demo.py` - Demonstration module (original work)
- `config.py` - Configuration management (original work)
- `exceptions.py` - Custom exception hierarchy (original work)

### Client Libraries
- `llm_client.py` - OpenRouter API wrapper (original work)
- `image_client.py` - Runware API wrapper (original work)
- `arunware_image_generator.py` - Runware image generation utilities (original work)

### Infrastructure Components
- `cache_manager.py` - Caching system (original work)
- `circuit_breaker.py` - Circuit breaker implementation (original work)
- `rate_limiter.py` - Rate limiting (original work)
- `metrics.py` - Metrics collection (original work)
- `health_check.py` - Health monitoring (original work)
- `validation.py` - Input validation and sanitization (original work)
- `utils.py` - Shared utilities (original work)

### Testing
- `enhanced_test_suite.py` - Comprehensive test suite (original work)
- `test_*.py` - Various test modules (original work)

---

## Data Privacy and Security

### API Key Management
- API keys are stored in `.env` files (not committed to version control)
- Environment variables are used for sensitive configuration
- Validation ensures keys are present before operations

### Input Sanitization
- XSS prevention through input cleaning
- Path traversal protection
- File name sanitization

---

## Compliance and Licensing

### Project License
This project's custom code is proprietary and created for doctoral research purposes.

### Third-Party License Compliance
All third-party libraries are used in compliance with their respective licenses:
- MIT License: Requires attribution (provided in this document)
- Apache 2.0: Requires attribution and notice (provided in this document)
- BSD Licenses: Requires attribution (provided in this document)
- Commercial APIs: Used with valid API keys and within terms of service

---

## Citation Information

If citing this work in academic contexts, please use:

```
Yohn, Brandon. (2025). AI-Powered Course Content Generation System:
A Framework for Automated Educational Content Development Using Large Language Models.
Praxis Doctoral Research Project. The George Washington University.
```

### Technology Stack Summary
- **Language**: Python 3.12+
- **LLM Provider**: OpenRouter (https://openrouter.ai/)
- **Image Generation**: Runware AI (https://runware.ai/)
- **Primary Model**: Google Gemini 2.5 Flash (via OpenRouter)
- **Architecture**: Microservices-inspired modular design
- **Testing**: unittest and pytest frameworks

---

## Acknowledgments

- OpenRouter team for providing unified LLM API access
- Runware team for image generation capabilities
- Open source community for the excellent Python libraries
- Academic advisors and committee members for guidance

---

## Contact and Questions

For questions about attributions, licensing, or usage:
- Review the project README.md
- Check individual file headers for specific attributions
- Refer to official documentation of third-party services

---

**Last Updated**: 2025-01-20

**Version**: 1.0

**Status**: Doctoral Research Project

---

## Disclaimer

This project uses AI services to generate educational content. All generated content should be reviewed and validated before use in production educational settings. The quality and accuracy of generated content depends on the underlying AI models and prompts provided.
