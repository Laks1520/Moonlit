import requests
import pandas as pd
import os
from dotenv import load_dotenv
import time

load_dotenv()

TMDB_KEY = os.getenv("TMDB_API_KEY")

# ─────────────────────────────────────────
# PART 1 — FETCH MOVIES FROM TMDB
# ─────────────────────────────────────────

def fetch_movies_by_language(language_code, pages=20):
    """Fetch movies for a specific language"""
    movies = []
    base_url = "https://api.themoviedb.org/3"
    
    endpoints = ["/movie/popular", "/movie/top_rated"]
    
    for endpoint in endpoints:
        for page in range(1, pages + 1):
            url = f"{base_url}{endpoint}"
            params = {
                "api_key": TMDB_KEY,
                "language": "en-US",  # descriptions in English
                "with_original_language": language_code,  # but filter by original language
                "page": page
            }
            try:
                response = requests.get(url, params=params, timeout=10)
            except Exception as e:
                print(f"Skipping page {page} — {e}")
                continue
            if response.status_code == 200:
                data = response.json()
                for movie in data.get("results", []):
                    if movie.get("overview"):
                        movies.append({
                            "id": movie["id"],
                            "title": movie["title"],
                            "original_title": movie.get("original_title", ""),
                            "overview": movie["overview"],
                            "genre_ids": movie.get("genre_ids", []),
                            "language": language_code,
                            "rating": movie.get("vote_average"),
                            "poster": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}",
                            "type": "movie",
                            "release_date": movie.get("release_date", "")
                        })
            time.sleep(0.1)
    
    return movies


def fetch_tv_shows_by_language(language_code, pages=20):
    """Fetch TV shows / dramas for a specific language"""
    shows = []
    base_url = "https://api.themoviedb.org/3"
    
    endpoints = ["/tv/popular", "/tv/top_rated"]
    
    for endpoint in endpoints:
        for page in range(1, pages + 1):
            url = f"{base_url}{endpoint}"
            params = {
                "api_key": TMDB_KEY,
                "language": "en-US",
                "with_original_language": language_code,
                "page": page
            }
            try:
                response = requests.get(url, params=params, timeout=10)
            except Exception as e:
                print(f"Skipping page {page} — {e}")
                continue
            
            if response.status_code == 200:
                data = response.json()
                for show in data.get("results", []):
                    if show.get("overview"):
                        shows.append({
                            "id": f"tv_{show['id']}",
                            "title": show.get("name", ""),
                            "original_title": show.get("original_name", ""),
                            "overview": show["overview"],
                            "genre_ids": show.get("genre_ids", []),
                            "language": language_code,
                            "rating": show.get("vote_average"),
                            "poster": f"https://image.tmdb.org/t/p/w500{show.get('poster_path', '')}",
                            "type": "tv_show",
                            "release_date": show.get("first_air_date", "")
                        })
            time.sleep(0.1)
    
    return shows


# ─────────────────────────────────────────
# PART 2 — FETCH BOOKS FROM GOOGLE BOOKS
# ─────────────────────────────────────────

def fetch_books(queries=None):
    books = []
    base_url = "https://openlibrary.org/search.json"
    
    if queries is None:
        queries = [
            "fiction", "mystery", "romance", "science fiction",
            "fantasy", "thriller", "horror", "biography",
            "classic literature", "indian fiction", "adventure",
            "psychological", "historical fiction", "crime", "drama"
        ]
    
    for query in queries:
        print(f"Fetching books for: {query}")
        params = {
            "q": query,
            "limit": 40,
            "fields": "key,title,author_name,first_publish_year,subject,ratings_average,cover_i"
        }
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            for item in data.get("docs", []):
                title = item.get("title", "")
                authors = item.get("author_name", ["Unknown"])
                subjects = item.get("subject", [])
                
                # Create a description from subjects
                if subjects and title:
                    description = f"{title} is a book involving {', '.join(subjects[:5])}."
                    cover_id = item.get("cover_i", "")
                    poster = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else ""
                    
                    books.append({
                        "id": item.get("key", ""),
                        "title": title,
                        "overview": description,
                        "author": ", ".join(authors[:2]) if authors else "Unknown",
                        "genre_ids": subjects[:3],
                        "language": "en",
                        "rating": item.get("ratings_average", 0),
                        "poster": poster,
                        "type": "book",
                        "release_date": str(item.get("first_publish_year", ""))
                    })
        
        time.sleep(0.2)
    
    df = pd.DataFrame(books)
    if not df.empty:
        df = df.drop_duplicates(subset="id")
    print(f"\nTotal unique books fetched: {len(df)}")
    return df


# ─────────────────────────────────────────
# PART 3 — COMBINE AND SAVE
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("MOONLIT — Building Global Knowledge Base")
    print("=" * 50)

    all_content = []

    # All languages we support
    languages = {
        "en": "English",
        "ko": "Korean",
        "ja": "Japanese",
        "zh": "Chinese",
        "th": "Thai",
        "tr": "Turkish",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "es": "Spanish",
        "fr": "French",
        "pt": "Portuguese",
        "de": "German",
        "it": "Italian",
        "id": "Indonesian"
    }

    # Fetch movies for ALL languages
    print("\n🎬 Fetching movies across all languages...")
    for code, name in languages.items():
        print(f"  → {name} movies...")
        movies = fetch_movies_by_language(code, pages=15)
        all_content.extend(movies)
        print(f"     Got {len(movies)} movies")

    # Fetch TV shows / dramas for ALL languages
    print("\n📺 Fetching TV shows and dramas across all languages...")
    for code, name in languages.items():
        print(f"  → {name} dramas/shows...")
        shows = fetch_tv_shows_by_language(code, pages=15)
        all_content.extend(shows)
        print(f"     Got {len(shows)} shows")

    # Fetch books
    print("\n📚 Fetching books...")
    books_df = fetch_books()
    books_data = books_df.to_dict('records')
    all_content.extend(books_data)

    # Combine everything
    df = pd.DataFrame(all_content)
    df = df.drop_duplicates(subset="id")

    print(f"\n{'='*50}")
    print(f"MOONLIT Knowledge Base Complete!")
    print(f"Movies:    {len(df[df['type']=='movie'])}")
    print(f"TV Shows:  {len(df[df['type']=='tv_show'])}")
    print(f"Books:     {len(df[df['type']=='book'])}")
    print(f"TOTAL:     {len(df)}")
    print(f"{'='*50}")

    df.to_csv("data/knowledge_base.csv", index=False)
    print("\nSaved to data/knowledge_base.csv ✅")