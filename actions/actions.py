from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import random
import datetime
import webbrowser
import requests
import spacy
from textblob import TextBlob
from googletrans import Translator
from collections import defaultdict
import sqlite3


nlp = spacy.load("ru_core_news_sm")
translator = Translator()
API_KEY = "93a53a60f881396460ca8faa30decc9b"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

class ActionRespondGreet(Action):
    def name(self) -> Text:
        return "action_respond_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        responses = [
            "Привет!",
            "Здравствуйте!",
            "Приветствую, как ваши дела?",
            "Доброго времени суток!"
        ]
        dispatcher.utter_message(text=random.choice(responses))
        return []

class ActionRespondAskName(Action):
    def name(self) -> Text:
        return "respond_ask_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        responses = [
            "Меня зовут Бот!",
            "Я — ваш помощник, Бот."
        ]
        dispatcher.utter_message(text=random.choice(responses))
        return []

class ActionRespondGoodbye(Action):
    def name(self) -> Text:
        return "action_respond_goodbye"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        responses = [
            "До свидания!",
            "Увидимся позже!",
            "Прощай, буду ждать вашего следующего вопроса!"
        ]
        dispatcher.utter_message(text=random.choice(responses))
        return []

class ActionShowTime(Action):
    def name(self) -> Text:
        return "action_show_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_time = datetime.datetime.now().strftime("%H:%M")
        dispatcher.utter_message(text=f"Сейчас {current_time}.")
        return []

class ActionShowDate(Action):
    def name(self) -> Text:
        return "action_show_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        dispatcher.utter_message(text=f"Сегодня {current_date}.")
        return []

class ActionGetWeather(Action):
    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        params = {
            "q": "Нижний Новгород",
            "appid": API_KEY,
            "units": "metric",
            "lang": "ru"
        }
        try:
            response = requests.get(WEATHER_URL, params=params)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                description = data["weather"][0]["description"]
                dispatcher.utter_message(
                    text=f"В Нижнем Новгороде сейчас {temp}°C, {description}.")
            else:
                dispatcher.utter_message(
                    text="Не удалось получить данные о погоде. Попробуйте позже.")
        except Exception as e:
            dispatcher.utter_message(text="Ошибка при получении погоды.")
        return []

class ActionGoogleSearch(Action):
    def name(self) -> Text:
        return "action_google_search"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Получаем query из сущности или всего сообщения
        query = next(tracker.get_latest_entity_values("query"), None) or " ".join(
            tracker.latest_message["text"].split()[1:])

        if not query:
            dispatcher.utter_message(text="Пожалуйста, укажите запрос для поиска.")
            return []

        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        dispatcher.utter_message(text=f"Открываю результаты по запросу: {query}")
        return []

class ActionAnalyzeText(Action):
    def name(self) -> Text:
        return "action_analyze_text"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        text = next(tracker.get_latest_entity_values("text"), None)
        if text:
            try:
                doc = nlp(text)
                analysis = {
                    'entities': [(ent.text, ent.label_) for ent in doc.ents],
                    'pos_tags': defaultdict(list),
                    'syntax': [],
                    'lemmas': []
                }

                for token in doc:
                    analysis['pos_tags'][token.pos_].append(token.text)
                    analysis['syntax'].append(
                        (token.text, token.dep_, token.head.text)
                    )
                    analysis['lemmas'].append(token.lemma_)

                response = "Результаты анализа:\n"
                if analysis['entities']:
                    entities_str = ", ".join(
                        [f"{ent[0]} ({ent[1]})" for ent in analysis['entities']]
                    )
                    response += f"Сущности: {entities_str}\n"

                for pos, words in analysis['pos_tags'].items():
                    response += f"{pos}: {', '.join(words)}\n"

                response += f"Леммы: {', '.join(analysis['lemmas'])}"

                dispatcher.utter_message(text=response)
            except Exception as e:
                dispatcher.utter_message(text="Ошибка при анализе текста.")
        else:
            dispatcher.utter_message(text="Пожалуйста, предоставьте текст для анализа.")
        return []

class ActionSentimentAnalysis(Action):
    def name(self) -> Text:
        return "action_sentiment_analysis"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Используем последнее сообщение, если сущность не извлечена
        text = next(tracker.get_latest_entity_values("text"), None) or tracker.latest_message.get("text")

        if not text:
            dispatcher.utter_message(text="Пожалуйста, укажите текст для анализа.")
            return []

        try:
            # Анализ тональности
            translated = translator.translate(text, src='ru', dest='en').text
            blob = TextBlob(translated)
            polarity = round(blob.sentiment.polarity, 2)

            # Определение тональности
            if polarity > 0.1:
                sentiment = "позитивная 😊"
            elif polarity < -0.1:
                sentiment = "негативная 😞"
            else:
                sentiment = "нейтральная 😐"

            dispatcher.utter_message(text=f"Тональность сообщения: {sentiment}. Коэффициент: {polarity}")

        except Exception as e:
            dispatcher.utter_message(text="Ошибка при анализе тональности.")

        return []

class ActionTellJoke(Action):
    def name(self) -> Text:
        return "action_tell_joke"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        jokes = [
            "Встречаются два программиста...\n— Как жизнь?\n— Компилируется.",
            "Почему программисты не боятся тёмного? Потому что у них всегда есть фонарик (flashlight).",
            "Как программисты учат детей? — Включают свет в комнате и говорят: 'Ну что, ребята, алгоритм реализован!'"
        ]
        dispatcher.utter_message(text=random.choice(jokes))
        return []

class ActionHandleMath(Action):
    def name(self) -> Text:
        return "action_handle_math"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get('text')
        try:
            result = eval(message)
            dispatcher.utter_message(text=f"Результат: {result}")
        except:
            dispatcher.utter_message(text="Не могу вычислить это выражение")
        return []


class ActionSaveUserData(Action):
    def name(self) -> Text:
        return "action_save_user_data"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        user_id = tracker.sender_id
        entities = tracker.latest_message.get("entities", [])
        name = tracker.get_slot("user_name")
        city = tracker.get_slot("user_city")
        try:
            conn = sqlite3.connect('user_data.db')
            cursor = conn.cursor()

            cursor.execute(''' INSERT OR REPLACE INTO users (user_id, name, city) VALUES (?, ?, ?) ''', (user_id, name, city))

            conn.commit()
            dispatcher.utter_message("Данные сохранены!")

        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            dispatcher.utter_message("Ошибка базы данных.")

        finally:
            if conn:
                conn.close()

        return []
