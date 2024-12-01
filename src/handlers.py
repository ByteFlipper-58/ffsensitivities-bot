import logging
from telegram import Update
from telegram.ext import ContextTypes
from .utils import ConfigManager, LocaleManager, DataFetcher
from .keyboards import KeyboardBuilder

# Настройка логирования
logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.default_language = self.config_manager.get_config('languages', 'default')

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            locale_manager = LocaleManager(self.default_language)
            keyboard = KeyboardBuilder.build_main_menu(locale_manager)
            
            if update.message:
                await update.message.reply_text(
                    locale_manager.translate('start_message'), 
                    reply_markup=keyboard
                )
            elif update.callback_query:
                await update.callback_query.edit_message_text(
                    locale_manager.translate('start_message'), 
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Ошибка в методе start: {e}", exc_info=True)

    async def handle_manufacturers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            locale_manager = LocaleManager(self.default_language)
            page = int(update.callback_query.data.split(':')[1]) if ':' in update.callback_query.data else 0
            manufacturers_url = self.config_manager.get_config('data_sources', 'manufacturers_url')
            
            manufacturers = DataFetcher.get_manufacturers(manufacturers_url)
            per_page = self.config_manager.get_config('pagination', 'manufacturers_per_page')
            columns = self.config_manager.get_config('pagination', 'manufacturers_columns')
            
            keyboard = KeyboardBuilder.build_manufacturers_keyboard(
                manufacturers, 
                page, 
                locale_manager, 
                per_page, 
                columns
            )
            
            await update.callback_query.edit_message_text(
                locale_manager.translate('select_manufacturer'), 
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в методе handle_manufacturers: {e}", exc_info=True)
            await update.callback_query.edit_message_text("Произошла ошибка при загрузке производителей.")

    async def handle_models(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            locale_manager = LocaleManager(self.default_language)
            manufacturer_model = update.callback_query.data.split(':')[1]
            
            base_model_url = self.config_manager.get_config('data_sources', 'base_model_url')
            models_data = DataFetcher.get_models(base_model_url, manufacturer_model)
            
            if not models_data or 'models' not in models_data:
                await update.callback_query.edit_message_text("Модели не найдены.")
                return

            models = models_data['models']
            per_page = self.config_manager.get_config('pagination', 'models_per_page')

            page_match = update.callback_query.data.split(':')
            page = int(page_match[2]) if len(page_match) > 2 else 0

            keyboard = KeyboardBuilder.build_models_keyboard(
                models, 
                manufacturer_model, 
                page, 
                locale_manager, 
                per_page
            )
            
            await update.callback_query.edit_message_text(
                locale_manager.translate('select_model', manufacturer=manufacturer_model), 
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в методе handle_models: {e}", exc_info=True)
            await update.callback_query.edit_message_text("Произошла ошибка при загрузке моделей.")

    async def show_model_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            locale_manager = LocaleManager(self.default_language)
            manufacturer, model_name = update.callback_query.data.split(':')[1:]
            
            base_model_url = self.config_manager.get_config('data_sources', 'base_model_url')
            models_data = DataFetcher.get_models(base_model_url, manufacturer)
            
            model = next((m for m in models_data.get('models', []) if m['name'] == model_name), None)
            
            if not model:
                await update.callback_query.edit_message_text("Модель не найдена.")
                return

            details_text = locale_manager.translate('model_details', 
                manufacturer=manufacturer, 
                name=model['name'], 
                dpi=model.get('dpi', 0),
                fire_button=model.get('fire_button', 0),
                **model.get('sensitivities', {})
            )

            keyboard = KeyboardBuilder.build_model_details_keyboard(
                manufacturer, 
                locale_manager
            )

            await update.callback_query.edit_message_text(
                details_text, 
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в методе show_model_details: {e}", exc_info=True)
            await update.callback_query.edit_message_text("Произошла ошибка при отображении деталей модели.")