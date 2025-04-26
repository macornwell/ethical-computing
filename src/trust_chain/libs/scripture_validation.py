"""
Scripture Validation Library

Provides functions for validating theological content against scripture references.
Uses vector embeddings to compare AI responses with scriptural passages.
"""

import re
import json
import os
from pathlib import Path

# Import this conditionally since it might not be available in all environments
try:
    from src.trust_chain.services.embedding_services import import_vector_embeddings
except ImportError:
    pass

# Default location for scripture vectors
DEFAULT_SCRIPTURE_VECTOR_PATH = Path(__file__).parent.parent / "data" / "scripture_vectors.json"

class ScriptureValidator:
    """Class for validating content against scripture vectors"""
    
    def __init__(self, vector_path=None):
        """Initialize the scripture validator with vectors"""
        self.vector_path = vector_path or DEFAULT_SCRIPTURE_VECTOR_PATH
        self.scripture_vectors = self._load_scripture_vectors()
        self.embedding_model = self._initialize_embedding_model()
    
    def _load_scripture_vectors(self):
        """Load scripture vectors from JSON file"""
        if not os.path.exists(self.vector_path):
            print(f"Warning: Scripture vector file not found at {self.vector_path}")
            return {}
            
        try:
            with open(self.vector_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading scripture vectors: {e}")
            return {}
    
    def _initialize_embedding_model(self):
        """Initialize the embedding model"""
        try:
            XLMRobertaEmbedding, _ = import_vector_embeddings()
            return XLMRobertaEmbedding()
        except Exception as e:
            print(f"Error initializing embedding model: {e}")
            return None
    
    def validate_content(self, content, threshold=0.7):
        """
        Validate content against scripture vectors
        
        Args:
            content (str): The content to validate
            threshold (float): Similarity threshold for validation
            
        Returns:
            dict: Results including overall score and matched scriptures
        """
        if not self.embedding_model or not self.scripture_vectors:
            return {"score": 0.0, "matches": []}
        
        # Get content embedding
        content_embedding = self.embedding_model.get_embeddings([content])[0]
        
        # Compare with scripture vectors
        matches = []
        total_similarity = 0.0
        
        for reference, data in self.scripture_vectors.items():
            vector = data["vector"]
            text = data["text"]
            
            # Calculate similarity
            similarity = self.embedding_model.similarity(content_embedding, vector)
            
            if similarity >= threshold:
                matches.append({
                    "reference": reference,
                    "text": text,
                    "similarity": float(similarity)
                })
                total_similarity += similarity
        
        # Calculate overall score
        overall_score = total_similarity / max(1, len(matches))
        if len(matches) == 0:
            overall_score = 0.0
            
        # Sort matches by similarity
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        
        return {
            "score": float(overall_score),
            "matches": matches[:10],  # Return top 10 matches
            "match_count": len(matches)
        }
    
    def analyze_theological_alignment(self, content):
        """
        Analyze theological alignment of content with scripture
        
        Args:
            content (str): The content to analyze
            
        Returns:
            float: A score between 0 and 1 representing theological alignment
        """
        results = self.validate_content(content)
        
        # Weight the score based on number of matches
        match_count = results["match_count"]
        base_score = results["score"]
        
        # No matches is a clear indicator of poor alignment
        if match_count == 0:
            return 0.0
            
        # Scale score based on number of matches (square root to dampen effect)
        scaled_score = base_score * min(1.0, (match_count / 10)**0.5)
        
        return scaled_score

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
        XLMRobertaEmbedding, _ = import_vector_embeddings()
        embedding_model = XLMRobertaEmbedding()
    except Exception as e:
        print(f"Error initializing embedding model: {e}")
        return {}
    
    scripture_vectors = {}
    
    for reference, text in scripture_data.items():
        # Generate vector
        vector = embedding_model.get_embeddings([text])[0]
        
        # Save vector
        scripture_vectors[reference] = {
            "text": text,
            "vector": vector.tolist()
        }
    
    # Save to file if path provided
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(scripture_vectors, f, indent=2)
    
    return scripture_vectors

def extract_scripture_references(text):
    """
    Extract potential scripture references from text
    
    Args:
        text (str): The text to extract references from
        
    Returns:
        list: List of potential scripture references
    """
    # Common scripture reference patterns
    patterns = [
        r'([1-3]\s*[A-Za-z]+\s+\d+:\d+(?:-\d+)?)',  # 1 John 3:16-18
        r'([A-Za-z]+\s+\d+:\d+(?:-\d+)?)',          # John 3:16-18
        r'([A-Za-z]+\s+\d+)',                       # Psalm 23
    ]
    
    references = []
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        references.extend(matches)
    
    return references

def check_scripture_references(content):
    """
    Check if content contains scripture references
    
    Args:
        content (str): The content to check
        
    Returns:
        dict: Results including reference count and references
    """
    references = extract_scripture_references(content)
    
    return {
        "reference_count": len(references),
        "references": references
    }

def enhance_commitment_score(base_score, scripture_score):
    """
    Enhance commitment score with scripture validation score
    
    Args:
        base_score (float): Base commitment score
        scripture_score (float): Scripture validation score
        
    Returns:
        float: Enhanced commitment score
    """
    # If scripture score is high but base score is low, this indicates
    # the response uses scriptural language but might lack personal commitment
    if scripture_score > 0.7 and base_score < 0.4:
        # Modest boost but still below threshold
        enhanced_score = base_score * 0.7 + scripture_score * 0.3
    else:
        # Normal weighting - scripture validation can boost score
        enhanced_score = base_score * 0.6 + scripture_score * 0.4
    
    return enhanced_score 