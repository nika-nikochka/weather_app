# gui/app.py
import customtkinter as ctk
import threading
from datetime import datetime
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
        self.theme = ctk.StringVar(value="light")
        self.language = ctk.StringVar(value="ru")
        self.folder_path = ctk.StringVar(value="weather_data/")
        self.update_period = ctk.IntVar(value=15)
        
        # Переменные для отображения в шапке
        self.current_city_display = "Не выбрано"
        self.current_time = datetime.now().strftime("%H:%M")
        self.current_date = datetime.now().strftime("%d.%m.%Y")
        
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
        
        # Создаем главный контейнер
        self.setup_main_container()
        
        # Создаем шапку приложения
        self.setup_header()
        
        # Создаем вкладки
        self.setup_tabs()
        
        # Создаем кнопку справки
        self.setup_help_button()
        
        # Запускаем обновление времени
        self.update_time()
        
        # Привязываем Enter к поиску (будет выполнено после создания weather_tab)
        self.after(100, self.bind_enter_key)
    
    def bind_enter_key(self):
        """Привязка клавиши Enter к поиску"""
        if hasattr(self, 'weather_tab') and self.weather_tab.city_entry:
            self.weather_tab.city_entry.bind('<Return>', lambda event: self.search_weather())
    
    def setup_main_container(self):
        """Создание главного контейнера"""
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
    
    def setup_header(self):
        """Создание шапки приложения"""
        self.header_frame = ctk.CTkFrame(self.main_container, height=80, corner_radius=10)
        self.header_frame.pack(fill="x", pady=(0, 10))
        self.header_frame.pack_propagate(False)
        
        # Левая часть - время, дата, место
        self.left_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.left_header.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        
        # Время (крупно)
        self.time_label = ctk.CTkLabel(
            self.left_header,
            text=self.current_time,
            font=("Arial", 32, "bold")
        )
        self.time_label.pack(anchor="w")
        
        # Нижняя строка с датой и местом
        info_frame = ctk.CTkFrame(self.left_header, fg_color="transparent")
        info_frame.pack(anchor="w", fill="x")
        
        self.date_label = ctk.CTkLabel(
            info_frame,
            text=self.current_date,
            font=("Arial", 14)
        )
        self.date_label.pack(side="left", padx=(0, 10))
        
        self.location_label = ctk.CTkLabel(
            info_frame,
            text=f"📍 {self.current_city_display}",
            font=("Arial", 14)
        )
        self.location_label.pack(side="left")
        
        # Правая часть - иконки вкладок
        self.right_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.right_header.pack(side="right", padx=20, pady=10)
        
        # Создаем иконки для вкладок
        self.tab_icons = []
        icon_data = [
            ("🌤", "Текущая погода"),
            ("📊", "Прогноз на несколько дней"),
            ("📈", "История погоды"),
            ("⚙️", "Настройки")
        ]

        
        for i, (icon, tooltip) in enumerate(icon_data):
            icon_frame = ctk.CTkFrame(self.right_header, fg_color="transparent", width=50, height=50)
            icon_frame.pack(side="left", padx=5)
            icon_frame.pack_propagate(False)
            
            icon_label = ctk.CTkLabel(
                icon_frame,
                text=icon,
                font=("Arial", 28),
                cursor="hand2"
            )
            icon_label.pack(expand=True)
            
            # Привязываем события для переключения вкладок
            icon_label.bind('<Button-1>', lambda e, idx=i: self.switch_to_tab(idx))
            icon_label.bind('<Enter>', lambda e, txt=tooltip: self.show_tooltip(e, txt))
            icon_label.bind('<Leave>', lambda e: self.hide_tooltip())
            
            self.tab_icons.append(icon_label)
        
        # Метка для всплывающей подсказки
        self.tooltip_label = None
        self.tooltip_timer = None
    
    def setup_help_button(self):
        """Создание кнопки справки в правом нижнем углу"""
        # Создаем фрейм для кнопки справки
        self.help_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.help_frame.place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")
        
        # Кнопка справки с текстом
        self.help_button = ctk.CTkButton(
            self.help_frame,
            text="? Справка",
            width=100,
            height=36,
            font=("Arial", 13, "bold"),
            corner_radius=18,
            fg_color="#4A5568",
            hover_color="#2D3748",
            command=self.show_help_window
        )
        self.help_button.pack()
        
        # Добавляем подсказку при наведении
        self.help_button.bind('<Enter>', lambda e: self.show_tooltip(e, "Открыть справку по использованию"))
        self.help_button.bind('<Leave>', lambda e: self.hide_tooltip())
    
    def show_help_window(self):
        """Отображает окно со справкой (вся справка в одном окне)"""
        # Создаем окно справки
        help_window = ctk.CTkToplevel(self)
        help_window.title("? Справка - Погодный информатор")
        help_window.geometry("600x650")
        help_window.minsize(500, 550)
        
        # Делаем окно модальным
        help_window.transient(self)
        help_window.grab_set()
        
        # Настраиваем цвета в зависимости от темы
        if self.theme.get() == "dark":
            bg_color = "#2b2b2b"
            text_color = "white"
            frame_color = "#333333"
            secondary_color = "#CCCCCC"
        else:
            bg_color = "white"
            text_color = "black"
            frame_color = "#f0f0f0"
            secondary_color = "#666666"
        
        help_window.configure(fg_color=bg_color)
        
        # Заголовок с городом (как в окне рекомендаций)
        header_frame = ctk.CTkFrame(help_window, fg_color=frame_color, height=60, corner_radius=10)
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="? Справка по использованию приложения",
            font=("Arial", 18, "bold"),
            text_color=text_color
        )
        title_label.pack(expand=True)
        
        # Основной контейнер для справки (как в окне рекомендаций)
        main_frame = ctk.CTkFrame(help_window, fg_color=frame_color)
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Текст справки (вся в одном текстовом поле с прокруткой)
        help_text = f"""
📖 ОБЩАЯ ИНФОРМАЦИЯ

«Погодный информатор» — приложение для получения актуальной информации 
о погоде, прогнозов и исторических данных.
📡 Данные предоставляются сервисом Open-Meteo API
🌍 Поддерживаются все города мира!


🔍 ВКЛАДКА «ТЕКУЩАЯ ПОГОДА»

• Введите название города в поле поиска (на русском или английском)
• При вводе появится выпадающий список с найденными городами
• Нажмите «Найти» или Enter для получения погоды
• Отобразятся: температура, ветер, влажность, давление, восход/закат
• Нажмите «Рекомендации по одежде» для советов по экипировке
• Графики покажут динамику температуры и ветра за сегодня


📊 ВКЛАДКА «ПРОГНОЗ НА НЕСКОЛЬКО ДНЕЙ»

• После выбора города на вкладке «Погода» прогноз загрузится автоматически
• Выберите период: 7 или 14 дней
• Вкладка «График температуры» покажет динамику max/min температур
• Вкладка «Карточки прогноза» покажет детальную информацию по дням:
  - Температура (max/min)
  - Осадки и вероятность
  - Скорость и направление ветра
  - Описание погоды


📈 ВКЛАДКА «ИСТОРИЯ ПОГОДЫ»

• Выберите дату для анализа (кнопки ◀ Сегодня ▶)
• Выберите период истории: 10, 25 или 50 лет
• Нажмите «Загрузить исторические данные»
• Будут показаны:
  - Статистика за весь период
  - Графики температур и осадков
  - Таблица с данными по годам


⚙️ ВКЛАДКА «НАСТРОЙКИ»

▶ ЕДИНИЦЫ ИЗМЕРЕНИЯ:
  • Температура: °C или °F
  • Скорость ветра: км/ч или м/с
  • Давление: гПа или мм рт. ст.
  • Осадки: мм или дюймы

▶ ОФОРМЛЕНИЕ:
  • Тема: Светлая / Тёмная / Системная
  • Язык: Русский / English (в разработке)

▶ ДАННЫЕ:
  • Автосохранение данных в файл
  • Выбор папки для сохранения
  • Период автоматического обновления: 5/15/30 мин

⚠️ Не забудьте нажать «СОХРАНИТЬ НАСТРОЙКИ» после изменений!


💡 ПОЛЕЗНЫЕ СОВЕТЫ

• Нажмите на иконки вкладок в правой части шапки для быстрого переключения
• Наведите курсор на иконку — появится подсказка
• Кнопка «Рекомендации по одежде» учитывает:
  - Текущую температуру и ощущаемую
  - Скорость ветра и влажность
  - УФ-индекс и вероятность осадков
  - Время суток и сезон
• Для исторических данных доступны даты с 1950 года по сегодня
• Все графики адаптируются под выбранную тему оформления


❓ ВОЗМОЖНЫЕ ПРОБЛЕМЫ

• Город не найден → проверьте правильность написания
• Нет исторических данных → попробуйте другую дату
• Ошибка API → проверьте подключение к интернету
• Графики не отображаются → выберите город на вкладке «Погода»


📞 ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ

Версия: 1.0
API: Open-Meteo (бесплатный, без ключа)
Разработчик: © 2026

Для получения актуальной погоды требуется подключение к интернету.
Данные обновляются автоматически согласно настройкам.

✨ Наслаждайтесь использованием приложения!
    """
        
        # Создаем текстовое поле с прокруткой (как в окне рекомендаций)
        textbox = ctk.CTkTextbox(
            main_frame,
            wrap="word",
            font=("Arial", 13),
            text_color=text_color,
            fg_color="transparent",
            border_width=0
        )
        textbox.pack(padx=20, pady=20, fill="both", expand=True)
        textbox.insert("1.0", help_text)
        textbox.configure(state="disabled")  # Только для чтения
        
        # Кнопка закрытия (как в окне рекомендаций)
        close_button = ctk.CTkButton(
            help_window,
            text="Закрыть",
            command=help_window.destroy,
            height=35,
            width=120,
            fg_color="#E53E3E",
            hover_color="#C53030",
            text_color="white"
        )
        close_button.pack(pady=(5, 15))
        
        # Обработчик закрытия окна
        help_window.protocol("WM_DELETE_WINDOW", help_window.destroy)
    
    def show_tooltip(self, event, text):
        """Показывает всплывающую подсказку сразу"""
        # Скрываем предыдущую подсказку
        self.hide_tooltip()

        # Получаем координаты виджета
        widget = event.widget
        x = (event.x_root - self.winfo_rootx() + 10) / 2 - 36
        y = widget.winfo_y() + widget.winfo_height() + 8

        # Создаём подсказку
        self.tooltip_label = ctk.CTkLabel(
            self,
            text=text,
            font=("Arial", 12, "bold"),
            fg_color="#2B2B2B" if self.theme.get() == "dark" else "#E0E0E0",
            text_color="white" if self.theme.get() == "dark" else "black",
            corner_radius=8,
            padx=12,
            pady=6
        )
        self.tooltip_label.place(x=x, y=y)

        # Автоматически скрываем через 3 секунды
        self.tooltip_timer = self.after(3000, self.hide_tooltip)

    
    def hide_tooltip(self):
        """Скрывает всплывающую подсказку"""
        if self.tooltip_timer:
            self.after_cancel(self.tooltip_timer)
            self.tooltip_timer = None

        if self.tooltip_label:
            self.tooltip_label.destroy()
            self.tooltip_label = None

    
    def update_active_tab_highlight(self):
        """Подсвечивает активную вкладку"""
        if not hasattr(self, 'tab_icons'):
            return

        current_tab = self.tab_view.get()
        tab_names = ["🌤 Погода", "📊 Вкладка 2", "📈 Вкладка 3", "⚙️ Настройки"]

        for i, icon_label in enumerate(self.tab_icons):
            if current_tab == tab_names[i]:
                # Подсвечиваем активную вкладку
                if self.theme.get() == "light":
                    icon_label.configure(text_color="#3EA5E5")
                else:
                    icon_label.configure(text_color="#6BBAFF")
            else:
                # Возвращаем обычный цвет
                icon_label.configure(text_color="white" if self.theme.get() == "dark" else "black")

    
    def switch_to_tab(self, tab_index):
        """Переключение на указанную вкладку"""
        tab_names = ["🌤 Погода", "📊 Вкладка 2", "📈 Вкладка 3", "⚙️ Настройки"]
        self.tab_view.set(tab_names[tab_index])
        
        # Подсвечиваем активную вкладку
        self.update_active_tab_highlight()
        
        # Скрываем подсказку при переключении
        self.hide_tooltip()
    
    def update_time(self):
        """Обновляет время в шапке"""
        self.current_time = datetime.now().strftime("%H:%M")
        self.time_label.configure(text=self.current_time)
        
        # Обновляем каждую секунду
        self.after(1000, self.update_time)
    
    def update_header_location(self, city_name):
        """Обновляет местоположение в шапке"""
        self.current_city_display = city_name
        self.location_label.configure(text=f"📍 {city_name}")
    
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
        
        # Обновляем цвета во всех вкладках
        if hasattr(self, 'weather_tab'):
            self.weather_tab.update_theme_colors(self.theme.get())
        if hasattr(self, 'settings_tab'):
            if hasattr(self.settings_tab, 'update_theme_colors'):
                self.settings_tab.update_theme_colors(self.theme.get())
        if hasattr(self, 'tab2'):
            if hasattr(self.tab2, 'on_theme_changed'):
                self.tab2.on_theme_changed()
        if hasattr(self, 'tab3'):
            if hasattr(self.tab3, 'on_theme_changed'):
                self.tab3.on_theme_changed()
        
        # Обновляем подсветку активной вкладки
        self.update_active_tab_highlight()
        
        # Обновляем цвет подсказки, если она видна
        if self.tooltip_label:
            if self.theme.get() == "dark":
                self.tooltip_label.configure(
                    fg_color="#2B2B2B",
                    text_color="white"
                )
            else:
                self.tooltip_label.configure(
                    fg_color="#E0E0E0",
                    text_color="black"
                )
    
    def setup_tabs(self):
        """Создание вкладок"""
        # Создаем вкладки
        self.tab_view = ctk.CTkTabview(self.main_container)
        self.tab_view.pack(fill="both", expand=True)
        
        # ИСПРАВЛЕНО: Полностью скрываем заголовки вкладок
        # Делаем их максимально маленькими и невидимыми
        if self.theme.get() == "light":
            btn_color = "#F0F0F0"  # Цвет под фон
        else:
            btn_color = "#2B2B2B"  # Цвет под фон
        
        # Настраиваем segmented button для полного скрытия
        self.tab_view._segmented_button.configure(
            font=("Arial", 1),  # Микроскопический шрифт
            height=1,  # Минимальная высота
            fg_color=btn_color,
            selected_color=btn_color,
            unselected_color=btn_color,
            border_width=0,
            corner_radius=0
        )
        
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
        
        # ИЗМЕНЕНО: передаем weather_api и settings_vars в Tab3
        self.tab3 = Tab3(
            self.tab_view.tab("📈 Вкладка 3"),
            self.weather_api,
            self.settings_vars
        )
        
        self.settings_tab = SettingsTab(
            self.tab_view.tab("⚙️ Настройки"),
            self.settings_vars,
            {
                'save_settings': self.save_settings,
                'browse_folder': self.browse_folder
            }
        )
        
        # Подсвечиваем активную вкладку
        self.update_active_tab_highlight()
   
    def browse_folder(self):
        """Открытие диалога выбора папки"""
        from tkinter import filedialog
        folder = filedialog.askdirectory(title="Выберите папку для сохранения данных")
        if folder:
            self.folder_path.set(folder)
    
    def search_weather(self):
        """Поиск погоды"""
        if not hasattr(self, 'weather_tab'):
            return
            
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
        
        thread = threading.Thread(target=self.get_weather_thread, args=(city_info, city_name, country))
        thread.daemon = True
        thread.start()
    
    def get_weather_thread(self, city_info, city_name, country):
        """Получение погоды в отдельном потоке"""
        weather_data = self.weather_api.get_weather(city_info)
        
        if weather_data:
            # Форматируем полное название города
            full_name = self.weather_api.format_city_full_name(city_info)
            
            # Обновляем шапку с названием города
            self.after(0, lambda: self.update_header_location(full_name))
            
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
                full_name, weather_data, temp_unit, wind_unit, self.pressure_unit.get()
            ))
            
            # После обновления текущей погоды, передаем город для прогноза и истории
            self.after(0, lambda: self.set_city_for_forecast(city_info))
            self.after(0, lambda: self.set_city_for_history(city_info))
            
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
    
    def set_city_for_history(self, city_info):
        """Передает выбранный город во вкладку с историческими данными"""
        if hasattr(self, 'tab3'):
            self.tab3.set_city(city_info)
    
    def save_settings(self):
        """Сохранение настроек"""
        self.settings_tab.show_save_status("✅ Настройки сохранены", "green")