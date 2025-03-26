import time
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
    """Load cookies from a file and validate them"""
    try:
        if 'cookies.json' in os.listdir():
            # First navigate to the site before adding cookies
            driver.get("https://www.zhipin.com")
            wait_for_page_load(driver)

            with open('cookies.json', 'r') as file:
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


def handle_job_card(driver, job, index):
    """Handle individual job card interaction"""
    try:
        # Scroll job into view first
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", job)
        time.sleep(1)  # Wait for scroll

        # Click job card to make it active
        job.click()
        time.sleep(1)  # Wait for active state

        # Wait for job card to become active
        active_job = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".job-card-wrap.active"))
        )

       # Now that card is active, find buttons within the active card
        buttons = driver.find_elements(By.CSS_SELECTOR, ".op-btn")
        print("here is button list expected", buttons)
        if len(buttons) > 0:
            # Get the first like button from the list
            like_button = buttons[0]

            # Wait for button to be clickable
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".op-btn.op-btn-like"))
            )

            # Try to click the button using JavaScript
            driver.execute_script("arguments[0].click();", like_button)
            print("Like button clicked")
            time.sleep(1)  # Wait for click to register
        else:
            print("No like button found")
            return False

        return True

    except Exception as e:
        print(f"Error handling job card {index + 1}: {str(e)}")
        return False


def apply_to_jobs(driver):
    """Function to handle job applications"""
    try:
        driver.get("https://www.zhipin.com/web/geek/job-recommend")
        # Wait for page loading
        wait_for_page_load(driver)
        # Wait for job list container to be present
        job_list = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".rec-job-list"))
        )

        # Add a short delay to ensure dynamic content loads
        time.sleep(3)
        # Scroll down slightly to trigger lazy loading
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(2)
        # Now find all job cards with explicit wait
        job_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".job-card-wrap"))
        )[:2]

        print(f"Found {len(job_cards)} jobs")

        if len(job_cards) == 0:
            print("Debug info:")
            print(f"Current URL: {driver.current_url}")
            print("Page source preview:", driver.page_source[:500])
            return

        for index, job in enumerate(job_cards):
            try:
                # Get job title before click for debugging
                job_title = job.find_element(By.CSS_SELECTOR, ".job-name").text
                print(
                    f"\nAttempting to click job {index + 1}: {job_title} and the job+++ {job}")

                # Handle job card interaction
                if handle_job_card(driver, job, index):
                    print(f"Successfully processed job {index + 1}")
                else:
                    print(f"Failed to process job {index + 1}")

                # # Wait for apply button and click it
                # apply_button = WebDriverWait(driver, 10).until(
                #     EC.element_to_be_clickable(
                #         (By.CSS_SELECTOR, ".op-btn.op-btn-like"))
                # )
                # print(f"Applying to job {index + 1}")
                # apply_button.click()

                # # Wait a moment for the application to process
                # time.sleep(2)

                # # Scroll job into view
                # driver.execute_script(
                #     "arguments[0].scrollIntoView(true);", job)

                # # Click on the job card to view details
                # job.click()
                # wait_for_page_load(driver)

                # # Go back to job list if needed
                # driver.back()
                # wait_for_page_load(driver)

                # # Verify if job card became active
                # active_job = driver.find_element(
                #     By.CSS_SELECTOR, ".job-card-wrap.active")
                # if active_job:
                #     print(f"Job card {index + 1} is now active")

            except Exception as e:
                print(f"Failed to apply for job {index + 1}: {str(e)}")
                continue

    except Exception as e:
        print(f"Error in job application process: {str(e)}")


def main():
    # Start with non-headless mode for login
    driver = create_driver(headless=False)

    try:
        # A logged in user try to load old session into the browser
        if load_cookies(driver):
            print('Previous session loaded successfully')
            # Call the apply_to_jobs function
            apply_to_jobs(driver)

        else:
            print('\nPlease login manually using WeChat or Phone OTP.')
            print('You have 60 seconds to complete the login process.')
            print('Waiting for login...')

            try:
                # Either new user or cookie is expired need to navigate for login
                login_url = 'https://www.zhipin.com/web/user/?intent=0&ka=header-geek'
                driver.get(login_url)
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

        print(f"Current URL: {driver.current_url}")

        # Get page content
        page_text = driver.find_element("tag name", "body").text
        print("\nPage Content:")
        print(page_text[:10])  # Print first 1000 characters

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
