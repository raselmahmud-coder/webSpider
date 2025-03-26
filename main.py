# Entry point to run the spider
from utils.browser import create_driver, wait_for_page_load
from auth.cookie_manager import save_cookies, load_cookies
from jobs.job_handler import apply_to_jobs
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def main():
    # Start with non-headless mode for login
    driver = create_driver(headless=False)
    # Maximize the browser window
    driver.maximize_window()

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
