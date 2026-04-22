import warnings
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

import pandas as pd
import numpy as np
import pickle
import argparse
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack
from rapidfuzz import process, fuzz

class MadeInRwandaRecommender:
    def __init__(self, model_path='tfidf_model.pkl', catalog_path='catalog.csv'):
        # 1. Load hybrid model
        with open(model_path, 'rb') as f:
            self.tfidf_word, self.tfidf_char, self.tfidf_matrix, \
            self.vocab, self.FR_EN, self.KIN_EN = pickle.load(f)

        self.df = pd.read_csv(catalog_path).drop_duplicates(subset='title').reset_index(drop=True)
        

        # 2. Stopwords
        self.STOPWORDS = {'à','en','de','le','la','les','du','un','une','pour','et'}

        # 3. Niche districts: least represented → get extra boost for geographic fairness
        self.niche_districts = self.df['origin_district'].value_counts().tail(2).index.tolist()

        # 4. Similarity threshold for fallback
        self.LOCAL_THRESHOLD = 0.10

    # ── Query Pipeline ─────────────────────────────────────────────────────────
    def _translate(self, query):
        """Translate French and Kinyarwanda words to English."""
        words = query.lower().split()
        return ' '.join(self.FR_EN.get(w, self.KIN_EN.get(w, w)) for w in words)

    def _correct(self, query):
        """Fuzzy spell correction against catalog vocabulary."""
        words = query.lower().split()
        corrected = []
        for word in words:
            if word in self.vocab:
                corrected.append(word)
            else:
                match, score, _ = process.extractOne(word, self.vocab, scorer=fuzz.ratio)
                corrected.append(match if score >= 65 else word)
        return ' '.join(corrected)

    def _preprocess(self, query):
        """Full pipeline: translate → remove stopwords → correct typos."""
        q = self._translate(query)
        q = ' '.join(w for w in q.split() if w not in self.STOPWORDS)
        q = self._correct(q)
        return q

    def _vectorize(self, query):
        """Convert cleaned query to hybrid word+char sparse vector."""
        clean = self._preprocess(query)
        return hstack([
            self.tfidf_word.transform([clean]),
            self.tfidf_char.transform([clean])
        ])

    # ── Local Boost ────────────────────────────────────────────────────────────
    def _boost(self, district, boost_factor):
        """
        All Made-in-Rwanda products get base boost.
        Niche (underrepresented) districts get an extra 10% on top.
        This implements the brief's 'niche-first' requirement.
        """
        if district in self.niche_districts:
            return boost_factor * 1.10
        return boost_factor

    # ── Core Recommendation ────────────────────────────────────────────────────
    def recommend(self, query, top_n=5, boost_factor=1.25):
        # Step 1: Vectorize
        q_vec = self._vectorize(query)
        similarities = cosine_similarity(q_vec, self.tfidf_matrix).flatten()

        # Step 2: Apply local boost to all products
        boost_mask = self.df['origin_district'].apply(
            lambda x: self._boost(x, boost_factor)
        ).values
        final_scores = similarities * boost_mask

        # Step 3: Fallback — if no product scores above threshold,
        # return curated local products sorted by popularity (price as proxy)
        if final_scores.max() < self.LOCAL_THRESHOLD:
            fallback = self.df.sort_values('price_rwf', ascending=False).head(top_n).copy()
            fallback['score'] = 0.0
            print("⚠️  No strong local match found — returning curated local fallback")
            return fallback[['sku', 'title', 'origin_district', 'price_rwf', 'score']]

        # Step 4: Rank by final boosted score
        results_idx = final_scores.argsort()[::-1]
        sorted_df = self.df.iloc[results_idx].copy()
        sorted_df['score'] = final_scores[results_idx]

        # Step 5: Fairness cap — no artisan occupies more than 15% of top-n
        final_results = []
        artisan_counts = {}
        fairness_limit = max(1, int(top_n * 0.15))

        for _, row in sorted_df.iterrows():
            if len(final_results) == top_n:
                break
            art_id = row['artisan_id']
            if artisan_counts.get(art_id, 0) < fairness_limit:
                final_results.append(row)
                artisan_counts[art_id] = artisan_counts.get(art_id, 0) + 1

        results = pd.DataFrame(final_results)[['sku', 'title', 'origin_district', 'price_rwf', 'score']]
        results['score'] = results['score'].round(4)
        return results

    # ── CLI Display ────────────────────────────────────────────────────────────
    def display(self, query, top_n=5):
        clean = self._preprocess(query)
        print(f"\n🔍 Query    : '{query}'")
        print(f"✅ Cleaned  : '{clean}'")
        print(f"📍 Niche districts (extra boost): {self.niche_districts}")
        print(f"{'─'*60}")

        results = self.recommend(query, top_n)

        for i, (_, row) in enumerate(results.iterrows(), 1):
            print(
                f"{i}. {row['title']:<38} "
                f"{row['origin_district']:<12} "
                f"{int(row['price_rwf']):>8} RWF  "
                f"(score: {row['score']})"
            )
        print(f"{'─'*60}\n")
        return results


# ── CLI Entry Point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Made in Rwanda — Niche-First Product Recommender"
    )
    parser.add_argument('--q', type=str, required=True,  help="Search query (English, French, or Kinyarwanda)")
    parser.add_argument('--n', type=int, default=5,      help="Number of results (default: 5)")
    args = parser.parse_args()

    engine = MadeInRwandaRecommender()
    engine.display(args.q, args.n)
