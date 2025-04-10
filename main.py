# Entry point to run the spider
import time
from config import BASE_URL, JOB_QUERY
from jobs.boss_zhipin_job_crawler import do_query_by_skills, process_first_job
from utils.browser import create_driver, wait_for_page_load
from auth.cookie_manager import save_cookies, load_cookies
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from utils.hr_login_state import import_browser_cookies, verify_login


def main():
    try:
        driver = create_driver()  # default is_headless is False
        driver.maximize_window()

        if import_browser_cookies(driver):
            print("Cookies imported, verifying login...")

            if verify_login(driver):
                print("✅ Successfully logged in")
                # Continue with your search functionality
                try:
                    job_cards = do_query_by_skills(driver=driver)
                    print("Job cards found ===>>> digging into first job",
                          len(job_cards))

                    process_first_job(driver=driver, job_cards=job_cards)

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
        print("inside function error", e)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
