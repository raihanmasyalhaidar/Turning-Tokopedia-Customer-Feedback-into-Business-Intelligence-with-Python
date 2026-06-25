"""
config.py
---------
Central configuration for the Tokopedia sentiment analysis pipeline.

Contains:
    - STOPWORDS         : Indonesian stopwords + marketplace noise words.
    - TOPIC_KEYWORDS    : keyword dictionary for the six business themes.
    - SENTIMENT_COLORS  : color palette used in the dashboard.
    - default file paths.
"""

from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR     = PROJECT_ROOT / "data"
ASSETS_DIR   = PROJECT_ROOT / "assets"

# Default output locations (override from the CLI / notebook if needed).
EXCEL_PATH     = DATA_DIR / "Tokopedia_Sentiment.xlsx"
DASHBOARD_PATH = ASSETS_DIR / "Tokopedia_Sentiment_dashboard.png"

# --------------------------------------------------------------------------- #
# Indonesian stopwords + high-frequency marketplace terms with little value
# --------------------------------------------------------------------------- #
STOPWORDS = {
    'dan', 'yang', 'di', 'ke', 'dari', 'ini', 'itu', 'dengan', 'untuk',
    'sudah', 'saya', 'tp', 'nya', 'ya', 'tidak', 'bisa', 'ada', 'tapi',
    'juga', 'sangat', 'barang', 'produk', 'good', 'oke', 'ok', 'gak',
    'ga', 'aja', 'udah', 'bgt', 'banget', 'sih', 'deh', 'lah', 'nih',
    'kalau', 'kalo', 'karena', 'jadi', 'lebih', 'paling', 'beli', 'kak',
    'mas', 'mba', 'min', 'shop', 'seller', 'si', 'pake', 'pakai',
    'udh', 'sdh', 'dgn', 'utk', 'yg', 'krn', 'jg', 'tdk',
}

# --------------------------------------------------------------------------- #
# Six predefined business themes for keyword-based multi-label tagging
# --------------------------------------------------------------------------- #
TOPIC_KEYWORDS = {
    'Kualitas Produk'   : ['bagus', 'baik', 'kualitas', 'mewah', 'solid', 'mantap',
                           'terbaik', 'original', 'ori', 'asli', 'premium'],
    'Pengiriman/Packing': ['packing', 'pengiriman', 'cepat', 'aman', 'segel', 'rapi',
                           'sampai', 'diterima', 'kirim', 'paket', 'bubble'],
    'Kesesuaian'        : ['sesuai', 'deskripsi', 'pesanan', 'ekspektasi', 'foto',
                           'gambar', 'listing'],
    'Fungsionalitas'    : ['berfungsi', 'normal', 'nyala', 'layar', 'kamera',
                           'baterai', 'performa', 'lancar', 'mulus', 'ngebut'],
    'Harga / Value'     : ['murah', 'harga', 'worth', 'flashsale', 'diskon',
                           'mahal', 'hemat', 'promo', 'flash'],
    'Layanan Toko'      : ['pelayanan', 'respon', 'responsif', 'seller', 'fast',
                           'resmi', 'garansi', 'servis'],
}

# --------------------------------------------------------------------------- #
# Dashboard palette
# --------------------------------------------------------------------------- #
SENTIMENT_COLORS = {
    'Positif'        : '#2ecc71',
    'Negatif'        : '#e74c3c',
    'Netral'         : '#f39c12',
    'Tidak Diketahui': '#95a5a6',
}
