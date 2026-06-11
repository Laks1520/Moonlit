from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from rank_bm25 import BM25Okapi
import re
import os

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

# ─────────────────────────────
# LOAD MOONLIT BRAIN
# ─────────────────────────────
print("Loading MOONLIT brain...")

df = pd.read_csv("data/knowledge_base_clean.csv")
index = faiss.read_index("data/moonlit.index")

with open("data/model_name.pkl", "rb") as f:
    model_name = pickle.load(f)

model = SentenceTransformer(model_name)

# Build BM25 index
print("Building BM25 index...")

def tokenize(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.split()

corpus = []
for _, row in df.iterrows():
    combined = f"{row['title']} {row['overview']}"
    corpus.append(tokenize(combined))

bm25 = BM25Okapi(corpus)
print("MOONLIT ready! 🌙")

# ─────────────────────────────
# HYBRID SEARCH
# ─────────────────────────────
def search(query, top_k=8, content_filter=None, semantic_weight=0.7):
    total = len(df)

    # Semantic search
    query_embedding = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)
    distances, indices = index.search(query_embedding, min(top_k * 10, total))

    semantic_scores = {}
    for dist, idx in zip(distances[0], indices[0]):
        if idx != -1:
            semantic_scores[idx] = float(dist)

    # BM25 search
    query_tokens = tokenize(query)
    bm25_scores_raw = bm25.get_scores(query_tokens)
    bm25_max = bm25_scores_raw.max()
    bm25_scores_norm = bm25_scores_raw / bm25_max if bm25_max > 0 else bm25_scores_raw

    # Combine
    keyword_weight = 1 - semantic_weight
    combined_scores = {}

    for idx in semantic_scores:
        sem = semantic_scores[idx]
        kw = float(bm25_scores_norm[idx])
        combined_scores[idx] = (semantic_weight * sem) + (keyword_weight * kw)

    top_bm25 = np.argsort(bm25_scores_norm)[::-1][:top_k * 5]
    for idx in top_bm25:
        if idx not in combined_scores:
            combined_scores[idx] = (semantic_weight * 0.3) + (keyword_weight * float(bm25_scores_norm[idx]))

    sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for idx, score in sorted_results:
        if len(results) == top_k:
            break

        row = df.iloc[idx]

        if content_filter and content_filter != "all":
            if str(row.get("type", "")) != content_filter:
                continue
            
            # Filter out adult content
        adult_keywords = ['erotic', 'pornographic', 'adult film', 
                  'xxx', 'explicit sexual', 'softcore', 'hardcore']
        overview_lower = str(row.get("overview", "")).lower()
        title_lower = str(row["title"]).lower()
        if any(kw in overview_lower or kw in title_lower for kw in adult_keywords):
            continue

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
# ROUTES
# ─────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search_route():
    data = request.get_json()
    query = data.get("query", "").strip()
    mode = data.get("mode", "find")
    content_filter = data.get("filter", "all")

    if not query:
        return jsonify({"error": "Please enter something!"}), 400

    results = search(query, top_k=8, content_filter=content_filter)

    return jsonify({
        "results": results,
        "query": query,
        "mode": mode,
        "count": len(results)
    })

if __name__ == "__main__":
    app.run(debug=False)