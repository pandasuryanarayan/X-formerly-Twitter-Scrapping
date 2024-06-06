import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import requests
from pymongo import MongoClient
import uuid
from time import sleep
from random import choice

# Initialize MongoDB client
client = MongoClient('localhost', 27017) # You can connect to  your MongoDB Atlas as well.
db = client.twitter_trends
collection = db.trending_topics

# Path to the ChromeDriver executable
chrome_driver_path = 'chromedriver'

def get_public_ip():
    try:
        response = requests.get('http://api.ipify.org')
        return response.text
    except requests.RequestException as e:
        print("Error fetching public IP: ", e)
        return None

### Because of free public proxy son't work all time So I don't used. Instead I used default IP address.
### For default IP address I used IPIFY so get the public url.

# def get_proxy():
#     url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
#     response = requests.get(url)
#     sleep(11)
#     proxies = response.text.split('\n')
#     proxies = [proxy for proxy in proxies if proxy]
#     return proxies

def fetch_trending_topics():
    # Setup Chrome Options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument(f'--proxy-server={proxy}')
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # sleep(10)
    
    # Open the login page
    driver.get('https://x.com/i/flow/login')

    # Wait for the page to load
    sleep(25)

    # Locate and input the username
    username = driver.find_element(By.TAG_NAME, "input")
    username.send_keys("") # Enter Phone , Email or Username

    # Wait for 2 seconds
    sleep(2)

    # Locate and click the "Next" button
    next_buttons = driver.find_element(By.CSS_SELECTOR, "#layers > div:nth-child(2) > div > div > div > div > div > div.css-175oi2r.r-1ny4l3l.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv.r-1awozwy > div.css-175oi2r.r-1wbh5a2.r-htvplk.r-1udh08x.r-1867qdf.r-kwpbio.r-rsyp9y.r-1pjcn9w.r-1279nm1 > div > div > div.css-175oi2r.r-1ny4l3l.r-6koalj.r-16y2uox.r-kemksi.r-1wbh5a2 > div.css-175oi2r.r-16y2uox.r-1wbh5a2.r-f8sm7e.r-13qz1uu.r-1ye8kvj > div > div > div > button:nth-child(6)")
    next_buttons.click()

    # Wait for 2 seconds
    sleep(25)

    # Check if the mobile number input field is displayed
    try:
        mobileNumber = driver.find_element(By.XPATH, "//input[@data-testid='ocfEnterTextTextInput']")
        mobileNumber.send_keys("") # Phone Number Field. If you enter Email Previously then might ask.

        # Wait for 5 seconds
        sleep(5)

        # Locate and click the "Next" button for mobile number input
        next = driver.find_element(By.XPATH, "//button[@data-testid='ocfEnterTextNextButton']")
        next.click()

        # Wait for 5 seconds
        sleep(5)
    except NoSuchElementException:
        pass

    # Check if the password input field is displayed
    try:
        password = driver.find_element(By.XPATH, "//input[@name='password']")
        password.send_keys("") # Password Field. Enter Your 'X' Password .

        sleep(5)

        # Locate and click the "Login" button
        login = driver.find_element(By.CSS_SELECTOR, "#layers > div:nth-child(2) > div > div > div > div > div > div.css-175oi2r.r-1ny4l3l.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv.r-1awozwy > div.css-175oi2r.r-1wbh5a2.r-htvplk.r-1udh08x.r-1867qdf.r-kwpbio.r-rsyp9y.r-1pjcn9w.r-1279nm1 > div > div > div.css-175oi2r.r-1ny4l3l.r-6koalj.r-16y2uox.r-kemksi.r-1wbh5a2 > div.css-175oi2r.r-16y2uox.r-1wbh5a2.r-f8sm7e.r-13qz1uu.r-1ye8kvj > div.css-175oi2r.r-1f0wa7y > div > div.css-175oi2r > div > div > button")
        login.click()

        # Wait for 25 seconds
        sleep(25)
    except NoSuchElementException:
        pass

    # Navigate to the trending topics page
    driver.get('https://x.com/explore')

    # Wait for the page to load
    sleep(10)

    # Fetch trending topics
    try:
        # Use WebDriverWait to wait until the elements are present
        wait = WebDriverWait(driver, 30)  # Increase wait time to 30 seconds

        trend_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-testid='trend']")))

        top_trends = []
        for trend in trend_elements[:5]:  # Limit to top 5 trends
            spans = trend.find_elements(By.TAG_NAME, "span")
            if len(spans) > 1:
                top_trends.append(spans[1].text)  # Get the 2nd span element

        return top_trends

    except (NoSuchElementException, TimeoutException, Exception) as e:
        print("Error: ", e)
        return []

def store_results(trends, ip_address):
    unique_id = str(uuid.uuid4())
    end_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    result = {
        "unique_id": unique_id,
        "trends": trends,
        "end_time": end_time,
        "ip_address": ip_address
    }
    insert_result = collection.insert_one(result)
    result["_id"] = str(insert_result.inserted_id)
    return result

if __name__ == "__main__":
    # proxies = get_proxy()
    # proxy = choice(proxies)
    ip_address = get_public_ip()
    trends = fetch_trending_topics()
    result = store_results(trends, ip_address)
    
    print(json.dumps(result))