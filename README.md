# 🌙 MOONLIT
### Movies, Our Opinions, Narratives & Literature Intelligence Tool

> *Find what you half-remember. Discover what your mood needs. Across every language and medium.*

---

## 🔗 Live Demo
🌐 **[moonlit.onrender.com](https://moonlit.onrender.com)** *(coming soon)*

---

## 🌙 What is MOONLIT?

MOONLIT is a cross-language, cross-medium semantic search and recommendation system for movies, TV shows, and books.

Unlike traditional recommenders that say *"you watched X, here's Y"* — MOONLIT understands **meaning and emotion.**

You can type:
- *"that anime where a boy fights demons to save his sister"* → finds Demon Slayer
- *"feeling lonely and nostalgic tonight"* → recommends movies matching that exact vibe
- *"sad Korean drama about rich and poor families"* → finds Parasite and similar

---

## ✨ Two Modes

### 🔍 Find It
Describe something you half-remember — a plot, a scene, a feeling — and MOONLIT finds it across 6,234 titles in 15+ languages.

### 🌙 Vibe Me
Tell MOONLIT how you're feeling right now. It reads your emotional state and recommends movies, shows, and books that match your mood.

---

## 🎤 Voice Input
Speak your query instead of typing — MOONLIT uses the browser's Web Speech API to convert your voice to text instantly.

---

## 🧠 How It Works
Your Input (text or voice)
↓
Multilingual Sentence Transformer
(paraphrase-multilingual-MiniLM-L12-v2)
↓
Converts meaning to 384-dimensional vector
↓
Hybrid Search: FAISS Semantic + BM25 Keyword
(70% semantic + 30% keyword)
↓
Top 8 matches ranked by combined score
↓
Results with posters, ratings, full details

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| ML Model | Sentence Transformers (multilingual) |
| Vector Search | FAISS (Facebook AI Similarity Search) |
| Keyword Search | BM25 (rank-bm25) |
| Backend | Flask (Python) |
| Data Sources | TMDB API + Kaggle TMDB Dataset + Open Library |
| Deployment | Render |

---

## 📊 Dataset

| Type | Count |
|---|---|
| 🎬 Movies | 5,967 |
| 📺 TV Shows / Dramas | 993 |
| 📚 Books | 1,047 |
| **Total** | **6,234** |

Languages covered: English, Korean, Japanese, Chinese, Hindi, Tamil, Telugu, Thai, Turkish, Spanish, French, Portuguese, German, Italian, Indonesian

---

## 🚀 What Makes MOONLIT Different

| Feature | Google | Netflix | MyDramaList | MOONLIT |
|---|---|---|---|---|
| Vague description search | ❌ | ❌ | ❌ | ✅ |
| Mood-based recommendations | ❌ | Partial | ❌ | ✅ |
| Cross-language input | Partial | ❌ | ❌ | ✅ |
| Movies + Books together | ❌ | ❌ | ❌ | ✅ |
| Voice input | ✅ | ❌ | ❌ | ✅ |
| Explains why it matched | ❌ | ❌ | ❌ | ✅ |

---

## 📁 Project Structure
moonlit/
├── data/
│   ├── knowledge_base_clean.csv   ← 6,234 titles
│   ├── embeddings.npy             ← meaning vectors
│   └── moonlit.index              ← FAISS search index
├── src/
│   ├── fetch_data.py              ← data collection
│   ├── expand_data.py             ← dataset expansion
│   ├── fetch_posters.py           ← poster fetching
│   ├── embed.py                   ← generate embeddings
│   ├── search.py                  ← hybrid search engine
│   └── app.py                     ← Flask web app
├── templates/
│   └── index.html                 ← frontend UI
├── static/
│   └── style.css                  ← styling
└── README.md

---

## ⚙️ Run Locally

```bash
# Clone the repo
git clone https://github.com/Laks1520/Moonlit.git
cd Moonlit

# Install dependencies
pip install flask sentence-transformers faiss-cpu rank-bm25 pandas numpy requests python-dotenv

# Set up environment
echo "TMDB_API_KEY=your_key_here" > .env

# Fetch data
python src/fetch_data.py
python src/expand_data.py

# Generate embeddings
python src/embed.py

# Run the app
python src/app.py
```

Open `http://127.0.0.1:5000` 🌙

---

## 🔍 Example Searches

**Find It mode:**
- *"man stuck reliving the same day"* → Groundhog Day, Edge of Tomorrow
- *"anime boy becomes strongest hero from being weakest"* → One Punch Man
- *"Korean drama rich girl poor boy hate to love"* → Boys Over Flowers

**Vibe Me mode:**
- *"feeling heartbroken and want to cry"* → Past Lives, Your Name
- *"need something exciting and adventurous"* → Indiana Jones, The Mummy
- *"cozy rainy night warm and comforting"* → Studio Ghibli films



