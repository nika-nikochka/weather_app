# gui/tabs/weather_tab.py
import customtkinter as ctk
from datetime import datetime

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
        self.wind_speed_label = None
        self.wind_direction_label = None
        self.time_label = None
        self.status_label = None
        self.current_theme = "light"
        
        # Переменные для выпадающего списка
        self.dropdown_frame = None
        self.dropdown_visible = False
        self.search_after_id = None
        self.last_search_text = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        # Верхняя панель с поиском
        search_frame = ctk.CTkFrame(self.parent)
        search_frame.pack(fill="x", padx=20, pady=(20, 0))
        
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
        self.weather_frame = ctk.CTkFrame(self.parent)
        self.weather_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Информация о городе
        self.city_label = ctk.CTkLabel(
            self.weather_frame,
            text="Введите город для получения информации",
            font=("Arial", 24, "bold")
        )
        self.city_label.pack(pady=(30, 20))
        
        # Температура
        self.temp_label = ctk.CTkLabel(
            self.weather_frame,
            text="",
            font=("Arial", 48),
        )
        self.temp_label.pack(pady=10)
        
        # Дополнительная информация
        info_frame = ctk.CTkFrame(self.weather_frame, fg_color="transparent")
        info_frame.pack(pady=20)
        
        # Ветер
        wind_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        wind_frame.pack(side="left", padx=30)
        
        wind_label = ctk.CTkLabel(
            wind_frame,
            text="💨 Ветер",
            font=("Arial", 16),
        )
        wind_label.pack()
        
        self.wind_speed_label = ctk.CTkLabel(
            wind_frame,
            text="",
            font=("Arial", 20, "bold"),
        )
        self.wind_speed_label.pack()
        
        # Направление ветра
        direction_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        direction_frame.pack(side="left", padx=30)
        
        direction_label = ctk.CTkLabel(
            direction_frame,
            text="🧭 Направление",
            font=("Arial", 16),
        )
        direction_label.pack()
        
        self.wind_direction_label = ctk.CTkLabel(
            direction_frame,
            text="",
            font=("Arial", 20, "bold"),
        )
        self.wind_direction_label.pack()
        
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
            self.parent,
            text="",
            font=("Arial", 12),
        )
        self.status_label.pack(pady=10)
    
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
        
        # Создаем новый фрейм для выпадающего списка с красивым оформлением
        self.dropdown_frame = ctk.CTkFrame(
            self.city_entry.master,
            fg_color="white",
            border_width=2,
            border_color="#CCCCCC",
            corner_radius=8
        )
        self.dropdown_frame.pack(fill="x", pady=(0, 5), padx=0)
        
        # Заголовок с количеством результатов
        if len(cities) > 0:
            header_frame = ctk.CTkFrame(self.dropdown_frame, fg_color="#F5F5F5", height=30, corner_radius=0)
            header_frame.pack(fill="x")
            header_frame.pack_propagate(False)
            
            header_label = ctk.CTkLabel(
                header_frame,
                text=f"🌍 Найдено городов: {len(cities)}",
                font=("Arial", 11, "bold"),
                text_color="#666666"
            )
            header_label.pack(side="left", padx=10)
        
        # Контейнер для элементов списка с прокруткой
        list_container = ctk.CTkScrollableFrame(
            self.dropdown_frame,
            fg_color="transparent",
            height=min(300, len(cities) * 60),  # Ограничиваем высоту
            corner_radius=0
        )
        list_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Добавляем города в список
        for i, city in enumerate(cities[:15]):  # Ограничиваем до 15 для производительности
            self.add_dropdown_item(list_container, city, i)
    
    def add_dropdown_item(self, container, city, index):
        """Добавляет элемент в выпадающий список"""
        # Фрейм для элемента
        item_frame = ctk.CTkFrame(
            container,
            fg_color="white",
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
            text_color="#333333",
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
                text_color="#666666",
                anchor="w"
            )
            subtitle_label.place(x=10, y=32)
        
        # Координаты (мелким шрифтом справа)
        coord_text = f"{city['latitude']:.2f}°, {city['longitude']:.2f}°"
        coord_label = ctk.CTkLabel(
            item_frame,
            text=coord_text,
            font=("Arial", 9),
            text_color="#999999",
            anchor="e"
        )
        coord_label.place(relx=1.0, x=-10, y=8, anchor="ne")
        
        # Кнопка выбора (при клике на весь элемент)
        def on_enter(e):
            item_frame.configure(fg_color="#F0F7FF")
            title_label.configure(text_color="#0066CC")
        
        def on_leave(e):
            item_frame.configure(fg_color="white")
            title_label.configure(text_color="#333333")
        
        item_frame.bind('<Enter>', on_enter)
        item_frame.bind('<Leave>', on_leave)
        item_frame.bind('<Button-1>', lambda e, c=city: self.select_city_from_dropdown(c))
        title_label.bind('<Button-1>', lambda e, c=city: self.select_city_from_dropdown(c))
        
        # Иконка выбора (появляется при наведении)
        select_icon = ctk.CTkLabel(
            item_frame,
            text="✓ Выбрать",
            font=("Arial", 11),
            text_color="#0066CC",
            anchor="e"
        )
        select_icon.place(relx=1.0, x=-10, y=32, anchor="ne")
        select_icon.configure(state="disabled")  # Делаем неактивным, чтобы не мешал
        
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
                # Визуально выделяем элемент
                for i, item in enumerate(self.dropdown_items):
                    if i == current_index + 1:
                        item.configure(fg_color="#F0F7FF")
                        # Находим и меняем цвет заголовка
                        for child in item.winfo_children():
                            if isinstance(child, ctk.CTkLabel) and child.cget("font") == ("Arial", 14, "bold"):
                                child.configure(text_color="#0066CC")
                    else:
                        item.configure(fg_color="white")
                        for child in item.winfo_children():
                            if isinstance(child, ctk.CTkLabel) and child.cget("font") == ("Arial", 14, "bold"):
                                child.configure(text_color="#333333")
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
                # Визуально выделяем элемент
                for i, item in enumerate(self.dropdown_items):
                    if i == current_index - 1:
                        item.configure(fg_color="#F0F7FF")
                        for child in item.winfo_children():
                            if isinstance(child, ctk.CTkLabel) and child.cget("font") == ("Arial", 14, "bold"):
                                child.configure(text_color="#0066CC")
                    else:
                        item.configure(fg_color="white")
                        for child in item.winfo_children():
                            if isinstance(child, ctk.CTkLabel) and child.cget("font") == ("Arial", 14, "bold"):
                                child.configure(text_color="#333333")
            else:
                self.city_entry.focus_set()
        except ValueError:
            pass
    
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
            
            # Время обновления
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.time_label.configure(text=f"Обновлено: {current_time}")