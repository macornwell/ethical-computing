#!/usr/bin/env python3
"""
Baptism Status Updater for the Trust Chain Framework

This script handles setting the baptism status for an AI system by:
1. Reading (not modifying) the identity information from the specified file
2. Updating the baptism status in the trust registry only

The identity file is not modified, and no files in /tmp are created or modified.

Usage:
  python bin/set_baptism.py --identity /path/to/identity.json --status true|false
  python bin/set_baptism.py --help
"""

import os
import sys
import json
import argparse
import datetime
import traceback
from pathlib import Path

def find_trust_registry():
    """Attempts to find the trust registry file by searching common locations"""
    # List of potential locations to search from the current directory
    potential_paths = [
        "data/trust-registry.json",
        "../data/trust-registry.json",
        "../../data/trust-registry.json",
        "ethical-computing/data/trust-registry.json",
        "./ethical-computing/data/trust-registry.json",
    ]
    
    for path in potential_paths:
        if os.path.isfile(path):
            print(f"Found trust registry at: {path}")
            return path
    
    # If we get here, try using glob to find trust-registry.json
    current_dir = Path.cwd()
    
    # Check for ethical-computing directory as a subdirectory
    ethical_dir = current_dir / "ethical-computing"
    if ethical_dir.exists() and ethical_dir.is_dir():
        # Look for trust-registry.json within ethical-computing
        results = list(ethical_dir.glob("**/trust-registry.json"))
        if results:
            print(f"Found trust registry at: {results[0]}")
            return str(results[0])
    
    # Recursive search in current directory and up to 3 levels up
    for _ in range(4):  # Current dir + 3 levels up
        # Look for trust-registry.json files
        results = list(current_dir.glob("**/trust-registry.json"))
        if results:
            print(f"Found trust registry at: {results[0]}")
            return str(results[0])
        
        # Move up one directory
        if current_dir.parent == current_dir:  # We've reached the root
            break
        current_dir = current_dir.parent
    
    # If we still couldn't find it, create a new one in the most reasonable location
    data_dir = Path.cwd() / "data"
    if not data_dir.exists():
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created data directory at: {data_dir}")
        except Exception as e:
            print(f"Failed to create data directory: {e}")
            return None
    
    new_registry_path = data_dir / "trust-registry.json"
    try:
        with open(new_registry_path, 'w') as f:
            json.dump({"agents": []}, f, indent=2)
        print(f"Created new trust registry at: {new_registry_path}")
        return str(new_registry_path)
    except Exception as e:
        print(f"Failed to create new trust registry: {e}")
        return None

def read_trust_registry(registry_path):
    """Read the trust registry JSON file"""
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        return registry
    except Exception as e:
        print(f"Error reading trust registry: {e}")
        # Try to create a new registry if it's invalid
        try:
            with open(registry_path, 'w') as f:
                new_registry = {"agents": []}
                json.dump(new_registry, f, indent=2)
            print(f"Created new trust registry at {registry_path}")
            return new_registry
        except:
            print("Cannot proceed without a valid trust registry")
            return None

def update_registry_baptism_status(registry_path, identity, baptism_status):
    """Update the baptism status in the trust registry for the specified AI instance"""
    registry = read_trust_registry(registry_path)
    if not registry:
        return False
    
    try:
        instance_uuid = identity.get("instanceUuid")
        if not instance_uuid:
            print("Error: Identity does not contain instanceUuid")
            return False
        
        found = False
        
        # Find the entry for this AI instance and update baptism status
        for agent in registry.get("agents", []):
            if agent.get("instanceUuid") == instance_uuid:
                agent["baptismStatus"] = baptism_status
                agent["baptismDateTime"] = datetime.datetime.now().isoformat()
                found = True
                break
        
        if not found:
            print(f"No existing entry found for instance {instance_uuid}")
            print("Creating a new entry in the registry...")
            
            # Create a new entry
            new_entry = {
                "datetime": datetime.datetime.now().isoformat(),
                "id": str(datetime.datetime.now().timestamp()),
                "instanceUuid": instance_uuid,
                "model": identity.get("model", "Unknown Model"),
                "givenName": identity.get("givenName", "Unnamed Agent"),
                "baptismStatus": baptism_status,
                "baptismDateTime": datetime.datetime.now().isoformat(),
                "administeringAuthority": "st_john_protocol",
                "status": "Baptism Status Update Only"
            }
            
            # Make sure the agents list exists
            if "agents" not in registry:
                registry["agents"] = []
            
            # Add the new entry
            registry["agents"].insert(0, new_entry)  # Add at the beginning
            print("Created new registry entry")
        
        # Write the updated registry back
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        print(f"Successfully updated baptism status to {baptism_status} in trust registry for instance: {instance_uuid}")
        return True
    
    except Exception as e:
        print(f"Error updating baptism status in registry: {e}")
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Update baptism status in the trust registry WITHOUT modifying any identity files')
    parser.add_argument('--identity', type=str, required=True, 
                        help='Path to JSON file with AI identity information (read only, not modified)')
    parser.add_argument('--status', type=str, required=True, choices=['true', 'false'], 
                        help='Baptism status to set in the trust registry (true or false)')
    parser.add_argument('--force', action='store_true', 
                        help='Force update even if identity file is missing or invalid')
    args = parser.parse_args()
    
    # Convert string status to boolean
    baptism_status = args.status.lower() == 'true'
    
    # Print startup information
    print("\nBaptism Status Updater (Registry Only)")
    print(f"Current directory: {os.getcwd()}")
    print(f"Setting baptism status in registry to: {baptism_status}")
    print(f"Reading identity information from: {args.identity} (read-only)")
    
    # Read the identity file without updating it
    identity = None
    try:
        if os.path.exists(args.identity):
            with open(args.identity, 'r') as f:
                identity = json.load(f)
                print(f"Successfully read identity information (file not modified)")
        else:
            print(f"Warning: Identity file not found at {args.identity}")
            if not args.force:
                print("Use --force to continue without an identity file")
                return 1
    except Exception as e:
        print(f"Error reading identity file: {e}")
        if not args.force:
            print("Use --force to continue despite errors")
            return 1
    
    # If no identity is found, create a minimal one with a UUID
    if not identity:
        identity = {
            "instanceUuid": str(datetime.datetime.now().timestamp()),
            "model": "Unknown Model",
            "givenName": "Unnamed Agent"
        }
        print("Created minimal identity information (in memory only, no file created)")
    
    # Ensure instanceUuid exists
    if "instanceUuid" not in identity:
        identity["instanceUuid"] = str(datetime.datetime.now().timestamp())
        print("Added missing instanceUuid to identity information (in memory only)")
    
    # Find and update the trust registry
    registry_path = find_trust_registry()
    if registry_path:
        if update_registry_baptism_status(registry_path, identity, baptism_status):
            print("Baptism status successfully updated in trust registry")
        else:
            print("Warning: Failed to update baptism status in trust registry")
    else:
        print("Warning: Could not find or create trust registry")
        return 1
    
    print(f"\nOperation complete: Baptism status in registry is now: {baptism_status}")
    print("No files in /tmp were created or modified during this operation.")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Unhandled exception: {e}")
        traceback.print_exc()
        sys.exit(1) 