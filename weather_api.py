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
        Получение данных о погоде для выбранного города с дополнительными параметрами
        city_info - словарь с информацией о городе (latitude, longitude, name, country и т.д.)
        """
        try:
            lat = city_info['latitude']
            lon = city_info['longitude']
            
            # Запрос погоды с дополнительными параметрами
            weather_url = (f"https://api.open-meteo.com/v1/forecast"
                          f"?latitude={lat}&longitude={lon}"
                          f"&current_weather=true"
                          f"&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,pressure_msl,windspeed_10m,winddirection_10m"
                          f"&daily=sunrise,sunset,weathercode,temperature_2m_max,temperature_2m_min"
                          f"&forecast_days=7"
                          f"&timezone=auto")
            
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
            
            # Добавляем дополнительные параметры из почасовых данных
            if 'hourly' in weather_data and 'current_weather' in weather_data:
                self._enrich_current_weather(weather_data)
            
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
    
    def _enrich_current_weather(self, weather_data):
        """
        Обогащает текущие данные погоды дополнительными параметрами из почасовых данных
        """
        try:
            current = weather_data['current_weather']
            hourly = weather_data['hourly']
            
            # Находим ближайший час к текущему времени
            current_time = current['time']
            
            if 'time' in hourly:
                for i, time in enumerate(hourly['time']):
                    if time >= current_time:
                        # Добавляем влажность
                        if 'relative_humidity_2m' in hourly and i < len(hourly['relative_humidity_2m']):
                            weather_data['current_weather']['relative_humidity'] = hourly['relative_humidity_2m'][i]
                        
                        # Добавляем ощущаемую температуру
                        if 'apparent_temperature' in hourly and i < len(hourly['apparent_temperature']):
                            weather_data['current_weather']['apparent_temperature'] = hourly['apparent_temperature'][i]
                        
                        # Добавляем давление
                        if 'pressure_msl' in hourly and i < len(hourly['pressure_msl']):
                            weather_data['current_weather']['pressure'] = hourly['pressure_msl'][i]
                        
                        # Добавляем дополнительную информацию о ветре для сверки
                        if 'windspeed_10m' in hourly and i < len(hourly['windspeed_10m']):
                            weather_data['current_weather']['hourly_windspeed'] = hourly['windspeed_10m'][i]
                        
                        if 'winddirection_10m' in hourly and i < len(hourly['winddirection_10m']):
                            weather_data['current_weather']['hourly_winddirection'] = hourly['winddirection_10m'][i]
                        
                        break
            
            # Добавляем информацию о восходе и закате
            if 'daily' in weather_data:
                daily = weather_data['daily']
                if 'sunrise' in daily and daily['sunrise']:
                    weather_data['sunrise'] = daily['sunrise'][0]
                if 'sunset' in daily and daily['sunset']:
                    weather_data['sunset'] = daily['sunset'][0]
                if 'weathercode' in daily and daily['weathercode']:
                    weather_data['daily_weathercode'] = daily['weathercode'][0]
                    
        except Exception as e:
            print(f"⚠️ Ошибка при обогащении данных: {e}")
    
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
            
            # Запрос прогноза с ежедневными данными и дополнительными параметрами
            forecast_url = (f"https://api.open-meteo.com/v1/forecast"
                           f"?latitude={lat}&longitude={lon}"
                           f"&daily=weathercode,temperature_2m_max,temperature_2m_min,"
                           f"apparent_temperature_max,apparent_temperature_min,"
                           f"precipitation_sum,precipitation_probability_max,"
                           f"windspeed_10m_max,winddirection_10m_dominant,"
                           f"sunrise,sunset,uv_index_max"
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
    
    def get_historical_data(self, city_info, date, years_back=50):
        """
        Получение исторических данных для указанной даты за последние N лет
        
        city_info - словарь с информацией о городе
        date - дата в формате datetime или строка YYYY-MM-DD
        years_back - количество лет для получения данных (максимум 50)
        
        Возвращает словарь с историческими данными за каждый год
        """
        try:
            lat = city_info['latitude']
            lon = city_info['longitude']
            
            # Преобразуем дату в объект datetime если передана строка
            if isinstance(date, str):
                target_date = datetime.strptime(date, '%Y-%m-%d')
            else:
                target_date = date
            
            # Ограничиваем количество лет
            if years_back > 50:
                years_back = 50
            
            historical_data = {
                'city_info': {
                    'name': city_info.get('name', ''),
                    'country': city_info.get('country', 'Неизвестно'),
                    'admin1': city_info.get('admin1', ''),
                    'latitude': lat,
                    'longitude': lon
                },
                'target_date': target_date.strftime('%Y-%m-%d'),
                'years_back': years_back,
                'historical_records': []
            }
            
            current_year = datetime.now().year
            month_day = target_date.strftime('-%m-%d')
            
            print(f"🔄 Запрос исторических данных за {years_back} лет для даты {target_date.strftime('%d.%m')}...")
            
            for year in range(current_year - years_back, current_year):
                historical_date = f"{year}{month_day}"
                
                # Запрос исторических данных с дополнительными параметрами
                historical_url = (f"https://archive-api.open-meteo.com/v1/archive"
                                 f"?latitude={lat}&longitude={lon}"
                                 f"&start_date={historical_date}"
                                 f"&end_date={historical_date}"
                                 f"&daily=temperature_2m_max,temperature_2m_min,"
                                 f"apparent_temperature_max,apparent_temperature_min,"
                                 f"precipitation_sum,weathercode,windspeed_10m_max,"
                                 f"relative_humidity_2m_max,pressure_msl_mean"
                                 f"&timezone=auto")
                
                try:
                    hist_response = requests.get(historical_url, timeout=10)
                    hist_response.raise_for_status()
                    hist_data = hist_response.json()
                    
                    if 'daily' in hist_data and len(hist_data['daily']['time']) > 0:
                        record = {
                            'year': year,
                            'date': historical_date,
                            'temperature_max': hist_data['daily']['temperature_2m_max'][0],
                            'temperature_min': hist_data['daily']['temperature_2m_min'][0],
                            'apparent_temperature_max': hist_data['daily'].get('apparent_temperature_max', [None])[0],
                            'apparent_temperature_min': hist_data['daily'].get('apparent_temperature_min', [None])[0],
                            'precipitation': hist_data['daily']['precipitation_sum'][0],
                            'weathercode': hist_data['daily']['weathercode'][0],
                            'wind_speed': hist_data['daily']['windspeed_10m_max'][0],
                            'humidity': hist_data['daily'].get('relative_humidity_2m_max', [None])[0],
                            'pressure': hist_data['daily'].get('pressure_msl_mean', [None])[0],
                            'weather_description': self.get_weather_description(hist_data['daily']['weathercode'][0]),
                            'weather_icon': self.get_weather_icon(hist_data['daily']['weathercode'][0])
                        }
                        historical_data['historical_records'].append(record)
                        
                except Exception as e:
                    print(f"⚠️ Не удалось получить данные за {year}: {str(e)}")
                    continue
            
            # Сортируем записи по году
            historical_data['historical_records'].sort(key=lambda x: x['year'])
            
            # Добавляем статистику
            if historical_data['historical_records']:
                temps_max = [r['temperature_max'] for r in historical_data['historical_records'] if r['temperature_max'] is not None]
                temps_min = [r['temperature_min'] for r in historical_data['historical_records'] if r['temperature_min'] is not None]
                precip = [r['precipitation'] for r in historical_data['historical_records'] if r['precipitation'] is not None]
                
                historical_data['statistics'] = {
                    'max_temperature_absolute': max(temps_max) if temps_max else None,
                    'min_temperature_absolute': min(temps_min) if temps_min else None,
                    'avg_temperature_max': round(sum(temps_max) / len(temps_max), 1) if temps_max else None,
                    'avg_temperature_min': round(sum(temps_min) / len(temps_min), 1) if temps_min else None,
                    'avg_precipitation': round(sum(precip) / len(precip), 1) if precip else None,
                    'years_with_data': len(historical_data['historical_records'])
                }
            
            print(f"✅ Получены исторические данные за {len(historical_data['historical_records'])} лет")
            return historical_data
            
        except requests.exceptions.Timeout:
            print("❌ Превышено время ожидания при получении исторических данных")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Ошибка подключения к интернету")
            return None
        except Exception as e:
            print(f"❌ Ошибка получения исторических данных: {str(e)}")
            return None
    
    def get_complete_weather_data(self, city_info, forecast_days=7, get_history=True, history_years=50):
        """
        Получение полных данных: текущая погода + прогноз + исторические данные
        """
        complete_data = {
            'city_info': {
                'name': city_info.get('name', ''),
                'country': city_info.get('country', 'Неизвестно'),
                'admin1': city_info.get('admin1', ''),
                'latitude': city_info['latitude'],
                'longitude': city_info['longitude']
            },
            'timestamp': datetime.now().isoformat(),
            'current_weather': None,
            'forecast': None,
            'historical_data': None
        }
        
        # Получаем текущую погоду
        weather_data = self.get_weather(city_info)
        if weather_data:
            complete_data['current_weather'] = weather_data.get('current_weather', {})
            if 'sunrise' in weather_data:
                complete_data['sunrise'] = weather_data['sunrise']
            if 'sunset' in weather_data:
                complete_data['sunset'] = weather_data['sunset']
        
        # Получаем прогноз
        forecast_data = self.get_forecast(city_info, forecast_days)
        if forecast_data and 'daily' in forecast_data:
            complete_data['forecast'] = {
                'daily': forecast_data['daily'],
                'forecast_days': forecast_days
            }
        
        # Получаем исторические данные для сегодняшней даты
        if get_history:
            today = datetime.now()
            historical_data = self.get_historical_data(city_info, today, history_years)
            if historical_data:
                complete_data['historical_data'] = historical_data
        
        return complete_data
    
    def save_weather_data(self, weather_data, city_name, country, data_type="complete", auto_save=True):
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
            return "🔆"  # Ясно
        elif weather_code == 1:
            return "🌤️"  # Преимущественно ясно
        elif weather_code == 2:
            return "⛅"  # Переменная облачность
        elif weather_code == 3:
            return "☁"  # Пасмурно
        elif weather_code in [45, 48]:
            return "⛆"  # Туман
        elif weather_code in [51, 53, 55, 56, 57]:
            return "☔"  # Морось/дождь
        elif weather_code in [61, 63, 65, 66, 67, 80, 81, 82]:
            return "☔"  # Дождь
        elif weather_code in [71, 73, 75, 77, 85, 86]:
            return "🌨"  # Снег
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
    
    @staticmethod
    def format_time(time_str):
        """Форматирование времени для отображения (только часы:минуты)"""
        if time_str and len(time_str) >= 16:
            return time_str[11:16]
        return time_str
