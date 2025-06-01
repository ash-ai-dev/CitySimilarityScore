# U.S. City–State Name Similarity Tool

---

## Purpose

This script analyzes the textual similarity between U.S. city names and their corresponding state names using character-level cosine similarity. The primary goal is to identify and group city–state pairs that share naming patterns, such as cities named after states or with partially similar names. This is done by computing a similarity score for each city–state name pair. It was developed as a request from the Crumbl/Get Chunky team (as my first assignment).

---

## How It Works

1. **User Input**:
   The user is prompted to enter a minimum similarity threshold (a number between 0.0 and 1.0). By entering `?`, the user can receive an explanation of similarity levels and the background of the program.

2. **Threshold Configuration**:
   The script generates a list of thresholds, starting from 1.0 down to the user-defined minimum, in intervals of 0.1. City–state pairs that meet or exceed these thresholds are grouped accordingly.

3. **Input Data**:
   The script expects the CSV named `us_cities.csv`, where we take in the inputs columns:

   - `STATE_NAME`
   - `CITY`

4. **Caching**:
   To improve processing time across multiple executions of the code, similarity scores are cached in `similarity_cache.csv`. If this file exists, previously computed scores are reused.

5. **Similarity Computation**:
   The program uses `scikit-learn`’s `CountVectorizer` to generate character-level n-grams (ranging from 2 to 4 characters), then calculates cosine similarity between the state and city names. For example, "New York" becomes "Ne", "ew", "w ", " Y", "Yo", "or", etc. These chunks are then used to create a numerical representation (a vector) for each name. Once both the city and state are converted into vectors, the program calculates the cosine similarity between them. This allows us to see partial matches, similar patterns, and name resemblances that might not be immediately obvious.

6. **Result Grouping**:
   Each city–state pair is assigned to the highest threshold bucket it qualifies for. These groups are stored in memory and printed to the terminal after processing.

7. **Cache Update**:
   New similarity scores are appended to the cache file to avoid recomputation in future runs.

---

## Output

For each threshold bucket (e.g., 1.0, 0.9, 0.8, etc.), the script prints a list of matching city–state pairs along with their similarity score.

Example:

```
--- Cities with similarity ≥ 1.0 (Exact match) ---
New York (New York) — Score: 1.0
```

---

## Similarity Levels

The script includes descriptive labels for each similarity range, starting from 1.0 (exact match) to 0.3 (very low similarity). These help interpret how closely a city name matches its state.

---

## Requirements

- Python 3
- `scikit-learn`
- `tqdm`

Dependencies can be installed with:

```
If a virtual environment isn't already created:
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Files

- `us_cities.csv`: Input file with U.S. city and state data. This was found on `https://github.com/kelvins/US-Cities-Database/tree/main`
- `similarity_cache.csv`: Cache file storing previously computed similarities. This is created dynamically upon running the program

---

## Notes

- Invalid or missing city/state names are skipped.
- The script is designed for terminal-based use and does not create an interface or export files beyond the cache.
- To adapt this for other geographic datasets, only the input CSV structure and column names would need to be changed.

---
