from router_faiss.local_model_info import models_info
import torch
from tqdm.auto import tqdm
import numpy as np

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
from transformers import BertTokenizer, BertModel
from transformers import XLMRobertaTokenizer, XLMRobertaModel

import time


class LocalModel():
    def __init__(self, model_name='RuBERT'):
        # Предполагается, что models_info передается в качестве аргумента или как глобальная переменная
        self.model_name = model_name
        model_info = models_info[self.model_name]

        column_width = 25
        print(f"\033[92m-- Информация о модели --\033[0m".ljust(column_width))
        for key, value in model_info.items():
            print(f"{key}:".ljust(column_width) + f"\033[92m{value}\033[0m")

        if model_info['type'] == 'bert':  # Используем model_info['type'] для проверки типа модели
            self.tokenizer = AutoTokenizer.from_pretrained(model_info['tokenizer'])
            self.model = AutoModel.from_pretrained(model_info['model'])
        if model_info['type'] == 'bert_xlm':  # Используем model_info['type'] для проверки типа модели
            self.tokenizer = XLMRobertaTokenizer.from_pretrained(model_info['tokenizer'])
            self.model = XLMRobertaModel.from_pretrained(model_info['model'])
        if model_info['type'] == 'mbert':  # Используем model_info['type'] для проверки типа модели
            self.tokenizer = BertTokenizer.from_pretrained(model_info['tokenizer'])
            self.model = BertModel.from_pretrained(model_info['model'])
        if model_info['type'] == 'minilm':  # Используем model_info['type'] для проверки типа модели
            self.tokenizer = AutoTokenizer.from_pretrained(model_info['tokenizer'])
            #self.model = SentenceTransformer(model_info['model'])
            self.model = AutoModel.from_pretrained(model_info['model'])

    def get_model(self):
        return self.model

    def get_tokenizer(self):
        return self.tokenizer

    def generate_embeddings_batch(self, texts_lists, batch_size=10, progress=False):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(device)
        embeddings = []

        if progress:
            progress_bar = tqdm(total=len(texts_lists), desc='Генерация эмбеддингов')

        for i in range(0, len(texts_lists), batch_size):
            # Объединяем тексты в каждом подсписке в один текст перед токенизацией
            batch_texts = [" ".join(text_list) for text_list in texts_lists[i:i+batch_size]   ]# if text_list and any(text_list)]
            if not batch_texts:
                continue  # Пропускаем пустые батчи

            #print("Batch Texts:", batch_texts)  # Отладочный вывод

            encoded_input = self.tokenizer(batch_texts, padding=True, truncation=True, max_length=512, return_tensors='pt').to(device)

            #print("Encoded Input:", encoded_input)  # Отладочный вывод

            with torch.no_grad():
                model_output = self.model(**encoded_input)
                # Предполагаем, что мы берем последнее скрытое состояние в качестве эмбеддинга
                batch_embeddings = model_output.last_hidden_state.mean(dim=1).cpu().numpy()
                embeddings.append(batch_embeddings)

            if progress:
                progress_bar.update(len(batch_texts))

        if progress:
            progress_bar.close()

        # Соединяем все батчи в один массив и возвращаем
        return np.vstack(embeddings)