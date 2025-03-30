import time
from config import BASE_URL, JOB_QUERY
from jobs.boss_company_details_crawler import extract_company_info
from utils import create_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv
import os
import requests

from utils.browser import wait_for_element


def do_query_by_skills(driver, skill="Java"):
    try:
        job_query = BASE_URL + JOB_QUERY
        print("job hello", job_query)
        driver.get(job_query)

        # Wait for query results to load with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Wait for job list container

                job_list = wait_for_element(
                    driver, "//ul[contains(@class, 'job-list-box')]")
                if not job_list:
                    raise Exception("Failed to load job list container")

                # Wait for job cards
                job_cards = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH,
                         ".//li[contains(@class, 'job-card-wrapper')]")
                    )
                )

                # Verify if job cards contain content
                if len(job_cards) > 0:
                    # Wait for first job card to have content
                    first_job = wait_for_element(
                        driver,
                        "//li[contains(@class, 'job-card-wrapper')]//div[contains(@class, 'job-title')]",
                        wait_type="visibility",
                        timeout=30
                    )

                    # Verify if job title is loaded
                    if first_job:
                        print(
                            f"Query results loaded successfully. Found {len(job_cards)} jobs.")
                        return job_cards
                    else:
                        raise Exception(
                            "Job cards found but content not loaded")
                else:
                    raise Exception("No job cards found")

            except Exception as e:
                print(f"Load attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(
                        "Failed to load query results after multiple attempts")
                driver.refresh()
                time.sleep(2)

    except Exception as e:
        print(
            f"Reason for failed=> {str(e)}")


""" New function for click and wait for loading a single job in new tab then extract information about the job and HR
"""


def extract_single_job_info(driver, job_card, index):
    """Extract information from a single job card"""
    try:
        job_title_element = job_card.find_element(
            By.XPATH, ".//div[contains(@class, 'job-title')]")
        print("single job ==========>", job_title_element.text)
        # Set up data directories
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        DATA_DIR = os.path.join(project_root, 'data')
        IMAGE_DIR = os.path.join(DATA_DIR, 'images', 'hr_images')
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(IMAGE_DIR, exist_ok=True)

        # Scroll job card into view
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
            job_title_element
        )
        time.sleep(1)

        # Click on job title element
        driver.execute_script("arguments[0].click();", job_title_element)

        # Wait for new tab and switch to it
        WebDriverWait(driver, 30).until(lambda d: len(d.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)

        # Dictionary of elements to extract
        elements_to_extract = {
            'job_title': "//h1",
            'salary': "//span[contains(@class, 'salary')]",
            'city': "//a[contains(@class, 'text-city')]",
            'experience': "//span[contains(@class, 'text-experiece')]",
            'degree': "//span[contains(@class, 'text-degree')]",
            'skills': "//ul[contains(@class, 'job-keyword-list')]",
            'job_description': "//div[contains(@class, 'job-sec-text')]"
        }

        # Extract job data
        job_data = {}
        for key, xpath in elements_to_extract.items():
            element = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            job_data[key] = element.text.strip()
            if not job_data[key]:
                raise Exception(f"Empty value for {key}")

        print("hello job new dic", job_data)

        # Extract HR information
        job_data['hr_name'] = driver.execute_script("""
            var element = document.querySelector('h2.name');
            return element.childNodes[0].nodeValue.trim();
        """)

        job_data['hr_designation'] = driver.execute_script("""
            var element = document.querySelector('.boss-info-attr');
            return element.textContent.split('·').pop().trim();
        """)

        # Handle HR profile picture
        hr_pic_url = driver.find_element(
            By.XPATH, "//div[contains(@class, 'detail-figure')]/img"
        ).get_attribute("src")

        # Save HR image
        timestamp = int(time.time())
        hr_pic_filename = f"hr_image_{index}_{timestamp}.jpg"
        hr_pic_path = os.path.join(IMAGE_DIR, hr_pic_filename)

        try:
            response = requests.get(hr_pic_url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(hr_pic_path, "wb") as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)
                job_data['hr_pic_path'] = hr_pic_path
            else:
                job_data['hr_pic_path'] = "N/A"
        except Exception as e:
            print(f"Failed to save HR image: {str(e)}")
            job_data['hr_pic_path'] = "N/A"

        print("final version ==========*******=========> ", job_data)
        extract_company_info(driver, index)
        return job_data

    finally:
        # Close the job detail tab and switch back to main window
        driver.close()
        driver.switch_to.window(driver.window_handles[0])


def save_job_to_csv(job_data, csv_file_path):
    """Save job data to CSV file"""
    file_exists = os.path.exists(csv_file_path)
    fieldnames = [
        'job_title', 'salary', 'city', 'experience', 'degree',
        'skills', 'job_description', 'hr_name',
        'hr_designation', 'hr_pic_path'
    ]

    with open(csv_file_path, mode='a' if file_exists else 'w',
              newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(job_data)


# Main function to process the first job card
def process_first_job(driver, job_cards):
    """Process only the first job card"""
    try:
        if not job_cards or len(job_cards) == 0:
            raise Exception("No job cards found")

        # Set up CSV file path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        csv_file_path = os.path.join(project_root, 'data', "job_details.csv")

        # Extract and save job information for multiple cards
        for index in range(5):
            try:
                print(f"Processing job {index + 1}")
                job_data = extract_single_job_info(
                    driver, job_cards[index], index=index)
                # Save each job_data immediately after extraction
                save_job_to_csv(job_data, csv_file_path)
                print(f"Successfully saved job {index + 1}")
            except Exception as e:
                print(f"Error processing job {index + 1}: {str(e)}")
                continue

        print("Successfully processed and saved all job information")

    except Exception as e:
        print(f"Error processing first job: {str(e)}")
