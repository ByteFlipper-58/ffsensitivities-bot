import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from .handlers import BotHandlers
from .utils import ConfigManager

# Загрузка переменных окружения
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

def main():
    config_manager = ConfigManager()
    
    # Получаем токен из переменных окружения
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token or bot_token == 'YOUR_BOT_TOKEN':
        print("Please set your Telegram Bot token in .env file")
        return

    handlers = BotHandlers()
    
    application = Application.builder().token(bot_token).build()

    # Регистрация команд
    application.add_handler(CommandHandler('start', handlers.start))
    
    # Регистрация обработчиков callback-запросов
    application.add_handler(CallbackQueryHandler(handlers.start, pattern=r'^home$'))
    application.add_handler(CallbackQueryHandler(handlers.handle_manufacturers, pattern=r'^manufacturers$|^manufacturers_page:\d+$'))
    application.add_handler(CallbackQueryHandler(handlers.handle_models, pattern=r'^manufacturer:\w+$|^models_page:\w+:\d+$'))
    application.add_handler(CallbackQueryHandler(handlers.show_model_details, pattern=r'^model:\w+:\w+$'))

    # Запуск бота
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()