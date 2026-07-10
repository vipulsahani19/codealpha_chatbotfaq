"""
AI engine: classical machine learning text matching using TF-IDF
vectorization + cosine similarity (scikit-learn) — NOT keyword rules, and
NOT a downloaded neural network.

Why TF-IDF instead of a transformer model:
A pretrained transformer (e.g. all-MiniLM-L6-v2) gives richer semantic
matching, but needs model weights downloaded and loaded into memory at
runtime — which repeatedly exceeded the 512MB RAM limit on free-tier hosting
(Render's free instance), whether run through PyTorch or ONNX Runtime.
TF-IDF needs no download, no large runtime, and uses only a few MB of RAM
for a knowledge base this size, while still being a real, well-established,
fully explainable ML technique — the same vector-space model used in
classical information retrieval and search engines for decades.

Trade-off, stated plainly: TF-IDF matches on weighted word overlap (with
bigrams), so it has no built-in notion of synonyms — "AI beginners" and
"AI student learn first" score lower against each other than a transformer
would, because they share fewer literal words. For a fixed, curated FAQ set
like this one it's still very accurate in practice, and it's something you
can fully explain line-by-line in a viva.

How matching works:
1. At startup, scikit-learn's TfidfVectorizer learns a vocabulary from all
   FAQ questions (unigrams + bigrams) and converts each into a sparse
   TF-IDF vector — rare, distinctive words get more weight than common ones.
2. A user's question is transformed into a vector using that same fitted
   vocabulary.
3. Cosine similarity is computed between the query vector and every FAQ
   vector.
4. The highest-scoring FAQ is returned along with its similarity score.
5. If the best score is below MATCH_THRESHOLD, the engine reports no
   confident match so the API can return a fallback response instead of
   guessing.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MATCH_THRESHOLD = 0.22


class AiEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.faq_ids: list[int] = []
        self.doc_matrix = None  # sparse matrix, shape (n_faqs, vocab_size)

    def index_faqs(self, faqs: list[dict]) -> None:
        """faqs: list of dicts with at least 'id' and 'question'."""
        if not faqs:
            self.faq_ids = []
            self.doc_matrix = None
            return
        self.faq_ids = [f["id"] for f in faqs]
        questions = [f["question"] for f in faqs]
        self.doc_matrix = self.vectorizer.fit_transform(questions)

    def match(self, query: str) -> tuple[int | None, float]:
        """Returns (faq_id, score) for the best match, or (None, 0.0)."""
        if self.doc_matrix is None or len(self.faq_ids) == 0:
            return None, 0.0
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.doc_matrix)[0]
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        return self.faq_ids[best_idx], best_score

    def is_confident(self, score: float) -> bool:
        return score >= MATCH_THRESHOLD
