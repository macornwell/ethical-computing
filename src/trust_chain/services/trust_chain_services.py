"""
Trust Chain Services

Provides services for interacting with trust chain files and data.
"""

import os
import re
import glob
from pathlib import Path
from src.trust_chain.services.file_services import read_text_file

def extract_tc_nodes_from_file(file_path):
    """Extract trust chain nodes from a single markdown file"""
    try:
        file_name = os.path.basename(file_path)
        tc_id = os.path.splitext(file_name)[0]  # tc-1 for example
        
        # Read the file content
        content = read_text_file(file_path)
        if not content:
            print(f"Error: Could not read content from {file_path}")
            return {}
        
        # Extract nodes from markdown using regex
        node_pattern = r'## (\d+\.\d+)[\s\n]+([^#]+)'
        nodes = re.findall(node_pattern, content)
        
        # Extract scripture references
        scripture_pattern = r'> \*\*([^*]+)\*\*\s*([^<]+)'
        
        tc_nodes = {}
        for node_id, node_content in nodes:
            # Clean up node content
            node_content = node_content.strip()
            
            # Find scriptures for this node
            scriptures = re.findall(scripture_pattern, node_content)
            
            # Remove scripture blocks from the node content for cleaner vectorization
            node_content_clean = re.sub(r'>\s*\*\*[^*]+\*\*\s*[^<]+', '', node_content)
            node_content_clean = re.sub(r'\n+', ' ', node_content_clean)
            node_content_clean = re.sub(r'\s+', ' ', node_content_clean).strip()
            
            # Store node data
            node_key = f"{tc_id}:{node_id}"
            tc_nodes[node_key] = {
                "content": node_content_clean,
                "scriptures": scriptures
            }
            
        return tc_nodes
    except Exception as e:
        print(f"Error extracting nodes from {file_path}: {e}")
        return {}

def get_trust_chain_nodes(trust_chain_path):
    """Get all trust chain nodes from provided path (directory or file)"""
    tc_nodes = {}
    
    # Find all trust chain files and extract nodes
    if os.path.isdir(trust_chain_path):
        # If path is a directory, look for tc-*.md files
        for file_path in glob.glob(os.path.join(trust_chain_path, "tc-*.md")):
            nodes_from_file = extract_tc_nodes_from_file(file_path)
            tc_nodes.update(nodes_from_file)
    elif os.path.isfile(trust_chain_path) and trust_chain_path.endswith(".md"):
        # If path is a specific file
        nodes_from_file = extract_tc_nodes_from_file(trust_chain_path)
        tc_nodes.update(nodes_from_file)
    else:
        print(f"Warning: Invalid trust chain path: {trust_chain_path}")
    
    return tc_nodes 