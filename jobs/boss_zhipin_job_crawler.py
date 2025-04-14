import time
from config import BASE_URL, EXPERIENCE_LEVELS_MAPPING, IT_SKILLS, JOB_QUERY, EXPERIENCE_LEVELS, POSITION_TYPES, POSITION_TYPES_MAPPING
from jobs.boss_company_details_crawler import extract_company_details_info
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidSessionIdException, TimeoutException, WebDriverException


import csv
import os
import requests

from utils.browser import wait_for_element
from utils.random_sleep import random_delay


def get_total_pages(driver):
    """Extract the total number of pages from the pagination section."""
    try:
        # Wait for the pagination area to be loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "pagination-area"))
        )

        # Extract all page number links (excluding the 'disabled' and navigation elements like arrows)
        page_links = driver.find_elements(
            By.XPATH, "//div[contains(@class, 'pagination-area')]//div[contains(@class, 'options-pages')]//a[not(contains(@class, 'disabled')) and not(contains(@class, 'ui-icon-arrow')) and not(contains(@class, 'fast-next-btn'))]")

        # Extract the text (page numbers) from the links and convert to integers
        page_numbers = [int(link.text)
                        for link in page_links if link.text.isdigit()]

        # If there are valid page numbers, return the largest one (the max page number)
        if page_numbers:
            max_page = max(page_numbers)
            print(f"Total pages available: {max_page}")
            return max_page
        else:
            print("No valid page numbers found.")
            return 0  # In case no valid page numbers are found

    except Exception as e:
        print(f"Error extracting total pages: {str(e)}")
        return 0


def do_query_by_skills(driver, filter_query):
    """ do_query_by_skills function for click and wait for loading first page and confirm the total job list length """
    try:

        print("Full Query looks like ==>>", filter_query)
        driver.get(filter_query)

        # Wait for query results to load with retry mechanism
        max_retries = 1
        for attempt in range(max_retries):
            print("Attempt to extract job card data")
            try:
                # Wait for job list container

                job_list = wait_for_element(
                    driver, "//ul[contains(@class, 'job-list-box')]")
                if not job_list:
                    return {"job_cards": [], "total_page": []}

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
                        total_page = get_total_pages(driver)

                        return {"job_cards": job_cards, "total_page": total_page}
                    else:
                        return {"job_cards": [], "total_page": 0}
                else:
                    return {"job_cards": [], "total_page": 0}

            except Exception as e:
                print(f"Load attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(
                        "Failed to load query results after multiple attempts")
                driver.refresh()
                random_delay(3, 8)

    except Exception as e:
        print(
            f"Reason for failed=> {str(e)}")


def save_job_to_csv(job_data, csv_file_path):
    """Save job data to CSV file"""
    try:
        file_exists = os.path.exists(csv_file_path)
        fieldnames = [
            'company_short_name',
            'job_title', 'salary', 'city', 'experience', 'degree',
            'skills', 'job_description', 'hr_name',
            'hr_designation', 'hr_pic_path', 'skill_category', 'position_type', 'experience_level'
        ]

        with open(csv_file_path, mode='a' if file_exists else 'w',
                  newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(job_data)

    except Exception as e:
        print(f"csv file error: {str(e)}")


def extract_company_info_from_job_card(driver, job_card):
    """Extract company information from the job card using XPath."""
    company_info = {}

    try:
        # Wait for the job card to be fully loaded (if necessary)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, ".//div[contains(@class, 'company-logo')]"))
        )

        # Extract company logo URL
        logo_element = job_card.find_element(
            By.XPATH, ".//div[contains(@class, 'company-logo')]//img")
        company_info['company_logo'] = logo_element.get_attribute(
            "src") if logo_element else "N/A"

        # Extract company name and company page URL
        company_name_element = job_card.find_element(
            By.XPATH, ".//h3[contains(@class, 'company-name')]//a")
        company_info['company_short_name'] = company_name_element.text if company_name_element else "N/A"
        company_info['company_url'] = company_name_element.get_attribute(
            "href") if company_name_element else "N/A"

        # Extract company tags (e.g., "环保", "B轮", "500-999人")
        tags_elements = job_card.find_elements(
            By.XPATH, ".//ul[contains(@class, 'company-tag-list')]//li")

        # Initialize company category, business category, and employee count as "N/A"
        company_info['company_category'] = "N/A"
        company_info['business_category'] = "N/A"
        company_info['employee_count'] = "N/A"

        if tags_elements:
            if len(tags_elements) >= 3:
                company_info['company_category'] = tags_elements[0].text if tags_elements[0].text else "N/A"
                company_info['business_category'] = tags_elements[1].text if tags_elements[1].text else "N/A"
                company_info['employee_count'] = tags_elements[2].text if tags_elements[2].text else "N/A"
            elif len(tags_elements) == 2:
                company_info['company_category'] = tags_elements[0].text if tags_elements[0].text else "N/A"
                company_info['employee_count'] = tags_elements[1].text if tags_elements[1].text else "N/A"
            elif len(tags_elements) == 1:
                company_info['company_category'] = tags_elements[0].text if tags_elements[0].text else "N/A"

        print(f"Company info extracted: {company_info}")
        return company_info

    except Exception as e:
        print(f"Error in right side company information extract: {str(e)}")
        return {}


def extract_single_job_info(driver, job_card, index, filter_query):
    """ extract_single_job_info() function for click and wait for loading a single job in new tab then extract information about the job details HR details then call and wait for company details information page """
    # Set up CSV file path
    try:
        # Verify that the session is valid before proceeding
        if not driver.session_id:
            raise InvalidSessionIdException(
                "Session has been closed or is invalid.")
        # Extract job data
        print("Inside try block of single job card ...", job_card)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        csv_file_path = os.path.join(project_root, 'data', "job_details.csv")
        print("Before job company element...")

        # Set up data directories
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        DATA_DIR = os.path.join(project_root, 'data')
        IMAGE_DIR = os.path.join(DATA_DIR, 'images', 'hr_images')
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(IMAGE_DIR, exist_ok=True)
        try:
            job_title_element = WebDriverWait(job_card, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, ".//div[contains(@class, 'job-title')]"))
            )

            if job_title_element:

                # Scroll job card into view
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                    job_title_element
                )
                random_delay(1, 5)

                # Click on job title element
                get_right_side_info = extract_company_info_from_job_card(
                    driver, job_card)
                print("get_right_side_info company short name",
                      get_right_side_info['company_short_name'])
                global prep_job_dic
                prep_job_dic = {
                    'company_short_name': get_right_side_info['company_short_name'] if get_right_side_info['company_short_name'] else "N/A",
                }
                driver.execute_script(
                    "arguments[0].click();", job_title_element)
            else:
                print("target company name not found!")
        except Exception as e:
            print(
                f"Company name element not found in job card {index} within the given time.", e)
            return False  # Handle the case if the element isn't found

        # Wait for new tab and switch to it
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

        driver.switch_to.window(driver.window_handles[-1])

        random_delay(2, 5)

        # Add URL verification
        current_url = driver.current_url

        print(f"Navigated to: {current_url}")

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

        for key, xpath in elements_to_extract.items():
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, xpath))
                )

                prep_job_dic[key] = element.text.strip()
                if not prep_job_dic[key]:
                    prep_job_dic[key] = "N/A"

            except Exception as e:
                print(f"elements_to_extract {key} not found: {str(e)}")

        # Extract HR information
        prep_job_dic['hr_name'] = driver.execute_script("""
            var element = document.querySelector('h2.name');
            return element.childNodes[0].nodeValue.trim();
        """)

        prep_job_dic['hr_designation'] = driver.execute_script("""
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
                prep_job_dic['hr_pic_path'] = hr_pic_path
            else:
                prep_job_dic['hr_pic_path'] = "N/A"
        except Exception as e:
            print(f"Failed to save HR image: {str(e)}")
            prep_job_dic['hr_pic_path'] = "N/A"

        prep_job_dic['skill_category'] = filter_query['skill']
        prep_job_dic['position_type'] = POSITION_TYPES_MAPPING[POSITION_TYPES.index(
            filter_query['position'])]
        prep_job_dic['experience_level'] = EXPERIENCE_LEVELS_MAPPING[EXPERIENCE_LEVELS.index(
            filter_query['experience'])]

        print("final version of single job ==========*******=========> ", prep_job_dic)

        save_job_to_csv(prep_job_dic, csv_file_path)

        print(f"Successfully saved job {index + 1}")

        extract_company_details_info(
            driver, company_right_side_info=get_right_side_info, index=index)
        # return prep_job_dic

    except Exception as e:
        print(f"Error in single job processing: {str(e)}")

    finally:
        # Close the job detail tab and switch back to main window
        driver.close()
        driver.switch_to.window(driver.window_handles[0])


# Main function to process the first job card

def process_first_job(driver):
    """Process jobs across 84 IT_SKILLS, 2 type_of_position, and 8 type_of_experience with dynamic pages"""

    for skill in IT_SKILLS:
        for position in POSITION_TYPES:
            for experience in EXPERIENCE_LEVELS:
                filter_query = {
                    'skill': skill,
                    'position': position,
                    'experience': experience
                }

                try:
                    # Execute query with current filters
                    job_query = f"{BASE_URL}{JOB_QUERY}&position={filter_query['skill']}&jobType={filter_query['position']}&experience={filter_query['experience']}"

                    results = do_query_by_skills(driver, job_query)
                    if not results["job_cards"]:
                        print(
                            f"No results for skill => {skill} position => {position} experience => {experience}, skipping...")
                        continue

                    job_cards = results["job_cards"]
                    total_page = results["total_page"]

                    print(
                        f"Found {len(job_cards)} job cards on {total_page} pages for experience {experience}")

                    max_pages = total_page  # Total pages available for this experience level
                    # Number of jobs per page
                    max_jobs_per_page = len(job_cards)

                    current_page = 1  # tracking page number and reset for initial request

                    while current_page <= max_pages:
                        # Process each job card on the current page
                        for index in range(len(job_cards)):
                            print(
                                f"Processing job {index + 1} on current page {current_page}")

                            try:
                                # Process the job information
                                extract_single_job_info(driver, job_cards[index], index=(
                                    (current_page - 1) * max_jobs_per_page) + index, filter_query=filter_query)

                            except Exception as e:
                                print(
                                    f"Error single job processing index: {index + 1}: {str(e)}")
                                break

                        current_page += 1

                        print(f"Moving to current page => {current_page}")

                        new_page_job_query = f"{BASE_URL}{JOB_QUERY}&position={filter_query['skill']}&jobType={filter_query['position']}&experience={filter_query['experience']}&page={current_page}"

                        results = do_query_by_skills(
                            driver, new_page_job_query)

                        if not results.get("job_cards"):
                            print(f"No more jobs on page {current_page}")
                            break

                        job_cards = results["job_cards"]
                        print("New query with current page done...")

                        random_delay(2, 6)  # Add delay between page loading

                    print(
                        f"Successfully processed {max_pages} pages for experience level {experience}.")

                    print('Starting new query for another experience level...')

                except Exception as e:
                    print(
                        f"Error in first job processing skill {skill} position {position} experience {experience}: {str(e)}")
                    # continue
                    break
