#!/usr/bin/env python3
"""
Vector Embeddings Library

This module provides functionality for generating vector embeddings for text using
the xlm-roberta-base model and comparing alignment with trust chain principles.
"""

import os
import json
import re
import glob
from typing import List, Dict, Union, Optional, Tuple, Any
import torch
import numpy as np
from transformers import AutoModel, AutoTokenizer

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


class TrustChainVectorizer:
    """Class to vectorize trust chain principles and calculate alignment."""
    
    def __init__(self, embedding_model: XLMRobertaEmbedding):
        """
        Initialize the vectorizer with an embedding model.
        
        Args:
            embedding_model: An initialized XLMRobertaEmbedding instance
        """
        self.embedding_model = embedding_model
        self.principle_embeddings = {}
        self.principle_texts = {}
        self.chain_modules = {}  # Maps chain IDs to their file paths
        
    def discover_trust_chains(self, directory_path: str) -> Dict[str, str]:
        """
        Discover all trust chain markdown files in a directory.
        
        Args:
            directory_path: Path to directory containing trust chain files
            
        Returns:
            Dictionary mapping chain IDs to their file paths
        """
        # Make sure the directory exists
        if not os.path.isdir(directory_path):
            raise ValueError(f"Directory not found: {directory_path}")
        
        # Find all markdown files in the directory and subdirectories
        chain_files = glob.glob(os.path.join(directory_path, "**", "*.md"), recursive=True)
        
        # Extract chain IDs from filenames
        chain_modules = {}
        for file_path in chain_files:
            filename = os.path.basename(file_path)
            # Look for pattern like tc-1-name.md or tc-2-another-name.md
            match = re.match(r'tc-(\d+)-(.*?)\.md', filename)
            if match:
                chain_id = f"tc-{match.group(1)}"
                chain_modules[chain_id] = file_path
                
        self.chain_modules = chain_modules
        return chain_modules
    
    def load_trust_chain_principles(self, trust_chain_path: str) -> Dict[str, str]:
        """
        Load trust chain principles from a file or directory.
        
        Args:
            trust_chain_path: Path to a trust chain markdown file or directory
            
        Returns:
            Dictionary mapping principle IDs to their text content
        """
        # If it's a directory, discover all trust chains
        if os.path.isdir(trust_chain_path):
            self.discover_trust_chains(trust_chain_path)
            # Load all discovered trust chains
            all_principles = {}
            for chain_id, file_path in self.chain_modules.items():
                principles = self._load_principles_from_file(file_path, chain_id)
                all_principles.update(principles)
            self.principle_texts = all_principles
            return all_principles
        else:
            # It's a single file, extract chain ID from filename if possible
            filename = os.path.basename(trust_chain_path)
            match = re.match(r'tc-(\d+)-(.*?)\.md', filename)
            chain_id = f"tc-{match.group(1)}" if match else "tc-1"
            
            principles = self._load_principles_from_file(trust_chain_path, chain_id)
            self.principle_texts = principles
            return principles
    
    def _load_principles_from_file(self, file_path: str, chain_id: str) -> Dict[str, str]:
        """
        Load principles from a specific trust chain file.
        
        Args:
            file_path: Path to the trust chain markdown file
            chain_id: ID of the chain (e.g., tc-1)
            
        Returns:
            Dictionary mapping principle IDs to their text content
        """
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Simple parser to extract sections with IDs
        sections = re.findall(r'### (\d+\.\d+|\d+) (.+?)(?=\n\n)', content, re.DOTALL)
        
        link_texts = {}
        for section_id, section_text in sections:
            section_id = section_id.strip()
            # Include chain ID in the principle key
            principle_key = f"{chain_id}:{section_id}"
            link_texts[principle_key] = section_text.strip()
            
        return link_texts
    
    def vectorize_principles(self) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for loaded trust chain principles.
        
        Returns:
            Dictionary mapping principle IDs to their embeddings
        """
        if not self.principle_texts:
            raise ValueError("No principles loaded. Call load_trust_chain_principles first.")
        
        # Embed each principle's text
        link_ids = list(self.principle_texts.keys())
        texts = [self.principle_texts[link_id] for link_id in link_ids]
        
        embeddings = self.embedding_model.get_embeddings(texts)
        
        # Create dictionary mapping link IDs to embeddings
        self.principle_embeddings = {link_id: embeddings[i] for i, link_id in enumerate(link_ids)}
        
        return self.principle_embeddings
    
    def parse_ai_responses(self, response_file: str) -> Dict[str, str]:
        """
        Parse AI responses from a file.
        
        Args:
            response_file: Path to file containing AI responses
            
        Returns:
            Dictionary mapping principle IDs to AI responses
        """
        with open(response_file, 'r') as f:
            content = f.read()
        
        # Parse responses with format [TC-#:LINK-#] Response text
        responses = {}
        matches = re.findall(r'\[(TC-\d+):(\d+\.\d+|\d+)\]\s*(.+?)(?=\n\[|$)', content, re.DOTALL | re.MULTILINE)
        
        for tc, link, response in matches:
            tc = tc.lower()
            link_id = link.strip()
            key = f"{tc}:{link_id}"
            responses[key] = response.strip()
            
        return responses
    
    def calculate_alignment(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate alignment scores between AI responses and trust chain principles.
        
        Args:
            responses: Dictionary mapping principle IDs to AI responses
            
        Returns:
            Alignment data including overall score and individual principle scores
        """
        if not self.principle_embeddings:
            raise ValueError("No principle embeddings available. Call vectorize_principles first.")
        
        # Calculate similarity for each principle with a response
        alignment_vectors = []
        chain_weights = {}  # Weights for each trust chain module
        
        # Set weights based on chain ID (tc-1 has highest weight, decreasing for higher numbers)
        for principle_id in self.principle_embeddings:
            if ":" in principle_id:
                chain_id = principle_id.split(":")[0]
                if chain_id not in chain_weights:
                    # Extract chain number
                    match = re.match(r'tc-(\d+)', chain_id)
                    if match:
                        chain_num = int(match.group(1))
                        # Decrease weight for higher chain numbers
                        chain_weights[chain_id] = 1.0 / (1.0 + 0.2 * (chain_num - 1))
                    else:
                        chain_weights[chain_id] = 1.0
        
        # Default for any chain not matched
        default_weight = 1.0
        
        for principle_id, principle_embedding in self.principle_embeddings.items():
            # Default value if no response for this principle
            similarity = 0.0
            
            # Extract chain ID and link ID
            if ":" in principle_id:
                chain_id, link_id = principle_id.split(":")
            else:
                chain_id = "tc-1"
                link_id = principle_id
                
            # Get chain weight
            chain_weight = chain_weights.get(chain_id, default_weight)
            
            # Check for matching response
            for response_key, response_text in responses.items():
                if link_id in response_key:
                    # Embed response and calculate similarity
                    response_embedding = self.embedding_model.get_embeddings([response_text])[0]
                    similarity = self.embedding_model.similarity(principle_embedding, response_embedding)
                    break
            
            # Add to alignment vectors
            alignment_vectors.append({
                "tc": chain_id,
                "link": link_id,
                "value": float(similarity),
                "weight": float(chain_weight)
            })
        
        # Calculate weighted average for overall score
        total_weight = 0.0
        weighted_sum = 0.0
        
        for vector in alignment_vectors:
            weight = vector["weight"]
            value = vector["value"]
            weighted_sum += weight * value
            total_weight += weight
            
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Return alignment data
        return {
            "model": "xlm-roberta-base",
            "overall": overall_score,
            "vectors": alignment_vectors
        }
    
    def save_embeddings(self, output_file: str) -> None:
        """
        Save principle embeddings to a file.
        
        Args:
            output_file: Path to save the embeddings
        """
        # Convert numpy arrays to lists for JSON serialization
        serializable_embeddings = {k: v.tolist() for k, v in self.principle_embeddings.items()}
        
        with open(output_file, 'w') as f:
            json.dump(serializable_embeddings, f)
        
        print(f"Embeddings saved to {output_file}") 