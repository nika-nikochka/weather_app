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
        
        self.setup_ui()
        
        # Отслеживаем изменение темы
        self.settings_vars['theme'].trace_add('write', self.on_theme_changed)
    
    def setup_ui(self):
        """Создание интерфейса вкладки"""
        # Основной контейнер
        self.main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Верхняя панель с информацией о городе и переключателем дней
        self.top_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.top_frame.pack(fill="x", pady=(0, 10))
        
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
        
        # --- ИЗМЕНЕНИЕ: Горизонтальный скроллинг ---
        # Создаем фрейм с горизонтальной прокруткой
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame, 
            corner_radius=10,
            orientation="horizontal",  # Горизонтальная ориентация
            height=200  # Фиксированная высота для горизонтального скролла
        )
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Контейнер для карточек (будет заполняться динамически)
        self.cards_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.cards_container.pack(side="left", fill="y", padx=5, pady=5)
        
        # Статус
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=(5, 0))
        
        # Показываем заглушку
        self.show_placeholder()
    
    def show_placeholder(self):
        """Показывает заглушку, когда город не выбран"""
        # Очищаем контейнер
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        
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
        """Отображение прогноза в виде карточек (горизонтально)"""
        # Очищаем контейнер
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        
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
        
        # --- ИЗМЕНЕНИЕ: Карточки располагаются горизонтально ---
        # Создаем карточки для каждого дня и размещаем их горизонтально
        for i in range(days):
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
            # --- ИЗМЕНЕНИЕ: Размещаем карточки горизонтально (слева направо) ---
            card.pack(side="left", padx=5, pady=5, fill="y")
    
    def create_forecast_card(self, date, icon, description, temp_max, temp_min, 
                            precip, precip_prob, wind_speed, wind_dir, 
                            temp_unit, wind_unit, precip_unit):
        """Создание карточки прогноза на один день (компактный дизайн для горизонтального расположения)"""
        card = ctk.CTkFrame(self.cards_container, corner_radius=8, width=150)
        card.pack_propagate(False)  # Запрещаем изменение размера
        
        # Дата (теперь с переносом строки)
        date_label = ctk.CTkLabel(
            card,
            text=date,
            font=("Arial", 12, "bold"),
            justify="center"
        )
        date_label.pack(pady=(8, 2))
        
        # Иконка погоды
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=("Arial", 32)
        )
        icon_label.pack()
        
        # Описание погоды (сокращенное)
        short_desc = description[:10] + "..." if len(description) > 10 else description
        desc_label = ctk.CTkLabel(
            card,
            text=short_desc,
            font=("Arial", 10)
        )
        desc_label.pack()
        
        # Температура
        temp_label = ctk.CTkLabel(
            card,
            text=f"{temp_max}↑ / {temp_min}↓",
            font=("Arial", 11, "bold")
        )
        temp_label.pack(pady=(2, 0))
        
        temp_unit_label = ctk.CTkLabel(
            card,
            text=temp_unit,
            font=("Arial", 9)
        )
        temp_unit_label.pack()
        
        # Разделитель
        separator = ctk.CTkFrame(card, height=1, width=120, fg_color="gray")
        separator.pack(pady=5)
        
        # Осадки
        precip_text = f"💧 {precip} {precip_unit}"
        if precip_prob > 0:
            precip_text += f"\n({precip_prob}%)"
        
        precip_label = ctk.CTkLabel(
            card,
            text=precip_text,
            font=("Arial", 9),
            justify="center"
        )
        precip_label.pack()
        
        # Ветер
        wind_text = f"💨 {wind_speed} {wind_unit}"
        if wind_dir:
            wind_text += f" {wind_dir}"
        
        wind_label = ctk.CTkLabel(
            card,
            text=wind_text,
            font=("Arial", 9),
            justify="center"
        )
        wind_label.pack(pady=(0, 8))
        
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
