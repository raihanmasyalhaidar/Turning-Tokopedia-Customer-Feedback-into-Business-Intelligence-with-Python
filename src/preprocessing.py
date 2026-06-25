"""
preprocessing.py
----------------
Text-preprocessing, sentiment classification, and NLP helper functions.

Pipeline stages implemented here:
    1. Product-name standardization.
    2. Review-text cleaning (lowercase, strip non-alphanumerics).
    3. Rating-based sentiment classification.
    4. Review-length categorization.
    5. Top-word and bigram extraction (stopword-filtered).
"""

import re
from collections import Counter

import pandas as pd

from config import STOPWORDS


def clean_product_name(name: str) -> str:
    """Standardize a marketplace product name by removing store names,
    promotional suffixes, and trailing marketing descriptions.
    """
    name = name.split('|')[0].strip()
    name = re.sub(r'\s*\[.*?Store\]', '', name, flags=re.IGNORECASE).strip()
    name = re.sub(r'^(XIAOMI OFFICIAL|Official)\s+', '', name, flags=re.IGNORECASE).strip()

    paren_matches = list(re.finditer(r'\([\w\s/+.]+\)', name))
    if paren_matches:
        last_paren_end = paren_matches[-1].end()
        if name[last_paren_end:].strip():
            name = name[:last_paren_end].strip()
        return name

    desc_pattern = re.compile(
        r'\s+(Baterai|Performa|Layar|Kamera|Ekspansi|besar|dengan|pengisian|Fast|Charging$)',
        re.IGNORECASE
    )
    m = desc_pattern.search(name)
    if m:
        name = name[:m.start()].strip()
    return name


def clean_ulasan(text: str) -> str:
    """Lowercase the review and strip everything except alphanumerics + spaces."""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def sentiment_by_rating(rating) -> str:
    """Map a 1-5 star rating to a sentiment label.

    4-5 stars -> Positif, 3 stars -> Netral, 1-2 stars -> Negatif.
    """
    if pd.isna(rating):
        return 'Tidak Diketahui'
    elif rating >= 4:
        return 'Positif'
    elif rating == 3:
        return 'Netral'
    else:
        return 'Negatif'


def get_review_length_category(word_count: int) -> str:
    """Bucket a review by its word count."""
    if word_count <= 3:    return 'Sangat Singkat (≤3 kata)'
    elif word_count <= 8:  return 'Singkat (4–8 kata)'
    elif word_count <= 15: return 'Sedang (9–15 kata)'
    else:                  return 'Panjang (>15 kata)'


def get_top_words(texts, n: int = 20):
    """Return the n most common meaningful words (stopword + short-word filtered)."""
    all_words = ' '.join(texts).split()
    filtered  = [w for w in all_words if w not in STOPWORDS and len(w) > 2]
    return Counter(filtered).most_common(n)


def get_bigrams(texts, n: int = 15):
    """Return the n most common two-word phrases (stopword + short-word filtered)."""
    bigrams = []
    for text in texts:
        words = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]
        for i in range(len(words) - 1):
            bigrams.append(f"{words[i]} {words[i+1]}")
    return Counter(bigrams).most_common(n)
