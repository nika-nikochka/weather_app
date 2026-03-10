# weather_api.py
import requests
import json
import os
from datetime import datetime, timedelta

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
    
    def get_forecast(self, city_info, days=7):
        """
        Получение прогноза погоды на указанное количество дней
        city_info - словарь с информацией о городе
        days - количество дней прогноза (7, 14 или 16 максимум)
        """
        try:
            lat = city_info['latitude']
            lon = city_info['longitude']
            
            # Ограничиваем максимальное количество дней (бесплатное API дает до 16 дней)
            if days > 16:
                days = 16
            
            # Запрос прогноза с ежедневными данными
            forecast_url = (f"https://api.open-meteo.com/v1/forecast"
                           f"?latitude={lat}&longitude={lon}"
                           f"&daily=weathercode,temperature_2m_max,temperature_2m_min,"
                           f"precipitation_sum,precipitation_probability_max,"
                           f"windspeed_10m_max,winddirection_10m_dominant"
                           f"&forecast_days={days}"
                           f"&timezone=auto")
            
            print(f"🔄 Запрос прогноза на {days} дней...")
            forecast_response = requests.get(forecast_url, timeout=10)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            # Добавляем информацию о городе
            forecast_data['city_info'] = {
                'name': city_info.get('name', ''),
                'country': city_info.get('country', 'Неизвестно'),
                'admin1': city_info.get('admin1', ''),
                'latitude': lat,
                'longitude': lon
            }
            
            # Добавляем информацию о периоде прогноза
            forecast_data['forecast_days'] = days
            
            return forecast_data
            
        except requests.exceptions.Timeout:
            print("❌ Превышено время ожидания при получении прогноза")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Ошибка подключения к интернету")
            return None
        except Exception as e:
            print(f"❌ Ошибка получения прогноза: {str(e)}")
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
            
            # Определяем тип данных (текущая погода или прогноз)
            data_type = "forecast" if "daily" in weather_data else "current"
            
            filename = f"weather_data/{clean_city}_{clean_country}_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    def get_weather_description(weather_code):
        """
        Получение текстового описания погоды по коду WMO
        https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM
        """
        weather_codes = {
            0: "Ясно",
            1: "Преимущественно ясно",
            2: "Переменная облачность",
            3: "Пасмурно",
            45: "Туман",
            48: "Изморозь",
            51: "Легкая морось",
            53: "Умеренная морось",
            55: "Сильная морось",
            56: "Легкая ледяная морось",
            57: "Сильная ледяная морось",
            61: "Небольшой дождь",
            63: "Умеренный дождь",
            65: "Сильный дождь",
            66: "Легкий ледяной дождь",
            67: "Сильный ледяной дождь",
            71: "Небольшой снег",
            73: "Умеренный снег",
            75: "Сильный снег",
            77: "Снежная крупа",
            80: "Небольшой ливень",
            81: "Умеренный ливень",
            82: "Сильный ливень",
            85: "Небольшой снегопад",
            86: "Сильный снегопад",
            95: "Гроза",
            96: "Гроза с градом",
            99: "Сильная гроза с градом"
        }
        return weather_codes.get(weather_code, "Неизвестно")
    
    @staticmethod
    def get_weather_icon(weather_code):
        """Получение эмодзи для погоды"""
        if weather_code == 0:
            return "☀️"  # Ясно
        elif weather_code == 1:
            return "🌤️"  # Преимущественно ясно
        elif weather_code == 2:
            return "⛅"  # Переменная облачность
        elif weather_code == 3:
            return "☁️"  # Пасмурно
        elif weather_code in [45, 48]:
            return "🌫️"  # Туман
        elif weather_code in [51, 53, 55, 56, 57]:
            return "🌧️"  # Морось/дождь
        elif weather_code in [61, 63, 65, 66, 67, 80, 81, 82]:
            return "🌧️"  # Дождь
        elif weather_code in [71, 73, 75, 77, 85, 86]:
            return "🌨️"  # Снег
        elif weather_code in [95, 96, 99]:
            return "⛈️"  # Гроза
        else:
            return "❓"
    
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
            return round(temp_celsius * 9/5 + 32, 1)
        return round(temp_celsius, 1)
    
    @staticmethod
    def convert_wind_speed(speed_kmh, to_unit='kmh'):
        """Конвертация скорости ветра"""
        if to_unit == 'ms':
            return round(speed_kmh / 3.6, 1)
        return round(speed_kmh, 1)
    
    @staticmethod
    def convert_precipitation(precip_mm, to_unit='mm'):
        """Конвертация осадков"""
        if to_unit == 'inches':
            return round(precip_mm / 25.4, 2)
        return round(precip_mm, 1)
