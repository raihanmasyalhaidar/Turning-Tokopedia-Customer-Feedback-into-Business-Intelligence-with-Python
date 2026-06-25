# Data Dictionary — `Tokopedia_Sentiment.xlsx`

The workbook contains six sheets produced by the analysis pipeline. The same
per-review table is also provided as a flat CSV at
`data/tokopedia_reviews.csv` for quick inspection.

> Snapshot scope: **942 reviews** across **139 products** from the official
> Xiaomi store on Tokopedia, captured at a single point in time. No customer
> identifiers, transaction values, purchase histories, or timestamps are present.

---

## Sheet 1 — `Data Review` (942 rows)

The enriched, per-review table. One row per customer review.

| Column            | Type    | Description                                                                 |
| ----------------- | ------- | --------------------------------------------------------------------------- |
| `Produk`          | text    | Standardized product name (store names / marketing suffixes removed).       |
| `Rating`          | integer | Star rating assigned by the buyer (1–5).                                     |
| `Ulasan`          | text    | Raw review text exactly as written by the customer.                         |
| `Clean_Ulasan`    | text    | Lowercased review with punctuation / special characters stripped.           |
| `Sentiment`       | text    | Rating-derived label: `Positif` (4–5), `Netral` (3), `Negatif` (1–2).       |
| `Word_Count`      | integer | Number of words in `Clean_Ulasan`.                                          |
| `Char_Count`      | integer | Number of characters in the raw `Ulasan`.                                   |
| `Length_Category` | text    | Length bucket: Sangat Singkat / Singkat / Sedang / Panjang.                  |

## Sheet 2 — `Summary Sentiment` (3 rows)

| Column      | Type    | Description                          |
| ----------- | ------- | ------------------------------------ |
| `Sentiment` | text    | Sentiment label.                     |
| `Jumlah`    | integer | Count of reviews with that sentiment.|

## Sheet 3 — `Summary Produk` (139 rows)

| Column                | Type    | Description                                          |
| --------------------- | ------- | ---------------------------------------------------- |
| `Produk`              | text    | Standardized product name.                           |
| `Jumlah_Ulasan`       | integer | Number of reviews for that product.                  |
| `Rata_Rating`         | float   | Mean star rating for that product.                   |
| `Sentiment_Terbanyak` | text    | Most frequent sentiment label for that product.      |

## Sheet 4 — `Analisis Tema` (6 rows)

Multi-label theme distribution — a review may match more than one theme, so
percentages do not sum to 100%.

| Column          | Type    | Description                                           |
| --------------- | ------- | ----------------------------------------------------- |
| `Tema`          | text    | One of six business themes.                           |
| `Jumlah_Ulasan` | integer | Number of reviews matching the theme's keywords.      |
| `Persentase`    | text    | Share of all reviews matching the theme.              |

## Sheet 5 — `Top Kata` (20 rows)

| Column      | Type    | Description                                          |
| ----------- | ------- | ---------------------------------------------------- |
| `Kata`      | text    | Meaningful word (stopwords & short words removed).   |
| `Frekuensi` | integer | Number of occurrences across the corpus.             |

## Sheet 6 — `Top Bigram` (15 rows)

| Column      | Type    | Description                                          |
| ----------- | ------- | ---------------------------------------------------- |
| `Bigram`    | text    | Two-word phrase (stopword-filtered).                 |
| `Frekuensi` | integer | Number of occurrences across the corpus.             |

---

## Business Themes & Keyword Mapping

| Theme                | Keywords (Indonesian)                                                        |
| -------------------- | --------------------------------------------------------------------------- |
| `Kualitas Produk`    | bagus, baik, kualitas, mewah, solid, mantap, terbaik, original, ori, asli, premium |
| `Pengiriman/Packing` | packing, pengiriman, cepat, aman, segel, rapi, sampai, diterima, kirim, paket, bubble |
| `Kesesuaian`         | sesuai, deskripsi, pesanan, ekspektasi, foto, gambar, listing               |
| `Fungsionalitas`     | berfungsi, normal, nyala, layar, kamera, baterai, performa, lancar, mulus, ngebut |
| `Harga / Value`      | murah, harga, worth, flashsale, diskon, mahal, hemat, promo, flash          |
| `Layanan Toko`       | pelayanan, respon, responsif, seller, fast, resmi, garansi, servis          |
