from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from telegram import Update
from dotenv import load_dotenv
import openai
import os
#from gpt import Chunk
from open_ai_router import OpenAIRouter
from router_faiss.router import FaissRouter
import random
import time

# список диалогов пользователей
dialog = {}

# инициализация индексной базы
#chunk = Chunk()
# подгружаем переменные окружения
load_dotenv()

# передаем секретные данные в переменные
TOKEN = os.environ.get("TG_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DOC_URL = os.environ.get("DOC_URL")

open_ai_router = OpenAIRouter()

load_result = open_ai_router.load_prompts(DOC_URL, 0)
if load_result[1]:
    print(f"\n\033[92m{load_result[0]}\033[0m")  # Зелёный
else:
    print(f"\n\033[91m{load_result[0]}\033[0m")  # Красный

# передаем секретный токен chatgpt
openai.api_key = OPENAI_API_KEY

faiss_router = FaissRouter()

# функция-обработчик команды /start 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global open_ai_router
    user_id = update.effective_user.id
    # возвращаем текстовое сообщение пользователю
    hello_text = 'Классификатор запросов "Планета Здоровья"'
    first_message = await update.message.reply_text(hello_text)

    load_result = open_ai_router.load_prompts(DOC_URL, user_id)
    if load_result[1]:
        print(f"\n\033[92m{load_result[0]}\033[0m")  # Зелёный
    else:
        print(f"\n\033[91m{load_result[0]}\033[0m")  # Красный

    prompts_url = f"""<b>Ссылка на исходные промпты для OpenAI:</b>\n{DOC_URL}\n
✅ Для смены промптов, скопируйте документ по ссылке выше и используйте команду /setdocurl <i>current_doc_url</i>
Где <i>current_doc_url</i> - ссылка на новый документ с промптами.\n
<b>ℹ️ Внимание, <i>current_doc_url</i> не сохраняется в файл и при перезапуске бота на сервере он будет сброшен.</b>\n
ℹ️ Для загрузки стандартных промптов, еще раз используйте команду /start"""
    
    await context.bot.edit_message_text(
        text=f"{hello_text}\n\n{load_result[0]}\n\n{prompts_url}",
        chat_id=update.message.chat_id,
        message_id=first_message.message_id,
        parse_mode='HTML',
        disable_web_page_preview=True
    )

# Функция-обработчик команды /setdocurl
async def set_doc_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args  # Получаем список аргументов
    if args:
        current_doc_url = args[0]  # Первый аргумент после команды считается URL
        load_result = open_ai_router.load_prompts(current_doc_url, user_id=user_id)
        response_text = f"URL для загрузки промптов обновлён: {current_doc_url}\n\n<b>Результат загрузки:</b>\n{load_result[0]}"
    else:
        response_text = "Пожалуйста, укажите URL после команды. Например: /setdocurl http://example.com/prompts.md"
    
    await update.message.reply_text(response_text, parse_mode='HTML', disable_web_page_preview=True)

async def reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Вызов функции перезагрузки промптов
    result_message = open_ai_router.reload_prompts(user_id)
    
    # Отправка результата пользователю
    await update.message.reply_text(result_message[0], parse_mode='HTML')

# функция-обработчик текстовых сообщений
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global faiss_router
    global open_ai_router
    user_id = update.effective_user.id
    # вывод сообщения об обработке документа
    first_message = await update.message.reply_text('Вопрос принят...')

    # Поиск по FAISS
    start_faiss_time = time.time()
    faiss_res = faiss_router.search([update.message.text])
    end_faiss_time = round(time.time() - start_faiss_time, 6)

    start_ai_time = time.time()
    res = await open_ai_router.get_route(question=update.message.text, user_id=user_id)
    end_ai_time = round(time.time() - start_ai_time, 6)
    prompt = open_ai_router.prompts.get(user_id)
    if prompt is not None:
        if prompt['url'] == DOC_URL:
            prompt_info = f"❗️<i><b>Используется стандартный промпт</b></i>"
        else:
            prompt_info = f"ℹ️ Промпт обновлен: {prompt['last_update']}"
    else:
        prompt_info = f"❗️<i><b>Используется стандартный промпт</b></i>"

    #faiss_result = f"\n<b>FAISS:</b>\n<i>{faiss_res[0]['cluster_name']}</i>\nУверен: <i>{(faiss_res[0]['stars_count']/faiss_res[0]['stars_total'])*100}%</i>"
    faiss_result = f"\n<b>FAISS</b> ({end_faiss_time} секунд):\n<i>{faiss_res[0]['cluster_name']}</i>\nУверен: <i>{faiss_res[0]['stars_count']}/{faiss_res[0]['stars_total']}</i>"
    open_ai_result = f"\n<b>OpenAI</b> ({end_ai_time} секунд):\n{prompt_info}\n<i>{res}</i>"

    end_time = round(end_faiss_time + end_ai_time, 6)
    message_text = f"Запрос выполнен за: <b>{end_time}</b> секунд\n{faiss_result}\n{open_ai_result}\n\nПерезагрузить промпт /reload"
    # сообщение результата
    await context.bot.edit_message_text(text = message_text, chat_id = update.message.chat_id, message_id = first_message.message_id, parse_mode='HTML')

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('setdocurl', set_doc_url))
    application.add_handler(CommandHandler('reload', reload))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

    print('\n\033[92mБот запущен...\033[0m')
    application.run_polling()
    print('Бот остановлен')

if __name__ == "__main__":
    main()