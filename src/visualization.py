"""
visualization.py
----------------
Builds the 7-panel sentiment dashboard and saves it as a PNG.

Panels:
    1. Sentiment distribution (pie).
    2. Rating distribution (bar).
    3. Top 10 words (horizontal bar).
    4. Theme distribution (horizontal bar).
    5. Top 8 products by review volume (horizontal bar).
    6. Review-length distribution (histogram).
    7. Top 8 bigrams (horizontal bar).
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

from config import SENTIMENT_COLORS


def plot_dashboard(df, sentiment_summary, produk_summary, df_topics,
                   df_words, df_bigrams, save_path: str):
    """Build and save the 7-chart sentiment dashboard.

    The output PNG is written next to ``save_path`` with the suffix
    ``_dashboard.png`` (e.g. ``Tokopedia_Sentiment.xlsx`` ->
    ``Tokopedia_Sentiment_dashboard.png``).
    """
    total = len(df)

    fig = plt.figure(figsize=(20, 15))
    fig.suptitle('Dashboard Analisis Sentimen Tokopedia', fontsize=20,
                 fontweight='bold', y=0.98, color='#2c3e50')
    gs = GridSpec(3, 3, figure=fig, hspace=0.50, wspace=0.38)

    # 1. Pie: sentiment distribution
    ax1 = fig.add_subplot(gs[0, 0])
    labels = sentiment_summary['Sentiment']
    sizes  = sentiment_summary['Jumlah']
    colors = [SENTIMENT_COLORS.get(s, '#95a5a6') for s in labels]
    wedges, texts, autotexts = ax1.pie(
        sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', startangle=90,
        textprops={'fontsize': 10},
        wedgeprops={'edgecolor': 'white', 'linewidth': 2},
    )
    for at in autotexts:
        at.set_fontweight('bold')
    ax1.set_title('Distribusi Sentimen', fontweight='bold', pad=12)

    # 2. Bar: rating distribution
    ax2 = fig.add_subplot(gs[0, 1])
    rating_counts = df['Rating'].value_counts().sort_index()
    bar_palette   = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60']
    bars = ax2.bar(
        rating_counts.index.astype(str), rating_counts.values,
        color=bar_palette[:len(rating_counts)],
        edgecolor='white', linewidth=1.5,
    )
    for bar, val in zip(bars, rating_counts.values):
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.15, str(val),
                 ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax2.set_title('Distribusi Rating', fontweight='bold', pad=12)
    ax2.set_xlabel('Bintang')
    ax2.set_ylabel('Jumlah Ulasan')
    ax2.set_ylim(0, rating_counts.max() * 1.18)
    ax2.spines[['top', 'right']].set_visible(False)

    # 3. Horizontal bar: top 10 words
    ax3 = fig.add_subplot(gs[0, 2])
    words, freqs = zip(*df_words.head(10).values)
    y_pos = np.arange(len(words))
    bars3 = ax3.barh(y_pos, freqs,
                     color=plt.cm.Blues(np.linspace(0.45, 0.85, len(words))),
                     edgecolor='white')
    for bar, val in zip(bars3, freqs):
        ax3.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                 str(val), va='center', fontsize=9)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(words, fontsize=10)
    ax3.invert_yaxis()
    ax3.set_title('Top 10 Kata', fontweight='bold', pad=12)
    ax3.set_xlabel('Frekuensi')
    ax3.spines[['top', 'right']].set_visible(False)

    # 4. Horizontal bar: review themes
    ax4 = fig.add_subplot(gs[1, :2])
    tema_sorted = df_topics.sort_values('Jumlah_Ulasan', ascending=True)
    tema_pcts   = [v / total * 100 for v in tema_sorted['Jumlah_Ulasan']]
    bars4 = ax4.barh(
        tema_sorted['Tema'], tema_sorted['Jumlah_Ulasan'],
        color=plt.cm.YlOrRd(np.linspace(0.35, 0.85, len(tema_sorted))),
        edgecolor='white',
    )
    for bar, val, pct in zip(bars4, tema_sorted['Jumlah_Ulasan'], tema_pcts):
        ax4.text(bar.get_width() + 0.2,
                 bar.get_y() + bar.get_height() / 2,
                 f'{val}  ({pct:.0f}%)', va='center', fontsize=9)
    ax4.set_title('Distribusi Tema Ulasan', fontweight='bold', pad=12)
    ax4.set_xlabel('Jumlah Ulasan')
    ax4.set_xlim(0, tema_sorted['Jumlah_Ulasan'].max() * 1.22)
    ax4.spines[['top', 'right']].set_visible(False)

    # 5. Horizontal bar: top 8 products by volume
    ax5 = fig.add_subplot(gs[1, 2])
    top8 = df['Produk'].value_counts().head(8)
    short_labels = [p[:22] + '…' if len(p) > 22 else p for p in top8.index]
    bars5 = ax5.barh(short_labels, top8.values,
                     color='#9b59b6', edgecolor='white')
    for bar, val in zip(bars5, top8.values):
        ax5.text(bar.get_width() + 0.5,
                 bar.get_y() + bar.get_height() / 2,
                 str(val),
                 va='center', ha='left', fontsize=10, fontweight='bold')
    ax5.invert_yaxis()
    ax5.set_xlim(0, top8.values.max() * 1.18)
    ax5.set_title('Top 8 Produk (Ulasan)', fontweight='bold', pad=12)
    ax5.set_xlabel('Jumlah Ulasan')
    ax5.spines[['top', 'right']].set_visible(False)

    # 6. Histogram: review length
    ax6 = fig.add_subplot(gs[2, 0])
    ax6.hist(df['Word_Count'], bins=15, color='#1abc9c',
             edgecolor='white', linewidth=1.2)
    ax6.axvline(df['Word_Count'].mean(), color='#e74c3c',
                linestyle='--', linewidth=1.8,
                label=f"Rata-rata: {df['Word_Count'].mean():.1f} kata")
    ax6.set_title('Distribusi Panjang Ulasan', fontweight='bold', pad=12)
    ax6.set_xlabel('Jumlah Kata')
    ax6.set_ylabel('Frekuensi')
    ax6.legend(fontsize=9)
    ax6.spines[['top', 'right']].set_visible(False)

    # 7. Horizontal bar: top 8 bigrams
    ax7 = fig.add_subplot(gs[2, 1:])
    bg_data = df_bigrams.head(8)
    bg_labels, bg_freqs = bg_data['Bigram'].tolist(), bg_data['Frekuensi'].tolist()
    y_pos7  = np.arange(len(bg_labels))
    bars7   = ax7.barh(y_pos7, bg_freqs, color='#e67e22', edgecolor='white')
    for bar, val in zip(bars7, bg_freqs):
        ax7.text(bar.get_width() + 0.05,
                 bar.get_y() + bar.get_height() / 2,
                 str(val), va='center', fontsize=9)
    ax7.set_yticks(y_pos7)
    ax7.set_yticklabels(bg_labels, fontsize=10)
    ax7.invert_yaxis()
    ax7.set_title('Top 8 Bigram (Frasa 2 Kata)', fontweight='bold', pad=12)
    ax7.set_xlabel('Frekuensi')
    ax7.spines[['top', 'right']].set_visible(False)

    # Save image
    img_path = save_path.replace('.xlsx', '_dashboard.png')
    plt.savefig(img_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Dashboard tersimpan ke: {img_path}")
    return img_path
