import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from rank_bm25 import BM25Okapi
import re

# ─────────────────────────────
# LOAD EVERYTHING
# ─────────────────────────────
print("Loading MOONLIT brain...")

df = pd.read_csv("data/knowledge_base_clean.csv")
index = faiss.read_index("data/moonlit.index")

with open("data/model_name.pkl", "rb") as f:
    model_name = pickle.load(f)

model = SentenceTransformer(model_name)

# ─────────────────────────────
# BUILD BM25 INDEX
# ─────────────────────────────
print("Building BM25 keyword index...")

def tokenize(text):
    """Simple tokenizer — lowercase, remove punctuation, split by space"""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.split()

# Tokenize all titles + overviews
corpus = []
for _, row in df.iterrows():
    combined = f"{row['title']} {row['overview']}"
    corpus.append(tokenize(combined))

bm25 = BM25Okapi(corpus)
print("BM25 ready! ✅")
print(f"Total indexed: {len(df)} entries")
print("MOONLIT ready! 🌙\n")

# ─────────────────────────────
# HYBRID SEARCH FUNCTION
# ─────────────────────────────
def search(query, top_k=8, content_filter=None, semantic_weight=0.7):
    """
    Hybrid search combining semantic + BM25 keyword search.
    
    semantic_weight = 0.7 means:
    - 70% trust semantic meaning
    - 30% trust keyword matching
    """
    
    total = len(df)

    # ── SEMANTIC SEARCH ──
    query_embedding = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)
    
    # Get more candidates than needed for re-ranking
    distances, indices = index.search(query_embedding, min(top_k * 10, total))
    
    # Build semantic scores dict {idx: score}
    semantic_scores = {}
    for dist, idx in zip(distances[0], indices[0]):
        if idx != -1:
            semantic_scores[idx] = float(dist)

    # ── BM25 KEYWORD SEARCH ──
    query_tokens = tokenize(query)
    bm25_scores_raw = bm25.get_scores(query_tokens)
    
    # Normalise BM25 scores to 0-1 range
    bm25_max = bm25_scores_raw.max()
    if bm25_max > 0:
        bm25_scores_norm = bm25_scores_raw / bm25_max
    else:
        bm25_scores_norm = bm25_scores_raw

    # ── COMBINE SCORES ──
    keyword_weight = 1 - semantic_weight
    
    combined_scores = {}
    
    # Start with all candidates from semantic search
    for idx in semantic_scores:
        sem_score = semantic_scores[idx]
        kw_score = float(bm25_scores_norm[idx])
        combined_scores[idx] = (semantic_weight * sem_score) + (keyword_weight * kw_score)
    
    # Also add any strong BM25 matches not in semantic results
    top_bm25_indices = np.argsort(bm25_scores_norm)[::-1][:top_k * 5]
    for idx in top_bm25_indices:
        if idx not in combined_scores:
            sem_score = 0.3  # default semantic score for non-semantic results
            kw_score = float(bm25_scores_norm[idx])
            combined_scores[idx] = (semantic_weight * sem_score) + (keyword_weight * kw_score)

    # Sort by combined score
    sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

    # ── BUILD RESULTS ──
    results = []
    for idx, score in sorted_results:
        if len(results) == top_k:
            break
            
        row = df.iloc[idx]
        
        # Apply content filter
        if content_filter and content_filter != "all":
            if str(row.get("type", "")) != content_filter:
                continue

        # Clean poster
        poster = str(row.get("poster", ""))
        if not poster or poster == "nan" or poster == "https://image.tmdb.org/t/p/w500":
            poster = ""

        results.append({
            "title": str(row["title"]),
            "type": str(row.get("type", "movie")),
            "overview": str(row["overview"])[:250] + "...",
            "rating": round(float(row.get("rating", 0) or 0), 1),
            "poster": poster,
            "language": str(row.get("language", "")),
            "similarity": round(score * 100, 1)
        })

    return results


# ─────────────────────────────
# TEST HYBRID SEARCH
# ─────────────────────────────
if __name__ == "__main__":

    print("=" * 55)
    print("TEST 1 — The classic time loop test")
    print("Query: 'man stuck reliving the same day time loop'")
    print("=" * 55)
    results = search("man stuck reliving the same day time loop")
    for r in results[:5]:
        print(f"🎯 {r['title']} ({r['type']}) — {r['similarity']}%")
        print(f"   {r['overview'][:80]}...")

    print("\n" + "=" * 55)
    print("TEST 2 — Vibe search")
    print("Query: 'feeling lonely and nostalgic tonight'")
    print("=" * 55)
    results = search("feeling lonely and nostalgic tonight")
    for r in results[:5]:
        print(f"🌙 {r['title']} ({r['type']}) — {r['similarity']}%")
        print(f"   {r['overview'][:80]}...")

    print("\n" + "=" * 55)
    print("TEST 3 — Korean drama")
    print("Query: 'sad Korean drama rich and poor family'")
    print("=" * 55)
    results = search("sad Korean drama rich and poor family")
    for r in results[:5]:
        print(f"🌍 {r['title']} ({r['type']}) — {r['similarity']}%")
        print(f"   {r['overview'][:80]}...")