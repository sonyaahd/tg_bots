import telebot
from telebot import types
import psycopg2
from datetime import datetime

API_TOKEN = 'тут API бота'

conn = psycopg2.connect(
    dbname='materialsib',
    user='user', #имя пользователя SQL
    password='111', #пароль
    host='localhost', #хост
    port='5432'
)

bot = telebot.TeleBot(API_TOKEN)

ADMIN_IDS = {12345678} #админ имеет доступ к просмотру выдач user id
AUTHORIZED_USERS = set()
PASSWORD = "1234"


user_states = {}

def get_main_markup(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Получить материал")
    if message.from_user.id in ADMIN_IDS:
        markup.add("📋 Просмотр выдач")
    return markup

def get_back_to_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("⬅️ Главное меню")
    return markup

def get_material_names():
    cur = conn.cursor()
    cur.execute("SELECT name FROM sklad ORDER BY name;")
    rows = cur.fetchall()
    cur.close()
    return [row[0] for row in rows]

def authorized_only(handler):
    def wrapper(message):
        if message.from_user.id not in AUTHORIZED_USERS:
            bot.send_message(message.chat.id, "🚫 Доступ запрещён. Введите пароль с помощью команды /start.")
            return
        return handler(message)
    return wrapper

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "Вы уже авторизованы.", reply_markup=get_main_markup(message))
    else:
        bot.send_message(message.chat.id, "Введите пароль для доступа:")
        bot.register_next_step_handler(message, check_password)

def check_password(message):
    if message.text.strip() == PASSWORD:
        AUTHORIZED_USERS.add(message.from_user.id)
        bot.send_message(message.chat.id, "✅ Доступ разрешён!", reply_markup=get_main_markup(message))
    else:
        bot.send_message(message.chat.id, "❌ Неверный пароль. Попробуйте ещё раз через /start.")

@bot.message_handler(commands=['logout'])
def logout(message):
    user_id = message.from_user.id
    if user_id in AUTHORIZED_USERS:
        AUTHORIZED_USERS.remove(user_id)
        bot.send_message(message.chat.id, "🚪 Вы вышли из системы. Для входа используйте /start.")
    else:
        bot.send_message(message.chat.id, "Вы не авторизованы.")

@bot.message_handler(func=lambda m: m.text == "Получить материал")
@authorized_only
def issue_material_start(message):
    try:
        materials = get_material_names()
        if not materials:
            bot.send_message(message.chat.id, "Склад пуст, выдача невозможна.", reply_markup=get_main_markup(message))
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for name in materials:
            markup.add(name)
        markup.add("Отмена")

        bot.send_message(message.chat.id, "Выберите материал для выдачи:", reply_markup=markup)
        bot.register_next_step_handler(message, process_issue_material_select)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}", reply_markup=get_main_markup(message))

def process_issue_material_select(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text == "Отмена":
        bot.send_message(message.chat.id, "Выдача отменена.", reply_markup=get_main_markup(message))
        return

    cur = conn.cursor()
    cur.execute("SELECT material_id, quantity FROM sklad WHERE name = %s;", (text,))
    row = cur.fetchone()
    cur.close()

    if not row:
        bot.send_message(message.chat.id, "Материал не найден, попробуйте снова.", reply_markup=get_main_markup(message))
        return

    material_id, stock_qty = row

    user_states[user_id] = {
        'material_id': material_id,
        'material_name': text,
        'stock_qty': stock_qty
    }

    bot.send_message(message.chat.id, "Введите номер кабинета (число):", reply_markup=get_back_to_main_markup())
    bot.register_next_step_handler(message, process_issue_room)

def process_issue_room(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text == "⬅️ Главное меню":
        bot.send_message(message.chat.id, "Отменено. Возврат в меню.", reply_markup=get_main_markup(message))
        user_states.pop(user_id, None)
        return

    if not text.isdigit():
        bot.send_message(message.chat.id, "Номер кабинета должен быть числом. Попробуйте снова.", reply_markup=get_back_to_main_markup())
        bot.register_next_step_handler(message, process_issue_room)
        return

    user_states[user_id]['room'] = int(text)
    bot.send_message(message.chat.id, "Введите ФИО сотрудника:", reply_markup=get_back_to_main_markup())
    bot.register_next_step_handler(message, process_issue_employee)

def process_issue_employee(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text == "⬅️ Главное меню":
        bot.send_message(message.chat.id, "Отменено. Возврат в меню.", reply_markup=get_main_markup(message))
        user_states.pop(user_id, None)
        return

    if not text:
        bot.send_message(message.chat.id, "ФИО не может быть пустым. Попробуйте снова.", reply_markup=get_back_to_main_markup())
        bot.register_next_step_handler(message, process_issue_employee)
        return

    user_states[user_id]['employee_name'] = text
    bot.send_message(message.chat.id, "Введите количество для выдачи:", reply_markup=get_back_to_main_markup())
    bot.register_next_step_handler(message, process_issue_quantity)

def process_issue_quantity(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text == "⬅️ Главное меню":
        bot.send_message(message.chat.id, "Отменено. Возврат в меню.", reply_markup=get_main_markup(message))
        user_states.pop(user_id, None)
        return

    if not text.isdigit():
        bot.send_message(message.chat.id, "Количество должно быть числом. Попробуйте снова.", reply_markup=get_back_to_main_markup())
        bot.register_next_step_handler(message, process_issue_quantity)
        return

    qty = int(text)
    stock_qty = user_states[user_id]['stock_qty']

    if qty <= 0:
        bot.send_message(message.chat.id, "Количество должно быть больше 0. Попробуйте снова.", reply_markup=get_back_to_main_markup())
        bot.register_next_step_handler(message, process_issue_quantity)
        return

    if qty > stock_qty:
        bot.send_message(message.chat.id, f"На складе недостаточно материала. Попробуйте снова.", reply_markup=get_back_to_main_markup())
        bot.register_next_step_handler(message, process_issue_quantity)
        return

    material_name = user_states[user_id]['material_name']
    room = user_states[user_id]['room']
    employee = user_states[user_id]['employee_name']

    confirm_text = (f"Вы собираетесь получить:\n"
                    f"Материал: {material_name}\n"
                    f"Количество: {qty}\n"
                    f"Кабинет: {room}\n"
                    f"Сотрудник: {employee}\n\n"
                    "Подтвердите действие (Да/Отмена):")

    user_states[user_id]['issue_qty'] = qty

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Да", "Отмена")

    bot.send_message(message.chat.id, confirm_text, reply_markup=markup)
    bot.register_next_step_handler(message, process_issue_confirm)

def process_issue_confirm(message):
    user_id = message.from_user.id
    text = message.text.strip().lower()

    if text == "да":
        data = user_states.get(user_id)
        if not data:
            bot.send_message(message.chat.id, "Ошибка: состояние не найдено. Начните заново.", reply_markup=get_main_markup(message))
            return

        try:
            cur = conn.cursor()
            cur.execute("UPDATE sklad SET quantity = quantity - %s WHERE material_id = %s;", (data['issue_qty'], data['material_id']))
            cur.execute(
                "INSERT INTO vidacha (material_id, room, employee_name, quantity) VALUES (%s, %s, %s, %s);",
                (data['material_id'], data['room'], data['employee_name'], data['issue_qty'])
            )
            conn.commit()
            cur.close()

            bot.send_message(message.chat.id,
                             f"Выдано: {data['material_name']} в количестве {data['issue_qty']} шт. сотруднику {data['employee_name']} в кабинет {data['room']}.",
                             reply_markup=get_main_markup(message))
            user_states.pop(user_id, None)
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при выдаче: {e}", reply_markup=get_main_markup(message))
    else:
        bot.send_message(message.chat.id, "Выдача отменена.", reply_markup=get_main_markup(message))
        user_states.pop(user_id, None)

@bot.message_handler(func=lambda m: m.text == "📋 Просмотр выдач" and m.from_user.id in ADMIN_IDS)
@authorized_only
def view_issues(message):
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT v.id, s.name, v.quantity, v.room, v.employee_name, v.date_issued
            FROM vidacha v
            JOIN sklad s ON v.material_id = s.material_id
            ORDER BY v.date_issued DESC;
        """)
        rows = cur.fetchall()
        cur.close()

        if not rows:
            bot.send_message(message.chat.id, "Выдачи не найдены.", reply_markup=get_main_markup(message))
            return

        chunk_size = 10
        chunks = [rows[i:i + chunk_size] for i in range(0, len(rows), chunk_size)]

        user_states[message.from_user.id] = {
            'issues_chunks': chunks,
            'current_page': 0
        }

        send_issues_page(message.chat.id, message.from_user.id)

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при получении выдач: {e}", reply_markup=get_main_markup(message))

def send_issues_page(chat_id, user_id):
    data = user_states.get(user_id)
    if not data:
        return

    chunks = data['issues_chunks']
    page = data['current_page']

    chunk = chunks[page]
    text = f"Выдачи (страница {page + 1} из {len(chunks)}):\n\n"
    for row in chunk:
        id, material_name, qty, room, employee_name, date_issued = row
        text += (f"ID: {id}\n"
                 f"Материал: {material_name}\n"
                 f"Количество: {qty}\n"
                 f"Кабинет: {room}\n"
                 f"Сотрудник: {employee_name}\n"
                 f"Дата: {date_issued.strftime('%Y-%m-%d %H:%M')}\n\n")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = []
    if page > 0:
        buttons.append("⬅️ Назад")
    if page < len(chunks) - 1:
        buttons.append("➡️ Далее")
    buttons.append("⬅️ Главное меню")
    markup.add(*buttons)

    bot.send_message(chat_id, text, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["⬅️ Назад", "➡️ Далее", "⬅️ Главное меню"])
def pagination_handler(message):
    user_id = message.from_user.id
    if user_id not in user_states or 'issues_chunks' not in user_states[user_id]:
        bot.send_message(message.chat.id, "Нет данных для навигации.", reply_markup=get_main_markup(message))
        return

    if message.text == "⬅️ Главное меню":
        user_states.pop(user_id, None)
        bot.send_message(message.chat.id, "Возврат в главное меню.", reply_markup=get_main_markup(message))
        return

    if message.text == "➡️ Далее":
        if user_states[user_id]['current_page'] < len(user_states[user_id]['issues_chunks']) - 1:
            user_states[user_id]['current_page'] += 1
        send_issues_page(message.chat.id, user_id)

    if message.text == "⬅️ Назад":
        if user_states[user_id]['current_page'] > 0:
            user_states[user_id]['current_page'] -= 1
        send_issues_page(message.chat.id, user_id)

@bot.message_handler(func=lambda m: True)
def default_handler(message):
    bot.send_message(message.chat.id, "Команда не распознана. Используйте главное меню.", reply_markup=get_main_markup(message))

bot.polling(none_stop=True)
