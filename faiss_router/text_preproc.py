import pandas as pd
import os
import re
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from razdel import tokenize

from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
import gspread

#import gspread

# Загрузка ресурсов NLTK, если они еще не загружены
import nltk
nltk.download('stopwords')



def clean_text(text):
    text = re.sub(r'[^\w\s<>\(\)]', ' ', text)  # Сохраняем специальные токены и скобки
    text = re.sub(r'\d', ' ', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def remove_stopwords(text, lang='russian'):
    stop_words = set(stopwords.words(lang))
    # Сохранение специальных токенов
    words = [word if word.startswith('<') and word.endswith('>') else word for word in text.split() if word not in stop_words or (word.startswith('<') and word.endswith('>'))]
    return ' '.join(words)

def stem_text(text, lang='russian'):
    stemmer = SnowballStemmer(lang)
    # Применение стемминга, за исключением специальных токенов
    words = [stemmer.stem(word) if not (word.startswith('<') and word.endswith('>')) else word for word in text.split()]
    return ' '.join(words)

def tokenize_text(text):
    # Токенизация, сохраняя специальные токены без изменений
    tokens = [token.text for token in tokenize(text)]
    return ' '.join(tokens)

def preprocess_text_list(text_list):
    processed_list = []
    for text in text_list:
        text = highlight_patterns(text, '<PHONE>')
        text = highlight_patterns(text, '<ORDER_NUMBER>')    

        text = clean_text(text)

        
        text = highlight_patterns(text, '<HELLO>')
        text = highlight_patterns(text, '<DELIVERY>')  # Выделяем упоминания о доставке
        text = highlight_patterns(text, '<HOLIDAY_HOURS>')
        text = highlight_patterns(text, '<AVAILABILITY>')
        text = highlight_patterns(text, '<PROMOCODE>')
        text = highlight_patterns(text, '<ORDER_STATUS_CHANGE>')
        text = highlight_patterns(text, '<ORDER>')
        text = highlight_patterns(text, '<SELF_MEDICATION>')
        text = highlight_patterns(text, '<LOCATION>')
        text = highlight_patterns(text, '<USER_SERVICE>')
        

        #text = tokenize_text(text)
        #text = remove_stopwords(text)
        #text = stem_text(text)

        text = restore_tokens(text)
        text = move_tokens_to_start(text)
        text = text[:128]

        processed_list.append(text)

    processed_list = remove_hello_tokens(processed_list)
    return processed_list

def preprocess_texts_in_df(df, column_name='texts', new_column_name='processed_texts'):
    # Создаем новую колонку с обработанными текстами
    # Мы используем .explode() для преобразования каждого списка в отдельные строки
    # Затем применяем preprocess_single_text к каждой строке
    # Используем .groupby(level=0).agg(list) для объединения обработанных строк обратно в списки
    processed_texts = df[column_name].explode().apply(preprocess_single_text).groupby(level=0).agg(list)
    df[new_column_name] = processed_texts  # Сохраняем обработанные тексты в новой колонке
    df = add_token_column(df)
    return df

def preprocess_single_text(text):
    # Обработка одиночного текста
    return preprocess_text_list([text])[0]


# ========= ПОСТОБРАБОТКА ==========
def restore_tokens(text):
    # Шаблон для поиска токенов с пробелами внутри угловых скобок
    token_pattern = re.compile(r'<\s*([A-Za-z_]+)\s*>')
    
    # Функция для замены найденных токенов
    def replace_func(match):
        token = match.group(1).upper()  # Преобразование текста токена к верхнему регистру
        return f'<{token}>'  # Возвращаем токен без пробелов и в верхнем регистру
    
    # Применяем замену ко всем найденным токенам
    return token_pattern.sub(replace_func, text)

def move_tokens_to_start(text):
    # Найти все специальные токены
    tokens = re.findall(r'<[A-Z_]+>', text)
    # Удалить найденные токены из текста
    text_without_tokens = re.sub(r'<[A-Z_]+>', '', text)
    # Собрать текст, начиная с токенов, и добавить оставшийся текст
    #result_text = ' '.join(tokens) + ' ' + ' '.join(text_without_tokens.split())

    # Оставляем только токены и краткий текст
    result_text = ' '.join(tokens) + ' ' + ' '.join(text_without_tokens.split())[:100]
    return result_text.strip()

import re

def remove_hello_tokens(text_list):
    # Удаляем все вхождения '<HELLO>' из списка
    cleaned_list = [text.replace('<HELLO>', '') for text in text_list]
    """
    # Проверяем, состоят ли все строки в списке теперь только из пустых строк
    if all(text == '' for text in cleaned_list):
        # Если да, добавляем '<HELLO>' в начало списка
        cleaned_list[0] = '<HELLO>'
    """
    return cleaned_list





def add_token_column(df, column_name='processed_texts', new_column_name='tokens'):
    # Создаем новый столбец с токенами
    df[new_column_name] = df[column_name].apply(extract_tokens)
    return df

def extract_tokens(text_list):
    # Функция для извлечения токенов из списка текстов
    token_list = []
    for text in text_list:
        # Используем регулярное выражение для поиска токенов в угловых скобках
        tokens = re.findall(r'<\s*([A-Za-z_]+)\s*>', text)
        # Преобразуем токены к верхнему регистру и добавляем их в список
        token_list.extend([f'<{token.upper()}>' for token in tokens])
    return ', '.join(token_list)


#===========================
def highlight_patterns(text, token):
    for pattern in patterns[token]:
        text = re.sub(pattern, f' {token} ', text, flags=re.IGNORECASE)
    return text

def load_patterns():
    current_directory = os.getcwd()
    json_keyfile = 'E:\_MY\__DEV\_DEV_AI\__PROJECTS\HealthPlanet\gpt_health_planet\gpt_health_planet\AI_Status_Team\Albert_Toma\\2024-02-27\qna-project-415519-60fff000bbf6.json'
    spreadsheet_id = '1lb90koMF6y8J2lQWWqV0xnbwbo5iUMBwE7SY7JzXYHI'

    # Создаем объект авторизации
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(spreadsheet_id).worksheet('regexp')

    # Читаем данные из листа в DataFrame
    df = pd.DataFrame(sheet.get_all_records())

    # Создаем словарь из DataFrame
    result_dict = {}
    for key, value in df.groupby('token')['regexp']:
        if key:
            result_dict[key] = value.tolist()
    return result_dict






from faiss_router._patterns import patterns
# patterns = load_patterns()


# Пример использования
if __name__ == "__main__":
    data = {
        'texts': [
            ['Добрый день! Приветствую! Какие планы на восстановление пароля в этот праздничный день? Можно ли изменить заказ на новогодний костюм с применением промокода?', 'Еще один текст для обработки.'],
            ['Доброе утро! Можно ли заказать кофеиновые шоколадки с бесплатной доставкой к нам в офис?', 'Еще один текст для обработки.'],
            ['Добрый день.']
        ]
    }
    df = pd.DataFrame(data)
    df_processed = preprocess_texts_in_df(df)
    print(df_processed)
