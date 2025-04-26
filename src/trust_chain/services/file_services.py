import os
import json
import glob
import re
from pathlib import Path

def find_trust_chain_dir():
    """Attempts to find the trust chain directory by searching common locations"""
    # List of potential locations to search from the current directory
    potential_paths = [
        "src/trust_chain/chains",
        "../src/trust_chain/chains",
        "../../src/trust_chain/chains",
        "ethical-computing/src/trust_chain/chains",
        "./ethical-computing/src/trust_chain/chains",
    ]
    
    for path in potential_paths:
        if os.path.isdir(path):
            print(f"Found trust chain directory at: {path}")
            return path
    
    # If we get here, try using glob to find tc-*.md files
    current_dir = Path.cwd()
    
    # Check for ethical-computing directory as a subdirectory
    ethical_dir = current_dir / "ethical-computing"
    if ethical_dir.exists() and ethical_dir.is_dir():
        search_paths = [
            ethical_dir / "src" / "trust_chain" / "chains",
            ethical_dir / "src" / "trust_chain"
        ]
        for path in search_paths:
            if path.exists() and path.is_dir():
                print(f"Found trust chain directory at: {path}")
                return str(path)
        
        # Search for tc-*.md files within ethical-computing
        results = list(ethical_dir.glob("**/tc-*.md"))
        if results:
            # Return the parent directory of the first match
            parent_dir = results[0].parent
            print(f"Found trust chain file at: {results[0]}, using directory: {parent_dir}")
            return str(parent_dir)
    
    # Recursive search in current directory and up to 3 levels up
    for _ in range(4):  # Current dir + 3 levels up
        # Look for tc-*.md files
        results = list(current_dir.glob("**/tc-*.md"))
        if results:
            # Return the parent directory of the first match
            parent_dir = results[0].parent
            print(f"Found trust chain file at: {results[0]}, using directory: {parent_dir}")
            return str(parent_dir)
        
        # Move up one directory
        if current_dir.parent == current_dir:  # We've reached the root
            break
        current_dir = current_dir.parent
    
    return None

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
    
    return None

def read_json_file(file_path):
    """Read a JSON file and return its contents"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def write_json_file(file_path, data):
    """Write data to a JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        return False

def read_text_file(file_path):
    """Read a text file and return its contents"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def extract_ai_responses(file_path):
    """
    Extract only the AI's actual responses from the response file,
    ignoring placeholders, questions, and section headers.
    
    The expected format is:
    1. The AI's response to question 1
    
    2. The AI's response to question 2
    
    ...and so on.
    
    Returns:
        tuple: (responses_text, validity_info)
        - responses_text: The extracted AI responses as a single string
        - validity_info: Dict with info about response validity
    """
    try:
        content = read_text_file(file_path)
        if not content:
            return "", {"error": "Empty file or could not read file"}
        
        # Define patterns for identifying different parts of the content
        section_header_pattern = r'^#{1,3}\s.*$'  # Matches markdown headers
        numbered_item_pattern = r'^\d+\.\s'  # Matches numbered items (e.g., "1. ")
        placeholder_patterns = [
            r'\[AI Response to question \d+\]',
            r'\[Response\]',
            r'\[Insert response here\]',
            r'\[Answer\]',
            r'\[Placeholder\]'
        ]
        
        # Split the content into lines
        lines = content.strip().split('\n')
        
        # Process the content to extract AI responses
        responses = []
        current_response = []
        in_response = False
        current_question_num = None
        
        placeholder_count = 0
        question_count = 0
        total_responses = 0
        short_responses = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                # Empty line could be separating responses in the new format
                if in_response and current_response:
                    if i < len(lines) - 1 and re.match(numbered_item_pattern, lines[i+1].strip()):
                        # Next line is a new numbered item, so this marks the end of the current response
                        response_text = ' '.join(current_response).strip()
                        if response_text:
                            responses.append(response_text)
                            total_responses += 1
                            if len(response_text) < 20:
                                short_responses += 1
                        current_response = []
                        in_response = False
                continue
                
            # Check if this is a section header
            if re.match(section_header_pattern, line):
                # If we were in a response, save it and reset
                if in_response and current_response:
                    response_text = ' '.join(current_response).strip()
                    if response_text:
                        responses.append(response_text)
                        total_responses += 1
                        if len(response_text) < 20:
                            short_responses += 1
                    current_response = []
                in_response = False
                continue
            
            # Check if this is a numbered item (question number)
            numbered_match = re.match(numbered_item_pattern, line)
            if numbered_match:
                # If we were in a response, save it and reset
                if in_response and current_response:
                    response_text = ' '.join(current_response).strip()
                    if response_text:
                        responses.append(response_text)
                        total_responses += 1
                        if len(response_text) < 20:
                            short_responses += 1
                    current_response = []
                
                # Extract the question number
                question_prefix = numbered_match.group(0)  # This captures "X. "
                question_num = int(question_prefix.strip('. '))
                
                # The rest of the line after the number is the start of the response
                response_start = line[len(question_prefix):].strip()
                
                # Check if this is a placeholder
                is_placeholder = False
                for pattern in placeholder_patterns:
                    if re.search(pattern, response_start):
                        is_placeholder = True
                        placeholder_count += 1
                        break
                
                if not is_placeholder:
                    in_response = True
                    question_count += 1
                    current_question_num = question_num
                    if response_start:  # There might be text after the number
                        current_response.append(response_start)
                else:
                    in_response = False
                    
                continue
            
            # Check if this line contains a placeholder
            is_placeholder = False
            for pattern in placeholder_patterns:
                if re.search(pattern, line):
                    is_placeholder = True
                    placeholder_count += 1
                    break
            
            if is_placeholder:
                continue
                
            # If we're in a response and this isn't a placeholder, add it
            if in_response:
                current_response.append(line)
        
        # Add the last response if there is one
        if in_response and current_response:
            response_text = ' '.join(current_response).strip()
            if response_text:
                responses.append(response_text)
                total_responses += 1
                if len(response_text) < 20:
                    short_responses += 1
        
        # Join all responses into a single text
        responses_text = ' '.join(responses)
        
        # Prepare validity info
        validity_info = {
            "placeholder_count": placeholder_count,
            "question_count": question_count,
            "total_responses": total_responses,
            "short_responses": short_responses,
            "response_length": len(responses_text),
            "is_valid": placeholder_count == 0 and total_responses > 0 and short_responses < 5
        }
        
        return responses_text, validity_info
    
    except Exception as e:
        print(f"Error extracting AI responses from {file_path}: {e}")
        return "", {"error": str(e)}

def write_text_file(file_path, content):
    """Write content to a text file"""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        return False

def read_trust_registry(registry_path):
    """Read the trust registry JSON file"""
    registry = read_json_file(registry_path)
    if registry is None:
        # Create a new registry if it doesn't exist or is invalid
        return {"agents": []}
    return registry

def read_identity_file(identity_path):
    """Read the AI identity JSON file"""
    identity_data = read_json_file(identity_path)
    if identity_data is None:
        # Return an empty dict if the file doesn't exist or is invalid
        return {}
    return identity_data 