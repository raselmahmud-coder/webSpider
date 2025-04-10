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


def extract_company_primary_info(driver, company_short_name):
    """Extract primary company info from the info-primary div"""
    primary_info = {
        'company_logo': '',
        'company_short_name': '',
        'employee_count': '',
        'company_category': '',
        'business_category': ''
    }

    try:
        # Wait for the primary info section to load
        primary_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "info-primary"))
        )

        # Extract logo URL
        logo_img = primary_div.find_element(By.TAG_NAME, "img")
        primary_info['company_logo'] = logo_img.get_attribute("src")
        primary_info['company_short_name'] = company_short_name

        print('So far what is primary comp info', primary_info)

        # Use JavaScript to extract the primary info (company category, employee count, business category)
        primary_info["company_category"], primary_info["employee_count"], primary_info["business_category"] = driver.execute_script("""
            var element = document.querySelector('.info p');
            var textContent = element ? element.textContent.split('·') : [];
            
            return [
                textContent.length > 0 ? textContent[0].trim() : '',  // company_category
                textContent.length > 1 ? textContent[1].trim() : '',  // employee_count
                element.querySelector('a') ? element.querySelector('a').textContent.trim() : ''  // business_category
            ];
        """)

    except Exception as e:
        print(f"Error extracting primary company info: {str(e)}")

    return primary_info


def extract_company_description(driver):
    """Extract company description from the fold-text or job-sec-text element"""
    try:
        # Wait for the parent container to be visible
        parent_div = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@class, 'company-info-box')]")
            )
        )

        # Try to find the description element with either 'fold-text' or 'job-sec-text' class
        description_element = None
        try:
            description_element = parent_div.find_element(
                By.CLASS_NAME, 'fold-text')
        except:
            pass  # If 'fold-text' not found, try 'job-sec-text'

        if not description_element:
            try:
                description_element = parent_div.find_element(
                    By.CLASS_NAME, 'job-sec-text')
            except Exception as e:
                print(f"Error finding description element: {str(e)}")
                return ""

        # Extract and clean up the description text
        company_description = description_element.text.strip() if description_element else ""

        print("Company description info box loaded", company_description)
        return ' '.join(company_description.split())

    except Exception as e:
        print(f"Error extracting company description: {str(e)}")
        return ""


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


def extract_company_brands(driver):
    """Extract company brand labels from the brand-list div if available"""
    brands = []
    try:
        # Wait for the brand-list element to be present
        brand_list = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "brand-list"))
        )

        # Find all brand labels within the div
        brand_labels = brand_list.find_elements(By.CLASS_NAME, "brand-label")

        # Extract text from each brand label
        brands = [label.text for label in brand_labels]

    except Exception as e:
        # If element not found, return empty list (not all companies have brands)
        print(f"Brand labels not found or error extracting: {str(e)}")

    return brands


def extract_company_addresses(driver):
    """Extract company address from the job location section."""
    addresses = []
    try:
        # Wait for the job-location container to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-location"))
        )

        # Find the location address within the job-location container
        location_container = driver.find_element(By.CLASS_NAME, "job-location")

        # Try to extract the address text
        try:
            address = location_container.find_element(
                By.CLASS_NAME, "location-address").text
        except Exception as e:
            print(f"Error extracting address: {str(e)}")
            address = ""

        # Initialize variables to empty strings for safety
        coordinates = ""
        address_id = ""

        # Try to extract latitude and longitude (coordinates) and address_id if available
        try:
            map_container = location_container.find_element(
                By.CLASS_NAME, "map-container")
            coordinates = map_container.get_attribute("data-lat") or ""
            address_id = map_container.get_attribute("data-addressid") or ""
        except Exception as e:
            print(f"Error extracting coordinates or address_id: {str(e)}")

        # Create address dictionary
        address_info = {
            "address": address if address else '',
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


def extract_company_details_info(driver, company_short_name, index):
    """Extract company information from the company details page."""
    new_tab_opened = False  # Track tab state
    try:
        company_data = {}
        company_details = {}  # Ensure initialization
        company_addresses = []
        primary_info = {}  # Initialize primary_info

        # Basic info extraction (always available)
        company_data['company_description'] = extract_company_description(
            driver)
        company_addresses = extract_company_addresses(driver)
        print("\nCompany Addresses:", company_addresses)

        # Attempt to find company details link
        try:
            a_element = WebDriverWait(driver, 3).until(  # Reduced timeout
                EC.presence_of_element_located(
                    (By.XPATH,
                     "//a[@ka='job-cominfo' and contains(@class, 'look-all')]")
                )
            )
            company_url = a_element.get_attribute("href")
            print("Company details URL found:", company_url)
        except TimeoutException:
            print("Company details link not found - skipping extended details")
            company_url = None

        # Process company details page only if URL exists
        if company_url:
            # Open and switch to new tab
            driver.execute_script("window.open(arguments[0]);", company_url)
            WebDriverWait(driver, 10).until(
                lambda d: len(d.window_handles) > 1)
            driver.switch_to.window(driver.window_handles[-1])
            new_tab_opened = True
            print("Switched to company details tab")

            # Extract data from details page
            primary_info = extract_company_primary_info(
                driver, company_short_name)
            company_data.update(primary_info)

            # Extract brands
            company_brands = extract_company_brands(driver)
            company_data['company_brands'] = '; '.join(
                company_brands) if company_brands else 'N/A'

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

        # If no company_url, try extracting basic business details from current page
        if not company_url:
            print("Attempting business details extraction from current page")
            company_details = extract_company_business_details(driver)

        # Merge all data
        company_data.update(company_details)
        print(f"Index {index}: Data collection complete")

        # Save results
        save_company_to_csv(company_data, company_details, company_addresses)

    except Exception as e:
        print(f"Critical error in extraction: {str(e)}")
    finally:
        # Clean up tabs
        if new_tab_opened:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            print("Returned to main window")
