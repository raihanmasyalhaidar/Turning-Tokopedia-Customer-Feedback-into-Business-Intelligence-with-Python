"""
main.py
-------
End-to-end runner for the Tokopedia voice-of-customer analytics pipeline.

Two modes:

1. SCRAPE mode (default) -- collect fresh reviews from a Tokopedia store, then
   analyze, summarize, export to Excel, and render the dashboard.

       python src/main.py --url "https://www.tokopedia.com/<store>/review"

2. OFFLINE mode -- skip scraping and re-run the analysis on an existing
   reviews CSV (the bundled snapshot, for example).

       python src/main.py --from-csv data/tokopedia_reviews.csv

Options:
    --url        Tokopedia store review URL (SCRAPE mode).
    --from-csv   Path to an existing reviews CSV (OFFLINE mode).
    --out        Excel output path (default: data/Tokopedia_Sentiment.xlsx).
    --no-plot    Skip dashboard rendering.
"""

import argparse
import sys

import pandas as pd

from config import EXCEL_PATH
from analysis import build_dataframes, print_summary, save_to_excel
from visualization import plot_dashboard


def run(data: list, out_path: str, make_plot: bool = True):
    """Run the analysis + reporting stages on a list of review records."""
    print("\n[2/4] Memproses data & analisis...")
    df, sentiment_summary, produk_summary, df_topics, df_words, df_bigrams = \
        build_dataframes(data)
    print(f"  Selesai. {len(df)} baris diproses.")

    print("\n[3/4] Menampilkan ringkasan...")
    print_summary(df, sentiment_summary, produk_summary,
                  df_topics, df_words, df_bigrams)

    save_to_excel(df, sentiment_summary, produk_summary,
                  df_topics, df_words, df_bigrams, out_path)

    if make_plot:
        print("\n[4/4] Membuat visualisasi...")
        plot_dashboard(df, sentiment_summary, produk_summary,
                       df_topics, df_words, df_bigrams, out_path)


def main():
    parser = argparse.ArgumentParser(
        description="Tokopedia sentiment analysis pipeline."
    )
    parser.add_argument('--url', help="Tokopedia store review URL (SCRAPE mode).")
    parser.add_argument('--from-csv', help="Existing reviews CSV (OFFLINE mode).")
    parser.add_argument('--out', default=str(EXCEL_PATH),
                        help="Excel output path.")
    parser.add_argument('--no-plot', action='store_true',
                        help="Skip dashboard rendering.")
    args = parser.parse_args()

    if args.from_csv:
        print(f"[1/4] Memuat data dari CSV: {args.from_csv}")
        df_in = pd.read_csv(args.from_csv)
        # Keep only the raw columns expected by build_dataframes.
        data = df_in[['Produk', 'Rating', 'Ulasan']].to_dict('records')
        print(f"  {len(data)} ulasan dimuat.")

    elif args.url:
        # Imported lazily so the offline path doesn't require selenium installed.
        from scraper import scrape_tokopedia
        print("\n[1/4] Memulai scraping...")
        data = scrape_tokopedia(args.url)
        if not data:
            print("Tidak ada data yang berhasil di-scrape. Keluar.")
            sys.exit(1)
        print(f"  Scraping selesai. Total {len(data)} ulasan dikumpulkan.")

    else:
        parser.error("Berikan salah satu: --url (scrape) atau --from-csv (offline).")

    run(data, args.out, make_plot=not args.no_plot)


if __name__ == '__main__':
    main()
