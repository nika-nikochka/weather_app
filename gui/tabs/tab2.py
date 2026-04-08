# gui/tabs/tab2.py
import customtkinter as ctk
import threading
from datetime import datetime, timedelta
from tkinter import messagebox

class Tab2:
    def __init__(self, parent, weather_api, settings_vars):
        """
        parent - родительский фрейм (вкладка)
        weather_api - экземпляр класса WeatherAPI
        settings_vars - словарь с переменными настроек
        """
        self.parent = parent
        self.weather_api = weather_api
        self.settings_vars = settings_vars
        self.current_city_info = None
        self.current_forecast_data = None
        
        # Переменные для периода прогноза
        self.forecast_days = ctk.IntVar(value=7)  # 7 или 14 дней
        
        # Устанавливаем прозрачный фон родительского фрейма
        self.parent.configure(fg_color="transparent")
        
        self.setup_ui()
        
        # Отслеживаем изменение темы
        self.settings_vars['theme'].trace_add('write', self.on_theme_changed)
    
    def setup_ui(self):
        """Создание интерфейса вкладки"""
        # --- ИЗМЕНЕНИЕ: Создаем прокручиваемую область для всего содержимого ---
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Контейнер для всего содержимого
        self.content_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        
        # Верхняя панель с информацией о городе и переключателем дней
        self.top_frame = ctk.CTkFrame(self.content_frame, corner_radius=10)
        self.top_frame.pack(fill="x", pady=(0, 20), padx=10)  # padx=10 для отступов по бокам
            
        # Информация о городе
        self.city_label = ctk.CTkLabel(
            self.top_frame,
            text="Город не выбран",
            font=("Arial", 18, "bold")
        )
        self.city_label.pack(pady=(15, 5))
        
        # Переключатель дней прогноза
        self.days_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.days_frame.pack(pady=(5, 15))
        
        days_label = ctk.CTkLabel(
            self.days_frame,
            text="Прогноз на:",
            font=("Arial", 14)
        )
        days_label.pack(side="left", padx=(0, 10))
        
        self.days_7_radio = ctk.CTkRadioButton(
            self.days_frame,
            text="7 дней",
            variable=self.forecast_days,
            value=7,
            command=self.on_days_changed
        )
        self.days_7_radio.pack(side="left", padx=10)
        
        self.days_14_radio = ctk.CTkRadioButton(
            self.days_frame,
            text="14 дней",
            variable=self.forecast_days,
            value=14,
            command=self.on_days_changed
        )
        self.days_14_radio.pack(side="left", padx=10)
        
        # Кнопка обновления
        self.update_button = ctk.CTkButton(
            self.top_frame,
            text="🔄 Обновить прогноз",
            command=self.update_forecast,
            width=150,
            height=32,
            fg_color="#4A5568",
            hover_color="#2D3748"
        )
        self.update_button.pack(pady=(0, 15))
        
         # Контейнер для карточек прогноза
        self.cards_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.cards_container.pack(fill="both", expand=True, padx=10)  # padx=10 для отступов по бокам
        
        # Здесь будут создаваться строки с карточками динамически
        self.rows = []  # Список для хранения строк
        
        # Статус
        self.status_label = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=(10, 0))
        
        # Показываем заглушку
        self.show_placeholder()
    
    def show_placeholder(self):
        """Показывает заглушку, когда город не выбран"""
        # Очищаем контейнер
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        self.rows.clear()
        
        placeholder = ctk.CTkLabel(
            self.cards_container,
            text="👆 Выберите город на вкладке 'Погода'\nдля отображения прогноза",
            font=("Arial", 16),
            text_color="gray"
        )
        placeholder.pack(expand=True, padx=50, pady=50)
    
    def set_city(self, city_info):
        """Устанавливает город для прогноза"""
        self.current_city_info = city_info
        city_name = self.weather_api.format_city_full_name(city_info)
        self.city_label.configure(text=city_name)
        
        # Автоматически загружаем прогноз
        self.update_forecast()
    
    def on_days_changed(self):
        """Обработчик изменения количества дней прогноза"""
        if self.current_city_info and self.current_forecast_data:
            self.update_forecast()
    
    def update_forecast(self):
        """Обновление прогноза"""
        if not self.current_city_info:
            self.show_status("⚠️ Сначала выберите город на вкладке 'Погода'", "orange")
            return
        
        # Блокируем кнопку
        self.update_button.configure(state="disabled", text="⏳ Загрузка...")
        self.show_status(f"🔄 Загрузка прогноза на {self.forecast_days.get()} дней...", "blue")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self.update_forecast_thread)
        thread.daemon = True
        thread.start()
    
    def update_forecast_thread(self):
        """Получение прогноза в отдельном потоке"""
        days = self.forecast_days.get()
        forecast_data = self.weather_api.get_forecast(self.current_city_info, days)
        
        if forecast_data:
            self.current_forecast_data = forecast_data
            
            # Конвертируем единицы измерения
            self.convert_forecast_units(forecast_data)
            
            # Обновляем интерфейс в главном потоке
            self.parent.after(0, self.display_forecast, forecast_data)
            self.parent.after(0, lambda: self.show_status(f"✅ Прогноз на {days} дней обновлен", "green"))
        else:
            self.parent.after(0, lambda: self.show_status("❌ Ошибка загрузки прогноза", "red"))
        
        self.parent.after(0, lambda: self.update_button.configure(state="normal", text="🔄 Обновить прогноз"))
    
    def convert_forecast_units(self, forecast_data):
        """Конвертирует единицы измерения в прогнозе"""
        if 'daily' not in forecast_data:
            return
        
        daily = forecast_data['daily']
        
        # Конвертация температуры
        temp_unit = self.settings_vars['temperature_unit'].get()
        for i in range(len(daily['temperature_2m_max'])):
            daily['temperature_2m_max'][i] = self.weather_api.convert_temperature(
                daily['temperature_2m_max'][i], temp_unit
            )
            daily['temperature_2m_min'][i] = self.weather_api.convert_temperature(
                daily['temperature_2m_min'][i], temp_unit
            )
        
        # Конвертация скорости ветра
        wind_unit = self.settings_vars['wind_speed_unit'].get()
        if 'windspeed_10m_max' in daily:
            for i in range(len(daily['windspeed_10m_max'])):
                daily['windspeed_10m_max'][i] = self.weather_api.convert_wind_speed(
                    daily['windspeed_10m_max'][i], wind_unit
                )
        
        # Конвертация осадков
        precip_unit = self.settings_vars['precipitation_unit'].get()
        if 'precipitation_sum' in daily:
            for i in range(len(daily['precipitation_sum'])):
                daily['precipitation_sum'][i] = self.weather_api.convert_precipitation(
                    daily['precipitation_sum'][i], precip_unit
                )
    
    def display_forecast(self, forecast_data):
        """Отображение прогноза с карточками в столбик (максимум 4 в строке)"""
        # Очищаем контейнер
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        self.rows.clear()
        
        if 'daily' not in forecast_data:
            error_label = ctk.CTkLabel(
                self.cards_container,
                text="❌ Нет данных для отображения",
                font=("Arial", 14),
                text_color="red"
            )
            error_label.pack(expand=True, padx=50, pady=50)
            return
        
        daily = forecast_data['daily']
        days = len(daily['time'])
        
        # Определяем единицы измерения для отображения
        temp_unit = "°F" if self.settings_vars['temperature_unit'].get() == "fahrenheit" else "°C"
        wind_unit = "м/с" if self.settings_vars['wind_speed_unit'].get() == "ms" else "км/ч"
        precip_unit = "дюймы" if self.settings_vars['precipitation_unit'].get() == "inches" else "мм"
        
        # Создаем строки по 4 карточки
        cards_per_row = 4
        num_rows = (days + cards_per_row - 1) // cards_per_row  # Округление вверх
        
        for row in range(num_rows):
            # Создаем новую строку
            row_frame = ctk.CTkFrame(self.cards_container, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            self.rows.append(row_frame)
            
            # Определяем индексы для этой строки
            start_idx = row * cards_per_row
            end_idx = min(start_idx + cards_per_row, days)
            
            # Создаем карточки для этой строки
            for i in range(start_idx, end_idx):
                # Дата
                date_str = daily['time'][i]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Форматируем дату
                today = datetime.now().date()
                if date_obj.date() == today:
                    day_name = "Сегодня"
                elif date_obj.date() == today + timedelta(days=1):
                    day_name = "Завтра"
                else:
                    # Название дня недели
                    day_name = self.get_weekday_name(date_obj.weekday())
                
                date_formatted = f"{day_name}\n{date_obj.strftime('%d.%m')}"
                
                # Код погоды и описание
                weather_code = daily['weathercode'][i]
                weather_desc = self.weather_api.get_weather_description(weather_code)
                weather_icon = self.weather_api.get_weather_icon(weather_code)
                
                # Температура
                temp_max = daily['temperature_2m_max'][i]
                temp_min = daily['temperature_2m_min'][i]
                
                # Осадки
                precip = daily['precipitation_sum'][i] if i < len(daily['precipitation_sum']) else 0
                precip_prob = daily['precipitation_probability_max'][i] if i < len(daily['precipitation_probability_max']) else 0
                
                # Ветер
                wind_speed = daily['windspeed_10m_max'][i] if 'windspeed_10m_max' in daily and i < len(daily['windspeed_10m_max']) else 0
                wind_dir = daily['winddirection_10m_dominant'][i] if 'winddirection_10m_dominant' in daily and i < len(daily['winddirection_10m_dominant']) else 0
                wind_dir_text = self.weather_api.get_wind_direction_text(wind_dir) if wind_dir else ""
                
                # Создаем карточку
                card = self.create_forecast_card(
                    row_frame,
                    date_formatted,
                    weather_icon,
                    weather_desc,
                    temp_max,
                    temp_min,
                    precip,
                    precip_prob,
                    wind_speed,
                    wind_dir_text,
                    temp_unit,
                    wind_unit,
                    precip_unit
                )
                card.pack(side="left", padx=2, fill="both", expand=True)
            
            # Если в строке меньше 4 карточек, добавляем пустые фреймы для выравнивания
            cards_in_row = end_idx - start_idx
            if cards_in_row < cards_per_row:
                for _ in range(cards_per_row - cards_in_row):
                    spacer = ctk.CTkFrame(row_frame, fg_color="transparent")
                    spacer.pack(side="left", padx=2, fill="both", expand=True)
    
    def create_forecast_card(self, parent, date, icon, description, temp_max, temp_min, 
                            precip, precip_prob, wind_speed, wind_dir, 
                            temp_unit, wind_unit, precip_unit):
        """Создание карточки прогноза на один день"""
        card = ctk.CTkFrame(parent, corner_radius=8)
        
        # Дата (жирным шрифтом)
        date_label = ctk.CTkLabel(
            card,
            text=date,
            font=("Arial", 14, "bold"),
            justify="center"
        )
        date_label.pack(pady=(12, 8))
        
        # Контейнер для иконки с центрированием
        icon_frame = ctk.CTkFrame(card, fg_color="transparent")
        icon_frame.pack(fill="x", pady=(0, 5))
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=("Arial", 42)
        )
        icon_label.pack(expand=True)
        
        # Описание погоды
        desc_label = ctk.CTkLabel(
            card,
            text=f"- {description}",
            font=("Arial", 11),
            wraplength=140,
            justify="center"
        )
        desc_label.pack(pady=(0, 8))
        
        # Температура (макс и мин отдельно)
        temp_max_label = ctk.CTkLabel(
            card,
            text=f"Макс: {temp_max:.1f} {temp_unit}",
            font=("Arial", 11)
        )
        temp_max_label.pack(pady=(0, 2))
        
        temp_min_label = ctk.CTkLabel(
            card,
            text=f"Мин: {temp_min:.1f} {temp_unit}",
            font=("Arial", 11)
        )
        temp_min_label.pack(pady=(0, 8))
        
        # Разделитель
        separator = ctk.CTkFrame(card, height=1, width=130, fg_color="gray")
        separator.pack(pady=5)
        
        # Осадки
        precip_text = f"{precip:.1f} {precip_unit}"
        if precip_prob > 0:
            precip_text += f" ({precip_prob}%)"
        
        precip_label = ctk.CTkLabel(
            card,
            text=f"💧 {precip_text}",
            font=("Arial", 11)
        )
        precip_label.pack(pady=(5, 2))
        
        # Ветер
        wind_text = f"{wind_speed:.1f} {wind_unit}"
        if wind_dir:
            wind_text += f" {wind_dir}"
        
        wind_label = ctk.CTkLabel(
            card,
            text=f"💨 {wind_text}",
            font=("Arial", 11)
        )
        wind_label.pack(pady=(2, 12))
        
        return card
    
    def get_weekday_name(self, weekday_num):
        """Получение названия дня недели по номеру"""
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        return weekdays[weekday_num]
    
    def show_status(self, message, color="green"):
        """Показывает статус"""
        theme = self.settings_vars['theme'].get()
        
        # Выбираем цвет в зависимости от темы
        if color == "green":
            text_color = "#4CAF50" if theme == "light" else "#81C784"
        elif color == "red":
            text_color = "#F44336" if theme == "light" else "#EF5350"
        elif color == "orange":
            text_color = "#FF9800" if theme == "light" else "#FFB74D"
        elif color == "blue":
            text_color = "#2196F3" if theme == "light" else "#64B5F6"
        else:
            text_color = color
        
        self.status_label.configure(text=message, text_color=text_color)
        self.status_label.after(3000, lambda: self.status_label.configure(text=""))
    
    def on_theme_changed(self, *args):
        """Обработчик изменения темы"""
        # Обновляем цвета, если нужно
        pass