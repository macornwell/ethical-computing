import sys
import os
from pathlib import Path

def import_vector_embeddings():
    """
    Dynamically imports the vector_embeddings module by searching
    for it in likely locations if the standard import fails.
    """
    try:
        # Try the standard import first
        from src.trust_chain.lib.vector_embeddings import XLMRobertaEmbedding, TrustChainVectorizer
        print("Successfully imported vector_embeddings from standard location")
        return XLMRobertaEmbedding, TrustChainVectorizer
    except ImportError:
        # List of potential locations to check
        current_dir = Path.cwd()
        
        # Check if we're in a parent directory of ethical-computing
        ethical_dir = current_dir / "ethical-computing"
        if ethical_dir.exists() and ethical_dir.is_dir():
            print(f"Found ethical-computing directory at: {ethical_dir}")
            # Add the ethical-computing directory to the path
            sys.path.append(str(ethical_dir))
            try:
                # Try importing from within ethical-computing
                from src.trust_chain.lib.vector_embeddings import XLMRobertaEmbedding, TrustChainVectorizer
                print("Successfully imported vector_embeddings from ethical-computing/src")
                return XLMRobertaEmbedding, TrustChainVectorizer
            except ImportError:
                pass
        
        # Try a more general approach if that fails
        print("Searching for vector_embeddings.py in various locations...")
        found_paths = []
        # Look for the file in current directory and parent directories
        for _ in range(4):  # Current dir + 3 levels up
            # Look for the module file
            results = list(current_dir.glob("**/vector_embeddings.py"))
            for result in results:
                found_paths.append(result)
            
            # Move up one directory
            if current_dir.parent == current_dir:  # We've reached the root
                break
            current_dir = current_dir.parent
        
        # Try each found path
        for path in found_paths:
            # Add the parent directory to the path
            lib_dir = path.parent
            project_dir = lib_dir.parent.parent  # Assuming structure: project/trust_chain/lib/vector_embeddings.py
            print(f"Trying to import from: {project_dir}")
            sys.path.append(str(project_dir))
            
            try:
                # If the path is like ethical-computing/src/trust_chain/lib/vector_embeddings.py
                if "src" in str(lib_dir):
                    from src.trust_chain.lib.vector_embeddings import XLMRobertaEmbedding, TrustChainVectorizer
                    print(f"Successfully imported vector_embeddings from {project_dir}/src")
                    return XLMRobertaEmbedding, TrustChainVectorizer
                else:
                    # Try a generic import based on directory structure
                    import_path = ".".join(lib_dir.parts[-2:]) + ".vector_embeddings"
                    print(f"Attempting import from: {import_path}")
                    module = __import__(import_path, fromlist=["XLMRobertaEmbedding", "TrustChainVectorizer"])
                    return module.XLMRobertaEmbedding, module.TrustChainVectorizer
            except (ImportError, AttributeError) as e:
                print(f"Import attempt failed: {e}")
                continue
    
    raise ImportError("Could not find vector_embeddings module. Make sure it exists in src/trust_chain/lib/") 