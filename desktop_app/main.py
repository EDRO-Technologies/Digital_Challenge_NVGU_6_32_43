"""
Desktop приложение для админа (PyQt6)
"""
import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QTabWidget,
    QComboBox, QLineEdit, QTextEdit, QDateEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QDate
from datetime import datetime
from typing import Optional

from config import API_HOST, API_PORT, API_SECRET_KEY

API_BASE_URL = f"http://{API_HOST}:{API_PORT}"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Панель администратора - Расписание")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Вкладки
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Вкладка заявок
        requests_tab = self.create_requests_tab()
        tabs.addTab(requests_tab, "Заявки")
        
        # Вкладка уведомлений
        notifications_tab = self.create_notifications_tab()
        tabs.addTab(notifications_tab, "Уведомления")
        
        # Вкладка истории
        logs_tab = self.create_logs_tab()
        tabs.addTab(logs_tab, "История действий")
        
        # Вкладка управления преподавателями
        teachers_tab = self.create_teachers_tab()
        tabs.addTab(teachers_tab, "Преподаватели")
        
        # Таймер для обновления данных
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)  # Обновление каждые 30 секунд
        
        # Загрузка данных при запуске
        self.refresh_data()
    
    def create_requests_tab(self) -> QWidget:
        """Создать вкладку заявок"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Фильтры
        filters_layout = QHBoxLayout()
        
        status_filter = QComboBox()
        status_filter.addItems(["Все", "Новые", "Принятые", "Отклоненные"])
        filters_layout.addWidget(QLabel("Статус:"))
        filters_layout.addWidget(status_filter)
        
        date_filter = QDateEdit()
        date_filter.setCalendarPopup(True)
        filters_layout.addWidget(QLabel("Дата:"))
        filters_layout.addWidget(date_filter)
        
        teacher_filter = QComboBox()
        teacher_filter.addItem("Все преподаватели")
        filters_layout.addWidget(QLabel("Преподаватель:"))
        filters_layout.addWidget(teacher_filter)
        
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.refresh_requests)
        filters_layout.addWidget(refresh_btn)
        
        filters_layout.addStretch()
        layout.addLayout(filters_layout)
        
        # Таблица заявок
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(6)
        self.requests_table.setHorizontalHeaderLabels([
            "ID", "Преподаватель", "Тип", "Статус", "Дата создания", "Действия"
        ])
        self.requests_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.requests_table)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        
        approve_btn = QPushButton("Одобрить")
        approve_btn.clicked.connect(self.approve_request)
        actions_layout.addWidget(approve_btn)
        
        reject_btn = QPushButton("Отклонить")
        reject_btn.clicked.connect(self.reject_request)
        actions_layout.addWidget(reject_btn)
        
        view_btn = QPushButton("Просмотр")
        view_btn.clicked.connect(self.view_request_details)
        actions_layout.addWidget(view_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        return widget
    
    def create_notifications_tab(self) -> QWidget:
        """Создать вкладку уведомлений"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Фильтры
        filters_layout = QHBoxLayout()
        
        status_filter = QComboBox()
        status_filter.addItems(["Все", "Непрочитанные", "Прочитанные"])
        filters_layout.addWidget(QLabel("Статус:"))
        filters_layout.addWidget(status_filter)
        
        mark_all_read_btn = QPushButton("Отметить все как прочитанные")
        mark_all_read_btn.clicked.connect(self.mark_all_notifications_read)
        filters_layout.addWidget(mark_all_read_btn)
        
        filters_layout.addStretch()
        layout.addLayout(filters_layout)
        
        # Таблица уведомлений
        self.notifications_table = QTableWidget()
        self.notifications_table.setColumnCount(4)
        self.notifications_table.setHorizontalHeaderLabels([
            "ID", "Сообщение", "Статус", "Дата"
        ])
        layout.addWidget(self.notifications_table)
        
        return widget
    
    def create_logs_tab(self) -> QWidget:
        """Создать вкладку истории"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Таблица истории
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(5)
        self.logs_table.setHorizontalHeaderLabels([
            "ID", "Действие", "Описание", "Дата", "Админ"
        ])
        layout.addWidget(self.logs_table)
        
        return widget
    
    def create_teachers_tab(self) -> QWidget:
        """Создать вкладку управления преподавателями"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Форма добавления преподавателя
        form_layout = QVBoxLayout()
        
        teacher_id_input = QLineEdit()
        teacher_id_input.setPlaceholderText("Telegram ID преподавателя")
        form_layout.addWidget(QLabel("Telegram ID:"))
        form_layout.addWidget(teacher_id_input)
        
        teacher_name_input = QLineEdit()
        teacher_name_input.setPlaceholderText("Имя преподавателя")
        form_layout.addWidget(QLabel("Имя:"))
        form_layout.addWidget(teacher_name_input)
        
        add_teacher_btn = QPushButton("Добавить преподавателя")
        form_layout.addWidget(add_teacher_btn)
        
        layout.addLayout(form_layout)
        
        # Таблица преподавателей
        self.teachers_table = QTableWidget()
        self.teachers_table.setColumnCount(3)
        self.teachers_table.setHorizontalHeaderLabels([
            "ID", "Имя", "Действия"
        ])
        layout.addWidget(self.teachers_table)
        
        return widget
    
    def get_headers(self) -> dict:
        """Получить заголовки для API запросов"""
        return {"X-API-Key": API_SECRET_KEY}
    
    def refresh_data(self):
        """Обновить все данные"""
        self.refresh_requests()
        self.refresh_notifications()
        self.refresh_logs()
    
    def refresh_requests(self):
        """Обновить список заявок"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/requests",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                requests_data = response.json()
                self.requests_table.setRowCount(len(requests_data))
                for row, req in enumerate(requests_data):
                    self.requests_table.setItem(row, 0, QTableWidgetItem(str(req['id'])))
                    self.requests_table.setItem(row, 1, QTableWidgetItem(str(req.get('teacher_id', ''))))
                    self.requests_table.setItem(row, 2, QTableWidgetItem(req.get('request_type', '')))
                    self.requests_table.setItem(row, 3, QTableWidgetItem(req.get('status', '')))
                    self.requests_table.setItem(row, 4, QTableWidgetItem(str(req.get('created_at', ''))))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить заявки: {e}")
    
    def refresh_notifications(self):
        """Обновить уведомления"""
        # TODO: Реализовать
        pass
    
    def refresh_logs(self):
        """Обновить историю"""
        # TODO: Реализовать
        pass
    
    def approve_request(self):
        """Одобрить выбранную заявку"""
        selected = self.requests_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заявку")
            return
        
        request_id = int(self.requests_table.item(selected, 0).text())
        # TODO: Показать диалог для выбора даты/времени/аудитории
        # TODO: Отправить запрос на одобрение
    
    def reject_request(self):
        """Отклонить выбранную заявку"""
        selected = self.requests_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заявку")
            return
        
        request_id = int(self.requests_table.item(selected, 0).text())
        # TODO: Показать диалог для комментария
        # TODO: Отправить запрос на отклонение
    
    def view_request_details(self):
        """Просмотр деталей заявки"""
        selected = self.requests_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заявку")
            return
        
        # TODO: Показать детали заявки в диалоге
    
    def mark_all_notifications_read(self):
        """Отметить все уведомления как прочитанные"""
        # TODO: Реализовать
        pass


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

