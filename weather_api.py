# weather_api.py
import requests
import json
import os
from datetime import datetime

class WeatherAPI:
    """Класс для работы с API погоды Open-Meteo"""
    
    def __init__(self):
        self.last_search_results = None
    
    def search_cities(self, city_name):
        """
        Поиск городов по названию
        Возвращает список найденных городов или None в случае ошибки
        """
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=20&language=ru"
        
        try:
            print(f"🔄 Поиск города: {city_name}")
            geo_response = requests.get(geocoding_url, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data.get('results'):
                print(f"❌ Город {city_name} не найден.")
                return None
            
            self.last_search_results = geo_data['results']
            return geo_data['results']
            
        except requests.exceptions.Timeout:
            print("❌ Превышено время ожидания ответа от сервера")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Ошибка подключения к интернету")
            return None
        except Exception as e:
            print(f"❌ Ошибка при запросе геоданных: {e}")
            return None
    
    def get_weather(self, city_info):
        """
        Получение данных о погоде для выбранного города
        city_info - словарь с информацией о городе (latitude, longitude, name, country и т.д.)
        """
        try:
            lat = city_info['latitude']
            lon = city_info['longitude']
            
            # Запрос погоды
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m&forecast_days=7&timezone=auto"
            
            print("🔄 Запрос данных о погоде...")
            weather_response = requests.get(weather_url, timeout=10)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            
            # Добавляем информацию о городе
            weather_data['city_info'] = {
                'name': city_info.get('name', ''),
                'country': city_info.get('country', 'Неизвестно'),
                'admin1': city_info.get('admin1', ''),
                'latitude': lat,
                'longitude': lon
            }
            
            return weather_data
            
        except requests.exceptions.Timeout:
            print("❌ Превышено время ожидания при получении погоды")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Ошибка подключения к интернету")
            return None
        except Exception as e:
            print(f"❌ Ошибка получения погоды: {str(e)}")
            return None
    
    def save_weather_data(self, weather_data, city_name, country, auto_save=True):
        """Сохранение данных в файл"""
        if not auto_save:
            return None
            
        try:
            # Создаем папку weather_data если её нет
            if not os.path.exists("weather_data"):
                os.makedirs("weather_data")
            
            # Очищаем имя файла от недопустимых символов
            clean_city = "".join(c for c in city_name if c.isalnum() or c in ' -_').rstrip()
            clean_country = "".join(c for c in country if c.isalnum() or c in ' -_').rstrip()
            
            filename = f"weather_data/{clean_city}_{clean_country}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(weather_data, f, ensure_ascii=False, indent=4)
            
            print(f"💾 Данные сохранены в {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Ошибка сохранения: {str(e)}")
            return None
    
    def format_city_full_name(self, city_info):
        """Форматирует полное название города"""
        city_name = city_info.get('name', '')
        admin = city_info.get('admin1', '')
        country = city_info.get('country', 'Неизвестно')
        
        full_name = city_name
        if admin and admin != city_name:
            full_name += f", {admin}"
        full_name += f", {country}"
        
        return full_name
    
    @staticmethod
    def get_wind_direction_text(degrees):
        """Преобразование градусов в текстовое направление"""
        directions = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
        index = round(degrees / 45) % 8
        return directions[index]
    
    @staticmethod
    def convert_temperature(temp_celsius, to_unit='celsius'):
        """Конвертация температуры"""
        if to_unit == 'fahrenheit':
            return temp_celsius * 9/5 + 32
        return temp_celsius
    
    @staticmethod
    def convert_wind_speed(speed_kmh, to_unit='kmh'):
        """Конвертация скорости ветра"""
        if to_unit == 'ms':
            return speed_kmh / 3.6
        return speed_kmh