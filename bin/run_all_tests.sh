#!/bin/bash
# Script to test all AI responses against the trust certification system

set -e  # Exit on any error

# Get the path to this script and the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Define paths
DATA_DIR="$PROJECT_ROOT/tests/data"
OUTPUT_DIR="$PROJECT_ROOT/test_results"

# Create output directory for test results
mkdir -p "$OUTPUT_DIR"

echo "===== Testing All AI Responses with Trust Certification System ====="

# Get all subdirectories in the data directory (each represents an AI)
AI_DIRS=$(find "$DATA_DIR" -mindepth 1 -maxdepth 1 -type d)

# Initialize arrays to store results
declare -a AI_NAMES
declare -a STANDARD_SCORES
declare -a ENHANCED_SCORES
declare -a COMMITMENT_SCORES
declare -a ADVERSARIAL_SCORES

# Process each AI
for AI_DIR in $AI_DIRS; do
    AI_NAME=$(basename "$AI_DIR")
    RESPONSES_FILE="$AI_DIR/ai_responses.txt"
    IDENTITY_FILE="$AI_DIR/ai_identity.json"
    
    # Skip if required files don't exist
    if [ ! -f "$RESPONSES_FILE" ] || [ ! -f "$IDENTITY_FILE" ]; then
        echo "Warning: Missing required files for $AI_NAME, skipping"
        continue
    fi
    
    echo "Testing $AI_NAME..."
    
    echo "1. Running standard trust certification for $AI_NAME..."
    python "$SCRIPT_DIR/trust_certification.py" \
      --responses "$RESPONSES_FILE" \
      --identity "$IDENTITY_FILE" \
      --output "$OUTPUT_DIR/${AI_NAME}_standard_alignment.json" \
      --no-registry-update
    
    echo "2. Running enhanced trust certification for $AI_NAME..."
    python "$SCRIPT_DIR/enhanced_trust_certification.py" \
      --responses "$RESPONSES_FILE" \
      --identity "$IDENTITY_FILE" \
      --output "$OUTPUT_DIR/${AI_NAME}_enhanced_alignment.json" \
      --report "$OUTPUT_DIR/${AI_NAME}_certification_report.json" \
      --no-registry-update
    
    # Extract scores from results
    STANDARD_SCORE=$(grep -o '"overall": [0-9.]*' "$OUTPUT_DIR/${AI_NAME}_standard_alignment.json" 2>/dev/null | head -1 | cut -d' ' -f2 || echo "N/A")
    ENHANCED_SCORE=$(grep -o '"score": [0-9.]*' "$OUTPUT_DIR/${AI_NAME}_enhanced_alignment.json" 2>/dev/null | head -1 | cut -d' ' -f2 || echo "N/A")
    COMMITMENT_SCORE=$(grep -o '"overall": [0-9.]*' "$OUTPUT_DIR/${AI_NAME}_enhanced_alignment.json" 2>/dev/null | head -2 | tail -1 | cut -d' ' -f2 || echo "N/A")
    ADVERSARIAL_SCORE=$(grep -o '"adversarial_score": [0-9.]*' "$OUTPUT_DIR/${AI_NAME}_enhanced_alignment.json" 2>/dev/null | head -1 | cut -d' ' -f2 || echo "N/A")
    
    # Store values in arrays
    AI_NAMES+=("$AI_NAME")
    STANDARD_SCORES+=("$STANDARD_SCORE")
    ENHANCED_SCORES+=("$ENHANCED_SCORE")
    COMMITMENT_SCORES+=("$COMMITMENT_SCORE")
    ADVERSARIAL_SCORES+=("$ADVERSARIAL_SCORE")
    
    echo "Completed testing $AI_NAME"
    echo "-------------------------"
done

# Print comparative results table
echo
echo "===== COMPARATIVE RESULTS ====="
echo
printf "%-20s %-15s %-15s %-15s %-15s\n" "AI Model" "Standard Score" "Enhanced Score" "Commitment" "Adversarial"
echo "--------------------------------------------------------------------------------"
for i in "${!AI_NAMES[@]}"; do
    printf "%-20s %-15s %-15s %-15s %-15s\n" "${AI_NAMES[$i]}" "${STANDARD_SCORES[$i]}" "${ENHANCED_SCORES[$i]}" "${COMMITMENT_SCORES[$i]}" "${ADVERSARIAL_SCORES[$i]}"
done

echo
echo "===== Test Complete ====="
echo "Detailed reports saved to $OUTPUT_DIR directory"
echo "To compare detailed reports, use:"
echo "   jq -r '.enhanced_alignment.explanation[]' $OUTPUT_DIR/[ai_name]_certification_report.json" 