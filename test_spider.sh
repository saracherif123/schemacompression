#!/bin/bash

# Exit on error
set -e

# Configuration
SPIDER_DIR="benchmarks/spider/subset"
SCHEMA_JSON="benchmarks/results.json"  # Use the results.json directly
ALL_QUERIES="benchmarks/spider/queries/train_spider.json"
SUBSET_QUERIES="benchmarks/queries_subset.json"
QUERIES_JSON="$SUBSET_QUERIES"
DB_SUFFIX=".sqlite"
METHOD="simple"  # Change to 'gurobi', 'greedy', etc. as needed
AI_KEY="sk-xxxxxxx"  # <-- Set your OpenAI API key here
RESULTS_JSON="results_precision_subset_${METHOD}.json"
PERFORMANCE_RESULTS="src/sc/benchmark/results.json"

# 1. Create SQLite databases for each .sql file if not present
for sqlfile in "$SPIDER_DIR"/*.sql; do
    dbname="${sqlfile%.sql}$DB_SUFFIX"
    if [ ! -f "$dbname" ]; then
        echo "Creating database $dbname from $sqlfile ..."
        sqlite3 "$dbname" < "$sqlfile" || echo "Warning: Could not create $dbname from $sqlfile"
    fi
done

echo "All databases created for subset."

# 2. Run performance evaluation to generate results.json
PYTHONPATH=src python3 src/sc/benchmark/performance.py "$SPIDER_DIR" 180 "$PERFORMANCE_RESULTS" --noilp

echo "Performance results written to $PERFORMANCE_RESULTS."

# 3. (Optional) Extract schemas from performance results
# python3 src/sc/benchmark/extract_schemas.py
# echo "Schemas extracted to $SCHEMA_JSON."

# 4. (Removed) Check schemas file
# if [ ! -f "$SCHEMA_JSON" ]; then
#     echo "ERROR: $SCHEMA_JSON not found. Please generate it for the subset."
#     exit 1
# fi

# 5. Filter the first 200 queries for the subset
if [ -f "$ALL_QUERIES" ]; then
    echo "Filtering first 200 queries for subset..."
    SUBSET_DB_IDS=$(for f in "$SPIDER_DIR"/*.sql; do basename "$f" .sql; done)
    python3 <<EOF
import json
import os
subset_db_ids = set("""$SUBSET_DB_IDS""".split())
with open("$ALL_QUERIES") as f:
    all_queries = json.load(f)
filtered = [q for q in all_queries if q['db_id'] in subset_db_ids][:200]
with open("$SUBSET_QUERIES", 'w') as f:
    json.dump(filtered, f, indent=2)
print(f"Wrote {len(filtered)} queries for subset to $SUBSET_QUERIES")
EOF
else
    echo "ERROR: $ALL_QUERIES not found. Please provide the queries file."
    exit 1
fi

# 6. Run precision evaluation
echo "Running precision evaluation for subset, method: $METHOD"
PYTHONPATH=src python3 -m sc.benchmark.precision \
  "$SCHEMA_JSON" \
  "$SPIDER_DIR" \
  "$QUERIES_JSON" \
  200 \
  "$METHOD" \
  "$AI_KEY" \
  "$RESULTS_JSON"

echo "Done. Results in $RESULTS_JSON" 