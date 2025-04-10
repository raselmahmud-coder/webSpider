import os
from datetime import datetime
import json
from selenium.webdriver.support.ui import WebDriverWait
from utils import wait_for_page_load
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

BASE_DIR = os.getcwd()


def validate_cookie_format(cookie):
    """Validate individual cookie format"""
    required_fields = ['name', 'value', 'domain']
    return all(field in cookie for field in required_fields)


def validate_cookies_file(cookies):
    """Validate the entire cookies file"""
    if not isinstance(cookies, list):
        return False
    return all(validate_cookie_format(cookie) for cookie in cookies)


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


def verify_login(driver):
    """Verify if the login is successful with better checks"""
    try:
        # First check if we're redirected to login page
        driver.get('https://www.zhipin.com/web/chat/search')
        # Add explicit wait for page load
        driver.execute_script("return document.readyState") == "complete"
        wait = WebDriverWait(driver, 10)

        # Check for login indicators with descriptive names
        login_indicators = [
            ("Card List", By.CSS_SELECTOR, ".card-list"),
            ("Logout Button", By.CSS_SELECTOR, ".nav-item.nav-logout"),
            ("Profile Card", By.CSS_SELECTOR,
             "[class*='.geek-info-card.geek-info-card-gray1013']")
        ]

        found_elements = []
        missing_elements = []

        for name, by, selector in login_indicators:
            try:
                element = wait.until(
                    EC.presence_of_element_located((by, selector)))
                if element.is_displayed():
                    found_elements.append(name)
                else:
                    missing_elements.append(f"{name} (hidden)")
            except:
                missing_elements.append(name)

        # Print status report
        if found_elements:
            print("✅ Found elements:")
            for element in found_elements:
                print(f"  • {element}")

        if missing_elements:
            print("❌ Missing elements:")
            for element in missing_elements:
                print(f"  • {element}")

        # Check if redirected to login page
        if 'login' in driver.current_url.lower():
            print("❌ Redirected to login page - not logged in")
            return False

        # Consider login successful if at least one indicator is found
        return len(found_elements) > 0

    except Exception as e:
        print(f"❌ Login verification failed: {str(e)}")
        return False
