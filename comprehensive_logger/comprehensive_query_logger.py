#!/usr/bin/env python3
"""
Comprehensive Query Logger: Enhanced precision evaluation with detailed per-query logging
Logs everything: queryId, schemaName, schemaCompressionMethod, schemaCompressionRuntime, 
schemaSizeInByte, compressedSchemaSizeInByte, success, runtime, accuracy, and more...
"""

import json
import os
import time
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class ComprehensiveQueryLogger:
    """Enhanced query logger that captures all execution details"""
    
    def __init__(self, output_dir: str = "query_logs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize log files
        self.detailed_log_file = self.output_dir / "detailed_query_logs.json"
        self.summary_log_file = self.output_dir / "query_summary.json"
        
        # Initialize data structures
        self.detailed_logs = []
        self.query_summary = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "methods_tested": [],
            "databases_tested": [],
            "execution_start": None,
            "execution_end": None
        }
    
    def log_query_execution(self, query_id: str, schema_name: str, 
                          compression_method: str, question: str, 
                          gold_sql: str, generated_sql: str,
                          execution_time: float, success: bool,
                          schema_compression_data: Dict[str, Any],
                          **kwargs) -> Dict[str, Any]:
        """Log detailed query execution information with comprehensive metrics"""
        
        # Generate unique query execution ID
        execution_id = hashlib.md5(f"{query_id}_{schema_name}_{compression_method}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        # Calculate additional metrics
        original_size = schema_compression_data.get("original_schema_size_bytes", 0)
        compressed_size = schema_compression_data.get("compressed_schema_size_bytes", 0)
        compression_time = schema_compression_data.get("compression_runtime_seconds", 0)
        
        # Calculate accuracy metrics
        accuracy_score = 1.0 if success else 0.0
        efficiency_score = compressed_size / original_size if original_size > 0 else 0
        
        query_log_entry = {
            "execution_id": execution_id,
            "timestamp": datetime.now().isoformat(),
            "query_id": query_id,
            "schema_name": schema_name,
            "schema_compression_method": compression_method,
            
            # Query details
            "question": question,
            "gold_sql": gold_sql,
            "generated_sql": generated_sql,
            
            # Timing metrics
            "query_execution_runtime_seconds": execution_time,
            "schema_compression_runtime_seconds": compression_time,
            "total_runtime_seconds": execution_time + compression_time,
            "llm_generation_time_seconds": kwargs.get("llm_time", 0),
            "validation_time_seconds": kwargs.get("validation_time", 0),
            
            # Success metrics
            "query_success": success,
            "schema_compression_success": schema_compression_data.get("compression_success", False),
            "accuracy_score": accuracy_score,
            
            # Schema size metrics
            "original_schema_size_bytes": original_size,
            "compressed_schema_size_bytes": compressed_size,
            "compression_ratio": schema_compression_data.get("compression_ratio", 0),
            "efficiency_score": efficiency_score,
            "size_reduction_bytes": original_size - compressed_size,
            "size_reduction_percentage": ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0,
            
            # Result metrics
            "expected_result_count": kwargs.get("expected_result_count", 0),
            "actual_result_count": kwargs.get("actual_result_count", 0),
            "result_count_match": kwargs.get("expected_result_count", 0) == kwargs.get("actual_result_count", 0),
            "expected_columns": kwargs.get("expected_columns", []),
            "actual_columns": kwargs.get("actual_columns", []),
            "column_match": kwargs.get("expected_columns", []) == kwargs.get("actual_columns", []),
            
            # Error handling
            "error_message": kwargs.get("error", None),
            "has_error": bool(kwargs.get("error")),
            
            # Additional metadata
            "additional_metadata": {k: v for k, v in kwargs.items() if k not in [
                "llm_time", "validation_time", "expected_result_count", "actual_result_count", 
                "expected_columns", "actual_columns", "error"
            ]}
        }
        
        # Add to detailed logs
        self.detailed_logs.append(query_log_entry)
        
        # Update summary
        self.query_summary["total_queries"] += 1
        if success:
            self.query_summary["successful_queries"] += 1
        else:
            self.query_summary["failed_queries"] += 1
        
        if compression_method not in self.query_summary["methods_tested"]:
            self.query_summary["methods_tested"].append(compression_method)
        
        if schema_name not in self.query_summary["databases_tested"]:
            self.query_summary["databases_tested"].append(schema_name)
        
        return query_log_entry
    
    def save_logs(self):
        """Save all logs to files"""
        
        # Set execution end time
        self.query_summary["execution_end"] = datetime.now().isoformat()
        
        # Save detailed query logs
        with open(self.detailed_log_file, 'w') as f:
            json.dump(self.detailed_logs, f, indent=2)
        
        # Save summary
        with open(self.summary_log_file, 'w') as f:
            json.dump(self.query_summary, f, indent=2)
        
        # Create structured data exports for easy analysis
        self.create_structured_exports()
        
        print(f"✅ Logs saved to {self.output_dir}")
        print(f"   - Detailed query logs: {len(self.detailed_logs)} entries")
        print(f"   - Summary: {self.query_summary['total_queries']} total queries")
        print(f"   - Structured exports: query_data.json, query_data.csv, queries_analysis.csv")
    
    def create_structured_exports(self):
        """Create structured data exports for easy SQL-like analysis"""
        
        # Create flattened query data for easy analysis - QUERY-WISE CSV
        query_data = []
        for log in self.detailed_logs:
            query_data.append({
                # Core query identification
                "queryId": log["query_id"],
                "executionId": log["execution_id"],
                "timestamp": log["timestamp"],
                
                # Schema information
                "schemaName": log["schema_name"],
                "schemaCompressionMethod": log["schema_compression_method"],
                
                # Query details
                "question": log["question"],
                "goldSql": log["gold_sql"],
                "generatedSql": log["generated_sql"],
                
                # Schema compression metrics
                "schemaCompressionRuntime": log["schema_compression_runtime_seconds"],
                "schemaSizeInByte": log["original_schema_size_bytes"],
                "compressedSchemaSizeInByte": log["compressed_schema_size_bytes"],
                "compressionRatio": log["compression_ratio"],
                "sizeReductionBytes": log["size_reduction_bytes"],
                "sizeReductionPercentage": log["size_reduction_percentage"],
                "schemaCompressionSuccess": log["schema_compression_success"],
                
                # Query execution metrics
                "queryExecutionRuntime": log["query_execution_runtime_seconds"],
                "totalRuntime": log["total_runtime_seconds"],
                "llmGenerationTime": log["llm_generation_time_seconds"],
                "validationTime": log["validation_time_seconds"],
                
                # Success and accuracy
                "querySuccess": log["query_success"],
                "accuracy": log["accuracy_score"],
                "efficiencyScore": log["efficiency_score"],
                
                # Result analysis
                "expectedResultCount": log["expected_result_count"],
                "actualResultCount": log["actual_result_count"],
                "resultCountMatch": log["result_count_match"],
                "expectedColumns": str(log["expected_columns"]),
                "actualColumns": str(log["actual_columns"]),
                "columnMatch": log["column_match"],
                
                # Error handling
                "hasError": log["has_error"],
                "errorMessage": log["error_message"] if log["error_message"] else "",
                
                # Performance indicators
                "isSlowQuery": log["total_runtime_seconds"] > 5.0,
                "isFastQuery": log["total_runtime_seconds"] < 1.0,
                "isHighCompression": log["compression_ratio"] > 0.7,
                "isLowCompression": log["compression_ratio"] < 0.3
            })
        
        # Save structured query data
        query_data_file = self.output_dir / "query_data.json"
        with open(query_data_file, 'w') as f:
            json.dump(query_data, f, indent=2)
        
        # Create CSV exports for easy analysis
        self.create_csv_exports(query_data)
    
    def create_csv_exports(self, query_data: List[Dict]):
        """Create CSV exports for easy analysis in Excel, pandas, etc."""
        
        # Create query data CSV
        query_csv_file = self.output_dir / "query_data.csv"
        if query_data:
            import csv
            with open(query_csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=query_data[0].keys())
                writer.writeheader()
                writer.writerows(query_data)
        
        print(f"   - CSV export: query_data.csv")
        
        # Create specialized query-wise CSV for easy analysis
        self.create_query_wise_csv(query_data)
    
    def create_query_wise_csv(self, query_data: List[Dict]):
        """Create a specialized query-wise CSV file optimized for query analysis"""
        
        # Create a more focused query-wise CSV
        query_wise_csv_file = self.output_dir / "queries_analysis.csv"
        
        if query_data:
            import csv
            
            # Define the most important columns for query analysis
            query_wise_columns = [
                # Core identification
                "queryId", "executionId", "timestamp",
                
                # Schema and method
                "schemaName", "schemaCompressionMethod",
                
                # Query content
                "question", "goldSql", "generatedSql",
                
                # Performance metrics
                "querySuccess", "accuracy", "totalRuntime", 
                "queryExecutionRuntime", "schemaCompressionRuntime",
                "llmGenerationTime", "validationTime",
                
                # Compression metrics
                "schemaSizeInByte", "compressedSchemaSizeInByte", 
                "compressionRatio", "sizeReductionBytes", "sizeReductionPercentage",
                "schemaCompressionSuccess",
                
                # Result analysis
                "expectedResultCount", "actualResultCount", "resultCountMatch",
                "expectedColumns", "actualColumns", "columnMatch",
                
                # Performance indicators
                "isSlowQuery", "isFastQuery", "isHighCompression", "isLowCompression",
                "efficiencyScore",
                
                # Error handling
                "hasError", "errorMessage"
            ]
            
            with open(query_wise_csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=query_wise_columns)
                writer.writeheader()
                
                # Write only the specified columns
                for record in query_data:
                    filtered_record = {col: record.get(col, "") for col in query_wise_columns}
                    writer.writerow(filtered_record)
        
        print(f"   - Query-wise CSV: queries_analysis.csv")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from logged data"""
        
        if not self.detailed_logs:
            return {"error": "No data logged yet"}
        
        # Calculate statistics
        total_queries = len(self.detailed_logs)
        successful_queries = sum(1 for log in self.detailed_logs if log["query_success"])
        failed_queries = total_queries - successful_queries
        
        # Group by method
        method_stats = {}
        for log in self.detailed_logs:
            method = log["schema_compression_method"]
            if method not in method_stats:
                method_stats[method] = {
                    "total_queries": 0,
                    "successful_queries": 0,
                    "failed_queries": 0,
                    "avg_execution_time": 0,
                    "avg_compression_time": 0,
                    "avg_compression_ratio": 0,
                    "total_execution_time": 0,
                    "total_compression_time": 0
                }
            
            method_stats[method]["total_queries"] += 1
            if log["query_success"]:
                method_stats[method]["successful_queries"] += 1
            else:
                method_stats[method]["failed_queries"] += 1
            
            method_stats[method]["total_execution_time"] += log["query_execution_runtime_seconds"]
            method_stats[method]["total_compression_time"] += log["schema_compression_runtime_seconds"]
        
        # Calculate averages
        for method, stats in method_stats.items():
            if stats["total_queries"] > 0:
                stats["avg_execution_time"] = stats["total_execution_time"] / stats["total_queries"]
                stats["avg_compression_time"] = stats["total_compression_time"] / stats["total_queries"]
                stats["success_rate"] = stats["successful_queries"] / stats["total_queries"]
        
        # Group by schema
        schema_stats = {}
        for log in self.detailed_logs:
            schema = log["schema_name"]
            if schema not in schema_stats:
                schema_stats[schema] = {
                    "total_queries": 0,
                    "successful_queries": 0,
                    "methods_tested": set(),
                    "avg_compression_ratio": 0
                }
            
            schema_stats[schema]["total_queries"] += 1
            if log["query_success"]:
                schema_stats[schema]["successful_queries"] += 1
            schema_stats[schema]["methods_tested"].add(log["schema_compression_method"])
        
        # Convert sets to lists for JSON serialization
        for schema, stats in schema_stats.items():
            stats["methods_tested"] = list(stats["methods_tested"])
            if stats["total_queries"] > 0:
                stats["success_rate"] = stats["successful_queries"] / stats["total_queries"]
        
        return {
            "overall_statistics": {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "failed_queries": failed_queries,
                "overall_success_rate": successful_queries / total_queries if total_queries > 0 else 0
            },
            "method_statistics": method_stats,
            "schema_statistics": schema_stats,
            "execution_summary": self.query_summary
        }
