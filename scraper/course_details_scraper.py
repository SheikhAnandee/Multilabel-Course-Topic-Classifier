# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import (
#     TimeoutException,
#     WebDriverException,
#     InvalidSessionIdException
# )

# import pandas as pd
# import time
# import random
# import os
# import csv
# import gc

# # =========================================================
# # CONFIG
# # =========================================================
# INPUT_FILE = "course_urls.csv"
# OUTPUT_FILE = "course_details.csv"

# RECYCLE_DRIVER_EVERY = 150
# MAX_FAILURES = 3

# PAGE_LOAD_TIMEOUT = 30
# WAIT_TIMEOUT = 12

# # =========================================================
# # LOAD URLS
# # =========================================================
# print("📥 Loading URLs...")

# df = pd.read_csv(INPUT_FILE)

# all_urls = (
#     df["url"]
#     .dropna()
#     .astype(str)
#     .str.strip()
#     .unique()
#     .tolist()
# )

# print(f"📌 Total URLs in CSV: {len(all_urls)}")

# # =========================================================
# # LOAD ALREADY SCRAPED URLS
# # =========================================================
# scraped_urls = set()

# if os.path.exists(OUTPUT_FILE):
#     try:
#         old_df = pd.read_csv(OUTPUT_FILE, usecols=["url"])

#         scraped_urls = set(
#             old_df["url"]
#             .dropna()
#             .astype(str)
#             .str.strip()
#             .tolist()
#         )

#         print(f"✔ Already scraped: {len(scraped_urls)} URLs")

#     except Exception as e:
#         print("⚠ Could not read existing output file")
#         print(e)

# # =========================================================
# # FILTER REMAINING URLS
# # =========================================================
# course_urls = [u for u in all_urls if u not in scraped_urls]

# total = len(course_urls)

# print(f"🟢 Remaining URLs to scrape: {total}")

# if total == 0:
#     print("\n✅ ALL URLS ALREADY SCRAPED")
#     exit()

# # =========================================================
# # CREATE OUTPUT FILE IF NOT EXISTS
# # =========================================================
# if not os.path.exists(OUTPUT_FILE):

#     with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:

#         writer = csv.writer(f)

#         writer.writerow([
#             "title",
#             "url",
#             "category",
#             "subcategory",
#             "sub_subcategory",
#             "description",
#             "labels"
#         ])

# # =========================================================
# # CHROME OPTIONS
# # =========================================================
# def get_options():

#     options = uc.ChromeOptions()

#     # Anti-detection
#     options.add_argument("--disable-blink-features=AutomationControlled")

#     # Stability
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-gpu")

#     # Prevent freezing when minimized / screen off
#     options.add_argument("--disable-background-timer-throttling")
#     options.add_argument("--disable-backgrounding-occluded-windows")
#     options.add_argument("--disable-renderer-backgrounding")

#     # Reduce memory
#     prefs = {
#         "profile.managed_default_content_settings.images": 2
#     }

#     options.add_experimental_option("prefs", prefs)

#     return options

# # =========================================================
# # START DRIVER
# # =========================================================
# def start_driver():

#     print("🔄 Starting new driver...")

#     driver = uc.Chrome(options=get_options())

#     driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

#     return driver

# # =========================================================
# # DRIVER HEALTH CHECK
# # =========================================================
# def is_driver_alive(driver):

#     try:
#         _ = driver.title
#         return True

#     except:
#         return False

# # =========================================================
# # SAFE PAGE LOAD
# # =========================================================
# def safe_get(driver, url, retries=3):

#     for attempt in range(retries):

#         try:
#             driver.get(url)
#             return True

#         except Exception as e:

#             print(f"⚠ Page load failed ({attempt+1}/{retries})")

#             time.sleep(2)

#     return False

# # =========================================================
# # SAFE SAVE
# # =========================================================
# def save_row(data):

#     with open(OUTPUT_FILE, "a", newline="", encoding="utf-8-sig") as f:

#         writer = csv.writer(f)

#         writer.writerow([
#             data["title"],
#             data["url"],
#             data["category"],
#             data["subcategory"],
#             data["sub_subcategory"],
#             data["description"],
#             data["labels"]
#         ])

# # =========================================================
# # START DRIVER
# # =========================================================
# driver = start_driver()

# wait = WebDriverWait(driver, WAIT_TIMEOUT)

# # =========================================================
# # SCRAPER LOOP
# # =========================================================
# fail_count = 0
# batch_count = 0

# for index, url in enumerate(course_urls, start=1):

#     print(f"\n[{index}/{total}] {url}")

#     # =====================================================
#     # CHECK DRIVER
#     # =====================================================
#     if not is_driver_alive(driver):

#         print("⚠ Driver crashed. Restarting...")

#         try:
#             driver.quit()
#         except:
#             pass

#         gc.collect()

#         driver = start_driver()
#         wait = WebDriverWait(driver, WAIT_TIMEOUT)

#     # =====================================================
#     # RECYCLE DRIVER
#     # =====================================================
#     if batch_count >= RECYCLE_DRIVER_EVERY:

#         print("♻ Recycling driver...")

#         try:
#             driver.quit()
#         except:
#             pass

#         gc.collect()

#         time.sleep(2)

#         driver = start_driver()
#         wait = WebDriverWait(driver, WAIT_TIMEOUT)

#         batch_count = 0

#     # =====================================================
#     # LOAD PAGE
#     # =====================================================
#     if not safe_get(driver, url):

#         print("❌ Failed loading page")

#         fail_count += 1

#         try:
#             driver.quit()
#         except:
#             pass

#         gc.collect()

#         driver = start_driver()
#         wait = WebDriverWait(driver, WAIT_TIMEOUT)

#         continue

#     batch_count += 1

#     # Human-like delay
#     time.sleep(random.uniform(1.0, 2.0))

#     try:

#         # =================================================
#         # TITLE
#         # =================================================
#         title = wait.until(
#             EC.presence_of_element_located((By.TAG_NAME, "h1"))
#         ).text.strip()

#         # =================================================
#         # BREADCRUMBS / CATEGORIES
#         # =================================================
#         breadcrumbs = driver.find_elements(
#             By.CSS_SELECTOR,
#             "ol.ud-unstyled-list li a"
#         )

#         categories = [
#             b.text.strip()
#             for b in breadcrumbs
#             if b.text.strip()
#         ]

#         category = categories[0] if len(categories) > 0 else ""
#         subcategory = categories[1] if len(categories) > 1 else ""
#         sub_subcategory = categories[2] if len(categories) > 2 else ""

#         # =================================================
#         # EXPAND DESCRIPTION
#         # =================================================
#         try:
#             show_more_btn = driver.find_element(
#                 By.CSS_SELECTOR,
#                 "button[aria-label='Show more description']"
#             )

#             driver.execute_script(
#                 "arguments[0].click();",
#                 show_more_btn
#             )

#             time.sleep(0.5)

#         except:
#             pass

#         # =================================================
#         # DESCRIPTION
#         # =================================================
#         try:
#             description = driver.find_element(
#                 By.CSS_SELECTOR,
#                 "div[data-purpose='safely-set-inner-html:description:description']"
#             ).text.replace("\n", " ").strip()

#         except:
#             description = ""

#         # =================================================
#         # LABELS
#         # =================================================
#         labels = "|".join([
#             x for x in [
#                 category,
#                 subcategory,
#                 sub_subcategory
#             ] if x
#         ])

#         # =================================================
#         # SAVE
#         # =================================================
#         save_row({
#             "title": title,
#             "url": url,
#             "category": category,
#             "subcategory": subcategory,
#             "sub_subcategory": sub_subcategory,
#             "description": description,
#             "labels": labels
#         })

#         print("✔ Saved")

#         fail_count = 0

#         # Random delay
#         time.sleep(random.uniform(1.5, 3.0))

#     except Exception as e:

#         print("⚠ Scraping Error:")
#         print(e)

#         fail_count += 1

#         # =================================================
#         # RESTART DRIVER IF TOO MANY FAILURES
#         # =================================================
#         if fail_count >= MAX_FAILURES:

#             print("🔥 Too many failures → restarting driver")

#             try:
#                 driver.quit()
#             except:
#                 pass

#             gc.collect()

#             time.sleep(2)

#             driver = start_driver()
#             wait = WebDriverWait(driver, WAIT_TIMEOUT)

#             fail_count = 0

#         continue

# # =========================================================
# # FINISH
# # =========================================================
# try:
#     driver.quit()
# except:
#     pass

# gc.collect()

# print("\n✅ SCRAPING COMPLETED SAFELY")
# print(f"📦 Total scraped this run: {total}")
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    InvalidSessionIdException
)

import pandas as pd
import time
import random
import os
import csv
import gc

# =========================================================
# CONFIG
# =========================================================
INPUT_FILE = "course_urls.csv"
OUTPUT_FILE = "course_details.csv"

RECYCLE_DRIVER_EVERY = 150
MAX_FAILURES = 3

PAGE_LOAD_TIMEOUT = 30
WAIT_TIMEOUT = 12

# =========================================================
# LOAD URLS
# =========================================================
print("📥 Loading URLs...")

df = pd.read_csv(INPUT_FILE)

all_urls = (
    df["url"]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
    .tolist()
)

print(f"📌 Total URLs in CSV: {len(all_urls)}")

# =========================================================
# LOAD ALREADY SCRAPED URLS
# =========================================================
scraped_urls = set()

if os.path.exists(OUTPUT_FILE):
    try:
        old_df = pd.read_csv(OUTPUT_FILE, usecols=["url"])

        scraped_urls = set(
            old_df["url"]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

        print(f"✔ Already scraped: {len(scraped_urls)} URLs")

    except Exception as e:
        print("⚠ Could not read existing output file")
        print(e)

# =========================================================
# FILTER REMAINING URLS
# =========================================================
course_urls = [u for u in all_urls if u not in scraped_urls]

total = len(course_urls)

print(f"🟢 Remaining URLs to scrape: {total}")

if total == 0:
    print("\n✅ ALL URLS ALREADY SCRAPED")
    exit()

# =========================================================
# CREATE OUTPUT FILE IF NOT EXISTS
# =========================================================
# SCHEMA (simplified):
#   title, url, description,
#   topic       -> single primary label
#   topic_list  -> full multi-label set (taxonomy path folded in + related topics)
# =========================================================
if not os.path.exists(OUTPUT_FILE):

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:

        writer = csv.writer(f)

        writer.writerow([
            "title",
            "url",
            "description",
            "topic",
            "topic_list"
        ])

# =========================================================
# CHROME OPTIONS
# =========================================================
def get_options():

    options = uc.ChromeOptions()

    # Anti-detection
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Stability
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    # Prevent freezing when minimized / screen off
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")

    # Reduce memory
    prefs = {
        "profile.managed_default_content_settings.images": 2
    }

    options.add_experimental_option("prefs", prefs)

    return options

# =========================================================
# START DRIVER
# =========================================================
# def start_driver():

#     print("🔄 Starting new driver...")

#     driver = uc.Chrome(options=get_options())

#     driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

#     return driver
def start_driver():

    print("🔄 Starting new driver...")

    driver = uc.Chrome(options=get_options(), version_main=151)

    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    return driver
# =========================================================
# DRIVER HEALTH CHECK
# =========================================================
def is_driver_alive(driver):

    try:
        _ = driver.title
        return True

    except:
        return False

# =========================================================
# SAFE PAGE LOAD
# =========================================================
def safe_get(driver, url, retries=3):

    for attempt in range(retries):

        try:
            driver.get(url)
            return True

        except Exception as e:

            print(f"⚠ Page load failed ({attempt+1}/{retries})")

            time.sleep(2)

    return False

# =========================================================
# SAFE SAVE
# =========================================================
def save_row(data):

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8-sig") as f:

        writer = csv.writer(f)

        writer.writerow([
            data["title"],
            data["url"],
            data["description"],
            data["topic"],
            data["topic_list"]
        ])

# =========================================================
# START DRIVER
# =========================================================
driver = start_driver()

wait = WebDriverWait(driver, WAIT_TIMEOUT)

# =========================================================
# SCRAPER LOOP
# =========================================================
fail_count = 0
batch_count = 0

for index, url in enumerate(course_urls, start=1):

    print(f"\n[{index}/{total}] {url}")

    # =====================================================
    # CHECK DRIVER
    # =====================================================
    if not is_driver_alive(driver):

        print("⚠ Driver crashed. Restarting...")

        try:
            driver.quit()
        except:
            pass

        gc.collect()

        driver = start_driver()
        wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # =====================================================
    # RECYCLE DRIVER
    # =====================================================
    if batch_count >= RECYCLE_DRIVER_EVERY:

        print("♻ Recycling driver...")

        try:
            driver.quit()
        except:
            pass

        gc.collect()

        time.sleep(2)

        driver = start_driver()
        wait = WebDriverWait(driver, WAIT_TIMEOUT)

        batch_count = 0

    # =====================================================
    # LOAD PAGE
    # =====================================================
    if not safe_get(driver, url):

        print("❌ Failed loading page")

        fail_count += 1

        try:
            driver.quit()
        except:
            pass

        gc.collect()

        driver = start_driver()
        wait = WebDriverWait(driver, WAIT_TIMEOUT)

        continue

    batch_count += 1

    # Human-like delay
    time.sleep(random.uniform(1.0, 2.0))

    try:

        # =================================================
        # TITLE
        # =================================================
        title = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        ).text.strip()

        # =================================================
        # BREADCRUMBS / CATEGORIES
        # (used only internally to build topic / topic_list —
        #  not saved as separate columns)
        # =================================================
        breadcrumbs = driver.find_elements(
            By.CSS_SELECTOR,
            "ol.ud-unstyled-list li a"
        )

        categories = [
            b.text.strip()
            for b in breadcrumbs
            if b.text.strip()
        ]

        category = categories[0] if len(categories) > 0 else ""
        subcategory = categories[1] if len(categories) > 1 else ""
        sub_subcategory = categories[2] if len(categories) > 2 else ""

        # =================================================
        # EXPAND DESCRIPTION
        # =================================================
        try:
            show_more_btn = driver.find_element(
                By.CSS_SELECTOR,
                "button[aria-label='Show more description']"
            )

            driver.execute_script(
                "arguments[0].click();",
                show_more_btn
            )

            time.sleep(0.5)

        except:
            pass

        # =================================================
        # DESCRIPTION
        # =================================================
        try:
            description = driver.find_element(
                By.CSS_SELECTOR,
                "div[data-purpose='safely-set-inner-html:description:description']"
            ).text.replace("\n", " ").strip()

        except:
            description = ""

        # =================================================
        # RELATED TOPICS  ("Explore related topics" section)
        # Structure (from page inspection):
        # <ul role="navigation" aria-label="Explore related topics">
        #   <li><a ...><span class="ud-btn-label">Game Development Fundamentals</span></a></li>
        #   <li><a ...><span class="ud-btn-label">2D Game Development</span></a></li>
        #   ...
        # </ul>
        # Scroll into view first since this section loads lower on the page
        # and may be lazy-rendered.
        # =================================================
        related_topics = []

        try:
            # Scroll down to trigger lazy-loaded sections
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight * 0.6);"
            )
            time.sleep(1)

            related_container = wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "ul[aria-label='Explore related topics']"
                ))
            )

            topic_spans = related_container.find_elements(
                By.CSS_SELECTOR,
                "span.ud-btn-label"
            )

            related_topics = [
                t.text.strip()
                for t in topic_spans
                if t.text.strip()
            ]

        except TimeoutException:
            # Not every course page has this section
            related_topics = []
        except Exception:
            related_topics = []

        # =================================================
        # TOPIC  (single primary label)
        # Most specific taxonomy leaf Udemy assigns to the course
        # =================================================
        topic = sub_subcategory if sub_subcategory else (
            subcategory if subcategory else category
        )

        # =================================================
        # TOPIC_LIST  (full multi-label set)
        # Combine taxonomy path + related topics, dedup, preserve order
        # =================================================
        combined = [category, subcategory, sub_subcategory] + related_topics

        seen = set()
        topic_list = []

        for t in combined:
            t_clean = t.strip()
            key = t_clean.lower()

            if t_clean and key not in seen:
                seen.add(key)
                topic_list.append(t_clean)

        # =================================================
        # SAVE
        # =================================================
        save_row({
            "title": title,
            "url": url,
            "description": description,
            "topic": topic,
            "topic_list": topic_list
        })

        print(f"✔ Saved | topics: {topic_list}")

        fail_count = 0

        # Random delay
        time.sleep(random.uniform(1.5, 3.0))

    except Exception as e:

        print("⚠ Scraping Error:")
        print(e)

        fail_count += 1

        # =================================================
        # RESTART DRIVER IF TOO MANY FAILURES
        # =================================================
        if fail_count >= MAX_FAILURES:

            print("🔥 Too many failures → restarting driver")

            try:
                driver.quit()
            except:
                pass

            gc.collect()

            time.sleep(2)

            driver = start_driver()
            wait = WebDriverWait(driver, WAIT_TIMEOUT)

            fail_count = 0

        continue

# =========================================================
# FINISH
# =========================================================
try:
    driver.quit()
except:
    pass

gc.collect()

print("\n✅ SCRAPING COMPLETED SAFELY")
print(f"📦 Total scraped this run: {total}")