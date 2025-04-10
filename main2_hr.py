# Entry point to run the spider
from utils.browser import create_driver, wait_for_page_load
from auth.cookie_manager import save_cookies, load_cookies
from jobs.job_handler import apply_to_jobs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from utils.hr_login_state import import_browser_cookies, verify_login


def search_jobs(driver, keyword="前端开发工程师·合肥"):
    try:
        print("✅ Successfully logged in")

        # Step 1: Wait for any loading toast to disappear
        wait = WebDriverWait(driver, 15)

        try:
            wait.until(EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".toast[style*='display: none']"))
            )
            print("✅ Toast loading indicator has disappeared.")
        except Exception as e:
            print("⚠️ Timeout or error waiting for toast to disappear:", e)

        # Step 2: Ensure the page has fully rendered (dynamic content)
        try:
            print("⏳ Waiting for dynamic content to render...")
            search_input = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[contains(@class, 'search-input')]")))
            print("✅ Dynamic content is fully loaded.")
        except Exception as e:
            print("⚠️ Error waiting for dynamic content to render:", e)
            return

        # Step 3: Wait for the search input element to be visible
        try:
            search_input = wait.until(EC.visibility_of(search_input))
            print("✅ Search input is visible.")
        except Exception as e:
            print("⚠️ Error waiting for search input visibility:", e)
            return

        # Step 4: Check if the search input is interactable
        try:
            if search_input.is_displayed() and search_input.is_enabled():
                # Extract the placeholder text from the search input
                placeholder_text = search_input.get_attribute("placeholder")
                print(f"Placeholder text is: {placeholder_text}")
            else:
                print("⚠️ Search input is not interactable.")
                return
        except Exception as e:
            print("⚠️ Error checking search input interactability:", e)
            return

        # Step 5: Enter search term and click search
        try:
            search_input.clear()
            search_input.send_keys(keyword)
            search_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//i[@class='icon-search']")))
            search_button.click()
            print("✅ Search button clicked.")
        except Exception as e:
            print("⚠️ Error interacting with search input or button:", e)
            return

        # Step 6: Wait for the results to be loaded
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'job-list-box')]")))
            print("✅ Search results loaded.")
        except Exception as e:
            print("⚠️ Error waiting for search results to load:", e)
            return

        # Step 7: Verify each <li> element text is loaded
        try:
            print("⏳ Verifying job list items...")
            job_list_items = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".card-list .geek-info-card")))

            for index, item in enumerate(job_list_items):
                try:
                    text_content = item.text.strip()
                    if text_content:
                        print(f"✅ Job item {index + 1} loaded: {text_content}")
                    else:
                        print(f"⚠️ Job item {index + 1} has no text content.")
                except Exception as e:
                    print(f"⚠️ Error processing job item {index + 1}: {e}")
        except Exception as e:
            print("⚠️ Error verifying job list items:", e)

    except Exception as e:
        print("Error in search page:", e)
        print(driver.page_source)  # Print page source to debug the issue


def main():
    driver = None
    try:
        driver = create_driver(is_headless=False)
        driver.maximize_window()

        print("Importing cookies...")
        if import_browser_cookies(driver):
            print("Cookies imported, verifying login...")

            if verify_login(driver):
                print("✅ Successfully logged in")
                # Continue with your search functionality
                try:
                    search_jobs(driver)

                except Exception as e:
                    print("Error in search page button", e)

                return True
            else:
                print("❌ Login failed - please check your cookies")
                print("Redirecting to manual login page...")
                driver.get(
                    'https://www.zhipin.com/web/user/?intent=1&ka=header-boss')
                return False
        else:
            print("X Cookie import failed")
            return False

    except Exception as e:
        print(f"Critical error: {str(e)}")
        return False
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
