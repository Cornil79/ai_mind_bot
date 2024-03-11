# импорт модулей
import os
import getpass
#from langchain.vectorstores import FAISS
#from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain.text_splitter import CharacterTextSplitter
#from langchain.docstore.document import Document
import re
import requests
import xmltodict
import json
import pandas as pd
import time
from tqdm.auto import tqdm  # Импортируем tqdm для отображения прогресс-бара
from sentence_transformers import SentenceTransformer
import numpy as np
#import faiss
import pickle
import ast  # Используется для преобразования строки в список/словарь
import matplotlib.pyplot as plt
import plotly.express as px
import ast

import faiss
import router_faiss.funcs2
import router_faiss.text_preproc
from router_faiss.text_preproc import preprocess_text_list
from router_faiss.local_model import LocalModel

# Сначала импортируем модуль importlib
import importlib

file_path = 'router_faiss/temp/'

class FaissRouter():
    def __init__(self, model_name='MiniLM'):
        self.model_name = model_name
        self.local_model = LocalModel('MiniLM')
        self.df_filtered = pd.read_pickle(f"{file_path}{self.model_name}-dataframe.pkl")
        self.embeddings = np.load(f"{file_path}{self.model_name}-embeddings.npy")
        
        # Нормализация эмбеддингов перед добавлением в faiss
        embeddings = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        dimension = embeddings.shape[1]  # Получаем размерность вектора эмбеддинга
        self.index = faiss.IndexFlatIP(dimension)  # Создаем индекс для L2 расстояния

        # Добавляем эмбеддинги в индекс
        self.index.add(embeddings)

        # Определите ширину первого столбца
        column_width = 25

        print(f"\033[92m-- Индекс faiss --\033[0m".ljust(column_width))
        print(f"Количество векторов:".ljust(column_width) + f"\033[92m{self.index.ntotal}\033[0m")
        print(f"Размерность векторов:".ljust(column_width) + f"\033[92m{self.index.d}\033[0m")
        print(f"Тип индекса:".ljust(column_width) + f"\033[92m{self.index.metric_type}\033[0m")  # 1 для L2
        print(f"dimension:".ljust(column_width) + f"\033[92m{dimension}\033[0m")

    def search_in_index(self, query_text, k=3):
        # Преобразование текста запроса в эмбеддинг
        questions = preprocess_text_list([query_text])
        query_embedding = self.local_model.generate_embeddings_batch([questions])
        # Поиск по индексу
        distances, indices = self.index.search(query_embedding, k)
        return distances[0], indices[0]  # Возвращаем индексы k наиболее похожих документов

    def search(self, questions):
        # @title Тестирование поиска FAISS

        from collections import Counter
        from router_faiss.funcs2 import colorful_bar

        k = 10
        result = []
        for query in questions:
            relevant_doc_distances, relevant_doc_indices = self.search_in_index(query, k=k)
            types = []
            for indice in relevant_doc_indices:
                types.append(self.df_filtered['Имя кластера'].iloc[indice])
                #types.append(self.df_filtered['Тип запроса (комби)'].iloc[indice])

            counter = Counter(types)
            # Наиболее часто встречающийся элемент и его количество
            most_common_element, count = counter.most_common(1)[0]
            stars = colorful_bar(count) if relevant_doc_distances[0].round(6) >=0.2 else " "

            result.append({
                'distance':         str(relevant_doc_distances[0].round(6)),
                'cluster_name':     most_common_element,
                'stars':            stars,
                'stars_count':      count,
                'stars_total':      k,
                'query_preproc':    preprocess_text_list([query]),
                'texts_preproc':    self.df_filtered['texts'][relevant_doc_indices[0]],
            })

        for res in result:
            print("{:<10} | {:<23} {:<10}| {} {}".format(res['distance'], res['cluster_name'], res['stars'], res['query_preproc'], res['texts_preproc']))

        return result