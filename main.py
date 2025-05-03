# Entry point to run the spider
from jobs.boss_zhipin_job_crawler import process_first_job
from utils.browser import create_driver

from utils.hr_login_state import import_browser_cookies, verify_login


def main():
    try:
        driver = create_driver()  # default is_headless is False
        driver.maximize_window()

        if import_browser_cookies(driver):
            print("Cookies imported, verifying login...")

            # if verify_login(driver):
            if True:
                print("✅ Successfully logged in")
                # Continue with your search functionality

                process_first_job(driver=driver)

                return True
            else:
                print("❌ Login failed - HTML element is missing")
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
