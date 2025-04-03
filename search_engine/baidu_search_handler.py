import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re

from utils import wait_for_page_load


def get_search_result(driver, query):
    """Function to handle baidu search results"""
    try:
        # Remove all non-alphanumeric chars except spaces
        formatted_query = re.sub(r'[^a-zA-Z0-9\s]', '', query)
        # Normalize whitespace
        formatted_query = ' '.join(formatted_query.split())
        formatted_query = formatted_query.lower()                # Convert to lowercase
        formatted_query = formatted_query.replace(
            ' ', '+')      # Replace spaces with plus

        print("Formatted query ===>>", formatted_query)

        driver.get(
            f"https://chat.baidu.com/search?word={formatted_query}&pd=csaitab&setype=csaitab&extParamsJson=%7B%22enter_type%22%3A%22a_ai_banner%22%2C%22sa%22%3A%22re_dl_ai_banner%22%2C%22apagelid%22%3A%2212577166845641557933%22%2C%22ori_lid%22%3A%2212577166845641557933%22%7D")
        # Wait for page loading
        wait_for_page_load(driver)

    except Exception as e:
        print(f"Error in search process: {str(e)}")

    try:
        # Wait for the AI response wrapper to be present and visible
        wrapper = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".answer-ask-wrapper_6o1ue_1"))
        )

        # Then wait for non-empty content inside the wrapper
        WebDriverWait(driver, 120).until(
            lambda d: len(wrapper.text.strip()) > 0 and
            not wrapper.text.strip().lower().startswith("正在生成") and  # "Generating" in Chinese
            not wrapper.text.strip().lower().startswith("generating")
        )

        # Add a small delay to ensure complete content generation
        time.sleep(2)

    except Exception as e:
        print("ai_response_wrapper error", e)

    try:
        # Wait for the ancestor element with class "cs-rank-container" to be present
        result_containers = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".cs-rank-container"))
        )
        # for index, container in enumerate(result_containers):
        print(f"Container: {len(result_containers)}")

    except Exception as e:
        print("element catching error", e)
        if len(result_containers) == 0:
            print("Debug info:")
            print(f"Current URL: {driver.current_url}")
            print("Page source preview:", driver.page_source[:500])
            return False

    try:
        # Wait for the element with both classes "cosd-markdown" and "cos-space-mt-lg" to be present
        final_wrapper = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.cosd-markdown.cos-space-mt-lg"))
        )
        # Combine all text chunks with proper spacing
        combined_text = '\n\n'.join(
            [element.text.strip() for element in final_wrapper if element.text.strip()])

        print("Final wrapper chunks:", len(final_wrapper))
        print("Combined text length:", len(combined_text))

        return combined_text if combined_text else "No content found"

    except Exception as e:
        print("final wrapper error", e)
        print("Current URL:", driver.current_url)
        print("Page source preview:", driver.page_source[:1000])
