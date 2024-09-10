import os
import json
import logging
import requests
from base64 import urlsafe_b64decode
from datetime import datetime
from urllib.parse import parse_qs, urlparse, unquote
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from colorama import init, Fore, Style

# Setup colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define color codes
merah = Fore.LIGHTRED_EX
hijau = Fore.LIGHTGREEN_EX
putih = Fore.LIGHTWHITE_EX
kuning = Fore.LIGHTYELLOW_EX
line = putih + "~" * 50

# Define the Telegram bot token
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    raise ValueError("Token bot tidak diset di variabel lingkungan.")

def decode_url_data(url):
    try:
        # Parse URL dan query params
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        fragment_params = parse_qs(parsed_url.fragment)
        
        # Ambil dan decode tgWebAppData
        tg_web_app_data = fragment_params.get('tgWebAppData', [''])[0]
        decoded_data = unquote(tg_web_app_data)
        
        # Temukan akhir data relevan
        end_index = decoded_data.find('&tgWebApp')
        if end_index != -1:
            decoded_data = decoded_data[:end_index]
        
        # Decode dan format data
        formatted_data = unquote(decoded_data)
        formatted_data = formatted_data.replace('&tgWebApp', ' ')
        
        # Mengubah data JSON jika perlu
        try:
            json_data = json.loads(formatted_data)
            formatted_data = json.dumps(json_data, indent=4)
        except json.JSONDecodeError:
            pass
        
        formatted_data = ' '.join(formatted_data.split())
        return '```\n' + formatted_data + '\n```'.replace('\n', ' ')
    except Exception as e:
        logger.error(f"Terjadi kesalahan saat mendecode URL: {e}")
        return 'Terjadi kesalahan saat memproses URL.'

async def handle_message(update: Update, context):
    message_text = update.message.text

    try:
        # Periksa jika pesan mengandung URL dengan 'tgWebAppData'
        if 'tgWebAppData=' in message_text:
            formatted_data = decode_url_data(message_text)
        else:
            # Decode pesan secara keseluruhan
            decoded_message = unquote(message_text)
            formatted_data = decoded_message.replace('&tgWebApp', ' ')
            formatted_data = ' '.join(formatted_data.split())
            formatted_data = '```\n' + formatted_data + '\n```'.replace('\n', ' ')
        
        await update.message.reply_text(formatted_data, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error(f"Terjadi kesalahan saat memproses pesan: {e}")
        await update.message.reply_text('Terjadi kesalahan saat memproses pesan.')

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
