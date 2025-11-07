"""
Comprehensive Query Logging System

A complete system for logging and analyzing schema compression evaluation results.
Captures detailed per-query information including execution times, success rates,
compression ratios, and more.

Main Components:
- ComprehensiveQueryLogger: Core logging system
- Enhanced precision evaluation scripts with detailed logging

Usage:
    from comprehensive_logger import ComprehensiveQueryLogger
    
    logger = ComprehensiveQueryLogger("output_dir")
    # Use logger to log query executions
"""

from .comprehensive_query_logger import ComprehensiveQueryLogger

__version__ = "1.0.0"
__author__ = "UTN"

__all__ = [
    "ComprehensiveQueryLogger"
]
