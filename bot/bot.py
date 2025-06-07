
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

BOT_TOKEN = '7578190238:AAGDDU88ngPbMMRcPcXyqKCTyTeeGiNN08k'
bot = telebot.TeleBot(BOT_TOKEN)

team = {}

# === Главное меню ===
def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Добавить участника", callback_data="action_add_member"),
        InlineKeyboardButton("🧑‍💼 Назначить роль", callback_data="action_assign_role"),
        InlineKeyboardButton("📝 Назначить задачу", callback_data="action_assign_task"),
        InlineKeyboardButton("❌ Удалить роль", callback_data="action_remove_role"),
        InlineKeyboardButton("❌ Удалить задачу", callback_data="action_remove_task"),
        InlineKeyboardButton("🗑 Удалить участника", callback_data="action_remove_member"),
        InlineKeyboardButton("📋 Показать команду", callback_data="action_show_team")
    )
    return markup

# === Обработчик старта ===
@bot.message_handler(commands=['start'])
def start_handler(message: Message):
    bot.send_message(message.chat.id, "👋 Привет! Выберите действие:", reply_markup=get_main_menu())

# === Обработка возврата в меню ===
@bot.callback_query_handler(func=lambda call: call.data == "go_back")
def go_back_handler(call: CallbackQuery):
    bot.edit_message_text("🔙 Главное меню:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_main_menu())

# === Обработка выбора действия ===
@bot.callback_query_handler(func=lambda call: call.data.startswith("action_"))
def action_handler(call: CallbackQuery):
    action = call.data.replace("action_", "")
    msg = {
        "add_member": "Введите имя нового участника:",
        "assign_role": "Введите имя участника, которому вы хотите назначить роль:",
        "assign_task": "Введите имя участника, которому вы хотите назначить задачу:",
        "remove_role": "Введите имя участника, у которого нужно удалить роль:",
        "remove_task": "Введите имя участника, у которого нужно удалить задачу:",
        "remove_member": "Введите имя участника, которого хотите удалить:",
        "show_team": None
    }

    if action == "show_team":
        show_team(call.message)
        return

    bot.send_message(call.message.chat.id, msg[action])
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_name_step, action)

# === Обработка ввода имени ===
def process_name_step(message: Message, action: str):
    name = message.text.strip()

    if action == "add_member":
        if name in team:
            bot.send_message(message.chat.id, f"{name} уже в команде.", reply_markup=get_back_button())
        else:
            team[name] = {"role": None, "task": None}
            bot.send_message(message.chat.id, f"✅ Участник {name} добавлен.", reply_markup=get_back_button())

    elif name not in team and action != "remove_member":
        bot.send_message(message.chat.id, f"❌ Участник {name} не найден.", reply_markup=get_back_button())

    elif action == "assign_role":
        bot.send_message(message.chat.id, f"Введите роль для {name}:")
        bot.register_next_step_handler_by_chat_id(message.chat.id, assign_custom_role, name)

    elif action == "assign_task":
        bot.send_message(message.chat.id, f"Введите задачу для {name}:")
        bot.register_next_step_handler_by_chat_id(message.chat.id, assign_custom_task, name)

    elif action == "remove_role":
        team[name]['role'] = None
        bot.send_message(message.chat.id, f"🧹 Роль у {name} удалена.", reply_markup=get_back_button())

    elif action == "remove_task":
        team[name]['task'] = None
        bot.send_message(message.chat.id, f"🧹 Задача у {name} удалена.", reply_markup=get_back_button())

    elif action == "remove_member":
        if name in team:
            del team[name]
            bot.send_message(message.chat.id, f"🗑 Участник {name} удалён.", reply_markup=get_back_button())
        else:
            bot.send_message(message.chat.id, f"❌ Участник {name} не найден.", reply_markup=get_back_button())

# === Ручной ввод роли ===
def assign_custom_role(message: Message, name: str):
    role = message.text.strip()
    team[name]['role'] = role
    bot.send_message(message.chat.id, f"✅ {name} назначен(а) на роль: {role}", reply_markup=get_back_button())

# === Ручной ввод задачи ===
def assign_custom_task(message: Message, name: str):
    task = message.text.strip()
    team[name]['task'] = task
    bot.send_message(message.chat.id, f"📝 {name} получил(а) задачу: {task}", reply_markup=get_back_button())

# === Показ команды ===
def show_team(message: Message):
    if not team:
        bot.send_message(message.chat.id, "👥 Команда пуста.", reply_markup=get_back_button())
        return
    msg = "👥 Состав команды:\n"
    for name, info in team.items():
        msg += f"🔸 {name} | 🧑‍💼 {info['role'] or '—'} | 📝 {info['task'] or '—'}\n"
    bot.send_message(message.chat.id, msg, reply_markup=get_back_button())

# === Кнопка возврата ===
def get_back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Назад в меню", callback_data="go_back"))
    return markup

# === Запуск ===
print("🚀 Бот запущен...")
bot.infinity_polling()
