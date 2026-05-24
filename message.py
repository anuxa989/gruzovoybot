from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters, ContextTypes
from datetime import datetime, timedelta
from pymongo import MongoClient
import os

# ── Словарь городов → флаг страны ─────────────────────
ГОРОДА_ФЛАГИ = {
    # Узбекистан 🇺🇿
    'ташкент': '🇺🇿', 'самарканд': '🇺🇿', 'бухара': '🇺🇿', 'наманган': '🇺🇿',
    'андижан': '🇺🇿', 'фергана': '🇺🇿', 'нукус': '🇺🇿', 'карши': '🇺🇿',
    'термез': '🇺🇿', 'навои': '🇺🇿', 'коканд': '🇺🇿', 'маргилан': '🇺🇿',
    'чирчик': '🇺🇿', 'ангрен': '🇺🇿', 'джизак': '🇺🇿', 'гулистан': '🇺🇿',
    'ургенч': '🇺🇿', 'хива': '🇺🇿',

    # Россия 🇷🇺
    'москва': '🇷🇺', 'мск': '🇷🇺', 'санкт-петербург': '🇷🇺', 'спб': '🇷🇺',
    'питер': '🇷🇺', 'новосибирск': '🇷🇺', 'екатеринбург': '🇷🇺', 'екб': '🇷🇺',
    'казань': '🇷🇺', 'нижний новгород': '🇷🇺', 'челябинск': '🇷🇺',
    'омск': '🇷🇺', 'самара': '🇷🇺', 'уфа': '🇷🇺', 'красноярск': '🇷🇺',
    'пермь': '🇷🇺', 'воронеж': '🇷🇺', 'волгоград': '🇷🇺', 'краснодар': '🇷🇺',
    'саратов': '🇷🇺', 'тюмень': '🇷🇺', 'тольятти': '🇷🇺', 'ижевск': '🇷🇺',
    'барнаул': '🇷🇺', 'иркутск': '🇷🇺', 'новокузнецк': '🇷🇺', 'хабаровск': '🇷🇺',
    'владивосток': '🇷🇺', 'ярославль': '🇷🇺', 'ростов-на-дону': '🇷🇺', 'ростов': '🇷🇺',
    'оренбург': '🇷🇺', 'кемерово': '🇷🇺', 'томск': '🇷🇺', 'астрахань': '🇷🇺',
    'рязань': '🇷🇺', 'пенза': '🇷🇺', 'липецк': '🇷🇺', 'тула': '🇷🇺',
    'киров': '🇷🇺', 'чебоксары': '🇷🇺', 'калининград': '🇷🇺', 'брянск': '🇷🇺',
    'курск': '🇷🇺', 'иваново': '🇷🇺', 'магнитогорск': '🇷🇺', 'улан-удэ': '🇷🇺',
    'тверь': '🇷🇺', 'ставрополь': '🇷🇺', 'белгород': '🇷🇺', 'сочи': '🇷🇺',
    'владимир': '🇷🇺', 'нальчик': '🇷🇺', 'симферополь': '🇷🇺',

    # Казахстан 🇰🇿
    'алматы': '🇰🇿', 'алма-ата': '🇰🇿', 'астана': '🇰🇿', 'нур-султан': '🇰🇿',
    'шымкент': '🇰🇿', 'караганда': '🇰🇿', 'актобе': '🇰🇿', 'тараз': '🇰🇿',
    'павлодар': '🇰🇿', 'усть-каменогорск': '🇰🇿', 'семей': '🇰🇿', 'атырау': '🇰🇿',
    'костанай': '🇰🇿', 'кызылорда': '🇰🇿', 'уральск': '🇰🇿', 'петропавловск': '🇰🇿',
    'актау': '🇰🇿', 'темиртау': '🇰🇿', 'туркестан': '🇰🇿',

    # Кыргызстан 🇰🇬
    'бишкек': '🇰🇬', 'ош': '🇰🇬', 'джалал-абад': '🇰🇬', 'каракол': '🇰🇬',
    'токмок': '🇰🇬', 'кант': '🇰🇬', 'узген': '🇰🇬', 'нарын': '🇰🇬',

    # Таджикистан 🇹🇯
    'душанбе': '🇹🇯', 'худжанд': '🇹🇯', 'куляб': '🇹🇯', 'курган-тюбе': '🇹🇯',
    'бохтар': '🇹🇯', 'истаравшан': '🇹🇯', 'пенджикент': '🇹🇯',

    # Туркменистан 🇹🇲
    'ашхабад': '🇹🇲', 'туркменабад': '🇹🇲', 'мары': '🇹🇲', 'туркменбаши': '🇹🇲',
    'дашогуз': '🇹🇲',

    # Азербайджан 🇦🇿
    'баку': '🇦🇿', 'гянджа': '🇦🇿', 'сумгаит': '🇦🇿', 'мингячевир': '🇦🇿',
    'нахчыван': '🇦🇿', 'лянкяран': '🇦🇿',

    # Армения 🇦🇲
    'ереван': '🇦🇲', 'гюмри': '🇦🇲', 'ванадзор': '🇦🇲',

    # Грузия 🇬🇪
    'тбилиси': '🇬🇪', 'батуми': '🇬🇪', 'кутаиси': '🇬🇪', 'рустави': '🇬🇪',

    # Украина 🇺🇦
    'киев': '🇺🇦', 'харьков': '🇺🇦', 'одесса': '🇺🇦', 'днепр': '🇺🇦',
    'запорожье': '🇺🇦', 'львов': '🇺🇦', 'николаев': '🇺🇦',

    # Беларусь 🇧🇾
    'минск': '🇧🇾', 'гомель': '🇧🇾', 'могилёв': '🇧🇾', 'витебск': '🇧🇾',
    'гродно': '🇧🇾', 'брест': '🇧🇾',

    # Китай 🇨🇳
    'пекин': '🇨🇳', 'шанхай': '🇨🇳', 'урумчи': '🇨🇳', 'кашгар': '🇨🇳',
    'гуанчжоу': '🇨🇳', 'шэньчжэнь': '🇨🇳', 'иу': '🇨🇳', 'ичан': '🇨🇳',
    'тяньцзинь': '🇨🇳', 'чэнду': '🇨🇳',

    # Турция 🇹🇷
    'стамбул': '🇹🇷', 'анкара': '🇹🇷', 'измир': '🇹🇷', 'бурса': '🇹🇷',
    'анталья': '🇹🇷', 'трабзон': '🇹🇷',

    # Иран 🇮🇷
    'тегеран': '🇮🇷', 'мешхед': '🇮🇷', 'исфахан': '🇮🇷', 'тебриз': '🇮🇷',
    'шираз': '🇮🇷',

    # Афганистан 🇦🇫
    'кабул': '🇦🇫', 'мазари-шариф': '🇦🇫', 'герат': '🇦🇫', 'кандагар': '🇦🇫',
    'термез афг': '🇦🇫', 'хайратон': '🇦🇫',
}

def получить_флаг(город: str) -> str:
    город_lower = город.strip().lower()
    if город_lower in ГОРОДА_ФЛАГИ:
        return ГОРОДА_ФЛАГИ[город_lower]
    for ключ, флаг in ГОРОДА_ФЛАГИ.items():
        if ключ in город_lower or город_lower.startswith(ключ):
            return флаг
    return '📍'

# ── Подключение к MongoDB ──────────────────────────────
MONGO_URI = os.getenv('MONGO_URI')  # добавь в переменные Railway
mongo_client = MongoClient(MONGO_URI)
db_mongo = mongo_client['gruzovoyuz']
col = db_mongo['data']  # одна коллекция, один документ

def загрузить_данные():
    doc = col.find_one({'_id': 'main'})
    if doc:
        doc.pop('_id', None)
        return doc
    return {'users': [], 'роли': {}, 'грузы': {}, 'машины': {}, 'отписавшиеся': [], 'забаненные': []}

def сохранить_данные(data):
    col.replace_one({'_id': 'main'}, {'_id': 'main', **data}, upsert=True)

# ── Настройки бота ─────────────────────────────────────
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL = '@gruzovoyuz'
ЗАДЕРЖКА = 0.5  # минут (30 секунд)
ADMIN_ID = 6611319251

# Состояния
(ВЫБОР_РОЛИ, ВЫБОР,
 ОТКУДА, КУДА, ТИП_ГРУЗА, ВЕС, СТАВКА, КОЛ_ВО_МАШИН, КОНТАКТ) = range(9)
(МАРШИНА_ОТКУДА, МАШИНА_КУДА, МАШИНА_ТИП, МАШИНА_КОЛ_ВО, МАШИНА_КОНТАКТ) = range(9, 14)

последняя_отправка = {}
data = загрузить_данные()

# ── Клавиатуры ─────────────────────────────────────────
меню_роли = ReplyKeyboardMarkup([
    [KeyboardButton('🚛 Я водитель')],
    [KeyboardButton('📦 Я грузоотправитель')],
], resize_keyboard=True)

меню_водитель = ReplyKeyboardMarkup([
    [KeyboardButton('🚚 Добавить машину')],
    [KeyboardButton('📋 Все грузы')],
    [KeyboardButton('🔕 Отписаться'), KeyboardButton('🗑 Удалить моё')],
], resize_keyboard=True)

меню_водитель_отписан = ReplyKeyboardMarkup([
    [KeyboardButton('🚚 Добавить машину')],
    [KeyboardButton('📋 Все грузы')],
    [KeyboardButton('🔔 Подписаться'), KeyboardButton('🗑 Удалить моё')],
], resize_keyboard=True)

меню_грузо = ReplyKeyboardMarkup([
    [KeyboardButton('📦 Добавить груз')],
    [KeyboardButton('📋 Все машины'), KeyboardButton('📋 Все грузы')],
    [KeyboardButton('🔕 Отписаться'), KeyboardButton('🗑 Удалить моё')],
], resize_keyboard=True)

меню_грузо_отписан = ReplyKeyboardMarkup([
    [KeyboardButton('📦 Добавить груз')],
    [KeyboardButton('📋 Все машины'), KeyboardButton('📋 Все грузы')],
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

# ── Вспомогательные функции ────────────────────────────
def получить_роль(user_id):
    return data.get('роли', {}).get(str(user_id), None)

def получить_меню(user_id):
    if user_id == ADMIN_ID:
        return админ_меню
    uid = str(user_id)
    роль = получить_роль(user_id)
    отписан = uid in data.get('отписавшиеся', [])
    if роль == 'водитель':
        return меню_водитель_отписан if отписан else меню_водитель
    elif роль == 'грузоотправитель':
        return меню_грузо_отписан if отписан else меню_грузо
    return меню_роли

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
    for idx, (запись_id, item) in enumerate(page_items, start=start+1):
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

# ── Старт ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in data.get('users', []):
        data.setdefault('users', []).append(user_id)
        сохранить_данные(data)

    if user_id == ADMIN_ID or получить_роль(user_id):
        await update.message.reply_text('Главное меню:', reply_markup=получить_меню(user_id))
        return ВЫБОР

    await update.message.reply_text('Добро пожаловать! 👋\n\nКто вы?', reply_markup=меню_роли)
    return ВЫБОР_РОЛИ

async def обработка_роли(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    uid = str(user_id)
    текст = update.message.text

    if текст == '🚛 Я водитель':
        data.setdefault('роли', {})[uid] = 'водитель'
        сохранить_данные(data)
        await update.message.reply_text(
            '✅ Вы вошли как водитель!\n\nМожете добавить свою машину или посмотреть доступные грузы.',
            reply_markup=получить_меню(user_id)
        )
        return ВЫБОР
    elif текст == '📦 Я грузоотправитель':
        data.setdefault('роли', {})[uid] = 'грузоотправитель'
        сохранить_данные(data)
        await update.message.reply_text(
            '✅ Вы вошли как грузоотправитель!\n\nМожете добавить груз или найти машину.',
            reply_markup=получить_меню(user_id)
        )
        return ВЫБОР
    else:
        await update.message.reply_text('Пожалуйста, выберите кто вы:', reply_markup=меню_роли)
        return ВЫБОР_РОЛИ

# ── Главное меню ───────────────────────────────────────
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

        грузы_удалить = [
            k for k, v in data.get('грузы', {}).items()
            if v.get('owner') == uid or k == uid
        ]
        for ключ in грузы_удалить:
            try:
                msg_id = data['грузы'][ключ].get('msg_id')
                if msg_id:
                    await context.bot.delete_message(chat_id=CHANNEL, message_id=msg_id)
            except Exception:
                pass
            del data['грузы'][ключ]
            удалено = True

        машины_удалить = [
            k for k, v in data.get('машины', {}).items()
            if v.get('owner') == uid or k == uid
        ]
        for ключ in машины_удалить:
            try:
                msg_id = data['машины'][ключ].get('msg_id')
                if msg_id:
                    await context.bot.delete_message(chat_id=CHANNEL, message_id=msg_id)
            except Exception:
                pass
            del data['машины'][ключ]
            удалено = True

        if удалено:
            сохранить_данные(data)
            await update.message.reply_text('✅ Ваши объявления удалены!', reply_markup=получить_меню(user_id))
        else:
            await update.message.reply_text('У вас нет активных объявлений.', reply_markup=получить_меню(user_id))
        return ВЫБОР

    if текст == '👮 Админ панель' and user_id == ADMIN_ID:
        грузов = len(data.get('грузы', {}))
        машин = len(data.get('машины', {}))
        пользователей = len(data.get('users', []))
        забанено = len(data.get('забаненные', []))
        список_грузов = ''
        for запись_id, item in data.get('грузы', {}).items():
            owner = item.get('owner', запись_id)
            список_грузов += f"\n  • ID {owner}: {item.get('краткое', '?')}"
        список_машин = ''
        for запись_id, item in data.get('машины', {}).items():
            owner = item.get('owner', запись_id)
            список_машин += f"\n  • ID {owner}: {item.get('краткое', '?')}"
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
            f'/delcargo ID — удалить все грузы пользователя\n'
            f'/delcar ID — удалить все машины пользователя',
            reply_markup=получить_меню(user_id)
        )
        return ВЫБОР

    if user_id != ADMIN_ID:
        задержка = проверить_задержку(user_id)
        if задержка and текст in ('📦 Добавить груз', '🚚 Добавить машину'):
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

# ── Грузы ──────────────────────────────────────────────
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
    await update.message.reply_text('Сколько машин нужно?', reply_markup=отмена_кнопка)
    return КОЛ_ВО_МАШИН

async def кол_во_машин(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['кол_во_машин'] = update.message.text
    await update.message.reply_text('Контакт для связи?', reply_markup=отмена_кнопка)
    return КОНТАКТ

async def контакт(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    uid = str(user_id)
    context.user_data['контакт'] = update.message.text

    флаг_откуда = получить_флаг(context.user_data['откуда'])
    флаг_куда = получить_флаг(context.user_data['куда'])

    текст = f"""📦 Новый груз

{флаг_откуда} Откуда: {context.user_data['откуда']}
{флаг_куда} Куда: {context.user_data['куда']}
📦 Груз: {context.user_data['тип_груза']}
⚖️ Вес/объём: {context.user_data['вес']}
💰 Ставка: {context.user_data['ставка']}
🚛 Нужно машин: {context.user_data['кол_во_машин']}
📞 Контакт: {context.user_data['контакт']}"""

    краткое = f"{context.user_data['откуда']} → {context.user_data['куда']}"
    запись_id = f"{uid}_{int(datetime.now().timestamp())}"
    data.setdefault('грузы', {})[запись_id] = {
        'msg_id': 0, 'краткое': краткое, 'текст': текст, 'owner': uid,
    }
    сохранить_данные(data)

    msg = await context.bot.send_message(chat_id=CHANNEL, text=текст + статистика())
    data['грузы'][запись_id]['msg_id'] = msg.message_id
    сохранить_данные(data)

    await разослать_всем(context, f'🔔 Новый груз!\n\n{текст}{статистика()}')
    последняя_отправка[user_id] = datetime.now()
    await update.message.reply_text('✅ Груз отправлен в канал!', reply_markup=получить_меню(user_id))
    return ВЫБОР

# ── Машины ─────────────────────────────────────────────
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
    await update.message.reply_text('Сколько машин?', reply_markup=отмена_кнопка)
    return МАШИНА_КОЛ_ВО

async def машина_кол_во(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['м_кол_во'] = update.message.text
    await update.message.reply_text('Контакт водителя?', reply_markup=отмена_кнопка)
    return МАШИНА_КОНТАКТ

async def машина_контакт(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    uid = str(user_id)
    context.user_data['м_контакт'] = update.message.text

    флаг_откуда = получить_флаг(context.user_data['м_откуда'])
    флаг_куда = получить_флаг(context.user_data['м_куда'])

    текст = f"""🚚 Свободная машина

{флаг_откуда} Откуда: {context.user_data['м_откуда']}
{флаг_куда} Куда: {context.user_data['м_куда']}
🚛 Тип: {context.user_data['м_тип']}
🔢 Количество: {context.user_data['м_кол_во']}
📞 Контакт: {context.user_data['м_контакт']}"""

    краткое = f"{context.user_data['м_откуда']} → {context.user_data['м_куда']}"
    запись_id = f"{uid}_{int(datetime.now().timestamp())}"
    data.setdefault('машины', {})[запись_id] = {
        'msg_id': 0, 'краткое': краткое, 'текст': текст, 'owner': uid,
    }
    сохранить_данные(data)

    msg = await context.bot.send_message(chat_id=CHANNEL, text=текст + статистика())
    data['машины'][запись_id]['msg_id'] = msg.message_id
    сохранить_данные(data)

    await разослать_всем(context, f'🔔 Новая машина!\n\n{текст}{статистика()}')
    последняя_отправка[user_id] = datetime.now()
    await update.message.reply_text('✅ Машина отправлена в канал!', reply_markup=получить_меню(user_id))
    return ВЫБОР

# ── Админ команды ──────────────────────────────────────
async def список_пользователей(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    роли = data.get('роли', {})
    грузы = data.get('грузы', {})
    машины = data.get('машины', {})
    забаненные = data.get('забаненные', [])
    текст = f'👥 Все пользователи ({len(data.get("users", []))}):\n\n'
    for user_id in data.get('users', []):
        uid = str(user_id)
        роль = роли.get(uid, 'не выбрана')
        статус = '🚫 забанен' if uid in забаненные else '✅'
        груз_инфо = ''
        for v in грузы.values():
            if v.get('owner') == uid:
                груз_инфо += f"\n    📦 {v.get('краткое', '?')}"
        машина_инфо = ''
        for v in машины.values():
            if v.get('owner') == uid:
                машина_инфо += f"\n    🚚 {v.get('краткое', '?')}"
        текст += f'{статус} ID: {uid}\n    Роль: {роль}{груз_инфо}{машина_инфо}\n\n'
    if len(текст) > 4096:
        текст = текст[:4090] + '\n...'
    await update.message.reply_text(текст)

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
    if update.message.from_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text('Использование: /delcargo USER_ID')
        return
    uid = context.args[0]
    грузы_удалить = [
        k for k, v in data.get('грузы', {}).items()
        if v.get('owner') == uid or k == uid
    ]
    if грузы_удалить:
        for ключ in грузы_удалить:
            try:
                msg_id = data['грузы'][ключ].get('msg_id')
                if msg_id:
                    await context.bot.delete_message(chat_id=CHANNEL, message_id=msg_id)
            except Exception:
                pass
            del data['грузы'][ключ]
        сохранить_данные(data)
        await update.message.reply_text(f'✅ Все грузы пользователя {uid} удалены ({len(грузы_удалить)} шт.).')
    else:
        await update.message.reply_text(f'❌ Грузы пользователя {uid} не найдены.')

async def удалить_машину_админ(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text('Использование: /delcar USER_ID')
        return
    uid = context.args[0]
    машины_удалить = [
        k for k, v in data.get('машины', {}).items()
        if v.get('owner') == uid or k == uid
    ]
    if машины_удалить:
        for ключ in машины_удалить:
            try:
                msg_id = data['машины'][ключ].get('msg_id')
                if msg_id:
                    await context.bot.delete_message(chat_id=CHANNEL, message_id=msg_id)
            except Exception:
                pass
            del data['машины'][ключ]
        сохранить_данные(data)
        await update.message.reply_text(f'✅ Все машины пользователя {uid} удалены ({len(машины_удалить)} шт.).')
    else:
        await update.message.reply_text(f'❌ Машины пользователя {uid} не найдены.')

# ── Запуск ─────────────────────────────────────────────
отмена_фильтр = MessageHandler(filters.Regex('^❌ Отмена$'), отмена)

app = Application.builder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        ВЫБОР_РОЛИ: [MessageHandler(filters.TEXT & ~filters.COMMAND, обработка_роли)],
        ВЫБОР: [MessageHandler(filters.TEXT & ~filters.COMMAND, выбор)],
        ОТКУДА: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, откуда)],
        КУДА: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, куда)],
        ТИП_ГРУЗА: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, тип_груза)],
        ВЕС: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, вес)],
        СТАВКА: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, ставка)],
        КОЛ_ВО_МАШИН: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, кол_во_машин)],
        КОНТАКТ: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, контакт)],
        МАРШИНА_ОТКУДА: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, машина_откуда)],
        МАШИНА_КУДА: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, машина_куда)],
        МАШИНА_ТИП: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, машина_тип)],
        МАШИНА_КОЛ_ВО: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, машина_кол_во)],
        МАШИНА_КОНТАКТ: [отмена_фильтр, MessageHandler(filters.TEXT & ~filters.COMMAND, машина_контакт)],
    },
    fallbacks=[отмена_фильтр]
)

app.add_handler(conv)
app.add_handler(CommandHandler('users', список_пользователей))
app.add_handler(CommandHandler('ban', бан))
app.add_handler(CommandHandler('unban', разбан))
app.add_handler(CommandHandler('delcargo', удалить_груз_админ))
app.add_handler(CommandHandler('delcar', удалить_машину_админ))
app.add_handler(CallbackQueryHandler(callback_handler))
print('Бот запущен!')
app.run_polling()
