import time
import csv
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import asyncio
import os
from typing import Dict, Set, Tuple
from urllib.parse import quote

# Constants
CSV_FILENAME = 'gmaps_data.csv'
SCROLL_PAUSE_TIME = 1.5  # Reduced pause time for better performance
MAX_RETRIES = 3
WAIT_FOR_NEW_RESULTS = 10
SCROLL_INCREMENT = 500  # Pixels to scroll each time

class GoogleMapsExtractor:
    def __init__(self, driver):
        self.driver = driver
        self.setup_logging()
        self.setup_files()
        self.seen_places: Set[Tuple[str, str]] = set()
        self.total_extracted = 0
        self.last_processed_index = 0

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_files(self):
        self.headers = [
            'name', 'rating', 'reviews', 'address',
            'phone', 'website', 'latitude', 'longitude', 'extracted_time'
        ]

        if not os.path.exists(CSV_FILENAME):
            with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()
        else:
            with open(CSV_FILENAME, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.seen_places.add((row['name'], row['address']))

    def save_place(self, place_data: Dict):
        place_key = (place_data['name'], place_data['address'])
        if place_key in self.seen_places:
            self.logger.debug(f"Skipping duplicate: {place_data['name']}")
            return False

        with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writerow(place_data)

        self.seen_places.add(place_key)
        self.total_extracted += 1
        self.logger.info(f"Saved place {self.total_extracted}: {place_data['name']}")
        return True

    def wait_for_element(self, by, value, timeout=10):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            self.logger.warning(f"Element not found: {value}")
            return None

    async def extract_basic_info(self, card):
        try:
            details = {field: 'N/A' for field in self.headers}
            details['extracted_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            name_element = card.find_element(By.CSS_SELECTOR, 'div.qBF1Pd')
            details['name'] = name_element.text.strip()

            try:
                address_element = card.find_element(By.CSS_SELECTOR, 'div.W4Efsd:last-child')
                details['address'] = address_element.text.strip()
            except NoSuchElementException:
                details['address'] = 'N/A'

            try:
                rating_element = card.find_element(By.CSS_SELECTOR, 'span.MW4etd')
                details['rating'] = rating_element.text.strip()
                
                reviews_element = card.find_element(By.CSS_SELECTOR, 'span.UY7F9')
                details['reviews'] = reviews_element.text.replace('(', '').replace(')', '')
            except NoSuchElementException:
                pass

            return details
        except (NoSuchElementException, StaleElementReferenceException):
            return None

    async def extract_detailed_info(self, details):
        try:
            # Extract detailed information
            selectors = {
                'address': 'button[data-item-id="address"]',
                'phone': 'button[data-item-id^="phone:tel"]',
                'website': 'a[data-item-id="authority"]'
            }

            for field, selector in selectors.items():
                try:
                    element = self.wait_for_element(By.CSS_SELECTOR, selector)
                    if element:
                        if field == 'website':
                            details[field] = element.get_attribute('href')
                        else:
                            details[field] = element.text.strip()
                except Exception:
                    pass

            # Extract coordinates from URL
            try:
                url = self.driver.current_url
                coords = url.split('@')[1].split(',')[:2]
                details['latitude'] = coords[0]
                details['longitude'] = coords[1]
            except:
                pass

            return details

        except Exception as e:
            self.logger.error(f"Error extracting detailed info: {e}")
            return details

    async def extract_place_details(self, card):
        try:
            # First get basic info without clicking
            details = await self.extract_basic_info(card)
            if not details:
                return None

            # Check if already seen
            place_key = (details['name'], details['address'])
            if place_key in self.seen_places:
                return None

            # Click card to get detailed info
            try:
                card.click()
                await asyncio.sleep(1)
                
                details = await self.extract_detailed_info(details)

                # Go back to results
                back_button = self.driver.find_element(By.CSS_SELECTOR, 'button[jsaction="pane.back"]')
                back_button.click()
                await asyncio.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Error during card interaction: {e}")
                try:
                    self.driver.find_element(By.CSS_SELECTOR, 'button[jsaction="pane.back"]').click()
                except:
                    pass

            return details

        except Exception as e:
            self.logger.error(f"Error in extract_place_details: {e}")
            return None

    async def monitor_scrolling(self):
        last_height = 0
        retries = 0
        no_new_results_count = 0
        processed_count = 0

        while retries < MAX_RETRIES and no_new_results_count < 3:
            try:
                scrollable_div = self.wait_for_element(By.CSS_SELECTOR, 'div[role="feed"]')
                if not scrollable_div:
                    self.logger.error("Scrollable results panel not found")
                    break

                # Get all cards
                cards = self.driver.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')
                
                # Process only new cards
                new_cards = cards[self.last_processed_index:]
                if new_cards:
                    for card in new_cards:
                        place_data = await self.extract_place_details(card)
                        if place_data:
                            if self.save_place(place_data):
                                processed_count += 1
                    
                    self.last_processed_index = len(cards)
                    no_new_results_count = 0
                else:
                    no_new_results_count += 1

                # Smooth scrolling
                current_height = self.driver.execute_script(
                    "return arguments[0].scrollTop",
                    scrollable_div
                )
                target_height = current_height + SCROLL_INCREMENT
                
                self.driver.execute_script(
                    f"arguments[0].scrollTop = {target_height}",
                    scrollable_div
                )
                await asyncio.sleep(SCROLL_PAUSE_TIME)

                new_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight",
                    scrollable_div
                )

                if new_height == last_height:
                    self.logger.info(f"Reached bottom, waiting for new results... (Processed: {processed_count})")
                    await asyncio.sleep(WAIT_FOR_NEW_RESULTS)
                    
                    updated_height = self.driver.execute_script(
                        "return arguments[0].scrollHeight",
                        scrollable_div
                    )
                    
                    if updated_height == new_height:
                        no_new_results_count += 1
                    else:
                        last_height = updated_height
                        retries = 0
                else:
                    last_height = new_height
                    retries = 0

            except Exception as e:
                self.logger.error(f"Error during scrolling: {e}")
                retries += 1
                await asyncio.sleep(2)

        self.logger.info(f"Extraction completed. Total places processed: {processed_count}")

def open_browser(url):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    return driver

async def main():
    choice = input("Enter '1' for manual search or '2' for URL input: ").strip()
    if choice == '1':
        query = input("Enter a business type or location (e.g., 'restaurants in New York'): ").strip()
        url = f"https://www.google.com/maps/search/{quote(query)}"
    elif choice == '2':
        url = input("Enter the Google Maps URL: ").strip()
    else:
        print("Invalid choice. Exiting.")
        return

    driver = open_browser(url)
    extractor = GoogleMapsExtractor(driver)

    try:
        await asyncio.sleep(5)  # Initial page load wait
        await extractor.monitor_scrolling()
    except KeyboardInterrupt:
        print("\nScript interrupted. Saving data...")
    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(main())