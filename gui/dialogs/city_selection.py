# gui/dialogs/city_selection.py
import customtkinter as ctk

# Цвета для кнопок
RED_COLOR = "#E53E3E"
HOVER_RED = "#C53030"

class CitySelectionDialog(ctk.CTkToplevel):
    """Диалог выбора города из нескольких вариантов"""
    def __init__(self, parent, cities, callback):
        super().__init__(parent)
        
        self.cities = cities
        self.callback = callback
        
        # Настройки окна
        self.title("Выберите город")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        # Делаем окно модальным
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Заголовок
        title_label = ctk.CTkLabel(
            self,
            text="🌍 Найдено несколько городов",
            font=("Arial", 20, "bold"),
            text_color="black"
        )
        title_label.pack(pady=(20, 5))
        
        info_label = ctk.CTkLabel(
            self,
            text="Выберите нужный город из списка:",
            font=("Arial", 14),
            text_color="black"
        )
        info_label.pack(pady=(0, 15))
        
        # Создаем прокручиваемую область для списка городов
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Добавляем города в список
        for i, city in enumerate(self.cities):
            self.add_city_widget(city, i + 1)
        
        # Кнопка отмены
        cancel_button = ctk.CTkButton(
            self,
            text="Отмена",
            command=self.on_close,
            fg_color="gray",
            hover_color="#4A5568",
            width=200,
            height=40,
            text_color="white"
        )
        cancel_button.pack(pady=20)
    
    def add_city_widget(self, city, number):
        """Добавление виджета города в список"""
        # Фрейм для города
        city_frame = ctk.CTkFrame(self.scroll_frame)
        city_frame.pack(fill="x", pady=5, padx=5)
        
        # Информация о городе
        name = city.get('name', 'Неизвестно')
        country = city.get('country', 'Неизвестно')
        admin = city.get('admin1', '')
        population = city.get('population', 'Н/Д')
        
        # Форматируем население
        if population != 'Н/Д' and population:
            try:
                population = f"{int(population):,}"
            except:
                pass
        
        # Название города и страна
        city_name_label = ctk.CTkLabel(
            city_frame,
            text=f"{number}. {name}, {country}",
            font=("Arial", 16, "bold"),
            anchor="w",
            text_color="black"
        )
        city_name_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # Дополнительная информация
        info_text = f"Регион: {admin if admin else 'Н/Д'} | Население: {population}"
        info_label = ctk.CTkLabel(
            city_frame,
            text=info_text,
            font=("Arial", 12),
            text_color="gray",
            anchor="w"
        )
        info_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Координаты
        coord_text = f"Координаты: {city['latitude']:.4f}, {city['longitude']:.4f}"
        coord_label = ctk.CTkLabel(
            city_frame,
            text=coord_text,
            font=("Arial", 11),
            text_color="gray",
            anchor="w"
        )
        coord_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Кнопка выбора - КРАСНАЯ
        select_button = ctk.CTkButton(
            city_frame,
            text="✅ Выбрать этот город",
            command=lambda c=city: self.select_city(c),
            height=35,
            fg_color=RED_COLOR,
            hover_color=HOVER_RED,
            text_color="white"
        )
        select_button.pack(anchor="e", padx=10, pady=10)
    
    def select_city(self, city):
        """Выбор города"""
        self.callback(city)
        self.destroy()
    
    def on_close(self):
        """Закрытие диалога без выбора"""
        self.callback(None)
        self.destroy()