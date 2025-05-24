import re
import random
import datetime
import webbrowser
import requests
import logging
import spacy
from spacy import displacy
from collections import defaultdict
from textblob import TextBlob
from googletrans import Translator


# Загрузка модели spaCy для обработки русского языка
nlp = spacy.load("ru_core_news_sm")

# Настройка логирования
logging.basicConfig(filename="chat_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# API-ключ OpenWeatherMap
API_KEY = "93a53a60f881396460ca8faa30decc9b"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

# Инициализация переводчика
translator = Translator()


def get_weather():
    params = {"q": "Нижний Новгород", "appid": API_KEY, "units": "metric", "lang": "ru"}
    response = requests.get(WEATHER_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"В Нижнем Новгороде сейчас {temp}°C, {description}."
    else:
        return "Не удалось получить данные о погоде. Попробуйте позже."


def search_google(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Открываю результаты поиска по запросу: {query}"


def analyze_text_structure(text):
    """Анализирует структуру текста с использованием spaCy"""
    doc = nlp(text)

    analysis = {
        'entities': [],
        'pos_tags': defaultdict(list),
        'syntax': [],
        'lemmas': []
    }

    # Извлекаем именованные сущности с типами
    analysis['entities'] = [(ent.text, ent.label_) for ent in doc.ents]

    # Анализ частей речи и синтаксиса
    for token in doc:
        analysis['pos_tags'][token.pos_].append(token.text)
        analysis['syntax'].append((token.text, token.dep_, token.head.text))
        analysis['lemmas'].append(token.lemma_)

    return analysis


def format_analysis(analysis):
    """Форматирует результаты анализа в читаемый вид"""
    result = []

    # Именованные сущности
    if analysis['entities']:
        entities_str = "\n- Сущности: " + ", ".join([f"{ent[0]} ({ent[1]})" for ent in analysis['entities']])
        result.append(entities_str)

    # Части речи
    pos_str = "\n- Части речи:"
    for pos, words in analysis['pos_tags'].items():
        pos_str += f"\n  {pos}: {', '.join(words)}"
    result.append(pos_str)

    # Синтаксические зависимости
    syntax_str = "\n- Синтаксис:"
    for dep in analysis['syntax']:
        syntax_str += f"\n  {dep[0]} ({dep[1]}) → {dep[2]}"
    result.append(syntax_str)

    # Леммы
    lemmas_str = "\n- Леммы: " + ", ".join(analysis['lemmas'])
    result.append(lemmas_str)

    return "".join(result)

def enhanced_analysis(text):
    """Улучшенный анализ текста с обработкой исключений"""
    try:
        analysis = analyze_text_structure(text)
        return "Результаты анализа:\n" + format_analysis(analysis)
    except Exception as e:
        logging.error(f"Ошибка анализа текста: {e}")
        return "Не удалось проанализировать текст"


def analyze_sentiment(text):
    try:
        # Переводим текст на английский
        translated = translator.translate(text, src='ru', dest='en').text

        # Анализируем тональность
        blob = TextBlob(translated)
        polarity = round(blob.sentiment.polarity, 2)  # Округляем до двух знаков

        sentiment_base = "Тональность сообщения: {}. Коэффициент: {}"

        if polarity > 0.1:
            return sentiment_base.format("позитивная 😊", polarity)
        elif polarity < -0.1:
            return sentiment_base.format("негативная 😞", polarity)
        else:
            return sentiment_base.format("нейтральная 😐", polarity)

    except Exception as e:
        logging.error(f"Ошибка анализа тональности: {e}")
        return "Не удалось определить тональность сообщения."


def extract_named_entities(text):
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents]
    if entities:
        return f"Вы упомянули следующие имена или места: {', '.join(entities)}."
    return "Я не нашел именованных сущностей в вашем сообщении."


patterns = {
    r'привет': lambda match=None: random.choice([
        "Привет!",
        "Здравствуйте!",
        "Приветствую, как ваши дела?",
        "Доброго времени суток!"
    ]),
    r'анализ (.+)': lambda match: enhanced_analysis(match.group(1)),
    r'сущности (.+)': lambda match: extract_named_entities(match.group(1)),
    r'структура (.+)': lambda match: format_analysis(analyze_text_structure(match.group(1))),
    r'как тебя зовут\??': lambda match=None: random.choice([
        "Меня зовут Бот!",
        "Я — ваш верный помощник, Бот.",
        "Я — просто Бот, а как вас зовут?"
    ]),
    r'как дела\??': lambda match=None: random.choice([
        "Отлично! Как у вас?",
        "Все замечательно, спасибо за интерес!",
        "Неплохо, а как ваши дела?",
        "Хорошо, спасибо за заботу!"
    ]),
    r'что ты умеешь\??': lambda match=None: random.choice([
        "Я могу отвечать на вопросы, искать информацию в интернете и показывать погоду!",
        "Я могу помочь вам с поиском и даже рассказать анекдот!",
        "Я умею много всего! Задавайте вопросы, и я помогу вам!"
    ]),
    r'где ты живешь\??': lambda match=None: random.choice([
        "Я живу в вашем компьютере!",
        "Я нахожусь прямо в вашем устройстве.",
        "Я — чисто виртуальный, не имею физического местоположения."
    ]),
    r'сколько времени': lambda match=None: f"Сейчас {datetime.datetime.now().strftime('%H:%M')}.",
    r'какая сегодня дата': lambda match=None: f"Сегодня {datetime.datetime.now().strftime('%d.%m.%Y')}.",
    r'погода': lambda match=None: get_weather(),
    r'поиск (.+)': lambda match: search_google(match.group(1)),
    r'тональность (.+)': lambda match: analyze_sentiment(match.group(1)),
    r'(\d+)\s*([+\-*/])\s*(\d+)': lambda match: str(eval(match.group(0))),
    r'расскажи анекдот': lambda match=None: random.choice([
        "Встречаются два программиста...\n— Как жизнь?\n— Компилируется.",
        "Почему программисты не боятся тёмного? Потому что у них всегда есть фонарик (flashlight).",
        "Как программисты учат детей? — Включают свет в комнате и говорят: 'Ну что, ребята, алгоритм реализован!'"
    ]),
    r'пока': lambda match=None: random.choice([
        "До свидания!",
        "Увидимся позже!",
        "Прощай, буду ждать вашего следующего вопроса!"
    ])
}

random_responses = [
    "Интересный вопрос!",
    "Я не совсем понял, попробуйте переформулировать.",
    "Извините, мне нужно немного подумать.",
    "Попробуйте задать что-то другое."
]


def chatbot():
    while True:
        user_input = input("Вы: ").lower().strip()
        logging.info(f"Пользователь: {user_input}")

        if user_input == "выход":
            print("Бот: До свидания!")
            logging.info("Бот: До свидания!")
            break

        for pattern, response in patterns.items():
            match = re.search(pattern, user_input)
            if match:
                reply = response(match) if match else response()
                print("Бот:", reply)
                logging.info(f"Бот: {reply}")
                break
        else:
            reply = random.choice(random_responses)
            print("Бот:", reply)
            logging.info(f"Бот: {reply}")


if __name__ == "__main__":
    chatbot()
