# gui/tabs/weather_tab.py
import customtkinter as ctk
from datetime import datetime
import tkinter as tk
from tkinter import Toplevel

class WeatherTab:
    def __init__(self, parent, weather_api, callbacks):
        """
        parent - родительский фрейм (вкладка)
        weather_api - экземпляр WeatherAPI
        callbacks - словарь с функциями обратного вызова
        """
        self.parent = parent
        self.weather_api = weather_api
        self.callbacks = callbacks
        
        # Переменные для виджетов
        self.city_entry = None
        self.search_button = None
        self.city_label = None
        self.temp_label = None
        self.time_label = None
        self.status_label = None
        self.current_theme = "light"
        
        # Новые переменные для отображения данных
        self.wind_speed_label = None
        self.feels_like_label = None
        self.humidity_label = None
        self.wind_direction_label = None
        self.sunrise_label = None
        self.sunset_label = None
        self.pressure_label = None
        
        # Переменные для рекомендаций
        self.clothing_button = None
        self.current_weather_data = None
        self.current_city_name = None
        self.recommendation_window = None  # Для хранения ссылки на окно
        
        # Переменные для выпадающего списка
        self.dropdown_frame = None
        self.dropdown_visible = False
        self.search_after_id = None
        self.last_search_text = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        # Устанавливаем прозрачный фон родительского фрейма
        self.parent.configure(fg_color="transparent")
        
        # --- ИЗМЕНЕНИЕ: Создаем прокручиваемую область для всего содержимого ---
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Контейнер для всего содержимого внутри прокрутки
        self.content_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Верхняя панель с поиском
        search_frame = ctk.CTkFrame(self.content_frame)
        search_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Контейнер для поля ввода и выпадающего списка
        entry_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        entry_container.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        # Поле ввода города
        self.city_entry = ctk.CTkEntry(
            entry_container, 
            placeholder_text="Введите название города на русском...",
            height=40,
            font=("Arial", 14),
            border_width=2,
            border_color="#CCCCCC"
        )
        self.city_entry.pack(fill="x", expand=True)
        
        # Привязываем события для поиска по мере ввода
        self.city_entry.bind('<KeyRelease>', self.on_key_release)
        self.city_entry.bind('<FocusOut>', self.on_focus_out)
        self.city_entry.bind('<Down>', self.on_arrow_down)
        
        # Кнопка поиска - КРАСНАЯ
        self.search_button = ctk.CTkButton(
            search_frame,
            text="🔍 Найти",
            height=40,
            width=120,
            command=self.callbacks['search'],
            font=("Arial", 14, "bold"),
            fg_color="#E53E3E",
            hover_color="#C53030",
            text_color="white",
            corner_radius=8
        )
        self.search_button.pack(side="right", padx=(5, 10), pady=10)
        
        # Фрейм для отображения погоды
        self.weather_frame = ctk.CTkFrame(self.content_frame)
        self.weather_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Информация о городе
        self.city_label = ctk.CTkLabel(
            self.weather_frame,
            text="Введите город для получения информации",
            font=("Arial", 24, "bold")
        )
        self.city_label.pack(pady=(30, 10))
        
        # Температура
        self.temp_label = ctk.CTkLabel(
            self.weather_frame,
            text="",
            font=("Arial", 48),
        )
        self.temp_label.pack(pady=(5, 20))
        
        # Основной контейнер для всех параметров погоды
        main_params_frame = ctk.CTkFrame(self.weather_frame, fg_color="transparent")
        main_params_frame.pack(fill="x", padx=20, pady=10)
        
        # Первая строка параметров (ветер, ощущается как, влажность)
        row1_frame = ctk.CTkFrame(main_params_frame, fg_color="transparent")
        row1_frame.pack(fill="x", pady=5)
        
        # Ветер
        wind_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        wind_frame.pack(side="left", expand=True, fill="x", padx=5)
        
        wind_title = ctk.CTkLabel(
            wind_frame,
            text="💨 Ветер",
            font=("Arial", 14)
        )
        wind_title.pack()
        
        self.wind_speed_label = ctk.CTkLabel(
            wind_frame,
            text="--",
            font=("Arial", 16, "bold")
        )
        self.wind_speed_label.pack()
        
        # Ощущается как
        feels_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        feels_frame.pack(side="left", expand=True, fill="x", padx=5)
        
        feels_title = ctk.CTkLabel(
            feels_frame,
            text="🌡️ Ощущается",
            font=("Arial", 14)
        )
        feels_title.pack()
        
        self.feels_like_label = ctk.CTkLabel(
            feels_frame,
            text="--",
            font=("Arial", 16, "bold")
        )
        self.feels_like_label.pack()
        
        # Влажность
        humidity_frame = ctk.CTkFrame(row1_frame, fg_color="transparent")
        humidity_frame.pack(side="left", expand=True, fill="x", padx=5)
        
        humidity_title = ctk.CTkLabel(
            humidity_frame,
            text="💧 Влажность",
            font=("Arial", 14)
        )
        humidity_title.pack()
        
        self.humidity_label = ctk.CTkLabel(
            humidity_frame,
            text="--",
            font=("Arial", 16, "bold")
        )
        self.humidity_label.pack()
        
        # Вторая строка параметров (направление, восход, закат, давление)
        row2_frame = ctk.CTkFrame(main_params_frame, fg_color="transparent")
        row2_frame.pack(fill="x", pady=5)
        
        # Направление ветра
        direction_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        direction_frame.pack(side="left", expand=True, fill="x", padx=5)
        
        direction_title = ctk.CTkLabel(
            direction_frame,
            text="🧭 Направление",
            font=("Arial", 14)
        )
        direction_title.pack()
        
        self.wind_direction_label = ctk.CTkLabel(
            direction_frame,
            text="--",
            font=("Arial", 16, "bold")
        )
        self.wind_direction_label.pack()
        
        # Восход
        sunrise_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        sunrise_frame.pack(side="left", expand=True, fill="x", padx=5)
        
        sunrise_title = ctk.CTkLabel(
            sunrise_frame,
            text="🌅 Восход",
            font=("Arial", 14)
        )
        sunrise_title.pack()
        
        self.sunrise_label = ctk.CTkLabel(
            sunrise_frame,
            text="--",
            font=("Arial", 16, "bold")
        )
        self.sunrise_label.pack()
        
        # Закат
        sunset_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        sunset_frame.pack(side="left", expand=True, fill="x", padx=5)
        
        sunset_title = ctk.CTkLabel(
            sunset_frame,
            text="🌇 Закат",
            font=("Arial", 14)
        )
        sunset_title.pack()
        
        self.sunset_label = ctk.CTkLabel(
            sunset_frame,
            text="--",
            font=("Arial", 16, "bold")
        )
        self.sunset_label.pack()
        
        # Давление
        pressure_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        pressure_frame.pack(side="left", expand=True, fill="x", padx=5)
        
        pressure_title = ctk.CTkLabel(
            pressure_frame,
            text="📊 Давление",
            font=("Arial", 14)
        )
        pressure_title.pack()
        
        self.pressure_label = ctk.CTkLabel(
            pressure_frame,
            text="--",
            font=("Arial", 16, "bold")
        )
        self.pressure_label.pack()
        
        # Фрейм для кнопки рекомендаций
        button_frame = ctk.CTkFrame(self.weather_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=15)
        
        # Кнопка "Рекомендации по одежде" - синяя
        self.clothing_button = ctk.CTkButton(
            button_frame,
            text="👔 Рекомендации по одежде",
            height=40,
            width=250,
            command=self.show_clothing_recommendation_window,
            font=("Arial", 14, "bold"),
            fg_color="#3182CE",
            hover_color="#2C5282",
            text_color="white",
            corner_radius=8,
            state="disabled"
        )
        self.clothing_button.pack(pady=5)
        
        # Дополнительная информация (время обновления и т.д.)
        self.time_label = ctk.CTkLabel(
            self.weather_frame,
            text="",
            font=("Arial", 10),
            text_color="gray"
        )
        self.time_label.pack(side="bottom", pady=10)
        
        # Статус загрузки
        self.status_label = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=("Arial", 12),
        )
        self.status_label.pack(pady=(0, 10))
    
    def show_clothing_recommendation_window(self):
        """Показывает отдельное окно с рекомендациями по одежде"""
        
        # Если окно уже открыто, просто активируем его
        if self.recommendation_window and self.recommendation_window.winfo_exists():
            self.recommendation_window.lift()
            self.recommendation_window.focus_force()
            return
        
        # Создаем новое окно
        self.recommendation_window = ctk.CTkToplevel(self.parent)
        self.recommendation_window.title(f"👔 Рекомендации по одежде - {self.current_city_name}")
        self.recommendation_window.geometry("500x500")
        self.recommendation_window.resizable(False, False)
        
        # Делаем окно модальным (блокирует основное окно)
        self.recommendation_window.transient(self.parent)
        self.recommendation_window.grab_set()
        
        # Настраиваем цвета в зависимости от темы
        if self.current_theme == "dark":
            bg_color = "#2b2b2b"
            text_color = "white"
            frame_color = "#333333"
            secondary_color = "#CCCCCC"
        else:
            bg_color = "white"
            text_color = "black"
            frame_color = "#f0f0f0"
            secondary_color = "#666666"
        
        self.recommendation_window.configure(fg_color=bg_color)
        
        # Заголовок с городом
        header_frame = ctk.CTkFrame(self.recommendation_window, fg_color=frame_color, height=60)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        city_header = ctk.CTkLabel(
            header_frame,
            text=f"🌍 {self.current_city_name}",
            font=("Arial", 18, "bold"),
            text_color=text_color
        )
        city_header.pack(expand=True)
        
        # Краткая сводка погоды
        summary_frame = ctk.CTkFrame(self.recommendation_window, fg_color="transparent")
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        if self.current_weather_data:
            current = self.current_weather_data.get('current_weather', {})
            temp = current.get('temperature', 0)
            feels_like = current.get('apparent_temperature', temp)
            wind = current.get('windspeed', 0)
            humidity = current.get('relative_humidity', 50)
            
            # Получаем описание погоды
            weather_desc = "Неизвестно"
            if 'weathercode' in current:
                weather_desc = self.weather_api.get_weather_description(current['weathercode'])
                weather_icon = self.weather_api.get_weather_icon(current['weathercode'])
            else:
                weather_icon = "🌡️"
            
            summary_text = f"{weather_icon} {weather_desc}\n"
            summary_text += f"Температура: {temp:.1f}°C | Ощущается: {feels_like:.1f}°C\n"
            summary_text += f"Ветер: {wind:.1f} км/ч | Влажность: {humidity}%"
            
            weather_summary = ctk.CTkLabel(
                summary_frame,
                text=summary_text,
                font=("Arial", 12),
                text_color=secondary_color,
                justify="center"
            )
            weather_summary.pack(pady=5)
        
        # Основной контейнер для рекомендаций
        main_frame = ctk.CTkFrame(self.recommendation_window, fg_color=frame_color)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Текст рекомендаций
        recommendation_text = self.generate_clothing_recommendation(
            temp, feels_like, wind, humidity
        )
        
        # Создаем текстовое поле с прокруткой для длинных рекомендаций
        textbox = ctk.CTkTextbox(
            main_frame,
            wrap="word",
            font=("Arial", 13),
            text_color=text_color,
            fg_color="transparent",
            border_width=0
        )
        textbox.pack(padx=20, pady=20, fill="both", expand=True)
        textbox.insert("1.0", recommendation_text)
        textbox.configure(state="disabled")  # Делаем только для чтения
        
        # Кнопка закрытия
        close_button = ctk.CTkButton(
            self.recommendation_window,
            text="Закрыть",
            command=self.close_recommendation_window,
            height=35,
            width=120,
            fg_color="#E53E3E",
            hover_color="#C53030",
            text_color="white"
        )
        close_button.pack(pady=10)
        
        # Настройка обработчика закрытия окна
        self.recommendation_window.protocol("WM_DELETE_WINDOW", self.close_recommendation_window)
    
    def close_recommendation_window(self):
        """Закрывает окно с рекомендациями"""
        if self.recommendation_window:
            self.recommendation_window.destroy()
            self.recommendation_window = None
    
    def generate_clothing_recommendation(self, temp, feels_like, wind_speed, humidity):
        """Генерирует рекомендации по одежде на основе погоды"""
        
        # Определяем текущее время суток
        current_hour = datetime.now().hour
        if 6 <= current_hour < 12:
            time_of_day = "утро"
        elif 12 <= current_hour < 18:
            time_of_day = "день"
        elif 18 <= current_hour < 23:
            time_of_day = "вечер"
        else:
            time_of_day = "ночь"
        
        recommendation = f"🏙️ Сейчас {time_of_day}\n\n"
        
        # Базовая рекомендация по температуре
        if temp <= -25:
            recommendation += "❄️❄️❄️ КАТАСТРОФИЧЕСКИ ХОЛОДНО ❄️❄️❄️\n\n"
            recommendation += "ОДЕЖДА:\n"
            recommendation += "• Термобелье (верх и низ)\n"
            recommendation += "• Утепленные штаны/комбинезон\n"
            recommendation += "• Пуховик (максимальное утепление)\n"
            recommendation += "• Шапка-ушанка + балаклава\n"
            recommendation += "• Шерстяной шарф\n"
            recommendation += "• Варежки с мехом внутри\n"
            recommendation += "• Зимние сапоги с мехом (-30°C)\n\n"
            recommendation += "⚠️ ВНИМАНИЕ: Ограничьте пребывание на улице! Риск обморожения!"
            
        elif temp <= -20:
            recommendation += "❄️❄️ ЭКСТРЕМАЛЬНО ХОЛОДНО ❄️❄️\n\n"
            recommendation += "ОДЕЖДА:\n"
            recommendation += "• Термобелье (верх и низ)\n"
            recommendation += "• Утепленные штаны\n"
            recommendation += "• Пуховик\n"
            recommendation += "• Шапка-ушанка\n"
            recommendation += "• Шарф\n"
            recommendation += "• Варежки/перчатки\n"
            recommendation += "• Зимние сапоги с мехом\n\n"
            recommendation += "⚠️ Ограничьте пребывание на улице! Возможны обморожения."
            
        elif temp <= -10:
            recommendation += "❄️ ОЧЕНЬ ХОЛОДНО\n\n"
            recommendation += "ОДЕЖДА:\n"
            recommendation += "• Термобелье\n"
            recommendation += "• Теплые штаны/джинсы\n"
            recommendation += "• Зимняя куртка\n"
            recommendation += "• Шапка\n"
            recommendation += "• Шарф\n"
            recommendation += "• Перчатки\n"
            recommendation += "• Зимняя обувь\n\n"
            recommendation += "💡 Защищайте открытые участки кожи."
            
        elif temp <= 0:
            recommendation += "⛄ ХОЛОДНО\n\n"
            recommendation += "ОДЕЖДА:\n"
            recommendation += "• Свитер/кофта\n"
            recommendation += "• Теплые штаны/джинсы\n"
            recommendation += "• Зимняя куртка\n"
            recommendation += "• Шапка\n"
            recommendation += "• Перчатки\n"
            recommendation += "• Зимняя обувь\n\n"
            recommendation += "💡 Не забудьте шапку и перчатки!"
            
        elif temp <= 5:
            recommendation += "🌬️ ПРОХЛАДНО\n\n"
            recommendation += "ОДЕЖДА:\n"
            recommendation += "• Кофта/свитер\n"
            recommendation += "• Джинсы\n"
            recommendation += "• Осенняя куртка/пальто\n"
            recommendation += "• Шарф по желанию\n"
            recommendation += "• Непромокаемая обувь\n\n"
            recommendation += "💡 Возможны осадки - возьмите зонт!"
            
        elif temp <= 10:
            recommendation += "🍂 СВЕЖО\n\n"
            recommendation += "ОДЕЖДА:\n"
            recommendation += "• Длинный рукав\n"
            recommendation += "• Джинсы/брюки\n"
            recommendation += "• Ветровка/легкая куртка\n"
            recommendation += "• Кроссовки\n\n"
            recommendation += "💡 Утром и вечером может быть прохладнее."
            
        elif temp <= 15:
            recommendation += "🌤️ ПРОХЛАДНО\n\n"
            recommendation += "ОДЕЖДА:\n"
            recommendation += "• Футболка + легкая кофта\n"
            recommendation += "• Джинсы/брюки\n"
            recommendation += "• Легкая куртка на вечер\n"
            recommendation += "• Кеды/кроссовки\n\n"
            recommendation += "💡 Одевайтесь слоями - днем может потеплеть."
            
        elif temp <= 20:
            recommendation += "☀️ ТЕПЛО\n\n"
            recommendation += "ОДЕЖДА:\n"
            recommendation += "• Футболка\n"
            recommendation += "• Шорты/легкие брюки\n"
            recommendation += "• Кроссовки/кеды\n"
            recommendation += "• Легкая ветровка на вечер\n\n"
            recommendation += "💡 Отличная погода для прогулок!"
            
        elif temp <= 25:
            recommendation += "🌞 ТЕПЛО\n\n"
            recommendation += "ОДЕЖДА:\n"
            recommendation += "• Футболка/майка\n"
            recommendation += "• Шорты/юбка\n"
            recommendation += "• Кеды/сандалии\n"
            recommendation += "• Кепка/панама\n\n"
            recommendation += "💡 Не забывайте про головной убор и солнцезащитный крем!"
            
        elif temp <= 30:
            recommendation += "🔥 ЖАРКО\n\n"
            recommendation += "ОДЕЖДА:\n"
            recommendation += "• Майка/топ\n"
            recommendation += "• Шорты/легкая юбка\n"
            recommendation += "• Сандалии/шлепанцы\n"
            recommendation += "• Панама/кепка\n"
            recommendation += "• Солнцезащитные очки\n\n"
            recommendation += "💡 Пейте больше воды! Избегайте прямых солнечных лучей."
            
        else:
            recommendation += "🥵 ОЧЕНЬ ЖАРКО!\n\n"
            recommendation += "ОДЕЖДА:\n"
            recommendation += "• Легкая светлая одежда\n"
            recommendation += "• Шорты\n"
            recommendation += "• Открытая обувь\n"
            recommendation += "• Головной убор\n"
            recommendation += "• Солнцезащитные очки\n\n"
            recommendation += "💡 Оставайтесь в тени! Используйте кондиционер."
        
        # Дополнительные рекомендации
        recommendation += "\n📊 ДОПОЛНИТЕЛЬНЫЕ ФАКТОРЫ:\n"
        
        # Ощущаемая температура
        if feels_like < temp - 3:
            recommendation += f"• 🌬️ Ветер усиливает охлаждение: ощущается как {feels_like:.1f}°C\n"
            recommendation += "  → Добавьте ветрозащитную одежду\n"
        elif feels_like > temp + 3:
            recommendation += f"• 💧 Влажность усиливает жару: ощущается как {feels_like:.1f}°C\n"
            recommendation += "  → Выбирайте дышащие материалы\n"
        
        # Ветер
        if wind_speed > 40:
            recommendation += "• 🌀 УРАГАННЫЙ ВЕТЕР! Будьте предельно осторожны!\n"
        elif wind_speed > 30:
            recommendation += "• 💨 Штормовой ветер. Наденьте непродуваемую одежду\n"
        elif wind_speed > 20:
            recommendation += "• 💨 Сильный ветер. Желательна ветрозащитная куртка\n"
        elif wind_speed > 10:
            recommendation += "• 💨 Ветрено. Застегните куртку\n"
        
        # Влажность
        if humidity > 85 and temp > 20:
            recommendation += "• 💧 Очень душно. Одежда из натуральных тканей обязательна\n"
        elif humidity > 70 and temp > 25:
            recommendation += "• 💧 Повышенная влажность. Выбирайте дышащие ткани\n"
        elif humidity < 30:
            recommendation += "• 💧 Низкая влажность. Увлажняйте кожу и пейте больше воды\n"
        
        # Время суток
        if time_of_day == "ночь":
            recommendation += "• 🌙 Ночью температура может упасть. Возьмите кофту\n"
        elif time_of_day == "утро":
            recommendation += "• 🌅 Утром прохладно, днем потеплеет. Одевайтесь слоями\n"
        elif time_of_day == "вечер":
            recommendation += "• 🌆 Вечером станет прохладнее. Не забудьте кофту\n"
        
        return recommendation
    
    def update_theme_colors(self, theme):
        """Обновление цветов в соответствии с выбранной темой"""
        self.current_theme = theme
        
        # Определяем цвета в зависимости от темы
        if theme == "dark":
            text_color = "white"
            border_color = "#555555"
            entry_text_color = "white"
            placeholder_color = "gray"
            time_color = "lightgray"
            status_color = "white"
            clothing_button_bg = "#3182CE"
            clothing_button_hover = "#2C5282"
        else:  # light
            text_color = "black"
            border_color = "#CCCCCC"
            entry_text_color = "black"
            placeholder_color = "gray"
            time_color = "gray"
            status_color = "black"
            clothing_button_bg = "#3182CE"
            clothing_button_hover = "#2C5282"
        
        # Обновляем поле ввода
        if self.city_entry:
            self.city_entry.configure(
                border_color=border_color,
                text_color=entry_text_color,
                placeholder_text_color=placeholder_color
            )
        
        # Обновляем текстовые метки
        labels_to_update = [
            self.city_label,
            self.temp_label,
            self.wind_speed_label,
            self.feels_like_label,
            self.humidity_label,
            self.wind_direction_label,
            self.sunrise_label,
            self.sunset_label,
            self.pressure_label
        ]
        
        for label in labels_to_update:
            if label:
                label.configure(text_color=text_color)
        
        if self.time_label:
            self.time_label.configure(text_color=time_color)
        if self.status_label:
            self.status_label.configure(text_color=status_color)
        
        # Обновляем цвета кнопок
        if self.search_button:
            self.search_button.configure(
                fg_color="#E53E3E",
                hover_color="#C53030",
                text_color="white"
            )
        
        if self.clothing_button:
            self.clothing_button.configure(
                fg_color=clothing_button_bg,
                hover_color=clothing_button_hover,
                text_color="white"
            )
        
        # Обновляем цвета выпадающего списка, если он открыт
        self.update_dropdown_colors()
    
    def update_dropdown_colors(self):
        """Обновление цветов выпадающего списка"""
        if not self.dropdown_frame:
            return
        
        # Определяем цвета в зависимости от темы
        if self.current_theme == "dark":
            bg_color = "#2B2B2B"
            text_color = "white"
            border_color = "#555555"
            hover_color = "#3E3E3E"
        else:
            bg_color = "white"
            text_color = "#333333"
            border_color = "#CCCCCC"
            hover_color = "#F0F7FF"
        
        # Обновляем основной фрейм
        self.dropdown_frame.configure(
            fg_color=bg_color,
            border_color=border_color
        )
        
        # Обновляем элементы списка
        if hasattr(self, 'dropdown_items'):
            for item in self.dropdown_items:
                if item.winfo_exists():
                    item.configure(fg_color=bg_color)
                    for child in item.winfo_children():
                        if isinstance(child, ctk.CTkLabel):
                            if child.cget("font") == ("Arial", 14, "bold"):
                                child.configure(text_color=text_color)
                            elif child.cget("font") in [("Arial", 11), ("Arial", 9)]:
                                child.configure(text_color=text_color)
    
    def on_key_release(self, event):
        """Обработчик отпускания клавиш в поле ввода"""
        # Игнорируем специальные клавиши
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Return', 'Escape']:
            return
        
        # Получаем текущий текст
        current_text = self.city_entry.get().strip()
        
        # Если текст изменился и не пустой
        if current_text and current_text != self.last_search_text:
            self.last_search_text = current_text
            
            # Отменяем предыдущий таймер поиска
            if self.search_after_id:
                self.city_entry.after_cancel(self.search_after_id)
            
            # Устанавливаем новый таймер для поиска (задержка 300 мс)
            self.search_after_id = self.city_entry.after(300, lambda: self.search_cities(current_text))
        
        # Если текст пустой, скрываем выпадающий список
        elif not current_text:
            self.hide_dropdown()
    
    def on_focus_out(self, event):
        """Обработчик потери фокуса полем ввода"""
        # Небольшая задержка, чтобы можно было кликнуть по выпадающему списку
        self.city_entry.after(200, self.hide_dropdown)
    
    def on_arrow_down(self, event):
        """Обработчик нажатия стрелки вниз для навигации по выпадающему списку"""
        if self.dropdown_visible and self.dropdown_frame:
            # Фокусируемся на первом элементе списка
            children = self.dropdown_frame.winfo_children()
            if children:
                children[0].focus_set()
    
    def search_cities(self, query):
        """Поиск городов по запросу"""
        if len(query) < 2:  # Ищем только если введено минимум 2 символа
            self.hide_dropdown()
            return
        
        # Выполняем поиск через API
        results = self.weather_api.search_cities(query)
        
        if results and len(results) > 0:
            self.show_dropdown(results)
        else:
            self.hide_dropdown()
    
    def show_dropdown(self, cities):
        """Показывает выпадающий список с найденными городами"""
        # Скрываем предыдущий список, если есть
        self.hide_dropdown()
        
        # Определяем цвета в зависимости от темы
        if self.current_theme == "dark":
            bg_color = "#2B2B2B"
            text_color = "white"
            border_color = "#555555"
            header_bg = "#3E3E3E"
            header_text = "#CCCCCC"
        else:
            bg_color = "white"
            text_color = "#333333"
            border_color = "#CCCCCC"
            header_bg = "#F5F5F5"
            header_text = "#666666"
        
        # Создаем новый фрейм для выпадающего списка
        self.dropdown_frame = ctk.CTkFrame(
            self.city_entry.master,
            fg_color=bg_color,
            border_width=2,
            border_color=border_color,
            corner_radius=8
        )
        self.dropdown_frame.pack(fill="x", pady=(0, 5), padx=0)
        
        # Заголовок с количеством результатов
        if len(cities) > 0:
            header_frame = ctk.CTkFrame(self.dropdown_frame, fg_color=header_bg, height=30, corner_radius=0)
            header_frame.pack(fill="x")
            header_frame.pack_propagate(False)
            
            header_label = ctk.CTkLabel(
                header_frame,
                text=f"🌍 Найдено городов: {len(cities)}",
                font=("Arial", 11, "bold"),
                text_color=header_text
            )
            header_label.pack(side="left", padx=10)
        
        # Контейнер для элементов списка с прокруткой
        list_container = ctk.CTkScrollableFrame(
            self.dropdown_frame,
            fg_color="transparent",
            height=min(300, len(cities) * 60),
            corner_radius=0
        )
        list_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Добавляем города в список
        for i, city in enumerate(cities[:15]):
            self.add_dropdown_item(list_container, city, i)
    
    def add_dropdown_item(self, container, city, index):
        """Добавляет элемент в выпадающий список"""
        # Определяем цвета в зависимости от темы
        if self.current_theme == "dark":
            bg_color = "#2B2B2B"
            text_color = "white"
            secondary_color = "#CCCCCC"
            hover_color = "#3E3E3E"
            title_hover_color = "#6BBAFF"
        else:
            bg_color = "white"
            text_color = "#333333"
            secondary_color = "#666666"
            hover_color = "#F0F7FF"
            title_hover_color = "#0066CC"
        
        # Фрейм для элемента
        item_frame = ctk.CTkFrame(
            container,
            fg_color=bg_color,
            height=60,
            corner_radius=4
        )
        item_frame.pack(fill="x", pady=1, padx=2)
        item_frame.pack_propagate(False)
        
        # Информация о городе
        name = city.get('name', '')
        country = city.get('country', '')
        admin = city.get('admin1', '')
        population = city.get('population', None)
        
        # Название города и страна (жирным)
        title_text = f"{name}"
        if country:
            title_text += f", {country}"
        
        title_label = ctk.CTkLabel(
            item_frame,
            text=title_text,
            font=("Arial", 14, "bold"),
            text_color=text_color,
            anchor="w"
        )
        title_label.place(x=10, y=8)
        
        # Дополнительная информация (регион)
        subtitle_text = ""
        if admin and admin != name:
            subtitle_text += f"{admin}"
        
        if population:
            try:
                pop_formatted = f"{int(population):,}"
                if subtitle_text:
                    subtitle_text += f" • "
                subtitle_text += f"Население: {pop_formatted}"
            except:
                pass
        
        if subtitle_text:
            subtitle_label = ctk.CTkLabel(
                item_frame,
                text=subtitle_text,
                font=("Arial", 11),
                text_color=secondary_color,
                anchor="w"
            )
            subtitle_label.place(x=10, y=32)
        
        # Координаты (мелким шрифтом справа)
        coord_text = f"{city['latitude']:.2f}°, {city['longitude']:.2f}°"
        coord_label = ctk.CTkLabel(
            item_frame,
            text=coord_text,
            font=("Arial", 9),
            text_color=secondary_color,
            anchor="e"
        )
        coord_label.place(relx=1.0, x=-10, y=8, anchor="ne")
        
        # Кнопка выбора (при клике на весь элемент)
        def on_enter(e):
            item_frame.configure(fg_color=hover_color)
            title_label.configure(text_color=title_hover_color)
        
        def on_leave(e):
            item_frame.configure(fg_color=bg_color)
            title_label.configure(text_color=text_color)
        
        item_frame.bind('<Enter>', on_enter)
        item_frame.bind('<Leave>', on_leave)
        item_frame.bind('<Button-1>', lambda e, c=city: self.select_city_from_dropdown(c))
        title_label.bind('<Button-1>', lambda e, c=city: self.select_city_from_dropdown(c))
        
        # Иконка выбора (появляется при наведении)
        select_icon = ctk.CTkLabel(
            item_frame,
            text="✓ Выбрать",
            font=("Arial", 11),
            text_color=title_hover_color,
            anchor="e"
        )
        select_icon.place(relx=1.0, x=-10, y=32, anchor="ne")
        select_icon.configure(state="disabled")
        
        # Привязываем клавиши для навигации
        item_frame.bind('<Return>', lambda e, c=city: self.select_city_from_dropdown(c))
        item_frame.bind('<Down>', self.on_next_item)
        item_frame.bind('<Up>', self.on_prev_item)
        item_frame.bind('<Escape>', lambda e: self.hide_dropdown())
        
        # Сохраняем ссылку на элемент для навигации
        if not hasattr(self, 'dropdown_items'):
            self.dropdown_items = []
        self.dropdown_items.append(item_frame)
    
    def on_next_item(self, event):
        """Переход к следующему элементу в списке"""
        if not hasattr(self, 'dropdown_items') or not self.dropdown_items:
            return
            
        current = event.widget
        try:
            current_index = self.dropdown_items.index(current)
            if current_index < len(self.dropdown_items) - 1:
                next_item = self.dropdown_items[current_index + 1]
                next_item.focus_set()
                self.highlight_dropdown_item(current_index + 1)
        except ValueError:
            pass
    
    def on_prev_item(self, event):
        """Переход к предыдущему элементу в списке"""
        if not hasattr(self, 'dropdown_items') or not self.dropdown_items:
            return
            
        current = event.widget
        try:
            current_index = self.dropdown_items.index(current)
            if current_index > 0:
                prev_item = self.dropdown_items[current_index - 1]
                prev_item.focus_set()
                self.highlight_dropdown_item(current_index - 1)
            else:
                self.city_entry.focus_set()
        except ValueError:
            pass
    
    def highlight_dropdown_item(self, index):
        """Подсвечивает элемент выпадающего списка"""
        if not hasattr(self, 'dropdown_items'):
            return
            
        # Определяем цвета в зависимости от темы
        if self.current_theme == "dark":
            hover_color = "#3E3E3E"
            text_color = "white"
            title_hover_color = "#6BBAFF"
        else:
            hover_color = "#F0F7FF"
            text_color = "#333333"
            title_hover_color = "#0066CC"
        
        for i, item in enumerate(self.dropdown_items):
            if i == index:
                item.configure(fg_color=hover_color)
                for child in item.winfo_children():
                    if isinstance(child, ctk.CTkLabel) and child.cget("font") == ("Arial", 14, "bold"):
                        child.configure(text_color=title_hover_color)
            else:
                item.configure(fg_color="transparent")
                for child in item.winfo_children():
                    if isinstance(child, ctk.CTkLabel) and child.cget("font") == ("Arial", 14, "bold"):
                        child.configure(text_color=text_color)
    
    def select_city_from_dropdown(self, city):
        """Выбор города из выпадающего списка"""
        # Устанавливаем название города в поле ввода
        name = city.get('name', '')
        country = city.get('country', '')
        
        # Формируем полное название для отображения
        display_name = name
        if country:
            display_name += f", {country}"
        
        self.city_entry.delete(0, 'end')
        self.city_entry.insert(0, display_name)
        
        # Скрываем выпадающий список
        self.hide_dropdown()
        
        # Вызываем поиск погоды для выбранного города
        self.callbacks['city_selected'](city)
    
    def hide_dropdown(self):
        """Скрывает выпадающий список"""
        if self.dropdown_frame:
            self.dropdown_frame.destroy()
            self.dropdown_frame = None
        self.dropdown_visible = False
        if hasattr(self, 'dropdown_items'):
            self.dropdown_items = []
    
    def get_city_name(self):
        """Возвращает введенное название города"""
        return self.city_entry.get().strip()
    
    def set_search_button_state(self, state, text=None):
        """Устанавливает состояние кнопки поиска"""
        self.search_button.configure(state=state)
        if text:
            self.search_button.configure(text=text)
    
    def show_status(self, message, color="black"):
        """Показывает статус сообщение"""
        self.status_label.configure(text=message, text_color=color)
        # Очищаем статус через 5 секунд
        self.status_label.after(5000, lambda: self.status_label.configure(text=""))
    
    def update_weather_display(self, full_name, weather_data, temp_unit, wind_unit):
        """Обновление отображения погоды"""
        if 'current_weather' in weather_data:
            current = weather_data['current_weather']
            
            # Сохраняем данные для рекомендаций
            self.current_weather_data = weather_data
            self.current_city_name = full_name
            
            # Активируем кнопку рекомендаций
            self.clothing_button.configure(state="normal")
            
            # Город
            self.city_label.configure(text=full_name)
            
            # Температура
            temp = current['temperature']
            self.temp_label.configure(text=f"{temp:.1f}{temp_unit}")
            
            # Ветер
            wind_speed = current['windspeed']
            self.wind_speed_label.configure(text=f"{wind_speed:.1f} {wind_unit}")
            
            # Направление ветра
            wind_dir = current['winddirection']
            direction_text = self.weather_api.get_wind_direction_text(wind_dir)
            self.wind_direction_label.configure(text=f"{wind_dir}° ({direction_text})")
            
            # Ощущается как (если есть данные)
            if 'apparent_temperature' in current:
                feels_like = current['apparent_temperature']
                self.feels_like_label.configure(text=f"{feels_like:.1f}{temp_unit}")
            else:
                self.feels_like_label.configure(text="--")
            
            # Влажность (если есть данные)
            if 'relative_humidity' in current:
                humidity = current['relative_humidity']
                self.humidity_label.configure(text=f"{humidity}%")
            else:
                self.humidity_label.configure(text="--")
            
            # Восход и закат (если есть данные)
            if 'sunrise' in weather_data:
                sunrise = weather_data['sunrise']
                if sunrise and isinstance(sunrise, str) and len(sunrise) >= 16:
                    self.sunrise_label.configure(text=sunrise[11:16])
                else:
                    self.sunrise_label.configure(text="--")
            else:
                self.sunrise_label.configure(text="--")
            
            if 'sunset' in weather_data:
                sunset = weather_data['sunset']
                if sunset and isinstance(sunset, str) and len(sunset) >= 16:
                    self.sunset_label.configure(text=sunset[11:16])
                else:
                    self.sunset_label.configure(text="--")
            else:
                self.sunset_label.configure(text="--")
            
            # Давление (если есть данные)
            if 'pressure' in current:
                pressure = current['pressure']
                self.pressure_label.configure(text=f"{pressure} гПа")
            else:
                self.pressure_label.configure(text="--")
            
            # Время обновления
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.time_label.configure(text=f"Обновлено: {current_time}")
            
            # Если окно с рекомендациями открыто, обновляем его
            if self.recommendation_window and self.recommendation_window.winfo_exists():
                self.recommendation_window.destroy()
                self.show_clothing_recommendation_window()
