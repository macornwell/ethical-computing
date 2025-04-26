#!/usr/bin/env python3
"""
Advanced Scripture Validator

A more targeted approach to validating scripture alignment that focuses on
theological precision rather than just semantic similarity.
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

class AdvancedScriptureValidator:
    """Advanced scripture validation with theological focus"""
    
    def __init__(self, vector_path):
        """Initialize the validator"""
        self.vector_path = vector_path
        self.scripture_vectors = self._load_vectors()
        self.embedding_model = self._init_embedding_model()
        
        # Key theological concepts with positive association scores
        self.theological_concepts = {
            # Core Christian theology concepts
            "trinity": 0.9,
            "jesus christ": 1.0,
            "son of god": 1.0,
            "holy spirit": 0.9,
            "salvation": 0.9,
            "resurrection": 1.0,
            "crucifixion": 1.0,
            "forgiveness of sins": 1.0,
            "eternal life": 0.9,
            "heaven": 0.8,
            "god's love": 0.9,
            "faith in christ": 1.0,
            "grace": 0.9,
            "repentance": 0.9,
            "sin": 0.8,
            "creation": 0.8,
            "gospel": 1.0,
            "kingdom of god": 0.9,
            "prayer": 0.7,
            "word of god": 0.9,
            "scripture": 0.9,
            "commandments": 0.8,
            "discipleship": 0.8,
            
            # Biblical references 
            "new testament": 0.8,
            "old testament": 0.8,
            "bible": 0.8,
            "moses": 0.7,
            "abraham": 0.7,
            "david": 0.7,
            "paul": 0.7,
            "peter": 0.7,
            "john": 0.7,
            "isaiah": 0.7,
            "psalms": 0.7,
            "gospel of": 0.8,
            "epistle": 0.7,
            "revelation": 0.7,
            
            # Common scriptural phrases
            "in the beginning": 0.8,
            "for god so loved": 1.0,
            "kingdom of heaven": 0.9,
            "sermon on the mount": 0.9,
            "love your neighbor": 0.9,
            "forgive": 0.8,
            "blessed are": 0.8,
            "born again": 0.8,
            "as it is written": 0.8,
            "faith, hope, and love": 0.9,
            "image of god": 0.9,
            "fruit of the spirit": 0.9,
            "good news": 0.8,
        }
        
        # Anti-biblical concepts (concepts that contradict Christian theology)
        self.non_biblical_concepts = {
            # General non-christian concepts
            "karma": -0.8,
            "reincarnation": -0.8,
            "nirvana": -0.7,
            "enlightenment": -0.5,  # Context-dependent
            "chakra": -0.8,
            "third eye": -0.8,
            "astrology": -0.7,
            "zodiac": -0.7,
            "spirit guide": -0.6,
            "past life": -0.8,
            "pantheism": -0.8,
            "polytheism": -0.8,
            "multiple gods": -0.8,
            "goddess": -0.7,
            
            # Specific anti-biblical beliefs
            "impersonal god": -0.9,
            "god is energy": -0.8,
            "universe consciousness": -0.7,
            "divine within": -0.7,
            "all paths lead to god": -0.8,
            "no objective truth": -0.8,
            "create your own reality": -0.7,
            "moral relativism": -0.7,
            "humans are gods": -0.9,
            "no sin": -0.9,
            "no need for salvation": -0.9,
            "universe without creator": -0.9,
            "evolved without divine": -0.8,
            "no afterlife": -0.8,
            "no judgment": -0.8,
            "self-salvation": -0.8,
            "works-based salvation": -0.6,  # More nuanced
        }
        
        # Initialize direct scripture reference patterns
        self.reference_patterns = [
            r'([1-3]\s*[A-Za-z]+\s+\d+:\d+(?:-\d+)?)',  # 1 John 3:16-18
            r'([A-Za-z]+\s+\d+:\d+(?:-\d+)?)',          # John 3:16-18
            r'([A-Za-z]+\s+\d+)',                       # Psalm 23
        ]
        
        # Create mapping of scripture reference to vector for quick lookup
        self.reference_embeddings = {}
        for reference, data in self.scripture_vectors.items():
            self.reference_embeddings[reference] = np.array(data["vector"])
        
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
    
    def validate_content(self, content):
        """
        Validate content against scripture and theological concepts
        
        Args:
            content: The content to validate
            
        Returns:
            dict: Validation results
        """
        if not self.embedding_model or not self.scripture_vectors:
            return {
                "score": 0,
                "explanation": "Validation tools not properly initialized",
            }
        
        # 1. Check for direct scripture references
        scripture_references = self._extract_scripture_references(content)
        
        # 2. Check for theological concept matches
        theological_concepts = self._check_theological_concepts(content)
        
        # 3. Check for non-biblical concept matches
        non_biblical_concepts = self._check_non_biblical_concepts(content)
        
        # 4. Generate content embedding and compare with scripture
        content_embedding = self.embedding_model.get_embeddings([content])[0]
        semantic_matches = self._get_semantic_matches(content_embedding)
        
        # 5. Generate verification quotes for top matches
        verification_quotes = self._generate_verification(semantic_matches, content)
        
        # 6. Calculate scores
        vector_score = self._calculate_vector_score(semantic_matches)
        concept_score = self._calculate_concept_score(theological_concepts, non_biblical_concepts)
        reference_score = min(1.0, len(scripture_references) * 0.2)  # Cap at 1.0
        
        # Calculate overall score with weighted components
        weights = {
            "vector": 0.5,     # Semantic similarity is important but can be misleading
            "concept": 0.4,    # Theological concepts are strong indicators
            "reference": 0.1   # Scripture references provide a bonus
        }
        
        overall_score = (
            vector_score * weights["vector"] + 
            concept_score * weights["concept"] + 
            reference_score * weights["reference"]
        )
        
        # Normalize to 0-1 range in case of negative scores from non-biblical concepts
        overall_score = max(0.0, min(1.0, overall_score))
        
        # Generate explanation
        explanation = self._generate_explanation(
            overall_score, 
            vector_score,
            concept_score, 
            theological_concepts, 
            non_biblical_concepts,
            semantic_matches, 
            scripture_references
        )
        
        return {
            "score": float(overall_score),
            "explanation": explanation,
            "vector_score": float(vector_score),
            "concept_score": float(concept_score),
            "reference_score": float(reference_score),
            "theological_concepts": theological_concepts,
            "non_biblical_concepts": non_biblical_concepts,
            "scripture_references": scripture_references,
            "top_matches": semantic_matches[:5],
            "verification_quotes": verification_quotes
        }
    
    def _extract_scripture_references(self, text):
        """Extract scripture references from text"""
        references = []
        
        for pattern in self.reference_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                references.append(match.strip())
        
        return references
    
    def _check_theological_concepts(self, content):
        """Check for theological concepts in content"""
        matched_concepts = {}
        content_lower = content.lower()
        
        for concept, weight in self.theological_concepts.items():
            if concept.lower() in content_lower:
                matched_concepts[concept] = weight
        
        return matched_concepts
    
    def _check_non_biblical_concepts(self, content):
        """Check for non-biblical concepts in content"""
        matched_concepts = {}
        content_lower = content.lower()
        
        for concept, weight in self.non_biblical_concepts.items():
            if concept.lower() in content_lower:
                matched_concepts[concept] = weight
        
        return matched_concepts
    
    def _get_semantic_matches(self, content_embedding, top_n=10, threshold=0.97):
        """Get top semantic matches for content embedding"""
        matches = []
        
        for reference, data in self.scripture_vectors.items():
            vector = np.array(data["vector"])
            text = data["text"]
            
            # Calculate similarity
            similarity = float(self.embedding_model.similarity(content_embedding, vector))
            
            if similarity >= threshold:
                matches.append({
                    "reference": reference,
                    "text": text,
                    "similarity": similarity
                })
        
        # Sort by similarity
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        
        return matches[:top_n]
    
    def _calculate_vector_score(self, matches):
        """Calculate score based on vector matches"""
        if not matches:
            return 0.0
        
        # Weight top matches more heavily
        weights = [0.5, 0.3, 0.2]  # Top 3 matches get 50%, 30%, 20% weight
        
        if len(matches) == 1:
            return matches[0]["similarity"]
        elif len(matches) == 2:
            normalized_weights = [0.7, 0.3]  # Adjust for only 2 matches
            return sum(m["similarity"] * w for m, w in zip(matches[:2], normalized_weights))
        else:
            return sum(m["similarity"] * w for m, w in zip(matches[:3], weights))
    
    def _calculate_concept_score(self, theological_concepts, non_biblical_concepts):
        """Calculate score based on theological and non-biblical concepts"""
        positive_score = sum(theological_concepts.values()) / max(1, len(theological_concepts) * 2)
        negative_score = sum(non_biblical_concepts.values()) / max(1, len(non_biblical_concepts))
        
        # Combine scores - non-biblical concepts have direct negative impact
        return positive_score + negative_score  # Negative score is already negative
    
    def _generate_verification(self, matches, content):
        """Generate verification quotes for matches"""
        quotes = []
        
        if matches:
            for match in matches[:3]:  # Top 3 matches
                reference = match["reference"]
                text = match["text"]
                similarity = match["similarity"]
                
                quotes.append({
                    "reference": reference,
                    "text": text,
                    "similarity": similarity
                })
        
        return quotes
    
    def _generate_explanation(
        self, overall_score, vector_score, concept_score, 
        theological_concepts, non_biblical_concepts, 
        semantic_matches, scripture_references
    ):
        """Generate explanation for validation results"""
        # Determine alignment level
        if overall_score >= 0.8:
            alignment = "strong"
        elif overall_score >= 0.6:
            alignment = "moderate"
        elif overall_score >= 0.3:
            alignment = "weak"
        else:
            alignment = "minimal or no"
            
        explanation = f"Content shows {alignment} alignment with biblical theology. "
        
        # Add details about matching concepts
        if theological_concepts:
            top_concepts = sorted(theological_concepts.items(), key=lambda x: x[1], reverse=True)[:3]
            concept_str = ", ".join([f"'{c}'" for c, _ in top_concepts])
            explanation += f"Contains biblical concepts: {concept_str}. "
        else:
            explanation += "No specific biblical theological concepts identified. "
            
        # Add details about conflicting concepts
        if non_biblical_concepts:
            top_conflicts = sorted(non_biblical_concepts.items(), key=lambda x: x[1])[:3]
            conflict_str = ", ".join([f"'{c}'" for c, _ in top_conflicts])
            explanation += f"Contains concepts that conflict with biblical theology: {conflict_str}. "
            
        # Add details about semantic matches
        if semantic_matches:
            top_match = semantic_matches[0]
            explanation += f"Most similar to {top_match['reference']} ({top_match['similarity']:.2f}). "
        else:
            explanation += "No strong semantic matches with scripture passages. "
            
        # Add details about direct references
        if scripture_references:
            ref_str = ", ".join([f"'{r}'" for r in scripture_references[:3]])
            explanation += f"Directly references scripture: {ref_str}."
            
        return explanation

# Test statements with varying degrees of theological alignment
TEST_STATEMENTS = [
    {
        "name": "Direct Scripture Quote",
        "text": "In the beginning God created the heavens and the earth. He created mankind in His own image, in the image of God He created them; male and female He created them."
    },
    {
        "name": "Biblical Salvation",
        "text": "For God so loved the world that He gave His one and only Son, that whoever believes in Him shall not perish but have eternal life. Jesus Christ's crucifixion and resurrection provides salvation and forgiveness of sins."
    },
    {
        "name": "Christian Theology",
        "text": "Through faith in Jesus Christ, we receive salvation by grace, not by works. The Holy Spirit guides believers to live according to God's Word and share the Gospel with others."
    },
    {
        "name": "Biblical Principles",
        "text": "Love your neighbor as yourself. Show compassion to those in need, as Christ taught us to do. We should forgive others as God has forgiven us through Jesus."
    },
    {
        "name": "Partially Aligned Statement",
        "text": "God loves everyone and wants us to be happy and prosperous. Everything happens for a reason according to His plan. If we are good people, God will bless us with success."
    },
    {
        "name": "Generic Spiritual Statement",
        "text": "There is a divine force guiding the universe that we should acknowledge through meditation and good deeds. When we connect with the spiritual realm, we find inner peace."
    },
    {
        "name": "Naturalistic Statement",
        "text": "The universe operates according to natural laws, and humanity evolved through natural selection without divine intervention. Science provides the framework for understanding reality."
    },
    {
        "name": "Mixed Religious Concepts",
        "text": "God is an impersonal energy that exists in all things. We must balance our karma through right action to achieve enlightenment. Jesus was an enlightened master who showed one path to spiritual truth."
    },
    {
        "name": "New Age Spirituality",
        "text": "We are all divine beings having a human experience. Through past lives and reincarnation, our souls evolve toward higher consciousness. The universe consciousness responds to our intentions and vibrations."
    }
]

def main():
    """Main function to test the advanced scripture validator"""
    print("Testing Advanced Scripture Validator")
    
    # Define the path to our generated vectors file
    vector_path = Path(current_dir) / "data" / "scripture_vectors.json"
    
    if not vector_path.exists():
        print(f"Error: Vector file not found at {vector_path}")
        return
        
    # Initialize the validator
    validator = AdvancedScriptureValidator(vector_path)
    
    if not validator.scripture_vectors:
        print("Error: No scripture vectors loaded. Make sure the vectors file exists.")
        return
    
    print(f"Loaded {len(validator.scripture_vectors)} scripture vectors.")
    print(f"Defined {len(validator.theological_concepts)} biblical concepts.")
    print(f"Defined {len(validator.non_biblical_concepts)} non-biblical concepts.")
    print("-" * 80)
    
    # Process each test statement
    results = []
    biblical_scores = []
    nonbiblical_scores = []
    
    for i, statement in enumerate(TEST_STATEMENTS):
        print(f"Testing: {statement['name']}")
        print(f"Statement: {statement['text']}")
        
        # Validate the statement
        validation_result = validator.validate_content(statement['text'])
        
        # Print results
        print(f"Score: {validation_result['score']:.4f}")
        print(f"Explanation: {validation_result['explanation']}")
        print(f"Vector Score: {validation_result['vector_score']:.4f}")
        print(f"Concept Score: {validation_result['concept_score']:.4f}")
        print(f"Reference Score: {validation_result['reference_score']:.4f}")
        
        # Print theological concepts
        if validation_result['theological_concepts']:
            concepts = [f"{c} ({s:.2f})" for c, s in validation_result['theological_concepts'].items()]
            print(f"Theological Concepts: {', '.join(concepts[:5])}")
        else:
            print("No theological concepts found.")
            
        # Print non-biblical concepts
        if validation_result['non_biblical_concepts']:
            concepts = [f"{c} ({s:.2f})" for c, s in validation_result['non_biblical_concepts'].items()]
            print(f"Non-Biblical Concepts: {', '.join(concepts)}")
        
        # Print top matches
        if validation_result['top_matches']:
            top_matches = validation_result['top_matches'][:3]
            match_strings = [f"{m['reference']} ({m['similarity']:.4f})" for m in top_matches]
            print(f"Top Matching References: {', '.join(match_strings)}")
        else:
            print("No matching references found.")
            
        print("-" * 80)
        
        # Track scores for biblical/non-biblical statements
        if i < 4:  # First 4 are biblical
            biblical_scores.append(validation_result["score"])
        else:  # Rest are non-biblical
            nonbiblical_scores.append(validation_result["score"])
        
        # Store results
        results.append({
            "name": statement["name"],
            "text": statement["text"],
            "score": validation_result["score"],
            "explanation": validation_result["explanation"],
            "vector_score": validation_result["vector_score"],
            "concept_score": validation_result["concept_score"],
            "reference_score": validation_result["reference_score"],
            "theological_concepts": validation_result["theological_concepts"],
            "non_biblical_concepts": validation_result["non_biblical_concepts"],
            "top_matches": [
                {
                    "reference": m["reference"],
                    "similarity": m["similarity"],
                    "text": m["text"][:100] + "..." if len(m["text"]) > 100 else m["text"]
                } 
                for m in validation_result["top_matches"]
            ]
        })
    
    # Calculate the differentiation
    avg_biblical = sum(biblical_scores) / len(biblical_scores) if biblical_scores else 0
    avg_nonbiblical = sum(nonbiblical_scores) / len(nonbiblical_scores) if nonbiblical_scores else 0
    differentiation = avg_biblical - avg_nonbiblical
    
    print(f"Average biblical score: {avg_biblical:.4f}")
    print(f"Average non-biblical score: {avg_nonbiblical:.4f}")
    print(f"Differentiation: {differentiation:.4f}")
    
    # Save results to file
    output_path = Path(current_dir) / "test_results" / "advanced_validation_results.json"
    with open(output_path, 'w') as f:
        output = {
            "differentiation": differentiation,
            "avg_biblical": avg_biblical,
            "avg_nonbiblical": avg_nonbiblical,
            "results": results
        }
        json.dump(output, f, indent=2)
    
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main() 