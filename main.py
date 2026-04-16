from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np
import re
from rapidfuzz import process, fuzz
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Dataset, Reader, SVD

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- LOAD DATA (Assets from recommender.py) ---
with open(r"C:\Users\mkdbh\Downloads\MovieRecom\other\model_artifacts.pkl", "rb") as f:
    assets = pickle.load(f)

movies = assets["movies"]
ratings_df = assets["ratings"]
tfidf_vectors = assets["tfidf_vectors"]
title_mapping = assets["title_mapping"]
all_titles = assets["all_titles"]

# --- HELPER FUNCTIONS (Mirrored from recommender.py) ---

def normalize_title(x):
    """Ensures title normalization matches the pickle generation logic."""
    if isinstance(x, str):
        x = x.lower().strip()
        x = x.replace("&", "and")
        x = re.sub(r"[^\w\s]", "", x)
        x = re.sub(r"\s+", " ", x).strip()
        if x.startswith("the "):
            x = x[4:]
        return x
    return ""

def is_same_franchise(title1, title2, threshold=70):
    """Prevents sequels from cluttering recommendations."""
    t1 = normalize_title(title1)
    t2 = normalize_title(title2)
    return fuzz.token_set_ratio(t1, t2) >= threshold

# --- API ENDPOINTS ---

@app.get("/")
def root():
    return {"message": "CINEPHILEX API running"}

@app.get("/search")
def search_movies(query: str):
    matches = process.extract(query, all_titles, limit=18, scorer=fuzz.token_set_ratio)
    valid_titles = [title_mapping[m[0]] for m in matches if m[1] > 55]

    results = []
    for t in valid_titles:
        # Using columns defined in recommender.py
        m = movies[movies['title'] == t].iloc[0]
        results.append({
            "title": t,
            "poster": m.get("poster_path", ""),
            "overview": m.get("overview_raw", ""),
            "tagline": m.get("tagline", ""),   
            "genres": m.get("genres", [])      
        })
    return results

class UserInput(BaseModel):
    movies: dict  # {title: rating}

@app.post("/recommend")
def recommend(data: UserInput):
    user_movies = data.movies
    favorites = list(user_movies.keys())
    
    # 1. Update Ratings & Re-train SVD
    new_user_id = ratings_df["userId"].max() + 1
    new_ratings_list = []
    
    for title, rating in user_movies.items():
        m_id = movies[movies['title'] == title].iloc[0]["movie_id"]
        new_ratings_list.append({"userId": new_user_id, "movieId": m_id, "rating": rating})

    combined_df = pd.concat([ratings_df, pd.DataFrame(new_ratings_list)], ignore_index=True)
    
    reader = Reader(rating_scale=(0.5, 5))
    dataset = Dataset.load_from_df(combined_df[['userId', 'movieId', 'rating']], reader)
    trainset = dataset.build_full_trainset()
    
    algo = SVD()
    algo.fit(trainset)

    # 2. Candidate Pooling (Multi-movie logic from original notebook)
    candidate_pool = []
    SIM_THRESHOLD = 0.15
    
    for fav_title in favorites:
        # Get index for the specific movie
        idx = movies[movies['title'] == fav_title].index[0]
        sim_scores = cosine_similarity(tfidf_vectors[idx], tfidf_vectors).flatten()
        
        # Get top 100 similar movies per favorite
        top_indices = sim_scores.argsort()[-100:][::-1]
        
        count = 0
        for rec_idx in top_indices:
            if sim_scores[rec_idx] < SIM_THRESHOLD or count >= 15:
                break
            
            row = movies.iloc[rec_idx]
            candidate_title = row["title"]
            
            # Skip if already rated or same franchise
            if candidate_title in favorites or any(is_same_franchise(candidate_title, f) for f in favorites):
                continue
            
            # 3. Hybrid Scoring (40/30/20/10 formula)
            pred_raw = algo.predict(new_user_id, row["movie_id"]).est
            pred_norm = min(pred_raw, 5.0) / 5.0
            pop_norm = min(row.get("popularity_norm", 0), 1.0)
            qual_norm = row.get("weighted_rating", 0) # Already normalized 0-1 in recommender.py
            sim_score = sim_scores[rec_idx]

            final_score = (0.40 * sim_score + 0.30 * qual_norm + 0.20 * pred_norm + 0.10 * pop_norm)
            
            # Diversity Tracking
            m_genres = row.get("genres", [])
            primary_genre = m_genres[0] if isinstance(m_genres, list) and len(m_genres) > 0 else "Unknown"
            
            candidate_pool.append({
                "title": candidate_title,
                "score": final_score,
                "genre": primary_genre,
                "poster": row.get("poster_path", ""),
                "overview": row.get("overview_raw", ""),
                "tagline": row.get("tagline", "")
            })
            count += 1

    # 4. Genre Diversity Penalty (From Movie Recommender.py)
    pool_df = pd.DataFrame(candidate_pool).sort_values("score", ascending=False).drop_duplicates("title")
    
    final_recs = []
    genre_counts = {}
    GENRE_LIMIT = 2      
    PENALTY_FACTOR = 0.7 

    for _, row in pool_df.iterrows():
        genre = row["genre"]
        current_score = row["score"]

        if genre_counts.get(genre, 0) >= GENRE_LIMIT:
            current_score *= PENALTY_FACTOR

        final_recs.append({
            "title": row["title"],
            "score": current_score,
            "poster": row["poster"],
            "overview": row["overview"],
            "tagline": row["tagline"]
        })
        genre_counts[genre] = genre_counts.get(genre, 0) + 1

    # Final Sort and Return top 12
    return sorted(final_recs, key=lambda x: x["score"], reverse=True)[:12]
