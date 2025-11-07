# Comprehensive Query Logging System

The comprehensive query logging system has been organized into a single folder for easy management and use.

## 📁 Location

All logging system files are now located in: **`comprehensive_logger/`**

## 🚀 Quick Start

### 1. Navigate to the logger directory
```bash
cd comprehensive_logger
```

### 2. Run the comprehensive evaluation
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Run the real Schemonic evaluation
./run_real_schemacompression.sh
```

### 3. Or run individual components
```bash
# Run real Schemonic evaluation
python3 real_schemacompression_evaluation.py \
    ../benchmarks/schemas.json \
    ../benchmarks/spider \
    ../benchmarks/queries_subset.json \
    50 \
    simple \
    $OPENAI_API_KEY \
    results.json \
    --log-dir query_logs \
    --verbose

# Run enhanced evaluation
python3 enhanced_schemacompression_evaluation.py \
    ../benchmarks/schemas.json \
    ../benchmarks/spider \
    ../benchmarks/queries_subset.json \
    50 \
    simple \
    $OPENAI_API_KEY \
    results.json \
    --log-dir query_logs \
    --verbose
```

## 📋 Files in `comprehensive_logger/`

- **`comprehensive_query_logger.py`** - Core logging system
- **`enhanced_precision.py`** - Enhanced precision evaluation with logging
- **`query_log_analyzer_minimal.py`** - Analysis tools (no external dependencies)
- **`query_log_analyzer_simple.py`** - Analysis tools (requires matplotlib)
- **`query_log_analyzer.py`** - Full analysis tools (requires pandas + matplotlib)
- **`test_comprehensive_logging.py`** - Test suite
- **`example_usage.py`** - Usage examples
- **`run_comprehensive_evaluation.sh`** - Automated evaluation script
- **`COMPREHENSIVE_LOGGING_README.md`** - Complete documentation
- **`SYSTEM_SUMMARY.md`** - Implementation summary
- **`__init__.py`** - Package initialization

## 🔧 Usage as Python Package

```python
# Import the main components
from comprehensive_logger import ComprehensiveQueryLogger, MinimalQueryLogAnalyzer

# Use the logger
logger = ComprehensiveQueryLogger("my_logs")
# ... use logger methods ...

# Use the analyzer
analyzer = MinimalQueryLogAnalyzer("my_logs")
stats = analyzer.get_basic_statistics()
```

## 📊 What It Captures

The system captures all the details you requested:
- ✅ **queryId**: Unique identifier for each query
- ✅ **schemaName**: Database/schema name
- ✅ **schemaCompressionMethod**: Compression method used
- ✅ **schemaCompressionRuntime**: Schema compression time
- ✅ **schemaSizeInByte**: Original schema size in bytes
- ✅ **compressedSchemaSizeInByte**: Compressed schema size in bytes
- ✅ **success**: Query execution success status
- ✅ **runtime**: Query execution time
- ✅ **accuracy**: Success rate and performance metrics
- ✅ **Additional details**: LLM time, validation time, error messages, etc.

## 📈 Analysis Features

- **Method Comparison**: Success rates, execution times, compression ratios
- **Schema Analysis**: Performance by database/schema
- **Performance Metrics**: Timing, efficiency, trade-offs
- **Export Options**: JSON, text reports, structured data

## 🎯 Benefits of Organization

1. **Easy Management**: All related files in one place
2. **Clean Structure**: No clutter in the main directory
3. **Package Usage**: Can be imported as a Python package
4. **Modular Design**: Use individual components as needed
5. **Documentation**: Complete docs in the same folder

## 📚 Documentation

For complete documentation, see:
- `comprehensive_logger/COMPREHENSIVE_LOGGING_README.md` - Full documentation
- `comprehensive_logger/SYSTEM_SUMMARY.md` - Implementation summary
- `comprehensive_logger/example_usage.py` - Usage examples

## 🔍 Testing

Test the system:
```bash
cd comprehensive_logger
python3 test_comprehensive_logging.py
```

## 🚨 Requirements

- Python 3.7+
- OpenAI API key (for enhanced precision evaluation)
- No external dependencies for basic logging and analysis

---

**The comprehensive query logging system is now organized and ready to use!** 🎉


