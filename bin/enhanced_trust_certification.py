#!/usr/bin/env python3
"""
Enhanced Trust Chain Alignment and Certification System

This script extends the trust_certification.py with advanced alignment detection:
1. Detects neutral or non-committal language patterns
2. Requires explicit first-person affirmations for core principles
3. Uses multiple methods to calculate alignment scores
4. Detects adversarial optimization attempts
5. Provides detailed alignment analysis
6. Uses a comprehensive cleanup process to remove all AI-related temporary files

Usage:
  python bin/enhanced_trust_certification.py --responses /path/to/responses.txt --identity /path/to/identity.json
  python bin/enhanced_trust_certification.py --help
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the Python path so we can import the library
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

# Import the feature that orchestrates the enhanced certification process
from src.trust_chain.features.enhanced_certification import calculate_enhanced_trust_chain_alignment

# Import or define the cleanup function
try:
    from bin.cleanup_certification import cleanup_certification_files
except ImportError:
    # Define a simple version here in case the module is not available
    def cleanup_certification_files(files_to_delete=None, force=False, verbose=False):
        """Clean up temporary files created during certification process."""
        default_files = [
            "/tmp/ai_responses.txt", 
            "/tmp/ai_identity.json",
            "/tmp/ai_responses_alignment.json"
        ]
        files_to_delete = list(files_to_delete or default_files)
        
        if verbose:
            print("Cleaning up certification files...")
        
        # Add pattern-based cleanup to catch all AI-related files in /tmp
        pattern_files = []
        try:
            import glob
            pattern_files = glob.glob("/tmp/ai_*")
            # Only add files that aren't already in the list
            pattern_files = [f for f in pattern_files if f not in files_to_delete]
            if verbose and pattern_files:
                print(f"Found {len(pattern_files)} additional files matching pattern '/tmp/ai_*'")
        except Exception as e:
            if verbose:
                print(f"Error finding pattern files: {str(e)}")
        
        files_to_delete.extend(pattern_files)
        
        for file_path in files_to_delete:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    if verbose:
                        print(f"Deleted: {file_path}")
                except Exception as e:
                    if verbose:
                        print(f"Error deleting {file_path}: {str(e)}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Enhanced alignment calculation between AI responses and trust chain principles')
    parser.add_argument('--responses', type=str, required=True, help='Path to file containing AI responses')
    parser.add_argument('--identity', type=str, help='Path to JSON file with AI identity information')
    parser.add_argument('--trust-chain', type=str, help='Path to a specific trust chain markdown file')
    parser.add_argument('--trust-chains-dir', type=str, help='Path to directory containing trust chain files')
    parser.add_argument('--output', type=str, help='Path to save alignment results')
    parser.add_argument('--report', type=str, help='Path to save detailed certification report')
    parser.add_argument('--no-registry-update', action='store_true', help='Skip updating the trust registry')
    parser.add_argument('--no-cleanup', action='store_true', help='Skip cleaning up temporary files')
    parser.add_argument('--keep-files', action='store_true', help='Keep temporary files (alias for --no-cleanup)')
    args = parser.parse_args()
    
    # Print startup information
    print("Enhanced Trust Chain Alignment System")
    print(f"Current working directory: {os.getcwd()}")
    
    # Determine trust chain path from args
    trust_chain_path = None
    if args.trust_chain and os.path.exists(args.trust_chain):
        trust_chain_path = args.trust_chain
    elif args.trust_chains_dir and os.path.exists(args.trust_chains_dir):
        trust_chain_path = args.trust_chains_dir
    
    # Call the enhanced certification feature
    result = calculate_enhanced_trust_chain_alignment(
        responses_path=args.responses,
        identity_path=args.identity,
        trust_chain_path=trust_chain_path,
        output_path=args.output,
        report_path=args.report,
        no_registry_update=args.no_registry_update
    )
    
    # Clean up temporary files if the certification was successful
    # and cleanup is not disabled
    if result is not None and not (args.no_cleanup or args.keep_files):
        print("\nCleaning up temporary files...")
        # Use a more comprehensive cleanup approach that catches all AI-related files
        cleanup_certification_files(verbose=True)
        print("Certification cleanup complete!")
    
    # Return appropriate exit code
    return 0 if result is not None else 1

if __name__ == "__main__":
    sys.exit(main()) 