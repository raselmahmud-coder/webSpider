from selenium.common.exceptions import TimeoutException  # Add this import at the top
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import csv
import os
from datetime import datetime

from config import BASE_URL
from utils import random_delay


def extract_company_description(driver):
    """Extract company description from the fold-text or job-sec-text element"""
    try:
        # Wait for the parent container to be visible
        parent_div = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@class, 'company-info-box')]")
            )
        )

        # Try to find the description element with either 'job-sec-text' or 'fold-text' class
        try:
            description_element = parent_div.find_element(
                By.XPATH, ".//div[contains(@class, 'job-sec-text') and contains(@class, 'fold-text')]")
            company_description = description_element.text.strip()
            cleaned_description = ' '.join(
                company_description.split()) if company_description else "N/A"
            print("Company description info box loaded:", cleaned_description)
            return cleaned_description

        except Exception as e:
            # If the description element is not found, return an empty string or "N/A"
            print(f"Error finding description element: {str(e)}")
            return "N/A"  # Return "N/A" or "" if description is not found

    except Exception as e:
        print(f"Error extracting company description: {str(e)}")
        return "N/A"  # Return "N/A" if there is an issue with the parent div


def extract_company_business_details(driver):
    """Extract detailed company information from the business details section."""
    company_details = {}
    try:
        # Wait for the business details list to be present
        business_details = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "business-detail"))
        )

        # Dictionary mapping Chinese labels to English keys
        label_mapping = {
            "企业名称": "company_full_name",
            "法定代表人": "legal_representative",
            "成立时间": "establishment_date",
            "企业类型": "company_type",
            "经营状态": "operation_status",
            "注册资本": "registered_capital",
            "注册地址": "registered_address",
            "营业期限": "business_term",
            "所属地区": "region",
            "统一社会信用代码": "social_credit_code",
            "核准日期": "approval_date",
            "曾用名": "former_names",
            "登记机关": "registration_authority",
            "经营范围": "business_scope"
        }

        # Find all list items
        list_items = business_details.find_elements(By.TAG_NAME, "li")
        print("expected all list company's information ====> ", len(list_items))

        for item in list_items:
            try:
                # Extract the label (text before colon)
                label_element = item.find_element(By.CLASS_NAME, "t")
                label = label_element.text.strip("：")

                # Extract the value (text after the span)
                value = item.text.replace(label_element.text, "").strip()

                # Map Chinese label to English key
                if label in label_mapping:
                    key = label_mapping[label]
                    company_details[key] = value if value != "-" else None

            except Exception as e:
                print(f"Error extracting detail from list item: {str(e)}")
                continue

        return company_details

    except Exception as e:
        print(f"Error extracting company details: {str(e)}")
        return company_details


def extract_company_brand_talent_info(driver):
    """Extract company information, including talent development and brand list."""
    company_info = {
        'talent_development': [],
        'brand_list': []
    }

    try:
        # Extract talent development list
        try:
            talent_section = driver.find_element(
                By.XPATH, "//div[contains(@class, 'company-talents')]//ul[contains(@class, 'company-talents-list')]")
            talent_development = [
                li.text for li in talent_section.find_elements(By.TAG_NAME, "li")]
            company_info['talent_development'] = talent_development if talent_development else [
            ]
        except Exception as e:
            print(
                f"Talent development list not found or error extracting: {str(e)}")
            company_info['talent_development'] = []

        # Extract brand list
        try:
            brand_section = driver.find_element(
                By.XPATH, "//div[contains(@class, 'brand-list')]")
            brand_labels = [label.text for label in brand_section.find_elements(
                By.CLASS_NAME, "brand-label")]
            company_info['brand_list'] = brand_labels if brand_labels else []
        except Exception as e:
            print(f"Brand labels not found or error extracting: {str(e)}")
            company_info['brand_list'] = []

        print(f"Company info extracted: {company_info}")
        return company_info

    except Exception as e:
        print(f"Error extracting company info: {str(e)}")
        return company_info


def extract_company_addresses(driver):
    """Extract company address from the job location section."""
    addresses = []
    try:
        # Wait for the job-location container to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-location"))
        )

        print("waiting for address items")

        # Find all location items using XPath
        location_items = driver.find_elements(
            By.XPATH, "//div[contains(@class, 'job-location')]//div[contains(@class, 'location-address')]")

        if location_items:
            for item in location_items:
                # Extract address text using XPath
                address = item.text.strip() if item.text else "n/a"

                # Extract latitude and longitude from data-lat attribute using XPath
                map_container = item.find_element(
                    By.XPATH, ".//following-sibling::div[contains(@class, 'job-location-map')]")
                coordinates = map_container.get_attribute(
                    "data-lat") if map_container.get_attribute("data-lat") else "n/a"

                # Extract address ID using XPath
                address_id = map_container.get_attribute(
                    "data-addressid") if map_container.get_attribute("data-addressid") else "n/a"

                # Create address dictionary
                address_info = {
                    "address": address,
                    "coordinates": coordinates,
                    "address_id": address_id
                }

                addresses.append(address_info)

        return addresses

    except Exception as e:
        print(f"Error extracting company addresses: {str(e)}")
        return addresses


def save_company_to_csv(company_data, company_details, company_addresses, csv_file_path='company_data.csv'):
    """Save company information to CSV file if any of the extracted data exists."""
    try:
        # Flatten company addresses into a single string if they exist
        formatted_addresses = '; '.join([
            f"Address: {addr['address']}, Coordinates: {addr['coordinates']}, ID: {addr['address_id']}"
            for addr in company_addresses
        ]) if company_addresses else 'N/A'

        # Combine all data into a single dictionary with fallback defaults
        csv_data = {
            'company_logo': company_data.get('company_logo', 'N/A'),
            'company_short_name': company_data.get('company_short_name', 'N/A'),
            'employee_count': company_data.get('employee_count', 'N/A'),
            'company_category': company_data.get('company_category', 'N/A'),
            'business_category': company_data.get('business_category', 'N/A'),
            'company_full_name': company_data.get('company_full_name', 'N/A'),
            'company_brands': company_data.get('company_brands', 'N/A'),
            'talents_dev': company_data.get('talents_dev', 'N/A'),
            'company_description': company_data.get('company_description', 'N/A'),
            # Company details
            'legal_representative': company_details.get('legal_representative', 'N/A') if company_details else 'N/A',
            'establishment_date': company_details.get('establishment_date', 'N/A') if company_details else 'N/A',
            'company_type': company_details.get('company_type', 'N/A') if company_details else 'N/A',
            'operation_status': company_details.get('operation_status', 'N/A') if company_details else 'N/A',
            'registered_capital': company_details.get('registered_capital', 'N/A') if company_details else 'N/A',
            'registered_address': company_details.get('registered_address', 'N/A') if company_details else 'N/A',
            'business_term': company_details.get('business_term', 'N/A') if company_details else 'N/A',
            'region': company_details.get('region', 'N/A') if company_details else 'N/A',
            'social_credit_code': company_details.get('social_credit_code', 'N/A') if company_details else 'N/A',
            'approval_date': company_details.get('approval_date', 'N/A') if company_details else 'N/A',
            'former_names': company_details.get('former_names', 'N/A') if company_details else 'N/A',
            'registration_authority': company_details.get('registration_authority', 'N/A') if company_details else 'N/A',
            'business_scope': company_details.get('business_scope', 'N/A') if company_details else 'N/A',
            'company_addresses': formatted_addresses
        }

        # Set up CSV file path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        csv_file_path = os.path.join(project_root, 'data', "company_data.csv")
        file_exists = os.path.exists(csv_file_path)

        # Write data to CSV
        with open(csv_file_path, mode='a' if file_exists else 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=csv_data.keys())
            if not file_exists:
                writer.writeheader()  # Write header if the file does not exist
            writer.writerow(csv_data)

        print("Company data saved to CSV successfully!")

    except Exception as e:
        print(f"Error saving company details to CSV: {str(e)}")


def extract_company_details_info(driver, company_right_side_info, index):
    """Extract company information from the company details page."""

    try:
        print("get right side info ", company_right_side_info)
        company_data = {}
        company_details = {}  # Ensure initialization
        company_addresses = []
        primary_info = company_right_side_info  # Initialize primary_info

        # Basic info extraction (always available)
        company_data['company_description'] = extract_company_description(
            driver)
        company_addresses = extract_company_addresses(driver)
        print("\nCompany Addresses:", company_addresses)

        # Attempt to find company details link
        try:
            a_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     "//a[@ka='job-cominfo' and contains(@class, 'look-all')]")
                )
            )
            company_url = a_element.get_attribute("href")
            print("Company details URL found:", company_url)
        except TimeoutException:
            print("Company details link not found - ignoring to extended details")
            company_url = None

        # Process company details page only if URL exists
        if company_url:
            # Open and switch to new tab
            driver.execute_script("window.open(arguments[0]);", company_url)
            WebDriverWait(driver, 10).until(
                lambda d: len(d.window_handles) > 1)
            driver.switch_to.window(driver.window_handles[-1])
            print("Switched to company details tab")

            company_data.update(primary_info)

            # Extract brands
            company_brands_n_talents = extract_company_brand_talent_info(
                driver)
            company_data['company_brands'] = company_brands_n_talents['brand_list']
            company_data['talents_dev'] = company_brands_n_talents['talent_development']

            print("ki ree pai na keno??",
                  company_brands_n_talents['talent_development'])

            # Try to expand business details
            try:
                more_info_label = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//label[@ka='company_full_info']")
                    )
                )
                more_info_label.click()
                print("Expanded business details section")
                random_delay(2, 3)
            except TimeoutException:
                print("Business details expansion not available")

            # Get business details
            company_details = extract_company_business_details(driver)

        # Merge all data
        company_data.update(company_details)

        print(f"Index {index}: Data collection complete")

        # Save results
        save_company_to_csv(company_data, company_details, company_addresses)

    except Exception as e:
        print(f"Critical error in extraction: {str(e)}")

    finally:
        # Close the company details tab and switch back to the main window
        window_handles = driver.window_handles
        if len(window_handles) > 2:  # Check if there are at least 3 tabs open
            driver.close()  # Close the 3rd tab
            # Switch back to the 2nd tab (previous tab)
            driver.switch_to.window(window_handles[-2])
            print("Returned to the previous (2nd) tab")
        else:
            print("Only 2 tabs open, no need to close the 3rd tab")
        print("Returned to main window")
