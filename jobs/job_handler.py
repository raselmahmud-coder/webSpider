import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from utils import wait_for_page_load


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
