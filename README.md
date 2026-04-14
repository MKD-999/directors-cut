# DIRECTOR’S CUT 🎬

A cinematic film discovery platform that uses SVD (Singular Value Decomposition) to curate a personalized "Shortlist" based on user taste.

## 🎞️ The Concept
Most movie recommenders feel like a data spreadsheet. **DIRECTOR’S CUT** is designed to feel like a high-end film studio’s internal tool. It moves away from the "Noir" aesthetic into a clean, high-contrast "Silver Screen" vibe.

## ✨ Key Features
* **The Search**: A minimalist entry point to find titles that "linger."
* **The Collection**: A private vault where you rate and archive your cinematic history.
* **Run the Final Cut**: A machine-learning process that analyzes your collection to generate a curated 12-movie "Shortlist."

## 🛠️ Technical Stack
* **Frontend**: SvelteKit (Svelte 5) with custom WebGL shader backgrounds.
* **Backend**: FastAPI (Python) implementing the SVD recommendation algorithm.
* **Machine Learning**: Scikit-Learn / Surprise for latent factor analysis.
* **Persistence**: LocalStorage for seamless browser-side data saving.
