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

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# Обработка сигналов завершения программы
def handle_exit(signal, frame):
    logging.info("Программа завершена пользователем.")
    delete_image()
    sys.exit(0)


signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

def load_image_links(file_path):
    """
    Читает ссылки на изображения из текстового файла и возвращает их в виде списка.
    """
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]


def delete_image():
    """
    Удаление файла изображения если оно загружено.
    """
    if os.path.exists("processed_image.jpg"):
        os.remove("processed_image.jpg")


def load_phone_numbers(file_path):
    """
    Читает номера телефонов из текстового файла и возвращает их в виде списка.
    """
    try:
        with open(file_path, 'r') as file:
            phone_numbers = [line.strip() for line in file.readlines()]
            logging.info(f"Загружено {len(phone_numbers)} номеров.")
            return phone_numbers
    except FileNotFoundError:
        logging.error(f"Файл с номерами не найден: {file_path}")
        return []
    except Exception as a:
        logging.error(f"Ошибка при загрузке номеров: {a}")
        return []


def clear_search_box(data_browser, position_search_box):
    """
    Очистка поля поиска перед отправкой следующего сообщения
    """
    try:
        actions = ActionChains(data_browser)
        actions.click(position_search_box).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(
            Keys.BACKSPACE).perform()
    except Exception as a:
        logging.exception(f"Ошибка очистки поля поиска: {a}")


def preview_image(save_path="processed_image.jpg"):
    """
    Скачивание и сохранение изображения в файл.
    """
    # url изображения
    image_url = random.choice(good_morning_list)
    try:
        # Скачивание изображения
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Проверка на ошибки HTTP

        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        img = Image.open(save_path)
        img.show()

        return os.path.abspath(save_path)

    except requests.exceptions.RequestException as a:
        logging.error(f"Ошибка загрузки изображения: {a}")
        return None
    except Exception as a:
        logging.error(f"Ошибка обработки изображения: {a}")
        return None


def convert_image(save_path="processed_image.jpg"):
    """
    Преобразует изображение в формат JPG, если это нужно.
    """
    try:
        # Если изображение уже сохранено в save_path, проверим его формат
        img = Image.open(save_path)

        # Преобразование в формат RGB, если это необходимо
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Перезаписываем файл в том же месте
        img.save(save_path, "JPEG")
        logging.info("Подготовка завершена, начало отправки.")

        return os.path.abspath(save_path)

    except Exception as a:
        logging.error(f"Ошибка обработки изображения: {a}")
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
    Отправка изображения по указанному номеру телефона через WhatsApp Web.
    """
    try:
        # Шаг 1: Очистка поля поиска
        clear_search_box(data_browser, position_search_box)

        # Шаг 2: Поиск контакта
        actions = ActionChains(data_browser)
        actions.click(position_search_box).send_keys(phone_number).send_keys(Keys.ENTER).perform()

        # Шаг 3: Ожидание загрузки чата
        wait_for_element(data_browser, 'xpath', '//*[@id="main"]/footer')

        # Шаг 4: Нажатие кнопки прикрепления
        attach_button = wait_for_element(data_browser, 'xpath', "//button[contains(@title, 'Прикрепить')]")
        if attach_button:
            attach_button.click()

        # Шаг 5: Выбор файла
        file_input = wait_for_element(data_browser, 'xpath', "(//input[@type='file'])[2]")
        if file_input:
            file_input.send_keys(image)

        wait_for_element(data_browser, 'xpath', "//div[@aria-label='Отправить']")

        # Шаг 6: Отправка сообщения
        actions.send_keys(Keys.ENTER).perform()
        logging.info(f"Сообщение отправлено: {phone_number}")

    except Exception:
        logging.exception(f"Ошибка при отправке изображения контакту {phone_number}")


if __name__ == "__main__":
    try:
        good_morning_list = load_image_links('good_morning_list.txt')
        phone_numbers = load_phone_numbers('phone_numbers.txt')

        if not phone_numbers:
            raise ValueError("Список номеров пуст или не удалось загрузить.")

        temp_image = preview_image()
        if not temp_image:
            raise ValueError("Не удалось загрузить изображение.")

        while input("Отправьте:\n1.Отправить Изображение\n2.Следующее Изображение\n==>> ") != '1':
            temp_image = preview_image()
            if not temp_image:
                raise ValueError("Не удалось загрузить изображение.")

        local_image_path = convert_image(temp_image)
        if not local_image_path:
            raise ValueError("Не удалось преобразовать изображение.")

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
                raise ValueError("Поле поиска не найдено")

            for number in phone_numbers:
                send_image(browser, search_box, number, local_image_path)

            delete_image()

            # Ожидание загрузки всех отправленных сообщений
            time.sleep(5)
            logging.info("Программа успешно завершила свою работу")

    except FileNotFoundError as e:
        logging.error(f"Файл не найден: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса: {e}")
    except Exception as e:
        logging.exception(f"Непредвиденная ошибка: {e}")
