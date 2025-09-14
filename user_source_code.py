#!/usr/bin/env python3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
import logging
from telegram.error import BadRequest
from datetime import datetime
from khayyam import JalaliDatetime
import requests
import random
import json
import re
import aiohttp
import os
import json
TOKEN_FILE = 'bot_files/telegram_token.txt'
def load_user_bot_data(file):

   with open(f"{file}", "r", encoding="utf-8") as f:

       return json.load(f)

# Configure logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token
with open("bot_files/telegram_token.txt") as f:
       TOKEN = f.read().strip()
# API Configuration
WEATHER_API_KEY = "your_weather_api_key"
EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price"

# Global dictionary to store user responses
user_responses = {}

# ----------- TEMPLATE PROCESSING FUNCTIONS -----------

# ----------- TEMPLATE PROCESSING FUNCTIONS -----------
async def get_market_price(key: str) -> str:
    url = f'https://api.tgju.online/v1/market/indicator/{key}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('data', {}).get('price', 'نامشخص')
            return 'نامشخص'

async def handle_template_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    result = await process_template_variables(user_text)
    await update.message.reply_text(result)


async def process_template_variables(text: str, user_responses: dict = None) -> str:
    if user_responses is None:
        user_responses = {}

    replacements = {
        "$time": datetime.now().strftime("%H:%M:%S"),
        "$date": datetime.now().strftime("%Y-%m-%d"),
        "$jalali": JalaliDatetime.now().strftime("%Y/%m/%d"),
        "$weekday": JalaliDatetime.now().weekdayname(),

    }

    for var, value in replacements.items():
        text = text.replace(var, value)

    financial_data = {
        "$dollar_market": ("price_dollar_rl", lambda p: f"{p} تومان"),
        "$gold": ("sekeb", lambda p: f"{p} تومان"),
        "$bitcoin": ("bitcoin", lambda p: f"{p} $")
    }

    for var, (api_key, formatter) in financial_data.items():
        if var in text:
            price = await get_market_price(api_key)
            text = text.replace(var, formatter(price))

    user_var_pattern = re.compile(r'\$([a-zA-Z_][a-zA-Z0-9_]*)')
    text = user_var_pattern.sub(
        lambda m: user_responses.get(m.group(1), "[No value]"),
        text
    )

    text = re.sub(
        r'\$weather_([a-zA-Z]+)',
        r'Weather in \1: ☀️ 24°C',
        text
    )

    return text


# ----------- SYSTEM COMMAND HANDLERS -----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when /start is issued."""
    await update.message.reply_text("👋 Welcome! This is your Telegram bot.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help message when /help is issued."""
        await update.message.reply_text("""No commands available""")
    

# ----------- MAIN KEYBOARD HANDLERS -----------


# ----------- CUSTOM COMMAND HANDLERS -----------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all button presses by sending new messages."""
    query = update.callback_query
    await query.answer()
    # Send new message with button data
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"{query.data}"
    )

async def products_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        with open("user_bot.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        product_command = next((cmd for cmd in data.get("commands", []) if cmd.get("name") == "products"), None)
        if not product_command or not isinstance(product_command.get("response"), list):
               await update.message.reply_text("❌ No products found.")
               return "" 
        products = product_command["response"]
        if not products:
               await update.message.reply_text("❌ No products found.")
               return
        for product in products:
               msg = "\n".join([f"{key}: {value}" for key, value in product.items()])
               await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Error reading file: {e}")


# ----------- MAIN FUNCTION -----------
def main() -> None:
    """Start the bot."""
    if not TOKEN:
        logger.error("Please set your Telegram bot token!")
        return
    application = Application.builder().token(TOKEN).build()
    # System commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    # Ready-made commands
    application.add_handler(CommandHandler("products", products_handler))
    # Callback handlers
    application.add_handler(CallbackQueryHandler(button_callback))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()