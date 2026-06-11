import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os

# Load knowledge base
print("Loading knowledge base...")
df = pd.read_csv("data/knowledge_base_clean.csv")

# Drop rows with empty overviews
df = df.dropna(subset=["overview"])
df = df.reset_index(drop=True)

print(f"Total entries to embed: {len(df)}")

print("\nLoading multilingual sentence transformer...")
print("(First time = downloads ~500MB model, be patient!)")

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("Model loaded! ✅")
print("\nGenerating embeddings for all content...")
print("This will take 5-10 minutes...")

# Combine title + overview for richer embeddings
# Why? "Inception" alone means less than "Inception — A thief enters dreams"
df["search_text"] = df["title"] + ". " + df["overview"]

texts = df["search_text"].tolist()

# Generate embeddings in batches
# batch_size=64 means 64 descriptions at a time — efficient memory usage
embeddings = model.encode(
    texts,
    batch_size=64,
    show_progress_bar=True,  # shows a progress bar!
    convert_to_numpy=True
)

print(f"\nEmbeddings shape: {embeddings.shape}")
# Should print: (total_entries, 384)
# 384 = dimensions of each embedding vector

print("\nBuilding FAISS index...")

# Get the dimension of our embeddings (384)
dimension = embeddings.shape[1]

# Normalise embeddings — makes similarity search more accurate
# Think of it as putting all vectors on the same scale
faiss.normalize_L2(embeddings)

# Create FAISS index
# IndexFlatIP = Inner Product similarity (cosine similarity after normalisation)
index = faiss.IndexFlatIP(dimension)

# Add all embeddings to the index
index.add(embeddings)

print(f"FAISS index built with {index.ntotal} vectors ✅")
print("\nSaving everything...")

# Save embeddings matrix
np.save("data/embeddings.npy", embeddings)

# Save FAISS index
faiss.write_index(index, "data/moonlit.index")

# Save the dataframe (we need it to look up titles after search)
df.to_csv("data/knowledge_base_clean.csv", index=False)

# Save model name for later use
with open("data/model_name.pkl", "wb") as f:
    pickle.dump('paraphrase-multilingual-MiniLM-L12-v2', f)

print("Saved!")
print("  → data/embeddings.npy")
print("  → data/moonlit.index")
print("  → data/knowledge_base_clean.csv")
print("\nMOONLIT brain is ready! 🌙✅")

