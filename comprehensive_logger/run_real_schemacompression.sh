#!/bin/bash
# Real Schemonic Evaluation Runner with Comprehensive Per-Query Logging
# Runs the real Schemonic precision evaluation with comprehensive logging

echo "🚀 Real Schemonic Precision Evaluation with Comprehensive Per-Query Logging"
echo "=========================================================================="

# Set your OpenAI API key
# export OPENAI_API_KEY="your-api-key-here"

# Configuration for your actual Schemonic setup
SCHEMAS_FILE="../src/sc/benchmark/schemas.json"
DATA_DIR="../benchmarks/spider"
QUERIES_FILE="../src/sc/benchmark/queries.json"
QUERY_LIMIT=10  # Start small for testing
COMPRESSION_METHOD="simple"  # or greedy, gurobi, pretty
OUTPUT_FILE="real_schemacompression_results.json"
LOG_DIR="real_schemacompression_logs"

echo "📊 Configuration:"
echo "   Schemas: $SCHEMAS_FILE"
echo "   Data Directory: $DATA_DIR"
echo "   Queries: $QUERIES_FILE"
echo "   Query Limit: $QUERY_LIMIT"
echo "   Compression Method: $COMPRESSION_METHOD"
echo "   Output: $OUTPUT_FILE"
echo "   Log Directory: $LOG_DIR"
echo ""

# Check if required files exist
if [ ! -f "$SCHEMAS_FILE" ]; then
    echo "❌ Error: Schema file not found: $SCHEMAS_FILE"
    echo "   Make sure you're running from the comprehensive_logger directory"
    exit 1
fi

if [ ! -d "$DATA_DIR" ]; then
    echo "❌ Error: Data directory not found: $DATA_DIR"
    exit 1
fi

if [ ! -f "$QUERIES_FILE" ]; then
    echo "❌ Error: Queries file not found: $QUERIES_FILE"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: Please set your OpenAI API key"
    echo "   export OPENAI_API_KEY='your-actual-api-key'"
    exit 1
fi

echo "✅ All required files found"
echo "🚀 Starting real Schemonic evaluation with comprehensive logging..."
echo ""

# Run the real evaluation
python3 real_schemacompression_evaluation.py \
    "$SCHEMAS_FILE" \
    "$DATA_DIR" \
    "$QUERIES_FILE" \
    "$QUERY_LIMIT" \
    "$COMPRESSION_METHOD" \
    "$OPENAI_API_KEY" \
    "$OUTPUT_FILE" \
    --log-dir "$LOG_DIR" \
    --verbose

echo ""
echo "🎯 Real Schemonic evaluation complete!"
echo "📁 Check the following files:"
echo "   - Results: $OUTPUT_FILE"
echo "   - Query-wise CSV: $LOG_DIR/queries_analysis.csv"
echo "   - Comprehensive CSV: $LOG_DIR/query_data.csv"
echo "   - Detailed logs: $LOG_DIR/detailed_query_logs.json"
echo "   - Summary: $LOG_DIR/query_summary.json"
echo ""
echo "🔍 You can now analyze the data with:"
echo "   - Excel: Import $LOG_DIR/queries_analysis.csv"
echo "   - Pandas: df = pd.read_csv('$LOG_DIR/queries_analysis.csv')"
echo "   - SQL: SELECT schemaName, COUNT(querySuccess) FROM queries_analysis.csv GROUP BY schemaName"
echo ""
echo "🚀 Ready for larger scale evaluation!"
echo "   To run with more queries, increase QUERY_LIMIT in this script"

