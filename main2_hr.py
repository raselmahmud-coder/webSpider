# Entry point to run the spider
from utils.browser import create_driver, wait_for_page_load
from auth.cookie_manager import save_cookies, load_cookies
from jobs.job_handler import apply_to_jobs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def import_browser_cookies(driver, cookie_file=os.path.join(BASE_DIR, 'userSecret', 'browser_cookies.json')):
    """Import cookies from browser export with validation"""
    try:
        if not os.path.exists(cookie_file):
            print(f"Cookie file {cookie_file} not found")
            return False

        with open(cookie_file, 'r', encoding='utf-8') as file:
            cookies = json.load(file)

        # Validate cookies format
        if not validate_cookies_file(cookies):
            print("Invalid cookie format")
            return False

        # Load domain before adding cookies
        driver.get('https://www.zhipin.com')
        wait_for_page_load(driver)

        # Clear existing cookies
        driver.delete_all_cookies()

        success_count = 0
        for cookie in cookies:
            try:
                # Remove any problematic fields
                cookie_dict = {k: v for k, v in cookie.items() if k in
                               ['name', 'value', 'domain', 'path', 'secure', 'httpOnly', 'expiry']}
                driver.add_cookie(cookie_dict)
                success_count += 1
            except Exception as e:
                print(f"Error adding cookie {cookie.get('name')}: {str(e)}")

        print(f"Successfully added {success_count}/{len(cookies)} cookies")
        driver.refresh()
        return success_count > 0

    except Exception as e:
        print(f"Error importing cookies: {str(e)}")
        return False


def validate_cookie_format(cookie):
    """Validate individual cookie format"""
    required_fields = ['name', 'value', 'domain']
    return all(field in cookie for field in required_fields)


def validate_cookies_file(cookies):
    """Validate the entire cookies file"""
    if not isinstance(cookies, list):
        return False
    return all(validate_cookie_format(cookie) for cookie in cookies)


def verify_login(driver):
    """Verify if the login is successful with better checks"""
    try:
        # First check if we're redirected to login page
        driver.get('https://www.zhipin.com/web/chat/index')
        wait = WebDriverWait(driver, 10)

        # Check for login indicators
        login_indicators = [
            (By.CSS_SELECTOR, ".chat-container"),
            # User navigation usually present when logged in
            (By.CSS_SELECTOR, ".user-nav"),
            (By.CSS_SELECTOR, "[class*='header-user']")  # User header element
        ]

        for indicator in login_indicators:
            try:
                element = wait.until(EC.presence_of_element_located(indicator))
                if element.is_displayed():
                    print(f"Login verified via indicator: {indicator[1]}")
                    return True
            except:
                continue

        # Check if redirected to login page
        if 'login' in driver.current_url.lower():
            print("Redirected to login page - not logged in")
            return False

        return False

    except Exception as e:
        print(f"Login verification failed: {str(e)}")
        return False


def main():
    driver = None
    try:
        driver = create_driver(is_headless=False)
        driver.maximize_window()

        print("Importing cookies...")
        if import_browser_cookies(driver):
            print("Cookies imported, verifying login...")

            if verify_login(driver):
                print("✓ Successfully logged in")
                # Continue with your search functionality
                return True
            else:
                print("× Login failed - please check your cookies")
                print("Redirecting to manual login page...")
                driver.get(
                    'https://www.zhipin.com/web/user/?intent=1&ka=header-boss')
                return False
        else:
            print("× Cookie import failed")
            return False

    except Exception as e:
        print(f"Critical error: {str(e)}")
        return False
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
