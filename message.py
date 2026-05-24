
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from datetime import datetime, timedelta

TOKEN = '8838757333:AAHIRBf1R1bhOx2PBzx5_fPHCaglZEZvhaI'
CHANNEL = '@gruziuzz'
ЗАДЕРЖКА = 5  # минут

ВЫБОР, ОТКУДА, КУДА, ТИП_ГРУЗА, ВЕС, СТАВКА, КОНТАКТ = range(7)
МАРШИНА_ОТКУДА, МАШИНА_КУДА, МАШИНА_ТИП, МАШИНА_КОНТАКТ = range(7, 11)

последняя_отправка = {}  # словарь для хранения времени последней отправки

главное_меню = ReplyKeyboardMarkup([
    [KeyboardButton('📦 Добавить груз')],
    [KeyboardButton('🚚 Добавить машину')],
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

def проверить_задержку(user_id):
    if user_id in последняя_отправка:
        прошло = datetime.now() - последняя_отправка[user_id]
        осталось = timedelta(minutes=ЗАДЕРЖКА) - прошло
        if осталось.total_seconds() > 0:
            минуты = int(осталось.total_seconds() // 60)
            секунды = int(осталось.total_seconds() % 60)
            return минуты, секунды
    return None

async def отмена(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text('Главное меню:', reply_markup=главное_меню)
    return ВЫБОР

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Выбери действие:', reply_markup=главное_меню)
    return ВЫБОР

async def выбор(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    задержка = проверить_задержку(user_id)
    if задержка:
        минуты, секунды = задержка
        await update.message.reply_text(
            f'⏳ Подождите ещё {минуты} мин {секунды} сек перед следующей отправкой.',
            reply_markup=главное_меню
        )
        return ВЫБОР

    текст = update.message.text
    if текст == '📦 Добавить груз':
        await update.message.reply_text('Откуда везём?', reply_markup=отмена_кнопка)
        return ОТКУДА
    elif текст == '🚚 Добавить машину':
        await update.message.reply_text('Откуда машина?', reply_markup=отмена_кнопка)
        return МАРШИНА_ОТКУДА

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
    context.user_data['контакт'] = update.message.text

    текст = f"""📦 Новый груз

🚚 Откуда: {context.user_data['откуда']}
📍 Куда: {context.user_data['куда']}
📦 Груз: {context.user_data['тип_груза']}
⚖️ Вес/объём: {context.user_data['вес']}
💰 Ставка: {context.user_data['ставка']}
📞 Контакт: {context.user_data['контакт']}"""

    await context.bot.send_message(chat_id=CHANNEL, text=текст)
    последняя_отправка[user_id] = datetime.now()
    await update.message.reply_text('✅ Груз отправлен в канал!', reply_markup=главное_меню)
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
    context.user_data['м_контакт'] = update.message.text

    текст = f"""🚚 Свободная машина

📍 Откуда: {context.user_data['м_откуда']}
🏁 Куда: {context.user_data['м_куда']}
🚛 Тип: {context.user_data['м_тип']}
📞 Контакт: {context.user_data['м_контакт']}"""

    await context.bot.send_message(chat_id=CHANNEL, text=текст)
    последняя_отправка[user_id] = datetime.now()
    await update.message.reply_text('✅ Машина отправлена в канал!', reply_markup=главное_меню)
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
print('Бот запущен!')
app.run_polling()
