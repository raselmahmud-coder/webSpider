# Entry point to run the spider
import time
from config import BASE_URL, JOB_QUERY
from jobs.boss_zhipin_job_crawler import do_query_by_skills, process_first_job
from search_engine import get_search_result
from utils.browser import create_driver, wait_for_page_load
from auth.cookie_manager import save_cookies, load_cookies
from jobs.job_handler import apply_to_jobs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def main_search_engine(query):
    try:
        driver = create_driver()  # default is_headless is False
        is_result_return = get_search_result(driver=driver, query=query)
        if is_result_return:
            print("Baidu search result returned", is_result_return)
            return is_result_return

        else:
            return ("Not found Baidu search result")

    except Exception as e:
        print("inside function error", e)

    finally:
        driver.quit()


if __name__ == "__main_search_engine__":
    main_search_engine()
