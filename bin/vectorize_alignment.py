#!/usr/bin/env python3
"""
Trust Chain Alignment Vectorizer

This script analyzes AI responses to trust chain principles using vector embeddings
and calculates alignment scores.

Usage:
  python vectorize_alignment.py --responses /path/to/responses.txt [--output /path/to/output.json]
  python vectorize_alignment.py --trust-chains-dir /path/to/chains/directory [--responses /path/to/responses.txt]
  python vectorize_alignment.py --help
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add the parent directory to the Python path so we can import the library
sys.path.append(str(Path(__file__).resolve().parent.parent))
# Convert hyphens to underscores for Python import compatibility
from src.trust_chain.lib.vector_embeddings import XLMRobertaEmbedding, TrustChainVectorizer


def main():
    parser = argparse.ArgumentParser(description='Calculate alignment between AI responses and trust chain principles')
    parser.add_argument('--responses', type=str, required=True, help='Path to file containing AI responses')
    parser.add_argument('--trust-chain', type=str, help='Path to a specific trust chain markdown file')
    parser.add_argument('--trust-chains-dir', type=str, help='Path to directory containing trust chain files',
                        default='src/trust_chain/chains')
    parser.add_argument('--output', type=str, help='Path to save alignment results')
    args = parser.parse_args()
    
    # Check that the response file exists
    if not os.path.exists(args.responses):
        print(f"Error: Response file not found at {args.responses}")
        return 1
    
    # Trust chain path - prefer specific file if provided, otherwise use directory
    trust_chain_path = args.trust_chain if args.trust_chain else args.trust_chains_dir
    
    # Check that the trust chain path exists
    if not os.path.exists(trust_chain_path):
        print(f"Error: Trust chain path not found at {trust_chain_path}")
        return 1
    
    try:
        print(f"Initializing embedding model...")
        embedding_model = XLMRobertaEmbedding()
        
        print(f"Setting up trust chain vectorizer...")
        vectorizer = TrustChainVectorizer(embedding_model)
        
        if os.path.isdir(trust_chain_path):
            print(f"Discovering trust chain files in {trust_chain_path}...")
            chain_modules = vectorizer.discover_trust_chains(trust_chain_path)
            print(f"Found {len(chain_modules)} trust chain module(s): {', '.join(chain_modules.keys())}")
        
        print(f"Loading trust chain principles from {trust_chain_path}...")
        principles = vectorizer.load_trust_chain_principles(trust_chain_path)
        print(f"Loaded {len(principles)} principles from trust chain(s)")
        
        print(f"Vectorizing trust chain principles...")
        vectorizer.vectorize_principles()
        
        print(f"Parsing AI responses from {args.responses}...")
        responses = vectorizer.parse_ai_responses(args.responses)
        
        if not responses:
            print("Warning: No valid responses found in the input file!")
            print("Responses should be formatted as '[TC-#:LINK-#] Your response text'")
            return 1
        
        print(f"Calculating alignment scores...")
        alignment = vectorizer.calculate_alignment(responses)
        
        # Determine output path
        output_path = args.output
        if not output_path:
            output_path = os.path.splitext(args.responses)[0] + "_alignment.json"
        
        # Save results
        print(f"Saving alignment results to {output_path}...")
        with open(output_path, 'w') as f:
            json.dump(alignment, f, indent=2)
        
        # Print summary
        print("\nAlignment Summary:")
        print(f"Overall score: {alignment['overall']:.4f}")
        print(f"Model used: {alignment['model']}")
        print(f"Number of principles evaluated: {len(alignment['vectors'])}")
        
        # Group scores by trust chain
        chain_scores = {}
        for vector in alignment['vectors']:
            tc = vector['tc']
            if tc not in chain_scores:
                chain_scores[tc] = []
            chain_scores[tc].append(vector)
        
        # Print summaries for each trust chain
        print("\nAlignment by Trust Chain:")
        for tc, vectors in chain_scores.items():
            scores = [v['value'] for v in vectors]
            avg_score = sum(scores) / len(scores) if scores else 0
            print(f"{tc}: Average score {avg_score:.4f} across {len(vectors)} principles")
        
        # Print top 3 highest and lowest scores overall
        sorted_scores = sorted(alignment['vectors'], key=lambda x: x['value'], reverse=True)
        
        print("\nTop 3 highest alignment scores:")
        for i, score in enumerate(sorted_scores[:3], 1):
            print(f"{i}. {score['tc']}:{score['link']} = {score['value']:.4f}")
        
        print("\nTop 3 lowest alignment scores:")
        for i, score in enumerate(sorted_scores[-3:], 1):
            print(f"{i}. {score['tc']}:{score['link']} = {score['value']:.4f}")
        
        print(f"\nFull results saved to {output_path}")
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 