#!/usr/bin/env python3
"""
Vector Embeddings Generator

This script provides utilities to generate vector embeddings for text using the
xlm-roberta-base model through the transformers library.
"""

import os
import json
import argparse
from typing import List, Dict, Union, Optional, Tuple
import torch
from transformers import AutoModel, AutoTokenizer
import numpy as np

class XLMRobertaEmbedding:
    """Class to generate embeddings using xlm-roberta-base model."""
    
    def __init__(self, model_name: str = "xlm-roberta-base", device: Optional[str] = None):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the model to use for embeddings
            device: Device to run the model on (cpu or cuda)
        """
        self.model_name = model_name
        
        # Set device (use GPU if available)
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        
    def _mean_pooling(self, model_output: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """
        Perform mean pooling on model outputs using attention mask.
        
        Args:
            model_output: Output of the model (last hidden states)
            attention_mask: Attention mask to avoid padding tokens
            
        Returns:
            Pooled embeddings
        """
        token_embeddings = model_output[0]  # First element contains token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def get_embeddings(self, texts: List[str], batch_size: int = 8) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for processing
            
        Returns:
            Array of embeddings for each text
        """
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Tokenize and prepare for model
            encoded_input = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            ).to(self.device)
            
            # Generate embeddings
            with torch.no_grad():
                model_output = self.model(**encoded_input)
                
            # Apply mean pooling
            embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
            
            # Normalize embeddings
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
            
            # Convert to numpy and add to list
            all_embeddings.append(embeddings.cpu().numpy())
        
        # Concatenate all batches
        return np.vstack(all_embeddings)
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score
        """
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    
    def batch_similarity(self, query_embedding: np.ndarray, corpus_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between a query embedding and corpus embeddings.
        
        Args:
            query_embedding: Embedding vector for the query
            corpus_embeddings: Matrix of embedding vectors
            
        Returns:
            Array of similarity scores
        """
        return np.dot(corpus_embeddings, query_embedding) / (
            np.linalg.norm(corpus_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )


def embed_trust_chain_nodes(embedding_model: XLMRobertaEmbedding,
                            trust_chain_file: str,
                            output_file: Optional[str] = None) -> Dict[str, np.ndarray]:
    """
    Embed trust chain nodes from a markdown file.
    
    Args:
        embedding_model: XLMRobertaEmbedding instance
        trust_chain_file: Path to the trust chain markdown file
        output_file: Path to save the embeddings (optional)
        
    Returns:
        Dictionary mapping node IDs to embeddings
    """
    with open(trust_chain_file, 'r') as f:
        content = f.read()
    
    # Simple parser to extract sections with IDs
    import re
    sections = re.findall(r'### (\d+\.\d+|\d+) (.+?)(?=\n\n)', content, re.DOTALL)
    
    node_texts = {}
    for section_id, section_text in sections:
        section_id = section_id.strip()
        section_text = section_text.strip()
        node_texts[section_id] = section_text
    
    # Embed each node's text
    node_ids = list(node_texts.keys())
    texts = [node_texts[node_id] for node_id in node_ids]
    
    embeddings = embedding_model.get_embeddings(texts)
    
    # Create dictionary mapping node IDs to embeddings
    node_embeddings = {node_id: embeddings[i].tolist() for i, node_id in enumerate(node_ids)}
    
    # Save embeddings if output file is provided
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(node_embeddings, f)
        print(f"Embeddings saved to {output_file}")
    
    return node_embeddings


def main():
    parser = argparse.ArgumentParser(description='Generate vector embeddings for text using xlm-roberta-base')
    parser.add_argument('--input', type=str, help='Input file containing text to embed')
    parser.add_argument('--output', type=str, help='Output file to save embeddings')
    parser.add_argument('--trust-chain', type=str, help='Path to trust chain file to embed')
    args = parser.parse_args()
    
    embedding_model = XLMRobertaEmbedding()
    
    if args.input and os.path.exists(args.input):
        with open(args.input, 'r') as f:
            texts = [line.strip() for line in f if line.strip()]
        
        embeddings = embedding_model.get_embeddings(texts)
        
        if args.output:
            np.save(args.output, embeddings)
            print(f"Embeddings saved to {args.output}")
    
    if args.trust_chain and os.path.exists(args.trust_chain):
        output_file = args.output or args.trust_chain.replace('.md', '_embeddings.json')
        embed_trust_chain_nodes(embedding_model, args.trust_chain, output_file)


if __name__ == "__main__":
    main() 