models_info = {
    'RuBERT': {
        'type': "bert", # RuBERT
        'model': "DeepPavlov/rubert-base-cased",
        'tokenizer': "DeepPavlov/rubert-base-cased",
    },
    'RuElectra': {
        'type': "bert", # RuElectra
        'model': "sberbank-ai/rugpt3small_based_on_gpt2",
        'tokenizer': "sberbank-ai/rugpt3small_based_on_gpt2",
    },
    'RuDialoGPT': {
        'type': "bert", # RuDialoGPT
        'model': "blinoff-levy/ru-electra",
        'tokenizer': "blinoff-levy/ru-electra",
    },
    'RuDialoGPT': {
        'type': "bert", # RuDialoGPT
        'model': "sberbank-ai/rugpt3large_based_on_gpt2",
        'tokenizer': "sberbank-ai/rugpt3large_based_on_gpt2",
    },
    'RuALBERT': {
        'type': "bert",  # RuALBERT
        'model': "ai4bharat/albert-base-v2-mrqa",
        'tokenizer': "ai4bharat/albert-base-v2-mrqa",
    },
    'LaBSE': {
        'type': "bert",  # LaBSE "setu4993/LaBSE"
        'model': "setu4993/LaBSE",
        'tokenizer': "setu4993/LaBSE",
    },
    'XLM-R': {
        'type': "bert_xlm",  # XLM-R (XLM-RoBERTa) "xlm-roberta-base"
        'model': "xlm-roberta-base",
        'tokenizer': "xlm-roberta-base",
    },
    'mBERT': {
        'type': "mbert",  # mBERT
        'model': "bert-base-multilingual-cased",
        'tokenizer': "bert-base-multilingual-cased",
    },
    'BioBERT': {
        'type': "mbert",  # BioBERT
        'model': "dmis-lab/biobert-base-cased-v1.1",
        'tokenizer': "dmis-lab/biobert-base-cased-v1.1",
    },
    # 'MiniLM': {
    #     'type': "minilm",  # all-MiniLM-L6-v2
    #     'model': "sentence-transformers/all-MiniLM-L6-v2",
    #     'tokenizer': "all-MiniLM-L6-v2",
    # },
    'MiniLM': {
        'type': "minilm",  # all-MiniLM-L6-v2
        'model': "sentence-transformers/all-MiniLM-L6-v2",
        'tokenizer': "sentence-transformers/all-MiniLM-L6-v2",
    },
}
