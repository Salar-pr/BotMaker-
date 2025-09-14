import os
import re
import json
from typing import List, Tuple
from datetime import datetime
from khayyam import JalaliDatetime

USER_BOT_JSON = "user_bot.json"
TOKEN_FILE = "bot_files/telegram_token.txt"


class BotCodeGenerator:
    def __init__(self, features: dict):
        self.features = features
        self.token = self._read_token()
        self.user_responses = {}

    def _read_token(self) -> str:
        """Read bot token from file."""
        if not os.path.exists(TOKEN_FILE):
            return f"{TOKEN_FILE}"

        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()

    def _generate_imports(self) -> str:
        """Generate import statements."""
        imports = [
            "from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup",
            "from telegram.ext import (",
            "    Application,",
            "    CommandHandler,",
            "    ContextTypes,",
            "    CallbackQueryHandler,",
            "    MessageHandler,",
            "    filters,",
            "    ConversationHandler,",
            ")",
            "import logging",
            "from telegram.error import BadRequest",
            "from datetime import datetime",
            "from khayyam import JalaliDatetime",
            "import requests",
            "import random",
            "import json",
            "import re",
            "import aiohttp",
            "import os",
            "import json",
            "TOKEN_FILE = 'bot_files/telegram_token.txt'",
            "def load_user_bot_data():\n",
                'with open("user_bot.json", "r", encoding="utf-8") as f:\n',
                    'return json.load(f)\n',
        ]
        return "\n".join(imports)

    def _generate_system_handlers(self) -> str:
        """Generate system command handlers with session support for /start"""
        handlers = []

        if self.features.get("start_session"):
            session_code = [
                "async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:",
                '    """Send welcome message when /start is issued."""',
                "    user_id = update.message.from_user.id",
                "    user_responses[user_id] = user_responses.get(user_id, {})",
            ]

            for item in self.features["start_session"]:
                if item["type"] == "text":
                    content = item["content"].replace('"', '\\"')
                    if item.get("buttons"):
                        buttons_per_row = item.get("buttons_per_row", 2)
                        button_lines = []
                        for btn in item["buttons"]:
                            btn_text = btn["text"].replace('"', '\\"')
                            btn_url = btn["url"].replace('"', '\\"')
                            button_lines.append(
                                f'InlineKeyboardButton("{btn_text}", callback_data="{btn_url}")'
                            )

                        session_code.extend(
                            [
                                f"    buttons = [{', '.join(button_lines)}]",
                                f"    keyboard = [buttons[i:i+{buttons_per_row}] for i in range(0, len(buttons), {buttons_per_row})]",
                                "    reply_markup = InlineKeyboardMarkup(keyboard)",
                                f'    processed_content = await process_template_variables("{content}", user_responses[user_id])',
                                "    await update.message.reply_text(",
                                "        text=processed_content,",
                                "        reply_markup=reply_markup",
                                "    )",
                            ]
                        )
                    else:
                        session_code.extend(
                            [
                                f'    processed_content = await process_template_variables("{content}", user_responses[user_id])',
                                "    await update.message.reply_text(processed_content)",
                            ]
                        )
                elif item["type"] == "image":
                    url = item["url"].replace('"', '\\"')
                    caption = item.get("caption", "").replace('"', '\\"')
                    session_code.extend(
                        [
                            f'    processed_caption = await process_template_variables("{caption}", user_responses[user_id])',
                            f'    await update.message.reply_photo(photo="{url}", caption=processed_caption)',
                        ]
                    )

            session_code.append("    await update.message.reply_text(")
            session_code.append('        text="Select an option:",')
            session_code.append("        reply_markup=get_main_keyboard()")
            session_code.append("    )")

            handlers.append("\n".join(session_code))
        else:
            start_message = self.features.get("start") or "Welcome to the bot!"
            start_message = str(start_message).replace('"', '\\"')
            handlers.append(
                "async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:\n"
                '    """Send welcome message when /start is issued."""\n'
                f'    await update.message.reply_text("{start_message}")\n'
              
            )

        command_list = []
        if "custom_commands" in self.features:
            for cmd in self.features["custom_commands"]:
                desc = self.features["custom_commands"][cmd].get(
                    "description", "No description"
                )
                safe_desc = desc.replace('"', '\\"').replace("\n", "\\n")
                command_list.append(f"{cmd} - {safe_desc}")

        help_text = (
            "\\n".join(["Available commands:"] + command_list)
            if command_list
            else "No commands available"
        )

        handlers.append(
            f'''async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help message when /help is issued."""
        await update.message.reply_text("""{help_text}""")
    '''
        )

        return "\n".join(handlers)

    def _generate_template_handler(self) -> str:
        return """
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

    user_var_pattern = re.compile(r'\\$([a-zA-Z_][a-zA-Z0-9_]*)')
    text = user_var_pattern.sub(
        lambda m: user_responses.get(m.group(1), "[No value]"),
        text
    )

    text = re.sub(
        r'\\$weather_([a-zA-Z]+)',
        r'Weather in \\1: ☀️ 24°C',
        text
    )

    return text
"""

    def _generate_conversation_handlers(self) -> tuple:
        """Generate handlers for conversation-based commands."""
        handlers = []
        conv_handlers = []

        handlers.append(
            "async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:\n"
            '    """Cancel the conversation."""\n'
            '    await update.message.reply_text("Operation cancelled.")\n'
            "    return ConversationHandler.END\n"
        )

        if "custom_commands" not in self.features:
            return "\n".join(handlers), conv_handlers

        for cmd, details in self.features["custom_commands"].items():
            if details.get("type") != "command" or not details.get("session"):
                continue

            states = {}
            state_counter = 1
            session_items = details["session"]

            for idx, item in enumerate(session_items):
                if item["type"] == "wait_for_response":
                    states[idx] = state_counter
                    state_counter += 1

            if not states:
                continue

            cmd_name = cmd.lstrip("/").lower()
            description = details.get("description", f"Handler for {cmd}")

            entry_handler = (
                f"async def {cmd_name}_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:\n"
                f'    """{description}"""\n'
                "    user_id = update.message.from_user.id\n"
                "    user_responses[user_id] = user_responses.get(user_id, {})\n"
            )

            current_idx = 0
            while current_idx < len(session_items):
                item = session_items[current_idx]
                if item["type"] != "text":
                    break

                content = item["content"].replace('"', '\\"')
                entry_handler += (
                    "    processed_content = await process_template_variables("
                    f'"{content}", user_responses[user_id])\n'
                    "    await update.message.reply_text(processed_content)\n"
                )
                current_idx += 1

            if (
                current_idx < len(session_items)
                and session_items[current_idx]["type"] == "wait_for_response"
            ):
                prompt = (
                    session_items[current_idx]
                    .get("prompt", "Please respond:")
                    .replace('"', '\\"')
                )
                entry_handler += (
                    f'    await update.message.reply_text("{prompt}")\n'
                    f"    return {states[current_idx]}\n"
                )
            else:
                entry_handler += "    return ConversationHandler.END\n"

            handlers.append(entry_handler)

            for idx, state_num in states.items():
                item = session_items[idx]
                variable_name = item.get("variable", "")

                state_handler = (
                    f"async def {cmd_name}_state_{state_num}(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:\n"
                    f'    """Handle state {state_num} for {cmd} command."""\n'
                    "    user_id = update.message.from_user.id\n"
                    f'    user_responses[user_id]["{variable_name}"] = update.message.text\n'
                )

                next_idx = idx + 1
                while next_idx < len(session_items):
                    next_item = session_items[next_idx]
                    if next_item["type"] != "text":
                        break

                    content = next_item["content"].replace('"', '\\"')
                    state_handler += (
                        "    processed_content = await process_template_variables("
                        f'"{content}", user_responses[user_id])\n'
                        "    await update.message.reply_text(processed_content)\n"
                    )
                    next_idx += 1

                if (
                    next_idx < len(session_items)
                    and session_items[next_idx]["type"] == "wait_for_response"
                ):
                    prompt = (
                        session_items[next_idx]
                        .get("prompt", "Please respond:")
                        .replace('"', '\\"')
                    )
                    state_handler += (
                        f'    await update.message.reply_text("{prompt}")\n'
                        f"    return {states[next_idx]}\n"
                    )
                else:
                    state_handler += "    return ConversationHandler.END\n"

                handlers.append(state_handler)

            states_code = [
                f"{state_num}: [MessageHandler(filters.TEXT & ~filters.COMMAND, {cmd_name}_state_{state_num})],"
                for state_num in states.values()
            ]

            conv_handler_code = (
                f"    {cmd_name}_conv_handler = ConversationHandler(\n"
                f"        entry_points=[CommandHandler('{cmd_name}', {cmd_name}_handler)],\n"
                f"        states={{\n"
                f"            " + "\n            ".join(states_code) + "\n"
                f"        }},\n"
                f"        fallbacks=[CommandHandler('cancel', cancel)],\n"
                f"        conversation_timeout={details.get('timeout', 10.0)}\n"
                f"    )\n"
                f"    application.add_handler({cmd_name}_conv_handler)\n"
            )
            conv_handlers.append(conv_handler_code)

        return "\n".join(handlers), conv_handlers

    def generate_main_keyboard(self) -> str:
        """Generate code for persistent main menu keyboard with response actions."""
        if "main_keyboard" not in self.features:
            return ""

        cfg = self.features["main_keyboard"]
        buttons = cfg["buttons"]
        resize = cfg.get("resize", True)
        persistent = cfg.get("persistent", True)

        code = []
        code.append("# ========== MAIN KEYBOARD SETUP ==========")
        code.append("from telegram import ReplyKeyboardMarkup, KeyboardButton")
        code.append("")
        code.append("def get_main_keyboard():")
        code.append('    """Return configured main keyboard markup."""')
        code.append("    button_layout = [")

        for i in range(0, len(buttons), 2):
            row = buttons[i : i + 2]
            items = ", ".join('KeyboardButton("{}")'.format(b["text"]) for b in row)
            code.append("        [{}],".format(items))

        code.append("    ]")
        code.append(
            "    return ReplyKeyboardMarkup(button_layout, "
            "resize_keyboard={}, is_persistent={})".format(resize, persistent)
        )
        code.append("")

        code.append("# ========== MAIN KEYBOARD HANDLER ==========")
        code.append(
            "async def handle_main_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:"
        )
        code.append("    user_id = update.message.from_user.id")
        code.append("    user_responses[user_id] = user_responses.get(user_id, {})")
        code.append("    text = update.message.text")
        code.append("")
        code.append("    # map button-text → handler")
        code.append("    mapping = {")

        session_handlers = []
        for b in buttons:
            txt = b["text"]
            resp = b["response"]

            if isinstance(resp, dict) and resp.get("type") == "session":
                handler_name = f"handle_{txt.lower()}_session"
                session_code = [
                    f"async def {handler_name}(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:",
                    f'    """Handler for {txt} session."""',
                    "    user_id = update.message.from_user.id",
                    "    user_responses[user_id] = user_responses.get(user_id, {})",
                ]

                for item in resp["data"]:
                    if item["type"] == "text":
                        content = item["content"].replace('"', '\\"')
                        session_code.extend(
                            [
                                f'    processed_content = await process_template_variables("{content}", user_responses[user_id])',
                                "    await update.message.reply_text(processed_content)",
                            ]
                        )
                    elif item["type"] == "image":
                        url = item["url"].replace('"', '\\"')
                        caption = item.get("caption", "").replace('"', '\\"')
                        session_code.extend(
                            [
                                f'    processed_caption = await process_template_variables("{caption}", user_responses[user_id])',
                                f'    await update.message.reply_photo(photo="{url}", caption=processed_caption)',
                            ]
                        )

                session_code.append("    await update.message.reply_text(")
                session_code.append('        text="Select an option:",')
                session_code.append("        reply_markup=get_main_keyboard()")
                session_code.append("    )")

                session_handlers.append("\n".join(session_code))
                code.append(f"        '{txt}': {handler_name},")

        for b in buttons:
            txt = b["text"]
            resp = b["response"]

            if isinstance(resp, str) and resp.strip().lower() == "/start":
                code.append("        '{}': start,".format(txt))
            elif isinstance(resp, str) and resp.startswith("/"):
                cmd = resp.lstrip("/").lower()
                code.append(
                    "        '{0}': lambda u,c: context.application._handlers[0][('{1}', None)][0].callback(u,c),".format(
                        txt, cmd
                    )
                )

        code.append("    }")
        code.append("")

        if session_handlers:
            code.append("\n".join(session_handlers))
            code.append("")

        code.append("    if text in mapping:")
        code.append("        await mapping[text](update, context)")
        code.append("    else:")
        code.append("        await update.message.reply_text(")
        code.append("            text='Unknown option',")
        code.append("            reply_markup=get_main_keyboard()")
        code.append("        )")
        code.append("")

        return "\n".join(code)

    def _generate_main_function(
        self, command_handlers: str, callback_handlers: list, text_registrations: list
    ) -> str:
        """Generate the main function with proper conversation handler setup."""
        main_code = [
            "def main() -> None:",
            '    """Start the bot."""',
            "    if not TOKEN:",
            '        logger.error("Please set your Telegram bot token!")',
            "        return",
            "    application = Application.builder().token(TOKEN).build()",
            "",
            "    # System commands",
            '    application.add_handler(CommandHandler("start", start))',
            '    application.add_handler(CommandHandler("help", help_command))',
            "",
            "    # Button callbacks from start session",
            "    application.add_handler(CallbackQueryHandler(button_callback))",
            "",
            "    # Main keyboard handler",
            "    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_keyboard))",
            "    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_template_message))",
        ]

        if text_registrations:
            main_code.extend(
                ["", "    # Text trigger handlers", "\n".join(text_registrations)]
            )

        main_code.extend(
            ["", "    application.run_polling(allowed_updates=Update.ALL_TYPES)"]
        )

        return "\n".join([line for line in main_code if line])

    def _generate_text_trigger_handlers(self) -> Tuple[str, List[str]]:
        """Generate combined text trigger handler with proper message processing order."""
        handlers = []
        registrations = []
        triggers = []

        if "custom_commands" not in self.features:
            return "", []

        for trigger, details in self.features["custom_commands"].items():
            if details.get("type") != "text":
                continue

            raw_response = (
                details.get("response", "").replace('"', '\\"').replace("\n", "\\n")
            )
            trigger_word = trigger.lstrip("/")
            triggers.append((trigger_word, raw_response))

        if not triggers:
            return "", []

        handler_code = [
            "async def text_trigger_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:",
            '    """Handle all text triggers in one handler."""',
            "    msg = update.message.text.lower()",
            "    user_id = update.message.from_user.id",
            "    user_responses[user_id] = user_responses.get(user_id, {})",
            "    handled = False",
        ]

        for trigger_word, response in triggers:
            handler_code.extend(
                [
                    f'    if "{trigger_word}" in msg and not handled:',
                    f'        processed = await process_template_variables("{response}", user_responses[user_id])',
                    "        await update.message.reply_text(processed)",
                    "        handled = True",
                ]
            )

        handler_code.append("    if not handled:")
        handler_code.append("        # No trigger matched, pass to other handlers")
        handler_code.append("        return")

        handlers.append("\n".join(handler_code))
        registrations.append(
            "    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_trigger_handler))"
        )

        return "\n".join(handlers), registrations

    def _generate_ready_made_handlers(self) -> tuple:
        """Generate async handlers for ready-made custom commands and features."""
        handlers = []
        command_handlers = []
        callback_handlers = []
        button_patterns = []
        conv_registrations = []
        text_registrations = []

        conv_handlers, conv_registrations = self._generate_conversation_handlers()
        if conv_handlers:
            handlers.append(conv_handlers)

        text_handlers, text_registrations = self._generate_text_trigger_handlers()
        if text_handlers:
            handlers.append(text_handlers)

        handlers.append(
            "async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:\n"
            '    """Handle all button presses by sending new messages."""\n'
            "    query = update.callback_query\n"
            "    await query.answer()\n"
            "    # Send new message with button data\n"
            "    await context.bot.send_message(\n"
            "        chat_id=query.message.chat_id,\n"
            '        text=f"{query.data}"\n'
            "    )\n"
        )

        for cmd, details in self.features.get("custom_commands", {}).items():
            if details.get("type") != "command":
                continue

            if details.get("session") and any(
                item["type"] == "wait_for_response" for item in details["session"]
            ):
                continue

            if details.get("session") is None:
                details["session"] = []

            cmd_name = cmd.lstrip("/").lower()
            description = details.get("description", f"Handler for {cmd}")

            if cmd == "/time":
                handlers.append(
                    f"async def {cmd_name}_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:\n"
                    f'    """{description}"""\n'
                    '    current_time = datetime.now().strftime("%H:%M:%S")\n'
                    '    await update.message.reply_text(f"🕒 Current time: {current_time}")\n'
                )
                command_handlers.append(
                    f'    application.add_handler(CommandHandler("{cmd_name}", {cmd_name}_handler))'
                )
                continue

            if cmd == "/date":
                handlers.append(
                    f"async def {cmd_name}_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:\n"
                    f'    """{description}"""\n'
                    '    gregorian_date = datetime.now().strftime("%Y-%m-%d")\n'
                    '    jalali_date = JalaliDatetime.now().strftime("%Y/%m/%d")\n'
                    "    weekday = JalaliDatetime.now().weekdayname()\n"
                    "    await update.message.reply_text(\n"
                    '        f"📅 Today: {gregorian_date} (Gregorian)\\n{jalali_date} ({weekday})"\n'
                    "    )\n"
                )
                command_handlers.append(
                    f'    application.add_handler(CommandHandler("{cmd_name}", {cmd_name}_handler))'
                )
                continue

            if cmd == "/weather":
                handlers.append(
                    f"async def {cmd_name}_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:\n"
                    f'    """{description}"""\n'
                    '    cities = ["Tehran", "Karaj", "Mashhad", "Isfahan", "Shiraz", "Tabriz", "Gilan"]\n'
                    '    keyboard = [[InlineKeyboardButton(city, callback_data=f"weather_{city.lower()}")] for city in cities]\n'
                    "    reply_markup = InlineKeyboardMarkup(keyboard)\n"
                    '    await update.message.reply_text("🌤 Select a city for weather:", reply_markup=reply_markup)\n'
                )
                handlers.append(
                    "async def weather_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:\n"
                    '    """Handle weather city selection."""\n'
                    "    query = update.callback_query\n"
                    "    await query.answer()\n"
                    "    city = query.data.replace('weather_', '').title()\n"
                    "    weather_info = {\n"
                    '        "tehran": "☀️ 24°C, Sunny",\n'
                    '        "karaj": "⛅ 22°C, Partly Cloudy",\n'
                    '        "mashhad": "☀️ 26°C, Sunny",\n'
                    '        "isfahan": "☀️ 28°C, Sunny",\n'
                    '        "shiraz": "☀️ 30°C, Sunny",\n'
                    '        "tabriz": "⛅ 20°C, Partly Cloudy",\n'
                    '        "gilan": "🌧 18°C, Rainy"\n'
                    "    }\n"
                    "    await query.edit_message_text(\n"
                    "        text=f\"Weather in {city}: {weather_info.get(city.lower(), 'No data available')}\")\n"
                )
                command_handlers.append(
                    f'    application.add_handler(CommandHandler("{cmd_name}", {cmd_name}_handler))'
                )
                callback_handlers.append(
                    '    application.add_handler(CallbackQueryHandler(weather_callback, pattern="^weather_"))'
                )
                continue

            if cmd == "/dollar":
                handlers.append(
                    f"async def {cmd_name}_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:\n"
                    f'    """{description}"""\n'
                    "    url = 'https://api.tgju.online/v1/market/indicator/price_dollar_rl'\n"
                    "    async with aiohttp.ClientSession() as session:\n"
                    "        async with session.get(url) as resp:\n"
                    "            if resp.status == 200:\n"
                    "                data = await resp.json()\n"
                    "                price = data.get('data', {}).get('price', 'نامشخص')\n"
                    "                await update.message.reply_text(f'💵 قیمت لحظه‌ای دلار: {price} تومان')\n"
                    "            else:\n"
                    "                await update.message.reply_text('❌ خطا در دریافت نرخ دلار')\n"
                )
                command_handlers.append(
                    f'    application.add_handler(CommandHandler("{cmd_name}", {cmd_name}_handler))'
                )
                continue

            if not details.get("session") and details.get("response"):
                response_text = (
                    details["response"].replace('"', '\\"').replace("\n", "\\n")
                )
                handlers.append(
                    f"async def {cmd_name}_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:\n"
                    f'    """{description}"""\n'
                    "    user_id = update.message.from_user.id\n"
                    "    user_responses[user_id] = user_responses.get(user_id, {})\n"
                    f'    processed = await process_template_variables("{response_text}", user_responses[user_id])\n'
                    "    await update.message.reply_text(processed)\n"
                )
                command_handlers.append(
                    f'    application.add_handler(CommandHandler("{cmd_name}", {cmd_name}_handler))'
                )
                continue

            if details.get("session"):
                handler_code = (
                    f"async def {cmd_name}_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:\n"
                    f'    """{description}"""\n'
                    "    user_id = update.message.from_user.id\n"
                    "    user_responses[user_id] = user_responses.get(user_id, {})\n"
                )
                cmd_button_patterns = []

                for item in details["session"]:
                    if item["type"] == "text":
                        content = (
                            item["content"].replace('"', '\\"').replace("\n", "\\n")
                        )
                        if item.get("buttons"):
                            buttons = []
                            for btn in item["buttons"]:
                                data = btn["url"].replace('"', '\\"')
                                buttons.append(
                                    f'InlineKeyboardButton("{btn["text"]}", callback_data="{data}")'
                                )
                                cmd_button_patterns.append(data)
                            handler_code += (
                                f'    processed_content = await process_template_variables("{content}", user_responses[user_id])\n'
                                f"    all_buttons = [{', '.join(buttons)}]\n"
                                f"    keyboard = [all_buttons[i:i+3] for i in range(0, len(all_buttons), 3)]\n"
                                f"    reply_markup = InlineKeyboardMarkup(keyboard)\n"
                                f"    await update.message.reply_text(processed_content, reply_markup=reply_markup)\n"
                            )
                        else:
                            handler_code += (
                                f'    processed_content = await process_template_variables("{content}", user_responses[user_id])\n'
                                "    await update.message.reply_text(processed_content)\n"
                            )

                    elif item["type"] == "image":
                        image_url = item["url"].replace('"', '\\"')
                        caption = item.get("caption", "").replace('"', '\\"')
                        text_position = item.get("text_position", "below")

                        handler_code += (
                            "    # Process image template\n"
                            "    processed_caption = await process_template_variables(\n"
                            f'        "{caption}", user_responses[user_id])\n'
                        )

                        if item.get("buttons"):
                            handler_code += "    # Create inline keyboard\n"
                            button_lines = []
                            for btn in item["buttons"]:
                                btn_text = (
                                    btn["text"]
                                    .replace("\\", "\\\\")
                                    .replace('"', r"\"")
                                )
                                btn_url = (
                                    btn["url"].replace("\\", "\\\\").replace('"', r"\"")
                                )

                                button_lines.append(
                                    "        InlineKeyboardButton(\n"
                                    "            await process_template_variables(\n"
                                    f'                r"{btn_text}", user_responses[user_id]),\n'
                                    f'            callback_data=await process_template_variables(r"{btn_url}", user_responses[user_id])\n'
                                    "        )"
                                )
                                cmd_button_patterns.append(btn_url)

                            handler_code += (
                                "    flat_buttons = [\n"
                                + ",\n".join(button_lines)
                                + "\n"
                                "    ]\n"
                                "    keyboard = [flat_buttons[i:i+3] for i in range(0, len(flat_buttons), 3)]\n"
                                "    reply_markup = InlineKeyboardMarkup(keyboard)\n"
                            )
                        else:
                            handler_code += "    reply_markup = None\n"

                        handler_code += (
                            "    # Send image with caption positioning\n"
                            "    await update.message.reply_photo(\n"
                            f'        photo="{image_url}",\n'
                            "        caption=processed_caption,\n"
                            "        reply_markup=reply_markup,\n"
                            f"        show_caption_above_media={text_position.lower() == 'above'}\n"
                            "    )\n"
                        )

                handlers.append(handler_code)
                command_handlers.append(
                    f'    application.add_handler(CommandHandler("{cmd_name}", {cmd_name}_handler))'
                )

                if cmd_button_patterns:
                    escaped = [f"^{re.escape(p)}" for p in cmd_button_patterns]
                    button_patterns.extend(escaped)

        if button_patterns:
            pattern = "|".join(button_patterns)
            callback_handlers.append(
                f'    application.add_handler(CallbackQueryHandler(button_callback, pattern="{pattern}"))'
            )

        callback_handlers.append(
            "    application.add_handler(CallbackQueryHandler(button_callback))"
        )

        command_handlers.extend(conv_registrations)

        if os.path.exists("user_bot.json"):
            with open("user_bot.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            product_command = next(
                (cmd for cmd in data.get("commands", []) if cmd.get("name") == "products"), None
            )
            if product_command and isinstance(product_command.get("response", None), list):
                handlers.append(
                    "async def products_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:\n"
                    '    try:\n'
                    '        with open("user_bot.json", "r", encoding="utf-8") as f:\n'
                    '            data = json.load(f)\n'
                    '        product_command = next((cmd for cmd in data.get("commands", []) if cmd.get("name") == "products"), None)\n'
                    '        if not product_command or not isinstance(product_command.get("response"), list):\n'
                    '               await update.message.reply_text("❌ No products found.")\n'
                    '               return "" \n'
                    '        products = product_command["response"]\n'
                    '        if not products:\n'
                    '               await update.message.reply_text("❌ No products found.")\n'
                    '               return\n'
                    '        for product in products:\n'
                    '               msg = "\\n".join([f"{key}: {value}" for key, value in product.items()])\n'
                    '               await update.message.reply_text(msg)\n'
                    '    except Exception as e:\n'
                    '        await update.message.reply_text(f"❌ Error reading file: {e}")\n'
                )
            command_handlers.append(
                '    application.add_handler(CommandHandler("products", products_handler))'
            )

        return (
            "\n".join(handlers),
            "\n".join(command_handlers),
            callback_handlers,
            text_registrations,
        )

    def _generate_main_function(
        self, command_handlers: str, callback_handlers: list, text_registrations: list
    ) -> str:
        """Generate the main function with proper conversation handler setup."""
        main_code = [
            "def main() -> None:",
            '    """Start the bot."""',
            "    if not TOKEN:",
            '        logger.error("Please set your Telegram bot token!")',
            "        return",
            "    application = Application.builder().token(TOKEN).build()",
            "",
            "    # System commands",
            '    application.add_handler(CommandHandler("start", start))',
            '    application.add_handler(CommandHandler("help", help_command))',
            "",
            "    # Ready-made commands",
            command_handlers,
            "",
            "    # Callback handlers",
            "\n".join(callback_handlers),
        ]

        if text_registrations:
            main_code.extend(
                ["", "    # Text trigger handlers", "\n".join(text_registrations)]
            )

        main_code.extend(
            ["", "    application.run_polling(allowed_updates=Update.ALL_TYPES)"]
        )

        return "\n".join([line for line in main_code if line])

    def generate_code(self) -> str:
        """Generate complete bot code."""
        code_parts = [
            "#!/usr/bin/env python3",
            self._generate_imports(),
            "",
            "# Configure logging",
            'logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)',
            "logger = logging.getLogger(__name__)",
            "",
            "# Bot Token",
            'with open("bot_files/telegram_token.txt") as f:',
            "       TOKEN = f.read().strip()",
            "# API Configuration",
            'WEATHER_API_KEY = "your_weather_api_key"',
            'EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"',
            'CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price"',
            "",
            "# Global dictionary to store user responses",
            "user_responses = {}",
            "",
            "# ----------- TEMPLATE PROCESSING FUNCTIONS -----------",
            self._generate_template_handler(),
            "",
            "# ----------- SYSTEM COMMAND HANDLERS -----------",
            self._generate_system_handlers(),
            "",
            "# ----------- MAIN KEYBOARD HANDLERS -----------",
            self.generate_main_keyboard(),
        ]

        command_handlers, cmd_reg, cb_reg, text_reg = (
            self._generate_ready_made_handlers()
        )
        code_parts.extend(
            [
                "",
                "# ----------- CUSTOM COMMAND HANDLERS -----------",
                command_handlers,
                "",
                "# ----------- MAIN FUNCTION -----------",
                self._generate_main_function(cmd_reg, cb_reg, text_reg),
                "",
                'if __name__ == "__main__":',
                "    main()",
            ]
        )
        return "\n".join(code_parts)
