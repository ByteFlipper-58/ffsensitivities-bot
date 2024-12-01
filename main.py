import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from src.bot import main as bot_main

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,  # Можно изменить на DEBUG для более подробной информации
    filename='bot.log'   # Логи будут записываться в этот файл
)

logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Запуск телеграм-бота")
        bot_main()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)

if __name__ == '__main__':
    main()