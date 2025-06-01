import csv
import os
import re
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

# Descriptions for the similarity scores over 0.1 intervals; User Experience
similarity_descriptions = {
    1.0: "A match!",
    0.9: "Very similar (e.g., shared prefixes or suffixes)",
    0.8: "Pretty Similar (e.g., partial matches, similar patterns)",
    0.7: "Moderately similar (some overlap)",
    0.6: "Good similarity",
    0.5: "Decently similarity",
    0.4: "Reasonably related",
    0.3: "Less similarity",
    0.2: "Low similarity",
    0.1: "Minimally related",
    0.0: "Unlikely to be related"
}

# Ask User to input minimum threshhold, allowing user to get more information by entering '?'
min_threshold = 0.3
while True:
    user_input = input("Enter minimum similarity threshold (e.g., 0.5) or type '?' to view similarity descriptions: ").strip()

    if user_input == "?":
        print("\n Background for this Program:")
        print("This program compares the names of U.S. cities and their corresponding states.")
        print("It measures how similar the names are using cosine similarity on character-level n-grams.")
        print("Similarity scores range from 0.0 (no similarity) to 1.0 (exact match).")
        print("This tool is intended to be used to see \"how many American states have cities in them that is also the name of the state\".\n")
        print("This tool was requested by the Crumbl/Get Chunky crew.\n")

        print("--- Similarity Descriptions ---")
        for level in sorted(similarity_descriptions.keys(), reverse=True):
            print(f"{level:.1f}: {similarity_descriptions[level]}")
        print()
    else:
        try:
            value = float(user_input)
            if 0.0 <= value <= 1.0:
                min_threshold = round(value, 1)
                break
            else:
                print("Please enter a value between 0.0 and 1.0.")
        except ValueError:
            print("Invalid input. Enter a number like 0.7 or type '?' to view similarity descriptions.")

# Create a list for each respective threshold
thresholds = sorted([round(i * 0.1, 1) for i in range(int(min_threshold * 10), 11)], reverse=True)

# Input/Output CSVs
csv_path = "us_cities.csv"
cache_path = "similarity_cache.csv"
similarity_buckets = defaultdict(list)

# Create a caching file so the entire CSV doesn't need to be parsed on every use of the program
cache = {}
if os.path.exists(cache_path):
    with open(cache_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["state"], row["city"])
            cache[key] = float(row["score"])

# Calculate the similarity between each state and the input city (passed as parameters)
def compute_similarity(state, city):
    vectorizer = CountVectorizer(analyzer='char', ngram_range=(2, 4))
    vectors = vectorizer.fit_transform([state, city])
    base_score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    state_lower = state.lower()
    city_lower = city.lower()

    # Check for whole-word match using regex word boundaries
    if re.search(rf'\b{re.escape(state_lower)}\b', city_lower):
        boost = 0.45
    elif state_lower in city_lower:
        boost = 0.2
    else:
        boost = 0.0

    boosted_score = min(base_score + boost, 1.0)
    return boosted_score

# Allow for appending to the cache
new_cache_rows = []

# Iterate through CSV entries and process relevant data ( + Add to the cache if necessary)
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = list(csv.DictReader(csvfile))

    for row in tqdm(reader, desc="Processing rows"):
        state = row["STATE_NAME"].strip()
        city = row["CITY"].strip()
        key = (state, city)

        if not state or not city:
            continue

        if key in cache:
            score = cache[key]
        else:
            score = compute_similarity(state, city)
            cache[key] = score
            new_cache_rows.append({"state": state, "city": city, "score": round(score, 2)})

        for threshold in thresholds:
            if score >= threshold:
                similarity_buckets[threshold].append({
                    "state": state,
                    "city": city,
                    "score": round(score, 2)
                })
                break

# Save all new entries to the cache with the state name, city name, and the relevant score
if new_cache_rows:
    write_header = not os.path.exists(cache_path)
    with open(cache_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["state", "city", "score"])
        if write_header:
            writer.writeheader()
        writer.writerows(new_cache_rows)

# Print results to terminal
for threshold in thresholds:
    if similarity_buckets[threshold]:
        desc = similarity_descriptions.get(threshold, "Unlabeled similarity level")
        print(f"\n--- Cities with similarity ≥ {threshold} ({desc}) ---")
        for match in similarity_buckets[threshold]:
            print(f"{match['city']} ({match['state']}) — Score: {match['score']}")
