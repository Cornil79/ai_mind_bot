def colorful_bar(length):
    red = '\033[91m'  # код цвета для красного
    yellow = '\033[93m'  # код цвета для желтого
    green = '\033[92m'  # код цвета для зеленого
    reset_color = '\033[0m'  # сброс цвета

    bar = ''  # строка для хранения бара

    for i in range(length, 0, -1):
        if i <= 3:
            bar += red + '*'  # добавляем красную звездочку
        elif 4 <= i <= 7:
            bar += yellow + '*'  # добавляем желтую звездочку
        else:
            bar += green + '*'  # добавляем зеленую звездочку
    return ' ' * (10 - length) + bar + reset_color  # добавляем пробелы слева от бара и возвращаем строку бара с сбросом цвета


import ast

# Функция для извлечения значений для ключа 0 и возвращения их как строки
def extract_questions(replies_str):
    try:
        # Преобразуем строку в список словарей
        replies_list = ast.literal_eval(replies_str)
        # Извлекаем значения для ключа 0
        values_with_key_zero = [reply[0] for reply in replies_list if 0 in reply]
        # Возвращаем значения объединенными в одну строку, если их несколько, или единственное значение
        if len(values_with_key_zero) > 0:
            return values_with_key_zero  # Возвращаем значение
        else:
            return None  # Возвращаем None, если нет значений
    except Exception as e:
        print(f"Error processing row: {e}")  # Для отладки
        return None


import numpy as np
import matplotlib.pyplot as plt
def chunks_diagram(df_texts, df_preproc):
    # "Выпрямляем" список списков строк в один список строк для исходных текстов
    flat_texts_original = [item for sublist in df_texts.tolist() for item in sublist]

    # Аналогично для обработанных текстов
    flat_texts_processed = [item for sublist in df_preproc.tolist() for item in sublist]

    # Вычисляем длину каждой строки
    lengths_original = [len(s) for s in flat_texts_original]
    lengths_processed = [len(s) for s in flat_texts_processed]

    # Фильтруем, удаляя нулевые значения
    lengths_filtered_original = [length for length in lengths_original if length > 0]
    lengths_filtered_processed = [length for length in lengths_processed if length > 0]

    # Вычисляем логарифмические бины
    min_length = min(min(lengths_filtered_original), min(lengths_filtered_processed)) if lengths_filtered_original and lengths_filtered_processed else 1
    max_length = max(max(lengths_filtered_original), max(lengths_filtered_processed)) if lengths_filtered_original and lengths_filtered_processed else 1
    bins = np.logspace(np.log10(min_length), np.log10(max_length), num=50)

    # Создаем сетку графиков
    fig, axs = plt.subplots(1, 2, figsize=(16, 6))

    # График для исходных текстов
    axs[0].hist(lengths_filtered_original, bins=bins, alpha=0.7, color='blue', edgecolor='black')
    axs[0].set_xscale('log')
    axs[0].set_title('Исходные тексты')
    axs[0].set_xlabel('Длина строки (логарифмический масштаб)')
    axs[0].set_ylabel('Количество строк')
    axs[0].grid(axis='y', alpha=0.75)

    # График для обработанных текстов
    axs[1].hist(lengths_filtered_processed, bins=bins, alpha=0.7, color='green', edgecolor='black')
    axs[1].set_xscale('log')
    axs[1].set_title('Обработанные тексты')
    axs[1].set_xlabel('Длина строки (логарифмический масштаб)')
    axs[1].set_ylabel('Количество строк')
    axs[1].grid(axis='y', alpha=0.75)

    plt.tight_layout()
    plt.show()


"""
import nlpaug.augmenter.word as naw
import pandas as pd

# Создаем объект для аугментации
aug = naw.SynonymAug(aug_src='wordnet')

# Список для хранения обогащенных текстов и категорий
augmented_texts = []
augmented_categories = []

# Проходим по всему DataFrame и применяем аугментацию
for index, row in df_filtered.iterrows():
    augmented_text = aug.augment(row['texts'])
    augmented_texts.append(augmented_text)
    augmented_categories.append(row['Тип запроса (комби)'])

# Создаем новый DataFrame для обогащенных данных
df_augmented = pd.DataFrame({
    'texts': augmented_texts,
    'Тип запроса (комби)': augmented_categories
})

# Объединяем исходный и обогащенный DataFrame
df_combined = pd.concat([df_filtered, df_augmented], ignore_index=True)
"""

"""
df_filtered = df_combined
# Переиндексация df_filtered
df_filtered = df_filtered.reset_index(drop=True)
# Проверяем результат
print(df_filtered[['texts', 'Тип запроса (комби)']][7000:])
"""

from google.oauth2 import service_account
import gspread
from faiss_router.text_preproc import patterns

def save_to_sheets(df_filtered, save_regexp=False):
    # Путь к файлу с учетными данными сервисного аккаунта
    SERVICE_ACCOUNT_FILE = 'qna-project-415519-60fff000bbf6.json'

    # ID вашего Google Spreadsheet
    SPREADSHEET_ID = '1lb90koMF6y8J2lQWWqV0xnbwbo5iUMBwE7SY7JzXYHI'

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # Аутентификация с помощью ключа сервисного аккаунта
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)

    # Соединение с таблицей
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)

    # Выбор рабочего листа
    worksheet = spreadsheet.worksheet("text_token")

    # Преобразуем все значения в DataFrame в строковый формат
    df_sheet = df_filtered.astype(str)

    # Сохранение определенных столбцов в Google Spreadsheets
    selected_columns = ['tokens', 'Уточнение типа запроса - не определен', 'Тип запроса (комби)', 'texts', 'processed_texts']
    # Выбираем только нужные столбцы
    selected_data = df_sheet[selected_columns]

    # Преобразуем DataFrame в список списков (список строк)
    data_values = selected_data.values.tolist()

    # Преобразуем заголовки столбцов в список строк
    header_values = [selected_data.columns.values.tolist()]

    # Обновляем Google Spreadsheets
    worksheet.update(header_values + data_values)

    # Запись данных в Google Spreadsheets
    worksheet.update([selected_data.columns.values.tolist()] + selected_data.values.tolist())

    if save_regexp:
        # === Сохранение patterns ===

        # Выбор рабочего листа
        worksheet = spreadsheet.worksheet("regexp")

        # Преобразование словаря patterns в список списков для записи в Google Sheets
        header = ['token', 'regexp']
        data_to_write = []
        for key, values in patterns.items():
            for value in values:
                data_to_write.append([key,value])
            data_to_write.append(['', ''])

        data_with_header = [header] + data_to_write

        # Обновление Google Spreadsheet
        worksheet.update(values=data_with_header, range_name=f'A1:B{len(data_with_header)}')