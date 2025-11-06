"""
Offline data preparation pipelines for the MovieLens recommendation project.

This package exposes helpers for computing popularity, collaborative
filtering, and content-based artifacts that will be consumed by the FastAPI
service.
"""

from .config import PipelineConfig

__all__ = ["PipelineConfig"]

