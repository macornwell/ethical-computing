#!/usr/bin/env python3
"""
Script to generate scripture vectors from initial JSON file
"""

import os
import json
import sys
from pathlib import Path

# Add the parent directory to the Python path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent.parent
sys.path.append(str(project_root))

from src.trust_chain.libs.scripture_validation import generate_scripture_vectors

def main():
    """Main function to generate scripture vectors"""
    
    # Paths
    input_path = Path(__file__).parent.parent / "data" / "scripture_vectors_initial.json"
    output_path = Path(__file__).parent.parent / "data" / "scripture_vectors.json"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Loading scripture data from {input_path}...")
    
    # Load initial scripture data
    try:
        with open(input_path, 'r') as f:
            scripture_data = json.load(f)
    except Exception as e:
        print(f"Error loading scripture data: {e}")
        return 1
    
    # Extract just the references and texts (without empty vectors)
    scripture_texts = {ref: data["text"] for ref, data in scripture_data.items()}
    
    print(f"Generating vectors for {len(scripture_texts)} scripture passages...")
    
    # Generate vectors
    scripture_vectors = generate_scripture_vectors(scripture_texts, output_path)
    
    print(f"Successfully generated vectors for {len(scripture_vectors)} scripture passages")
    print(f"Vectors saved to {output_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 