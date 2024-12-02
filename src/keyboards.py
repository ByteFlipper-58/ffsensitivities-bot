# src/keyboards.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict

class KeyboardBuilder:
    @staticmethod
    def build_main_menu(locale_manager):
        keyboard = [
            [InlineKeyboardButton(locale_manager.translate('sensitivity_settings'), callback_data='manufacturers')],
            [InlineKeyboardButton(locale_manager.translate('support'), url='https://t.me/ibremminer837')],
            [InlineKeyboardButton(locale_manager.translate('channel'), url='https://t.me/byteflipper')],
            [InlineKeyboardButton(locale_manager.translate('request_settings'), url='https://t.me/byteflipper_feedback_bot')],
            [InlineKeyboardButton(locale_manager.translate('download_app'), url='https://play.google.com/store/apps/details?id=com.byteflipper.ffsensitivities')]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def build_manufacturers_keyboard(manufacturers: List[Dict], page: int, locale_manager, per_page: int = 5, columns: int = 2):
        start_idx = page * per_page
        end_idx = start_idx + per_page
        current_manufacturers = manufacturers[start_idx:end_idx]

        # Создаем клавиатуру с указанным количеством столбцов
        keyboard = []
        for i in range(0, len(current_manufacturers), columns):
            row = [
                InlineKeyboardButton(m['name'], callback_data=f"manufacturer:{m['model']}")
                for m in current_manufacturers[i:i+columns]
            ]
            keyboard.append(row)

        # Кнопки навигации
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"manufacturers_page:{page-1}"))
        if end_idx < len(manufacturers):
            nav_row.append(InlineKeyboardButton("➡️", callback_data=f"manufacturers_page:{page+1}"))

        if nav_row:
            keyboard.append(nav_row)

        # Убираем кнопку "Назад"
        keyboard.append([
            InlineKeyboardButton(locale_manager.translate('home'), callback_data='home')
        ])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def build_models_keyboard(models: List[Dict], manufacturer: str, page: int, locale_manager, per_page: int = 5):
        start_idx = page * per_page
        end_idx = start_idx + per_page
        current_models = models[start_idx:end_idx]

        keyboard = [
            [InlineKeyboardButton(m['name'], callback_data=f"model:{manufacturer}:{m['name']}")]
            for m in current_models
        ]

        # Кнопки навигации
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"models_page:{manufacturer}:{page-1}"))
        if end_idx < len(models):
            nav_row.append(InlineKeyboardButton("➡️", callback_data=f"models_page:{manufacturer}:{page+1}"))

        if nav_row:
            keyboard.append(nav_row)

        # Кнопки возврата
        keyboard.append([
            InlineKeyboardButton(locale_manager.translate('back'), callback_data=f'manufacturer:{manufacturer}'),
            InlineKeyboardButton(locale_manager.translate('home'), callback_data='home')
        ])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def build_model_details_keyboard(manufacturer: str, locale_manager):
        keyboard = [
            [
                InlineKeyboardButton(locale_manager.translate('back'), callback_data='manufacturers'),
                InlineKeyboardButton(locale_manager.translate('home'), callback_data='home')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)