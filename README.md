# Director's Cut

**Find stories that linger.**

---

### THE FRAMEWORK

* **The Collection**: A private archive to search for and rate movies you love.
* **The Shortlist**: A hybrid engine that identifies patterns to project what is next.

---

### THE LOGIC

The system is a hybrid recommender which uses:
* **Semantic Layer**: Uses Cosine Similarity to identify content-based relationships.
* **Collaborative Layer**: Employs Collaborative Filtering to refine results based on collective user behavior.

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
