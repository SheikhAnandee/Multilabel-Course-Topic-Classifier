import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
import os

CATEGORIES = {
    "development": "https://www.udemy.com/courses/development/",
    "business": "https://www.udemy.com/courses/business/",
    "finance": "https://www.udemy.com/courses/finance-and-accounting/",
    "it_and_software": "https://www.udemy.com/courses/it-and-software/",
    "design": "https://www.udemy.com/courses/design/",
    "marketing": "https://www.udemy.com/courses/marketing/",
    "personal_development": "https://www.udemy.com/courses/personal-development/"
}

OUTPUT_FILE = "course_urls.csv"

def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    # Using version_main=147 as per your environment
    driver = uc.Chrome(options=options, version_main=147)
    driver.set_page_load_timeout(30)
    return driver

def smooth_scroll(driver):
    current_pos = 0
    page_height = driver.execute_script("return document.body.scrollHeight")
    while current_pos < page_height:
        current_pos += 600 
        driver.execute_script(f"window.scrollTo(0, {current_pos});")
        time.sleep(0.2)
        page_height = driver.execute_script("return document.body.scrollHeight")

def main():
    all_data = []
    seen_urls = set()
    
    # RESUME LOGIC: Load existing data instead of deleting it
    if os.path.exists(OUTPUT_FILE):
        try:
            df_existing = pd.read_csv(OUTPUT_FILE)
            all_data = df_existing.to_dict('records')
            # Extract clean URLs to avoid re-scraping duplicates
            seen_urls = set(df_existing['url'].str.split('?').str[0].str.rstrip('/').tolist())
            print(f"📂 Found existing file. Loaded {len(seen_urls)} unique courses.")
        except Exception as e:
            print(f"⚠️ Could not load existing file: {e}")

    driver = init_driver()
    pages_scraped_this_session = 0

    try:
        for category_name, base_url in CATEGORIES.items():
            print(f"\n🚀 STARTING CATEGORY: {category_name.upper()}")

            for page_id in range(1, 101):
                # RESTART CHECK: Restart browser every 10 pages to avoid memory crashes
                if pages_scraped_this_session >= 10:
                    driver.quit()
                    time.sleep(2)
                    driver = init_driver()
                    pages_scraped_this_session = 0

                url = f"{base_url}?p={page_id}"
                print(f"   📄 Page {page_id}")

                try:
                    driver.get(url)
                    pages_scraped_this_session += 1
                    
                    wait = WebDriverWait(driver, 20)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3[data-purpose='course-title-url']")))
                    
                    smooth_scroll(driver)
                    time.sleep(1)
                    
                    rows = driver.find_elements(By.CSS_SELECTOR, "h3[data-purpose='course-title-url']")
                    new_count = 0
                    
                    for row in rows:
                        try:
                            link = row.find_element(By.TAG_NAME, "a")
                            raw_url = link.get_attribute("href")
                            clean_url = raw_url.split('?')[0].rstrip('/')
                            
                            if clean_url not in seen_urls:
                                title = link.text.strip().split('\n')[0]
                                seen_urls.add(clean_url)
                                all_data.append({"title": title, "url": clean_url, "category": category_name})
                                new_count += 1
                        except:
                            continue

                    print(f"      ✅ Added {new_count} (Total Unique: {len(all_data)})")
                    
                    # Incremental Save - keeps the existing data and adds new rows
                    pd.DataFrame(all_data).to_csv(OUTPUT_FILE, index=False)
                    
                    time.sleep(random.uniform(2, 4))

                except Exception as e:
                    print(f"   ⚠️ Skipping Page {page_id} due to error: {str(e)[:50]}")
                    if "session id" in str(e).lower() or "disconnected" in str(e).lower():
                        driver.quit()
                        driver = init_driver()
                    continue

    finally:
        print(f"\n Finished! Total records collected: {len(all_data)}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()