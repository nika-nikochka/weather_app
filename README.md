# weather_app

weather_app/
│
├── main.py                    # Точка входа
├── weather_api.py             # Работа с API
│
├── gui/
│   ├── __init__.py
│   ├── app.py                 # Главное окно приложения
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── weather_tab.py     # Вкладка погоды
│   │   ├── tab2.py            # Вкладка 2
│   │   ├── tab3.py            # Вкладка 3
│   │   └── settings_tab.py    # Вкладка настроек
│   └── dialogs/
│       └── city_selection.py  # Диалог выбора города
│
└── weather_data/              # Папка для сохраненных данных
