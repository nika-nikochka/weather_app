# gui/tabs/tab3.py
import customtkinter as ctk
import threading
from datetime import datetime, timedelta
from tkinter import messagebox

class Tab3:
    def __init__(self, parent, weather_api=None, settings_vars=None):
        """
        parent - родительский фрейм (вкладка)
        weather_api - экземпляр класса WeatherAPI
        settings_vars - словарь с переменными настроек
        """
        self.parent = parent
        self.weather_api = weather_api
        self.settings_vars = settings_vars if settings_vars else {}
        self.current_city_info = None
        self.historical_data = None
        
        # Переменные для выбора даты
        self.current_date = datetime.now()
        self.selected_date = None
        
        # Переменная для количества лет истории
        self.history_years = ctk.IntVar(value=10)  # 10, 25 или 50 лет
        
        self.setup_ui()
        
        # Отслеживаем изменение темы
        if 'theme' in self.settings_vars:
            self.settings_vars['theme'].trace_add('write', self.on_theme_changed)
    
    def setup_ui(self):
        """Создание интерфейса вкладки"""
        # Основной контейнер
        self.main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Верхняя панель с информацией о городе и настройками
        self.top_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.top_frame.pack(fill="x", pady=(0, 10))
        
        # Информация о городе
        self.city_label = ctk.CTkLabel(
            self.top_frame,
            text="Город не выбран",
            font=("Arial", 18, "bold")
        )
        self.city_label.pack(pady=(15, 10))
        
        # Панель выбора даты
        date_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        date_frame.pack(pady=5)
        
        # Метка для даты
        date_label = ctk.CTkLabel(
            date_frame,
            text="Дата для анализа:",
            font=("Arial", 14)
        )
        date_label.pack(side="left", padx=(0, 10))
        
        # Отображение выбранной даты
        self.date_display = ctk.CTkLabel(
            date_frame,
            text=self.current_date.strftime("%d.%m.%Y"),
            font=("Arial", 14, "bold"),
            width=120
        )
        self.date_display.pack(side="left", padx=5)
        
        # Кнопки изменения даты
        prev_date_btn = ctk.CTkButton(
            date_frame,
            text="◀",
            width=30,
            height=30,
            command=self.prev_day,
            fg_color="#4A5568",
            hover_color="#2D3748"
        )
        prev_date_btn.pack(side="left", padx=2)
        
        today_btn = ctk.CTkButton(
            date_frame,
            text="Сегодня",
            width=70,
            height=30,
            command=self.today_date,
            fg_color="#4A5568",
            hover_color="#2D3748"
        )
        today_btn.pack(side="left", padx=2)
        
        next_date_btn = ctk.CTkButton(
            date_frame,
            text="▶",
            width=30,
            height=30,
            command=self.next_day,
            fg_color="#4A5568",
            hover_color="#2D3748"
        )
        next_date_btn.pack(side="left", padx=2)
        
        # Панель выбора количества лет
        years_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        years_frame.pack(pady=5)
        
        years_label = ctk.CTkLabel(
            years_frame,
            text="История за:",
            font=("Arial", 14)
        )
        years_label.pack(side="left", padx=(0, 10))
        
        # Радио-кнопки для выбора количества лет
        self.years_10_radio = ctk.CTkRadioButton(
            years_frame,
            text="10 лет",
            variable=self.history_years,
            value=10,
            command=self.on_years_changed
        )
        self.years_10_radio.pack(side="left", padx=10)
        
        self.years_25_radio = ctk.CTkRadioButton(
            years_frame,
            text="25 лет",
            variable=self.history_years,
            value=25,
            command=self.on_years_changed
        )
        self.years_25_radio.pack(side="left", padx=10)
        
        self.years_50_radio = ctk.CTkRadioButton(
            years_frame,
            text="50 лет",
            variable=self.history_years,
            value=50,
            command=self.on_years_changed
        )
        self.years_50_radio.pack(side="left", padx=10)
        
        # Кнопка обновления
        self.update_button = ctk.CTkButton(
            self.top_frame,
            text="📊 Загрузить исторические данные",
            command=self.load_historical_data,
            width=200,
            height=35,
            fg_color="#4A5568",
            hover_color="#2D3748"
        )
        self.update_button.pack(pady=(10, 15))
        
        # Основная область с прокруткой для отображения данных
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame, corner_radius=10)
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Контейнер для содержимого
        self.content_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True, padx=10, pady=10)
        
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
        for widget in self.content_container.winfo_children():
            widget.destroy()
        
        placeholder = ctk.CTkLabel(
            self.content_container,
            text="👆 Выберите город на вкладке 'Погода'\nдля отображения исторических данных",
            font=("Arial", 16),
            text_color="gray"
        )
        placeholder.pack(expand=True, padx=50, pady=50)
    
    def set_city(self, city_info):
        """Устанавливает город для исторических данных"""
        self.current_city_info = city_info
        city_name = self.weather_api.format_city_full_name(city_info) if self.weather_api else "Город"
        self.city_label.configure(text=city_name)
        
        # Автоматически загружаем исторические данные
        self.load_historical_data()
    
    def prev_day(self):
        """Переход к предыдущему дню"""
        self.current_date = self.current_date - timedelta(days=1)
        self.update_date_display()
        if self.current_city_info:
            self.load_historical_data()
    
    def next_day(self):
        """Переход к следующему дню"""
        self.current_date = self.current_date + timedelta(days=1)
        # Не даем заглянуть в будущее
        if self.current_date > datetime.now():
            self.current_date = datetime.now()
        self.update_date_display()
        if self.current_city_info:
            self.load_historical_data()
    
    def today_date(self):
        """Возврат к сегодняшней дате"""
        self.current_date = datetime.now()
        self.update_date_display()
        if self.current_city_info:
            self.load_historical_data()
    
    def update_date_display(self):
        """Обновляет отображение даты"""
        self.date_display.configure(text=self.current_date.strftime("%d.%m.%Y"))
    
    def on_years_changed(self):
        """Обработчик изменения количества лет истории"""
        if self.current_city_info:
            self.load_historical_data()
    
    def load_historical_data(self):
        """Загрузка исторических данных"""
        if not self.current_city_info:
            self.show_status("⚠️ Сначала выберите город на вкладке 'Погода'", "orange")
            return
        
        if not self.weather_api:
            self.show_status("❌ Ошибка: API погоды не доступен", "red")
            return
        
        # Блокируем кнопку
        self.update_button.configure(state="disabled", text="⏳ Загрузка...")
        years = self.history_years.get()
        date_str = self.current_date.strftime("%Y-%m-%d")
        self.show_status(f"🔄 Загрузка исторических данных за {years} лет для даты {date_str}...", "blue")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self.load_historical_data_thread, args=(years, date_str))
        thread.daemon = True
        thread.start()
    
    def load_historical_data_thread(self, years, date_str):
        """Получение исторических данных в отдельном потоке"""
        historical_data = self.weather_api.get_historical_data(
            self.current_city_info, 
            date_str, 
            years
        )
        
        if historical_data and historical_data.get('historical_records'):
            self.historical_data = historical_data
            
            # Конвертируем единицы измерения
            self.convert_historical_units(historical_data)
            
            # Обновляем интерфейс в главном потоке
            self.parent.after(0, self.display_historical_data, historical_data)
            self.parent.after(0, lambda: self.show_status(
                f"✅ Исторические данные за {len(historical_data['historical_records'])} лет загружены", 
                "green"
            ))
        else:
            self.parent.after(0, lambda: self.show_status(
                f"❌ Не удалось загрузить исторические данные за {date_str}", 
                "red"
            ))
            self.parent.after(0, self.show_no_data)
        
        self.parent.after(0, lambda: self.update_button.configure(
            state="normal", 
            text="📊 Загрузить исторические данные"
        ))
    
    def convert_historical_units(self, historical_data):
        """Конвертирует единицы измерения в исторических данных"""
        if 'historical_records' not in historical_data:
            return
        
        # Конвертация температуры
        temp_unit = self.settings_vars.get('temperature_unit', ctk.StringVar(value="celsius")).get()
        
        for record in historical_data['historical_records']:
            record['temperature_max'] = self.weather_api.convert_temperature(
                record['temperature_max'], temp_unit
            )
            record['temperature_min'] = self.weather_api.convert_temperature(
                record['temperature_min'], temp_unit
            )
        
        # Конвертируем также статистику
        if 'statistics' in historical_data:
            stats = historical_data['statistics']
            if 'avg_temperature_max' in stats:
                stats['avg_temperature_max'] = self.weather_api.convert_temperature(
                    stats['avg_temperature_max'], temp_unit
                )
            if 'avg_temperature_min' in stats:
                stats['avg_temperature_min'] = self.weather_api.convert_temperature(
                    stats['avg_temperature_min'], temp_unit
                )
            if 'max_temperature_absolute' in stats:
                stats['max_temperature_absolute'] = self.weather_api.convert_temperature(
                    stats['max_temperature_absolute'], temp_unit
                )
            if 'min_temperature_absolute' in stats:
                stats['min_temperature_absolute'] = self.weather_api.convert_temperature(
                    stats['min_temperature_absolute'], temp_unit
                )
    
    def display_historical_data(self, historical_data):
        """Отображение исторических данных"""
        # Очищаем контейнер
        for widget in self.content_container.winfo_children():
            widget.destroy()
        
        if not historical_data or 'historical_records' not in historical_data:
            self.show_no_data()
            return
        
        # Определяем единицы измерения
        temp_unit = "°F" if self.settings_vars.get('temperature_unit', ctk.StringVar(value="celsius")).get() == "fahrenheit" else "°C"
        
        records = historical_data['historical_records']
        target_date = datetime.strptime(historical_data['target_date'], '%Y-%m-%d')
        date_str = target_date.strftime('%d.%m')
        
        # Заголовок
        title = ctk.CTkLabel(
            self.content_container,
            text=f"📅 Исторические данные для {date_str}",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(10, 15))
        
        # Статистика (если есть)
        if 'statistics' in historical_data:
            stats = historical_data['statistics']
            stats_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
            stats_frame.pack(fill="x", padx=20, pady=10)
            
            stats_title = ctk.CTkLabel(
                stats_frame,
                text="📊 Статистика за весь период",
                font=("Arial", 16, "bold")
            )
            stats_title.pack(pady=(10, 5))
            
            # Создаем сетку для статистики
            stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stats_grid.pack(padx=20, pady=10)
            
            # Средние температуры
            avg_temp_label = ctk.CTkLabel(
                stats_grid,
                text=f"Средняя max: {stats['avg_temperature_max']:.1f}{temp_unit}   |   Средняя min: {stats['avg_temperature_min']:.1f}{temp_unit}",
                font=("Arial", 14)
            )
            avg_temp_label.pack(pady=2)
            
            # Абсолютные рекорды
            record_label = ctk.CTkLabel(
                stats_grid,
                text=f"Абсолютный max: {stats['max_temperature_absolute']:.1f}{temp_unit}   |   Абсолютный min: {stats['min_temperature_absolute']:.1f}{temp_unit}",
                font=("Arial", 14, "bold")
            )
            record_label.pack(pady=2)
            
            # Средние осадки
            if 'avg_precipitation' in stats:
                precip_label = ctk.CTkLabel(
                    stats_grid,
                    text=f"Средние осадки: {stats['avg_precipitation']:.1f} мм",
                    font=("Arial", 14)
                )
                precip_label.pack(pady=2)
            
            # Количество лет с данными
            years_count = ctk.CTkLabel(
                stats_grid,
                text=f"Данные за {stats['years_with_data']} лет",
                font=("Arial", 12),
                text_color="gray"
            )
            years_count.pack(pady=2)
        
        # Заголовок таблицы
        table_header = ctk.CTkFrame(self.content_container, corner_radius=5, fg_color="#2B2B2B")
        table_header.pack(fill="x", padx=20, pady=(20, 0))
        
        # Колонки
        col_year = ctk.CTkLabel(table_header, text="Год", width=80, font=("Arial", 12, "bold"))
        col_year.pack(side="left", padx=5)
        
        col_temp_max = ctk.CTkLabel(table_header, text=f"Макс, {temp_unit}", width=100, font=("Arial", 12, "bold"))
        col_temp_max.pack(side="left", padx=5)
        
        col_temp_min = ctk.CTkLabel(table_header, text=f"Мин, {temp_unit}", width=100, font=("Arial", 12, "bold"))
        col_temp_min.pack(side="left", padx=5)
        
        col_weather = ctk.CTkLabel(table_header, text="Погода", width=150, font=("Arial", 12, "bold"))
        col_weather.pack(side="left", padx=5)
        
        col_precip = ctk.CTkLabel(table_header, text="Осадки, мм", width=100, font=("Arial", 12, "bold"))
        col_precip.pack(side="left", padx=5)
        
        # Контейнер для записей с прокруткой
        records_container = ctk.CTkScrollableFrame(
            self.content_container, 
            height=300,
            corner_radius=5
        )
        records_container.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Добавляем записи
        for i, record in enumerate(records):
            # Чередуем цвета строк
            row_color = "#3A3A3A" if i % 2 == 0 else "#2D2D2D"
            
            row_frame = ctk.CTkFrame(records_container, fg_color=row_color, height=35)
            row_frame.pack(fill="x", pady=1)
            row_frame.pack_propagate(False)
            
            # Год
            year_label = ctk.CTkLabel(
                row_frame, 
                text=str(record['year']), 
                width=80,
                font=("Arial", 11)
            )
            year_label.pack(side="left", padx=5)
            
            # Макс температура
            temp_max_label = ctk.CTkLabel(
                row_frame, 
                text=f"{record['temperature_max']:.1f}", 
                width=100,
                font=("Arial", 11)
            )
            temp_max_label.pack(side="left", padx=5)
            
            # Мин температура
            temp_min_label = ctk.CTkLabel(
                row_frame, 
                text=f"{record['temperature_min']:.1f}", 
                width=100,
                font=("Arial", 11)
            )
            temp_min_label.pack(side="left", padx=5)
            
            # Погода (иконка + описание)
            weather_text = f"{record.get('weather_icon', '')} {record.get('weather_description', '')[:15]}"
            weather_label = ctk.CTkLabel(
                row_frame, 
                text=weather_text, 
                width=150,
                font=("Arial", 11),
                anchor="w"
            )
            weather_label.pack(side="left", padx=5)
            
            # Осадки
            precip_label = ctk.CTkLabel(
                row_frame, 
                text=f"{record['precipitation']:.1f}", 
                width=100,
                font=("Arial", 11)
            )
            precip_label.pack(side="left", padx=5)
        
        # Информация о конвертации
        if 'temperature_unit' in self.settings_vars:
            info_label = ctk.CTkLabel(
                self.content_container,
                text=f"Единицы измерения: {temp_unit}",
                font=("Arial", 10),
                text_color="gray"
            )
            info_label.pack(pady=(5, 10))
    
    def show_no_data(self):
        """Показывает сообщение об отсутствии данных"""
        for widget in self.content_container.winfo_children():
            widget.destroy()
        
        no_data_label = ctk.CTkLabel(
            self.content_container,
            text="❌ Нет исторических данных для выбранной даты",
            font=("Arial", 16),
            text_color="red"
        )
        no_data_label.pack(expand=True, padx=50, pady=50)
    
    def show_status(self, message, color="green"):
        """Показывает статус"""
        theme = self.settings_vars.get('theme', ctk.StringVar(value="dark")).get()
        
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
        self.status_label.after(5000, lambda: self.status_label.configure(text=""))
    
    def on_theme_changed(self, *args):
        """Обработчик изменения темы"""
        # Обновляем цвета, если нужно
        pass