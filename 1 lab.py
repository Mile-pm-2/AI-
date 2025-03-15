import re
import random
import datetime

# Словарь шаблонов и ответов
patterns = {
    r'привет': "Добрый день!",
    r'как тебя зовут\??': "Меня зовут Бот!",
    r'сколько времени': lambda: f"Сейчас {datetime.datetime.now().strftime('%H:%M')}",
    r'какая сегодня дата': lambda: f"Сегодня {datetime.datetime.now().strftime('%d.%m.%Y')}",
    r'какая погода': "Я не синоптик, но могу посмотреть прогноз!",
    r'(\d+)\s*([+\-*/])\s*(\d+)': lambda match: str(eval(match.group(0))),
    r'как дела\??': "У меня всё отлично! Спасибо, что спросил.",
    r'расскажи анекдот': lambda: random.choice([
        "Встречаются два программиста...\n— Как жизнь?\n— Компилируется.",
        "Почему программисты не боятся тёмного?\nПотому что у них всегда есть фонарик (flashlight)."
    ]),
    r'что ты умеешь\??': "Я умею отвечать на вопросы, считать и рассказывать анекдоты!",
    r'где ты живешь\??': "Я живу в твоем компьютере, так что лучше меня не злить :)",
    r'выход': "До свидания!"
}

random_responses = [
    "Интересный вопрос!",
    "Я не уверен, что понял вас.",
    "Может, спросите что-то другое?",
    "Попробуйте переформулировать!"
]

def chatbot():
    while True:
        user_input = input("Вы: ").lower().strip()

        if user_input == "выход":
            print("Бот: До свидания!")
            break

        for pattern, response in patterns.items():
            match = re.search(pattern, user_input)
            if match:
                if callable(response):
                    print("Бот:", response(match) if match.groups() else response())
                else:
                    print("Бот:", response)
                break
        else:
            print("Бот:", random.choice(random_responses))

if __name__ == "__main__":
    chatbot()