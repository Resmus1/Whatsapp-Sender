import os
import time
import logging
import requests
import random
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import signal
import sys

# Sitting Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# Processing signal end program
def handle_exit(signal, frame):
    logging.info("Program terminated by user.")
    delete_image()
    sys.exit(0)


signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

def load_image_links(file_path):
    """
    Load txt with links on images.
    """
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]


def delete_image():
    """
    Delete file processed_image if it download.
    """
    if os.path.exists("processed_image.jpg"):
        os.remove("processed_image.jpg")


def load_phone_numbers(file_path):
    """
    Load download txt with numbers.
    """
    try:
        with open(file_path, 'r') as file:
            phone_numbers = [line.strip() for line in file.readlines()]
            logging.info(f"Load {len(phone_numbers)} numbers.")
            return phone_numbers
    except FileNotFoundError:
        logging.error(f"File with numbers not found: {file_path}")
        return []
    except Exception as a:
        logging.error(f"Error load numbers: {a}")
        return []


def clear_search_box(data_browser, position_search_box):
    """
    Clear search field.
    """
    try:
        actions = ActionChains(data_browser)
        actions.click(position_search_box).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(
            Keys.BACKSPACE).perform()
    except Exception as a:
        logging.exception(f"Error clear search field: {a}")


def preview_image(save_path="processed_image.jpg"):
    """
    Download image in file and open file.
    """
    # url image
    image_url = random.choice(good_morning_list)
    try:
        # download image
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Status HTTP

        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        img = Image.open(save_path)
        img.show()

        return os.path.abspath(save_path)

    except requests.exceptions.RequestException as a:
        logging.error(f"Error load image: {a}")
        return None
    except Exception as a:
        logging.error(f"Error processing image: {a}")
        return None


def convert_image(save_path="processed_image.jpg"):
    """
    Converts the image to JPG format if needed.".
    """
    try:
        # If the image is already saved in save_path, we will check its format.
        img = Image.open(save_path)

        # Convert to RGB format if necessary.
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Overwrite the file in the same location.
        img.save(save_path, "JPEG")
        logging.info("Preparation completed, starting the sending process.")

        return os.path.abspath(save_path)

    except Exception as a:
        logging.error(f"Image processing error: {a}")
        return None


def wait_for_element(driver, by, locator, timeout=30):
    """
    Ожидание появления элемента на странице.
    """
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))
    except Exception:
        logging.exception(f"Ошибка ожидания элемента: {locator}")
        return None


def send_image(data_browser, position_search_box, phone_number, image):
    """
    Sending an image to the specified phone number via WhatsApp Web.
    """
    try:
        # Step 1: Clear find contact field
        clear_search_box(data_browser, position_search_box)

        # Step 2: Search contact
        actions = ActionChains(data_browser)
        actions.click(position_search_box).send_keys(phone_number).send_keys(Keys.ENTER).perform()

        # Step 3: Wait download chat
        wait_for_element(data_browser, 'xpath', '//*[@id="main"]/footer')

        # Step 4: Click attach button
        attach_button = wait_for_element(data_browser, 'xpath', "//button[contains(@title, 'Прикрепить')]")
        if attach_button:
            attach_button.click()

        # Step 5: Choice file
        file_input = wait_for_element(data_browser, 'xpath', "(//input[@type='file'])[2]")
        if file_input:
            file_input.send_keys(image)

        wait_for_element(data_browser, 'xpath', "//div[@aria-label='Отправить']")

        # Step 6: Send message
        actions.send_keys(Keys.ENTER).perform()
        logging.info(f"Message send: {phone_number}")

    except Exception:
        logging.exception(f"Error sending image to the contact {phone_number}")


if __name__ == "__main__":
    try:
        good_morning_list = load_image_links('good_morning_list.txt')
        phone_numbers = load_phone_numbers('phone_numbers.txt')

        if not phone_numbers:
            raise ValueError("The list of numbers is empty or could not be loaded.")

        temp_image = preview_image()
        if not temp_image:
            raise ValueError("Failed to load the image.")

        while input("Send:\n1.Send message\n2.Next image\n==>> ") != '1':
            temp_image = preview_image()
            if not temp_image:
                raise ValueError("Failed to load the image.")

        local_image_path = convert_image(temp_image)
        if not local_image_path:
            raise ValueError("Failed to convert the image.")

        chrome_options = webdriver.ChromeOptions()
        profile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile", "User Data")
        profile_name = "Default"
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument(f"--profile-directory={profile_name}")

        with webdriver.Chrome(options=chrome_options) as browser:
            browser.get('https://web.whatsapp.com/')
            search_box = wait_for_element(browser, 'xpath', "//div[@aria-owns='emoji-suggestion']")
            if not search_box:
                raise ValueError("Field search not found")

            for number in phone_numbers:
                send_image(browser, search_box, number, local_image_path)

            delete_image()

            # Wait download all message
            time.sleep(5)
            logging.info("Program successful end")

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error request: {e}")
    except Exception as e:
        logging.exception(f"Fatal error: {e}")
