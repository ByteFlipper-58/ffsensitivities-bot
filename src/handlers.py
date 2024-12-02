# src/handlers.py

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
            if update.callback_query:
                await update.callback_query.answer("Произошла ошибка. Попробуйте позже.")

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
            await update.callback_query.edit_message_text(
                "Произошла ошибка при загрузке производителей. Попробуйте позже."
            )

    async def handle_models(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            locale_manager = LocaleManager(self.default_language)
            manufacturer_model = update.callback_query.data.split(':')[1]

            base_model_url = self.config_manager.get_config('data_sources', 'base_model_url')
            logger.info(f"Загрузка моделей с URL: {base_model_url.format(model=manufacturer_model)}")

            models_data = DataFetcher.get_models(base_model_url, manufacturer_model)

            logger.info(f"Полученные данные моделей: {models_data}")

            if not models_data or 'models' not in models_data:
                logger.error(f"Модели для {manufacturer_model} не найдены")
                await update.callback_query.edit_message_text("Модели не найдены.")
                return

            models = models_data['models']
            logger.info(f"Количество моделей: {len(models)}")

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
            await update.callback_query.edit_message_text(
                "Произошла ошибка при загрузке моделей. Попробуйте позже."
            )

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

            # Формируем текст с чувствительностями
            sensitivities_text = "\n".join([
                f"• {locale_manager.translate(key)}: {value}"
                for key, value in model.get('sensitivities', {}).items()
            ])

            details_text = (
                f"📱 Модель: {model['name']}\n\n"
                f"🔍 Производитель: {manufacturer}\n\n"
                f"🎯 DPI: {model.get('dpi', 'Не указано')}\n"
                f"🖱️ Кнопка Fire: {model.get('fire_button', 'Не указано')}\n\n"
                f"Чувствительность:\n{sensitivities_text}"
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
            await update.callback_query.edit_message_text(
                "Произошла ошибка при отображении деталей модели. Попробуйте позже."
            )

    async def handle_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            locale_manager = LocaleManager(self.default_language)

            support_text = locale_manager.translate('support_message')
            keyboard = KeyboardBuilder.build_support_keyboard(locale_manager)

            if update.callback_query:
                await update.callback_query.edit_message_text(
                    support_text,
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    support_text,
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Ошибка в методе handle_support: {e}", exc_info=True)
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    "Произошла ошибка при отображении поддержки. Попробуйте позже."
                )

    async def handle_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            locale_manager = LocaleManager(self.default_language)

            channel_text = locale_manager.translate('channel_message')
            keyboard = KeyboardBuilder.build_channel_keyboard(locale_manager)

            if update.callback_query:
                await update.callback_query.edit_message_text(
                    channel_text,
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    channel_text,
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Ошибка в методе handle_channel: {e}", exc_info=True)
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    "Произошла ошибка при отображении канала. Попробуйте позже."
                )