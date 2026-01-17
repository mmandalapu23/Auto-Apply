"""LLM integration module.

NOTE: This module contains stubs for advanced features planned for v2.0+:
  - Job description parsing and extraction
  - Resume-to-JD matching and scoring
  - Resume validation and ATS formatting

For the MVP, these are handled by simplified helper functions.
Reactivate when LLM provider (OpenAI, Anthropic, etc.) integration is ready.
"""
from app.llm.client import LLMClient
from app.llm.pipeline import LLMPipeline
from app.llm.validators import validate_no_fabrication, validate_ats_formatting, validate_consistent_dates

__all__ = [
    "LLMClient",
    "LLMPipeline",
    "validate_no_fabrication",
    "validate_ats_formatting",
    "validate_consistent_dates",
]
