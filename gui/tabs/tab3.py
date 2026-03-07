# gui/tabs/tab3.py
import customtkinter as ctk

class Tab3:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        # Заглушка для третьей вкладки
        label = ctk.CTkLabel(
            self.parent,
            text="Вкладка 3 - здесь будет дополнительный функционал",
            font=("Arial", 20),
            text_color="black"
        )
        label.pack(expand=True)