import sys
import random
import pyperclip
from PyQt6 import QtWidgets
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLabel, QMessageBox, QLineEdit,
                             QSpinBox, QTableWidget, QTableWidgetItem, QFrame)
from PyQt6.QtCore import Qt
import os
import sqlite3


class PasswordGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Генератор паролей")
        self.setMinimumSize(400, 600)

        # Стиль для приложения
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: 'Segoe UI';
            }
            QLineEdit {
                background-color: #3c3f41;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                font-size: 16px;
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #3c3f41;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 10px;
                min-width: 100px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #4e5254;
                border: 1px solid #666;
            }
            QPushButton:pressed {
                background-color: #2b2b2b;
            }
            QSpinBox {
                background-color: #3c3f41;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                color: #e0e0e0;
            }
            QLabel {
                font-size: 14px;
                color: #bbbbbb;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Заголовок
        title = QLabel("Генератор паролей")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #6d9eeb;")
        main_layout.addWidget(title)

        # Поле для пароля
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setFont(QFont("Consolas", 18))
        self.password_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_display.setPlaceholderText("Ваш пароль появится здесь")
        self.password_display.setStyleSheet("""
            QLineEdit {
                background-color: #3c3f41;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 12px;
                font-size: 18px;
                color: #6d9eeb;
            }
        """)
        main_layout.addWidget(self.password_display)

        # Настройки пароля
        settings_frame = QFrame()
        settings_frame.setFrameShape(QFrame.Shape.StyledPanel)
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setContentsMargins(15, 15, 15, 15)
        settings_layout.setSpacing(15)

        # Длина пароля
        length_layout = QHBoxLayout()
        length_label = QLabel("Длина пароля:")
        length_label.setFont(QFont("Segoe UI", 12))
        self.length_input = QSpinBox()
        self.length_input.setRange(6, 64)
        self.length_input.setValue(16)
        self.length_input.setFont(QFont("Segoe UI", 12))
        length_layout.addWidget(length_label)
        length_layout.addWidget(self.length_input)
        settings_layout.addLayout(length_layout)

        # Кнопки выбора символов
        self.uppercase_button = self.create_toggle_button("Заглавные буквы (A-Z)")
        self.lowercase_button = self.create_toggle_button("Строчные буквы (a-z)")
        self.digits_button = self.create_toggle_button("Цифры (0-9)")
        self.special_button = self.create_toggle_button("Спецсимволы (!@#$%^&*)")

        settings_layout.addWidget(self.uppercase_button)
        settings_layout.addWidget(self.lowercase_button)
        settings_layout.addWidget(self.digits_button)
        settings_layout.addWidget(self.special_button)

        main_layout.addWidget(settings_frame)

        # Поле для URL
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL (необязательно)")
        self.url_input.setFont(QFont("Segoe UI", 12))
        main_layout.addWidget(self.url_input)

        # Кнопки действий
        buttons_layout = QHBoxLayout()
        self.generate_button = QPushButton("Сгенерировать")
        self.generate_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #6d9eeb;
                color: #ffffff;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #7daeff;
            }
        """)
        self.generate_button.clicked.connect(self.generate_password)

        self.copy_button = QPushButton("Копировать")
        self.copy_button.setFont(QFont("Segoe UI", 12))
        self.copy_button.clicked.connect(self.copy_to_clipboard)

        buttons_layout.addWidget(self.generate_button)
        buttons_layout.addWidget(self.copy_button)
        main_layout.addLayout(buttons_layout)

        # Инициализация состояний
        self.use_uppercase = True
        self.use_lowercase = True
        self.use_digits = True
        self.use_special = True
        self.update_button_styles()

    def create_toggle_button(self, text):
        button = QPushButton(text)
        button.setCheckable(True)
        button.setChecked(True)
        button.setFont(QFont("Segoe UI", 11))
        button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                text-align: left;
                border-radius: 5px;
            }
            QPushButton:checked {
                background-color: #4a6da7;
                color: white;
            }
        """)
        button.clicked.connect(self.update_button_styles)
        return button

    def update_button_styles(self):
        self.use_uppercase = self.uppercase_button.isChecked()
        self.use_lowercase = self.lowercase_button.isChecked()
        self.use_digits = self.digits_button.isChecked()
        self.use_special = self.special_button.isChecked()

    def generate_password(self):
        length = self.length_input.value()

        if not (self.use_uppercase or self.use_lowercase or self.use_digits or self.use_special):
            self.password_display.setText("Выберите хотя бы одну опцию!")
            return

        characters = ''
        if self.use_uppercase: characters += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if self.use_lowercase: characters += 'abcdefghijklmnopqrstuvwxyz'
        if self.use_digits: characters += '0123456789'
        if self.use_special: characters += '!@#$%^&*'

        password = ''.join(random.choice(characters) for _ in range(length))
        self.password_display.setText(password)

    def copy_to_clipboard(self):
        password = self.password_display.text()
        if password:
            pyperclip.copy(password)
            url = self.url_input.text()
            if url:
                self.save_to_database(password, url)
            else:
                self.save_to_database(password, '-')

            # Красивое всплывающее сообщение
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Успешно")
            msg.setText("Пароль скопирован в буфер обмена!")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2b2b2b;
                }
                QLabel {
                    color: #e0e0e0;
                }
            """)
            msg.exec()
        else:
            QMessageBox.warning(self, "Ошибка", "Нет пароля для копирования!")

    def save_to_database(self, password, url):
        try:
            conn = sqlite3.connect('passwords_database.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO passwords (password, url) VALUES (?, ?)", (password, url))
            conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()


class PasswordManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Менеджер паролей")
        self.setMinimumSize(600, 400)

        # Стиль для виджета
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: 'Segoe UI';
            }
            QTableWidget {
                background-color: #3c3f41;
                border: 1px solid #555;
                gridline-color: #555;
                font-size: 17px;
            }
            QHeaderView::section {
                background-color: #3c3f41;
                padding: 5px;
                border: 1px solid #555;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #4a6da7;
                color: white;
            }
            QPushButton {
                background-color: #3c3f41;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                min-width: 100px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #4e5254;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("Менеджер паролей")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #6d9eeb;")
        layout.addWidget(title)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Пароль", "URL"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.setStyleSheet("""
            QTableWidget {
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.table)

        # Кнопка обновления
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.setFont(QFont("Segoe UI", 12))
        self.refresh_button.clicked.connect(self.load_data)
        layout.addWidget(self.refresh_button)

        self.init_database()
        self.load_data()

    def on_cell_clicked(self, row, column):
        item = self.table.item(row, column)
        if item is not None:
            text = item.text()
            pyperclip.copy(text)

            # Создаем красивый тултип
            tooltip = QLabel(self)
            tooltip.setText("Скопировано!" if column == 1 else "URL скопирован!")
            tooltip.setStyleSheet("""
                QLabel {
                    background-color: #4a6da7;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                }
            """)
            tooltip.adjustSize()

            # Позиционируем тултип рядом с курсором
            pos = self.table.viewport().mapToGlobal(self.table.visualItemRect(item).topLeft())
            tooltip.move(pos.x(), pos.y() - 30)
            tooltip.show()

            # Убираем тултип через 1 секунду
            QtWidgets.QTimer.singleShot(1000, tooltip.deleteLater)

    def init_database(self):
        try:
            conn = sqlite3.connect('passwords_database.db')
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS passwords 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          password TEXT NOT NULL, 
                          url TEXT)''')
            cur.execute("SELECT COUNT(*) FROM passwords")
            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO passwords (password, url) VALUES (?, ?)",
                            ("yDswHDDO7ppxvn$WAuA9!UScDIXoWbJ", "https://lmarena.ai/"))
                cur.execute("INSERT INTO passwords (password, url) VALUES (?, ?)",
                            ("9is@^x2mc!63ttP*k8oiARaJ", "yandex.lyceym.ru"))
                conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    def load_data(self):
        try:
            conn = sqlite3.connect('passwords_database.db')
            cur = conn.cursor()
            result = cur.execute("SELECT * FROM passwords")
            data = result.fetchall()

            self.table.setRowCount(len(data))
            self.table.setColumnCount(3)

            for row_num, row_data in enumerate(data):
                for col_num, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Разные цвета для разных столбцов
                    if col_num == 1:  # Пароль
                        item.setForeground(QColor("#6d9eeb"))
                    elif col_num == 2:  # URL
                        item.setForeground(QColor("#a5c261"))

                    self.table.setItem(row_num, col_num, item)

            self.table.resizeColumnsToContents()
            if self.table.columnWidth(1) < 200:
                self.table.setColumnWidth(1, 200)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Менеджер паролей')
        self.setGeometry(200, 100, 1000, 600)

        # Темная тема для всего приложения
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(43, 43, 43))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(109, 158, 235))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        QApplication.setPalette(dark_palette)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Боковая панель
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-right: 1px solid #444;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 15px 20px;
                font-size: 14px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #3c3f41;
            }
            QPushButton:pressed {
                background-color: #4a6da7;
            }
        """)
        sidebar.setFixedWidth(200)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Логотип
        logo = QLabel("Password Manager")
        logo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("""
            QLabel {
                color: #6d9eeb;
                padding: 20px 0;
                border-bottom: 1px solid #444;
            }
        """)
        sidebar_layout.addWidget(logo)

        # Кнопки навигации
        self.btn_generator = QPushButton("Генератор паролей")
        self.btn_generator.setIcon(QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon))
        self.btn_generator.clicked.connect(self.show_generator)

        self.btn_manager = QPushButton("Хранилище паролей")
        self.btn_manager.setIcon(QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirIcon))
        self.btn_manager.clicked.connect(self.show_manager)

        self.btn_notes = QPushButton("Хранилище заметок")
        self.btn_notes.setIcon(
            QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.btn_notes.clicked.connect(self.show_notes)

        sidebar_layout.addWidget(self.btn_generator)
        sidebar_layout.addWidget(self.btn_manager)
        sidebar_layout.addWidget(self.btn_notes)
        sidebar_layout.addStretch()

        # Основная область
        self.stack = QtWidgets.QStackedWidget()

        # Создаем и добавляем виджеты
        self.password_generator = PasswordGeneratorApp()
        self.password_manager = PasswordManager()

        self.stack.addWidget(self.password_generator)
        self.stack.addWidget(self.password_manager)

        # Добавляем виджеты в основной макет
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        # Показываем генератор по умолчанию
        self.show_generator()

    def show_generator(self):
        self.stack.setCurrentIndex(0)
        self.btn_generator.setStyleSheet("background-color: #4a6da7;")
        self.btn_manager.setStyleSheet("background-color: transparent;")
        self.btn_notes.setStyleSheet("background-color: transparent;")

    def show_manager(self):
        self.stack.setCurrentIndex(1)
        self.password_manager.load_data()
        self.btn_generator.setStyleSheet("background-color: transparent;")
        self.btn_manager.setStyleSheet("background-color: #4a6da7;")
        self.btn_notes.setStyleSheet("background-color: transparent;")

    def show_notes(self):
        QMessageBox.information(self, "Хранилище заметок", "Эта функция в разработке")
        self.btn_generator.setStyleSheet("background-color: transparent;")
        self.btn_manager.setStyleSheet("background-color: transparent;")
        self.btn_notes.setStyleSheet("background-color: #4a6da7;")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Устанавливаем стиль Fusion для более современного вида
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
