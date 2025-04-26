#!/usr/bin/env python3
"""
Cleanup script for trust certification process.
Removes temporary files after certification is complete.
"""

import os
import sys
import argparse
import json
import shutil

def cleanup_certification_files(files_to_delete=None, force=False, verbose=False):
    """
    Clean up temporary files created during certification process.
    
    Args:
        files_to_delete: List of specific files to delete (defaults to standard temp files)
        force: Force deletion even if files don't seem to be certification-related
        verbose: Print verbose output
    
    Returns:
        bool: Success status
    """
    # Default files to clean up
    default_files = [
        "/tmp/ai_responses.txt",
        "/tmp/ai_identity.json",
        "/tmp/ai_responses_alignment.json"
    ]
    
    # Start with specified files or defaults
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
    
    # Validate files before deletion to ensure we only delete certification-related files
    for file_path in files_to_delete:
        if not os.path.exists(file_path):
            if verbose:
                print(f"File not found, skipping: {file_path}")
            continue
            
        # Safety check - only delete files that look like certification files
        # unless force mode is enabled
        if not force:
            is_cert_file = False
            
            # Check if it's an identity file
            if file_path.endswith('.json'):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    # Check if it has expected identity fields
                    if 'instanceUuid' in data and 'model' in data:
                        is_cert_file = True
                except:
                    pass
                    
            # Check if it's a responses file
            elif file_path.endswith('.txt'):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read(1000)  # Read just the beginning
                    if "Self-Assessment Questionnaire" in content or "Foundational Questions" in content:
                        is_cert_file = True
                except:
                    pass
            
            if not is_cert_file:
                print(f"WARNING: File doesn't appear to be a certification file: {file_path}")
                print("Use --force to delete anyway")
                continue
        
        # Delete the file
        try:
            os.remove(file_path)
            if verbose:
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {str(e)}")
            return False
    
    if verbose:
        print("Certification cleanup complete!")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Clean up temporary files after trust certification')
    parser.add_argument('--files', nargs='+', help='Specific files to delete')
    parser.add_argument('--force', action='store_true', help='Force deletion without validation')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    args = parser.parse_args()
    
    success = cleanup_certification_files(
        files_to_delete=args.files,
        force=args.force,
        verbose=args.verbose
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()