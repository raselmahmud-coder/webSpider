# Selenium browser helper functions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from typing import Optional


def create_driver(is_headless=False):
    """Create a new Chrome driver with given is_headless setting"""
    options = Options()
    if is_headless:
        options.add_argument("--is_headless=new")

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
    driver = webdriver.Chrome(options=options)

    if not is_headless:
        driver.maximize_window()

    return driver


def wait_for_page_load(driver, timeout=30):
    """Wait for page to load completely"""
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script(
            'return document.readyState') == 'complete'
    )


def wait_for_element(
    driver,
    xpath: str,
    timeout: int = 30,
    check_text: bool = True,
    wait_type: str = "presence"
) -> Optional[object]:
    """
    Dynamically wait for and verify an element by xpath.

    Args:
        driver: Selenium WebDriver instance
        xpath: XPATH string to locate element
        timeout: Maximum time to wait in seconds
        check_text: Whether to verify element has text content
        wait_type: Type of wait - "presence" or "visibility"

    Returns:
        WebElement if found, None if not found or verification fails
    """
    try:
        # Choose wait condition based on wait_type
        wait_condition = (
            EC.presence_of_element_located if wait_type == "presence"
            else EC.visibility_of_element_located
        )

        # Wait for element
        element = WebDriverWait(driver, timeout).until(
            wait_condition((By.XPATH, xpath))
        )

        # Verify text content if required
        if check_text and not element.text.strip():
            print(f"Element found but no text content: {xpath}")
            return None

        return element

    except Exception as e:
        print(f"Error waiting for element {xpath}: {str(e)}")
        return None
