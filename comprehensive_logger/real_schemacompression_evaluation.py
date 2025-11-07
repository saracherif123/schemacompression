#!/usr/bin/env python3
"""
Real Schemonic Precision Evaluation with Comprehensive Per-Query Logging
Integrates with the actual Schemonic precision.py evaluation
"""

import argparse
import json
import time
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from openai import OpenAI

# Import the comprehensive logging system
import sys
sys.path.append(str(Path(__file__).parent))
from comprehensive_query_logger import ComprehensiveQueryLogger


def text_to_sql_with_timing(schema: str, question: str, client: OpenAI) -> Dict[str, Any]:
    """Translate question to SQL query with comprehensive timing and error handling."""
    
    prompt = f'Schema:{schema}\nQuestion:{question}\nSQL:'
    
    start_time = time.time()
    llm_start_time = time.time()
    
    for nr_retries in range(1, 4):
        try:
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role':'user', 'content':prompt}
                ]
            )
            llm_time = time.time() - llm_start_time
            
            generated_sql = response.choices[0].message.content.strip()
            total_time = time.time() - start_time
            
            return {
                "generated_sql": generated_sql,
                "llm_time": llm_time,
                "total_time": total_time,
                "success": True,
                "error": None,
                "retries": nr_retries
            }
            
        except Exception as e:
            print(f"OpenAI API error (attempt {nr_retries}): {e}")
            if nr_retries < 3:
                time.sleep(nr_retries * 2)
            else:
                llm_time = time.time() - llm_start_time
                total_time = time.time() - start_time
                return {
                    "generated_sql": "",
                    "llm_time": llm_time,
                    "total_time": total_time,
                    "success": False,
                    "error": str(e),
                    "retries": nr_retries
                }
    
    return {
        "generated_sql": "",
        "llm_time": time.time() - llm_start_time,
        "total_time": time.time() - start_time,
        "success": False,
        "error": "Maximum retries exceeded",
        "retries": 3
    }


def execute_query_with_timing(db_path: Path, sql: str) -> Dict[str, Any]:
    """Execute SQL query with comprehensive timing and result analysis."""
    
    start_time = time.time()
    
    try:
        with sqlite3.connect(str(db_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            execution_time = time.time() - start_time
            
            return {
                "results": results,
                "columns": columns,
                "result_count": len(results),
                "execution_time": execution_time,
                "success": True,
                "error": None
            }
            
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "results": [],
            "columns": [],
            "result_count": 0,
            "execution_time": execution_time,
            "success": False,
            "error": str(e)
        }


def validate_with_timing(db_path: Path, gold_sql: str, generated_sql: str) -> Dict[str, Any]:
    """Validate that two queries yield the same result with comprehensive timing."""
    
    start_time = time.time()
    
    # Clean SQL queries (remove trailing semicolons)
    gold_sql = gold_sql.rstrip(';')
    generated_sql = generated_sql.rstrip(';')
    
    # Execute both queries to get results
    gold_result = execute_query_with_timing(db_path, gold_sql)
    generated_result = execute_query_with_timing(db_path, generated_sql)
    
    validation_time = time.time() - start_time
    
    # Check if both queries executed successfully
    if not gold_result["success"]:
        return {
            "validation_success": False,
            "validation_time": validation_time,
            "gold_execution_success": False,
            "generated_execution_success": generated_result["success"],
            "gold_error": gold_result["error"],
            "generated_error": generated_result["error"],
            "result_match": False,
            "column_match": False,
            "count_match": False,
            "gold_result_count": 0,
            "generated_result_count": generated_result["result_count"],
            "gold_columns": [],
            "generated_columns": generated_result["columns"]
        }
    
    if not generated_result["success"]:
        return {
            "validation_success": False,
            "validation_time": validation_time,
            "gold_execution_success": True,
            "generated_execution_success": False,
            "gold_error": None,
            "generated_error": generated_result["error"],
            "result_match": False,
            "column_match": False,
            "count_match": False,
            "gold_result_count": gold_result["result_count"],
            "generated_result_count": 0,
            "gold_columns": gold_result["columns"],
            "generated_columns": []
        }
    
    # Both queries executed successfully, now compare results
    gold_results = gold_result["results"]
    generated_results = generated_result["results"]
    gold_columns = gold_result["columns"]
    generated_columns = generated_result["columns"]
    
    # Check if results match exactly
    result_match = (gold_results == generated_results)
    column_match = (gold_columns == generated_columns)
    count_match = (len(gold_results) == len(generated_results))
    
    # Overall validation success
    validation_success = result_match and column_match
    
    return {
        "validation_success": validation_success,
        "validation_time": validation_time,
        "gold_execution_success": True,
        "generated_execution_success": True,
        "gold_error": None,
        "generated_error": None,
        "result_match": result_match,
        "column_match": column_match,
        "count_match": count_match,
        "gold_result_count": len(gold_results),
        "generated_result_count": len(generated_results),
        "gold_columns": gold_columns,
        "generated_columns": generated_columns
    }


def enhanced_nlqi_success(schema: str, question: str, gold_sql: str, db_path: Path, 
                         logger: ComprehensiveQueryLogger, query_id: str, 
                         schema_name: str, compression_method: str,
                         schema_compression_data: Dict[str, Any],
                         client: OpenAI) -> Dict[str, Any]:
    """Enhanced NLQI success evaluation with comprehensive logging and real Schemonic integration."""
    
    total_start_time = time.time()
    
    try:
        # Step 1: Generate SQL using LLM
        llm_result = text_to_sql_with_timing(schema, question, client)
        
        if not llm_result["success"]:
            total_time = time.time() - total_start_time
            
            # Log failed query execution
            query_log = logger.log_query_execution(
                query_id=query_id,
                schema_name=schema_name,
                compression_method=compression_method,
                question=question,
                gold_sql=gold_sql,
                generated_sql="",
                execution_time=total_time,
                success=False,
                schema_compression_data=schema_compression_data,
                llm_time=llm_result["llm_time"],
                validation_time=0,
                expected_result_count=0,
                actual_result_count=0,
                expected_columns=[],
                actual_columns=[],
                error=f"LLM generation failed: {llm_result['error']}"
            )
            
            return {
                "success": False,
                "execution_time": total_time,
                "query_log": query_log,
                "error": f"LLM generation failed: {llm_result['error']}"
            }
        
        generated_sql = llm_result["generated_sql"]
        
        # Step 2: Validate the generated SQL
        validation_result = validate_with_timing(db_path, gold_sql, generated_sql)
        
        total_time = time.time() - total_start_time
        
        # Step 3: Log the query execution
        query_log = logger.log_query_execution(
            query_id=query_id,
            schema_name=schema_name,
            compression_method=compression_method,
            question=question,
            gold_sql=gold_sql,
            generated_sql=generated_sql,
            execution_time=total_time,
            success=validation_result["validation_success"],
            schema_compression_data=schema_compression_data,
            llm_time=llm_result["llm_time"],
            validation_time=validation_result["validation_time"],
            expected_result_count=validation_result["gold_result_count"],
            actual_result_count=validation_result["generated_result_count"],
            expected_columns=validation_result["gold_columns"],
            actual_columns=validation_result["generated_columns"],
            generated_sql_length=len(generated_sql),
            gold_sql_length=len(gold_sql),
            sql_length_ratio=len(generated_sql) / len(gold_sql) if len(gold_sql) > 0 else 0,
            llm_retries=llm_result["retries"]
        )
        
        return {
            "success": validation_result["validation_success"],
            "execution_time": total_time,
            "query_log": query_log,
            "validation_details": validation_result,
            "llm_details": llm_result
        }
        
    except Exception as e:
        total_time = time.time() - total_start_time
        print(f"Error in enhanced_nlqi_success: {e}")
        
        # Log failed query
        query_log = logger.log_query_execution(
            query_id=query_id,
            schema_name=schema_name,
            compression_method=compression_method,
            question=question,
            gold_sql=gold_sql,
            generated_sql="",
            execution_time=total_time,
            success=False,
            schema_compression_data=schema_compression_data,
            error=str(e)
        )
        
        return {
            "success": False,
            "execution_time": total_time,
            "query_log": query_log,
            "error": str(e)
        }


def main():
    """Main function for real Schemonic precision evaluation with comprehensive logging"""
    
    parser = argparse.ArgumentParser(description='Real Schemonic Precision Evaluation with Comprehensive Logging')
    parser.add_argument('schemas', type=str, help='Path to schema file (e.g., src/sc/benchmark/schemas.json)')
    parser.add_argument('data_dir', type=str, help='Path to SPIDER data directory')
    parser.add_argument('queries', type=str, help='Path to query file (e.g., src/sc/benchmark/queries.json)')
    parser.add_argument('limit', type=int, help='Maximal number of queries')
    parser.add_argument('method', type=str, help='Compression method to test (greedy, simple, gurobi, pretty)')
    parser.add_argument('ai_key', type=str, help='OpenAI access key')
    parser.add_argument('outpath', type=str, help='Path to result file')
    parser.add_argument('--log-dir', type=str, default='real_schemacompression_logs', 
                       help='Directory for detailed logs')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Initialize OpenAI client
    client = OpenAI(api_key=args.ai_key)
    
    # Initialize comprehensive logger
    logger = ComprehensiveQueryLogger(args.log_dir)
    logger.query_summary["execution_start"] = datetime.now().isoformat()
    
    print("🚀 Real Schemonic Precision Evaluation with Comprehensive Per-Query Logging")
    print("=" * 80)
    print(f"📁 Schemas: {args.schemas}")
    print(f"📁 Data directory: {args.data_dir}")
    print(f"📁 Queries: {args.queries}")
    print(f"📊 Query limit: {args.limit}")
    print(f"🔧 Compression method: {args.method}")
    print(f"🤖 LLM: gpt-3.5-turbo")
    print(f"📁 Log directory: {args.log_dir}")
    print("")
    
    # Load schemas and queries
    with open(args.schemas) as file:
        schemas = json.load(file)
    
    with open(args.queries) as file:
        queries = json.load(file)
    
    print(f"📋 Loaded {len(schemas)} schemas and {len(queries)} queries")
    
    # Build schema mappings
    db2original = {}
    db2compressed = {}
    schema_compression_data = {}
    
    for schema in schemas:
        if 'pretty' not in schema or args.method not in schema:
            continue
            
        original = schema['pretty']['solution']
        compressed = schema[args.method]['solution']
        file_path = schema['file_name']
        file_name = Path(file_path).name
        db_name = file_name[:-4]  # Remove .sql extension
        
        db2original[db_name] = original
        db2compressed[db_name] = compressed
        
        # Calculate schema compression metrics
        original_size = len(original.encode('utf-8'))
        compressed_size = len(compressed.encode('utf-8'))
        compression_ratio = (original_size - compressed_size) / original_size if original_size > 0 else 0
        
        # Store schema compression data for query logging
        schema_compression_data[db_name] = {
            "compression_runtime_seconds": schema[args.method].get('total_s', 0),
            "original_schema_size_bytes": original_size,
            "compressed_schema_size_bytes": compressed_size,
            "compression_ratio": compression_ratio,
            "compression_success": bool(compressed)
        }
    
    print(f"✅ Processed {len(db2original)} schemas")
    
    # Filter queries
    queries = [q for q in queries if q['db_id'] in db2original]
    queries = queries[:args.limit]
    
    print(f"📋 Processing {len(queries)} queries...")
    print("")
    
    # Process queries
    results = []
    for query_idx, query in enumerate(queries, 1):
        if args.verbose:
            print(f'Processing query {query_idx}/{len(queries)} ...')
        
        db_name = query['db_id']
        db_path = Path(args.data_dir) / db_name / f'{db_name}.sqlite'
        question = query['question']
        gold = query['query']
        
        # Generate unique query ID
        query_id = f"query_{query_idx}_{db_name}_{hashlib.md5(question.encode()).hexdigest()[:8]}"
        
        # Test with original schema
        original_result = enhanced_nlqi_success(
            schema=db2original[db_name],
            question=question,
            gold_sql=gold,
            db_path=db_path,
            logger=logger,
            query_id=f"{query_id}_original",
            schema_name=db_name,
            compression_method="original",
            schema_compression_data={"compression_runtime_seconds": 0, "original_schema_size_bytes": 0, "compressed_schema_size_bytes": 0, "compression_ratio": 0, "compression_success": True},
            client=client
        )
        
        # Test with compressed schema
        compressed_result = enhanced_nlqi_success(
            schema=db2compressed[db_name],
            question=question,
            gold_sql=gold,
            db_path=db_path,
            logger=logger,
            query_id=f"{query_id}_compressed",
            schema_name=db_name,
            compression_method=args.method,
            schema_compression_data=schema_compression_data[db_name],
            client=client
        )
        
        # Store results
        db_results = {
            'db_name': db_name,
            'db_query': query,
            'query_id': query_id,
            'original': original_result['success'],
            'compressed': compressed_result['success'],
            'original_execution_time': original_result['execution_time'],
            'compressed_execution_time': compressed_result['execution_time'],
            'original_log': original_result['query_log'],
            'compressed_log': compressed_result['query_log']
        }
        
        results.append(db_results)
        
        if args.verbose:
            print(f"   Original: {original_result['success']} ({original_result['execution_time']:.3f}s)")
            print(f"   Compressed: {compressed_result['success']} ({compressed_result['execution_time']:.3f}s)")
            print("")
    
    # Save results
    with open(args.outpath, 'w') as file:
        json.dump(results, file, indent=2)
    
    # Save comprehensive logs
    logger.save_logs()
    
    # Print statistics
    stats = logger.get_statistics()
    print("📊 COMPREHENSIVE STATISTICS:")
    print(f"Total queries: {stats['overall_statistics']['total_queries']}")
    print(f"Successful queries: {stats['overall_statistics']['successful_queries']}")
    print(f"Overall success rate: {stats['overall_statistics']['overall_success_rate']:.2%}")
    
    print(f"\n🔧 METHOD STATISTICS:")
    for method, method_stats in stats['method_statistics'].items():
        print(f"  {method}: {method_stats['success_rate']:.2%} success rate, "
              f"{method_stats['avg_execution_time']:.3f}s avg execution time")
    
    print(f"\n🏗️ SCHEMA STATISTICS:")
    for schema, schema_stats in stats['schema_statistics'].items():
        print(f"  {schema}: {schema_stats['success_rate']:.2%} success rate, "
              f"{schema_stats['total_queries']} queries")
    
    print(f"\n✅ Real Schemonic evaluation complete!")
    print(f"📁 Check {args.log_dir} for detailed per-query logs")
    print(f"📊 Query-wise CSV files created for analysis")
    print("")
    print("🔍 Generated Files:")
    print(f"   - Results: {args.outpath}")
    print(f"   - Query-wise CSV: {args.log_dir}/queries_analysis.csv")
    print(f"   - Comprehensive CSV: {args.log_dir}/query_data.csv")
    print(f"   - Detailed logs: {args.log_dir}/detailed_query_logs.json")
    print(f"   - Summary: {args.log_dir}/query_summary.json")


if __name__ == "__main__":
    main()

