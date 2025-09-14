#!/usr/bin/env python3
import os
import sys
import json
import shutil
import time
import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich import box
from custom_command import custom_command
import sys
from wcwidth import wcwidth
sys.path.insert(1, "./python_dependence/")
from session_manager import create_new_session
from BotCodeGenerator import BotCodeGenerator
import google.generativeai as genai
import pandas as pd
from tkinter import Tk, filedialog
from python import print_centered, IDEA_FLOW_ART

console = Console()
USER_BOT_JSON = "user_bot.json"
BOT_SCRIPT_FILENAME = "user_source_code.py"
TOKEN_FILE = "bot_files/telegram_token.txt"
SESSIONS_FILE = "sessions.json"
ECO_TEMPLATE_FILENAME = "eco_template.json"
TODO_TEMPLATE_FILENAME = "todo_template.json"
EXCEL_FILE_JSON = "Excel.json"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)
features = {}

def load_user_bot_data(file):
    with open(f"{file}", "r", encoding="utf-8") as f:
        return json.load(f)
    
if not os.path.exists("session_manager.py"):
    with open("session_manager.py", "w", encoding="utf-8") as f:
        f.write("""
from rich.console import Console
console = Console()
def create_new_session():
    console.print("[yellow]Placeholder for create_new_session[/]")
        """)

if not os.path.exists("custom_command.py"):
    with open("custom_command.py", "w", encoding="utf-8") as f:
        f.write("""
from rich.console import Console
console = Console()
def custom_command():
    console.print("[yellow]Placeholder for custom_command[/]")
        """)

if not os.path.exists("BotCodeGenerator.py"):
    with open("BotCodeGenerator.py", "w", encoding="utf-8") as f:
        f.write("""
import json
import telebot
from telebot import types
import os

class BotCodeGenerator:
    def __init__(self, features):
        self.features = features

    def generate_code(self):
        code = f"# Auto-generated Telegram Bot Code by BotCodeGenerator\\n"
        code += f"import json\\n"
        code += f"import telebot\\n"
        code += f"from telebot import types\\n"
        code += f"import os\\n\\n"
        
        # Load token from file
        code += f"TOKEN_FILE = 'bot_files/telegram_token.txt'\\n"
        code += f"TOKEN = None\\n"
        code += f"try:\\n"
        code += f"    with open(TOKEN_FILE, 'r', encoding='utf-8') as f:\\n"
        code += f"        TOKEN = f.read().strip()\\n"
        code += f"except FileNotFoundError:\\n"
        code += f"    print(f'Error: Token file {{TOKEN_FILE}} not found.')\\n"
        code += f"    exit(1)\\n"
        code += f"if not TOKEN or TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':\\n"
        code += f"    print('Error: Please replace YOUR_TELEGRAM_BOT_TOKEN_HERE in bot_files/telegram_token.txt with your actual bot token.')\\n"
        code += f"    exit(1)\\n\\n"
        code += f"bot = telebot.TeleBot(TOKEN)\\n\\n"

        start_config = self.features.get('start', "Hello!")
        if isinstance(start_config, dict):
            start_message_text = start_config.get('text', 'Default welcome message.')
            start_image_url = start_config.get('image_url')
            code += f"START_MESSAGE_TEXT = {json.dumps(start_message_text)}\\n"
            if start_image_url:
                code += f"START_IMAGE_URL = {json.dumps(start_image_url)}\\n"
            else:
                code += f"START_IMAGE_URL = None\\n"
        else:
            code += f"START_MESSAGE_TEXT = {json.dumps(str(start_config))}\\n"
            code += f"START_IMAGE_URL = None\\n"
        help_message = self.features.get('help', 'This is a general help message.')
        code += f"HELP_MESSAGE = {json.dumps(help_message)}\\n\\n"
        
        # Main keyboard generation
        if "main_keyboard" in self.features:
            keyboard_config = self.features["main_keyboard"]
            code += f"def create_main_keyboard():\\n"
            code += f"    markup = types.ReplyKeyboardMarkup(resize_keyboard={keyboard_config.get('resize', True)}, one_time_keyboard=False, selective=False)\\n"
            for button in keyboard_config.get("buttons", []):
                code += f"    markup.add(types.KeyboardButton({json.dumps(button['text'])}))\\n"
            code += f"    return markup\\n\\n"
            code += f"MAIN_KEYBOARD = create_main_keyboard()\\n\\n" # Store keyboard for easy access
        else:
            code += f"MAIN_KEYBOARD = None\\n\\n"

        # Start command handler
        code += f"@bot.message_handler(commands=['start'])\\n"
        code += f"def send_welcome(message):\\n"
        code += f"    if START_IMAGE_URL:\\n"
        code += f"        bot.send_photo(message.chat.id, START_IMAGE_URL, caption=START_MESSAGE_TEXT, reply_markup=MAIN_KEYBOARD)\\n"
        code += f"    else:\\n"
        code += f"        bot.send_message(message.chat.id, START_MESSAGE_TEXT, reply_markup=MAIN_KEYBOARD)\\n\\n"

        # Help command handler
        code += f"@bot.message_handler(commands=['help'])\\n"
        code += f"def send_help(message):\\n"
        code += f"    bot.send_message(message.chat.id, HELP_MESSAGE, reply_markup=MAIN_KEYBOARD)\\n\\n"

        # Custom commands
        if "commands" in self.features:
            for command in self.features["commands"]:
                command_name = command["name"].replace("/", "") # Remove leading slash for function name
                response_text = command["response"]
                code += f"@bot.message_handler(commands=['{command_name}'])\\n"
                code += f"def handle_{command_name}(message):\\n"
                # Handle '{params}' placeholder for commands like addtask
                if '{params}' in response_text:
                    code += f"    try:\\n"
                    code += f"        params = message.text.split(maxsplit=1)[1].strip()\\n"
                    code += f"        response = {json.dumps(response_text)}.replace('{{params}}', params)\\n"
                    code += f"    except IndexError:\\n"
                    code += f"        response = 'Please provide parameters for the command.'\\n"
                    code += f"    bot.send_message(message.chat.id, response, reply_markup=MAIN_KEYBOARD)\\n\\n"
                else:
                    code += f"    bot.send_message(message.chat.id, {json.dumps(response_text)}, reply_markup=MAIN_KEYBOARD)\\n\\n"

        # Generic message handler (for buttons or other text)
        code += f"@bot.message_handler(func=lambda message: True)\\n"
        code += f"def echo_all(message):\\n"
        code += f"    # This handler can be customized for general text responses or button presses\\n"
        code += f"    # For now, it just echoes the message or handles specific button texts\\n"
        
        if "main_keyboard" in self.features:
            code += f"    handled_by_keyboard = False\\n"
            for button in keyboard_config.get("buttons", []):
                button_text = button['text']
                response_for_button = button.get('response', f"You pressed {button_text}")
                # Ensure correct escaping for comparison in Python code
                escaped_button_text = json.dumps(button_text)
                escaped_response_text = json.dumps(response_for_button)
                code += f"    if message.text == {escaped_button_text}:\\n"
                code += f"        bot.send_message(message.chat.id, {escaped_response_text}, reply_markup=MAIN_KEYBOARD)\\n"
                code += f"        handled_by_keyboard = True\\n"
            code += f"    if not handled_by_keyboard and message.text.startswith('/'):\\n"
            code += f"        bot.send_message(message.chat.id, 'Unknown command. Type /help for available commands.', reply_markup=MAIN_KEYBOARD)\\n"
            code += f"    elif not handled_by_keyboard:\\n"
            code += f"        bot.send_message(message.chat.id, 'I received: ' + message.text, reply_markup=MAIN_KEYBOARD)\\n"
        else:
            code += f"    # Default echo if no keyboard is present\\n"
            code += f"    bot.send_message(message.chat.id, 'I received: ' + message.text)\\n"

        code += f"print('Bot polling started.')\\n"
        code += f"bot.infinity_polling()\\n"
        
        return code
        """)

if not os.path.exists("eco_config_handler.py"):
    with open("eco_config_handler.py", "w", encoding="utf-8") as f:
        f.write("""
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich import box
import os
import time
def manage_eco_template_config(features_ref, console_ref, save_features_func, recursive_replace_func):
    console_ref.print("[bold yellow]Placeholder: Eco Config Handler Module Loaded.[/]")
    console_ref.print("[bold yellow]This is where you would manage Eco template settings.[/]")
    console_ref.input("[bold yellow]Press Enter to return from placeholder eco_config_handler...[/]")
""")

if not os.path.exists("todo_config_handler.py"):
    with open("todo_config_handler.py", "w", encoding="utf-8") as f:
        f.write("""
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich import box
import os
import time
def manage_todo_template_config(features_ref, console_ref, save_features_func, recursive_replace_func):
    console_ref.print("[bold yellow]Placeholder: ToDo Config Handler Module Loaded.[/]")
    console_ref.print("[bold yellow]This is where you would manage ToDo template settings (e.g., adding/removing tasks).[/]")
    console_ref.input("[bold yellow]Press Enter to return from placeholder todo_config_handler...[/]")
""")


def excel_to_json(filepath):
    try:
        df = pd.read_excel(filepath, engine="openpyxl")
        result = df.to_dict(orient="records")
        return result
    except Exception as e:
        console.print(f"❌ Error reading Excel file: {e}")
        return []


def open_file_dialog(title="Select file", filetypes=None):
    root = Tk()
    root.withdraw()
    if filetypes is None:
        filetypes = [("Excel files", "*.xlsx *.xls")]
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return file_path


def get_session_response():
    session_data = None
    use_session = (
        console.input("[bold magenta]❓ Use a session for reply? (yes/no): [/]")
        .strip()
        .lower()
    )
    if use_session == "yes":
        if not os.path.exists(SESSIONS_FILE):
            console.print("[bold red]⚠️ No sessions file found![/]")
        else:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                sessions = json.load(f)
            if sessions:
                console.print("[bold cyan]Available sessions:[/]")
                for idx, sess in enumerate(sessions.keys(), 1):
                    console.print(f"    [yellow]{idx}.[/] {sess}")
                try:
                    sess_choice = int(
                        console.input(
                            "[bold magenta]👉 Choose session (1-{}): [/]".format(
                                len(sessions)
                            )
                        )
                    )
                    if 1 <= sess_choice <= len(sessions):
                        chosen_session = list(sessions.keys())[sess_choice - 1]
                        session_data = sessions[chosen_session]
                        console.print(
                            f"[bold green]✅ Using session: {chosen_session}[/]"
                        )
                    else:
                        console.print("[bold red]⚠️ Invalid selection![/]")
                except ValueError:
                    console.print(
                        "[bold red]⚠️ Invalid input. Please enter a number.[/]"
                    )
            else:
                console.print("[bold blue] No sessions available[/]")
    return session_data


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def initialize_user_bot():
    global features
    default_config = {
        "start": "👋 Welcome! This is your Telegram bot.",
        "help": "Type /help for assistance.",
        "commands": [],
    }

    if not os.path.exists(USER_BOT_JSON):
        features = default_config
        save_features_to_json(features, USER_BOT_JSON)
    else:
        loaded_features = load_features_from_json(USER_BOT_JSON)
        if isinstance(loaded_features, dict):
            features = loaded_features
            for key in default_config:
                if key not in features:
                    features[key] = default_config[key]
        else:
            features = default_config
            save_features_to_json(features, USER_BOT_JSON)


def save_features_to_json(data, File="user_bot.json"):
    try:
        if os.path.exists(File):
            shutil.copyfile(File, f"{File}.bak")
            console.print(
                f"[bold blue]ℹ️ Created a backup of the previous configuration (`{File}.bak`).[/]"
            )
        with open(File, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        console.print(f"[bold green]✅ Configuration saved to `{File}`![/]")
    except Exception as e:
        console.print(f"[bold red]❌ Error saving configuration: {str(e)}[/]")


def load_features_from_json(File=""):
    default_config = {
        "start": "👋 Welcome! This is your Telegram bot.",
        "help": "Type /help for assistance.",
        "commands": [],
    }

    try:
        with open(File, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return default_config
            return data
    except FileNotFoundError:
        console.print(
            f"[bold yellow]⚠️ `{File}` not found. Initializing with default config.[/]"
        )
        return default_config
    except json.JSONDecodeError:
        console.print(
            f"[bold red]❌ Error decoding `{File}`. File might be corrupted. Using default config.[/]"
        )
        return default_config
    except Exception as e:
        console.print(
            f"[bold red]❌ Error loading `{File}`: {str(e)}. Using default config.[/]"
        )
        return default_config


def handle_add_start():
    global features
    current_start = features.get("start")
    current_start_text = ""
    if isinstance(current_start, dict):
        current_start_text = current_start.get("text", "")
    elif isinstance(current_start, str):
        current_start_text = current_start
    console.print(
        f"[cyan]Current /start message text: {current_start_text if current_start_text else 'Not set'}[/]"
    )
    start_message_text = console.input(
        "[bold magenta]Enter new welcome message text for /start: [/]"
    ).strip()
    if start_message_text:
        if isinstance(features.get("start"), dict):
            features["start"]["text"] = start_message_text
        else:
            features["start"] = start_message_text
        save_features_to_json(features, USER_BOT_JSON)
        console.print("[bold green]✅ /start command updated![/]")
    else:
        console.print(
            "[bold yellow]⚠️ Start message text cannot be empty. No changes made.[/]"
        )
    console.input("[bold yellow]Press Enter to continue...[/]")


def handle_add_help():
    global features
    console.print(f"[cyan]Current /help message: {features.get('help', 'Not set')}[/]")
    help_message = console.input(
        "[bold magenta]Enter new help message for /help: [/]"
    ).strip()
    if help_message:
        features["help"] = help_message
        save_features_to_json(features, USER_BOT_JSON)
        console.print("[bold green]✅ /help command updated![/]")
    else:
        console.print(
            "[bold yellow]⚠️ Help message cannot be empty. No changes made.[/]"
        )
    console.input("[bold yellow]Press Enter to continue...[/]")


def _recursive_replace(item, old_value, new_value):
    if isinstance(item, dict):
        return {k: _recursive_replace(v, old_value, new_value) for k, v in item.items()}
    elif isinstance(item, list):
        return [_recursive_replace(elem, old_value, new_value) for elem in item]
    elif isinstance(item, str):
        return item.replace(old_value, new_value)
    return item


def handle_template():
    global features
    clear_terminal()
    warning_message = Panel(
        Align.center(
            "[bold yellow]IMPORTANT[/]\n\n"
            "Selecting a template will [underline]overwrite your current `user_bot.json` configuration[/].\n"
            "All previous settings will be replaced by the template's defaults."
        ),
        title="[bold red]Template Selection Warning[/]",
        border_style="red",
        padding=(1, 1),
        expand=False,
    )
    console.print(Align.center(warning_message))
    console.print("\n")
    templates_master_config = {
        "Eco": {
            "description": "An e-commerce bot template. Asks for shop name.",
            "source_file": ECO_TEMPLATE_FILENAME,
            "placeholder_to_replace": "EcoStore",
        },
        "ToDo": {
            "description": "A simple ToDo list bot template.",
            "inline_data": {
                "template_name": "ToDo",
                "active_template": "ToDo List Bot",
                "start": "📝 Welcome to your ToDo Bot! Let's get organized.",
                "help": "Available commands:\n/addtask <task> - Add a new task\n/viewtasks - View your tasks",
                "commands": [
                    {"name": "addtask", "response": "✅ Task '{params}' added!"},
                    {
                        "name": "viewtasks",
                        "response": "📋 Your tasks:\n1. Buy groceries\n2. Finish report",
                    },
                ],
                "main_keyboard": {
                    "buttons": [
                        {"text": "/addtask", "response": "/addtask"},
                        {"text": "/viewtasks", "response": "/viewtasks"},
                    ],
                    "resize": True,
                    "persistent": True,
                },
            },
        },
    }
    eco_config = templates_master_config["Eco"]
    eco_path = eco_config.get("source_file")

    if eco_path and not os.path.exists(eco_path):
        console.print(f"[⚠️] '{eco_path}' not found! Creating default file...")
        with open(eco_path, "w", encoding="utf-8") as f:
            f.write("")
        console.print(f"[✅] '{eco_path}' created with default content.")
    console.print("[bold cyan]📋 Available Templates:[/]")
    template_names_list = list(templates_master_config.keys())
    for idx, name in enumerate(template_names_list, 1):
        console.print(
            f"    [yellow]{idx}.[/] {name} - {templates_master_config[name]['description']}"
        )
    try:
        choice_input = console.input(
            f"[bold magenta]👉 Select template (1-{len(template_names_list)} or 0 to cancel): [/]"
        ).strip()
        if not choice_input:
            console.print("[bold yellow]ℹ️ Template selection cancelled (no input).[/]")
            console.input("[bold yellow]Press Enter to continue...[/]")
            return
        choice = int(choice_input)
        if choice == 0:
            console.print("[bold yellow]ℹ️ Template selection cancelled by user.[/]")
        elif 1 <= choice <= len(template_names_list):
            selected_template_key = template_names_list[choice - 1]
            template_details = templates_master_config[selected_template_key]
            console.print(
                f"[bold blue]You selected the '{selected_template_key}' template.[/]"
            )
            confirm = (
                console.input(
                    f"[bold red]❓ Are you sure you want to apply the '{selected_template_key}' template? "
                    f"This will ERASE your current `user_bot.json`. (yes/no): [/]"
                )
                .strip()
                .lower()
            )
            if confirm == "yes":
                    if eco_path and not os.path.exists(eco_path):
                        console.print(f"[⚠️] '{eco_path}' not found! Creating default file...")
                        with open(eco_path, "w", encoding="utf-8") as f:
                            json.dump({}, f, ensure_ascii=False, indent=4)
                        console.print(f"[✅] '{eco_path}' created as an empty JSON object.")

                    new_bot_config = None
                    applied_template_name_for_display = selected_template_key

                    if "source_file" in template_details:
                        template_file = template_details["source_file"]
                        placeholder = template_details["placeholder_to_replace"]
                        user_shop_name = console.input(
                            f"[bold magenta]Enter the name for your {selected_template_key} shop (e.g., 'My Awesome Store').\n"
                            f"This will replace '{placeholder}' in the template. [Default: Your New Shop]: [/]"
                        ).strip()
                        effective_shop_name = user_shop_name if user_shop_name else "Your New Shop"
                        applied_template_name_for_display = effective_shop_name

                        try:
                            # 👇 اینجا امنش می‌کنیم
                            if not os.path.exists(template_file):
                                raise FileNotFoundError(f"{template_file} not found.")

                            with open(template_file, "r", encoding="utf-8") as f:
                                try:
                                    template_json_content = json.load(f)
                                except json.JSONDecodeError:
                                    console.print(
                                        f"[yellow]⚠️ Warning: File '{template_file}' is empty or malformed. Using default empty object.[/]"
                                    )
                                    template_json_content = {}

                            new_bot_config = _recursive_replace(
                                template_json_content, placeholder, effective_shop_name
                            )
                            new_bot_config["template_name"] = selected_template_key
                            new_bot_config["active_template"] = effective_shop_name

                        except FileNotFoundError:
                            console.print(f"[bold red]❌ Error: Template file '{template_file}' not found.[/]")
                            console.input("[bold yellow]Press Enter to continue...[/]")
                            return

                        except Exception as e:
                            console.print(f"[bold red]❌ Error processing template file: {str(e)}[/]")
                            console.input("[bold yellow]Press Enter to continue...[/]")
                            return

                    elif "inline_data" in template_details:
                        new_bot_config = template_details["inline_data"].copy()

                    if new_bot_config is not None:
                        features = new_bot_config
                        save_features_to_json(features, USER_BOT_JSON)
                        console.print(
                            f"[bold green]✅ Template '{selected_template_key}' (Name: '{applied_template_name_for_display}') applied! Configuration saved.[/]"
                        )
                    else:
                        console.print(f"[bold red]❌ Failed to load or process template '{selected_template_key}'.[/]")
            else:
                console.print("[bold yellow]ℹ️ Template application cancelled.[/]")
    except Exception as e:
            console.print(f"[red]❌ Failed to generate handler: {e}[/]")


def handle_code_filtering(code_content, summary_type):
    if summary_type != "short":
        return code_content
    filtered_lines = []
    skip_comment_block = False
    for line in code_content.split("\n"):
        if "# ----------- TEMPLATE PROCESSING FUNCTIONS -----------" in line:
            skip_comment_block = True
            continue
        if "# ----------- END TEMPLATE PROCESSING -----------" in line:
            skip_comment_block = False
            continue
        filtered_lines.append(line)
    return "\n".join(filtered_lines)


def handle_explain():
    clear_terminal()
    console.print(
        Align.center(
            Panel.fit(
                "[bold cyan]🤖 AI Code Explainer[/]",
                border_style="cyan",
                padding=(1, 1),
            )
        )
    )
    if not features:
        console.print(
            Align.center(
                Panel.fit(
                    "[bold red]⚠️ No configuration! Load a template or set up features first.[/]",
                    border_style="red",
                    padding=(1, 1),
                )
            )
        )
        console.input("[bold yellow]Press Enter to continue...[/]")
        return
    try:
        generator = BotCodeGenerator(features)
        bot_code = generator.generate_code()
        success, saved_path = save_bot_code(bot_code)
    except Exception as e:
        console.print(
            Align.center(
                Panel.fit(
                    f"[bold red]❌ Error generating/saving code: {str(e)}[/]",
                    border_style="red",
                    padding=(1, 1),
                )
            )
        )
        console.input("[bold yellow]Press Enter to continue...[/]")
        return
    if not success:
        console.print(
            Align.center(
                Panel.fit(
                    f"[red]❌ Error saving code: {saved_path}[/]",
                    title="Save Error",
                    border_style="red",
                    padding=(1, 1),
                )
            )
        )
        console.input("[bold yellow]Press Enter to continue...[/]")
        return
    try:
        with open(saved_path, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception as e:
        console.print(
            Align.center(
                Panel.fit(
                    f"[bold red]❌ Error reading code ('{saved_path}'): {str(e)}[/]",
                    border_style="red",
                    padding=(1, 1),
                )
            )
        )
        console.input("[bold yellow]Press Enter to continue...[/]")
        return
    console.print("\n[bold magenta]📏 Summary Type Selection[/]", justify="center")
    summary_type = (
        console.input("[bold cyan](short/complete) [short]: [/]").strip().lower()
        or "short"
    )
    code_to_analyze = handle_code_filtering(code_content, summary_type)
    base_prompt = "Analyze this Python Telegram bot code and provide"
    prompt_details = {
        "complete": "a detailed technical analysis: 1. Commands 🤖. 2. Architecture 🏗️. 3. Interaction 💬. 4. Session Mgmt 💾. 5. Error Handling 🛡️. 6. Security 🔒. 7. Improvements 💡. 8. Dependencies 📚. Use emojis.",
        "short": "a concise overview: 1. Main purpose ✨. 2. Interaction style 🗣️. 3. Available commands 📋. Short answer, use emojis.",
    }
    prompt = (
        f"{base_prompt} {prompt_details.get(summary_type, prompt_details['short'])}"
    )
    prompt += f"\n\n[Configuration Details]\n{json.dumps(features, indent=2)}\n\n[Source Code]\n```python\n{code_to_analyze}\n```\nFormat with headers (## Title) and bullets."
    try:
        console.print("\n[bold yellow]⏳ Generating analysis with Gemini AI...[/]")
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        summary_text = (
            response.text.replace("**", "[bold]")
            if response.text
            else "[bold red]❌ No summary generated.[/]"
        )
        if not response.text and hasattr(response, "prompt_feedback"):
            summary_text += f"\nFeedback: {response.prompt_feedback}"
    except Exception as e:
        summary_text = f"[bold red]❌ Gemini AI Error: {str(e)}[/]"
    console.print(
        Align.center(
            Panel(
                f"[not bold white]{summary_text}[/]",
                title="[bold green]✨ Bot Analysis Report ✨[/]",
                border_style="blue",
                width=min(console.width - 4, 80),
                padding=(1, 1),
            )
        )
    )
    console.input("[bold yellow]Press Enter to continue...[/]")


def handle_gui():
    try:
        console.print("[bold cyan]🖥️ Launching GUI...[/]")
        subprocess.run([sys.executable, "telegram_bot_maker_gui.py"], check=True)
        console.print("[bold green]✅ GUI process finished.[/]")
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]❌ GUI Error: {e}[/]")
    except FileNotFoundError:
        console.print("[bold red]❌ GUI file not found.[/]")
    console.input("[bold yellow]Press Enter to continue...[/]")


def handle_run_bot():
    if not os.path.exists(BOT_SCRIPT_FILENAME):
        console.print(
            Panel(
                f"[bold red]❌ Error: Bot script '{BOT_SCRIPT_FILENAME}' not found.\n"
                f"Please generate the code first using the '/generate' command.[/]",
                title="[red]File Not Found[/]",
                border_style="red",
            )
        )
        console.input("[bold yellow]Press Enter to continue...[/]")
        return

    try:
        console.print(
            Panel(
                "[bold cyan]🚀 Attempting to start the bot script...\n"
                "A new terminal window should open to run the bot.[/]",
                title="[cyan]Running Bot[/]",
                border_style="cyan",
            )
        )

        abs_path = os.path.abspath(BOT_SCRIPT_FILENAME)

        if sys.platform == "win32":
            subprocess.Popen(f'start cmd /k python "{abs_path}"', shell=True)

        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Terminal", abs_path])

        else:  # Linux systems
            terminals = [
                "gnome-terminal",
                "konsole",
                "xfce4-terminal",
                "lxterminal",
                "xterm",
            ]
            for term in terminals:
                try:
                    subprocess.Popen([term, "--", "python3", abs_path])
                    return
                except FileNotFoundError:
                    continue
            console.print(
                Panel(
                    "[bold red]❌ Could not find a supported terminal automatically.[/]\n"
                    "Please run the script manually:\n\n"
                    f"[bold white]python3 {BOT_SCRIPT_FILENAME}[/]",
                    title="[red]Terminal Error[/]",
                    border_style="red",
                )
            )
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]❌ Failed to run bot script: {e}[/]",
                title="[red]Execution Error[/]",
                border_style="red",
            )
        )

    console.input("[bold yellow]Press Enter to continue...[/]")


def save_bot_code(code, filename=BOT_SCRIPT_FILENAME):
    try:
        dir_name = os.path.dirname(filename)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        return True, os.path.abspath(filename)
    except Exception as e:
        return False, str(e)


def handle_bot_code_generation():
    console.print("\n[bold yellow]🔄 Generating bot source code...[/]")
    if not features:
        console.print(
            Panel(
                "[bold red]⚠️ No configuration loaded. Cannot generate code. Please use '/template' or configure features first.[/]",
                title="[red]Error[/]",
                border_style="red",
            )
        )
        console.input("[bold yellow]Press Enter to continue...[/]")
        return
    try:
        generator = BotCodeGenerator(features)
        bot_code = generator.generate_code()
        success, res_msg = save_bot_code(bot_code)
        if success:
            console.print(
                Panel(
                    f"[green]✅ Bot code successfully saved to: [b]{res_msg}[/b]\n\nTo run your bot, execute:\n[white]python3 {os.path.basename(res_msg)}[/white]",
                    title="[green]Code Generation Complete[/]",
                    border_style="green",
                    padding=(1, 1),
                )
            )
        else:
            console.print(
                Panel(
                    f"[red]❌ Failed to save the bot code. Error: {res_msg}[/]",
                    title="[red]Save Error[/]",
                    border_style="red",
                    padding=(1, 1),
                )
            )
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]❌ An unexpected error occurred during code generation: {str(e)}[/]",
                title="[red]Generation Failed[/]",
                border_style="red",
                padding=(1, 1),
            )
        )
    console.input("[bold yellow]Press Enter to return to the main menu...[/]")


def handle_eco_config():
    try:
        console.print("[bold cyan]⚙️ Launching Eco Configurator (eco_python.py)...[/]")
        subprocess.run([sys.executable, "eco_python.py"], check=True)
        console.print("[bold green]✅ Eco Configurator process finished.[/]")
    except subprocess.CalledProcessError as e:
        console.print(
            f"[bold red]❌ Eco Configurator Error: The script exited with an error: {e}[/]"
        )
    except FileNotFoundError:
        console.print(
            "[bold red]❌ Script Not Found: The 'eco_python.py' file could not be found.[/]"
        )
    except Exception as e:
        console.print(f"[bold red]❌ An unexpected error occurred: {e}[/]")
    console.input("[bold yellow]Press Enter to return to the main menu...[/]")


def handle_todo_config():
    try:
        console.print("[bold cyan]⚙️ Launching ToDo Configurator (todo_python.py)...[/]")
        subprocess.run([sys.executable, "todo_python.py"], check=True)
        console.print("[bold green]✅ ToDo Configurator process finished.[/]")
    except subprocess.CalledProcessError as e:
        console.print(
            f"[bold red]❌ ToDo Configurator Error: The script exited with an error: {e}[/]"
        )
    except FileNotFoundError:
        console.print(
            "[bold red]❌ Script Not Found: The 'todo_python.py' file could not be found.[/]"
        )
    except Exception as e:
        console.print(f"[bold red]❌ An unexpected error occurred: {e}[/]")
    console.input("[bold yellow]Press Enter to return to the main menu...[/]")

def clear_history():
    files=[
        "eco_template.json",
        "todo_template.json",
        "user_bot.json",
        "user_bot.json.bak",
        "sessions.json",
        "user_source_code.py",
        
        ]
    for i in files:
        if i:
            try:
                os.remove(i)
            except:
                continue

    console.print("[bold green]✅ clear Configurator process finished.[/]")
    console.input("[bold yellow]Press Enter to continue...[/]")


def main():
    default_config = {
        "start": "👋 Welcome! This is your Telegram bot.",
        "help": "Type /help for assistance.",
        "commands": [],
    }

    if not os.path.exists(USER_BOT_JSON):
        with open(USER_BOT_JSON, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        console.print(
            f"[bold green]✅ Created new configuration file: {USER_BOT_JSON}[/]"
        )
    else:
        try:
            with open(USER_BOT_JSON, "r", encoding="utf-8") as f:
                existing_config = json.load(f)
                if not isinstance(existing_config, dict):
                    raise ValueError("Configuration is not a dictionary")

                for key in default_config:
                    if key not in existing_config:
                        existing_config[key] = default_config[key]

                with open(USER_BOT_JSON, "w", encoding="utf-8") as f:
                    json.dump(existing_config, f, indent=4)
        except (json.JSONDecodeError, ValueError) as e:
            console.print(f"[bold red]❌ Error in configuration file: {str(e)}[/]")
            console.print(
                "[yellow]⚠️ Recreating configuration file with default values[/]"
            )
            with open(USER_BOT_JSON, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4)

    while True:
        clear_terminal()
        initialize_user_bot()
        print_centered(IDEA_FLOW_ART, "\t\033[38;5;208m")

        eco_config_active = features.get("template_name") == "Eco"
        todo_config_active = features.get("template_name") == "ToDo"

        eco_config_item_details = None
        if eco_config_active:
            active_shop_name = features.get("active_template", "your Eco shop")
            eco_config_item_details = {
                "command_text": "/eco-config ",
                "description": f"Configure '{active_shop_name}' (Eco template).",
                "handler_key": "eco-config",
            }
            info_panel_text = (
                f" The '[bold cyan]{active_shop_name}[/]' (Eco Template) is active.\n"
                f"For template-specific settings (like Shop Name), please use the "
                f"'[bold yellow]/eco-config[/]' option shown in its own section below."
            )
            console.print(
                Align.center(
                    Panel(
                        info_panel_text,
                        title="[blue][b]Template Active[/b][/blue]",
                        border_style="blue",
                        padding=(1, 1),
                        expand=False,
                    )
                )
            )
            console.print()

        todo_config_item_details = None
        if todo_config_active:
            active_todo_name = features.get("active_template", "your ToDo List Bot")
            todo_config_item_details = {
                "command_text": "/todo-config ",
                "description": f"Configure '{active_todo_name}' (ToDo template).",
                "handler_key": "todo-config",
            }
            info_panel_text = (
                f" The '[bold cyan]{active_todo_name}[/]' (ToDo Template) is active.\n"
                f"For template-specific settings (like tasks), please use the "
                f"'[bold yellow]/todo-config[/]' option shown in its own section below."
            )
            console.print(
                Align.center(
                    Panel(
                        info_panel_text,
                        title="[blue][b]Template Active[/b][/blue]",
                        border_style="blue",
                        padding=(1, 1),
                        expand=False,
                    )
                )
            )
            console.print()

        all_actionable_items = []
        option_number = 1
        base_menu_items_config = [
            ("/start 🚀", "Edit welcome message."),
            ("/help ❓", "Configure help response."),
            ("/commands 💡", "Manage custom commands."),
            ("/generate 💾", "Export bot source code."),
            ("/sessions 👥", "Manage user sessions (Placeholder)."),
            ("/keyboard 💻", "Design custom keyboard.(but first /generate)"),
            ("/template 📋", "Apply a pre-built template."),
            ("/explain 🤖", "AI code explanation."),
            ("/run ⚡", "Run the generated bot."),
            ("/gui 🔗", "Open experimental GUI."),
            ("/clear 🚮", "clear history"),
        ]

        for cmd_txt, desc_txt in base_menu_items_config:
            all_actionable_items.append(
                {
                    "number_str": str(option_number),
                    "command_text": cmd_txt,
                    "description": desc_txt,
                    "handler_key": cmd_txt.split(" ")[0].replace("/", ""),
                }
            )
            option_number += 1

        if eco_config_active and eco_config_item_details:
            all_actionable_items.append(
                {"number_str": str(option_number), **eco_config_item_details}
            )
            option_number += 1

        if todo_config_active and todo_config_item_details:
            all_actionable_items.append(
                {"number_str": str(option_number), **todo_config_item_details}
            )
            option_number += 1

        all_actionable_items.append(
            {
                "number_str": str(option_number),
                "command_text": "/exit 🚪",
                "description": "Exit the application.",
                "handler_key": "exit",
            }
        )

        max_option = option_number
        current_console_width = console.width

        if eco_config_active and eco_config_item_details:
            eco_table_width = max(45, min(int(current_console_width * 0.75), 70))
            eco_config_table = Table(
                box=box.ROUNDED,
                show_edge=True,
                header_style="bold magenta",
                title="\n",
                border_style="blue",
                expand=False,
                padding=(0, 1),
                show_lines=True,
                show_header=False,
                width=eco_table_width,
            )
            eco_config_table.add_column(
                "Opt", style="cyan", no_wrap=True, justify="left", min_width=3, width=4
            )
            eco_config_table.add_column(
                "Command", style="yellow", min_width=18, width=20
            )
            eco_config_table.add_column("Description", style="white", overflow="fold")
            eco_item_for_display = next(
                item
                for item in all_actionable_items
                if item["handler_key"] == "eco-config"
            )
            eco_config_table.add_row(
                eco_item_for_display["number_str"] + ".",
                eco_item_for_display["command_text"],
                eco_item_for_display["description"],
            )
            console.print(Align.center(eco_config_table))
            console.print()

        if todo_config_active and todo_config_item_details:
            todo_table_width = max(45, min(int(current_console_width * 0.75), 70))
            todo_config_table = Table(
                box=box.ROUNDED,
                show_edge=True,
                header_style="bold magenta",
                title="\n",
                border_style="blue",
                expand=False,
                padding=(0, 1),
                show_lines=True,
                show_header=False,
                width=todo_table_width,
            )
            todo_config_table.add_column(
                "Opt", style="cyan", no_wrap=True, justify="left", min_width=3, width=4
            )
            todo_config_table.add_column(
                "Command", style="yellow", min_width=18, width=20
            )
            todo_config_table.add_column("Description", style="white", overflow="fold")
            todo_item_for_display = next(
                item
                for item in all_actionable_items
                if item["handler_key"] == "todo-config"
            )
            todo_config_table.add_row(
                todo_item_for_display["number_str"] + ".",
                todo_item_for_display["command_text"],
                todo_item_for_display["description"],
            )
            console.print(Align.center(todo_config_table))
            console.print()

        main_menu_table_width = max(55, min(int(current_console_width * 0.9), 80))
        main_menu_table = Table(
            box=box.SQUARE,
            show_edge=True,
            header_style="bold magenta",
            title="\n[bold green]Main Menu[/]",
            border_style="bright_blue",
            expand=False,
            padding=(0, 1),
            show_lines=True,
            width=main_menu_table_width,
        )
        main_menu_table.add_column(
            "Opt", style="cyan", no_wrap=True, justify="left", min_width=3, width=4
        )
        main_menu_table.add_column("Command", style="yellow", min_width=18, width=20)
        main_menu_table.add_column("Description", style="white", overflow="fold")
        for item in all_actionable_items:
            if (eco_config_active and item["handler_key"] == "eco-config") or (
                todo_config_active and item["handler_key"] == "todo-config"
            ):
                continue
            main_menu_table.add_row(
                item["number_str"] + ".", item["command_text"], item["description"]
            )
        console.print(Align.center(main_menu_table))
        console.print("\n")
        choice_input_str = console.input(
            f"[bold magenta]👉 Select option (1-{max_option}): [/]"
        ).strip()
        try:
            selected_handler_key = None
            if choice_input_str:
                for item in all_actionable_items:
                    if item["number_str"] == choice_input_str:
                        selected_handler_key = item["handler_key"]
                        break

            if selected_handler_key == "start":
                handle_add_start()
            elif selected_handler_key == "help":
                handle_add_help()
            elif selected_handler_key == "commands":
                custom_command()
            elif selected_handler_key == "generate":
                handle_bot_code_generation()
            elif selected_handler_key == "sessions":
                create_new_session()
                console.input("[yellow]Press Enter...[/]")
            elif selected_handler_key == "keyboard":
                try:
                    clear_terminal()
                    term_width = shutil.get_terminal_size().columns
                    panel_width = min(max(50, term_width // 2), term_width - 4)
                    handle_bot_code_generation()
                except Exception as e:
                    console.print(
                        Panel(
                            f"An error occurred: {e}",
                            title="ERROR",
                            border_style="red",
                            padding=(1, 1),
                        )
                    )
                    console.input("[yellow]Press Enter...[/]")
                    continue
                resize = (
                    console.input("[magenta]🤖 Auto-resize? (y/n) [y]:[/]").lower()
                    != "n"
                )
                persistent = (
                    console.input("[magenta]🔒 Persistent? (y/n) [n]:[/]").lower()
                    == "y"
                )
                btns = []
                idx = 1
                while True:
                    txt = console.input(
                        f"[cyan]🔘 Btn #{idx} ('done'/'cancel'):[/]"
                    ).strip()
                    if txt.lower() == "done":
                        break
                    if txt.lower() == "cancel":
                        btns = []
                        console.print("[red]Cancelled.[/]")
                        break
                    if not txt:
                        console.print("[yellow]Cannot be empty.[/]")
                        continue
                    btns.append({"text": txt, "response": txt})
                    console.print(f"[green]Added: '{txt}'[/]")
                    idx += 1
                if btns:
                    features["main_keyboard"] = {
                        "buttons": btns,
                        "resize": resize,
                        "persistent": persistent,
                    }
                    save_features_to_json(features, USER_BOT_JSON)
                    console.print("[green]Keyboard saved![/]")
                elif not (txt.lower() == "done" or txt.lower() == "cancel"):
                    console.print("[yellow]No buttons added.[/]")
                console.input("[yellow]Press Enter...[/]")
            elif selected_handler_key == "template":
                handle_template()
            elif selected_handler_key == "explain":
                handle_explain()
            elif selected_handler_key == "run":
                handle_run_bot()
            elif selected_handler_key == "gui":
                handle_gui()
            elif selected_handler_key == "clear":
                clear_history()
            elif selected_handler_key == "eco-config":
                handle_eco_config()
            elif selected_handler_key == "todo-config":
                handle_todo_config()
            elif selected_handler_key == "exit":
                console.print("[green]👋 Goodbye![/]")
                sys.exit(0)
            else:
                if choice_input_str:
                    console.print(f"[red]⚠️ Invalid option '{choice_input_str}'.[/]")
                    time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[red]🚫 Operation cancelled! Exiting.[/]")
            sys.exit(1)
        except ValueError:
            console.print("[red]⚠️ Invalid input (not a number).[/]")
            time.sleep(1.5)


if __name__ == "__main__":
    if not os.path.exists(TOKEN_FILE):
        os.makedirs(os.path.dirname(TOKEN_FILE) or "bot_files", exist_ok=True)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write("bot_files/telegram_token.txt")
        console.print(
            f"[yellow]⚠️ Token file '{TOKEN_FILE}' not found. Placeholder created.[/]"
        )
        console.print(f"[yellow]Edit with your Telegram Bot Token.[/]")
        time.sleep(2.5)

    if not os.path.exists(ECO_TEMPLATE_FILENAME):
        dummy_eco_template = {
            "template_name": "Eco",
            "template_description": "Dummy Eco Template for E-commerce Bot",
            "active_template": "EcoStore",
            "start": {
                "text": "Welcome to **EcoStore**!",
                "image_url": "https://example.com/default_eco_image.jpg",
            },
            "help": "Help for EcoStore: /products, /cart, etc.",
            "commands": [{"name": "products", "response": "Showing products..."}],
            "main_keyboard": {
                "buttons": [{"text": "🛍️ Products", "response": "/products"}],
                "resize": True,
                "persistent": False,
            },
        }
        with open(ECO_TEMPLATE_FILENAME, "w", encoding="utf-8") as f:
            json.dump(dummy_eco_template, f, indent=4)
        console.print(
            f"[yellow]⚠️ Dummy '{ECO_TEMPLATE_FILENAME}' created for testing purposes.[/]"
        )
        time.sleep(1)

    if not os.path.exists("eco_python.py"):
        with open("eco_python.py", "w", encoding="utf-8") as f:
            f.write("""
from rich.console import Console
console = Console()
console.print("[bold green]Eco Python Script Running![/]")
console.print("This is the placeholder for the Eco template configuration script.")
console.input("[bold yellow]Press Enter to return...[/]")
""")

    if not os.path.exists(TODO_TEMPLATE_FILENAME):
        dummy_todo_template = {
            "template_name": "ToDo",
            "active_template": "ToDo List Bot",
            "start": "📝 Welcome to your ToDo Bot! Let's get organized.",
            "help": "Available commands:\n/addtask <task> - Add a new task\n/viewtasks - View your tasks",
            "commands": [
                {"name": "addtask", "response": "✅ Task '{params}' added!"},
                {
                    "name": "viewtasks",
                    "response": "📋 Your tasks:\n1. Buy groceries\n2. Finish report",
                },
            ],
            "main_keyboard": {
                "buttons": [
                    {"text": "🛍️ Products", "response": "/products"},
                    {"text": "📋 View Tasks", "response": "/viewtasks"},
                ],
                "resize": True,
                "persistent": True,
            },
        }
        with open(TODO_TEMPLATE_FILENAME, "w", encoding="utf-8") as f:
            json.dump(dummy_todo_template, f, indent=4)
        console.print(
            f"[yellow]⚠️ Dummy '{TODO_TEMPLATE_FILENAME}' created for reference (inline data is used for ToDo).[/]"
        )
        time.sleep(1)

    if not os.path.exists("todo_python.py"):
        with open("todo_python.py", "w", encoding="utf-8") as f:
            f.write("""
from rich.console import Console
console = Console()
console.print("[bold green]ToDo Python Script Running![/]")
console.print("This is the placeholder for the ToDo template configuration script.")
console.input("[bold yellow]Press Enter to return...[/]")
""")

    main()
