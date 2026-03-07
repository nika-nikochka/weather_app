# gui/app.py
import customtkinter as ctk
import threading
from weather_api import WeatherAPI
from gui.tabs import WeatherTab, Tab2, Tab3, SettingsTab

class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Инициализация API
        self.weather_api = WeatherAPI()
        
        # Настройки окна
        self.title("Погодный информатор")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Переменные для настроек
        self.temperature_unit = ctk.StringVar(value="celsius")
        self.wind_speed_unit = ctk.StringVar(value="kmh")
        self.auto_save = ctk.BooleanVar(value=True)
        
        # Словарь с переменными настроек для передачи во вкладки
        self.settings_vars = {
            'temperature_unit': self.temperature_unit,
            'wind_speed_unit': self.wind_speed_unit,
            'auto_save': self.auto_save
        }
        
        # Создаем вкладки
        self.setup_tabs()
        
        # Привязываем Enter к поиску
        self.weather_tab.city_entry.bind('<Return>', lambda event: self.search_weather())
    
    def setup_tabs(self):
        """Создание вкладок"""
        # Создаем вкладки
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Добавляем вкладки
        self.tab_view.add("🌤 Погода")
        self.tab_view.add("📊 Вкладка 2")
        self.tab_view.add("📈 Вкладка 3")
        self.tab_view.add("⚙️ Настройки")
        
        # Создаем экземпляры вкладок
        self.weather_tab = WeatherTab(
            self.tab_view.tab("🌤 Погода"),
            self.weather_api,
            {
                'search': self.search_weather,
                'city_selected': self.get_weather  # Добавляем callback для выбора города из списка
            }
        )
        
        self.tab2 = Tab2(self.tab_view.tab("📊 Вкладка 2"))
        self.tab3 = Tab3(self.tab_view.tab("📈 Вкладка 3"))
        
        self.settings_tab = SettingsTab(
            self.tab_view.tab("⚙️ Настройки"),
            self.settings_vars,
            {'save_settings': self.save_settings}
        )
    
    def search_weather(self):
        """Поиск погоды"""
        city_name = self.weather_tab.get_city_name()
        
        if not city_name:
            self.weather_tab.show_status("⚠️ Введите название города!", "orange")
            return
        
        # Блокируем кнопку
        self.weather_tab.set_search_button_state("disabled", "⏳ Поиск...")
        self.weather_tab.show_status(f"🔄 Поиск города '{city_name}'...", "blue")
        
        # Запускаем поиск в отдельном потоке
        thread = threading.Thread(target=self.search_weather_thread, args=(city_name,))
        thread.daemon = True
        thread.start()
    
    def search_weather_thread(self, city_name):
        """Поиск погоды в отдельном потоке"""
        # Поиск городов через API
        results = self.weather_api.search_cities(city_name)
        
        if not results:
            self.weather_tab.show_status(f"❌ Город '{city_name}' не найден!", "red")
            self.weather_tab.set_search_button_state("normal", "🔍 Найти")
            return
        
        # Если найден один город
        if len(results) == 1:
            city_info = results[0]
            self.get_weather(city_info)
        else:
            # Если найдено несколько городов, показываем их в выпадающем списке
            self.weather_tab.show_status(f"✅ Найдено {len(results)} городов. Выберите из списка.", "blue")
            # Выпадающий список уже должен был появиться через on_key_release
            self.weather_tab.set_search_button_state("normal", "🔍 Найти")
    
    def get_weather(self, city_info):
        """Получение данных о погоде"""
        city_name = city_info.get('name', '')
        country = city_info.get('country', 'Неизвестно')
        
        self.weather_tab.show_status(f"🔄 Получение данных о погоде для {city_name}...", "blue")
        
        # Получаем погоду через API в отдельном потоке
        thread = threading.Thread(target=self.get_weather_thread, args=(city_info, city_name, country))
        thread.daemon = True
        thread.start()
    
    def get_weather_thread(self, city_info, city_name, country):
        """Получение погоды в отдельном потоке"""
        weather_data = self.weather_api.get_weather(city_info)
        
        if weather_data:
            # Форматируем полное название города
            full_name = self.weather_api.format_city_full_name(city_info)
            
            # Конвертируем единицы измерения для отображения
            temp = weather_data['current_weather']['temperature']
            temp = self.weather_api.convert_temperature(temp, self.temperature_unit.get())
            temp_unit = "°F" if self.temperature_unit.get() == "fahrenheit" else "°C"
            
            wind_speed = weather_data['current_weather']['windspeed']
            wind_speed = self.weather_api.convert_wind_speed(wind_speed, self.wind_speed_unit.get())
            wind_unit = "м/с" if self.wind_speed_unit.get() == "ms" else "км/ч"
            
            # Сохраняем конвертированные значения в weather_data для отображения
            weather_data['current_weather']['temperature'] = temp
            weather_data['current_weather']['windspeed'] = wind_speed
            
            # Обновляем интерфейс в главном потоке
            self.after(0, lambda: self.weather_tab.update_weather_display(
                full_name, weather_data, temp_unit, wind_unit
            ))
            
            # Сохраняем в файл если нужно
            if self.auto_save.get():
                self.weather_api.save_weather_data(weather_data, city_name, country, True)
            
            self.weather_tab.show_status(f"✅ Данные обновлены для {city_name}", "green")
        else:
            self.weather_tab.show_status("❌ Ошибка получения данных о погоде", "red")
        
        self.weather_tab.set_search_button_state("normal", "🔍 Найти")
    
    def save_settings(self):
        """Сохранение настроек"""
        self.settings_tab.show_save_status("✅ Настройки сохранены", "green")