import pandas as pd
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
TMDB_KEY = os.getenv("TMDB_API_KEY")

# ─────────────────────────────
# PART 1 — KAGGLE TMDB DATASET
# ─────────────────────────────
def load_kaggle_movies():
    print("Loading Kaggle TMDB dataset...")
    df = pd.read_csv("data/tmdb_5000_movies.csv")
    
    # Only keep rows with overview
    df = df[df["overview"].notna()]
    df = df[df["overview"].str.len() > 50]
    
    # Standardise columns to match our format
    movies = []
    for _, row in df.iterrows():
        movies.append({
            "id": f"kaggle_{row['id']}",
            "title": row["title"],
            "original_title": row.get("original_title", ""),
            "overview": row["overview"],
            "genre_ids": row.get("genres", []),
            "language": row.get("original_language", "en"),
            "rating": row.get("vote_average", 0),
            "poster": "",  # Kaggle dataset doesn't have poster URLs
            "type": "movie",
            "release_date": str(row.get("release_date", ""))
        })
    
    result = pd.DataFrame(movies)
    print(f"Kaggle movies loaded: {len(result)}")
    return result


# ─────────────────────────────
# PART 2 — ANIME FROM TMDB
# ─────────────────────────────
def fetch_anime(pages=25):
    print("\nFetching anime...")
    anime = []
    
    for page in range(1, pages + 1):
        url = "https://api.themoviedb.org/3/discover/tv"
        params = {
            "api_key": TMDB_KEY,
            "with_genres": "16",          # Animation genre
            "with_original_language": "ja", # Japanese
            "sort_by": "vote_count.desc",
            "page": page
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for show in data.get("results", []):
                    if show.get("overview"):
                        anime.append({
                            "id": f"anime_{show['id']}",
                            "title": show.get("name", ""),
                            "original_title": show.get("original_name", ""),
                            "overview": show["overview"],
                            "genre_ids": show.get("genre_ids", []),
                            "language": "ja",
                            "rating": show.get("vote_average", 0),
                            "poster": f"https://image.tmdb.org/t/p/w500{show.get('poster_path', '')}",
                            "type": "tv_show",
                            "release_date": show.get("first_air_date", "")
                        })
        except Exception as e:
            print(f"Skipping page {page} — {e}")
        time.sleep(0.1)
    
    result = pd.DataFrame(anime)
    print(f"Anime fetched: {len(result)}")
    return result


# ─────────────────────────────
# PART 3 — K-DRAMAS FROM TMDB
# ─────────────────────────────
def fetch_kdramas(pages=25):
    print("\nFetching K-dramas...")
    kdramas = []
    
    for page in range(1, pages + 1):
        url = "https://api.themoviedb.org/3/discover/tv"
        params = {
            "api_key": TMDB_KEY,
            "with_original_language": "ko",
            "sort_by": "vote_count.desc",
            "page": page
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for show in data.get("results", []):
                    if show.get("overview"):
                        kdramas.append({
                            "id": f"kdrama_{show['id']}",
                            "title": show.get("name", ""),
                            "original_title": show.get("original_name", ""),
                            "overview": show["overview"],
                            "genre_ids": show.get("genre_ids", []),
                            "language": "ko",
                            "rating": show.get("vote_average", 0),
                            "poster": f"https://image.tmdb.org/t/p/w500{show.get('poster_path', '')}",
                            "type": "tv_show",
                            "release_date": show.get("first_air_date", "")
                        })
        except Exception as e:
            print(f"Skipping page {page} — {e}")
        time.sleep(0.1)

    result = pd.DataFrame(kdramas)
    print(f"K-dramas fetched: {len(result)}")
    return result


# ─────────────────────────────
# PART 4 — MORE BOOKS
# ─────────────────────────────
def fetch_more_books():
    print("\nFetching more books...")
    books = []
    base_url = "https://openlibrary.org/search.json"
    
    queries = [
        "manga comic", "graphic novel", "young adult",
        "dystopia", "romance korean", "japanese novel",
        "indian author", "magical realism", "coming of age",
        "mythology retelling", "spy thriller", "medical drama",
        "true crime", "philosophy", "poetry collection"
    ]
    
    for query in queries:
        print(f"  → {query}")
        params = {
            "q": query,
            "limit": 50,
            "fields": "key,title,author_name,first_publish_year,subject,ratings_average,cover_i"
        }
        try:
            response = requests.get(base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("docs", []):
                    title = item.get("title", "")
                    subjects = item.get("subject", [])
                    authors = item.get("author_name", ["Unknown"])
                    
                    if subjects and title:
                        description = f"{title} is a book about {', '.join(subjects[:5])}."
                        cover_id = item.get("cover_i", "")
                        poster = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else ""
                        
                        books.append({
                            "id": f"book_{item.get('key', '')}",
                            "title": title,
                            "overview": description,
                            "author": ", ".join(authors[:2]),
                            "genre_ids": subjects[:3],
                            "language": "en",
                            "rating": item.get("ratings_average", 0),
                            "poster": poster,
                            "type": "book",
                            "release_date": str(item.get("first_publish_year", ""))
                        })
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(0.2)
    
    result = pd.DataFrame(books)
    if not result.empty:
        result = result.drop_duplicates(subset="id")
    print(f"Additional books fetched: {len(result)}")
    return result


# ─────────────────────────────
# COMBINE EVERYTHING
# ─────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("MOONLIT — Expanding Knowledge Base")
    print("=" * 55)

    # Load existing knowledge base
    print("\nLoading existing knowledge base...")
    existing = pd.read_csv("data/knowledge_base_clean.csv")
    print(f"Existing entries: {len(existing)}")

    # Fetch all new data
    kaggle_movies = load_kaggle_movies()
    anime = fetch_anime(pages=25)
    kdramas = fetch_kdramas(pages=25)
    more_books = fetch_more_books()

    # Combine everything
    all_data = pd.concat([
        existing,
        kaggle_movies,
        anime,
        kdramas,
        more_books
    ], ignore_index=True)

    # Remove duplicates by title + type
    all_data = all_data.drop_duplicates(subset=["title", "type"])
    all_data = all_data[all_data["overview"].notna()]
    all_data = all_data[all_data["overview"].str.len() > 30]
    all_data = all_data.reset_index(drop=True)

    print(f"\n{'=' * 55}")
    print(f"MOONLIT Expanded Knowledge Base!")
    print(f"Movies:    {len(all_data[all_data['type'] == 'movie'])}")
    print(f"TV/Anime:  {len(all_data[all_data['type'] == 'tv_show'])}")
    print(f"Books:     {len(all_data[all_data['type'] == 'book'])}")
    print(f"TOTAL:     {len(all_data)}")
    print(f"{'=' * 55}")

    # Save expanded knowledge base
    all_data.to_csv("data/knowledge_base_clean.csv", index=False)
    print("\nSaved! Now run embed.py to rebuild the brain 🌙")