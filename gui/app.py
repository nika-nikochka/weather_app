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
        
        # Дополнительные переменные для настроек
        self.pressure_unit = ctk.StringVar(value="mmhg")
        self.precipitation_unit = ctk.StringVar(value="mm")
        self.theme = ctk.StringVar(value="dark")
        self.language = ctk.StringVar(value="ru")
        self.folder_path = ctk.StringVar(value="weather_data/")
        self.update_period = ctk.IntVar(value=15)
        
        # Применяем начальную тему
        self.apply_theme(self.theme.get())
        
        # Отслеживаем изменение темы
        self.theme.trace_add('write', self.on_theme_changed)
        
        # Словарь с переменными настроек для передачи во вкладки
        self.settings_vars = {
            'temperature_unit': self.temperature_unit,
            'wind_speed_unit': self.wind_speed_unit,
            'auto_save': self.auto_save,
            'pressure_unit': self.pressure_unit,
            'precipitation_unit': self.precipitation_unit,
            'theme': self.theme,
            'language': self.language,
            'folder_path': self.folder_path,
            'update_period': self.update_period
        }
        
        # Создаем вкладки
        self.setup_tabs()
        
        # Привязываем Enter к поиску
        self.weather_tab.city_entry.bind('<Return>', lambda event: self.search_weather())
    
    def apply_theme(self, theme_name):
        """Применение темы оформления"""
        if theme_name == "light":
            ctk.set_appearance_mode("light")
        elif theme_name == "dark":
            ctk.set_appearance_mode("dark")
        else:  # system
            ctk.set_appearance_mode("system")
    
    def on_theme_changed(self, *args):
        """Обработчик изменения темы"""
        self.apply_theme(self.theme.get())
        
        # Обновляем цвета во вкладках, если это необходимо
        if hasattr(self, 'settings_tab'):
            self.settings_tab.update_theme_colors(self.theme.get())
    
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
                'city_selected': self.get_weather
            }
        )
        
        # Обновленная инициализация Tab2 с передачей weather_api и settings_vars
        self.tab2 = Tab2(
            self.tab_view.tab("📊 Вкладка 2"),
            self.weather_api,
            self.settings_vars
        )
        
        self.tab3 = Tab3(self.tab_view.tab("📈 Вкладка 3"))
        
        self.settings_tab = SettingsTab(
            self.tab_view.tab("⚙️ Настройки"),
            self.settings_vars,
            {
                'save_settings': self.save_settings,
                'browse_folder': self.browse_folder
            }
        )
    
    def browse_folder(self):
        """Открытие диалога выбора папки"""
        from tkinter import filedialog
        folder = filedialog.askdirectory(title="Выберите папку для сохранения данных")
        if folder:
            self.folder_path.set(folder)
    
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
            
            # После обновления текущей погоды, передаем город для прогноза
            self.after(0, lambda: self.set_city_for_forecast(city_info))
            
            # Сохраняем в файл если нужно
            if self.auto_save.get():
                self.weather_api.save_weather_data(weather_data, city_name, country, True)
            
            self.weather_tab.show_status(f"✅ Данные обновлены для {city_name}", "green")
        else:
            self.weather_tab.show_status("❌ Ошибка получения данных о погоде", "red")
        
        self.weather_tab.set_search_button_state("normal", "🔍 Найти")
    
    def set_city_for_forecast(self, city_info):
        """Передает выбранный город во вкладку с прогнозом"""
        if hasattr(self, 'tab2'):
            self.tab2.set_city(city_info)
    
    def save_settings(self):
        """Сохранение настроек"""
        # Здесь можно добавить сохранение настроек в файл
        self.settings_tab.show_save_status("✅ Настройки сохранены", "green")
