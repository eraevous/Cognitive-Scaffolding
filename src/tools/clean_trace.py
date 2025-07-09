import re
import sys

input_path = sys.argv[1]
output_path = sys.argv[2]

print(f"Opening input: {input_path}")
print(f"Saving to output: {output_path}")

try:
    with open(input_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
except UnicodeDecodeError:
    print("⚠️ UTF-8 failed, trying latin1...")
    with open(input_path, 'r', encoding='latin1') as infile:
        lines = infile.readlines()

print(f"Read {len(lines)} lines.")

buffer = []
output_lines = 0

with open(output_path, 'w', encoding='utf-8') as outfile:
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip code fences and pure shell prompts
        if not stripped or stripped.startswith('```'):
            continue
        if re.match(r'^(root@.+?#|\$ )', stripped):
            continue

        # Capture dialogue chunks (e.g., User: or Assistant:)
        if re.match(r'^\w+:', stripped):
            if buffer:
                outfile.write('\n'.join(buffer).strip() + '\n\n')
                output_lines += 1
                buffer = []
            buffer.append(stripped)
        else:
            buffer.append(stripped)

    if buffer:
        outfile.write('\n'.join(buffer).strip() + '\n')
        output_lines += 1

print(f"✅ Output written: {output_lines} entries.")
 