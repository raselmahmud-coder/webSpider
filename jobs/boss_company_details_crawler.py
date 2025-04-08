from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import csv
import os
from datetime import datetime

from config import BASE_URL


def extract_company_details(driver):
    """Extract detailed company information from the business details section."""
    company_details = {}
    try:
        # Wait for the business details list to be present
        business_details = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "business-detail"))
        )

        # Dictionary mapping Chinese labels to English keys
        label_mapping = {
            "企业名称": "company_name",
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
            "所属行业": "industry",
            "经营范围": "business_scope"
        }

        # Find all list items
        list_items = business_details.find_elements(By.TAG_NAME, "li")
        print("expected all list items ====> ", list_items)

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


def extract_company_addresses(driver):
    """Extract all company addresses from the job location section."""
    addresses = []
    try:
        # Wait for the job-location container to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-location"))
        )

        # Find all location items
        location_items = driver.find_elements(By.CLASS_NAME, "location-item")

        for item in location_items:
            try:
                # Extract address text
                address = item.find_element(
                    By.CLASS_NAME, "location-address").text

                # Extract latitude and longitude from data-lat attribute
                map_container = item.find_element(
                    By.CLASS_NAME, "map-container")
                coordinates = map_container.get_attribute("data-lat")

                # Create address dictionary
                address_info = {
                    "address": address,
                    "coordinates": coordinates,
                    "address_id": map_container.get_attribute("data-addressid")
                }

                addresses.append(address_info)

            except Exception as e:
                print(f"Error extracting individual address: {str(e)}")
                continue

        return addresses

    except Exception as e:
        print(f"Error extracting company addresses: {str(e)}")
        return addresses


def save_company_to_csv(company_data, company_details, company_addresses, csv_file_path='company_data.csv'):
    """Save company information to CSV file"""

    # Flatten company addresses into a single string
    formatted_addresses = '; '.join([
        f"Address: {addr['address']}, Coordinates: {addr['coordinates']}, ID: {addr['address_id']}"
        for addr in company_addresses
    ])

    # Combine all data into a single dictionary
    csv_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'company_name': company_data.get('company_name', ''),
        'company_description': company_data.get('company_description', ''),
        # Company details
        'legal_representative': company_details.get('legal_representative', ''),
        'establishment_date': company_details.get('establishment_date', ''),
        'company_type': company_details.get('company_type', ''),
        'operation_status': company_details.get('operation_status', ''),
        'registered_capital': company_details.get('registered_capital', ''),
        'registered_address': company_details.get('registered_address', ''),
        'business_term': company_details.get('business_term', ''),
        'region': company_details.get('region', ''),
        'social_credit_code': company_details.get('social_credit_code', ''),
        'approval_date': company_details.get('approval_date', ''),
        'former_names': company_details.get('former_names', ''),
        'registration_authority': company_details.get('registration_authority', ''),
        'industry': company_details.get('industry', ''),
        'business_scope': company_details.get('business_scope', ''),
        'company_addresses': formatted_addresses
    }
    # Set up CSV file path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    csv_file_path = os.path.join(project_root, 'data', "company_data.csv")
    file_exists = os.path.exists(csv_file_path)

    with open(csv_file_path, mode='a' if file_exists else 'w',
              newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=csv_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(csv_data)


def extract_company_info(driver, index):
    """Extract company information from the company details page."""
    try:
        # Wait for the element to be present and clickable
        a_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 "//a[@ka='job-cominfo' and contains(@class, 'look-all')]")
            )
        )

        # Extract the href attribute
        company_url = a_element.get_attribute("href")
        # company_url = company_uri
        print("Extracted company URL:", company_url)

        # Open the company details page in a new tab
        driver.execute_script("window.open(arguments[0]);", company_url)
    except Exception as e:
        print(f"Error extracting a element in company URL: {str(e)}")
        print("Skipping company information extraction for this job...")
        # Return early to skip the rest of the company info extraction
        return {
            'company_name': 'N/A',
            'company_description': 'N/A',
            'company_details': {},
            'company_addresses': []
        }

    try:
        # Switch to the new tab
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[-1])
        print("It's switch in the new tab")

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'company-info')]"))
        )
        print("Waiting for page loading...")
    except Exception as e:
        print(f"Error in switch in the new tab: {str(e)}")
        time.sleep(2)

    try:
        # Wait for the page unfold/expand to find the "more info" label about business information section
        more_info_label = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'business-detail')]//label[@ka='company_full_info']"))
        )
        print("For unfold section waiting for page loading...")

        # Click the label to expand the unfold section
        more_info_label.click()
        time.sleep(2)

        # Wait for the business info fold section to be visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'company-info-box')]"))
        )
        print("Waiting finished soon enter into try block...")

    except Exception as e:
        print(f"Error in unfold section: {str(e)}")

    # Extract company information (adjust the XPath as needed)
    try:
        company_name = driver.find_element(
            By.XPATH, "//h1[contains(@class, 'name')]").text
        description_element = driver.find_elements(
            By.XPATH, "//div[contains(@class, 'text fold-text')]")

        # Extract text if element was found
        if description_element:
            company_description = description_element[0].text
        else:
            company_description = "No description available"

        # Print the extracted company information
        print(f"Company Name: {company_name}")
        print(f"Company Description: {company_description}")

    except Exception as e:
        print(f"Error extracting company description: {str(e)}")

    try:
        # Collect company basic info
        company_data = {
            'company_name': company_name,
            'company_description': company_description
        }
        # Extract detailed company information
        company_details = extract_company_details(driver)

        # Print the extracted company details
        print("\nDetailed Company Information:")
        for key, value in company_details.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error extracting company_details: {str(e)}")

    try:
        # Extract company addresses
        company_addresses = extract_company_addresses(driver)

        # Print the extracted addresses
        print("\nCompany Addresses:")
        for idx, addr in enumerate(company_addresses, 1):
            print(f"Address {idx}:")
            print(f"  Location: {addr['address']}")
            print(f"  Coordinates: {addr['coordinates']}")
            print(f"  Address ID: {addr['address_id']}")
    except Exception as e:
        print(f"Error extracting company's address: {str(e)}")

    try:
        # Save all collected data to CSV
        save_company_to_csv(
            company_data, company_details, company_addresses)

        print("Company data has been saved to CSV successfully!")

    except Exception as e:
        print(f"Error in save company to csv: {str(e)}")

    finally:
        # Close the company details tab and switch back to the main window
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
