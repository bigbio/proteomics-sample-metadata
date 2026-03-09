#!/bin/bash
# Add development version banner to all documentation pages
# Usage: ./add-dev-banner.sh <output_dir>

set -e

OUTPUT_DIR="${1:-docs}"

echo "Adding dev banner to all HTML pages in: $OUTPUT_DIR"

# Use Python for reliable cross-platform HTML injection
python3 -c "
import os, re

output_dir = '$OUTPUT_DIR'
banner = '<div class=\"dev-banner\">&#9888;&#65039; Development Version - This documentation is from the dev branch and may contain unreleased changes. <a href=\"/\">View stable version</a></div>'

for root, dirs, files in os.walk(output_dir):
    for f in files:
        if not f.endswith('.html'):
            continue
        path = os.path.join(root, f)
        with open(path, 'r') as fh:
            content = fh.read()
        if 'dev-banner' in content:
            continue
        content = re.sub(r'(<body[^>]*>)', r'\1' + banner, content)
        with open(path, 'w') as fh:
            fh.write(content)
"

# Append dev banner CSS to stylesheet (only once)
if ! grep -q "dev-banner" "$OUTPUT_DIR/css/style.css" 2>/dev/null; then
    cat >> "$OUTPUT_DIR/css/style.css" << 'EOF'

/* Dev banner */
.dev-banner {
  background: #fef3c7;
  color: #92400e;
  padding: 0.75rem 1rem;
  text-align: center;
  font-size: 0.9rem;
  border-bottom: 1px solid #fcd34d;
}
.dev-banner a {
  color: #92400e;
  font-weight: 600;
}
EOF
fi

echo "Dev banner added to all pages successfully!"
