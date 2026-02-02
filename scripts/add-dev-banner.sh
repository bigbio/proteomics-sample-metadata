#!/bin/bash
# Add development version banner to documentation
# Usage: ./add-dev-banner.sh <output_dir>

set -e

OUTPUT_DIR="${1:-docs}"

echo "Adding dev banner to: $OUTPUT_DIR"

# Add banner HTML to index.html
sed -i.bak 's/<body>/<body><div class="dev-banner">⚠️ Development Version - This documentation is from the dev branch and may contain unreleased changes. <a href="\/">View stable version<\/a><\/div>/' "$OUTPUT_DIR/index.html"
rm -f "$OUTPUT_DIR/index.html.bak"

# Append dev banner CSS to stylesheet
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

echo "Dev banner added successfully!"
