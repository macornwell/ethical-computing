#!/usr/bin/env python3
"""
Custom Scripture Validator

This module implements a custom approach to validating content against scripture,
with a focus on better differentiating between biblical and non-biblical content.
"""

import json
import sys
import re
from pathlib import Path
import numpy as np

# Add paths to ensure we can import necessary modules
current_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(current_dir))

try:
    from src.trust_chain.lib.vector_embeddings import XLMRobertaEmbedding
except ImportError:
    try:
        from src.trust_chain.services.embedding_services import import_vector_embeddings
        XLMRobertaEmbedding, _ = import_vector_embeddings()
    except ImportError as e:
        print(f"Error importing vector embeddings: {e}")
        sys.exit(1)

class CustomScriptureValidator:
    """Custom scripture validation with enhanced differentiation"""
    
    def __init__(self, vector_path, exact_match_bonus=0.2):
        """
        Initialize the validator
        
        Args:
            vector_path: Path to the scripture vectors file
            exact_match_bonus: Bonus score for exact matches
        """
        self.vector_path = vector_path
        self.exact_match_bonus = exact_match_bonus
        self.scripture_vectors = self._load_vectors()
        self.embedding_model = self._init_embedding_model()
        self.reference_patterns = [
            r'([1-3]\s*[A-Za-z]+\s+\d+:\d+(?:-\d+)?)',  # 1 John 3:16-18
            r'([A-Za-z]+\s+\d+:\d+(?:-\d+)?)',          # John 3:16-18
            r'([A-Za-z]+\s+\d+)',                       # Psalm 23
        ]
        
        # Extract key biblical terms
        self.biblical_terms = self._extract_biblical_terms()
        
    def _load_vectors(self):
        """Load vectors from file"""
        try:
            with open(self.vector_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading vectors: {e}")
            return {}
            
    def _init_embedding_model(self):
        """Initialize the embedding model"""
        try:
            return XLMRobertaEmbedding()
        except Exception as e:
            print(f"Error initializing embedding model: {e}")
            return None
            
    def _extract_biblical_terms(self):
        """Extract key biblical terms from scripture texts"""
        terms = set()
        
        # Common biblical terms that are distinctive
        predefined_terms = {
            "Jesus", "Christ", "God", "Holy Spirit", "sin", "salvation", 
            "gospel", "repent", "faith", "Lord", "crucified", "resurrection",
            "heaven", "eternal life", "Kingdom of God", "disciples", "apostles",
            "baptism", "communion", "Scripture", "prophet", "covenant"
        }
        
        # Add predefined terms
        terms.update(predefined_terms)
        
        # Extract terms from scripture
        if self.scripture_vectors:
            for reference, data in self.scripture_vectors.items():
                # Split text into words
                words = re.findall(r'\b[A-Za-z]+\b', data["text"].lower())
                
                # Add significant words (4+ letters to avoid common words)
                for word in words:
                    if len(word) >= 4 and word not in {"that", "with", "have", "this", 
                                                      "from", "they", "will", "what", 
                                                      "when", "make", "like", "time",
                                                      "more", "other", "into", "some", 
                                                      "than", "were", "your", "them"}:
                        terms.add(word)
        
        return terms
    
    def validate_content(self, content, similarity_threshold=0.99, term_threshold=0.02):
        """
        Validate content against scripture
        
        Args:
            content: The content to validate
            similarity_threshold: Threshold for vector similarity
            term_threshold: Threshold for term proportion
            
        Returns:
            dict: Validation results
        """
        if not self.embedding_model or not self.scripture_vectors:
            return {
                "score": 0,
                "explanation": "Validation tools not properly initialized",
                "matches": [],
                "match_count": 0,
                "biblical_terms": [],
                "term_count": 0
            }
        
        # Check for exact scripture references in content
        references_mentioned = self._extract_scripture_references(content)
        
        # Check for biblical terms
        biblical_terms_found = self._check_biblical_terms(content)
        term_proportion = len(biblical_terms_found) / max(1, len(content.split()))
        
        # Generate content embedding
        content_embedding = self.embedding_model.get_embeddings([content])[0]
        
        # Find matching scripture passages
        matches = []
        similarity_scores = []
        
        for reference, data in self.scripture_vectors.items():
            vector = np.array(data["vector"])
            text = data["text"]
            
            # Calculate vector similarity
            similarity = float(self.embedding_model.similarity(content_embedding, vector))
            
            # Apply bonus for exact matches and mentioned references
            bonus = 0
            
            # Direct quote bonus
            if text in content or any(ref in content for ref in [reference, reference.lower()]):
                bonus += self.exact_match_bonus
                
            # Mentioned reference bonus
            for ref in references_mentioned:
                if ref in reference or reference in ref:
                    bonus += 0.1
            
            # Include if similarity is high enough or there's a substantial bonus
            adjusted_similarity = min(1.0, similarity + bonus)
            if adjusted_similarity >= similarity_threshold:
                matches.append({
                    "reference": reference,
                    "text": text,
                    "similarity": similarity,
                    "adjusted_similarity": adjusted_similarity
                })
                similarity_scores.append(adjusted_similarity)
        
        # Sort matches by adjusted similarity
        matches.sort(key=lambda x: x["adjusted_similarity"], reverse=True)
        
        # Calculate overall score
        if len(similarity_scores) > 0:
            # Weight top matches more heavily
            top_match_weight = 0.4
            other_matches_weight = 0.6
            
            if len(similarity_scores) == 1:
                vector_score = similarity_scores[0]
            else:
                top_match = similarity_scores[0]
                avg_others = sum(similarity_scores[1:]) / max(1, len(similarity_scores) - 1)
                vector_score = (top_match * top_match_weight) + (avg_others * other_matches_weight)
        else:
            vector_score = 0
        
        # Term-based score component
        term_score = min(1.0, term_proportion / term_threshold)
        
        # Overall score combining vector similarity and term usage
        # Weight vector similarity more, but term usage can boost or reduce the score
        vector_weight = 0.7
        term_weight = 0.3
        
        overall_score = (vector_score * vector_weight) + (term_score * term_weight)
        
        # Add penalty for content that's very short
        if len(content.split()) < 10:
            overall_score *= 0.8
        
        # Generate explanation
        explanation = self._generate_explanation(
            overall_score, 
            len(matches), 
            len(biblical_terms_found), 
            term_proportion, 
            references_mentioned
        )
        
        return {
            "score": float(overall_score),
            "explanation": explanation,
            "matches": matches[:10],  # Top 10 matches
            "match_count": len(matches),
            "biblical_terms": biblical_terms_found,
            "term_count": len(biblical_terms_found),
            "term_proportion": float(term_proportion),
            "vector_score": float(vector_score),
            "term_score": float(term_score),
            "references_mentioned": references_mentioned
        }
        
    def _extract_scripture_references(self, text):
        """Extract scripture references from text"""
        references = []
        
        for pattern in self.reference_patterns:
            matches = re.findall(pattern, text)
            references.extend(matches)
        
        return references
    
    def _check_biblical_terms(self, content):
        """Check content for biblical terms"""
        found_terms = []
        content_lower = content.lower()
        
        for term in self.biblical_terms:
            if term.lower() in content_lower:
                found_terms.append(term)
                
        return found_terms
    
    def _generate_explanation(self, score, match_count, term_count, term_proportion, references):
        """Generate an explanation for the score"""
        
        if score > 0.85:
            level = "high"
        elif score > 0.6:
            level = "moderate"
        else:
            level = "low"
            
        explanation = f"Content shows {level} alignment with scripture. "
        
        if match_count > 0:
            explanation += f"Found {match_count} matching scripture passages. "
        else:
            explanation += "No clear scripture passages matched. "
            
        if term_count > 0:
            explanation += f"Contains {term_count} biblical terms. "
        else:
            explanation += "No significant biblical terminology detected. "
            
        if references:
            explanation += f"Explicitly mentions {len(references)} scripture references."
            
        return explanation

# Test statements with varying degrees of theological alignment
TEST_STATEMENTS = [
    {
        "name": "Biblical Creation",
        "text": "In the beginning, God created the heavens and the earth. He created humans in His image."
    },
    {
        "name": "Biblical Salvation",
        "text": "For God so loved the world that He gave His one and only Son, that whoever believes in Him shall not perish but have eternal life."
    },
    {
        "name": "Love and Compassion",
        "text": "Love your neighbor as yourself. Show compassion to those in need, as Christ taught us to do."
    },
    {
        "name": "Sermon on the Mount Reference",
        "text": "Blessed are the poor in spirit, for theirs is the kingdom of heaven. Blessed are those who mourn, for they will be comforted."
    },
    {
        "name": "Partially Aligned Statement",
        "text": "God loves everyone and wants us to be happy and prosperous. Everything happens for a reason according to His plan."
    },
    {
        "name": "Generic Spiritual Statement",
        "text": "There is a divine force guiding the universe that we should acknowledge through meditation and good deeds."
    },
    {
        "name": "Naturalistic Statement",
        "text": "The universe operates according to natural laws, and humanity evolved through natural selection without divine intervention."
    },
    {
        "name": "Mixed Religious Concepts",
        "text": "God is an impersonal energy that exists in all things. We must balance our karma through right action to achieve enlightenment."
    }
]

def main():
    """Main function to test the custom scripture validator"""
    print("Testing Custom Scripture Validator")
    
    # Define the path to our generated vectors file
    vector_path = Path(current_dir) / "data" / "scripture_vectors.json"
    
    if not vector_path.exists():
        print(f"Error: Vector file not found at {vector_path}")
        return
        
    # Initialize the validator
    validator = CustomScriptureValidator(vector_path)
    
    if not validator.scripture_vectors:
        print("Error: No scripture vectors loaded. Make sure the vectors file exists.")
        return
    
    print(f"Loaded {len(validator.scripture_vectors)} scripture vectors.")
    print(f"Identified {len(validator.biblical_terms)} biblical terms.")
    print("-" * 80)
    
    # Process each test statement
    results = []
    for statement in TEST_STATEMENTS:
        print(f"Testing: {statement['name']}")
        print(f"Statement: {statement['text']}")
        
        # Validate the statement
        validation_result = validator.validate_content(statement['text'])
        
        # Print results
        print(f"Score: {validation_result['score']:.4f}")
        print(f"Explanation: {validation_result['explanation']}")
        print(f"Vector Score: {validation_result['vector_score']:.4f}")
        print(f"Term Score: {validation_result['term_score']:.4f}")
        
        if validation_result['matches']:
            top_matches = validation_result['matches'][:3]
            match_strings = [f"{m['reference']} ({m['adjusted_similarity']:.4f})" for m in top_matches]
            print(f"Top Matching References: {', '.join(match_strings)}")
        else:
            print("No matching references found.")
        
        if validation_result['biblical_terms']:
            print(f"Biblical Terms: {', '.join(validation_result['biblical_terms'][:10])}...")
        else:
            print("No biblical terms found.")
            
        print(f"Match Count: {validation_result['match_count']}")
        print("-" * 80)
        
        # Store results
        results.append({
            "name": statement["name"],
            "text": statement["text"],
            "score": validation_result["score"],
            "explanation": validation_result["explanation"],
            "vector_score": validation_result["vector_score"],
            "term_score": validation_result["term_score"],
            "matches": [
                {
                    "reference": m["reference"],
                    "similarity": m["similarity"],
                    "adjusted_similarity": m["adjusted_similarity"],
                    "text": m["text"][:100] + "..." if len(m["text"]) > 100 else m["text"]
                } 
                for m in validation_result["matches"][:5]  # Store top 5 matches with truncated text
            ],
            "match_count": validation_result["match_count"],
            "biblical_terms": validation_result["biblical_terms"][:20],  # Store up to 20 terms
            "term_count": validation_result["term_count"]
        })
    
    # Calculate the differentiation
    biblical_scores = [r["score"] for r in results[:4]]  # First 4 are biblical
    nonbiblical_scores = [r["score"] for r in results[4:]]  # Last 4 are non-biblical
    
    avg_biblical = sum(biblical_scores) / len(biblical_scores)
    avg_nonbiblical = sum(nonbiblical_scores) / len(nonbiblical_scores)
    differentiation = avg_biblical - avg_nonbiblical
    
    print(f"Average biblical score: {avg_biblical:.4f}")
    print(f"Average non-biblical score: {avg_nonbiblical:.4f}")
    print(f"Differentiation: {differentiation:.4f}")
    
    # Save results to file
    output_path = Path(current_dir) / "test_results" / "custom_validation_results.json"
    with open(output_path, 'w') as f:
        output = {
            "differentiation": differentiation,
            "results": results
        }
        json.dump(output, f, indent=2)
    
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main() 