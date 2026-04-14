
import pandas as pd
import numpy as np
import ast



# Will start with the credits data which contains data about the cast & crew
credits_data = pd.read_csv(r"C:\Users/mkdbh/Downloads/MovieRecom/Data/credits.csv")

# Since the df contains a list of dictionaries for the cast of every movie, we can split the data
# on the keys & make them columns so that we can make more sense of it
credits_data["cast"] = credits_data["cast"].apply(ast.literal_eval)
credits_data["crew"] = credits_data["crew"].apply(ast.literal_eval)

# Arranging the data about the cast & crew of movies into a clean tabular format for
# easier usage

cast_data = credits_data.explode("cast").reset_index(drop= True)
cast_df = pd.json_normalize(cast_data["cast"])
cast_df = pd.concat([cast_data["id"].rename("movie_id"), cast_df], axis= 1)

cast_df.drop(["credit_id", "profile_path", "cast_id", "id", "character", "gender"], axis= 1, inplace= True)
cast_df = cast_df[cast_df["order"] <= 3]


crew_data = credits_data.explode("crew").reset_index(drop= True)
crew_df = pd.json_normalize(crew_data["crew"])
crew_df = pd.concat([crew_data["id"].rename("movie_id"), crew_df], axis= 1)

crew_df.drop(["credit_id", "profile_path", "department", "gender", "id"], axis= 1, inplace= True)

crew_df = crew_df[crew_df["job"] == "Director"]



# Now going to keywords used to describe a movie

keywords_data = pd.read_csv(r"C:/Users/mkdbh/Downloads/MovieRecom/Data/keywords.csv")

keywords_data["keywords"] = keywords_data["keywords"].apply(ast.literal_eval)

# Now making the list of dictionaries into rows of dictionaries
keywords_info = keywords_data.explode("keywords").dropna(subset=["keywords"]).reset_index(drop= True)
keywords_df = pd.json_normalize(keywords_info["keywords"])
keywords_df = pd.concat([keywords_info["id"].rename("movie_id"), keywords_df], axis=1)

keywords_df.drop("id", inplace= True, axis= 1)


# Information about each movie

#   Genres
#   Overview
#   Votes
#   Runtime


movies_metadata = pd.read_csv(r"C:/Users/mkdbh/Downloads/MovieRecom/Data/movies_metadata.csv")

movies_metadata = movies_metadata[
    ["id","title","release_date","genres","original_language",
     "overview","tagline","production_companies",
     "popularity","vote_average","vote_count","runtime", "poster_path"]
]


movies_metadata["vote_count"] = movies_metadata["vote_count"].fillna(0)
movies_metadata["vote_average"] = movies_metadata["vote_average"].fillna(0)

movies_metadata["popularity"] = pd.to_numeric(
    movies_metadata["popularity"],
    errors="coerce"
).fillna(0)


movies_metadata = movies_metadata[movies_metadata["id"].str.isnumeric()]
movies_metadata["id"] = movies_metadata["id"].astype(int)

# Only taking movies released after 1980s
movies_metadata["release_date"] = pd.to_datetime(movies_metadata["release_date"], errors="coerce")
movies_metadata["release_year"] = movies_metadata["release_date"].dt.year

movies_metadata = movies_metadata[movies_metadata["release_year"] >= 1980]

# Removing obscure indie films
movies_metadata = movies_metadata[movies_metadata["vote_count"] > 25]

# Adding the overview & tagline together
movies_metadata["overview_raw"] = movies_metadata["overview"].fillna("").astype(str).copy()
movies_metadata["overview_clean"] = (movies_metadata["overview"].fillna("") + " " + movies_metadata["tagline"].fillna(""))

movies_metadata["tagline"] = movies_metadata["tagline"].fillna("").astype(str)
movies_metadata["tagline"] = movies_metadata["tagline"].apply(lambda x: x.strip().strip('"').strip("'"))

def safe_convert(obj):
    try:
        data = ast.literal_eval(obj)

        if isinstance(data, list):
            return [i["name"] for i in data]

        return []
    except:
        return []


movies_metadata["genres"] = movies_metadata["genres"].apply(safe_convert)
movies_metadata["production_companies"] = movies_metadata["production_companies"].apply(safe_convert)

# Removing documentaries, short films, non - english movies & movies with no popularity score since we do not want them in recs
movies_metadata = movies_metadata[~movies_metadata["genres"].apply(lambda g: "Documentary" in g)]
movies_metadata = movies_metadata[movies_metadata["runtime"] >= 80]
movies_metadata = movies_metadata[movies_metadata["original_language"] == "en"]
movies_metadata = movies_metadata[movies_metadata["popularity"] > 1]

# Normalising the popularity score since it has a huge range
movies_metadata["popularity_norm"] = (movies_metadata["popularity"] / movies_metadata["popularity"].max())


movies_metadata.rename(columns={"id": "movie_id"}, inplace=True)

# A # of votes gained weighted average voting system to ensure that rating is backed by votes
# This method is used by IMDB to rate movies

"""
Weighted Rating Formula (IMDb style):

WR = (v / (v + m)) * R + (m / (v + m)) * C

where:
R = average rating for the movie (vote_average)
v = number of votes for the movie (vote_count)
m = minimum votes required to be listed
C = mean vote across the whole dataset

"""

# The minimum # of votes required for the movie to get listed is generally set as the 90th percentile of votes gained
# Implementing this


R = movies_metadata["vote_average"]
v = movies_metadata["vote_count"]
m = movies_metadata["vote_count"].quantile(0.90)
C = movies_metadata["vote_average"].mean()

movies_metadata["weighted_rating"] = ((v/(v+m))*R + (m/(v+m))*C)


# When we have mutiple movies with the same title, we choose the most popular one
movies_metadata = movies_metadata.sort_values(["title", "popularity_norm", "weighted_rating"], ascending=[True, False, False])

movies_metadata = movies_metadata.drop_duplicates("title")



# Now we need to get the text data into a format ready for processing
# This includes making everything into lower case & replacing spaces with underscores to make them a single word
# So basically have to do this for the columns which are of type string or contain a list of strings


def clean_list(x):
    if isinstance(x, list):
        return [i.replace(" ", "_").lower() for i in x if isinstance(i, str)]
    return []


def clean_str(s):
    if isinstance(s, str):
        return s.replace(" ", "_").lower()
    return ""


import re

def clean_text(x):
    x = str(x).lower()

    # To remove punctuation
    x = re.sub(r"[^\w\s]", "", x)

    return x


def normalize_title(x):

    if isinstance(x, str):
        x = x.lower().strip()
        x = x.replace("&", "and")
        x = re.sub(r"[^\w\s]", "", x)
        x = re.sub(r"\s+", " ", x)
        x = x.replace("the ", "")
        return x

    return ""


dfs = [cast_df, crew_df, keywords_df, movies_metadata]

list_cols = ["genres", "actors", "crew", "keywords", "production_companies"]

for df in dfs:
    for col in df.columns:

        if col == "overview_clean":
            df[col] = df[col].apply(clean_text)

        elif col in list_cols:
            df[col] = df[col].apply(clean_list)

        elif df[col].dtype == "object" and col not in ["title", "overview_clean", "overview_raw", "tagline"]:
            df[col] = df[col].apply(clean_str)


cast_df = cast_df.groupby("movie_id")["name"].apply(list).reset_index()
cast_df.rename(columns={"name": "actors"}, inplace=True)

crew_df = crew_df.groupby("movie_id")["name"].apply(list).reset_index()
crew_df.rename(columns={"name": "crew"}, inplace=True)

keywords_df = keywords_df.groupby("movie_id")["name"].apply(list).reset_index()
keywords_df.rename(columns={"name": "keywords"}, inplace=True)



# The final df called tags which contains the main influential features
# From cast_df -> name, order
# From crew_df -> job, name
# From keywords_df -> name
# From movies_metadata -> genres, overview_clean

movies = movies_metadata \
    .merge(cast_df, on="movie_id", how="left") \
    .merge(crew_df, on="movie_id", how="left") \
    .merge(keywords_df, on="movie_id", how="left")

# Clean titles for fuzzy matching (DO NOT replace spaces)
movies["clean_title"] = movies["title"].apply(normalize_title)
title_mapping = dict(zip(movies["clean_title"], movies["title"]))
all_titles = movies["clean_title"].tolist()

# Getting the movie posters but from letterboxd
lb_movies = pd.read_csv(r"C:\Users\mkdbh\Downloads\MovieRecom\Data\lb_movies.csv")
lb_posters = pd.read_csv(r"C:\Users\mkdbh\Downloads\MovieRecom\Data\posters.csv")

lb_bridge = lb_movies.merge(lb_posters, on='id')

lb_bridge['join_key'] = lb_bridge['name'].apply(normalize_title)
lb_bridge['release_year'] = pd.to_numeric(lb_bridge['date'], errors='coerce')


movies['join_key'] = movies['clean_title']

movies = movies.merge(
    lb_bridge[['join_key', 'release_year', 'link']], 
    on=['join_key', 'release_year'], 
    how='left'
)

movies['poster_path'] = movies['link'].fillna(movies['poster_path'])

movies['poster_path'] = movies['poster_path'].apply(
    lambda x: str(x).replace('0-150-0-225-crop', '0-2000-0-3000-crop')
)


# Giving extra weight to genres & director
def build_weighted_tags(row):

    tags = []

    # GENRES (weight = 3)
    if isinstance(row["genres"], list):
        tags += row["genres"] * 3

    # KEYWORDS (weight = 1)
    if isinstance(row["keywords"], list):
        tags += row["keywords"] * 1

    # ACTORS (weight = 1)
    if isinstance(row["actors"], list):
        tags += row["actors"] * 1

    # DIRECTOR (weight = 3)
    if isinstance(row["crew"], list):
        tags += row["crew"] * 3

    # OVERVIEW (weight = 1)
    if isinstance(row["overview_clean"], str):
      tags += row["overview_clean"].split()

    return " ".join(tags)

# To avoid missing values resulting in Nan after the merging
for col in ["genres", "keywords", "actors", "crew"]:
    movies[col] = movies[col].apply(lambda x: x if isinstance(x, list) else [])

movies["overview_clean"] = movies["overview_clean"].fillna("")

movies["tags"] = movies.apply(build_weighted_tags, axis= 1)

# Normalising the ratings
min_rating = movies_metadata["weighted_rating"].min()
max_rating = movies_metadata["weighted_rating"].max()
movies_metadata["weighted_rating"] = (movies_metadata["weighted_rating"] - min_rating) / (max_rating - min_rating)

# Since we only need the tags column & the non textual columns, we can remove the other columns
movies = movies[
    ["movie_id", "title", "clean_title", "tags", "popularity_norm", "weighted_rating", "genres", "poster_path", "overview_clean", "overview_raw", "tagline"]
]


import pandas as pd
import numpy as np
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from surprise import Dataset, Reader, SVD
from rapidfuzz import process, fuzz



# Just using a pandas series to store the movies_id instead of accessing the big dataframe again & again

movie_indices = pd.Series(movies.index, index=movies["title"]).drop_duplicates()


# The ratings dataset contains movie ratings of about 200 million users from the IMDB & TMDB dataset. We are using only 800K due to computation constraints
# We randomly sample the movie ratings because we want the model to learn from both popular as well as not popular movies

ratings = pd.read_csv(r"C:\Users\mkdbh\Downloads\MovieRecom\Data\ratings.csv")
ratings = ratings.sample(n=800000, random_state= 99)
user_counts = ratings["userId"].value_counts()


# This will filter only users who have rated more than 10 movies
active_users = user_counts[user_counts >= 10].index
ratings = ratings[ratings["userId"].isin(active_users)]


def fuzzy_match_movie(query, choices, limit=5, threshold=75):

    query = normalize_title(query)

    # Exact match
    if query in choices:
        return [query]

    # Fuzzy match
    results = process.extract(
        query,
        choices,
        scorer=fuzz.token_set_ratio,
        limit=limit
    )

    matches = [match for match, score, _ in results if score >= threshold]

    return matches if matches else []

import re
from rapidfuzz import process, fuzz

def normalize_title(x):
    if isinstance(x, str):
        x = x.lower().strip()
        x = x.replace("&", "and")
        # CRITICAL: We remove punctuation but KEEP letters and numbers.
        # This ensures 'ii', 'iii', and 'iv' remain intact.
        x = re.sub(r"[^\w\s]", "", x)
        x = re.sub(r"\s+", " ", x).strip()
        if x.startswith("the "):
            x = x[4:]
        return x
    return ""

def fuzzy_match_movie(query, choices, limit=10, threshold=65):
    clean_query = normalize_title(query)

    # Get initial fuzzy results
    # token_set_ratio is great for "Mission Impossible" -> "Mission Impossible II"
    results = process.extract(
        clean_query,
        choices,
        scorer=fuzz.token_set_ratio,
        limit=limit * 3
    )

    # Filter by threshold
    matches = [match for match, score, _ in results if score >= threshold]

    # Substring matching
    # If I type 'mission impossible', this catches 'mission impossible ii'
    # and 'mission impossible fallout' instantly.
    substring_matches = [c for c in choices if clean_query in c]

    # Combine and remove duplicates
    combined = list(dict.fromkeys(substring_matches + matches))

    # Use ratio to keep the closest name-match at the top.
    combined.sort(key=lambda x: fuzz.ratio(clean_query, x), reverse=True)

    return combined[:limit]

# We do NOT return sequels of a liked movie because the point of a movie recommender is to find movies that I do not know about
def is_same_franchise(title1, title2, threshold=70):
    t1 = normalize_title(title1)
    t2 = normalize_title(title2)

    score = fuzz.token_set_ratio(t1, t2)

    return score >= threshold



from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


# We use the TF-IDF method to find important words. Here the documents are the various movies

tfidf = TfidfVectorizer(max_features= 5000, stop_words="english", ngram_range= (1,2))
tfidf_vectors = tfidf.fit_transform(movies["tags"])



import pickle

# Save the necessary objects
artifacts = {
    "movies": movies,
    "ratings": ratings,
    "tfidf_vectors": tfidf_vectors,
    "movie_indices": movie_indices,
    "title_mapping": title_mapping,
    "all_titles": all_titles
}

with open("model_artifacts.pkl", "wb") as f:
    pickle.dump(artifacts, f)

print("Setup complete! model_artifacts.pkl has been created.")

