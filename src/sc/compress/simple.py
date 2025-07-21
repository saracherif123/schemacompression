import argparse
import re

def strip_types_and_constraints(sql_text):
    # Pattern to match CREATE TABLE blocks (allowing for backticks, quotes, and flexible whitespace)
    table_pattern = re.compile(
        r'CREATE\s+TABLE\s+[`\"]?(\w+)[`\"]?\s*\((.*?)\)\s*;',
        re.DOTALL | re.IGNORECASE
    )
    # Pattern to match column definitions (first word is column name, allow for backticks/quotes)
    column_pattern = re.compile(r'^[`\"]?(\w+)[`\"]?\s+', re.IGNORECASE)

    output = []
    for match in table_pattern.finditer(sql_text):
        table_name = match.group(1)
        columns_block = match.group(2)
        columns = []
        # Split by commas to get all column definitions, even if multiple per line
        for part in columns_block.split(','):
            line = part.strip()
            # Skip empty lines and lines that are constraints or table-level options
            if not line or re.match(r'^(PRIMARY|FOREIGN|CONSTRAINT|UNIQUE|CHECK|KEY|\))', line, re.IGNORECASE):
                continue
            col_match = column_pattern.match(line)
            if col_match:
                columns.append(col_match.group(1))
        # Format output: table_name: col1, col2, col3
        output.append(f'{table_name}: {", ".join(columns)}\n')
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Strip types and constraints from SQL schema.')
    parser.add_argument('input', type=str, help='Input SQL schema file')
    parser.add_argument('output', type=str, help='Output file (names only)')
    args = parser.parse_args()

    with open(args.input) as infile:
        sql_text = infile.read()
    result = strip_types_and_constraints(sql_text)
    with open(args.output, 'w') as outfile:
        outfile.write(result)

if __name__ == '__main__':
    main() 