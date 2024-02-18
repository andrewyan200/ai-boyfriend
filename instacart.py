from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import time
import undetected_chromedriver as webdriver
from capsolver_python import RecaptchaV2Task

load_dotenv()
CAPTCHA_API_KEY = os.getenv("CAPTCHA_API_KEY")
INSTACART_EMAIL = os.getenv("INSTACART_EMAIL")
INSTACART_PASSWORD = os.getenv("INSTACART_PASSWORD")
COFFEE_LINK = "https://www.instacart.com/products/248557-high-brew-cold-brew-coffee-mexican-vanilla-8-fl-oz?retailerSlug=safeway"
MEDICINE_LINK = "https://www.instacart.com/products/90236-vicks-dayquil-and-nyquil-cold-flu-and-congestion-medicine-48-ct?retailerSlug=safeway"
CHECKOUT_LINK = "https://www.instacart.com/store/checkout_v4?sid=53040"
DELIVERY_ADDRESS = "475 Via Ortega, Stanford, CA 94305"
# URL of the Instacart CVS storefront
LOGIN_URL = "https://www.instacart.com/login"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--use_subprocess")

def order_instacart(product_link):
    driver = webdriver.Chrome(options=chrome_options)
    # Open the URL
    driver.get(LOGIN_URL)
    time.sleep(1)
    email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    email_input.send_keys(INSTACART_EMAIL)
    time.sleep(1)
    email_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    email_input.send_keys(INSTACART_PASSWORD)
    time.sleep(1)
    submit_button = driver.find_element(
        By.CSS_SELECTOR, "button[class='e-ztomkz']")
    submit_button.click()

    # Captcha solver
    # capsolver = RecaptchaV2Task(CAPTCHA_API_KEY)
    # task_id = capsolver.create_task(login_url, "website_key")
    # result = capsolver.join_task_result(task_id)
    # print(result.get("gRecaptchaResponse"))
    # time.sleep(30)

    time.sleep(5)
    driver.get(product_link)

    time.sleep(12)

    button = driver.find_element(By.CLASS_NAME, 'e-1mchykm')
    button.click()

    driver.implicitly_wait(5)
    driver.get(CHECKOUT_LINK)

    # text_area = driver.find_element(By.ID, "deliveryInstructions")
    # text_area.send_keys("Please leave at the front door")
    # save_and_continue = driver.find_element(By.CLASS_NAME, "e-15utg5h")
    # save_and_continue.click()
    time.sleep(2)
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.e-rloafg")))
    element.click()
    time.sleep(4)
    # phone_number = driver.find_element(By.CSS_SELECTOR, "input[type='tel']")
    # phone_number.send_keys("2034518641")
    # submit_phone_number = driver.find_element(By.CLASS_NAME, "e-sp84se")
    # submit_phone_number.click()
    # time.sleep(4)
    final_continue = driver.find_element(By.CLASS_NAME, "e-15utg5h")
    final_continue.click()
    time.sleep(3)

    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Continue')]]"))
    )
    button.click()

    time.sleep(10)

    #Simulating Order Placed (uncomment)
    # Find the span element by its text content "Place order"
    place_order_span = driver.find_element(
        By.XPATH, "//span[text()='Place order']")
    # Click the span element
    place_order_span.click()

    print("Order placed!!")
    driver.quit()

def order_coffee():
    order_instacart(COFFEE_LINK)

def order_medicine():
    order_instacart(MEDICINE_LINK)