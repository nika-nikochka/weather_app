# gui/tabs/settings_tab.py
import customtkinter as ctk

class SettingsTab:
    def __init__(self, parent, settings_vars, callbacks):
        """
        parent - родительский фрейм (вкладка)
        settings_vars - словарь с переменными настроек
        callbacks - словарь с функциями обратного вызова
        """
        self.parent = parent
        self.settings_vars = settings_vars
        self.callbacks = callbacks
        self.settings_status = None
        self.about_frame = None
        self.settings_frame = None
        self.main_frame = None
        
        # Устанавливаем цвет фона родительского фрейма
        self.parent.configure(fg_color="transparent")
        
        self.setup_ui()
        
        # Отслеживаем изменение темы
        self.settings_vars['theme'].trace_add('write', self.on_theme_changed)
    
    def setup_ui(self):
        # Основной фрейм с прокруткой
        self.main_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Фрейм для настроек
        self.settings_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.settings_frame.pack(fill="x", padx=10, pady=10)
        
        # Заголовок "НАСТРОЙКИ ПРИЛОЖЕНИЯ"
        title = ctk.CTkLabel(
            self.settings_frame,
            text="НАСТРОЙКИ ПРИЛОЖЕНИЯ",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=(20, 10))
        
        # --- БЛОК ЕДИНИЦЫ ИЗМЕРЕНИЯ ---
        units_label = ctk.CTkLabel(
            self.settings_frame,
            text="ЕДИНИЦЫ ИЗМЕРЕНИЯ",
            font=("Arial", 18, "bold")
        )
        units_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        # Температура
        temp_frame = self._create_unit_frame(
            self.settings_frame, 
            "Температура:", 
            'temperature_unit',
            [
                ("° Цельсий (°C)", "celsius"), 
                ("° Фаренгейт (°F)", "fahrenheit")
            ]
        )
        temp_frame.pack(fill="x", padx=30, pady=5)
        
        # Скорость ветра
        wind_frame = self._create_unit_frame(
            self.settings_frame, 
            "Скорость ветра:", 
            'wind_speed_unit',
            [
                ("км/ч", "kmh"), 
                ("м/с", "ms")
            ]
        )
        wind_frame.pack(fill="x", padx=30, pady=5)
        
        # Давление
        pressure_frame = self._create_unit_frame(
            self.settings_frame, 
            "Давление:", 
            'pressure_unit',
            [
                ("гПа", "hpa"), 
                ("мм рт. ст.", "mmhg")
            ]
        )
        pressure_frame.pack(fill="x", padx=30, pady=5)
        
        # Осадки
        precip_frame = self._create_unit_frame(
            self.settings_frame, 
            "Осадки:", 
            'precipitation_unit',
            [
                ("мм", "mm"), 
                ("дюймы", "inches")
            ]
        )
        precip_frame.pack(fill="x", padx=30, pady=5)
        
        # Разделитель
        separator1 = ctk.CTkFrame(self.settings_frame, height=2, fg_color="gray")
        separator1.pack(fill="x", padx=20, pady=15)
        
        # --- БЛОК ОФОРМЛЕНИЕ ---
        design_label = ctk.CTkLabel(
            self.settings_frame,
            text="ОФОРМЛЕНИЕ",
            font=("Arial", 18, "bold")
        )
        design_label.pack(anchor="w", padx=20, pady=(5, 5))
        
        # Тема
        theme_frame = self._create_unit_frame(
            self.settings_frame, 
            "Тема:", 
            'theme',
            [
                ("Светлая", "light"), 
                ("Тёмная", "dark"), 
                ("Системная", "system")
            ]
        )
        theme_frame.pack(fill="x", padx=30, pady=5)
        
        # Язык
        lang_frame = self._create_unit_frame(
            self.settings_frame, 
            "Язык:", 
            'language',
            [
                ("Русский", "ru"), 
                ("English", "en")
            ]
        )
        lang_frame.pack(fill="x", padx=30, pady=5)
        
        # Разделитель
        separator2 = ctk.CTkFrame(self.settings_frame, height=2, fg_color="gray")
        separator2.pack(fill="x", padx=20, pady=15)
        
        # --- БЛОК ДАННЫЕ ---
        data_label = ctk.CTkLabel(
            self.settings_frame,
            text="ДАННЫЕ",
            font=("Arial", 18, "bold")
        )
        data_label.pack(anchor="w", padx=20, pady=(5, 5))
        
        # Автосохранение с чекбоксом
        auto_save_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        auto_save_frame.pack(fill="x", padx=30, pady=5)
        
        auto_save_check = ctk.CTkCheckBox(
            auto_save_frame,
            text="Автоматически сохранять данные в файл",
            variable=self.settings_vars['auto_save'],
            checkbox_width=20,
            checkbox_height=20
        )
        auto_save_check.pack(anchor="w", pady=5)
        
        # Папка с полем ввода
        folder_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        folder_frame.pack(fill="x", padx=30, pady=5)
        
        folder_label = ctk.CTkLabel(
            folder_frame,
            text="Папка:",
            width=60
        )
        folder_label.pack(side="left")
        
        folder_entry = ctk.CTkEntry(
            folder_frame,
            textvariable=self.settings_vars['folder_path'],
            width=200,
            border_color="gray"
        )
        folder_entry.pack(side="left", padx=(5, 5))
        
        browse_button = ctk.CTkButton(
            folder_frame,
            text="Обзор",
            width=70,
            height=28,
            command=self.callbacks.get('browse_folder', lambda: None),
            fg_color="#4A5568",
            hover_color="#2D3748"
        )
        browse_button.pack(side="left")
        
        # Период обновления
        update_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        update_frame.pack(fill="x", padx=30, pady=(15, 10))
        
        update_label = ctk.CTkLabel(
            update_frame,
            text="Период обновления:",
            width=120
        )
        update_label.pack(side="left")
        
        update_radio_frame = ctk.CTkFrame(update_frame, fg_color="transparent")
        update_radio_frame.pack(side="left", padx=10)
        
        update_5min = ctk.CTkRadioButton(
            update_radio_frame,
            text="5 мин",
            variable=self.settings_vars['update_period'],
            value=5
        )
        update_5min.pack(side="left", padx=10)
        
        update_15min = ctk.CTkRadioButton(
            update_radio_frame,
            text="15 мин",
            variable=self.settings_vars['update_period'],
            value=15
        )
        update_15min.pack(side="left", padx=10)
        
        update_30min = ctk.CTkRadioButton(
            update_radio_frame,
            text="30 мин",
            variable=self.settings_vars['update_period'],
            value=30
        )
        update_30min.pack(side="left", padx=10)
        
        # --- БЛОК О ПРОГРАММЕ (внизу, отдельно) ---
        self.about_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.about_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        about_label = ctk.CTkLabel(
            self.about_frame,
            text="О ПРОГРАММЕ",
            font=("Arial", 18, "bold")
        )
        about_label.pack(pady=(15, 10))
        
        # Информация о версии
        version_label = ctk.CTkLabel(
            self.about_frame,
            text="Погодный информатор v1.0",
            font=("Arial", 14)
        )
        version_label.pack()
        
        # Информация об API
        api_label = ctk.CTkLabel(
            self.about_frame,
            text="Данные предоставлены Open-Meteo API",
            font=("Arial", 12),
            text_color="gray"
        )
        api_label.pack(pady=(5, 5))
        
        # Копирайт
        copyright_label = ctk.CTkLabel(
            self.about_frame,
            text="© 2026",
            font=("Arial", 10),
            text_color="gray"
        )
        copyright_label.pack(pady=(0, 15))
        
        # --- КРАСНАЯ КНОПКА СОХРАНЕНИЯ ---
        save_button = ctk.CTkButton(
            self.main_frame,
            text="СОХРАНИТЬ НАСТРОЙКИ",
            height=45,
            font=("Arial", 16, "bold"),
            command=self.callbacks.get('save_settings', lambda: self.show_save_status("Функция сохранения не реализована", "orange")),
            fg_color="#E53E3E",
            hover_color="#C53030",
            corner_radius=8
        )
        save_button.pack(pady=20, padx=50, fill="x")
        
        # Статус сохранения - теперь будет адаптироваться под тему
        self.settings_status = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Arial", 12)
        )
        self.settings_status.pack(pady=(0, 10))
        
        # Применяем начальную тему
        self.update_theme_colors(self.settings_vars['theme'].get())
    
    def _create_unit_frame(self, parent, label_text, var_name, options):
        """
        Вспомогательный метод для создания строки с радио-кнопками
        parent - родительский фрейм
        label_text - текст метки
        var_name - имя переменной в self.settings_vars
        options - список кортежей (текст, значение)
        """
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Метка с названием параметра
        label = ctk.CTkLabel(
            frame,
            text=label_text,
            width=120,
            anchor="w"
        )
        label.pack(side="left")
        
        # Контейнер для радио-кнопок
        radio_container = ctk.CTkFrame(frame, fg_color="transparent")
        radio_container.pack(side="left", padx=10)
        
        # Создаем радио-кнопки
        for i, (text, value) in enumerate(options):
            radio = ctk.CTkRadioButton(
                radio_container,
                text=text,
                variable=self.settings_vars[var_name],
                value=value
            )
            radio.pack(side="left", padx=(0 if i == 0 else 20, 0))
        
        return frame
    
    def show_save_status(self, message, color="green"):
        """Показывает статус сохранения настроек"""
        # Преобразуем цвет в соответствии с темой
        theme = self.settings_vars['theme'].get()
        
        # Выбираем цвет текста в зависимости от темы
        if color == "green":
            text_color = "#4CAF50" if theme == "light" else "#81C784"  # Светло-зеленый для темной темы
        elif color == "red":
            text_color = "#F44336" if theme == "light" else "#EF5350"
        elif color == "orange":
            text_color = "#FF9800" if theme == "light" else "#FFB74D"
        elif color == "blue":
            text_color = "#2196F3" if theme == "light" else "#64B5F6"
        else:
            text_color = color
        
        self.settings_status.configure(text=message, text_color=text_color)
        self.settings_status.after(3000, lambda: self.settings_status.configure(text=""))
    
    def on_theme_changed(self, *args):
        """Обработчик изменения темы"""
        self.update_theme_colors(self.settings_vars['theme'].get())
    
    def update_theme_colors(self, theme):
        """Обновление цветов в зависимости от темы"""
        # Обновляем цвет разделителей
        if theme == "dark":
            separator_color = "#404040"
            api_text_color = "#A0A0A0"
            # Обновляем текст в блоке "О программе"
            if hasattr(self, 'about_frame'):
                for child in self.about_frame.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        if "v1.0" in child.cget("text") or "Погодный" in child.cget("text"):
                            child.configure(text_color="white")
                        elif "Open-Meteo" in child.cget("text"):
                            child.configure(text_color=api_text_color)
                        elif "©" in child.cget("text"):
                            child.configure(text_color=api_text_color)
        else:  # светлая тема
            separator_color = "#E0E0E0"
            api_text_color = "gray"
            # Обновляем текст в блоке "О программе"
            if hasattr(self, 'about_frame'):
                for child in self.about_frame.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        if "v1.0" in child.cget("text") or "Погодный" in child.cget("text"):
                            child.configure(text_color="black")
                        elif "Open-Meteo" in child.cget("text"):
                            child.configure(text_color=api_text_color)
                        elif "©" in child.cget("text"):
                            child.configure(text_color=api_text_color)
        
        # Обновляем разделители
        for child in self.settings_frame.winfo_children():
            if isinstance(child, ctk.CTkFrame) and child.cget("height") == 2:
                child.configure(fg_color=separator_color)
        
        # Обновляем текст об API в блоке "О программе"
        if self.about_frame:
            for child in self.about_frame.winfo_children():
                if isinstance(child, ctk.CTkLabel) and "Open-Meteo" in child.cget("text"):
                    child.configure(text_color=api_text_color)
                elif isinstance(child, ctk.CTkLabel) and "©" in child.cget("text"):
                    child.configure(text_color=api_text_color)
