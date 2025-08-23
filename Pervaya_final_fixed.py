import sys
import sqlite3
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QDialogButtonBox,
    QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton, QRadioButton, QButtonGroup,
    QMessageBox, QGridLayout, QFrame, QGroupBox, QProgressBar, QLineEdit, QTabWidget, QWidget, QFormLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход / Регистрация")
        self.setModal(True)
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.login_tab = QWidget()
        self.register_tab = QWidget()

        # Вкладка входа
        login_layout = QFormLayout()
        self.login_username = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        login_layout.addRow("Логин:", self.login_username)
        login_layout.addRow("Пароль:", self.login_password)
        self.login_tab.setLayout(login_layout)

        # Вкладка регистрации
        register_layout = QFormLayout()
        self.register_fio = QLineEdit()
        self.register_username = QLineEdit()
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_confirm_password = QLineEdit()
        self.register_confirm_password.setEchoMode(QLineEdit.Password)
        register_layout.addRow("ФИО:", self.register_fio)
        register_layout.addRow("Логин:", self.register_username)
        register_layout.addRow("Пароль:", self.register_password)
        register_layout.addRow("Подтвердите пароль:", self.register_confirm_password)
        self.register_tab.setLayout(register_layout)

        self.tabs.addTab(self.login_tab, "Вход")
        self.tabs.addTab(self.register_tab, "Регистрация")

        # Кнопки
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        self.buttons.accepted.connect(self.validate)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.tabs)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def validate(self):
        if self.tabs.currentIndex() == 0:  # Вход
            username = self.login_username.text().strip()
            password = self.login_password.text().strip()
            if not username or not password:
                QMessageBox.warning(self, "Ошибка", "Заполните все поля")
                return
            conn = sqlite3.connect('study_app.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                self.user_data = {
                    'id': user[0],
                    'fio': user[1],
                    'username': user[2],
                    'score': user[4]
                }
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
        else:  # Регистрация
            fio = self.register_fio.text().strip()
            username = self.register_username.text().strip()
            password = self.register_password.text().strip()
            confirm_password = self.register_confirm_password.text().strip()
            if not all([fio, username, password, confirm_password]):
                QMessageBox.warning(self, "Ошибка", "Заполните все поля")
                return
            if password != confirm_password:
                QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
                return
            conn = sqlite3.connect('study_app.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")
                conn.close()
                return
            cursor.execute("INSERT INTO users (fio, username, password, score) VALUES (?, ?, ?, 0)",
                           (fio, username, password))
            conn.commit()
            cursor.execute("SELECT id, fio, username, score FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            conn.close()
            self.user_data = {
                'id': user[0],
                'fio': user[1],
                'username': user[2],
                'score': user[3]
            }
            self.accept()

class StudyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информатика: Python, JavaScript, CSS")
        self.setGeometry(100, 100, 900, 700)
        
        # Настройка цветовой палитры
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
        palette.setColor(QPalette.Highlight, QColor(100, 150, 200))
        self.setPalette(palette)
        
        # Инициализация таймера
        self.timer = QTimer(self)
        self.time_left = 60
        
        # Остальной код инициализации...
        self.tabs = QTabWidget()
        # ... остальной код метода __init__
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                padding: 10px;
                font-size: 14px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: #6495ED;
                color: white;
            }
        """)
        
        # Главный экран с иконками
        self.main_screen = self.create_main_screen()
        
        # Добавляем вкладки для изучения
        self.python_tab = self.create_language_tab("Python")
        self.javascript_tab = self.create_language_tab("JavaScript")
        self.css_tab = self.create_language_tab("CSS")
        
        # Вкладка с викториной
        self.quiz_tab = self.create_quiz_tab()
        
        # Добавляем вкладки
        self.tabs.addTab(self.main_screen, "Главная")
        self.tabs.addTab(self.python_tab, "Python")
        self.tabs.addTab(self.javascript_tab, "JavaScript")
        self.tabs.addTab(self.css_tab, "CSS")
        self.tabs.addTab(self.quiz_tab, "Викторина")
        self.profile_tab = self.create_profile_tab()
        self.tabs.addTab(self.profile_tab, "Профиль")
        
        self.setCentralWidget(self.tabs)
        self.load_study_materials()
        self.load_quiz_questions()
        # Вход пользователя
        self.user_data = None
        self.show_login_dialog()

        self.current_question = 0
        self.score = 0
        self.show_question()
        
        # Таймер для викторины
        self.time_left = 60
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
    
    def create_main_screen(self):
        """Создает главный экран с иконками"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Изучение информатики")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #4169E1; margin-bottom: 30px;")
        layout.addWidget(title)

        avatar = QLabel()
        avatar.setPixmap(QPixmap(":/icons/avatar.png").scaled(80, 80))
        avatar.setAlignment(Qt.AlignCenter)
        layout.addWidget(avatar)

        
        grid = QGridLayout()
        grid.setSpacing(30)
        grid.setContentsMargins(50, 20, 50, 50)
        
        cards = [
            {"name": "Python", "icon": "🐍", "desc": "Основы программирования", "size": "750 MB", "color": "#FF6347"},
            {"name": "JavaScript", "icon": "📜", "desc": "Веб-программирование", "size": "248 MB", "color": "#FFD700"},
            {"name": "CSS", "icon": "🎨", "desc": "Стилизация веб-страниц", "size": "687 MB", "color": "#9370DB"},
            {"name": "Викторина", "icon": "❓", "desc": "Проверка знаний", "size": "120 вопросов", "color": "#20B2AA"}
        ]
        
        for i, card in enumerate(cards):
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setLineWidth(2)
            frame.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-radius: 10px;
                    border: 2px solid {card['color']};
                }}
            """)
            frame.setMinimumSize(250, 250)
            
            card_layout = QVBoxLayout()
            card_layout.setAlignment(Qt.AlignCenter)
            
            # Иконка
            icon = QLabel(card["icon"])
            icon.setFont(QFont("Arial", 64))
            icon.setAlignment(Qt.AlignCenter)
            icon.setStyleSheet(f"color: {card['color']}; margin-bottom: 10px;")
            card_layout.addWidget(icon)
            
            # Название
            name = QLabel(card["name"])
            name.setFont(QFont("Arial", 16, QFont.Bold))
            name.setAlignment(Qt.AlignCenter)
            name.setStyleSheet(f"color: {card['color']};")
            card_layout.addWidget(name)
            
            # Описание
            desc = QLabel(card["desc"])
            desc.setFont(QFont("Arial", 12))
            desc.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(desc)
            
            # Размер
            size = QLabel(card["size"])
            size.setFont(QFont("Arial", 10))
            size.setAlignment(Qt.AlignCenter)
            size.setStyleSheet("color: #666; margin-top: 10px;")
            card_layout.addWidget(size)
            
            # Кнопка
            btn = QPushButton("Открыть")
            btn.setFixedSize(120, 40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {card['color']};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: {self.darken_color(card['color'])};
                }}
            """)
            btn.clicked.connect(lambda _, idx=i+1: self.tabs.setCurrentIndex(idx))
            card_layout.addWidget(btn, alignment=Qt.AlignCenter)
            
            frame.setLayout(card_layout)
            grid.addWidget(frame, i//2, i%2)
        
        layout.addLayout(grid)
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def darken_color(self, hex_color, factor=0.8):
        """Затемняет цвет для эффекта hover"""
        color = QColor(hex_color)
        return color.darker(int(100 + (100 * (1 - factor)))).name()
    
    def create_language_tab(self, language):
        """Создает вкладку для изучения языка"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel(f"Изучение {language}")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #4169E1; margin-bottom: 20px;")
        layout.addWidget(title)

        avatar = QLabel()
        avatar.setPixmap(QPixmap(":/icons/avatar.png").scaled(80, 80))
        avatar.setAlignment(Qt.AlignCenter)
        layout.addWidget(avatar)

        
        # Кнопка возврата
        back_btn = QPushButton("← На главную")
        back_btn.setFixedSize(150, 40)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #6495ED;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #4169E1;
            }
        """)
        back_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(0))
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)
        
        # Область с учебным материалом
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont("Consolas", 12))
        self.text_area.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.text_area)
        
        # Кнопки навигации (для CSS и JavaScript)
        if language != "Python":
            nav_layout = QHBoxLayout()
            prev_btn = QPushButton("◄ Назад")
            next_btn = QPushButton("Вперед ►")
            
            for btn in [prev_btn, next_btn]:
                btn.setFixedSize(120, 40)
                btn.setStyleSheet("""
                    QPushButton {
                        background: #6495ED;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: #4169E1;
                    }
                """)
            
            prev_btn.clicked.connect(lambda: self.navigate_material(language, -1))
            next_btn.clicked.connect(lambda: self.navigate_material(language, 1))
            
            nav_layout.addWidget(prev_btn)
            nav_layout.addWidget(next_btn)
            layout.addLayout(nav_layout)
        
        tab.setLayout(layout)
        return tab
    
    def create_quiz_tab(self):
        """Создает вкладку с викториной"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Группа для оформления
        quiz_box = QGroupBox()
        quiz_box.setStyleSheet("""
            QGroupBox {
                background: white;
                border: 2px solid #6495ED;
                border-radius: 10px;
                padding: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #4169E1;
            }
        """)
        box_layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Проверка знаний")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #4169E1; margin-bottom: 20px;")
        box_layout.addWidget(title)

        avatar = QLabel()
        avatar.setPixmap(QPixmap(":/icons/avatar.png").scaled(80, 80))
        avatar.setAlignment(Qt.AlignCenter)
        layout.addWidget(avatar)

        
        # Кнопка возврата
        back_btn = QPushButton("← На главную")
        back_btn.setFixedSize(150, 40)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #6495ED;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #4169E1;
            }
        """)
        back_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(0))
        box_layout.addWidget(back_btn, alignment=Qt.AlignLeft)
        
        # Таймер и баллы
        info_layout = QHBoxLayout()
        
        # Таймер
        self.time_label = QLabel("Время: 60 сек")
        self.time_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.time_label.setStyleSheet("color: #FF6347;")
        info_layout.addWidget(self.time_label)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 60)
        self.progress_bar.setValue(60)
        self.progress_bar.setFormat("%v сек")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background: #FF6347;
            }
        """)
        info_layout.addWidget(self.progress_bar)
        
        # Баллы
        self.points_label = QLabel("Баллы: 0")
        self.points_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.points_label.setStyleSheet("color: #4169E1;")
        info_layout.addWidget(self.points_label)
        
        box_layout.addLayout(info_layout)
        
        # Вопрос
        self.question_label = QLabel()
        self.question_label.setFont(QFont("Arial", 14))
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("""
            QLabel {
                background: #F0F8FF;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                margin: 15px 0;
            }
        """)
        box_layout.addWidget(self.question_label)
        
        # Варианты ответов
        options_group = QGroupBox("Варианты ответов:")
        options_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #4169E1;
            }
        """)
        options_layout = QVBoxLayout()
        
        self.option1 = QRadioButton()
        self.option2 = QRadioButton()
        self.option3 = QRadioButton()
        self.option4 = QRadioButton()
        
        for i, option in enumerate([self.option1, self.option2, self.option3, self.option4]):
            option.setFont(QFont("Arial", 12))
            option.setStyleSheet("""
                QRadioButton {
                    padding: 10px;
                    margin: 5px;
                    border-radius: 5px;
                }
                QRadioButton:hover {
                    background: #F0F8FF;
                }
            """)
            options_layout.addWidget(option)
        
        options_group.setLayout(options_layout)
        box_layout.addWidget(options_group)
        
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.option1)
        self.button_group.addButton(self.option2)
        self.button_group.addButton(self.option3)
        self.button_group.addButton(self.option4)
        
        # Кнопки навигации
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("◄ Предыдущий вопрос")
        self.next_btn = QPushButton("Следующий вопрос ►")
        self.submit_btn = QPushButton("✅ Проверить")
        
        for btn in [self.prev_btn, self.next_btn, self.submit_btn]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background: #6495ED;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    padding: 0 15px;
                }
                QPushButton:hover {
                    background: #4169E1;
                }
                QPushButton:disabled {
                    background: #cccccc;
                }
            """)
        
        self.prev_btn.clicked.connect(self.prev_question)
        self.next_btn.clicked.connect(self.next_question)
        self.submit_btn.clicked.connect(self.check_answer)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.submit_btn)
        nav_layout.addWidget(self.next_btn)
        box_layout.addLayout(nav_layout)
        
        # Результаты
        self.result_label = QLabel()
        self.result_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.result_label.setStyleSheet("color: #4169E1;")
        self.result_label.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(self.result_label)
        
        quiz_box.setLayout(box_layout)
        layout.addWidget(quiz_box)
        tab.setLayout(layout)
        return tab
    
    def load_study_materials(self):
        """Загружает учебные материалы для каждого языка"""
        # Материалы по Python (остаются без изменений)
        python_material = """
        <h2>Основы Python</h2>
        <p>Python — это высокоуровневый язык программирования с простой синтаксической структурой.</p>

        <h3>1. Переменные и типы данных</h3>
        <pre><code>
x = 5               # целое число
y = 3.14            # число с плавающей точкой
name = "Alice"      # строка
is_active = True    # булево значение
numbers = [1, 2, 3] # список
info = {"age": 25}  # словарь
        </code></pre>

        <h3>2. Условия</h3>
        <pre><code>
if x > 10:
    print("Больше 10")
elif x == 10:
    print("Равно 10")
else:
    print("Меньше 10")
        </code></pre>

        <h3>3. Циклы</h3>
        <pre><code>
# Цикл for
for i in range(5):
    print(i)

# Цикл while
count = 0
while count < 5:
    print(count)
    count += 1
        </code></pre>

        <h3>4. Функции</h3>
        <pre><code>
def greet(name):
    return f"Привет, {name}!"

print(greet("Мир"))
        </code></pre>

        <h3>5. Классы и объекты</h3>
        <pre><code>
class Person:
    def __init__(self, name):
        self.name = name

    def say_hello(self):
        print(f"Привет, меня зовут {self.name}")

user = Person("Анна")
user.say_hello()
        </code></pre>
"""
        self.python_tab.findChild(QTextEdit).setHtml(python_material)
        
        # Расширенные материалы по JavaScript
        self.javascript_materials = [
            """
            <h2>JavaScript: Основы</h2>
            <p>JavaScript - это язык программирования для создания интерактивных веб-страниц.</p>
            
            <h3>1. Переменные и типы данных</h3>
            <pre><code>// Объявление переменных
let name = "Alice";         // строка
const age = 25;             // число (неизменяемое)
var isActive = true;        // булево значение

// Типы данных
let num = 42;               // число
let str = "Hello";          // строка
let bool = true;            // boolean
let obj = {x: 10, y: 20};  // объект
let arr = [1, 2, 3];       // массив
let nothing = null;         // null
let notDefined;             // undefined</code></pre>
            
            <h3>2. Функции и область видимости</h3>
            <pre><code>// Объявление функций
function greet(name) {
    return `Hello, ${name}!`;
}

// Стрелочные функции (ES6+)
const add = (a, b) => a + b;

// Область видимости
let globalVar = "I'm global";

function testScope() {
    let localVar = "I'm local";
    console.log(globalVar); // доступно
    console.log(localVar);  // доступно
}

console.log(localVar); // Ошибка - не определено</code></pre>
            """,
            """
            <h3>3. Работа с DOM</h3>
            <pre><code>// Получение элементов
const btn = document.getElementById('myButton');
const items = document.querySelectorAll('.item');

// Обработка событий
btn.addEventListener('click', function() {
    console.log('Button clicked!');
});

// Изменение DOM
const div = document.createElement('div');
div.textContent = 'New element';
document.body.appendChild(div);

// Манипуляции со стилями
const elem = document.querySelector('#someElement');
elem.style.color = 'red';
elem.classList.add('active');</code></pre>
            
            <h3>4. Асинхронный JavaScript</h3>
            <pre><code>// Callbacks
function fetchData(callback) {
    setTimeout(() => {
        callback('Data received');
    }, 1000);
}

// Promises
fetch('https://api.example.com/data')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));

// Async/await
async function getData() {
    try {
        const response = await fetch('https://api.example.com/data');
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.error(error);
    }
}</code></pre>
            """,
            """
            <h3>5. Современный JavaScript (ES6+)</h3>
            <pre><code>// Деструктуризация
const person = {name: 'Alice', age: 25};
const {name, age} = person;

// Оператор расширения
const arr1 = [1, 2, 3];
const arr2 = [...arr1, 4, 5];

// Шаблонные строки
const greeting = `Hello, ${name}! You are ${age} years old.`;

// Классы
class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
    
    greet() {
        console.log(`Hello, my name is ${this.name}`);
    }
}</code></pre>
            """
        ]
        self.javascript_tab.findChild(QTextEdit).setHtml(self.javascript_materials[0])
        
        # Расширенные материалы по CSS
        self.css_materials = [
            """
            <h2>CSS: Основы</h2>
            <p>CSS (Cascading Style Sheets) - язык стилей для оформления HTML-документов.</p>
            
            <h3>1. Синтаксис и селекторы</h3>
            <pre><code>/* Базовый синтаксис */
селектор {
    свойство: значение;
    свойство: значение;
}

/* Типы селекторов */
#header { }              /* по id */
.menu { }                /* по классу */
div { }                  /* по тегу */
a:hover { }              /* псевдокласс */
p::first-line { }        /* псевдоэлемент */
[type="text"] { }        /* по атрибуту */

/* Комбинирование селекторов */
nav a { }                /* потомки */
div > p { }              /* прямые потомки */
h1 + p { }               /* соседний элемент */
h2 ~ p { }               /* все соседние элементы */</code></pre>
            
            <h3>2. Блочная модель и позиционирование</h3>
            <pre><code>/* Блочная модель */
.box {
    width: 300px;
    height: 200px;
    padding: 20px;
    border: 5px solid #333;
    margin: 10px;
    box-sizing: border-box; /* учитывает padding и border в width */
}

/* Позиционирование */
.static { position: static; }    /* по умолчанию */
.relative { position: relative; top: 10px; left: 20px; }
.absolute { position: absolute; top: 0; right: 0; }
.fixed { position: fixed; bottom: 20px; right: 20px; }
.sticky { position: sticky; top: 0; }</code></pre>
            """,
            """
            <h3>3. Flexbox и Grid</h3>
            <pre><code>/* Flexbox */
.container {
    display: flex;
    flex-direction: row; /* или column */
    justify-content: center; /* выравнивание по главной оси */
    align-items: center; /* выравнивание по поперечной оси */
    gap: 10px;
}

.item {
    flex: 1; /* пропорциональное распределение */
}

/* CSS Grid */
.grid-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: 100px auto;
    gap: 15px;
}

.grid-item {
    grid-column: span 2;
    grid-row: 1;
}</code></pre>
            
            <h3>4. Анимации и переходы</h3>
            <pre><code>/* Transition */
.button {
    background: blue;
    transition: background 0.3s ease, transform 0.2s;
}

.button:hover {
    background: darkblue;
    transform: scale(1.05);
}

/* Animation */
@keyframes slide-in {
    from { transform: translateX(-100%); }
    to { transform: translateX(0); }
}

.slide {
    animation: slide-in 0.5s forwards;
}</code></pre>
            """,
            """
            <h3>5. Адаптивный дизайн и переменные</h3>
            <pre><code>/* Медиазапросы */
@media (max-width: 768px) {
    .menu { display: none; }
    .mobile-menu { display: block; }
}

/* CSS переменные */
:root {
    --primary-color: #4285f4;
    --secondary-color: #34a853;
}

.element {
    color: var(--primary-color);
    background: var(--secondary-color);
}

/* Современные единицы измерения */
.container {
    width: min(100%, 1200px);
    height: clamp(300px, 50vh, 500px);
    margin-inline: auto; /* логические свойства */
}</code></pre>
            """
        ]
        self.css_tab.findChild(QTextEdit).setHtml(self.css_materials[0])
    
    def navigate_material(self, language, direction):
        """Перемещается между материалами по языку"""
        if language == "JavaScript":
            materials = self.javascript_materials
            text_area = self.javascript_tab.findChild(QTextEdit)
        else:  # CSS
            materials = self.css_materials
            text_area = self.css_tab.findChild(QTextEdit)
        
        current_index = materials.index(text_area.toHtml())
        new_index = (current_index + direction) % len(materials)
        text_area.setHtml(materials[new_index])
    
    def load_quiz_questions(self):
        """Загружает вопросы для викторины"""
        self.quiz_questions = [
            {
                "question": "Какой оператор используется для присваивания значения переменной в Python?",
                "options": ["=", "==", ":=", "->"],
                "answer": 0,
                "points": 200
            },
            {
                "question": "Как объявить функцию в JavaScript?",
                "options": ["function myFunc() {}", "def myFunc() {}", "func myFunc() {}", "myFunc() => {}"],
                "answer": 0,
                "points": 300
            },
            {
                "question": "Какое свойство CSS изменяет цвет текста?",
                "options": ["color", "text-color", "font-color", "text-style"],
                "answer": 0,
                "points": 250
            },
            {
                "question": "Какой цикл в Python выполняется, пока условие истинно?",
                "options": ["while", "for", "loop", "do-while"],
                "answer": 0,
                "points": 200
            },
            {
                "question": "Как добавить комментарий в CSS?",
                "options": ["/* комментарий */", "// комментарий", "<!-- комментарий -->", "# комментарий"],
                "answer": 0,
                "points": 150
            },
            {
                "question": "Что делает метод querySelector() в JavaScript?",
                "options": ["Возвращает первый элемент, соответствующий селектору", 
                          "Возвращает все элементы с указанным классом",
                          "Выполняет AJAX-запрос",
                          "Создает новый DOM-элемент"],
                "answer": 0,
                "points": 400
            },
            {
                "question": "Какое свойство CSS отвечает за внешние отступы?",
                "options": ["margin", "padding", "border", "spacing"],
                "answer": 0,
                "points": 300
            },
            {
                "question": "Какой метод преобразует JSON-строку в JavaScript-объект?",
                "options": ["JSON.parse()", "JSON.stringify()", "JSON.decode()", "JSON.toObject()"],
                "answer": 0,
                "points": 350
            },
            {
                "question": "Какое правило CSS позволяет создавать адаптивный дизайн?",
                "options": ["@media", "@responsive", "@viewport", "@adaptive"],
                "answer": 0,
                "points": 400
            },
            {
                "question": "Что такое замыкание (closure) в JavaScript?",
                "options": ["Функция, которая запоминает свое лексическое окружение",
                          "Способ скрытия элементов на странице",
                          "Метод закрытия модального окна",
                          "Тип данных для хранения закрытой информации"],
                "answer": 0,
                "points": 500
            }
        ]
    
    
    def show_question(self):
        """Показывает текущий вопрос"""
        if self.current_question < len(self.quiz_questions):
            question_data = self.quiz_questions[self.current_question]
            self.current_correct_index = question_data['answer']

            options = question_data['options']
            indices = list(range(len(options)))
            random.shuffle(indices)
            self.option_map = {i: indices[i] for i in range(4)}  # отображение кнопки -> индекс в оригинале
            inverse_map = {v: k for k, v in self.option_map.items()}  # индекс правильного ответа

            # Запоминаем где оказался правильный ответ
            self.shuffled_correct_index = inverse_map[self.current_correct_index]

            self.question_label.setText(
                f"Вопрос {self.current_question + 1}/{len(self.quiz_questions)}: {question_data['question']}"
            )
            self.option1.setText(f"A. {options[self.option_map[0]]}")
            self.option2.setText(f"B. {options[self.option_map[1]]}")
            self.option3.setText(f"C. {options[self.option_map[2]]}")
            self.option4.setText(f"D. {options[self.option_map[3]]}")

            self.button_group.setExclusive(False)
            self.option1.setChecked(False)
            self.option2.setChecked(False)
            self.option3.setChecked(False)
            self.option4.setChecked(False)
            self.button_group.setExclusive(True)

            self.prev_btn.setEnabled(self.current_question > 0)
            self.next_btn.setEnabled(self.current_question < len(self.quiz_questions) - 1)
            self.points_label.setText(f"Баллы: {self.score}")

            self.time_left = 60
            self.progress_bar.setValue(self.time_left)
            self.time_label.setText(f"Время: {self.time_left} сек")
            self.timer.start(1000)

    def update_timer(self):
        """Обновляет таймер"""
        self.time_left -= 1
        self.progress_bar.setValue(self.time_left)
        self.time_label.setText(f"Время: {self.time_left} сек")
        
        if self.time_left <= 10:
            self.time_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.time_label.setStyleSheet("color: #FF6347; font-weight: bold;")
        
        if self.time_left <= 0:
            self.timer.stop()
            QMessageBox.warning(self, "Время вышло!", "Время на ответ истекло!")
            self.next_question()
    
    def next_question(self):
        """Переходит к следующему вопросу"""
        self.timer.stop()
        if self.current_question < len(self.quiz_questions) - 1:
            self.current_question += 1
            self.show_question()
        else:
            self.show_results()
    
    def prev_question(self):
        """Возвращается к предыдущему вопросу"""
        self.timer.stop()
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question()
    
    def check_answer(self):
        """Проверяет выбранный ответ"""
        self.timer.stop()
        if not any([self.option1.isChecked(), self.option2.isChecked(), 
                   self.option3.isChecked(), self.option4.isChecked()]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите ответ!")
            return
        
        selected_option = -1
        if self.option1.isChecked(): selected_option = 0
        elif self.option2.isChecked(): selected_option = 1
        elif self.option3.isChecked(): selected_option = 2
        elif self.option4.isChecked(): selected_option = 3
        
        correct_answer = self.shuffled_correct_index
        points = self.quiz_questions[self.current_question]['points']
        
        if selected_option == correct_answer:
            self.score += points
            QMessageBox.information(self, "Правильно!", 
                                  f"Ваш ответ верный! +{points} баллов\n\n"
                                  f"Общий счет: {self.score}")
        else:
            correct = ['A', 'B', 'C', 'D'][correct_answer]
            QMessageBox.warning(self, "Неправильно", 
                              f"Правильный ответ: {correct}\n\n"
                              f"Общий счет: {self.score}")
        
        self.points_label.setText(f"Баллы: {self.score}")
        
        if self.current_question < len(self.quiz_questions) - 1:
            self.current_question += 1
            self.show_question()
        else:
            self.show_results()
    
    def show_results(self):
        """Показывает итоговые результаты"""
        total_points = sum(q['points'] for q in self.quiz_questions)
        percentage = (self.score / total_points) * 100
        
        if percentage >= 80:
            message = "Отличный результат! 🎉"
            color = "green"
        elif percentage >= 50:
            message = "Хороший результат! 👍"
            color = "blue"
        else:
            message = "Попробуйте еще раз! 💪"
            color = "orange"
        
        self.result_label.setText(
            f"<div style='font-size: 16px; color: {color};'>"
            f"<b>Тест завершен!</b><br>"
            f"Ваш результат: {self.score} из {total_points} баллов<br>"
            f"({percentage:.1f}%)<br>"
            f"{message}"
            f"</div>"
        )
        
        # Сброс для повторного прохождения
        self.current_question = 0
        self.score = 0
        self.submit_btn.setText("Начать заново")
        self.submit_btn.clicked.disconnect()
        self.submit_btn.clicked.connect(self.reset_quiz)
    
    def reset_quiz(self):
        """Сбрасывает викторину для повторного прохождения"""
        self.submit_btn.setText("✅ Проверить")
        self.submit_btn.clicked.disconnect()
        self.submit_btn.clicked.connect(self.check_answer)
        self.result_label.clear()
        self.show_question()


    def create_profile_tab(self):
        """Создает вкладку личного кабинета"""
        tab = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Личный кабинет")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        avatar = QLabel()
        avatar.setPixmap(QPixmap(":/icons/avatar.png").scaled(80, 80))
        avatar.setAlignment(Qt.AlignCenter)
        layout.addWidget(avatar)


        self.profile_info = QLabel("Информация о пользователе появится после входа")
        self.profile_info.setFont(QFont("Arial", 12))
        self.profile_info.setAlignment(Qt.AlignTop)
        self.profile_info.setStyleSheet("padding: 20px;")
        layout.addWidget(self.profile_info)

        tab.setLayout(layout)
        return tab


    def show_login_dialog(self):
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.user_data = dialog.user_data
            self.update_profile_tab()

    def update_profile_tab(self):
        if hasattr(self, 'profile_info') and self.user_data:
            self.profile_info.setText(
                f"<b>ФИО:</b> {self.user_data['fio']}<br>"
                f"<b>Логин:</b> {self.user_data['username']}<br>"
                f"<b>Лучший результат:</b> {self.user_data['score']} баллов"
            )


    def logout_user(self):
        """Выход из аккаунта"""
        self.user_data = None
        self.profile_info.setText("Информация о пользователе появится после входа")
        QMessageBox.information(self, "Выход", "Вы вышли из аккаунта.")
        self.show_login_dialog()


    def load_user_rating(self):
        try:
            conn = sqlite3.connect("study_app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT fio, score FROM users ORDER BY score DESC LIMIT 10")
            users = cursor.fetchall()
            conn.close()

            self.rating_table.setRowCount(len(users))
            for i, (fio, score) in enumerate(users):
                self.rating_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.rating_table.setItem(i, 1, QTableWidgetItem(fio))
                self.rating_table.setItem(i, 2, QTableWidgetItem(str(score)))
        except Exception as e:
            print("Ошибка при загрузке рейтинга:", e)


    def toggle_theme(self):
        """Переключает тему интерфейса"""
        if self.dark_mode:
            self.setStyleSheet("")  # светлая тема
            self.dark_mode = False
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2E2E2E;
                    color: white;
                }
                QLineEdit, QTextEdit, QTableWidget, QLabel {
                    background-color: #3C3C3C;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 5px;
                }
                QPushButton {
                    background-color: #5A5A5A;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #777;
                }
                QHeaderView::section {
                    background-color: #444;
                    color: white;
                }
            """)
            self.dark_mode = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudyApp()
    window.show()
    sys.exit(app.exec_())
