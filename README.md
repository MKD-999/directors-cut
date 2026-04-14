# Director's Cut

**A curated discovery engine.**

Stories that linger

---

### THE FRAMEWORK

* **Search**: Identify titles that define a mood or feeling.
* **The Collection**: A private archive to rate and track history.
* **The Shortlist**: A hybrid engine that identifies patterns to project what is next.

---

### THE LOGIC

The system is a hybrid recommender:
1. **Semantic Layer**: Uses Cosine Similarity to identify content-based relationships.
2. **Collaborative Layer**: Employs Collaborative Filtering to refine results based on collective user behavior.

---

### TECH STACK

* **Frontend**: Svelte 5 / WebGL Shaders
* **Backend**: FastAPI / Python
* **ML**: Scikit-Learn / Surprise
* **Persistence**: LocalStorage / Pickle Serialization

---

### SETUP

**Backend**
1. `pip install -r requirements.txt`
2. `python recommender.py` (Process base model)
3. `python main.py` (Start API)

**Frontend**
1. `npm install`
2. `npm run dev`
