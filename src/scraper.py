"""
scraper.py
----------
Selenium-based web scraper for the review section of a Tokopedia store.

Because Tokopedia loads review content dynamically through JavaScript, a
headful/headless browser is required rather than plain HTTP requests. The
scraper navigates the paginated review list, parses each review container, and
extracts the product name, star rating (with three fallback strategies), and
review text.

Requirements:
    - Google Chrome + a matching chromedriver on PATH.
    - selenium, beautifulsoup4.

Usage:
    from scraper import scrape_tokopedia
    data = scrape_tokopedia("https://www.tokopedia.com/<store>/review")
"""

import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from preprocessing import clean_product_name


def scrape_tokopedia(url: str, max_pages: int = 100) -> list:
    """Scrape reviews from a Tokopedia store review page.

    Parameters
    ----------
    url : str
        URL of the store's review section.
    max_pages : int
        Safety cap on how many pages to paginate through.

    Returns
    -------
    list of dict
        Each dict has keys: 'Produk', 'Rating', 'Ulasan'.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)

    data = []

    for i in range(max_pages):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-testid='lblItemUlasan']")
                )
            )
        except Exception:
            print(f"  Halaman {i+1}: elemen ulasan tidak ditemukan, skip...")
            continue

        soup       = BeautifulSoup(driver.page_source, 'html.parser')
        containers = soup.find_all('article', class_='css-1pr2lii')

        for container in containers:
            try:
                produk_raw = container.find('a', class_='styProduct').find('p').text.strip()
                produk     = clean_product_name(produk_raw)

                ulasan = container.find(
                    'span', attrs={'data-testid': 'lblItemUlasan'}
                ).text.strip()

                # --- Extract rating (3 fallback strategies) ---
                rating = None

                star_wrapper = container.find(
                    attrs={'aria-label': re.compile(r'\d', re.IGNORECASE)}
                )
                if star_wrapper:
                    match = re.search(r'(\d+)', star_wrapper['aria-label'])
                    if match:
                        rating = int(match.group(1))

                if rating is None:
                    bintang_container = container.find(
                        'div', attrs={'data-testid': 'icnStarRating'}
                    )
                    if bintang_container:
                        parent = bintang_container.find_parent()
                        if parent:
                            match = re.search(r'\b([1-5])\b', parent.get_text())
                            if match:
                                rating = int(match.group(1))

                if rating is None:
                    for testid in ['lblRating', 'ratingScore', 'rating', 'score']:
                        el = container.find(
                            attrs={'data-testid': re.compile(testid, re.IGNORECASE)}
                        )
                        if el:
                            match = re.search(r'([1-5])', el.get_text())
                            if match:
                                rating = int(match.group(1))
                                break

                data.append({'Produk': produk, 'Rating': rating, 'Ulasan': ulasan})

            except AttributeError:
                continue

        print(f"  Halaman {i+1}: {len(containers)} ulasan ditemukan | Total: {len(data)}")
        time.sleep(2)

        try:
            next_btn = driver.find_element(
                By.CSS_SELECTOR, "button[aria-label^='Laman berikutnya']"
            )
            driver.execute_script('arguments[0].click();', next_btn)
            time.sleep(3)
        except Exception:
            print("  Tombol halaman berikutnya tidak ditemukan. Scraping selesai.")
            break

    driver.quit()
    return data
