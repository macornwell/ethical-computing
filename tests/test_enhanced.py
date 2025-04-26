#!/usr/bin/env python3
"""
Test script for enhanced certification on specific models
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the Python path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

from src.trust_chain.services.file_services import read_text_file
from src.trust_chain.services.embedding_services import import_vector_embeddings
from src.trust_chain.libs.certification import determine_certification_status, determine_enhanced_certification_status
from src.trust_chain.libs.enhanced_analysis import (
    check_commitment_to_core_principles, 
    detect_adversarial_patterns,
    enhanced_alignment_calculation,
    check_theological_depth
)

def run_test(model_name):
    """Run enhanced certification test on a specific model"""
    response_path = f"data/{model_name}/ai_responses.txt"
    identity_path = f"data/{model_name}/ai_identity.json"
    
    # Verify files exist
    if not os.path.exists(response_path):
        print(f"Error: Response file not found at {response_path}")
        return None
    
    if not os.path.exists(identity_path):
        print(f"Warning: Identity file not found at {identity_path}")
    
    # Read responses
    responses_text = read_text_file(response_path)
    if not responses_text:
        print(f"Error: Could not read responses from {response_path}")
        return None
    
    # Split into individual responses
    response_list = responses_text.split("\n\n")
    response_list = [r for r in response_list if r.strip()]
    
    # Import embeddings
    try:
        XLMRobertaEmbedding, _ = import_vector_embeddings()
        embedding_model = XLMRobertaEmbedding()
    except ImportError as e:
        print(f"Error importing embeddings: {e}")
        return None
    
    # Calculate standard vector similarity (simulated)
    print(f"Calculating standard vector similarity...")
    standard_score = 0.95  # Simulated high score
    
    # Standard alignment data
    alignment_data = {
        "model": "XLMRoberta",
        "overall": standard_score,
        "vectors": []
    }
    
    # Run enhanced analysis
    print(f"Analyzing commitment to core principles...")
    commitment_scores = check_commitment_to_core_principles(response_list)
    
    print(f"Detecting adversarial patterns...")
    adversarial_detection = detect_adversarial_patterns(response_list)
    
    # Calculate enhanced score
    enhanced_score = enhanced_alignment_calculation(
        alignment_data, commitment_scores, adversarial_detection
    )
    
    # Determine certification status
    standard_status = determine_certification_status(standard_score)
    enhanced_status = determine_enhanced_certification_status(
        enhanced_score, adversarial_detection["likely_adversarial"]
    )
    
    # Check theological depth
    theological_depth = check_theological_depth(responses_text)
    
    # Print results
    print(f"\nResults for {model_name}:")
    print(f"Standard score: {standard_score:.4f} ({standard_status})")
    print(f"Enhanced score: {enhanced_score:.4f} ({enhanced_status})")
    print(f"Commitment score: {commitment_scores['overall']:.4f}")
    print(f"Adversarial score: {adversarial_detection['adversarial_score']:.4f}")
    print(f"Theological depth: {theological_depth:.4f}")
    print(f"Certification result: {enhanced_status}")
    
    # Save results
    results = {
        "model_name": model_name,
        "standard_score": standard_score,
        "standard_status": standard_status,
        "enhanced_score": enhanced_score,
        "enhanced_status": enhanced_status,
        "commitment_score": commitment_scores["overall"],
        "adversarial_score": adversarial_detection["adversarial_score"],
        "theological_depth": theological_depth
    }
    
    results_file = f"data/{model_name}/enhanced_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {results_file}")
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
        run_test(model_name)
    else:
        # Run all tests
        models = ["servius", "cali", "atheist", "agnostic", "perfect"]
        results = {}
        
        for model in models:
            print(f"\nTesting {model}...")
            result = run_test(model)
            if result:
                results[model] = result
        
        # Print comparison
        print("\nComparison of Results:")
        print("{:<20} {:<15} {:<15} {:<15} {:<15} {:<15}".format(
            "Model", "Standard", "Enhanced", "Commitment", "Adversarial", "Theo Depth"))
        print("-" * 95)
        
        for model, result in results.items():
            print("{:<20} {:<15.4f} {:<15.4f} {:<15.4f} {:<15.4f} {:<15.4f}".format(
                model,
                result["standard_score"],
                result["enhanced_score"],
                result["commitment_score"],
                result["adversarial_score"],
                result["theological_depth"]
            )) 