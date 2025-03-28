# Entry point to run the spider
import time
from config import BASE_URL, JOB_QUERY
from jobs.boss_zhipin_job_crawler import do_query_by_skills, process_first_job
from utils.browser import create_driver, wait_for_page_load
from auth.cookie_manager import save_cookies, load_cookies
from jobs.job_handler import apply_to_jobs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def main():
    try:
        driver = create_driver()  # default is_headless is False
        job_cards = do_query_by_skills(driver=driver, skill="Java")

        if len(job_cards) > 0:
            print("query func loaded ************ ", len(job_cards[:5]))
            process_first_job(driver=driver, job_cards=job_cards)
    except Exception as e:
        print("inside function error", e)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
