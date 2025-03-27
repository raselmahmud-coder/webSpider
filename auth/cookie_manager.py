import json
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from utils import wait_for_page_load


def save_cookies(driver):
    """Save cookies to a file"""
    cookies = driver.get_cookies()
    with open('userSecret/cookies.json', 'w') as file:
        json.dump(cookies, file)
    print('New cookies saved successfully')


def load_cookies(driver):
    """Load cookies from a file and validate them"""
    try:
        if 'userSecret/cookies.json' in os.listdir():
            # First navigate to the site before adding cookies
            driver.get("https://www.zhipin.com")
            wait_for_page_load(driver=driver)

            with open('userSecret/cookies.json', 'r') as file:
                cookies = json.load(file)

            # Check if cookies exist and are not expired
            current_time = time.time()
            valid_cookies = []

            for cookie in cookies:
                try:
                    # Standardize domain format
                    if cookie['domain'] == 'www.zhipin.com':
                        cookie['domain'] = '.zhipin.com'

                    # Convert expiry to integer if exists
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                        if cookie['expiry'] > current_time:
                            valid_cookies.append(cookie)
                    else:
                        valid_cookies.append(cookie)

                    # Remove sameSite attribute
                    if 'sameSite' in cookie:
                        del cookie['sameSite']

                except Exception as e:
                    print(
                        f"Error processing cookie {cookie.get('name')}: {str(e)}")
                    continue

            if not valid_cookies:
                print('No valid cookies found')
                return False

            # Add valid cookies to driver
            success_count = 0
            for cookie in valid_cookies:
                try:
                    driver.add_cookie(cookie)
                    success_count += 1
                except Exception as e:
                    print(
                        f"Error adding cookie {cookie.get('name')}: {str(e)}")
                    continue

            print(
                f"Successfully added {success_count}/{len(valid_cookies)} cookies")

            # Refresh and verify login state
            driver.refresh()
            wait_for_page_load(driver)

            # Verify login status
            try:
                driver.get("https://www.zhipin.com/web/geek/job-recommend")
                # Wait for page loading
                wait_for_page_load(driver)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".label-text"))
                )
                print('Cookie validation successful - user is logged in')
                return True
            except Exception:
                print('Cookie validation failed - user is not logged in')
                return False

        else:
            print('No cookies file found')
            return False

    except Exception as e:
        print(f'Error loading cookies: {str(e)}')
        return False
