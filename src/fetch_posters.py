import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()

TMDB_KEY = os.getenv("TMDB_API_KEY")

df = pd.read_csv("data/knowledge_base_clean.csv")

# Find rows with missing posters
mask = df['poster'].isna() | (df['poster'] == '') | (df['poster'] == 'nan') | (df['poster'] == 'https://image.tmdb.org/t/p/w500')
missing = df[mask & (df['type'] != 'book')]
print(f"Missing posters: {len(missing)}")

def fetch_poster(title, content_type):
    try:
        endpoint = 'movie' if content_type == 'movie' else 'tv'
        url = f"https://api.themoviedb.org/3/search/{endpoint}"
        params = {"api_key": TMDB_KEY, "query": title}
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results and results[0].get("poster_path"):
                return f"https://image.tmdb.org/t/p/w500{results[0]['poster_path']}"
    except:
        pass
    return ""

count = 0
for idx in missing.index:
    poster = fetch_poster(df.loc[idx, 'title'], df.loc[idx, 'type'])
    if poster:
        df.loc[idx, 'poster'] = poster
        count += 1
    time.sleep(0.08)
    if count % 100 == 0 and count > 0:
        df.to_csv("data/knowledge_base_clean.csv", index=False)
        print(f"Saved {count} posters so far...")

df.to_csv("data/knowledge_base_clean.csv", index=False)
print(f"Done! Filled {count} posters ✅")