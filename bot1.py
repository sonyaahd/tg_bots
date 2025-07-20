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

ALLOWED_USERS = {12345678}  # список разрешенных пользователей их user id

def is_allowed(user_id):
    return user_id in ALLOWED_USERS

def restricted(func):
    def wrapper(message, *args, **kwargs):
        if not is_allowed(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "🚫 У вас нет доступа к этому боту."
            )
            return
        return func(message, *args, **kwargs)
    return wrapper

def get_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📦 Показать склад", "➕ Добавить материал")
    markup.add("🗑 Удалить материал", "✏️ Изменить количество")
    markup.add("📈 Аналитика")
    return markup

def get_back_to_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("⬅️ Главное меню")
    return markup

user_states = {}

@bot.message_handler(commands=['start'])
@restricted
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Это бот-склад.\nВыберите действие из меню ниже:",
        reply_markup=get_main_markup()
    )

@bot.message_handler(func=lambda m: m.text == "⬅️ Главное меню")
@restricted
def back_to_main(message):
    bot.send_message(
        message.chat.id,
        "⬅️ Вернулись в главное меню.",
        reply_markup=get_main_markup()
    )

@bot.message_handler(func=lambda m: m.text == "📦 Показать склад")
@restricted
def show_sklad(message):
    try:
        cur = conn.cursor()
        cur.execute("SELECT material_id, name, quantity FROM sklad ORDER BY material_id;")
        rows = cur.fetchall()
        cur.close()

        if not rows:
            response = "📦 Склад пуст."
        else:
            response = "📋 Материалы на складе:\n\n"
            for mid, name, qty in rows:
                qty_text = qty if qty is not None else "не указано"
                response += f"• {mid}. {name}: {qty_text} шт.\n"
    except Exception as e:
        response = f"⚠️ Ошибка при запросе к базе: {e}"
    bot.send_message(message.chat.id, response, reply_markup=get_main_markup())

@bot.message_handler(func=lambda m: m.text == "➕ Добавить материал")
@restricted
def add_material_start(message):
    try:
        cur = conn.cursor()
        cur.execute("SELECT material_id, name FROM sklad ORDER BY material_id;")
        rows = cur.fetchall()
        cur.close()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
        for mid, name in rows:
            markup.add(f"{mid} - {name}")
        markup.add("➕ Новый материал", "⬅️ Главное меню")

        bot.send_message(
            message.chat.id,
            "Выберите материал из списка или добавьте новый:",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, process_material_selection)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при запросе к базе: {e}", reply_markup=get_main_markup())

def process_material_selection(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text == "⬅️ Главное меню":
        back_to_main(message)
        return

    if text == "➕ Новый материал":
        bot.send_message(
            message.chat.id,
            "Введите название нового материала:",
            reply_markup=get_back_to_main_markup()
        )
        user_states[user_id] = {}
        bot.register_next_step_handler(message, process_new_material_name)
        return

    try:
        material_id = int(text.split(" - ")[0])
        user_states[user_id] = {'material_id': material_id}
        bot.send_message(
            message.chat.id,
            "Введите количество поступившего материала:",
            reply_markup=get_back_to_main_markup()
        )
        bot.register_next_step_handler(message, process_existing_material_quantity)
    except Exception:
        bot.send_message(
            message.chat.id,
            "❗ Неверный формат выбора. Попробуйте снова.",
            reply_markup=get_main_markup()
        )
        add_material_start(message)

def process_new_material_name(message):
    user_id = message.from_user.id
    if message.text.strip() == "⬅️ Главное меню":
        back_to_main(message)
        return

    material_name = message.text.strip()
    if not material_name:
        bot.send_message(
            message.chat.id,
            "❗ Название не может быть пустым. Введите название материала:",
            reply_markup=get_back_to_main_markup()
        )
        bot.register_next_step_handler(message, process_new_material_name)
        return

    user_states[user_id] = {'material_name': material_name}
    bot.send_message(
        message.chat.id,
        "Введите количество поступившего материала:",
        reply_markup=get_back_to_main_markup()
    )
    bot.register_next_step_handler(message, process_new_material_quantity)

def process_existing_material_quantity(message):
    user_id = message.from_user.id
    if message.text.strip() == "⬅️ Главное меню":
        back_to_main(message)
        return

    try:
        quantity = int(message.text.strip())
        material_id = user_states[user_id]['material_id']

        cur = conn.cursor()
        cur.execute("UPDATE sklad SET quantity = quantity + %s WHERE material_id = %s;", (quantity, material_id))
        cur.execute("INSERT INTO priemka (date_received, material_id, quantity) VALUES (CURRENT_DATE, %s, %s);", (material_id, quantity))
        conn.commit()
        cur.close()

        bot.send_message(
            message.chat.id,
            f"✅ Количество материала с ID {material_id} успешно обновлено (+{quantity}).",
            reply_markup=get_main_markup()
        )
        user_states.pop(user_id, None)
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"⚠️ Ошибка при обновлении: {e}",
            reply_markup=get_main_markup()
        )
        user_states.pop(user_id, None)

def process_new_material_quantity(message):
    user_id = message.from_user.id
    if message.text.strip() == "⬅️ Главное меню":
        back_to_main(message)
        return

    try:
        quantity = int(message.text.strip())
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        material_name = user_states[user_id]['material_name']

        cur = conn.cursor()

        cur.execute("SELECT material_id FROM sklad WHERE LOWER(name) = LOWER(%s);", (material_name,))
        existing = cur.fetchone()

        if existing:
            cur.close()
            bot.send_message(
                message.chat.id,
                f"❗ Материал с названием '{material_name}' уже существует на складе.\n"
                f"Выберите другой или используйте пункт 'Добавить материал' для пополнения существующего.",
                reply_markup=get_main_markup()
            )
            user_states.pop(user_id, None)
            return

        cur.execute(
            "INSERT INTO sklad (name, quantity) VALUES (%s, %s) RETURNING material_id;",
            (material_name, quantity)
        )
        material_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO priemka (date_received, material_id, quantity) VALUES (CURRENT_DATE, %s, %s);",
            (material_id, quantity)
        )
        conn.commit()
        cur.close()

        bot.send_message(
            message.chat.id,
            f"✅ Новый материал '{material_name}' добавлен с ID {material_id}.",
            reply_markup=get_main_markup()
        )
        user_states.pop(user_id, None)

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"⚠️ Ошибка при добавлении материала: {e}",
            reply_markup=get_main_markup()
        )
        user_states.pop(user_id, None)

@bot.message_handler(func=lambda m: m.text == "🗑 Удалить материал")
@restricted
def delete_material_start(message):
    try:
        cur = conn.cursor()
        cur.execute("SELECT material_id, name FROM sklad ORDER BY material_id;")
        rows = cur.fetchall()
        cur.close()

        if not rows:
            bot.send_message(message.chat.id, "📦 Склад пуст, нечего удалять.", reply_markup=get_main_markup())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
        for mid, name in rows:
            markup.add(f"{mid} - {name}")
        markup.add("⬅️ Главное меню")

        bot.send_message(
            message.chat.id,
            "Выберите материал для удаления:",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, process_delete_material)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при запросе к базе: {e}", reply_markup=get_main_markup())

def process_delete_material(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text == "⬅️ Главное меню":
        back_to_main(message)
        return

    try:
        material_id = int(text.split(" - ")[0])
        cur = conn.cursor()
        cur.execute("DELETE FROM priemka WHERE material_id = %s;", (material_id,))
        cur.execute("DELETE FROM vidacha WHERE material_id = %s;", (material_id,))
        cur.execute("DELETE FROM sklad WHERE material_id = %s;", (material_id,))
        conn.commit()
        cur.close()

        bot.send_message(
            message.chat.id,
            f"🗑 Материал с ID {material_id} успешно удалён со склада.",
            reply_markup=get_main_markup()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"⚠️ Ошибка при удалении: {e}",
            reply_markup=get_main_markup()
        )

@bot.message_handler(func=lambda m: m.text == "✏️ Изменить количество")
@restricted
def change_quantity_start(message):
    try:
        cur = conn.cursor()
        cur.execute("SELECT material_id, name, quantity FROM sklad ORDER BY material_id;")
        rows = cur.fetchall()
        cur.close()

        if not rows:
            bot.send_message(message.chat.id, "📦 Склад пуст, нечего изменять.", reply_markup=get_main_markup())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
        for mid, name, qty in rows:
            markup.add(f"{mid} - {name} (текущ. {qty})")
        markup.add("⬅️ Главное меню")

        bot.send_message(
            message.chat.id,
            "Выберите материал для изменения количества:",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, process_change_quantity_select)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при запросе к базе: {e}", reply_markup=get_main_markup())

def process_change_quantity_select(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text == "⬅️ Главное меню":
        back_to_main(message)
        return

    try:
        material_id = int(text.split(" - ")[0])
        user_states[user_id] = {'material_id': material_id}

        bot.send_message(
            message.chat.id,
            "Введите новое количество материала:",
            reply_markup=get_back_to_main_markup()
        )
        bot.register_next_step_handler(message, process_change_quantity_input)
    except Exception:
        bot.send_message(
            message.chat.id,
            "❗ Неверный формат выбора. Попробуйте снова.",
            reply_markup=get_main_markup()
        )

def process_change_quantity_input(message):
    user_id = message.from_user.id
    if message.text.strip() == "⬅️ Главное меню":
        back_to_main(message)
        return

    try:
        new_qty = int(message.text.strip())
        if new_qty < 0:
            raise ValueError("Количество не может быть отрицательным")
        material_id = user_states[user_id]['material_id']

        cur = conn.cursor()
        cur.execute("UPDATE sklad SET quantity = %s WHERE material_id = %s;", (new_qty, material_id))
        conn.commit()
        cur.close()

        bot.send_message(
            message.chat.id,
            f"✏️ Количество материала с ID {material_id} изменено на {new_qty}.",
            reply_markup=get_main_markup()
        )
        user_states.pop(user_id, None)
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"⚠️ Ошибка при изменении количества: {e}",
            reply_markup=get_main_markup()
        )
        user_states.pop(user_id, None)



@bot.message_handler(func=lambda m: m.text == "📈 Аналитика")
@restricted
def analytics_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    markup.add("📋 Статистика по кабинетам", "🔥 Самые ходовые/редкие материалы", "⬅️ Главное меню")
    bot.send_message(message.chat.id, "Выберите тип аналитики:", reply_markup=markup)
    bot.register_next_step_handler(message, process_analytics_choice)

def process_analytics_choice(message):
    text = message.text.strip()
    if text == "⬅️ Главное меню":
        back_to_main(message)
        return
    elif text == "📋 Статистика по кабинетам":
        show_cabinets_list(message)
    elif text == "🔥 Самые ходовые/редкие материалы":
        show_popular_rare_materials(message)
    else:
        bot.send_message(message.chat.id, "❗ Неверный выбор. Попробуйте снова.", reply_markup=get_main_markup())

def show_cabinets_list(message):
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT room FROM vidacha ORDER BY room;")
        rows = cur.fetchall()
        cur.close()

        if not rows:
            bot.send_message(message.chat.id, "ℹ️ Нет данных по кабинетам.", reply_markup=get_main_markup())
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
        for (cabinet,) in rows:
            markup.add(str(cabinet))
        markup.add("⬅️ Главное меню")

        bot.send_message(message.chat.id, "Выберите номер кабинета для статистики:", reply_markup=markup)
        bot.register_next_step_handler(message, process_cabinet_choice)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при получении кабинетов: {e}", reply_markup=get_main_markup())
def process_cabinet_choice(message):
    text = message.text.strip()
    if text == "⬅️ Главное меню":
        back_to_main(message)
        return

    try:
        room = text
        current_year = datetime.now().year
        cur = conn.cursor()

        cur.execute("""
            SELECT SUM(quantity) FROM vidacha
            WHERE room = %s AND EXTRACT(YEAR FROM date_issued) = %s;
        """, (room, current_year))
        total_qty_row = cur.fetchone()
        total_qty = total_qty_row[0] or 0

        cur.execute("""
            SELECT
                EXTRACT(MONTH FROM date_issued) AS month,
                material_id,
                SUM(quantity) AS sum_qty
            FROM vidacha
            WHERE room = %s AND EXTRACT(YEAR FROM date_issued) = %s
            GROUP BY month, material_id
            ORDER BY month, material_id;
        """, (room, current_year))
        rows = cur.fetchall()

        cur.execute("SELECT material_id, name FROM sklad;")
        materials = {row[0]: row[1] for row in cur.fetchall()}
        cur.close()

        if total_qty == 0 or not rows:
            bot.send_message(message.chat.id, f"ℹ️ За {current_year} год в кабинете {room} выдач не зафиксировано.", reply_markup=get_main_markup())
            return

        months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

        data = {}
        for month, mid, qty in rows:
            m = int(month)
            data.setdefault(m, {})
            data[m][mid] = data[m].get(mid, 0) + qty

        response = f"📋 Статистика по кабинету {room} за {current_year} год:\n\n"
        for m in range(1, 13):
            month_data = data.get(m, {})
            if not month_data:
                response += f"• {months[m-1]}: Нет выдач\n"
                continue
            response += f"• {months[m-1]}:\n"
            for mid, qty in month_data.items():
                percent = (qty / total_qty) * 100 if total_qty > 0 else 0
                name = materials.get(mid, f"ID {mid}")
                response += f"    - {name}: {qty} шт. ({percent:.1f}%)\n"

        bot.send_message(message.chat.id, response, reply_markup=get_main_markup())

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при получении статистики: {e}", reply_markup=get_main_markup())
def show_popular_rare_materials(message):
    try:
        current_year = datetime.now().year
        cur = conn.cursor()

        cur.execute("""
            SELECT
                material_id,
                SUM(quantity) AS total_qty
            FROM vidacha
            WHERE EXTRACT(YEAR FROM date_issued) = %s
            GROUP BY material_id
            ORDER BY total_qty DESC;
        """, (current_year,))
        rows = cur.fetchall()

        cur.execute("SELECT material_id, name FROM sklad;")
        materials = {row[0]: row[1] for row in cur.fetchall()}
        cur.close()

        if not rows:
            bot.send_message(message.chat.id, f"ℹ️ За {current_year} год выданных материалов не зафиксировано.", reply_markup=get_main_markup())
            return

        top_n = 5 
        
        top_materials = rows[:top_n]
        rare_materials = rows[-top_n:] if len(rows) >= top_n else rows[-len(rows):]

        response = f"🔥 Самые ходовые материалы за {current_year} год:\n"
        for mid, qty in top_materials:
            name = materials.get(mid, f"ID {mid}")
            response += f"• {name}: {qty} шт.\n"

        response += f"\n❄️ Самые редкие материалы за {current_year} год:\n"
        for mid, qty in rare_materials:
            name = materials.get(mid, f"ID {mid}")
            response += f"• {name}: {qty} шт.\n"

        bot.send_message(message.chat.id, response, reply_markup=get_main_markup())

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при получении аналитики: {e}", reply_markup=get_main_markup())

bot.polling(none_stop=True)
