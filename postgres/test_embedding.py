from dummy_mentor_data import generate_realistic_embedding
import numpy as np

# Generate one embedding
emb = generate_realistic_embedding()

# Check it
print(f"Length: {len(emb)}")
print(f"Type: {type(emb)}")
print(f"First 10 numbers: {emb[:10]}")
print(f"Norm (should be ~1.0): {np.linalg.norm(emb):.4f}")
