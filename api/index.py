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
        # ИЗМЕНЕНИЕ ЗДЕСЬ: Используем синхронный метод send_message
        response = chat.send_message(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error during Gemini call or reply: {e}")
        await update.message.reply_text("Извините, у меня возникла внутренняя ошибка. Попробуйте еще раз позже.")

# --- Код для запуска (точка входа для Vercel) ---
app = Flask(__name__)

@app.route('/api/index', methods=['POST'])
def webhook():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    async def process_update_async():
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)
        await application.initialize()
        await application.process_update(update)
        await application.shutdown()

    asyncio.run(process_update_async())
    
    return Response('ok', status=200)
