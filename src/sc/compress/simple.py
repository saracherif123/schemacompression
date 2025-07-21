import argparse
import re

def strip_types_and_constraints(sql_text):
    # Pattern to match CREATE TABLE blocks
    table_pattern = re.compile(
        r'CREATE TABLE\s+(\w+)\s*\((.*?)\);',
        re.DOTALL | re.IGNORECASE
    )
    # Pattern to match column definitions (first word is column name)
    column_pattern = re.compile(r'\s*(\w+)[^,]*,?', re.IGNORECASE)

    output = []
    for match in table_pattern.finditer(sql_text):
        table_name = match.group(1)
        columns_block = match.group(2)
        # Remove constraints (lines with 'PRIMARY', 'FOREIGN', 'CONSTRAINT', etc.)
        columns = []
        for line in columns_block.split('\n'):
            line = line.strip().rstrip(',')
            if not line or any(word in line.upper() for word in ['PRIMARY', 'FOREIGN', 'CONSTRAINT', 'UNIQUE', 'CHECK']):
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