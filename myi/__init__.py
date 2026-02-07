"""Myi - Real-time income tracker"""
__version__ = "1.0.1"
__author__ = "Mr Noor"
__description__ = "Watch your income grow in real-time"

from .core import IncomeConfig, IncomeTracker
from .display import MyiDisplay

__all__ = ["IncomeConfig", "IncomeTracker", "MyiDisplay"]
