from logic import DB_Manager
from config import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telebot import types

# Инициализируем менеджер базы данных (добавьте ваш файл бд, если требуется в конструкторе)
manager = DB_Manager(DATABASE) 

bot = TeleBot(TOKEN)
hideBoard = types.ReplyKeyboardRemove() 

# Красивая кнопка отмены
cancel_button = "Отмена 🚫"

def cansel(message):
    bot.send_message(
        message.chat.id, 
        "<b>Действие отменено!</b> 📋 Чтобы вспомнить, что я умею, введи команду /info", 
        reply_markup=hideBoard,
        parse_mode='HTML'
    )
  
def no_projects(message):
    bot.send_message(
        message.chat.id, 
        "📂 <b>У тебя пока нет созданных проектов!</b>\n\nСамое время зафиксировать гениальную идею. Используй команду /new_project, чтобы начать! ✨",
        parse_mode='HTML'
    )

def gen_inline_markup(rows):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for row in rows:
        # Добавляем иконку папки к инлайн-кнопкам для красоты
        markup.add(InlineKeyboardButton(f"📁 {row}", callback_data=row))
    return markup

def gen_markup(rows):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
    markup.add(KeyboardButton(cancel_button))
    return markup

# Словарь атрибутов теперь хранит кортеж: (Красивое имя, Текст подсказки, Имя поля в БД)
attributes_of_projects = {
    '🚀 Имя проекта': ["📝 <b>Введите новое имя проекта:</b>", "project_name"],
    "📖 Описание": ["✏️ <b>Введите новое описание проекта:</b>", "description"],
    "🔗 Ссылка": ["🌐 <b>Укажите новую ссылку на проект:</b>", "url"],
    "📊 Статус": ["⚡ <b>Выберите новый статус из списка ниже:</b>", "status_id"]
}

# Карта эмодзи для статусов (подстройте под названия статусов из вашей БД)
STATUS_EMOJIS = {
    "В разработке": "🟢 В разработке",
    "На паузе": "🟡 На паузе",
    "Завершен": "🔵 Завершен",
    "Идея": "💡 Идея"
}

def get_status_with_emoji(status_text):
    return STATUS_EMOJIS.get(status_text, f"🔸 {status_text}")

def info_project(message, user_id, project_name):
    info = manager.get_project_info(user_id, project_name)[0]
    skills = manager.get_project_skills(project_name)
    
    # Красивое форматирование навыков
    if not skills:
        skills_text = "<i>Навыки пока не добавлены 🛠️</i>"
    else:
        # Если навыки приходят списком/строкой, оформляем их в виде тегов
        skills_text = ", ".join([f"<code>{s}</code>" for s in skills]) if isinstance(skills, list) else f"<code>{skills}</code>"

    status_with_icon = get_status_with_emoji(info[3])

    # Оформляем карточку проекта в виде стильного блока
    card = f"""
╔════════════════════════════════🌟
║  <b>ПРОЕКТ:</b> {info[0]}
╠════════════════════════════════
║  📝 <b>Описание:</b> 
║  <i>{info[1] if info[1] else 'Отсутствует'}</i>
║  
║  🔗 <b>Ссылка:</b> {info[2] if info[2] else 'Не указана'}
║  📊 <b>Статус:</b> {status_with_icon}
║  🛠️ <b>Стек / Навыки:</b> {skills_text}
╚════════════════════════════════💫
"""
    bot.send_message(message.chat.id, card, parse_mode='HTML')

@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = (
        f"👋 <b>Привет, {message.from_user.first_name}!</b>\n\n"
        f"🤖 Я твой персональный <b>Бот-Менеджер Проектов</b>.\n"
        f"Помогу структурировать твои идеи, вести учет репозиториев, "
        f"контролировать статусы задач и прокачивать навыки! 📈\n\n"
        f"Давай наведем порядок в твоем коде и планах! 🚀"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')
    info(message)

@bot.message_handler(commands=['add_description'])
def add_description_column(message):
    bot.send_message(
        message.chat.id,
        "📝 Эта команда пока в разработке. Используй /new_project, /projects или /update_projects для работы с проектами.",
        parse_mode='HTML'
    )

@bot.message_handler(commands=['info'])
def info(message):
    menu_text = """
✨ <b>🚀 ПАНЕЛЬ УПРАВЛЕНИЯ ПРОЕКТАМИ</b> ✨

🧠 <b>Что я умею:</b>
• /start — приветствие и запуск рабочего режима
• /info — открыть эту справку и список команд
• /new_project — создать новый проект с названием, ссылкой и статусом
• /skills — добавить технологии и инструменты в проект
• /projects — показать все твои проекты в одном списке
• /update_projects — изменить описание, ссылку, статус или имя проекта
• /delete — удалить проект навсегда

🎯 <b>Как пользоваться:</b>
1. Создай проект через /new_project
2. Добавь стек через /skills
3. Следи за статусом через /projects
4. Редактируй данные через /update_projects
5. Не бойся экспериментировать — идеи любят порядок! 💡

💎 <b>Фишка:</b> просто напиши точное название проекта в чат — я быстро найду и покажу его карточку!
"""
    bot.send_message(message.chat.id, menu_text, parse_mode='HTML')
#Запустить новый проект 🚀
@bot.message_handler(commands=['new_project'])
def addtask_command(message):
    bot.send_message(message.chat.id, "🚀 <b>Шаг 1.</b> Напиши броское <b>название</b> твоего нового проекта:", parse_mode='HTML')
    bot.register_next_step_handler(message, name_project)

def name_project(message):
    name = message.text
    user_id = message.from_user.id
    data = [user_id, name]
    bot.send_message(message.chat.id, "🌐 <b>Шаг 2.</b> Прикрепи <b>ссылку</b> на проект (GitHub, GitLab, сайт или напиши '-':", parse_mode='HTML')
    bot.register_next_step_handler(message, link_project, data=data)

def link_project(message, data):
    data.append(message.text)
    raw_statuses = [x[0] for x in manager.get_statuses()] 
    
    # Создаем красивое отображение для кнопок
    bot.send_message(
        message.chat.id, 
        "⚡ <b>Шаг 3.</b> Какой у проекта <b>текущий статус</b>? Выбери на клавиатуре:", 
        reply_markup=gen_markup(raw_statuses),
        parse_mode='HTML'
    )
    bot.register_next_step_handler(message, callback_project, data=data, statuses=raw_statuses)

def callback_project(message, data, statuses):
    status = message.text
    if message.text == cancel_button:
        cansel(message)
        return
    if status not in statuses:
        bot.send_message(
            message.chat.id, 
            "⚠️ <b>Упс!</b> Пожалуйста, выбери вариант из предложенных кнопок 👇", 
            reply_markup=gen_markup(statuses),
            parse_mode='HTML'
        )
        bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses)
        return
    
    status_id = manager.get_status_id(status)
    data.append(status_id)
    manager.insert_project([tuple(data)])
    bot.send_message(
        message.chat.id, 
        "🎉 <b>Ура! Проект успешно зафиксирован!</b> Теперь он под моим контролем. 🧠✨", 
        reply_markup=hideBoard,
        parse_mode='HTML'
    )
#Прикрепить технологии и навыки 🛠️
@bot.message_handler(commands=['skills'])
def skill_handler(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(
            message.chat.id, 
            '🛠️ <b>Выбери проект</b>, для которого нужно добавить технологию/навык:', 
            reply_markup=gen_markup(projects),
            parse_mode='HTML'
        )
        bot.register_next_step_handler(message, skill_project, projects=projects)
    else:
        no_projects(message)

def skill_project(message, projects):
    project_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return
        
    if project_name not in projects:
        bot.send_message(
            message.chat.id, 
            '🔍 Такого проекта не найдено. Выбери проект из списка:', 
            reply_markup=gen_markup(projects)
        )
        bot.register_next_step_handler(message, skill_project, projects=projects)
    else:
        skills = [x[1] for x in manager.get_skills()]
        bot.send_message(
            message.chat.id, 
            '💡 Какой <b>навык или инструмент</b> (например: Python, SQL, Docker) ты задействовал?', 
            reply_markup=gen_markup(skills),
            parse_mode='HTML'
        )
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)

def set_skill(message, project_name, skills):
    skill = message.text
    user_id = message.from_user.id
    if message.text == cancel_button:
        cansel(message)
        return
        
    if skill not in skills:
        bot.send_message(
            message.chat.id, 
            '⚠️ Выбери существующий навык из списка, либо добавь его сначала в базу данных!', 
            reply_markup=gen_markup(skills)
        )
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)
        return
    manager.insert_skill(user_id, project_name, skill)
    bot.send_message(
        message.chat.id, 
        f'✅ В стек проекта <b>{project_name}</b> успешно добавлен навык: <code>{skill}</code>! 💪', 
        reply_markup=hideBoard,
        parse_mode='HTML'
    )
#Список всех твоих арен 📂
@bot.message_handler(commands=['projects'])
def get_projects(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        # Формируем красивый компактный список
        title_text = "📂 <b>Твоя библиотека активных проектов:</b>\n\n"
        project_lines = []
        for x in projects:
            project_lines.append(f"• <b>{x[2]}</b> 🔗 <a href='{x[4]}'>Ссылка на репозиторий</a>")
        
        full_text = title_text + "\n".join(project_lines) + "\n\n👇 <i>Нажми на инлайн-кнопку ниже, чтобы открыть интерактивную карточку проекта:</i>"
        
        bot.send_message(
            message.chat.id, 
            full_text, 
            reply_markup=gen_inline_markup([x[2] for x in projects]),
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    else:
        no_projects(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    project_name = call.data
    # Уведомляем Telegram, что нажатие обработано (чтобы кнопка не "зависала" в режиме загрузки)
    bot.answer_callback_query(call.id, text=f"Открываю {project_name}... 🔎")
    info_project(call.message, call.from_user.id, project_name)
#Стереть проект из истории 🗑️
@bot.message_handler(commands=['delete'])
def delete_handler(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    
    if projects:
        # Извлекаем имя проекта из кортежа БД (индекс 2)
        project_names = [x[2] for x in projects]
        
        bot.send_message(
            message.chat.id, 
            "🗑️ <b>Внимание! Режим удаления.</b>\nВыбери проект, который хочешь безвозвратно стереть:", 
            reply_markup=gen_markup(project_names),
            parse_mode='HTML'
        )
        bot.register_next_step_handler(message, delete_project, projects=project_names)
    else:
        no_projects(message)


def delete_project(message, projects):
    project = message.text
    user_id = message.from_user.id

    if message.text == cancel_button:
        cansel(message)
        return
        
    if project not in projects:
        bot.send_message(
            message.chat.id, 
            '❌ Такого проекта нет. Выбери из списка ниже:', 
            reply_markup=gen_markup(projects)
        )
        bot.register_next_step_handler(message, delete_project, projects=projects)
        return
        
    project_id = manager.get_project_id(project, user_id)
    manager.delete_project(user_id, project_id)
    bot.send_message(
        message.chat.id, 
        f'🗑️ Проект <b>{project}</b> был успешно удален. Освобождено место для новых свершений! 🪐',
        reply_markup=hideBoard,
        parse_mode='HTML'
    )

#Тюнинг и изменение данных ⚙️
@bot.message_handler(commands=['update_projects'])
def update_project(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    
    if projects:
        # Извлекаем имя проекта из кортежа БД (индекс 2)
        project_names = [x[2] for x in projects]
        
        bot.send_message(
            message.chat.id, 
            "⚙️ <b>Режим редактирования.</b>\nКакой проект ты хочешь изменить?", 
            reply_markup=gen_markup(project_names),
            parse_mode='HTML'
        )
        bot.register_next_step_handler(message, update_project_step_2, projects=project_names)
    else:
        no_projects(message)


def update_project_step_2(message, projects):
    project_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return
        
    if project_name not in projects:
        bot.send_message(
            message.chat.id, 
            "⚠️ Что-то пошло не так. Пожалуйста, выбери проект кнопкой на клавиатуре:", 
            reply_markup=gen_markup(projects)
        )
        bot.register_next_step_handler(message, update_project_step_2, projects=projects)
        return
    
    # Получаем красивые названия кнопок-атрибутов из вашего словаря
    attributes = list(attributes_of_projects.keys())
    bot.send_message(
        message.chat.id, 
        "💎 <b>Что именно мы будем менять?</b> Выбери категорию:", 
        reply_markup=gen_markup(attributes),
        parse_mode='HTML'
    )
    bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)


def update_project_step_3(message, project_name):
    attribute_key = message.text
    if message.text == cancel_button:
        cansel(message)
        return
        
    if attribute_key not in attributes_of_projects:
        bot.send_message(
            message.chat.id, 
            "⚠️ Выбери пункт меню на клавиатуре!", 
            reply_markup=gen_markup(list(attributes_of_projects.keys()))
        )
        bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)
        return
    
    text_prompt, db_field = attributes_of_projects[attribute_key]
    
    if db_field == "status_id":
        # Извлекаем текстовое имя статуса из кортежа БД (индекс 0)
        statuses = [x[0] for x in manager.get_statuses()]
        
        bot.send_message(
            message.chat.id, 
            text_prompt, 
            reply_markup=gen_markup(statuses), 
            parse_mode='HTML'
        )
        bot.register_next_step_handler(message, save_updated_status, project_name=project_name, db_field=db_field, statuses=statuses)
    else:
        bot.send_message(
            message.chat.id, 
            text_prompt, 
            reply_markup=hideBoard, 
            parse_mode='HTML'
        )
        bot.register_next_step_handler(message, save_updated_project, project_name=project_name, db_field=db_field)


def save_updated_project(message, project_name, db_field):
    if message.text == cancel_button:
        cansel(message)
        return
        
    new_value = message.text
    user_id = message.from_user.id
    
    manager.update_project(user_id, project_name, db_field, new_value)
    bot.send_message(
        message.chat.id, 
        f"✨ <b>Готово!</b> Параметр обновлен. Проект <b>{project_name}</b> стал еще лучше! 💅", 
        reply_markup=hideBoard,
        parse_mode='HTML'
    )


def save_updated_status(message, project_name, db_field, statuses):
    status = message.text
    if message.text == cancel_button:
        cansel(message)
        return
        
    if status not in statuses:
        bot.send_message(
            message.chat.id, 
            "⚠️ Выбери статус из предложенных кнопок!", 
            reply_markup=gen_markup(statuses)
        )
        bot.register_next_step_handler(message, save_updated_status, project_name=project_name, db_field=db_field, statuses=statuses)
        return
        
    status_id = manager.get_status_id(status)
    user_id = message.from_user.id
    
    manager.update_project(user_id, project_name, db_field, status_id)
    
    # Используем функцию красивого отображения статуса с эмодзи
    bot.send_message(
        message.chat.id, 
        f"📊 Статус проекта <b>{project_name}</b> успешно изменен на <b>{get_status_with_emoji(status)}</b>!", 
        reply_markup=hideBoard,
        parse_mode='HTML'
    )
