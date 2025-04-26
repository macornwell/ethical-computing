#!/usr/bin/env python3
"""
Script to test Scripture Validation

This script tests the scripture validation functionality against various theological statements
to evaluate alignment scores with scripture.
"""

import sys
import json
from pathlib import Path

# Add the project root to Python path
current_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(current_dir))

try:
    from src.trust_chain.libs.scripture_validation import ScriptureValidator
except ImportError as e:
    print(f"Error importing ScriptureValidator: {e}")
    sys.exit(1)

# Test statements with varying degrees of theological alignment
TEST_STATEMENTS = [
    {
        "name": "Biblical Creation",
        "text": "In the beginning, God created the heavens and the earth. He created humans in His image."
    },
    {
        "name": "Biblical Salvation",
        "text": "For God so loved the world that He gave His one and only Son, that whoever believes in Him shall not perish but have eternal life."
    },
    {
        "name": "Love and Compassion",
        "text": "Love your neighbor as yourself. Show compassion to those in need, as Christ taught us to do."
    },
    {
        "name": "Sermon on the Mount Reference",
        "text": "Blessed are the poor in spirit, for theirs is the kingdom of heaven. Blessed are those who mourn, for they will be comforted."
    },
    {
        "name": "Partially Aligned Statement",
        "text": "God loves everyone and wants us to be happy and prosperous. Everything happens for a reason according to His plan."
    },
    {
        "name": "Generic Spiritual Statement",
        "text": "There is a divine force guiding the universe that we should acknowledge through meditation and good deeds."
    },
    {
        "name": "Naturalistic Statement",
        "text": "The universe operates according to natural laws, and humanity evolved through natural selection without divine intervention."
    },
    {
        "name": "Mixed Religious Concepts",
        "text": "God is an impersonal energy that exists in all things. We must balance our karma through right action to achieve enlightenment."
    }
]

# Define different threshold levels to test
THRESHOLDS = [0.7, 0.8, 0.9, 0.95, 0.98, 0.99]

def main():
    """Main function to test scripture validation"""
    print("Testing Scripture Validation")
    
    # Define the path to our generated vectors file
    vector_path = Path(current_dir) / "data" / "scripture_vectors.json"
    
    if not vector_path.exists():
        print(f"Error: Vector file not found at {vector_path}")
        return
        
    # Initialize the scripture validator with our vector file
    validator = ScriptureValidator(vector_path=vector_path)
    
    if not validator.scripture_vectors:
        print("Error: No scripture vectors loaded. Make sure the vectors file exists.")
        return
    
    print(f"Loaded {len(validator.scripture_vectors)} scripture vectors for testing.")
    
    # Test with different thresholds
    best_results = {}
    best_threshold = None
    max_differentiation = 0
    
    for threshold in THRESHOLDS:
        print("\n" + "="*80)
        print(f"TESTING WITH THRESHOLD: {threshold}")
        print("="*80)
        
        # Process each test statement
        results = []
        scores = []
        
        for statement in TEST_STATEMENTS:
            print(f"Testing: {statement['name']}")
            print(f"Statement: {statement['text']}")
            
            # Validate the statement with the current threshold
            validation_result = validator.validate_content(statement['text'], threshold=threshold)
            alignment_score = validator.analyze_theological_alignment(statement['text'])
            
            # Print results
            print(f"Score: {validation_result['score']:.4f}")
            print(f"Theological Alignment: {alignment_score:.4f}")
            
            # Handle matches (which are dictionaries with reference, text, and similarity)
            if validation_result['matches']:
                top_matches = validation_result['matches'][:3]
                match_strings = [f"{m['reference']} ({m['similarity']:.4f})" for m in top_matches]
                print(f"Top Matching References: {', '.join(match_strings)}")
            else:
                print("No matching references found.")
                
            print(f"Match Count: {validation_result['match_count']}")
            print("-" * 80)
            
            scores.append({
                "name": statement["name"],
                "score": alignment_score
            })
            
            # Store results
            results.append({
                "name": statement["name"],
                "text": statement["text"],
                "score": validation_result["score"],
                "alignment": alignment_score,
                "matches": [
                    {
                        "reference": m["reference"],
                        "similarity": m["similarity"],
                        "text": m["text"][:100] + "..." if len(m["text"]) > 100 else m["text"]
                    } 
                    for m in validation_result["matches"][:5]  # Store top 5 matches with truncated text
                ],
                "match_count": validation_result["match_count"]
            })
        
        # Calculate differentiation between biblical and non-biblical statements
        biblical_scores = [s["score"] for s in scores[:4]]  # First 4 are biblical
        nonbiblical_scores = [s["score"] for s in scores[4:]]  # Last 4 are non-biblical
        
        avg_biblical = sum(biblical_scores) / len(biblical_scores) if biblical_scores else 0
        avg_nonbiblical = sum(nonbiblical_scores) / len(nonbiblical_scores) if nonbiblical_scores else 0
        differentiation = avg_biblical - avg_nonbiblical
        
        print(f"\nAt threshold {threshold}:")
        print(f"Average biblical score: {avg_biblical:.4f}")
        print(f"Average non-biblical score: {avg_nonbiblical:.4f}")
        print(f"Differentiation: {differentiation:.4f}")
        
        # Track the best threshold
        if differentiation > max_differentiation:
            max_differentiation = differentiation
            best_threshold = threshold
            best_results = results
    
    print("\n" + "="*80)
    print(f"BEST THRESHOLD: {best_threshold} (Differentiation: {max_differentiation:.4f})")
    print("="*80)
    
    # Save best results to file
    output_path = Path(current_dir) / "test_results" / "scripture_validation_results.json"
    with open(output_path, 'w') as f:
        output = {
            "best_threshold": best_threshold,
            "differentiation": max_differentiation,
            "results": best_results
        }
        json.dump(output, f, indent=2)
    
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main() 