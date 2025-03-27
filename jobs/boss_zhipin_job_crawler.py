
import time
from config import BASE_URL, JOB_QUERY
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
                        timeout=10
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


def open_new_tab_n_extract_job(driver, job_cards):
    try:
        # Get the current file's directory and set up paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)

        # Set up data directories
        DATA_DIR = os.path.join(project_root, 'data')
        IMAGE_DIR = os.path.join(DATA_DIR, 'images', 'hr_images')

        # Create directories if they don't exist
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(IMAGE_DIR, exist_ok=True)

        # CSV file setup
        csv_file_path = os.path.join(DATA_DIR, "job_details.csv")

        # Create CSV file with headers if it doesn't exist
        file_exists = os.path.exists(csv_file_path)

        # Process each job
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'job_title', 'salary', 'city', 'experience', 'degree',
                'skills', 'job_description', 'hr_name',
                'hr_company_name_n_designation', 'hr_pic_path'
            ])

            # Write header only if file is new
            if not file_exists:
                writer.writeheader()

            for index, job_item in enumerate(job_cards[:5]):
                print("hello job item", job_item)
                try:
                    # Find and click job title with retry
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            # Wait for the page to settle after previous iteration
                            time.sleep(2)
                            # Scroll job into view
                            driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                                job_item
                            )
                            time.sleep(1)

                            # Locate job title using WebDriverWait for better reliability
                            job_title_element = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable(
                                    (By.XPATH,
                                     ".//div[contains(@class, 'job-title')]")
                                )
                            )
                            job_title = job_title_element.text
                            print(f"\nProcessing job {index + 1}: {job_title}")

                            # Try clicking with JavaScript if regular click fails
                            try:
                                job_title_element.click()
                            except:
                                driver.execute_script(
                                    "arguments[0].click();", job_title_element)

                             # Verify new tab opened
                            if len(driver.window_handles) > 1:
                                break

                        except Exception as e:
                            print(
                                f"Click attempt {attempt + 1} failed: {str(e)}")
                            if attempt == max_retries - 1:
                                raise
                            time.sleep(2)

                    # Wait for new tab
                    WebDriverWait(driver, 10).until(
                        lambda d: len(d.window_handles) > 1
                    )
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(2)  # Allow page to load

                    print("New tab clicked waiting for visible the element")
                    # Wait for job detail section to be visible and verify content
                    detail_section = WebDriverWait(driver, 60).until(
                        EC.visibility_of_element_located(
                            (By.XPATH,
                                "//div[contains(@class, 'job-detail-section')]")
                        )
                    )

                    # Verify if the section contains any text
                    if not detail_section.text.strip():
                        raise Exception("Job detail section is empty")
                    print("Job detail section loaded with content")

                    # Verify critical elements are present and visible
                    critical_elements = {
                        'job_title': "//h1",
                        'salary': "//span[contains(@class, 'salary')]",
                        'city': "//a[contains(@class, 'text-city')]",
                        'experience': "//span[contains(@class, 'text-experiece')]",
                        'degree': "//span[contains(@class, 'text-degree')]",
                        'skills': "//ul[contains(@class, 'job-keyword-list')]",
                        'job_description': "//div[contains(@class, 'job-sec-text')]"
                    }

                    # Check each critical element
                    for element_name, xpath in critical_elements.items():
                        element = WebDriverWait(driver, 60).until(
                            EC.visibility_of_element_located((By.XPATH, xpath))
                        )
                        if not element.text.strip():
                            raise Exception(f"{element_name} is empty")
                        print(
                            f"{element_name} loaded with content: {element.text}")

                    # If all verifications pass, proceed with data extraction
                    print("All elements verified, proceeding with data extraction...")

                    # After successfully loading job details, collect all information
                    job_data = {}

                    # Extract job details
                    job_data['job_title'] = driver.find_element(
                        By.XPATH, "//h1").text
                    job_data['salary'] = driver.find_element(
                        By.XPATH, "//span[contains(@class, 'salary')]").text
                    job_data['city'] = driver.find_element(
                        By.XPATH, "//a[contains(@class, 'text-city')]").text
                    job_data['experience'] = driver.find_element(
                        By.XPATH, "//span[contains(@class, 'text-experiece')]").text
                    job_data['degree'] = driver.find_element(
                        By.XPATH, "//span[contains(@class, 'text-degree')]").text
                    job_data['skills'] = driver.find_element(
                        By.XPATH, "//ul[contains(@class, 'job-keyword-list')]").text
                    job_data['job_description'] = driver.find_element(
                        By.XPATH, "//div[contains(@class, 'job-sec-text')]").text

                    # HR information section
                    # HR Profile Picture URL
                    hr_pic_url = driver.find_element(
                        By.XPATH, "//div[contains(@class, 'detail-figure')]/img"
                    ).get_attribute("src")
                    print("hello hr pic", hr_pic_url)
                    # Download the HR profile picture
                    # Generate a unique filename
                    hr_pic_filename = f"hr_image_{index + 1}.jpg"

                    job_data['hr_name'] = driver.execute_script(""" 
                        var element = document.querySelector('h2.name');
                        return element.childNodes[0].nodeValue.trim();
                    """)
                    # Extract HR designation using JavaScript
                    job_data['hr_company_name_n_designation'] = driver.execute_script(""" 
                        var element = document.querySelector('.boss-info-attr');
                        var text = element.textContent;
                        return text.split('·').pop().trim();
                    """)

                    print(
                        f"expect hr name => {job_data['hr_name']}, HR Designation=> {job_data['hr_company_name_n_designation']}")

                    # Handle HR profile picture
                    hr_pic_url = driver.find_element(
                        By.XPATH, "//div[contains(@class, 'detail-figure')]/img"
                    ).get_attribute("src")

                    # Save HR profile picture
                    hr_pic_filename = f"hr_image_{index + 1}.jpg"
                    hr_pic_path = os.path.join(IMAGE_DIR, hr_pic_filename)

                    try:
                        response = requests.get(hr_pic_url, stream=True)
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

                    # Write the job data to CSV
                    writer.writerow(job_data)
                    print(f"Saved job {index + 1} data to CSV")

                    # Close current tab and switch back to main window
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(1)

                except Exception as e:
                    print(f"Error processing job {index + 1}: {str(e)}")
                    continue

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
