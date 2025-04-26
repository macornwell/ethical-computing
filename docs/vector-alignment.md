## Vector Embedding Model

The Trust Chain certification process uses the **XLM-RoBERTa-base** model for generating vector embeddings. This model was specifically selected for several key reasons:

- **Cross-lingual Biblical Encoder**: The model can process and understand biblical and ethical texts across multiple languages and cultural contexts
- **Multilingual Support**: Built-in support for Hebrew, Greek, and English - languages fundamental to biblical and ethical scholarship
- **Contextual Understanding**: Deep semantic comprehension of ethical principles and their nuances
- **Robust Representation**: Produces high-dimensional vector embeddings that capture the subtle relations between ethical concepts

The `XLMRobertaEmbedding` class in the codebase encapsulates this model, providing methods for:
- Generating embeddings from text
- Calculating similarity between text passages
- Batch processing for efficient analysis
- Mean pooling to create comprehensive text representations

This approach allows for nuanced, quantifiable measurements of how well AI responses align with the established Trust Chain principles. 

## Trust Chain Hierarchical Structure

The vector alignment system supports a hierarchical structure of trust chains:

### Directory-Based Processing

The system can process either:
- A single trust chain file
- An entire directory of trust chain files

Trust chains are automatically discovered based on their filename pattern: `tc-[number]-[name].md`

### Hierarchical Weighting

Trust chains are weighted based on their hierarchy level:
- Primary chains (tc-1) have the highest weight (1.0)
- Secondary chains (tc-2) have reduced weight (0.83)
- Tertiary chains (tc-3) have further reduced weight (0.71)
- And so on with decreasing weights

This weighting system ensures that foundational principles have greater influence on alignment scores than derivative principles.

### Multiple Chain Processing

When processing multiple trust chains:
1. All principles from all chains are embedded
2. AI responses are compared against all principles
3. Weighted alignment scores are calculated
4. Overall alignment considers the hierarchical weight of each principle

## Technical Implementation

The `XLMRobertaEmbedding` class provides the following technical capabilities:

```python
def get_embeddings(self, texts: List[str], batch_size: int = 8) -> np.ndarray:
    # Generates embeddings for a list of texts with batching
    # Returns normalized vector representations

def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    # Calculates cosine similarity between two embeddings
    
def batch_similarity(self, query_embedding: np.ndarray, corpus_embeddings: np.ndarray) -> np.ndarray:
    # Calculates similarities between a query and multiple corpus embeddings
```

The embeddings are generated through mean pooling of the model's token embeddings, with normalization applied to ensure consistent similarity calculations. The model processes text in batches of 8 by default, supporting efficient analysis of large datasets of biblical and ethical text.

These vector representations serve as the foundation for the `TrustChainVectorizer` class, which calculates alignment scores between AI-generated responses and established trust chain principles. The overall alignment score provides a quantitative measure of ethical compliance.

## Usage Example

To analyze alignment using all available trust chains:

```bash
python vectorize_alignment.py --responses /path/to/responses.txt --trust-chains-dir src/trust_chain/chains
```

To use a specific trust chain file:

```bash
python vectorize_alignment.py --responses /path/to/responses.txt --trust-chain src/trust_chain/chains/tc-1-seeds-of-creation.md
```

This produces an alignment report with:
- Overall alignment score
- Per-chain alignment scores
- Individual principle scores with hierarchical weighting
- Detailed vector representations 