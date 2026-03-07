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
        
        self.setup_ui()
    
    def setup_ui(self):
        # Фрейм для настроек
        settings_frame = ctk.CTkFrame(self.parent)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        title = ctk.CTkLabel(
            settings_frame,
            text="Настройки приложения",
            font=("Arial", 20, "bold"),
            text_color="black"
        )
        title.pack(pady=20)
        
        # Единицы измерения температуры
        temp_frame = ctk.CTkFrame(settings_frame)
        temp_frame.pack(fill="x", padx=20, pady=10)
        
        temp_label = ctk.CTkLabel(
            temp_frame,
            text="Единицы измерения температуры:",
            font=("Arial", 14),
            text_color="black"
        )
        temp_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        temp_radio_frame = ctk.CTkFrame(temp_frame, fg_color="transparent")
        temp_radio_frame.pack(padx=10, pady=5)
        
        celsius_radio = ctk.CTkRadioButton(
            temp_radio_frame,
            text="Цельсий (°C)",
            variable=self.settings_vars['temperature_unit'],
            value="celsius",
            text_color="black"
        )
        celsius_radio.pack(side="left", padx=20)
        
        fahrenheit_radio = ctk.CTkRadioButton(
            temp_radio_frame,
            text="Фаренгейт (°F)",
            variable=self.settings_vars['temperature_unit'],
            value="fahrenheit",
            text_color="black"
        )
        fahrenheit_radio.pack(side="left", padx=20)
        
        # Единицы измерения ветра
        wind_frame = ctk.CTkFrame(settings_frame)
        wind_frame.pack(fill="x", padx=20, pady=10)
        
        wind_label = ctk.CTkLabel(
            wind_frame,
            text="Единицы измерения ветра:",
            font=("Arial", 14),
            text_color="black"
        )
        wind_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        wind_radio_frame = ctk.CTkFrame(wind_frame, fg_color="transparent")
        wind_radio_frame.pack(padx=10, pady=5)
        
        kmh_radio = ctk.CTkRadioButton(
            wind_radio_frame,
            text="Км/ч",
            variable=self.settings_vars['wind_speed_unit'],
            value="kmh",
            text_color="black"
        )
        kmh_radio.pack(side="left", padx=20)
        
        ms_radio = ctk.CTkRadioButton(
            wind_radio_frame,
            text="М/с",
            variable=self.settings_vars['wind_speed_unit'],
            value="ms",
            text_color="black"
        )
        ms_radio.pack(side="left", padx=20)
        
        # Автосохранение
        save_frame = ctk.CTkFrame(settings_frame)
        save_frame.pack(fill="x", padx=20, pady=10)
        
        save_checkbox = ctk.CTkCheckBox(
            save_frame,
            text="Автоматически сохранять данные в файл",
            variable=self.settings_vars['auto_save'],
            text_color="black"
        )
        save_checkbox.pack(anchor="w", padx=10, pady=10)
        
        # Кнопка сохранения настроек - КРАСНАЯ
        save_button = ctk.CTkButton(
            settings_frame,
            text="Сохранить настройки",
            height=40,
            command=self.callbacks['save_settings'],
            fg_color="#E53E3E",
            hover_color="#C53030",
            text_color="white"
        )
        save_button.pack(pady=20)
        
        # Статус сохранения
        self.settings_status = ctk.CTkLabel(
            settings_frame,
            text="",
            font=("Arial", 12),
            text_color="black"
        )
        self.settings_status.pack()
    
    def show_save_status(self, message, color="green"):
        """Показывает статус сохранения настроек"""
        self.settings_status.configure(text=message, text_color=color)
        self.settings_status.after(3000, lambda: self.settings_status.configure(text=""))