import yaml
import json
import requests
import os
import logging
from typing import Dict, List, Optional

# Настройка логера
logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config_path: str = 'config/config.yaml'):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Конфигурация успешно загружена из {config_path}")
        except FileNotFoundError:
            logger.error(f"Файл конфигурации не найден: {config_path}")
            self.config = {}
        except yaml.YAMLError as e:
            logger.error(f"Ошибка парсинга YAML: {e}")
            self.config = {}

    def get_config(self, *keys):
        try:
            value = self.config
            for key in keys:
                value = value.get(key)
            return value
        except Exception as e:
            logger.error(f"Ошибка получения конфигурации для ключей {keys}: {e}")
            return None

class LocaleManager:
    def __init__(self, language: str = 'ru'):
        locale_path = f'config/locales/{language}.json'
        try:
            with open(locale_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            logger.info(f"Локализация успешно загружена для языка: {language}")
        except FileNotFoundError:
            logger.error(f"Файл локализации не найден: {locale_path}")
            self.translations = {}
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON локализации: {e}")
            self.translations = {}

    def translate(self, key: str, **kwargs) -> str:
        try:
            template = self.translations.get(key, key)
            return template.format(**kwargs)
        except Exception as e:
            logger.warning(f"Ошибка перевода для ключа {key}: {e}")
            return key

class DataFetcher:
    @staticmethod
    def fetch_json(url: str) -> Optional[Dict]:
        try:
            logger.info(f"Попытка загрузки JSON с URL: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"JSON успешно загружен. Количество ключей: {len(data) if data else 0}")
            return data
        except requests.RequestException as e:
            logger.error(f"Ошибка при загрузке данных с {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON с {url}: {e}")
            return None

    @staticmethod
    def get_manufacturers(url: str) -> List[Dict]:
        logger.info(f"Получение списка производителей из {url}")
        data = DataFetcher.fetch_json(url)
        
        if data is None:
            logger.error("Не удалось загрузить данные о производителях")
            return []
        
        if 'manufacturers' not in data:
            logger.error(f"Ключ 'manufacturers' отсутствует. Доступные ключи: {data.keys()}")
            return []
        
        manufacturers = [
            manufacturer for manufacturer in data['manufacturers']
            if manufacturer.get('showInProductionApp', False)
        ]
        
        logger.info(f"Найдено производителей: {len(manufacturers)}")
        for manufacturer in manufacturers:
            logger.info(f"Производитель: {manufacturer.get('name', 'Неизвестно')}, showInProductionApp: {manufacturer.get('showInProductionApp')}")
        
        return manufacturers

    @staticmethod
    def get_models(base_url: str, model: str) -> Optional[Dict]:
        logger.info(f"Получение моделей для {model}")
        url = base_url.format(model=model)
        
        try:
            data = DataFetcher.fetch_json(url)
            
            if data is None:
                logger.error(f"Не удалось загрузить модели для {model}")
                return None
            
            if 'models' not in data:
                logger.error(f"Ключ 'models' отсутствует в данных для {model}")
                return None
            
            logger.info(f"Получено моделей: {len(data['models'])}")
            return data
        
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при получении моделей для {model}: {e}")
            return None