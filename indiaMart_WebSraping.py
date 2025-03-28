from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import time
import datetime


def get_timestamp():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def log_message(message):
    print(f"{get_timestamp()} {message}")

log_message("Starting the web scraper")

chrome_options = Options()
chrome_options.add_argument("--incognito")
driver = webdriver.Chrome(options=chrome_options)
log_message("Chrome WebDriver initialized")
driver.get('https://www.indiamart.com/')
time.sleep(5)  

# Load cookies and local storage if available
try:
    with open("cookies.json", "r") as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    log_message("Cookies loaded successfully!")
    
    with open("local_storage.json", "r") as file:
        local_storage = json.load(file)
        for key, value in local_storage.items():
            driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")
    log_message("Local storage loaded successfully!")
    
    driver.refresh()
    time.sleep(5)  # Allow session to apply
except Exception as e:
    log_message(f"Error loading session data: {str(e)}")

# Navigate to the target search page
product=input("Enter the product name:")
location=input("Enter the location:")
driver.get(f'https://dir.indiamart.com/search.mp?ss={product}&cq={location}')
log_message("Page loaded successfully")
time.sleep(10)

all_data = []
page_number = 1

while True:
    try:
        log_message(f"Processing page {page_number}")
        # Click "Show More Results" button until it's gone
        while True:
            try:
                show_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Show more results')]")
                if show_more_button.is_displayed():
                    log_message("Clicking 'Show More Results' button")
                    driver.execute_script("arguments[0].click();", show_more_button)
                    time.sleep(15)
                else:
                    break
            except Exception:
                log_message("No 'Show More Results' button found or all results loaded")
                break

        log_message("Locating mobile number elements to click")
        time.sleep(2)

        # Click "View Mobile Number" buttons
        elements = driver.find_elements(By.CSS_SELECTOR, 'span.mo.viewn.vmn.fs14.clr5.fwb[data-click="^MobileNo"]')
        log_message(f"Found {len(elements)} mobile number elements to click")

        for i, element in enumerate(elements):
            log_message(f"Clicking element {i+1}/{len(elements)}")
            try:
                ActionChains(driver).move_to_element(element).click(element).perform()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'span.pns_h.duet.fwb'))
                )
                time.sleep(2)
            except Exception as e:
                log_message(f"Error clicking element {i+1}: {str(e)}")

        log_message("All 'View Mobile Number' buttons clicked, proceeding with extraction.")
        break

    except Exception as error:
        log_message(f"Critical error during scraping: {str(error)}")
        break

log_message("Starting data extraction")
phone_numbers = driver.find_elements(By.CSS_SELECTOR, 'span.pns_h.duet.fwb')
company_names = driver.find_elements(By.CSS_SELECTOR, 'a.cardlinks.elps.elps1')
locations = driver.find_elements(By.CSS_SELECTOR, 'div.newLocationUi.fs11.clr7.lh12.flx100.pr.db-trgt.tac.dib')

log_message(f"Found {len(phone_numbers)} phone numbers, {len(company_names)} company names, and {len(locations)} locations")

previous_data_count = len(all_data)
for index in range(len(phone_numbers)):
    phone_number = phone_numbers[index].text
    company_name = company_names[index].text if index < len(company_names) else None
    location = locations[index].text if index < len(locations) else None
    all_data.append({
        'phoneNumber': phone_number,
        'companyName': company_name,
        'location': location
    })

log_message(f"Added {len(all_data) - previous_data_count} new records. Total records: {len(all_data)}")
time.sleep(3)

log_message("Saving current data progress to JSON")
with open('data.json', 'w') as file:
    json.dump(all_data, file, indent=2)
log_message("Data saved successfully")
time.sleep(5)

# Save session cookies and local storage
log_message("Saving session data")
try:
    with open("cookies.json", "w") as file:
        json.dump(driver.get_cookies(), file)
    log_message("Cookies saved successfully")
    
    local_storage = driver.execute_script("return window.localStorage;")
    with open("local_storage.json", "w") as file:
        json.dump(local_storage, file)
    log_message("Local storage saved successfully")
except Exception as e:
    log_message(f"Error saving session data: {str(e)}")

driver.quit()
log_message("Browser closed. Script execution complete.")

# Save the html page
log_message("Saving complete page HTML")
with open('page.html', 'w', encoding='utf-8') as file:
    file.write(driver.page_source)
log_message("Page HTML saved successfully")