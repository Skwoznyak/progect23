import logging
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from telegram import Update, ReplyKeyboardMarkup
Token_tg = '7742618807:AAFhs_iDheMVTloiQD9SOtpVPvEKANbshvg'

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
INPUT_TRACKING_NUMBER = 0

# Функция для парсинга сайта


def parse_cargo_data(tracking_number):
    try:
        # Настройка Selenium с автоматической установкой ChromeDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Без графического интерфейса
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)

        # Открываем сайт
        driver.get('https://www.cargog20.com/h5/#/')

        # Ждем загрузки страницы
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[placeholder="请输入运单号"]'))
        )

        # Вводим трек-номер
        input_field = driver.find_element(
            By.CSS_SELECTOR, 'input[placeholder="请输入运单号"]')
        input_field.send_keys(tracking_number)

        # Нажимаем кнопку поиска (замените селектор на актуальный)
        search_button = driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label="搜索"]')  # Уточните селектор
        search_button.click()

        # Ждем загрузки результатов
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.result-container'))  # Уточните селектор
        )

        # Парсим данные (замените селекторы на актуальные)
        total_weight = driver.find_element(
            By.CSS_SELECTOR, '.total-weight').text  # Уточните селектор
        total_volume = driver.find_element(
            By.CSS_SELECTOR, '.total-volume').text  # Уточните селектор
        delivery_date = driver.find_element(
            By.CSS_SELECTOR, '.delivery-date').text  # Уточните селектор
        delivery_status = driver.find_element(
            By.CSS_SELECTOR, '.delivery-status').text  # Уточните селектор

        # Формируем результат
        result = (
            f"📦 Трек-номер: {tracking_number}\n"
            f"⚖️ Общий вес: {total_weight}\n"
            f"📏 Общий объем: {total_volume}\n"
            f"📅 Дата актуализации: {delivery_date}\n"
            f"🚚 Статус доставки: {delivery_status}"
        )

        driver.quit()
        return result

    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        driver.quit()
        return "❌ Произошла ошибка при обработке запроса. Пожалуйста, проверьте трек-номер и попробуйте снова."

# Команда /start


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"Пользователь {user.first_name} начал взаимодействие с ботом")

    keyboard = [['Отследить посылку']]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот для отслеживания посылок на сайте cargog20.com. "
        "Нажми 'Отследить посылку' и отправь мне трек-номер.",
        reply_markup=reply_markup
    )
    return INPUT_TRACKING_NUMBER

# Обработка трек-номера


async def receive_tracking_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text

    if user_input == 'Отследить посылку':
        await update.message.reply_text("📬 Пожалуйста, отправь мне трек-номер посылки.")
        return INPUT_TRACKING_NUMBER

    await update.message.reply_text("⏳ Обрабатываю запрос, пожалуйста, подождите...")

    # Парсим данные с сайта
    result = parse_cargo_data(user_input)

    # Отправляем результат пользователю
    await update.message.reply_text(result)

    # Возвращаем возможность нового запроса
    keyboard = [['Отследить посылку']]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Хочешь отследить еще одну посылку?", reply_markup=reply_markup)
    return INPUT_TRACKING_NUMBER

# Команда /cancel для отмены


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("🚫 Операция отменена. Напиши /start, чтобы начать заново.")
    return ConversationHandler.END


def main():
    # Замените 'YOUR_BOT_TOKEN' на токен вашего бота
    application = Application.builder().token(Token_tg).build()

    # Настройка ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            INPUT_TRACKING_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_tracking_number)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Добавляем обработчик
    application.add_handler(conv_handler)

    # Запускаем бота
    logger.info("Бот запущен")
    application.run_polling()


if __name__ == '__main__':
    main()
