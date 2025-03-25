from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import os


def save_cookies(driver):
    """Save cookies to a file"""
    cookies = driver.get_cookies()
    with open('cookies.json', 'w') as file:
        json.dump(cookies, file)
    print('New cookies saved successfully')


def load_cookies(driver):
    """Load cookies from a file"""
    if 'cookies.json' in os.listdir():
        with open('cookies.json', 'r') as file:
            cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
        isr = driver.refresh()
        print(isr, "========== is refresh return something? =========")
        return True
    else:
        print('No cookies file found')
        return False


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


def main():
    # Start with non-headless mode for login
    driver = create_driver(headless=False)

    try:
        # Navigate to the login page directly
        login_url = 'https://www.zhipin.com/web/user/?intent=0&ka=header-geek'
        driver.get(login_url)

        # Load old session into the browser
        if load_cookies(driver):
            print('Previous session loaded successfully')
            driver.get("https://www.zhipin.com")
            wait_for_page_load(driver)
        else:
            print('\nPlease login manually using WeChat or Phone OTP.')
            print('You have 60 seconds to complete the login process.')
            print('Waiting for login...')

            try:
                # Wait for successful login
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".online-service"))
                )
                print("Login successful!")
                save_cookies(driver)
            except Exception:
                print("Login timeout or failed!")
                return

        # Navigate to main page
        driver.get("https://www.zhipin.com")
        wait_for_page_load(driver)

        # Print basic information
        print(f"Title: {driver.title}")
        print(f"Current URL: {driver.current_url}")

        # Get page content
        page_text = driver.find_element("tag name", "body").text
        print("\nPage Content:")
        print(page_text[:1000])  # Print first 1000 characters

        # Get all links
        links = driver.find_elements("tag name", "a")
        print("\nLinks found:", len(links))
        for link in links[:5]:  # Print first 5 links
            print(
                f"Link text: {link.text} -> URL: {link.get_attribute('href')}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
