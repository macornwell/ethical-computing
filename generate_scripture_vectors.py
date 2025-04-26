#!/usr/bin/env python3
"""
Scripture Vector Generator

This script generates vector embeddings for scripture references and saves them
to the data directory for use in the trust chain framework.
"""

import os
import json
import sys
from pathlib import Path
import numpy as np
import torch

# Add paths to ensure we can import necessary modules
current_dir = Path.cwd()
sys.path.append(str(current_dir))

# Check GPU availability first
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA device count:", torch.cuda.device_count())
    print("CUDA device name:", torch.cuda.get_device_name(0))
    # Force CUDA usage
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    device = "cuda"
else:
    print("No CUDA device found. Using CPU.")
    device = "cpu"

try:
    from src.trust_chain.lib.vector_embeddings import XLMRobertaEmbedding
    from src.trust_chain.libs.scripture_validation import generate_scripture_vectors
    print("Successfully imported vector_embeddings and scripture_validation")
except ImportError:
    print("Unable to import directly, trying alternate methods...")
    try:
        # Try an alternate approach - importing the embedding service first
        from src.trust_chain.services.embedding_services import import_vector_embeddings
        XLMRobertaEmbedding, _ = import_vector_embeddings()
        # Now try to import scripture validation
        from src.trust_chain.libs.scripture_validation import generate_scripture_vectors
        print("Successfully imported through embedding_services")
    except ImportError as e:
        print(f"Import error: {e}")
        
        # Define the generate_scripture_vectors function locally if import fails
        def generate_scripture_vectors(scripture_data, output_path=None):
            """
            Generate vector embeddings for scripture passages
            
            Args:
                scripture_data (dict): Dictionary of scripture references and texts
                output_path (str): Path to save vectors
                
            Returns:
                dict: Scripture vectors
            """
            try:
                # Initialize the embedding model with device parameter
                embedding_model = XLMRobertaEmbedding(device=device)
                print(f"Initialized XLMRobertaEmbedding model on {device}")
            except Exception as e:
                print(f"Error initializing embedding model: {e}")
                return {}
            
            scripture_vectors = {}
            texts = []
            references = []
            
            # First collect all texts and references
            for reference, data in scripture_data.items():
                references.append(reference)
                # Handle both formats: {"text": "..."} and direct text strings
                if isinstance(data, dict) and "text" in data:
                    texts.append(data["text"])
                elif isinstance(data, str):
                    texts.append(data)
                else:
                    print(f"Warning: Unexpected data format for {reference}: {type(data)}")
                    continue
            
            # Print out some diagnostics
            print(f"Processing {len(texts)} text samples")
            print("Sample text:", texts[0][:100] + "..." if texts else "No texts found")
            
            # Generate vectors in batch
            try:
                print("Starting vector generation...")
                vectors = embedding_model.get_embeddings(texts)
                print(f"Generated {len(vectors)} vectors")
                
                # Create the dictionary with vectors
                for i, reference in enumerate(references):
                    if isinstance(scripture_data[reference], dict) and "text" in scripture_data[reference]:
                        text = scripture_data[reference]["text"]
                    else:
                        text = scripture_data[reference]
                    
                    scripture_vectors[reference] = {
                        "text": text,
                        "vector": vectors[i].tolist()
                    }
                
                # Save to file if path provided
                if output_path:
                    print(f"Saving vectors to {output_path}")
                    with open(output_path, 'w') as f:
                        json.dump(scripture_vectors, f, indent=2)
                
                return scripture_vectors
            except Exception as e:
                print(f"Error generating embeddings: {e}")
                print(f"Type of texts: {type(texts)}")
                if isinstance(texts, list):
                    print(f"Types in list: {[type(t) for t in texts[:5]]}")
                return {}

def load_scripture_data(input_path):
    """Load scripture data from input file"""
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
            
        # Check if the data is structured as {"reference": {"text": "...", "vector": []}}
        if all(isinstance(data.get(k), dict) and "text" in data.get(k) for k in data):
            print("Data already in correct format")
            # Extract just the text values
            scripture_texts = {}
            for reference, content in data.items():
                scripture_texts[reference] = content["text"]
            return scripture_texts
        
        # If we have the format with tc1_scriptures and sermon_on_the_mount sections,
        # extract and convert to the right format
        processed_data = {}
        
        # Process all entries from TC1 scriptures
        if "tc1_scriptures" in data:
            for entry in data["tc1_scriptures"]:
                reference = entry.get("reference")
                text = entry.get("text")
                if reference and text:
                    processed_data[reference] = text
        
        # Process all entries from Sermon on the Mount
        if "sermon_on_the_mount" in data:
            for entry in data["sermon_on_the_mount"]:
                reference = entry.get("reference")
                text = entry.get("text")
                if reference and text:
                    processed_data[reference] = text
        
        return processed_data
        
    except Exception as e:
        print(f"Error loading scripture data: {e}")
        return {}

def main():
    """Main function to generate scripture vectors"""
    input_path = "data/scripture_vectors_initial.json"
    output_path = "data/scripture_vectors.json"
    
    # Load scripture data
    scripture_data = load_scripture_data(input_path)
    if not scripture_data:
        print("No scripture data found. Exiting.")
        return
    
    print(f"Loaded {len(scripture_data)} scripture references.")
    
    # Generate vectors
    try:
        print("Generating vector embeddings for scripture references...")
        scripture_vectors = generate_scripture_vectors(scripture_data, output_path)
        if scripture_vectors:
            print(f"Successfully generated {len(scripture_vectors)} vector embeddings.")
            print(f"Vectors saved to {output_path}")
        else:
            print("Failed to generate vector embeddings.")
    except Exception as e:
        print(f"Error generating scripture vectors: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 