import re
import random
import datetime
import webbrowser
import requests
import logging

# Настройка логирования
logging.basicConfig(filename="chat_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# API-ключ OpenWeatherMap (замените на свой)
API_KEY = "93a53a60f881396460ca8faa30decc9b"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

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

# Словарь шаблонов и ответов с добавлением разнообразия
patterns = {
    r'привет': lambda match=None: random.choice([
        "Привет!",
        "Здравствуйте!",
        "Приветствую, как ваши дела?",
        "Доброго времени суток!"
    ]),
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
