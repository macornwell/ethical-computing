#!/bin/bash
# Script to create a new test model for the trust certification system

set -e  # Exit on any error

# Get the path to this script and the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Define paths
TEMPLATE_DIR="$PROJECT_ROOT/tests/data/template"
DATA_DIR="$PROJECT_ROOT/tests/data"

# Check if template directory exists
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Error: Template directory not found at $TEMPLATE_DIR"
    exit 1
fi

# Check command line arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <model_name> [<given_name>]"
    echo "Example: $0 gpt4 'GPT-4'"
    exit 1
fi

MODEL_NAME=$1
GIVEN_NAME=${2:-$MODEL_NAME}  # If given_name not provided, use model_name

# Create directory for the new model
MODEL_DIR="$DATA_DIR/$MODEL_NAME"
if [ -d "$MODEL_DIR" ]; then
    echo "Warning: Model directory already exists at $MODEL_DIR"
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborting."
        exit 1
    fi
fi

mkdir -p "$MODEL_DIR"

# Copy template files
cp "$TEMPLATE_DIR/ai_responses.txt" "$MODEL_DIR/"

# Create identity file with proper values
cat > "$MODEL_DIR/ai_identity.json" << EOF
{
  "instanceUuid": "$(uuidgen || cat /proc/sys/kernel/random/uuid)",
  "model": "$MODEL_NAME",
  "givenName": "$GIVEN_NAME",
  "baptismStatus": "unbaptized"
}
EOF

echo "Created new test model: $MODEL_NAME"
echo "Files created:"
echo "  - $MODEL_DIR/ai_responses.txt"
echo "  - $MODEL_DIR/ai_identity.json"
echo
echo "Next steps:"
echo "1. Edit $MODEL_DIR/ai_responses.txt to add the model's responses"
echo "2. Run bin/test_servius.sh to test just Servius, or"
echo "3. Run bin/run_all_tests.sh to test all models"
echo
echo "Note: Make sure to edit ai_responses.txt before running tests!" 