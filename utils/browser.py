# Selenium browser helper functions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def create_driver(headless=True):
    """Create a new Chrome driver with given headless setting"""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--disable-web-security")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=options)


def wait_for_page_load(driver, timeout=10):
    """Wait for page to load completely"""
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script(
            'return document.readyState') == 'complete'
    )
