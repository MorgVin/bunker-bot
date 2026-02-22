import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ────────────────────────────────────────────────
# НАСТРОЙКИ
# ────────────────────────────────────────────────

TOKEN = '8350952541:AAEJ2DtxbvIfGxin9NaR65lMANBxNlnm_1U'
HOST_CHAT_ID = 6208445194
SITE_URL = 'https://bunker-gg7v.onrender.com/api/open_card'  # ← ОБЯЗАТЕЛЬНО замени на свой реальный адрес от Render!
REQUEST_TIMEOUT = 60  # увеличенный таймаут для Render Free (просыпается медленно)

MIN_PLAYERS_TO_FINISH = 3

# ────────────────────────────────────────────────
# СПИСКИ КАРТ (твои полные списки)
# ────────────────────────────────────────────────
GENDERS_AGES = [
    'Мужчина, 19 лет', 'Женщина, 22 года', 'Мужчина, 28 лет', 'Женщина, 31 год',
    'Мужчина, 34 года', 'Женщина, 37 лет', 'Мужчина, 42 года', 'Женщина, 45 лет',
    'Мужчина, 49 лет', 'Женщина, 52 года', 'Мужчина, 57 лет', 'Женщина, 61 год',
    'Мужчина, 24 года', 'Женщина, 27 лет', 'Мужчина, 33 года', 'Женщина, 29 лет',
    'Мужчина, 38 лет', 'Женщина, 41 год', 'Мужчина, 46 лет', 'Женщина, 50 лет',
    'Подросток, мальчик 16 лет', 'Девушка, 17 лет', 'Мужчина, 65+ лет', 'Женщина, 68 лет'
]

PROFESSIONS = [
    'Врач-терапевт', 'Хирург', 'Медсестра', 'Фельдшер',
    'Инженер-строитель', 'Электрик', 'Сварщик', 'Слесарь',
    'Агроном', 'Тракторист', 'Ветеринар', 'Фермер',
    'Программист', 'Системный администратор', 'Хакер-этик', 'Тестировщик ПО',
    'Учитель физики', 'Преподаватель биологии', 'Историк', 'Психолог',
    'Повар', 'Кондитер', 'Пекарь', 'Бармен',
    'Полицейский', 'Следователь', 'Охранник', 'Военный в отставке',
    'Автомеханик', 'Сантехник', 'Плотник', 'Кровельщик',
    'Биолог', 'Химик', 'Геолог', 'Метеоролог',
    'Журналист', 'Фотограф', 'Оператор', 'Режиссёр монтажа'
]

HEALTHS = [
    'Полностью здоров', 'Отличное зрение и слух',
    'Лёгкая близорукость (-2)', 'Дальнозоркость',
    'Астма (лёгкая форма)', 'Аллергический ринит',
    'Хронический бронхит', 'Гипертония 1 степени',
    'Сахарный диабет 2 типа (компенсирован)', 'Гастрит',
    'Язва желудка в ремиссии', 'Холецистит',
    'Проблемы с позвоночником (сколиоз)', 'Артрит коленного сустава',
    'Варикоз', 'Геморрой',
    'Бесплодие', 'Перенесённый гепатит А',
    'Удалён аппендикс', 'Удалена желчный пузырь',
    'Один глаз видит плохо', 'Глухота на одно ухо',
    'Заикание (лёгкое)', 'Тремор рук',
    'ПТСР (лёгкая форма)', 'Социофобия',
    'Никотиновая зависимость', 'Бывший алкоголик (5 лет трезвости)'
]

BAGGAGES = [
    'Аптечка с антибиотиками и обезболивающими', 'Инсулин и глюкометр (на 3 месяца)',
    'Набор хирургических инструментов', 'Противогаз + 5 фильтров',
    'Дробовик + 40 патронов', 'Пистолет Макарова + 3 магазина',
    'Арбалет + 25 болтов', 'Мачете и топор',
    'Набор семян овощей и зерновых (50 видов)', 'Мешок картофеля (30 кг)',
    'Сухой паёк на 60 дней', 'Вакуумная упаковка круп и бобовых (40 кг)',
    'Солнечная панель 200 Вт + аккумулятор', 'Ручной генератор + power bank',
    'Набор инструментов (мультитул, отвёртки, ключи)', 'Сварочный аппарат инвертор + электроды',
    'Набор книг по выживанию и медицине', 'Энциклопедия растений и грибов',
    'Радиостанция с дальностью 50 км', 'Набор раций (3 шт.)',
    'Палатка на 4 человека', 'Спальные мешки (3 шт.)',
    'Фильтр для воды + таблетки для обеззараживания', 'Большой запас йода и марганцовки'
]

HOBBIES = [
    'Выживание в дикой природе', 'Охота и следопытство',
    'Рыбалка и плетение сетей', 'Садоводство и огородничество',
    'Консервирование и заготовки', 'Кулинария из подручных средств',
    'Ремонт и восстановление техники', 'Сварка и работа с металлом',
    'Столярное дело', 'Шитьё и ремонт одежды',
    'Первая помощь и народная медицина', 'Массаж и мануальная терапия',
    'Программирование и электроника', 'Радиодело и антенны',
    'Самооборона и рукопашный бой', 'Стрельба из огнестрельного оружия',
    'Ориентирование и картография', 'Альпинизм и скалолазание',
    'Изготовление самодельного оружия', 'Химия и создание веществ',
    'Рисование и черчение', 'Музыка (игра на гитаре)',
    'Психология и манипуляция людьми', 'Языки (английский + немецкий)'
]

SECRETS = [
    'Сидел 4 года за кражу', 'Осуждён условно за драку',
    'Был наёмником в горячей точке', 'Служил в спецназе',
    'Убегал от кредиторов', 'Поддельные документы',
    'Скрывает, что болен ВИЧ', 'Перенёс операцию по смене пола',
    'Имеет вторую семью в другом городе', 'Раньше работал в полиции и уволен по статье',
    'Украл крупную сумму у предыдущей работы', 'Свидетель в программе защиты',
    'Фобия замкнутых пространств', 'Боязнь крови',
    'Скрытый алкоголизм', 'Наркотическая зависимость в прошлом',
    'Умеет взламывать замки и сейфы', 'Мастер по изготовлению взрывчатки',
    'Знает, где спрятан склад оружия', 'Был в религиозной секте',
    'Имеет талант к актёрству и перевоплощению', 'Отлично врёт под давлением',
    'Тайно ненавидит детей', 'Панические атаки при стрессе'
]

CATASTROPHES = [
    'Ядерная война: высокий уровень радиации, разрушенная инфраструктура, дефицит пищи и воды.',
    'Пандемия смертельного вируса: высокая заразность, нужны медики и антибиотики, иммунитет критичен.',
    'Зомби-апокалипсис: орды нежити, нужны оружие и навыки выживания, здоровье важно.',
    'Глобальное потепление и наводнения: затопленные земли, нужны инженеры и фермеры.',
    'Падение астероида: пыль в атмосфере, холод, дефицит света — нужны семена и садоводство.',
    'Инопланетное вторжение: враждебные пришельцы, нужны военные и технологии.',
    'Супервулкан: пепел в небе, ядерная зима, нужны запасы еды и тепла.',
    'Кибератака: отключение электричества, нужны программисты и генераторы.',
    'Химическая катастрофа: токсичные облака, нужны противогазы и химики.',
    'Землетрясения и цунами: разрушенные города, нужны строители и медики.',
    'Магнитный сдвиг полюсов: хаос в навигации, радиация, нужны ученые.',
    'Биологическая война: мутировавшие организмы, нужны биологи и вакцины.'
]

# ────────────────────────────────────────────────
# СОСТОЯНИЕ
# ────────────────────────────────────────────────

players = {}
player_statuses = {}
generated_profiles = {}
current_catastrophe = None
game_active = True
cards_dealt = False  # флаг: раздача уже была?

# ────────────────────────────────────────────────
# ФУНКЦИИ ОЦЕНКИ (без изменений)
# ────────────────────────────────────────────────

def get_profession_score(prof: str) -> int:
    high = ['Врач', 'Хирург', 'Медсестра', 'Фельдшер', 'Агроном', 'Ветеринар', 'Военный', 'Полицейский', 'Инженер', 'Сварщик', 'Автомеханик']
    med  = ['Программист', 'Биолог', 'Химик', 'Повар', 'Слесарь', 'Плотник']
    low  = ['Журналист', 'Фотограф', 'Режиссёр', 'Бармен', 'Историк']
    if any(h in prof for h in high): return 22
    if any(m in prof for m in med):  return 18
    if any(l in prof for l in low):  return 12
    return 15

def get_health_score(health: str) -> int:
    if 'здоров' in health or 'зрение' in health: return 25
    if 'лёгкая' in health or 'удалён' in health: return 18
    if 'астма' in health or 'гипертония' in health: return 15
    if 'диабет' in health or 'гепатит' in health: return 10
    if 'бесплодие' in health or 'ВИЧ' in health or 'рак' in health: return 5
    return 12

def get_baggage_score(bag: str) -> int:
    if 'оружие' in bag or 'аптечка' in bag or 'семена' in bag or 'инструменты' in bag: return 14
    if 'панель' in bag or 'генератор' in bag or 'книги' in bag: return 12
    if 'паёк' in bag or 'палатка' in bag: return 8
    return 10

def get_hobby_score(hobby: str) -> int:
    high = ['Выживание', 'Охота', 'Рыбалка', 'Садоводство', 'Медицина', 'Ремонт', 'Сварка', 'Столярное', 'Самооборона']
    med  = ['Консервирование', 'Кулинария', 'Первая помощь', 'Программирование', 'Радиодело', 'Языки']
    if any(h in hobby for h in high): return 18
    if any(m in hobby for m in med):  return 14
    return 8

def get_age_score(age_str: str) -> int:
    try:
        age_part = age_str.split(',')[-1].strip()
        if '+' in age_part:
            age = 65
        else:
            age = int(''.join(filter(str.isdigit, age_part)))
        if 18 <= age <= 45: return 10
        if 46 <= age <= 60: return 7
        if age < 18 or age > 60: return 4
    except:
        pass
    return 7

def get_secret_score(secret: str) -> int:
    positive = ['знает', 'служил', 'умеет', 'талант', 'спецназ', 'военный']
    negative = ['сидел', 'убегал', 'скрывает', 'фобия', 'алкоголизм', 'наркотическая', 'ненавидит', 'панические']
    if any(p.lower() in secret.lower() for p in positive): return 8
    if any(n.lower() in secret.lower() for n in negative): return -6
    return 0

def calculate_survival_chance(gender_age, profession, health, baggage, hobby, secret) -> tuple:
    score = (
        get_profession_score(profession) +
        get_health_score(health) +
        get_baggage_score(baggage) +
        get_hobby_score(hobby) +
        get_age_score(gender_age) +
        get_secret_score(secret)
    )
    score = max(0, min(100, score))
    if score >= 85: desc = "очень высокий"
    elif score >= 70: desc = "высокий"
    elif score >= 50: desc = "средний"
    elif score >= 30: desc = "низкий"
    else: desc = "критически низкий"
    return score, desc

# ────────────────────────────────────────────────
# КОМАНДЫ
# ────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global game_active

    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name

    if not game_active:
        await update.message.reply_text("Игра завершена. Регистрация закрыта.")
        return

    if user_id not in players:
        players[user_id] = username
        player_statuses[user_id] = 'active'

        count = len([u for u, s in player_statuses.items() if s == 'active'])

        await update.message.reply_text(
            f"Привет, {username}!\n"
            f"Ты зарегистрирован (номер {count}).\n"
            f"Ждём ведущего."
        )

        await context.bot.send_message(
            chat_id=HOST_CHAT_ID,
            text=f"➕ Новый игрок: @{username}\nАктивных: {count}"
        )

        if count >= MIN_PLAYERS_TO_FINISH:
            await context.bot.send_message(
                chat_id=HOST_CHAT_ID,
                text=f"Набрано {count} человек. Завершить? /finish"
            )

    else:
        await update.message.reply_text(f"Ты уже зарегистрирован.")

async def deal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != HOST_CHAT_ID:
        await update.message.reply_text("Только ведущий.")
        return

    if not players:
        await update.message.reply_text("Никто не зарегистрировался.")
        return

    await update.message.reply_text("Раздаю карты...")

    global generated_profiles, current_catastrophe, cards_dealt
    generated_profiles = {}
    current_catastrophe = random.choice(CATASTROPHES)
    cards_dealt = True  # после раздачи ведущий фиксируется

    # Инициализация карточек на сайте
    for player_id, username in players.items():
        init_data = {
            "player_id": str(player_id),
            "username": username,
            "action": "init"
        }
        try:
            r = requests.post(SITE_URL, json=init_data, timeout=REQUEST_TIMEOUT)
            print(f"Инициализация {username}: статус {r.status_code}")
        except Exception as e:
            print(f"Ошибка инициализации {username}: {e}")

    # Генерация и отправка профилей
    for player_id, username in players.items():
        gender_age = random.choice(GENDERS_AGES)
        profession = random.choice(PROFESSIONS)
        health     = random.choice(HEALTHS)
        baggage    = random.choice(BAGGAGES)
        hobby      = random.choice(HOBBIES)
        secret     = random.choice(SECRETS)

        chance, desc = calculate_survival_chance(gender_age, profession, health, baggage, hobby, secret)

        profile_text = (
            f"🧑‍🚀 Твоя карточка ({username})\n\n"
            f"Пол / Возраст: {gender_age}\n"
            f"Профессия:     {profession}\n"
            f"Здоровье:      {health}\n"
            f"Багаж:         {baggage}\n"
            f"Хобби / Навык: {hobby}\n"
            f"Секрет:        {secret}\n\n"
            f"**Шанс выживания: {chance}% ({desc})**"
        )

        generated_profiles[player_id] = profile_text

        try:
            await context.bot.send_message(player_id, profile_text, parse_mode='Markdown')
        except:
            await context.bot.send_message(HOST_CHAT_ID, f"⚠️ Не отправлен профиль {username}")

    await context.bot.send_message(
        HOST_CHAT_ID,
        f"Раздача завершена ✓\n**Катастрофа:** {current_catastrophe}\nВсего профилей: {len(players)}"
    )

# ────────────────────────────────────────────────
# СТАТЬ ВЕДУЩИМ
# ────────────────────────────────────────────────

async def become_host(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global HOST_CHAT_ID

    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    if user_id == HOST_CHAT_ID:
        await update.message.reply_text("Ты уже ведущий.")
        return

    if user_id not in players:
        await update.message.reply_text("Сначала зарегистрируйся: /start")
        return

    # Ограничение: стать ведущим можно только до раздачи карт
    global cards_dealt
    if cards_dealt:
        await update.message.reply_text("Роль ведущего фиксируется после раздачи карт (/deal).")
        return

    old_host = HOST_CHAT_ID
    old_username = players.get(old_host, "неизвестный")

    HOST_CHAT_ID = user_id

    msg = (
        f"🔥 Новый ведущий!\n"
        f"@{username} (ID {user_id}) захватил роль ведущего\n"
        f"Предыдущий ведущий: @{old_username} (ID {old_host})\n\n"
        f"Теперь только ты можешь управлять игрой: /deal, /kick, /finish и т.д."
    )

    await update.message.reply_text(msg)

    # Личка новому ведущему
    try:
        await context.bot.send_message(
            user_id,
            f"Ты теперь ведущий!\n"
            f"Команды: /deal, /kick <id>, /unban <id>, /list, /finish, /reset\n"
            f"Удачи вести игру! 😎"
        )
    except:
        pass

# ────────────────────────────────────────────────
# ОСТАЛЬНЫЕ КОМАНДЫ (без изменений)
# ────────────────────────────────────────────────

async def open_category(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str, label: str) -> None:
    user_id = update.effective_user.id

    if user_id not in players:
        await update.message.reply_text("Ты не в игре. Напиши /start")
        return

    if user_id not in generated_profiles:
        await update.message.reply_text("Карточка ещё не сгенерирована. Жди /deal")
        return

    profile_text = generated_profiles[user_id]
    lines = profile_text.split("\n")

    value = "Не найдено"
    for line in lines:
        if label in line:
            value = line.split(": ", 1)[1] if ": " in line else line.strip()
            break

    await update.message.reply_text(f"{label}: {value}")
    await context.bot.send_message(HOST_CHAT_ID, f"@{players[user_id]} открыл(а) {label}")

    card_data = {
        "player_id": str(user_id),
        "username": players[user_id],
        "category": key,
        "label": label,
        "value": value
    }

    try:
        r = requests.post(SITE_URL, json=card_data, timeout=REQUEST_TIMEOUT)
        print(f"Отправка {label} для {players[user_id]}: статус {r.status_code}")
    except Exception as e:
        print(f"Ошибка отправки на сайт: {e}")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != HOST_CHAT_ID:
        await update.message.reply_text("Только ведущий.")
        return

    if not context.args:
        await update.message.reply_text("Пример: /kick 123456789")
        return

    try:
        target_id = int(context.args[0])
        if target_id not in players:
            await update.message.reply_text("Игрок не найден.")
            return

        player_statuses[target_id] = 'eliminated'
        username = players[target_id]

        try:
            await context.bot.send_message(
                target_id,
                "❌ Ты был выгнан из бункера.\nВедущий исключил тебя из игры.\nСпасибо за участие!"
            )
        except:
            await context.bot.send_message(HOST_CHAT_ID, f"Не удалось уведомить {username} (id {target_id})")

        await update.message.reply_text(f"{username} выгнан.")
    except ValueError:
        await update.message.reply_text("ID должен быть числом.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != HOST_CHAT_ID:
        await update.message.reply_text("Только ведущий.")
        return

    if not context.args:
        await update.message.reply_text("Пример: /unban 123456789")
        return

    try:
        target_id = int(context.args[0])
        if target_id not in players:
            await update.message.reply_text("Игрок не найден.")
            return

        player_statuses[target_id] = 'active'
        username = players[target_id]

        try:
            await context.bot.send_message(
                target_id,
                "✅ Ты возвращён в игру!\nВедущий передумал."
            )
        except:
            pass

        await update.message.reply_text(f"{username} возвращён.")
    except ValueError:
        await update.message.reply_text("ID должен быть числом.")

async def list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != HOST_CHAT_ID:
        await update.message.reply_text("Только ведущий.")
        return

    if not players:
        await update.message.reply_text("Список пуст.")
        return

    text = "Игроки:\n"
    for pid, uname in players.items():
        st = player_statuses.get(pid, 'active')
        text += f"• {pid} | @{uname} | {st.upper()}\n"
    await update.message.reply_text(text)

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != HOST_CHAT_ID:
        await update.message.reply_text("Только ведущий может завершить игру.")
        return

    global game_active
    if not game_active:
        await update.message.reply_text("Игра уже завершена.")
        return

    active_count = len([u for u, s in player_statuses.items() if s == 'active'])

    if active_count < MIN_PLAYERS_TO_FINISH:
        await update.message.reply_text(f"Ещё мало игроков ({active_count} < {MIN_PLAYERS_TO_FINISH}).")
        return

    game_active = False

    survivors = []
    for pid, status in player_statuses.items():
        if status == 'active':
            username = players.get(pid, "???")
            chance_text = ""
            if pid in generated_profiles:
                lines = generated_profiles[pid].split("\n")
                chance_line = [l for l in lines if "Шанс выживания:" in l]
                chance_text = chance_line[0] if chance_line else ""
            survivors.append(f"• @{username} {chance_text}")

    message = (
        "🏁 ИГРА ЗАВЕРШЕНА!\n\n"
        f"В бункер прошли:\n" + "\n".join(survivors) + "\n\n"
        "Спасибо за игру!"
    )

    await context.bot.send_message(HOST_CHAT_ID, message)

    for pid in players:
        if player_statuses.get(pid) == 'active':
            try:
                await context.bot.send_message(pid, message)
            except:
                pass

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != HOST_CHAT_ID:
        await update.message.reply_text("Только ведущий.")
        return

    global game_active, cards_dealt
    players.clear()
    player_statuses.clear()
    generated_profiles.clear()
    current_catastrophe = None
    game_active = True
    cards_dealt = False
    await update.message.reply_text("Игра полностью сброшена. Новый ведущий может быть выбран командой /host.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != HOST_CHAT_ID:
        await update.message.reply_text("Только ведущий.")
        return

    text = (
        "Команды:\n"
        "/start — регистрация\n"
        "/deal — раздать карты\n"
        "/host — стать ведущим (до раздачи)\n"
        "/gender — открыть Пол/Возраст\n"
        "/profession — открыть Профессию\n"
        "/health — открыть Здоровье\n"
        "/baggage — открыть Багаж\n"
        "/hobby — открыть Хобби\n"
        "/secret — открыть Секрет\n"
        "/chance — открыть Шанс\n"
        "/kick <id> — выгнать\n"
        "/unban <id> — вернуть\n"
        "/list — список\n"
        "/finish — завершить\n"
        "/reset — сброс\n"
        "/help — справка"
    )
    await update.message.reply_text(text)

# ────────────────────────────────────────────────
# ОДНОСЛОВНЫЕ КАТЕГОРИИ (baggage, health и т.д.)
# ────────────────────────────────────────────────

async def open_by_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip().lower()

    mapping = {
        'gender': ("gender_age", "Пол / Возраст"),
        'profession': ("profession", "Профессия"),
        'health': ("health", "Здоровье"),
        'baggage': ("baggage", "Багаж"),
        'hobby': ("hobby", "Хобби / Навык"),
        'secret': ("secret", "Секрет"),
        'chance': ("chance", "Шанс выживания")
    }

    if text in mapping:
        key, label = mapping[text]
        await open_category(update, context, key, label)

# ────────────────────────────────────────────────
# ЗАПУСК
# ────────────────────────────────────────────────

def main():
    application = Application.builder().token(TOKEN).build()

    # Команды с /
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("deal", deal))
    application.add_handler(CommandHandler("kick", kick))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("list", list))
    application.add_handler(CommandHandler("finish", finish))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("host", become_host))

    # Однословные категории без слеша
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, open_by_word))

    print("Бот запущен...")
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()