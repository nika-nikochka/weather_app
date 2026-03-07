# gui/tabs/tab2.py
import customtkinter as ctk

class Tab2:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        # Заглушка для второй вкладки
        label = ctk.CTkLabel(
            self.parent,
            text="Вкладка 2 - здесь будет дополнительный функционал",
            font=("Arial", 20),
            text_color="black"
        )
        label.pack(expand=True)