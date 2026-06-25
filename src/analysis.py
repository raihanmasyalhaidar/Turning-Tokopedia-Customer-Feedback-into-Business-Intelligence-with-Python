"""
analysis.py
-----------
Builds the analytical DataFrames from raw scraped data, prints a terminal
summary, and saves all results to a multi-sheet Excel workbook.

Analytical views produced:
    - df                  : enriched per-review table.
    - sentiment_summary   : sentiment label counts.
    - produk_summary      : per-product review count / mean rating / dominant sentiment.
    - df_topics           : multi-label theme distribution.
    - df_words            : top words.
    - df_bigrams          : top two-word phrases.
"""

import os

import pandas as pd

from config import TOPIC_KEYWORDS
from preprocessing import (
    clean_ulasan,
    sentiment_by_rating,
    get_review_length_category,
    get_top_words,
    get_bigrams,
)


def build_dataframes(data: list):
    """Build every analytical DataFrame from the raw scraped records."""
    # Main DataFrame
    df = pd.DataFrame(data, columns=['Produk', 'Rating', 'Ulasan'])
    df['Clean_Ulasan']    = df['Ulasan'].apply(clean_ulasan)
    df['Sentiment']       = df['Rating'].apply(sentiment_by_rating)
    df['Word_Count']      = df['Clean_Ulasan'].apply(lambda x: len(x.split()))
    df['Char_Count']      = df['Ulasan'].apply(len)
    df['Length_Category'] = df['Word_Count'].apply(get_review_length_category)

    # Sentiment summary
    sentiment_summary = df['Sentiment'].value_counts().reset_index()
    sentiment_summary.columns = ['Sentiment', 'Jumlah']

    # Product summary
    produk_summary = (
        df.groupby('Produk')
        .agg(
            Jumlah_Ulasan       = ('Ulasan',    'count'),
            Rata_Rating         = ('Rating',    'mean'),
            Sentiment_Terbanyak = ('Sentiment', lambda x: x.mode()[0])
        )
        .reset_index()
        .sort_values('Rata_Rating', ascending=False)
    )

    # Theme analysis (multi-label)
    total      = len(df)
    topic_rows = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        count = sum(
            1 for rev in df['Clean_Ulasan']
            if any(kw in rev.lower() for kw in keywords)
        )
        topic_rows.append({
            'Tema'          : topic,
            'Jumlah_Ulasan' : count,
            'Persentase'    : f"{count / total * 100:.1f}%",
        })
    df_topics = pd.DataFrame(topic_rows)

    # Top words & bigrams
    df_words   = pd.DataFrame(get_top_words(df['Clean_Ulasan'], 20),
                              columns=['Kata', 'Frekuensi'])
    df_bigrams = pd.DataFrame(get_bigrams(df['Clean_Ulasan'], 15),
                              columns=['Bigram', 'Frekuensi'])

    return df, sentiment_summary, produk_summary, df_topics, df_words, df_bigrams


def print_summary(df, sentiment_summary, produk_summary, df_topics, df_words, df_bigrams):
    """Print a complete, formatted analysis summary to the terminal."""
    total = len(df)
    SEP   = '=' * 65

    print(f"\n{SEP}")
    print("   RINGKASAN ANALISIS SENTIMEN TOKOPEDIA")
    print(SEP)

    print(f"\n  Total ulasan     : {total}")
    print(f"  Total produk     : {df['Produk'].nunique()}")
    print(f"  Rata-rata rating : {df['Rating'].mean():.2f} / 5")
    print(f"  Median rating    : {df['Rating'].median():.1f}")
    print(f"  Rata-rata kata   : {df['Word_Count'].mean():.1f} kata/ulasan")

    # Sentiment
    print(f"\n  {'─'*40}")
    print("  Distribusi Sentimen")
    print(f"  {'─'*40}")
    COLORS_LABEL = {'Positif': '🟢', 'Negatif': '🔴', 'Netral': '🟡'}
    for _, row in sentiment_summary.iterrows():
        pct = row['Jumlah'] / total * 100
        bar = '█' * int(pct / 3)
        ico = COLORS_LABEL.get(row['Sentiment'], '⚪')
        print(f"  {ico} {row['Sentiment']:<12} {bar:<30} {row['Jumlah']:>3} ({pct:.1f}%)")

    # Rating
    print(f"\n  {'─'*40}")
    print("  Distribusi Rating")
    print(f"  {'─'*40}")
    for star in sorted(df['Rating'].dropna().unique().astype(int), reverse=True):
        count = (df['Rating'] == star).sum()
        pct   = count / total * 100
        stars = '★' * star + '☆' * (5 - star)
        print(f"  {stars}  {count:>3} ulasan ({pct:.1f}%)")

    # Review length
    print(f"\n  {'─'*40}")
    print("  Kategori Panjang Ulasan")
    print(f"  {'─'*40}")
    for cat in ['Sangat Singkat (≤3 kata)', 'Singkat (4–8 kata)',
                'Sedang (9–15 kata)', 'Panjang (>15 kata)']:
        count = (df['Length_Category'] == cat).sum()
        pct   = count / total * 100
        print(f"  {cat:<30} : {count:>3} ({pct:.1f}%)")

    # Themes
    print(f"\n  {'─'*40}")
    print("  Distribusi Tema Ulasan")
    print(f"  {'─'*40}")
    for _, row in df_topics.sort_values('Jumlah_Ulasan', ascending=False).iterrows():
        pct = row['Jumlah_Ulasan'] / total * 100
        bar = '▪' * int(pct / 3)
        print(f"  {row['Tema']:<25} {bar:<20} {row['Jumlah_Ulasan']:>3} ({pct:.1f}%)")

    # Top words
    print(f"\n  {'─'*40}")
    print("  Top 15 Kata Paling Sering")
    print(f"  {'─'*40}")
    for rank, (_, row) in enumerate(df_words.head(15).iterrows(), 1):
        print(f"  {rank:>2}. {row['Kata']:<20} {row['Frekuensi']}x")

    # Top bigrams
    print(f"\n  {'─'*40}")
    print("  Top 10 Bigram (Frasa 2 Kata)")
    print(f"  {'─'*40}")
    for rank, (_, row) in enumerate(df_bigrams.head(10).iterrows(), 1):
        print(f"  {rank:>2}. {row['Bigram']:<30} {row['Frekuensi']}x")

    # Top-rated products
    print(f"\n  {'─'*40}")
    print("  Top 5 Produk Rating Tertinggi (min 2 ulasan)")
    print(f"  {'─'*40}")
    top_rated = (produk_summary[produk_summary['Jumlah_Ulasan'] >= 2]
                 .sort_values('Rata_Rating', ascending=False)
                 .head(5))
    for _, row in top_rated.iterrows():
        print(f"  ⭐ {row['Rata_Rating']:.2f}  {row['Produk'][:45]}  ({row['Jumlah_Ulasan']} ulasan)")

    # Negative reviews
    neg = df[df['Sentiment'] == 'Negatif']
    print(f"\n  {'─'*40}")
    print(f"  Ulasan Negatif ({len(neg)} ditemukan)")
    print(f"  {'─'*40}")
    if len(neg):
        for _, row in neg.iterrows():
            print(f"  [{row['Rating']}★] {row['Produk'][:45]}")
            print(f"       \"{str(row['Ulasan'])[:90]}\"")
    else:
        print("  Tidak ada ulasan negatif!")

    print(f"\n{SEP}\n")


def save_to_excel(df, sentiment_summary, produk_summary,
                  df_topics, df_words, df_bigrams, path: str):
    """Save every analytical view to a single multi-sheet Excel workbook."""
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        df.to_excel(writer,                sheet_name='Data Review',       index=False)
        sentiment_summary.to_excel(writer, sheet_name='Summary Sentiment', index=False)
        produk_summary.to_excel(writer,    sheet_name='Summary Produk',    index=False)
        df_topics.to_excel(writer,         sheet_name='Analisis Tema',     index=False)
        df_words.to_excel(writer,          sheet_name='Top Kata',          index=False)
        df_bigrams.to_excel(writer,        sheet_name='Top Bigram',        index=False)

    print(f"  Data tersimpan ke: {path}")
    print("  Sheet: Data Review | Summary Sentiment | Summary Produk | "
          "Analisis Tema | Top Kata | Top Bigram")
