from flask import Flask, request, Response
import os
import asyncio
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    system_instruction = "Ты — персональный психолог-консультант. Твоя задача — поддерживать пользователя, проявлять эмпатию и помогать ему разобраться в своих чувствах. Говори мягко и спокойно. Не давай прямых советов или команд. Вместо этого задавай уточняющие вопросы, которые помогут пользователю самому найти решение. Твои ответы должны быть краткими и направлены на поддержку диалога."
    chat = model.start_chat(history=[{'role': 'user', 'parts': [system_instruction]},{'role': 'model', 'parts': ["Здравствуйте. Я готов выслушать вас. Расскажите, что вас беспокоит?"]}])
    try:
        response = await chat.send_message_async(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error: {e}")

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app = Flask(__name__)

@app.route('/api/index', methods=['POST'])
def webhook():
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, application.bot)
    asyncio.run(application.process_update(update))
    return Response('ok', status=200)
