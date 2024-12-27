import sys
import random
import pyperclip
from PyQt6 import QtWidgets
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, \
    QLineEdit, QSpinBox, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
import os  # Предоставляет функции для взаимодействия с операционной системой, такие как проверка существования файла и запуск файлов.
import sqlite3


class PasswordGeneratorApp(QWidget):
    """
    Этот класс представляет собой часть приложения, отвечающую за генерацию паролей.
    Он позволяет пользователям указывать критерии пароля (длину, типы символов)
    и генерировать случайный пароль на основе этих критериев.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Генератор паролей")
        self.setGeometry(400, 200, 800, 400)

        # Создаем поле для отображения сгенерированного пароля.
        self.password_display = QLineEdit(self)
        self.password_display.setReadOnly(True)
        self.password_display.setFont(QFont("Arial", 20))
        self.password_display.setPlaceholderText("Здесь появится пароль")

        # Создаем метку для поля ввода длины пароля.
        length_label = QLabel("Длина пароля:", self)
        length_label.setStyleSheet("QLabel { margin-top: 10px; }")
        length_label.setFont(QFont("Arial", 20))
        # Создаем спинбокс, чтобы пользователь мог указать длину пароля.
        self.length_input = QSpinBox(self)
        self.length_input.setValue(20)
        self.length_input.setFont(QFont("Arial", 10))
        self.length_input.setRange(6, 32)

        # Определяем общий стиль для кнопок, чтобы избежать повторения.
        button_style = "QPushButton { padding: 15px; font-size: 16px; }"

        # Создаем кнопки для переключения различных типов символов в пароле.
        self.uppercase_button = QPushButton("Заглавные буквы (A-Z)", self)
        self.uppercase_button.clicked.connect(self.uppercase_toggle)
        self.uppercase_button.setStyleSheet(
            "background-color: lightblue; color: black;" + button_style)

        self.lowercase_button = QPushButton("Строчные буквы (a-z)", self)
        self.lowercase_button.clicked.connect(self.lowercase_toggle)
        self.lowercase_button.setStyleSheet("background-color: lightblue; color: black;" + button_style)

        self.digits_button = QPushButton("Цифры (0-9)", self)
        self.digits_button.clicked.connect(self.digits_toggle)
        self.digits_button.setStyleSheet("background-color: lightblue; color: black; " + button_style)

        self.special_button = QPushButton("Специальные символы (!@#$%^&*)", self)
        self.special_button.clicked.connect(self.special_toggle)
        self.special_button.setStyleSheet("background-color: lightblue; color: black; " + button_style)

        # Создаем кнопку для генерации пароля.
        self.generate_button = QPushButton("Сгенерировать", self)
        self.generate_button.clicked.connect(self.generate_password)
        self.generate_button.setStyleSheet(button_style)

        # Создаем кнопку для копирования сгенерированного пароля в буфер обмена.
        self.copy_button = QPushButton("Скопировать", self)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setStyleSheet(button_style)

        # Создаем поле для ввода URL, связанного с паролем (необязательно).
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("URL...")
        self.url_input.setFont(QFont("Arial", 12))
        self.url_input.setStyleSheet(button_style)

        # Создаем вертикальный макет для размещения виджетов.
        layout = QVBoxLayout(self)
        layout.addWidget(self.password_display)
        layout.addSpacing(10)
        layout.addWidget(length_label)
        layout.addWidget(self.length_input)
        layout.addSpacing(10)
        layout.addWidget(self.uppercase_button)
        layout.addSpacing(10)
        layout.addWidget(self.lowercase_button)
        layout.addSpacing(10)
        layout.addWidget(self.digits_button)
        layout.addSpacing(10)
        layout.addWidget(self.special_button)
        layout.addSpacing(10)
        layout.addWidget(self.url_input)
        layout.addSpacing(10)
        layout.addWidget(self.generate_button)
        layout.addSpacing(10)
        layout.addWidget(self.copy_button)
        layout.addSpacing(40)

        self.setLayout(layout)  # макет для главного окна.

        # Инициализируем булевы переменные для отслеживания того, какие типы символов выбраны.
        self.use_uppercase = False
        self.use_lowercase = False
        self.use_digits = False
        self.use_special = False

    def generate_password(self):
        """
        Генерируем пароль на основе выбранных критериев (длина и типы символов).
        """
        length = self.length_input.value()  # Получаем длину пароля из спинбокса.

        # Проверяем, выбран ли хотя бы один тип символов. Если нет, выводим сообщение.
        if not (self.use_uppercase or self.use_lowercase or self.use_digits or self.use_special):
            self.password_display.setText("Выберите хотя бы одну опцию!")
            return

        characters = ''  # Пустая строку для хранения разрешенных символов.
        # Добавляем символы в строку 'characters' в зависимости от выбранных опций.
        if self.use_uppercase: characters += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if self.use_lowercase: characters += 'abcdefghijklmnopqrstuvwxyz'
        if self.use_digits: characters += '0123456789'
        if self.use_special: characters += '!@#$%^&*'

        # Генерируем пароль, случайным образом выбирая символы из строки 'characters'.
        password = ''.join(random.choice(characters) for _ in range(length))
        self.password_display.setText(password)  # Отображаем сгенерированный пароль в поле.

    def copy_to_clipboard(self):
        """
        Копирует сгенерированный пароль в буфер обмена и сохраняет его в базу данных вместе с URL (если он указан).
        """
        password = self.password_display.text()
        if password:
            pyperclip.copy(password)  # Копируем пароль в буфер обмена.
            url = self.url_input.text()  # Получаем URL из поля ввода.
            # Сохраняем пароль и URL (или "-", если URL не указан) в базу данных.
            if url:
                self.save_to_database(password, url)
            else:
                self.save_to_database(password, '-')

            # Показываем сообщение, подтверждающее, что пароль скопирован.
            QMessageBox.information(self, "Скопировано", "Пароль скопирован в буфер обмена!")
        else:
            # Показываем предупреждение, если нет пароля для копирования.
            QMessageBox.warning(self, "Ошибка", "Нет пароля для копирования!")

    def save_to_database(self, password, url):
        """
        Сохраняет переданный пароль и URL в базу данных 'passwords_database.db'.
        """
        try:
            conn = sqlite3.connect('passwords_database.db')
            cur = conn.cursor()
            # Выполняем SQL-запрос INSERT, чтобы добавить пароль и URL в таблицу 'passwords'.
            cur.execute("INSERT INTO passwords (password, url) VALUES (?, ?)", (password, url))
            conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        finally:
            # Гарантируем, что соединение с базой данных будет закрыто, даже если произошла ошибка.
            if 'conn' in locals() and conn: conn.close()

    def uppercase_toggle(self):
        """Переключает использование заглавных букв и обновляет стиль кнопки."""
        self.use_uppercase = not self.use_uppercase
        # Обновляем стиль кнопки, чтобы указать, выбрана она (зеленый) или нет (светло-синий).
        self.uppercase_button.setStyleSheet(
            f"background-color: {'green' if self.use_uppercase else 'lightblue'}; QPushButton "
            f"{{ padding: 15px; font-size: 16px; }}; {'color: black;' if not self.use_uppercase else ''}")

    def lowercase_toggle(self):
        """Переключает использование строчных букв и обновляет стиль кнопки."""
        self.use_lowercase = not self.use_lowercase
        self.lowercase_button.setStyleSheet(
            f"background-color: {'green' if self.use_lowercase else 'lightblue'}; QPushButton "
            f"{{ padding: 15px; font-size: 16px; }}; {'color: black;' if not self.use_lowercase else ''}")

    def digits_toggle(self):
        """Переключает использование цифр и обновляет стиль кнопки."""
        self.use_digits = not self.use_digits
        self.digits_button.setStyleSheet(
            f"background-color: {'green' if self.use_digits else 'lightblue'}; QPushButton "
            f"{{ padding: 15px; font-size: 16px; }}; {'color: black;' if not self.use_digits else ''}")

    def special_toggle(self):
        """Переключает использование специальных символов и обновляет стиль кнопки."""
        self.use_special = not self.use_special
        self.special_button.setStyleSheet(
            f"background-color: {'green' if self.use_special else 'lightblue'}; QPushButton "
            f"{{ padding: 15px; font-size: 16px; }}; {'color: black;' if not self.use_special else ''}")


class PasswordManager(QWidget):
    """
    Этот класс представляет собой часть приложения, отвечающую за управление паролями.
    Он отображает сохраненные пароли и связанные с ними URL из базы данных в таблице.
    """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Настраивает пользовательский интерфейс для менеджера паролей, включая таблицу
        для отображения паролей и кнопку для обновления данных в базе данных.
        """
        self.setWindowTitle("Password Manager")
        layout = QVBoxLayout(self)

        # Создаем таблицу для отображения паролей
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Устанавливаем 3 столбца: ID, Пароль, URL
        self.table.setHorizontalHeaderLabels(["ID", "Password", "URL"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection) # Разрешаем выделение только одной ячейки
        self.table.cellClicked.connect(self.on_cell_clicked) # Подключаем сигнал нажатия на ячейку к функции копирования
        layout.addWidget(self.table)

        # Создаем кнопку для обновления данных из базы данных
        self.refresh_button = QPushButton("Обновить базу данных", self)
        self.refresh_button.clicked.connect(self.load_data)
        self.refresh_button.setStyleSheet("QPushButton { padding: 10px; font-size: 14px; }")
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)  # Устанавливаем макет для виджета
        self.init_database()  # Инициализируем базу данных (создаем таблицу, если она не существует)
        self.load_data()  # Загружаем данные из базы данных в таблицу

    def on_cell_clicked(self, row, column):
        """
        Обрабатывает нажатия на ячейки в таблице. Копирует содержимое нажатой ячейки (пароль или URL) в буфер обмена.
        """
        item = self.table.item(row, column)
        if item is not None:
            if column == 1: # Если нажат столбец "Пароль"
                pyperclip.copy(item.text()) # Копируем пароль в буфер обмена
                QMessageBox.information(self, "Copied", "Password copied to clipboard!")
            elif column == 2:  # Если нажат столбец "URL"
                pyperclip.copy(item.text()) # Копируем URL в буфер обмена
                QMessageBox.information(self, "Copied", "URL copied to clipboard!")

    def init_database(self):
        """
        Инициализирует базу данных SQLite. Создает таблицу 'passwords', если она не существует,
        и вставляет две начальные записи, если таблица пуста.
        """
        try:
            conn = sqlite3.connect('passwords_database.db')
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS passwords (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            password TEXT NOT NULL, url TEXT)''')
            cur.execute("SELECT COUNT(*) FROM passwords")
            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO passwords (password, url) VALUES (?, ?)",
                            ("yDswHDDO7ppxvn$WAuA9!UScDIXoWbJ", "https://lmarena.ai/"))
                cur.execute("INSERT INTO passwords (password, url) VALUES (?, ?)",
                            ("9is@^x2mc!63ttP*k8oiARaJ", "yandex.lyceym.ru"))
                conn.commit()  # Фиксируем изменения

        except sqlite3.Error as e:
            # Обрабатываем любые ошибки базы данных
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        finally:
            # Закрываем соединение
            if 'conn' in locals() and conn: conn.close()

    def load_data(self):
        """
        Загружает данные из таблицы 'passwords' в базе данных и заполняет ими виджет таблицы.
        Делает ячейки таблицы нередактируемыми и изменяет размеры столбцов.
        """
        try:
            conn = sqlite3.connect('passwords_database.db')
            cur = conn.cursor()
            result = cur.execute("SELECT * FROM passwords")
            data = result.fetchall()

            self.table.setRowCount(len(data))  # Устанавливаем количество строк в таблице

            # Заполняем таблицу полученными данными
            for row_num, row_data in enumerate(data):
                for col_num, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))  # Создаем элемент таблицы с данными
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Делаем элемент нередактируемым
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter) #выравниваем текст по центру ячейки
                    self.table.setItem(row_num, col_num, item)  # Устанавливаем элемент в таблицу

            self.table.resizeColumnsToContents()  # Подгоняем ширину столбцов под содержимое
            if self.table.columnWidth(1) < 200: #если столбец с паролем слишком узкий, задаем минимальную ширину
                self.table.setColumnWidth(1, 200)

        except sqlite3.Error as e:
            # Обрабатываем ошибки базы данных
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        finally:
            # Закрываем соединение
            if 'conn' in locals() and conn: conn.close()


class Example(QWidget):
    """
    Этот класс является главным окном приложения. Он объединяет виджеты PasswordGeneratorApp
    и PasswordManager, а также несколько других примеров кнопок.
    """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1100, 550)
        self.setWindowTitle('Генератор паролей')
        main_layout = QHBoxLayout(self)

        # Создаем контейнер для кнопок в левой части со стилизацией
        button_container = QWidget()
        button_container.setStyleSheet(
            "background-color: lightblue; border: 2px solid black; padding: 10px; border-radius: 20px;")
        button_layout = QVBoxLayout(button_container)
        button_container.setFixedWidth(200)
        main_layout.addWidget(button_container)
        button_layout.addSpacing(50)


        self.btn1 = QPushButton('Хранилище паролей', self)
        self.btn1.setStyleSheet(
            "background-color: lightgreen; border: 2px solid; padding: 10px; color: black; border-radius: 20px")
        self.btn1.clicked.connect(self.on_btn1_click)
        button_layout.addWidget(self.btn1)
        button_layout.addSpacing(30)


        self.btn2 = QPushButton("Хранилище заметок", self)
        self.btn2.setStyleSheet(
            "background-color: lightgreen; border: 2px solid; padding: 10px; color: black; border-radius: 20px")
        self.btn2.clicked.connect(self.on_btn2_click)
        button_layout.addWidget(self.btn2)
        button_layout.addSpacing(20)


        self.btn3 = QPushButton("Кнопка 3", self)
        self.btn3.setStyleSheet("background-color: lightgreen; padding: 10px; color: black; border-radius: 20px")
        self.btn3.clicked.connect(self.on_btn3_click)
        button_layout.addWidget(self.btn3)
        button_layout.addStretch(1)

        # Создаем экземпляр PasswordManager и добавляем его в основной макет
        self.password_manager = PasswordManager()
        main_layout.addWidget(self.password_manager)

        # Создаем экземпляр PasswordGeneratorApp и добавляем его в основной макет
        self.password_generator = PasswordGeneratorApp()
        main_layout.addWidget(self.password_generator)

    def on_btn1_click(self):
        file_path = "Хранилище.txt"
        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            QMessageBox.information(self, "Файл не найден", "Файл не найден")
    def on_btn2_click(self):
        QMessageBox.information(self, "Хранилище заметок", "Хранилище заметок")

    def on_btn3_click(self):
        QMessageBox.information(self, "Кнопка номер 3", "Кнопка номер 3")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())