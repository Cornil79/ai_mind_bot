import openai
#from config import route_form, system, user_footer
import requests


class OpenAIRouter():
    def __init__(self):
        self.prompts = {
            'system': '',
            'user_footer': '',
        }

    async def get_route(self, question: str):
        user = f"Вопрос пользователя: {question}\nФорма_000: {self.prompts['route_form']}\n{self.prompts['user_footer']}"
        messages = [
            {"role": "system", "content": self.prompts['system']},
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

    def reload_prompts(self, export_url):
        export_url = export_url.replace("/edit", "/export?format=txt")
        response = requests.get(export_url)
        # Проверяем, успешно ли выполнен запрос
        if response.status_code == 200:
            document_text = response.text
            #print(document_text)
            prompts = load_markdown_to_dict(document_text)
            if all(key in prompts for key in ['system', 'user_footer', 'route_form']):
                self.prompts = prompts
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

