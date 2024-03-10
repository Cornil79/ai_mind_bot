from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from telegram import Update
from dotenv import load_dotenv
import openai
import os
#from gpt import Chunk
from open_ai_router import OpenAIRouter
from faiss_router.router import FaissRouter
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
load_result = open_ai_router.reload_prompts(DOC_URL)
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
    # возвращаем текстовое сообщение пользователю
    hello_text = 'Классификатор запросов "Планета Здоровья"'
    first_message = await update.message.reply_text(hello_text)

    load_result = open_ai_router.reload_prompts(DOC_URL)
    if load_result[1]:
        print(f"\n\033[92m{load_result[0]}\033[0m")  # Зелёный
    else:
        print(f"\n\033[91m{load_result[0]}\033[0m")  # Красный

    prompts_url = f"<b>Ссылка для редактирования промптов:</b>\n{DOC_URL}\n\nПосле редактирования, еще раз используйте команду /start"
    await context.bot.edit_message_text(
        text=f"{hello_text}\n\n{load_result[0]}\n\n{prompts_url}",
        chat_id=update.message.chat_id,
        message_id=first_message.message_id,
        parse_mode='HTML',
        disable_web_page_preview=True
    )

# функция-обработчик текстовых сообщений
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global faiss_router
    global open_ai_router
    # вывод сообщения об обработке документа
    first_message = await update.message.reply_text('Вопрос принят...')

    # Поиск по FAISS
    start_faiss_time = time.time()
    faiss_res = faiss_router.search([update.message.text])
    end_faiss_time = round(time.time() - start_faiss_time, 6)

    start_ai_time = time.time()
    res = await open_ai_router.get_route(question = update.message.text)
    end_ai_time = round(time.time() - start_ai_time, 6)

    #faiss_result = f"\n<b>FAISS:</b>\n<i>{faiss_res[0]['cluster_name']}</i>\nУверен: <i>{(faiss_res[0]['stars_count']/faiss_res[0]['stars_total'])*100}%</i>"
    faiss_result = f"\n<b>FAISS</b> ({end_faiss_time} секунд):\n<i>{faiss_res[0]['cluster_name']}</i>\nУверен: <i>{faiss_res[0]['stars_count']}/{faiss_res[0]['stars_total']}</i>"
    open_ai_result = f"\n<b>OpenAI</b> ({end_ai_time} секунд):\n<i>{res}</i>"

    end_time = round(end_faiss_time + end_ai_time, 6)
    message_text = f"Запрос выполнен за: <b>{end_time}</b> секунд\n{faiss_result}\n{open_ai_result}"
    # сообщение результата
    await context.bot.edit_message_text(text = message_text, chat_id = update.message.chat_id, message_id = first_message.message_id, parse_mode='HTML')

def main():
    # создаем приложение и передаем в него токен бота
    application = Application.builder().token(TOKEN).build()
    print('\n\033[92mБот запущен...\033[0m')
    # добавление обработчиков
    application.add_handler(CommandHandler('start', start, block=False))
    application.add_handler(MessageHandler(filters.TEXT, text, block=False))
    # запуск бота (нажать Ctrl+C для остановки)
    application.run_polling()
    print('Бот остановлен')

if __name__ == "__main__":
    main()