import openai
#from config import route_form, system, user_footer
import requests
import os
from datetime import datetime
import pytz

# Создаём объект временного пояса для Москвы
moscow_tz = pytz.timezone('Europe/Moscow')


class OpenAIRouter():
    def __init__(self):
        self.DOC_URL = os.environ.get("DOC_URL")
        moscow_time = datetime.now(moscow_tz)
        self.prompts = {
            '0': {
                'url': self.DOC_URL,
                'system': '',
                'user_footer': '',
                'route_form': '',
                'last_update': moscow_time.strftime('%Y-%m-%d <b>%H:%M:%S</b>')
            }
        }
        # self.reload_prompts(self, self.DOC_URL, 0)

    async def get_route(self, question: str, user_id):
        user_prompts = self.prompts.get(user_id)
        if user_prompts is None:
            user_prompts = self.prompts.get(0)

        user = f"Вопрос пользователя: {question}\nФорма_000: {user_prompts['route_form']}\n{user_prompts['user_footer']}"
        messages = [
            {"role": "system", "content": user_prompts['system']},
            {"role": "user", "content": user}
        ]
        completion = openai.ChatCompletion.create(model='gpt-3.5-turbo-16k', messages=messages, temperature=0)
        answer = completion.choices[0].message.content
        
        # Возможная постобработка ответа
        processed_answer = self.process_answer(answer)
        
        print(question, processed_answer)
        return processed_answer

    def process_answer(self, answer):
        # Здесь может быть реализована логика для анализа и выбора наиболее подходящей категории
        # Это может включать в себя анализ "score" или других параметров для определения релевантности
        return answer  # Пока возвращает оригинальный ответ без изменений

    def reload_prompts(self, user_id):
        prompt = self.prompts.get(user_id)
        if prompt is not None:
            return self.load_prompts(prompt['url'], user_id)
        else:
            return [f"❌ Не могу найти ссылку на промпт"]

    def load_prompts(self, export_url, user_id):
        if "/edit" in export_url:
            index_of_edit = export_url.find("/edit") + len("/edit")
            load_url = export_url[:index_of_edit]
            load_url = load_url.replace("/edit", "/export?format=txt")
        else:
            print("URL не содержит '/edit'")

        response = requests.get(load_url)
        # Проверяем, успешно ли выполнен запрос
        if response.status_code == 200:
            document_text = response.text
            #print(document_text)
            prompts = load_markdown_to_dict(document_text)
            if all(key in prompts for key in ['system', 'user_footer', 'route_form']):
                moscow_time = datetime.now(moscow_tz)
                prompts['last_update'] = moscow_time.strftime('%Y-%m-%d <b>%H:%M:%S</b>')
                prompts['url'] = export_url
                self.prompts[user_id] = prompts
                return ["✅ Промпты и форма_000 успешно загружены", True]
            else:
                print(prompts)
                return ["❌ Ошибга при парсинге промптов", False]
        else:
            return ["❌ Ошибка при получении документа", False]


def load_markdown_to_dict(markdown_text):
    # Разбиение текста по заголовкам
    sections = markdown_text.split('## ')[1:]  # Игнорируем часть перед первым заголовком

    # Словарь для результатов
    result_dict = {}

    for section in sections:
        if section.strip():  # Игнорируем пустые секции
            title, *content = section.split('\n', 1)
            key = title.strip()
            text = content[0].strip() if content else ''  # Обрабатываем случай без текста
            result_dict[key] = text

    return result_dict

