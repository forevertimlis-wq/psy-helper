from flask import Flask, request, Response
import os
import asyncio
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- Настройка ---
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Логика бота ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    system_instruction = "Ты — персональный психолог-консультант. Твоя задача — поддерживать пользователя, проявлять эмпатию и помогать ему разобраться в своих чувствах. Говори мягко и спокойно. Не давай прямых советов или команд. Вместо этого задавай уточняющие вопросы, которые помогут пользователю самому найти решение. Твои ответы должны быть краткими и направлены на поддержку диалога."
    chat = model.start_chat(history=[{'role': 'user', 'parts': [system_instruction]},{'role': 'model', 'parts': ["Здравствуйте. Я готов выслушать вас. Расскажите, что вас беспокоит?"]}])
    try:
        response = await chat.send_message_async(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error: {e}")

# --- Код для запуска (точка входа для Vercel) ---
app = Flask(__name__)

@app.route('/api/index', methods=['POST'])
def webhook():
    # Создаем экземпляр приложения внутри обработчика
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Создаем асинхронную функцию для обработки
    async def process_update_async():
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)
        # Инициализируем приложение ПЕРЕД обработкой
        await application.initialize()
        await application.process_update(update)
        # Корректно завершаем работу после выполнения
        await application.shutdown()

    # Запускаем асинхронную функцию
    asyncio.run(process_update_async())
    
    return Response('ok', status=200)
