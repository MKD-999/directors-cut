from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
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

# --- LOAD DATA ---
with open("model_artifacts.pkl", "rb") as f:
    assets = pickle.load(f)

movies = assets["movies"]
ratings_df = assets["ratings"]
tfidf_vectors = assets["tfidf_vectors"]
title_mapping = assets["title_mapping"]
all_titles = assets["all_titles"]


# --- ROOT ---
@app.get("/")
def root():
    return {"message": "CINEPHILEX API running"}


# --- SEARCH (UNCHANGED LOGIC, FULL DATA RETURN) ---
@app.get("/search")
def search_movies(query: str):
    matches = process.extract(query, all_titles, limit=18, scorer=fuzz.token_set_ratio)
    valid_titles = [title_mapping[m[0]] for m in matches if m[1] > 55]

    results = []
    for t in valid_titles:
        m = movies[movies['title'] == t].iloc[0]

        results.append({
            "title": t,
            "poster": m["poster_path"],
            "overview": m["overview_raw"],
            "tagline": m["tagline"],   
            "genres": m["genres"]      
        })

    return results


# --- INPUT MODEL ---
class UserInput(BaseModel):
    movies: dict  # {title: rating}


# --- RECOMMENDER (100% ORIGINAL LOGIC) ---
@app.post("/recommend")
def recommend(data: UserInput):
    user_movies = data.movies

    new_user_id = ratings_df["userId"].max() + 1

    new_ratings = [
        {
            "userId": new_user_id,
            "movieId": movies[movies['title'] == k].iloc[0]["movie_id"],
            "rating": v
        }
        for k, v in user_movies.items()
    ]

    combined = pd.concat([ratings_df, pd.DataFrame(new_ratings)], ignore_index=True)

    reader = Reader(rating_scale=(0.5, 5))
    dataset = Dataset.load_from_df(combined[['userId', 'movieId', 'rating']], reader)
    trainset = dataset.build_full_trainset()

    algo = SVD()
    algo.fit(trainset)

    best = max(user_movies, key=user_movies.get)
    idx = movies[movies['title'] == best].index[0]

    sim = cosine_similarity(tfidf_vectors[idx], tfidf_vectors).flatten()

    rated_ids = [r["movieId"] for r in new_ratings]
    candidates = movies[~movies["movie_id"].isin(rated_ids)].copy()   

    scores = []
    for i2, row in candidates.iterrows():
        cf = algo.predict(new_user_id, row["movie_id"]).est
        cb = sim[i2]
        pop = row.get("popularity_norm", 0) 
        wr = row.get("weighted_rating", 0) / 10

        
        scores.append(0.35 * cb + 0.25 * cf + 0.20 * wr + 0.20 * pop)

    candidates["score"] = scores
    recs = candidates.sort_values("score", ascending=False).head(12)

    return [
        {
            "title": row["title"],
            "poster": row["poster_path"],
            "overview": row["overview_raw"],
            "tagline": row["tagline"]   
        }
        for _, row in recs.iterrows()
    ]