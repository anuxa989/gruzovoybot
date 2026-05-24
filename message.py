from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters, ContextTypes
from datetime import datetime, timedelta
import json
import os

TOKEN = '8838757333:AAHIRBf1R1bhOx2PBzx5_fPHCaglZEZvhaI'
CHANNEL = '@gruzovoyuz'
ЗАДЕРЖКА = 0.5  # минут (30 секунд)
ADMIN_ID = 6611319251  # ЗАМЕНИ НА СВОЙ ID от @userinfobot

ВЫБОР, ОТКУДА, КУДА, ТИП_ГРУЗА, ВЕС, СТАВКА, КОНТАКТ = range(7)
МАРШИНА_ОТКУДА, МАШИНА_КУДА, МАШИНА_ТИП, МАШИНА_КОНТАКТ = range(7, 11)

последняя_отправка = {}

def загрузить_данные():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'users': [], 'грузы': {}, 'машины': {}, 'отписавшиеся': [], 'забаненные': []}

def сохранить_данные(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = загрузить_данные()

главное_меню = ReplyKeyboardMarkup([
    [KeyboardButton('📦 Добавить груз')],
    [KeyboardButton('🚚 Добавить машину')],
    [KeyboardButton('📋 Все грузы'), KeyboardButton('📋 Все машины')],
    [KeyboardButton('🔕 Отписаться'), KeyboardButton('🗑 Удалить моё')],
], resize_keyboard=True)

меню_отписан = ReplyKeyboardMarkup([
    [KeyboardButton('📦 Добавить груз')],
    [KeyboardButton('🚚 Добавить машину')],
    [KeyboardButton('📋 Все грузы'), KeyboardButton('📋 Все машины')],
    [KeyboardButton('🔔 Подписаться'), KeyboardButton('🗑 Удалить моё')],
], resize_keyboard=True)

админ_меню = ReplyKeyboardMarkup([
    [KeyboardButton('📦 Добавить груз')],
    [KeyboardButton('🚚 Добавить машину')],
    [KeyboardButton('📋 Все грузы'), KeyboardButton('📋 Все машины')],
    [KeyboardButton('🔕 Отписаться'), KeyboardButton('🗑 Удалить моё')],
    [KeyboardButton('👮 Админ панель')],
], resize_keyboard=True)

отмена_кнопка = ReplyKeyboardMarkup([
    [KeyboardButton('❌ Отмена')]
], resize_keyboard=True)

тип_машины_кнопки = ReplyKeyboardMarkup([
    [KeyboardButton('🚛 Тент'), KeyboardButton('❄️ Реф')],
    [KeyboardButton('🚂 Паровоз'), KeyboardButton('📦 Контейнер')],
    [KeyboardButton('🚐 Газель'), KeyboardButton('🏗 Борт')],
    [KeyboardButton('❌ Отмена')],
], resize_keyboard=True)

def получить_меню(user_id):
    if user_id == ADMIN_ID:
        return админ_меню
    if str(user_id) in data.get('отписавшиеся', []):
        return меню_отписан
    return главное_меню

def проверить_задержку(user_id):
    if user_id in последняя_отправка:
        прошло = datetime.now() - последняя_отправка[user_id]
        осталось = timedelta(minutes=ЗАДЕРЖКА) - прошло
        if осталось.total_seconds() > 0:
            секунды = int(осталось.total_seconds())
            return 0, секунды
    return None

def статистика():
    грузов = len(data.get('грузы', {}))
    машин = len(data.get('машины', {}))
    return f'\n\n📊 Сейчас активно: {грузов} груз(ов) | {машин} машин(ы)'

async def разослать_всем(context, текст):
    for user_id in list(data.get('users', [])):
        if str(user_id) in data.get('отписавшиеся', []):
            continue
        if str(user_id) in data.get('забаненные', []):
            continue
        try:
            await context.bot.send_message(chat_id=user_id, text=текст)
        except Exception:
            pass

def создать_кнопки_списка(items_dict, тип, page=0):
    items = list(items_dict.items())
    per_page = 5
    start = page * per_page
    end = start + per_page
    page_items = items[start:end]

    buttons = []
    for idx, (user_id, item) in enumerate(page_items, start=start+1):
        краткое = item.get('краткое', f'{тип} {idx}')
        msg_id = item.get('msg_id', 0)

        buttons.append([InlineKeyboardButton(
            f"{idx}. {краткое}",
            url=f"https://t.me/gruzovoyuz/{msg_id}"
        )])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"{тип}_page_{page-1}"))
    if end < len(items):
        nav_buttons.append(InlineKeyboardButton("Вперёд ▶️", callback_data=f"{тип}_page_{page+1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    return InlineKeyboardMarkup(buttons)

async def показать_грузы(update, context, page=0):
    if not data.get('грузы'):
        if update.callback_query:
            await update.callback_query.answer("Активных грузов нет")
        else:
            await update.message.reply_text('Активных грузов нет.')
        return

    keyboard = создать_кнопки_списка(data['грузы'], 'груз', page)
    текст = f"📦 Активные грузы (стр. {page+1}):"

    if update.callback_query:
        await update.callback_query.edit_message_text(текст, reply_markup=keyboard)
    else:
        await update.message.reply_text(текст, reply_markup=keyboard)

async def показать_машины(update, context, page=0):
    if not data.get('машины'):
        if update.callback_query:
            await update.callback_query.answer("Свободных машин нет")
        else:
            await update.message.reply_text('Свободных машин нет.')
        return

    keyboard = создать_кнопки_списка(data['машины'], 'машина', page)
    текст = f"🚚 Свободные машины (стр. {page+1}):"

    if update.callback_query:
        await update.callback_query.edit_message_text(текст, reply_markup=keyboard)
    else:
        await update.message.reply_text(текст, reply_markup=keyboard)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith('груз_page_'):
        page = int(query.data.split('_')[-1])
        await показать_грузы(update, context, page)
    elif query.data.startswith('машина_page_'):
        page = int(query.data.split('_')[-1])
        await показать_машины(update, context, page)

async def отмена(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user_id = update.message.from_user.id
    await update.message.reply_text('Главное меню:', reply_markup=получить_меню(user_id))
    return ВЫБОР

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in data.get('users', []):
        data.setdefault('users', []).append(user_id)
        сохранить_данные(data)
    await update.message.reply_text(
        'Добро пожаловать! 👋\n\nЭтот бот помогает добавлять грузы и машины в канал @gruzovoyuz\n\nВыбери действие:',
        reply_markup=получить_меню(user_id)
    )
    return ВЫБОР

async def выбор(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    текст = update.message.text
    uid = str(user_id)

    if uid in data.get('забаненные', []):
        await update.message.reply_text('🚫 Вы заблокированы.')
        return ВЫБОР

    if текст == '🔕 Отписаться':
        if uid not in data.get('отписавшиеся', []):
            data.setdefault('отписавшиеся', []).append(uid)
            сохранить_данные(data)
        await update.message.reply_text('🔕 Вы отписались от уведомлений.', reply_markup=получить_меню(user_id))
        return ВЫБОР

    if текст == '🔔 Подписаться':
        if uid in data.get('отписавшиеся', []):
            data['отписавшиеся'].remove(uid)
            сохранить_данные(data)
        await update.message.reply_text('🔔 Вы подписались на уведомления!', reply_markup=получить_меню(user_id))
        return ВЫБОР

    if текст == '📋 Все грузы':
        await показать_грузы(update, context, 0)
        return ВЫБОР

    if текст == '📋 Все машины':
        await показать_машины(update, context, 0)
        return ВЫБОР

    if текст == '🗑 Удалить моё':
        удалено = False
        if uid in data.get('грузы', {}):
            try:
                msg_id = data['грузы'][uid].get('msg_id')
                if msg_id:
                    await context.bot.delete_message(chat_id=CHANNEL, message_id=msg_id)
            except Exception:
                pass
            del data['грузы'][uid]
            удалено = True
        if uid in data.get('машины', {}):
            try:
                msg_id = data['машины'][uid].get('msg_id')
                if msg_id:
                    await context.bot.delete_message(chat_id=CHANNEL, message_id=msg_id)
            except Exception:
                pass
            del data['машины'][uid]
            удалено = True

        if удалено:
            сохранить_данные(data)
            await update.message.reply_text('✅ Ваше объявление удалено!', reply_markup=получить_меню(user_id))
        else:
            await update.message.reply_text('У вас нет активных объявлений.', reply_markup=получить_меню(user_id))
        return ВЫБОР

    if текст == '👮 Админ панель' and user_id == ADMIN_ID:
        грузов = len(data.get('грузы', {}))
        машин = len(data.get('машины', {}))
        пользователей = len(data.get('users', []))
        забанено = len(data.get('забаненные', []))

        # Список всех объявлений с ID пользователей
        список_грузов = ''
        for uid, item in data.get('грузы', {}).items():
            список_грузов += f"\n  • ID {uid}: {item.get('краткое', '?')}"

        список_машин = ''
        for uid, item in data.get('машины', {}).items():
            список_машин += f"\n  • ID {uid}: {item.get('краткое', '?')}"

        await update.message.reply_text(
            f'👮 Админ панель\n\n'
            f'👥 Пользователей: {пользователей}\n'
            f'📦 Активных грузов: {грузов}{список_грузов}\n\n'
            f'🚚 Свободных машин: {машин}{список_машин}\n\n'
            f'🚫 Забанено: {забанено}\n\n'
            f'━━━━━━━━━━━━━━━\n'
            f'Команды:\n'
            f'/ban ID — забанить\n'
            f'/unban ID — разбанить\n'
            f'/delcargo ID — удалить груз пользователя\n'
            f'/delcar ID — удалить машину пользователя',
            reply_markup=получить_меню(user_id)
        )
        return ВЫБОР

    задержка = проверить_задержку(user_id)
    if задержка:
        минуты, секунды = задержка
        await update.message.reply_text(
            f'⏳ Подождите ещё {секунды} сек.',
            reply_markup=получить_меню(user_id)
        )
        return ВЫБОР

    if текст == '📦 Добавить груз':
        await update.message.reply_text('Откуда везём?', reply_markup=отмена_кнопка)
        return ОТКУДА
    elif текст == '🚚 Добавить машину':
        await update.message.reply_text('Откуда машина?', reply_markup=отмена_кнопка)
        return МАРШИНА_ОТКУДА

async def бан(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    if context.args:
        uid = context.args[0]
        data.setdefault('забаненные', []).append(uid)
        сохранить_данные(data)
        await update.message.reply_text(f'🚫 Пользователь {uid} забанен.')

async def разбан(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    if context.args:
        uid = context.args[0]
        if uid in data.get('забаненные', []):
            data['забаненные'].remove(uid)
            сохранить_данные(data)
        await update.message.reply_text(f'✅ Пользователь {uid} разбанен.')

async def удалить_груз_админ(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ удаляет груз по ID пользователя: /delcargo USER_ID"""
    if update.message.from_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text('Использование: /delcargo USER_ID')
        return

    uid = context.args[0]
    if uid in data.get('грузы', {}):
        try:
            msg_id = data['грузы'][uid].get('msg_id')
            if msg_id:
                await context.bot.delete_message(chat_id=CHANNEL, message_id=msg_id)
        except Exception:
            pass
        краткое = data['грузы'][uid].get('краткое', '?')
        del data['грузы'][uid]
        сохранить_данные(data)
        await update.message.reply_text(f'✅ Груз пользователя {uid} удалён ({краткое}).')
    else:
        await update.message.reply_text(f'❌ Груз пользователя {uid} не найден.')

async def удалить_машину_админ(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ удаляет машину по ID пользователя: /delcar USER_ID"""
    if update.message.from_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text('Использование: /delcar USER_ID')
        return

    uid = context.args[0]
    if uid in data.get('машины', {}):
        try:
            msg_id = data['машины'][uid].get('msg_id')
            if msg_id:
                await context.bot.delete_message(chat_id=CHANNEL, message_id=msg_id)
        except Exception:
            pass
        краткое = data['машины'][uid].get('краткое', '?')
        del data['машины'][uid]
        сохранить_данные(data)
        await update.message.reply_text(f'✅ Машина пользователя {uid} удалена ({краткое}).')
    else:
        await update.message.reply_text(f'❌ Машина пользователя {uid} не найдена.')

async def откуда(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['откуда'] = update.message.text
    await update.message.reply_text('Куда везём?', reply_markup=отмена_кнопка)
    return КУДА

async def куда(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['куда'] = update.message.text
    await update.message.reply_text('Какой груз?', reply_markup=отмена_кнопка)
    return ТИП_ГРУЗА

async def тип_груза(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['тип_груза'] = update.message.text
    await update.message.reply_text('Вес и объём?', reply_markup=отмена_кнопка)
    return ВЕС

async def вес(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['вес'] = update.message.text
    await update.message.reply_text('Ставка за перевозку?', reply_markup=отмена_кнопка)
    return СТАВКА

async def ставка(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ставка'] = update.message.text
    await update.message.reply_text('Контакт для связи?', reply_markup=отмена_кнопка)
    return КОНТАКТ

async def контакт(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    uid = str(user_id)
    context.user_data['контакт'] = update.message.text

    текст = f"""📦 Новый груз

🚚 Откуда: {context.user_data['откуда']}
📍 Куда: {context.user_data['куда']}
📦 Груз: {context.user_data['тип_груза']}
⚖️ Вес/объём: {context.user_data['вес']}
💰 Ставка: {context.user_data['ставка']}
📞 Контакт: {context.user_data['контакт']}"""

    краткое = f"{context.user_data['откуда']} → {context.user_data['куда']}"
    data.setdefault('грузы', {})[uid] = {
        'msg_id': 0,
        'краткое': краткое,
        'текст': текст
    }
    сохранить_данные(data)

    msg = await context.bot.send_message(chat_id=CHANNEL, text=текст + статистика())

    data['грузы'][uid]['msg_id'] = msg.message_id
    сохранить_данные(data)

    await разослать_всем(context, f'🔔 Новый груз!\n\n{текст}{статистика()}')
    последняя_отправка[user_id] = datetime.now()
    await update.message.reply_text('✅ Груз отправлен в канал!', reply_markup=получить_меню(user_id))
    return ВЫБОР

async def машина_откуда(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['м_откуда'] = update.message.text
    await update.message.reply_text('Куда едет машина?', reply_markup=отмена_кнопка)
    return МАШИНА_КУДА

async def машина_куда(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['м_куда'] = update.message.text
    await update.message.reply_text('Выбери тип машины:', reply_markup=тип_машины_кнопки)
    return МАШИНА_ТИП

async def машина_тип(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['м_тип'] = update.message.text
    await update.message.reply_text('Контакт водителя?', reply_markup=отмена_кнопка)
    return МАШИНА_КОНТАКТ

async def машина_контакт(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    uid = str(user_id)
    context.user_data['м_контакт'] = update.message.text

    текст = f"""🚚 Свободная машина

📍 Откуда: {context.user_data['м_откуда']}
🏁 Куда: {context.user_data['м_куда']}
🚛 Тип: {context.user_data['м_тип']}
📞 Контакт: {context.user_data['м_контакт']}"""

    краткое = f"{context.user_data['м_откуда']} → {context.user_data['м_куда']}"
    data.setdefault('машины', {})[uid] = {
        'msg_id': 0,
        'краткое': краткое,
        'текст': текст
    }
    сохранить_данные(data)

    msg = await context.bot.send_message(chat_id=CHANNEL, text=текст + статистика())

    data['машины'][uid]['msg_id'] = msg.message_id
    сохранить_данные(data)

    await разослать_всем(context, f'🔔 Новая машина!\n\n{текст}{статистика()}')
    последняя_отправка[user_id] = datetime.now()
    await update.message.reply_text('✅ Машина отправлена в канал!', reply_markup=получить_меню(user_id))
    return ВЫБОР

отмена_фильтр = MessageHandler(filters.Regex('^❌ Отмена$'), отмена)

app = Application.builder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        ВЫБОР: [MessageHandler(filters.TEXT & ~filters.COMMAND, выбор)],
        ОТКУДА: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, откуда)],
        КУДА: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, куда)],
        ТИП_ГРУЗА: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, тип_груза)],
        ВЕС: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, вес)],
        СТАВКА: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, ставка)],
        КОНТАКТ: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, контакт)],
        МАРШИНА_ОТКУДА: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, машина_откуда)],
        МАШИНА_КУДА: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, машина_куда)],
        МАШИНА_ТИП: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, машина_тип)],
        МАШИНА_КОНТАКТ: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, машина_контакт)],
    },
    fallbacks=[отмена_фильтр]
)

app.add_handler(conv)
app.add_handler(CommandHandler('ban', бан))
app.add_handler(CommandHandler('unban', разбан))
app.add_handler(CommandHandler('delcargo', удалить_груз_админ))
app.add_handler(CommandHandler('delcar', удалить_машину_админ))
app.add_handler(CallbackQueryHandler(callback_handler))
print('Бот запущен!')
app.run_polling()
