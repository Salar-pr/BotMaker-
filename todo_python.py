import os
import time
import json
import logging
import re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich import box

BOT_CONFIG_FILEPATH = "user_bot.json"
TODO_TEMPLATE_FILENAME = "todo_template.json"
BOT_TOKEN_FILE = "bot_files/telegram_token.txt"
GENERATED_BOT_SCRIPT_FILENAME = "user_source_code.py"

console = Console()


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def save_features_to_json(data, file_path=BOT_CONFIG_FILEPATH):
    """Saves the bot's features (configuration) to a JSON file."""
    try:
        if os.path.exists(file_path):
            shutil.copyfile(file_path, f"{file_path}.bak")
            console.print(
                f"[bold blue]ℹ️ Created a backup of the previous configuration (`{file_path}.bak`).[/]"
            )

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        console.print(f"[bold green]✅ Configuration saved to `{file_path}`![/]")
    except Exception as e:
        console.print(f"[bold red]❌ Error saving configuration: {str(e)}[/]")


def load_features_from_json(file_path=BOT_CONFIG_FILEPATH):
    """Loads the bot's features (configuration) from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(
            f"[bold yellow]⚠️ `{file_path}` not found. Initializing with a default welcome message.[/]"
        )
        return {"start": "👋 Welcome! This is your Telegram bot."}
    except json.JSONDecodeError:
        console.print(
            f"[bold red]❌ Error decoding `{file_path}`. File might be corrupted. Initializing with default.[/]"
        )
        return {"start": "👋 Welcome! This is your Telegram bot."}
    except Exception as e:
        console.print(f"[bold red]❌ Error loading `{file_path}`: {str(e)}[/]")
        return {}


def _recursive_replace(item, old_value, new_value):
    """Recursively replaces old_value with new_value in a dictionary or list."""
    if isinstance(item, dict):
        return {k: _recursive_replace(v, old_value, new_value) for k, v in item.items()}
    elif isinstance(item, list):
        return [_recursive_replace(elem, old_value, new_value) for elem in item]
    elif isinstance(item, str):
        return item.replace(old_value, new_value)
    return item


class ToDoBotCodeGenerator:
    """
    Generates the Telegram bot script for a To-Do list manager
    based on a provided JSON configuration.
    """

    def __init__(self, config_data, console_ref):
        self.config = config_data
        self.console = console_ref
        self.template_name = self.config.get("template_name", "ToDoManager")
        self.active_template = self.config.get("active_template", "ToDoManager")
        self.actual_bot_token = self._load_bot_token()

        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )
        self.logger = logging.getLogger("ToDoBotGenerator")

    def _load_bot_token(self):
        """Attempts to load the bot token from a file."""
        try:
            token_dir = os.path.dirname(BOT_TOKEN_FILE)
            if token_dir and not os.path.exists(token_dir):
                os.makedirs(token_dir, exist_ok=True)
                self.console.print(
                    f"[yellow]ℹ️ Created directory for token file: {token_dir}[/yellow]"
                )

            with open(BOT_TOKEN_FILE, "r", encoding="utf-8") as f:
                token = f.read().strip()
            if not token:
                self.console.print(
                    f"[yellow]⚠️ Token file '{BOT_TOKEN_FILE}' found but is empty.[/yellow]"
                )
                return None
            return token
        except FileNotFoundError:
            self.console.print(
                f"[red]❌ Token file '{BOT_TOKEN_FILE}' not found. "
                "The generated script will use a placeholder token. "
                "Please create this file and add your bot token.[/red]"
            )
            return None
        except Exception as e:
            self.console.print(
                f"[red]❌ Error reading token from '{BOT_TOKEN_FILE}': {e}. "
                "Generated script will use a placeholder.[/red]"
            )
            return None

    def _generate_imports(self):
        return """import logging
import os
import json
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.constants import ParseMode
"""

    def _generate_bot_init(self):
        token_to_embed = (
            self.actual_bot_token
            if self.actual_bot_token
            else "YOUR_BOT_TOKEN_HERE_UPDATE_THIS_OR_ENSURE_GENERATOR_CAN_READ_TOKEN_FILE"
        )

        return f"""
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "{token_to_embed}"
BOT_NAME = "{self.active_template.replace('"', '\\"')}"

# In-memory storage for tasks. For a production bot, use a database or file.
# Format: {{user_id: [{{'id': 1, 'task': 'Task description', 'completed': False}}, ...]}}
USER_TASKS = {{}}

# Conversation states for adding, completing, and deleting tasks
ADD_TASK, COMPLETE_TASK, DELETE_TASK = range(3)

if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE_UPDATE_THIS_OR_ENSURE_GENERATOR_CAN_READ_TOKEN_FILE":
    logger.critical(
        "FATAL: Telegram Bot Token is a placeholder. "
        "Please replace it with your actual bot token in this script, "
        "or ensure the generator script can read it from '{BOT_TOKEN_FILE}' upon generation."
    )
"""

    def _generate_start_handler(self):
        start_config = self.config.get("start", {})
        start_text = start_config.get(
            "text", f"Welcome to **{{BOT_NAME}}**! Organize your tasks efficiently."
        )
        image_url = start_config.get("image_url", "")

        kb_config = self.config.get("main_keyboard", {})
        buttons_config = kb_config.get("buttons", [])

        keyboard_layout_str = "    keyboard_buttons = [\n"
        if buttons_config:
            current_row_buttons = []
            for i, btn_data in enumerate(buttons_config):
                btn_text_py = btn_data.get("text", f"Button {i + 1}").replace(
                    '"', '\\"'
                )
                current_row_buttons.append(f'KeyboardButton("{btn_text_py}")')
                if len(current_row_buttons) == 2 or i == len(buttons_config) - 1:
                    keyboard_layout_str += (
                        f"        [{', '.join(current_row_buttons)}],\n"
                    )
                    current_row_buttons = []
        else:
            keyboard_layout_str += "    # No keyboard buttons configured.\n"
        keyboard_layout_str += "    ]\n"

        keyboard_layout_str += f"""
    reply_markup = ReplyKeyboardMarkup(
        keyboard_buttons,
        resize_keyboard={kb_config.get("resize", True)},
        is_persistent={kb_config.get("persistent", False)}
    )
"""

        handler_code = f"""
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in USER_TASKS:
        USER_TASKS[user_id] = []
    
    start_message = f\"\"\"{start_text.replace("{BOT_NAME}", BOT_NAME)}\"\"\"
    image_url = "{image_url}"

{keyboard_layout_str}

    if image_url:
        try:
            await update.message.reply_photo(photo=image_url)
        except Exception as e:
            logger.error(f"Error sending start photo: {{e}}")

    await update.message.reply_text(start_message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
"""
        return handler_code

    def _generate_help_handler(self):
        help_text = self.config.get(
            "help", "Help for **ToDoManager**: Use /tasks, /add, /complete, /delete"
        )
        return f"""
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_message = f\"\"\"{help_text.replace("{BOT_NAME}", self.active_template)}\"\"\"
    await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
"""

    def _generate_tasks_handler(self):
        return """
async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    tasks = USER_TASKS.get(user_id, [])

    if not tasks:
        await update.message.reply_text("You have no tasks yet! Use /add to add a new task.")
        return

    response_text = "*Your Current Tasks:*\n\n"
    for task_item in tasks:
        status = "✅" if task_item.get("completed", False) else "⏳"
        response_text += f"{status} ID: `{task_item['id']}` - {task_item['task']}\\n"
    
    await update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
"""

    def _generate_add_task_conversation(self):
        add_command_config = next(
            (
                cmd
                for cmd in self.config.get("commands", [])
                if cmd.get("name") == "add"
            ),
            {},
        )
        add_prompt = add_command_config.get(
            "response", "Please enter the task you want to add."
        )

        return f"""
# --- Add Task Conversation ---
async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("{add_prompt}")
    return ADD_TASK

async def add_receive_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    task_description = update.message.text.strip()

    if not task_description:
        await update.message.reply_text("Task description cannot be empty. Please try again or /cancel.")
        return ADD_TASK

    if user_id not in USER_TASKS:
        USER_TASKS[user_id] = []

    new_task_id = 1
    if USER_TASKS[user_id]:
        new_task_id = max(task['id'] for task in USER_TASKS[user_id]) + 1
    
    USER_TASKS[user_id].append({{'id': new_task_id, 'task': task_description, 'completed': False}})
    await update.message.reply_text(f"Task '{{task_description}}' (ID: {{new_task_id}}) added! Use /tasks to view.")
    return ConversationHandler.END

async def add_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Adding task has been cancelled.")
    return ConversationHandler.END
"""

    def _generate_complete_task_conversation(self):
        complete_command_config = next(
            (
                cmd
                for cmd in self.config.get("commands", [])
                if cmd.get("name") == "complete"
            ),
            {},
        )
        complete_prompt = complete_command_config.get(
            "response", "Enter the task ID to mark as completed."
        )

        return f"""
# --- Complete Task Conversation ---
async def complete_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("{complete_prompt}")
    return COMPLETE_TASK

async def complete_receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    task_id_str = update.message.text.strip()

    if not USER_TASKS.get(user_id):
        await update.message.reply_text("You have no tasks to complete.")
        return ConversationHandler.END

    try:
        task_id = int(task_id_str)
    except ValueError:
        await update.message.reply_text("Invalid ID. Please enter a number or /cancel.")
        return COMPLETE_TASK

    found = False
    for task_item in USER_TASKS[user_id]:
        if task_item['id'] == task_id:
            task_item['completed'] = True
            await update.message.reply_text(f"Task '{{task_item['task']}}' (ID: {{task_id}}) marked as completed! ✅")
            found = True
            break
    
    if not found:
        await update.message.reply_text(f"Task with ID {{task_id}} not found. Use /tasks to see your tasks.")

    return ConversationHandler.END

async def complete_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Completing task has been cancelled.")
    return ConversationHandler.END
"""

    def _generate_delete_task_conversation(self):
        delete_command_config = next(
            (
                cmd
                for cmd in self.config.get("commands", [])
                if cmd.get("name") == "delete"
            ),
            {},
        )
        delete_prompt = delete_command_config.get(
            "response", "Enter the task ID to delete."
        )

        return f"""
# --- Delete Task Conversation ---
async def delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("{delete_prompt}")
    return DELETE_TASK

async def delete_receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    task_id_str = update.message.text.strip()

    if not USER_TASKS.get(user_id):
        await update.message.reply_text("You have no tasks to delete.")
        return ConversationHandler.END

    try:
        task_id = int(task_id_str)
    except ValueError:
        await update.message.reply_text("Invalid ID. Please enter a number or /cancel.")
        return DELETE_TASK

    initial_task_count = len(USER_TASKS[user_id])
    USER_TASKS[user_id] = [task for task in USER_TASKS[user_id] if task['id'] != task_id]

    if len(USER_TASKS[user_id]) < initial_task_count:
        await update.message.reply_text(f"Task with ID {{task_id}} deleted! 🗑️")
    else:
        await update.message.reply_text(f"Task with ID {{task_id}} not found. Use /tasks to see your tasks.")

    return ConversationHandler.END

async def delete_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Deleting task has been cancelled.")
    return ConversationHandler.END
"""

    def _generate_text_trigger_handler(self):
        """
        Generates a handler that triggers command functions based on exact text matches from keyboard buttons.
        """
        map_str = "KEYBOARD_COMMAND_MAP = {\n"
        kb_config = self.config.get("main_keyboard", {})
        buttons_config = kb_config.get("buttons", [])
        has_mapped_buttons = False

        for btn_data in buttons_config:
            btn_text = btn_data.get("text")
            btn_resp = btn_data.get("response")
            if btn_text and btn_resp and btn_resp.startswith("/"):
                command_name = btn_resp[1:]
                btn_text_py = btn_text.replace('"', '\\"')
                map_str += f'    "{btn_text_py}": "{command_name}",\n'
                has_mapped_buttons = True
        map_str += "}\n"

        if not has_mapped_buttons:
            return "", ""

        handler_code = f"""
{map_str}
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    command_name = KEYBOARD_COMMAND_MAP.get(message_text)

    if command_name and command_name in COMMAND_HANDLERS:
        await COMMAND_HANDLERS[command_name](update, context)
        return
"""
        registration_code = "application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))"
        return handler_code, registration_code

    def generate_full_script(self):
        imports = self._generate_imports()
        bot_init = self._generate_bot_init()

        all_handlers_code = []
        all_registrations = []

        all_handlers_code.append(self._generate_start_handler())
        all_registrations.append(
            'application.add_handler(CommandHandler("start", start_command))'
        )

        all_handlers_code.append(self._generate_help_handler())
        all_registrations.append(
            'application.add_handler(CommandHandler("help", help_command))'
        )

        all_handlers_code.append(self._generate_tasks_handler())
        all_registrations.append(
            'application.add_handler(CommandHandler("tasks", tasks_command))'
        )

        add_conv_code = self._generate_add_task_conversation()
        all_handlers_code.append(add_conv_code)
        add_button_text = next(
            (
                b["text"]
                for b in self.config.get("main_keyboard", {}).get("buttons", [])
                if b.get("response") == "/add"
            ),
            "➕ Add Task",
        )
        all_registrations.append(f"""
add_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('add', add_start), MessageHandler(filters.Regex(r'^{re.escape(add_button_text)}$'), add_start)],
    states={{
        ADD_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_receive_task)],
    }},
    fallbacks=[CommandHandler('cancel', add_cancel)],
)
application.add_handler(add_conv_handler)
""")

        complete_conv_code = self._generate_complete_task_conversation()
        all_handlers_code.append(complete_conv_code)
        complete_button_text = next(
            (
                b["text"]
                for b in self.config.get("main_keyboard", {}).get("buttons", [])
                if b.get("response") == "/complete"
            ),
            "✅ Complete Task",
        )
        all_registrations.append(f"""
complete_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('complete', complete_start), MessageHandler(filters.Regex(r'^{re.escape(complete_button_text)}$'), complete_start)],
    states={{
        COMPLETE_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_receive_id)],
    }},
    fallbacks=[CommandHandler('cancel', complete_cancel)],
)
application.add_handler(complete_conv_handler)
""")

        delete_conv_code = self._generate_delete_task_conversation()
        all_handlers_code.append(delete_conv_code)
        delete_button_text = next(
            (
                b["text"]
                for b in self.config.get("main_keyboard", {}).get("buttons", [])
                if b.get("response") == "/delete"
            ),
            "🗑️ Delete Task",
        )
        all_registrations.append(f"""
delete_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('delete', delete_start), MessageHandler(filters.Regex(r'^{re.escape(delete_button_text)}$'), delete_start)],
    states={{
        DELETE_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_receive_id)],
    }},
    fallbacks=[CommandHandler('cancel', delete_cancel)],
)
application.add_handler(delete_conv_handler)
""")

        text_trigger_code, text_trigger_reg_code = self._generate_text_trigger_handler()
        if text_trigger_code:
            all_handlers_code.append(text_trigger_code)
            all_registrations.append(text_trigger_reg_code)

        command_map_str = "\n# This map helps the general text handler route messages to command functions.\n"
        command_map_str += "COMMAND_HANDLERS = {\n"
        for cmd in self.config.get("commands", []):
            cmd_name = cmd.get("name")
            if cmd_name:
                if cmd_name == "start":
                    command_map_str += f'    "start": start_command,\n'
                elif cmd_name == "help":
                    command_map_str += f'    "help": help_command,\n'
                elif cmd_name == "tasks":
                    command_map_str += f'    "tasks": tasks_command,\n'
                elif cmd_name == "add":
                    command_map_str += f'    "add": add_start,\n'
                elif cmd_name == "complete":
                    command_map_str += f'    "complete": complete_start,\n'
                elif cmd_name == "delete":
                    command_map_str += f'    "delete": delete_start,\n'
        command_map_str += "}\n"
        all_handlers_code.append(command_map_str)

        main_body = [
            "    application = Application.builder().token(BOT_TOKEN).build()",
            "\n    # Register all handlers",
        ]
        main_body.extend([f"    {reg_line}" for reg_line in all_registrations])
        main_func = f"""
def main() -> None:
{chr(10).join(main_body)}

    logger.info(f"Bot '{{BOT_NAME}}' is starting... Polling for updates.")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
"""
        return f"{imports}\n{bot_init}\n{''.join(all_handlers_code)}\n{main_func}"

    def save_script(self):
        script_content = self.generate_full_script()
        try:
            with open(GENERATED_BOT_SCRIPT_FILENAME, "w", encoding="utf-8") as f:
                f.write(script_content)
            self.console.print(
                f"[green]✅ To-Do Bot script successfully generated and saved to '[bold]{GENERATED_BOT_SCRIPT_FILENAME}[/bold]'[/green]"
            )
        except IOError as e:
            self.console.print(
                f"[red]❌ Error saving script to '{GENERATED_BOT_SCRIPT_FILENAME}': {e}[/red]"
            )


def _todo_edit_bot_name(
    features_ref, console_ref, save_features_func, recursive_replace_func
):
    """Handles editing the bot's name (active_template)."""
    current_bot_name = features_ref.get("active_template", "ToDoManager")
    console_ref.print(
        f"\n[cyan]🤖 Current Bot Name:[/cyan] [yellow]{current_bot_name}[/yellow]"
    )
    new_name = console_ref.input(
        f"[magenta]✏️ Enter new bot name (leave blank to keep '{current_bot_name}'): [/]"
    ).strip()
    if new_name and new_name != current_bot_name:
        if (
            console_ref.input(
                f"[red]🔄 Replace all instances of '{current_bot_name}' with '{new_name}' throughout the configuration? (yes/no): [/]"
            ).lower()
            == "yes"
        ):
            features_copy = json.loads(json.dumps(features_ref))
            features_updated_contents = recursive_replace_func(
                features_copy, current_bot_name, new_name
            )
            features_ref.clear()
            features_ref.update(features_updated_contents)
            features_ref["active_template"] = new_name
            save_features_func(features_ref)
            console_ref.print(
                f"[green]✅ Bot name updated to '{new_name}' and all instances replaced.[/green]"
            )
        else:
            features_ref["active_template"] = new_name
            save_features_func(features_ref)
            console_ref.print(
                f"[green]✅ Bot name updated to '{new_name}'. Other instances of '{current_bot_name}' were not changed.[/green]"
            )
    elif not new_name:
        console_ref.print("[yellow]🤷 No change to bot name.[/yellow]")
    else:
        console_ref.print(
            f"[yellow]🤔 New name is same as current. No change.[/yellow]"
        )


def _todo_edit_start_text(features_ref, console_ref, save_features_func):
    """Handles editing the start message text."""
    start_config = features_ref.get("start", {})
    console_ref.print(
        f"\n[cyan]💬 Current Start Text:[/cyan]\n[yellow]{start_config.get('text', 'Not set')}[/yellow]"
    )
    new_text = console_ref.input(
        "[magenta]✏️ New start text (leave blank to keep current): [/]"
    ).strip()
    if new_text and new_text != start_config.get("text"):
        start_config["text"] = new_text
        save_features_func(features_ref)
        console_ref.print("[green]✅ Start text updated.[/green]")
    elif not new_text:
        console_ref.print("[yellow]👍 Start text kept as current.[/yellow]")
    else:
        console_ref.print("[yellow]🤔 New text is same as current. No change.[/yellow]")


def _todo_edit_welcome_image(features_ref, console_ref, save_features_func):
    """Handles editing the welcome image URL."""
    start_config = features_ref.get("start", {})
    console_ref.print(
        f"\n[cyan]Current Welcome Image URL:[/cyan] [yellow]{start_config.get('image_url', 'Not set')}[/yellow]"
    )
    new_url = console_ref.input(
        "[magenta]✏️ New image URL (leave blank to keep, 'none' to remove): [/]"
    ).strip()
    if new_url.lower() == "none":
        if start_config.get("image_url"):
            start_config["image_url"] = ""
            save_features_func(features_ref)
            console_ref.print("[green]🗑️ Welcome image URL removed.[/green]")
        else:
            console_ref.print(
                "[yellow]🤷 Welcome image URL was already not set.[/yellow]"
            )
    elif new_url and new_url != start_config.get("image_url"):
        start_config["image_url"] = new_url
        save_features_func(features_ref)
        console_ref.print("[green]✅ Welcome image URL updated.[/green]")
    elif not new_url:
        console_ref.print("[yellow]👍 Welcome image URL kept as current.[/yellow]")


def _todo_edit_help_message(features_ref, console_ref, save_features_func):
    """Handles editing the help message."""
    current_help = features_ref.get("help", "Not set")
    console_ref.print(
        f"\n[cyan]❓ Current Help Message:[/cyan]\n[yellow]{current_help}[/yellow]"
    )
    new_help = console_ref.input(
        "[magenta]✏️ New help message (leave blank to keep current, use \\n for new lines): [/]"
    ).strip()
    if new_help and new_help != current_help:
        features_ref["help"] = new_help
        save_features_func(features_ref)
        console_ref.print("[green]✅ Help message updated.[/green]")
    elif not new_help:
        console_ref.print("[yellow]👍 Help message kept as current.[/yellow]")
    else:
        console_ref.print(
            "[yellow]🤔 New help message is same as current. No change.[/yellow]"
        )


def _todo_manage_commands(
    features_ref, console_ref, save_features_func, clear_terminal_func
):
    """Manages commands, allowing edits only to responses of system commands or adding/editing custom ones."""
    if "commands" not in features_ref or not isinstance(features_ref["commands"], list):
        features_ref["commands"] = []

    SYSTEM_COMMANDS_DEFAULTS = {
        "tasks": {"name": "tasks", "response": "Here are your current tasks..."},
        "add": {"name": "add", "response": "Please enter the task you want to add."},
        "complete": {
            "name": "complete",
            "response": "Enter the task ID to mark as completed.",
        },
        "delete": {"name": "delete", "response": "Enter the task ID to delete."},
    }

    changed_config_flag = False
    for cmd_name, default_data in SYSTEM_COMMANDS_DEFAULTS.items():
        found = False
        for cmd in features_ref["commands"]:
            if cmd.get("name") == cmd_name:
                if "response" not in cmd:
                    cmd["response"] = default_data["response"]
                    changed_config_flag = True
                found = True
                break
        if not found:
            features_ref["commands"].append(default_data)
            changed_config_flag = True
            console_ref.print(
                f"[yellow]ℹ️ Added missing system command '/{cmd_name}' to configuration.[/yellow]"
            )

    if changed_config_flag:
        save_features_func(features_ref)
        console_ref.input("[bold yellow]\nPress Enter to continue... ↩️[/bold yellow]")

    while True:
        clear_terminal_func()
        console_ref.print(
            Align.center(
                Panel.fit(
                    "🔧 [bold]Manage ToDo Commands[/bold] 🔧",
                    border_style="green",
                    padding=(1, 1),
                )
            )
        )

        all_commands = features_ref.get("commands", [])
        cmd_table = Table(
            title="Current Commands",
            box=box.MINIMAL,
            expand=False,
            width=min(console_ref.width - 4, 90),
        )
        cmd_table.add_column("No.", style="dim", width=3)
        cmd_table.add_column("Command Name", style="cyan", width=20)
        cmd_table.add_column("Response (Preview)", style="yellow", overflow="fold")
        cmd_table.add_column("Type", style="magenta", width=15)

        if not all_commands:
            console_ref.print(
                "[italic yellow]🤷 No commands configured yet.[/italic yellow]"
            )
        else:
            for i, cmd in enumerate(all_commands):
                cmd_name = cmd.get("name", "N/A")
                response = cmd.get("response")

                cmd_type = "Custom"
                if cmd_name in SYSTEM_COMMANDS_DEFAULTS:
                    cmd_type = "System"

                response_preview = str(response)[:70] + (
                    "..."
                    if isinstance(response, str) and len(str(response)) > 70
                    else ""
                )

                cmd_table.add_row(
                    str(i + 1), f"/{cmd_name}", response_preview, cmd_type
                )
            console_ref.print(cmd_table)

        console_ref.print("\n[bold]Options:[/bold]")
        console_ref.print("  [cyan]1.[/cyan] ✏️ Edit Command Response (Custom & System)")
        console_ref.print("  [cyan]2.[/cyan] ➕ Add New Custom Command")
        console_ref.print("  [cyan]3.[/cyan] 🗑️ Remove Custom Command")
        console_ref.print("  [cyan]0.[/cyan] 🔙 Back to ToDo Config Menu")
        choice = console_ref.input("[magenta]👉 Select: [/]").strip()
        action_taken = False

        if choice == "1":
            if not all_commands:
                console_ref.print("[red]🤷 No commands to edit.[/red]")
                time.sleep(1)
                continue
            try:
                idx_str = console_ref.input(
                    "[cyan]✏️ Enter number of command to edit: [/]"
                ).strip()
                if not idx_str:
                    continue
                idx = int(idx_str) - 1

                if 0 <= idx < len(all_commands):
                    cmd_to_modify = all_commands[idx]
                    cmd_name = cmd_to_modify.get("name")
                    current_resp = cmd_to_modify.get("response", "")

                    console_ref.print(
                        f"✍️ Editing response for: [yellow]/{cmd_name}[/yellow]"
                    )
                    new_resp = (
                        console_ref.input(
                            f"[cyan]New response (blank for '{current_resp}'): [/]"
                        ).strip()
                        or current_resp
                    )

                    if new_resp != current_resp:
                        features_ref["commands"][idx]["response"] = new_resp
                        save_features_func(features_ref)
                        console_ref.print("[green]✅ Command response updated.[/green]")
                        action_taken = True
                    else:
                        console_ref.print(
                            "[yellow]🤔 Response is same as current. No change.[/yellow]"
                        )
                else:
                    console_ref.print("[red]❌ Invalid command number.[/red]")
            except ValueError:
                console_ref.print("[red]❌ Invalid input. Please enter a number.[/red]")

        elif choice == "2":
            cmd_name = console_ref.input(
                "[cyan]⌨️ New custom command name (e.g., 'about', no slash): [/]"
            ).strip()
            if cmd_name.lower() in SYSTEM_COMMANDS_DEFAULTS:
                console_ref.print(
                    f"[red]❌ The '/{cmd_name}' command is a system command. You can only edit its response. Choose a different name for a custom command.[/red]"
                )
            elif cmd_name:
                cmd_resp = console_ref.input(
                    f"[cyan]💬 Response for '/{cmd_name}' (use \\n for new lines): [/]"
                ).strip()
                features_ref["commands"].append(
                    {"name": cmd_name, "response": cmd_resp}
                )
                save_features_func(features_ref)
                console_ref.print(
                    f"[green]✅ Custom command '/{cmd_name}' added.[/green]"
                )
                action_taken = True
            else:
                console_ref.print("[red]❌ Command name cannot be empty.[/red]")

        elif choice == "3":
            if not any(
                cmd.get("name") not in SYSTEM_COMMANDS_DEFAULTS for cmd in all_commands
            ):
                console_ref.print("[red]🤷 No custom commands to remove.[/red]")
                time.sleep(1)
                continue
            try:
                idx_str = console_ref.input(
                    "[cyan]🗑️ Enter number of custom command to remove: [/]"
                ).strip()
                if not idx_str:
                    continue
                idx = int(idx_str) - 1

                if 0 <= idx < len(all_commands):
                    cmd_to_remove = all_commands[idx]
                    cmd_name = cmd_to_remove.get("name")
                    if cmd_name in SYSTEM_COMMANDS_DEFAULTS:
                        console_ref.print(
                            f"[red]❌ System command '/{cmd_name}' cannot be removed.[/red]"
                        )
                    else:
                        removed_cmd = features_ref["commands"].pop(idx)
                        save_features_func(features_ref)
                        console_ref.print(
                            f"[green]🗑️ Custom command '/{removed_cmd['name']}' removed.[/green]"
                        )
                        action_taken = True
                else:
                    console_ref.print("[red]❌ Invalid command number.[/red]")
            except ValueError:
                console_ref.print("[red]❌ Invalid input. Please enter a number.[/red]")

        elif choice == "0":
            break
        else:
            console_ref.print("[red]❌ Invalid choice.[/red]")

        if action_taken:
            console_ref.input(
                "[bold yellow]\nPress Enter to continue... ↩️[/bold yellow]"
            )


def _todo_manage_keyboard(
    features_ref, console_ref, save_features_func, clear_terminal_func
):
    """Handles editing the main reply keyboard for the ToDo bot."""
    if "main_keyboard" not in features_ref or not isinstance(
        features_ref.get("main_keyboard"), dict
    ):
        features_ref["main_keyboard"] = {
            "buttons": [],
            "resize": True,
            "persistent": False,
        }
    if "buttons" not in features_ref["main_keyboard"] or not isinstance(
        features_ref["main_keyboard"]["buttons"], list
    ):
        features_ref["main_keyboard"]["buttons"] = []

    SYSTEM_COMMANDS_FOR_BUTTONS = [
        "tasks",
        "add",
        "complete",
        "delete",
        "help",
        "start",
    ]

    while True:
        clear_terminal_func()
        console_ref.print(
            Align.center(
                Panel.fit(
                    "⌨️ [bold]Manage ToDo Keyboard[/bold] ⌨️",
                    border_style="green",
                    padding=(1, 1),
                )
            )
        )
        kb_table = Table(
            title="⌨️ Current Keyboard Buttons",
            box=box.MINIMAL,
            expand=False,
            width=min(console_ref.width - 4, 80),
        )
        kb_table.add_column("No.", style="dim", width=3)
        kb_table.add_column("Button Text", style="cyan", width=25)
        kb_table.add_column("Response/Action", style="yellow", overflow="fold")

        for i, btn in enumerate(features_ref["main_keyboard"]["buttons"]):
            kb_table.add_row(
                str(i + 1), btn.get("text", "N/A"), btn.get("response", "N/A")
            )
        if not features_ref["main_keyboard"]["buttons"]:
            console_ref.print(
                "[italic yellow]🤷 No buttons defined yet.[/italic yellow]"
            )
        else:
            console_ref.print(kb_table)

        console_ref.print(
            f"\n[cyan]📏 Resize Keyboard:[/cyan] {'✅ Yes' if features_ref['main_keyboard'].get('resize', True) else '❌ No'}"
        )
        console_ref.print(
            f"[cyan]📌 Persistent Keyboard:[/cyan] {'✅ Yes' if features_ref['main_keyboard'].get('persistent', False) else '❌ No'}"
        )

        console_ref.print("\n[bold]Options:[/bold]")
        console_ref.print("  [cyan]1.[/cyan] ➕ Add New Button")
        console_ref.print("  [cyan]2.[/cyan] ✏️ Edit Button")
        console_ref.print("  [cyan]3.[/cyan] 🗑️ Remove Button")
        console_ref.print("  [cyan]4.[/cyan] 📏 Toggle Resize Keyboard")
        console_ref.print("  [cyan]5.[/cyan] 📌 Toggle Persistent Keyboard")
        console_ref.print("  [cyan]0.[/cyan] 🔙 Back to ToDo Config Menu")
        choice = console_ref.input("[magenta]👉 Select: [/]").strip()
        action_taken = False

        if choice == "1":
            btn_text = console_ref.input("[cyan]➕ New button text: [/]").strip()
            if btn_text:
                console_ref.print("\n[bold]Available Commands to Link:[/bold]")
                available_commands = features_ref.get("commands", [])

                cmd_options_table = Table(box=box.MINIMAL, show_header=False)
                cmd_options_table.add_column("Num", style="dim")
                cmd_options_table.add_column("Command", style="cyan")
                cmd_options_table.add_column("Type", style="yellow")

                linkable_cmds = []
                for i, cmd in enumerate(available_commands):
                    cmd_name = cmd.get("name")
                    if cmd_name in SYSTEM_COMMANDS_FOR_BUTTONS:
                        linkable_cmds.append(cmd)
                        cmd_options_table.add_row(
                            str(len(linkable_cmds)), f"/{cmd_name}", "System"
                        )
                    elif cmd.get("response") is not None and not isinstance(
                        cmd.get("response"), list
                    ):
                        linkable_cmds.append(cmd)
                        cmd_options_table.add_row(
                            str(len(linkable_cmds)), f"/{cmd_name}", "Custom Text"
                        )

                if linkable_cmds:
                    console_ref.print(cmd_options_table)
                    console_ref.print(
                        "[yellow]Type 'custom' to enter your own response text.[/yellow]"
                    )
                else:
                    console_ref.print(
                        "[italic yellow]No linkable commands found. You can enter a custom response.[/italic yellow]"
                    )

                resp_choice = console_ref.input(
                    "[magenta]Choose response (enter number of command, or type custom text/URL): [/]"
                ).strip()

                btn_resp = ""
                if resp_choice.lower() == "custom":
                    btn_resp = console_ref.input(
                        "[cyan]💬 Enter custom response for button: [/]"
                    ).strip()
                else:
                    try:
                        resp_idx = int(resp_choice) - 1
                        if 0 <= resp_idx < len(linkable_cmds):
                            selected_cmd = linkable_cmds[resp_idx]
                            btn_resp = f"/{selected_cmd.get('name')}"
                        else:
                            console_ref.print(
                                "[red]❌ Invalid choice. Using entered text as custom response.[/red]"
                            )
                            btn_resp = resp_choice
                    except ValueError:
                        btn_resp = resp_choice

                if btn_text:
                    features_ref["main_keyboard"]["buttons"].append(
                        {"text": btn_text, "response": btn_resp}
                    )
                    save_features_func(features_ref)
                    console_ref.print(
                        f"[green]✅ Button '{btn_text}' added with response '{btn_resp}'.[/green]"
                    )
                    action_taken = True
            else:
                console_ref.print("[red]❌ Button text cannot be empty.[/red]")

        elif choice == "2":
            if not features_ref["main_keyboard"]["buttons"]:
                console_ref.print("[red]🤷 No buttons to edit.[/red]")
                time.sleep(1)
                continue
            try:
                idx = (
                    int(
                        console_ref.input(
                            "[cyan]✏️ Enter number of button to edit: [/]"
                        ).strip()
                    )
                    - 1
                )
                if 0 <= idx < len(features_ref["main_keyboard"]["buttons"]):
                    old_btn = features_ref["main_keyboard"]["buttons"][idx]
                    console_ref.print(
                        f"✍️ Editing button: [yellow]{old_btn['text']}[/yellow]"
                    )
                    new_text = (
                        console_ref.input(
                            f"[cyan]New text (blank for '{old_btn['text']}'): [/]"
                        ).strip()
                        or old_btn["text"]
                    )

                    console_ref.print("\n[bold]Available Commands to Link:[/bold]")
                    available_commands = features_ref.get("commands", [])

                    cmd_options_table = Table(box=box.MINIMAL, show_header=False)
                    cmd_options_table.add_column("Num", style="dim")
                    cmd_options_table.add_column("Command", style="cyan")
                    cmd_options_table.add_column("Type", style="yellow")

                    linkable_cmds = []
                    for i, cmd in enumerate(available_commands):
                        cmd_name = cmd.get("name")
                        if cmd_name in SYSTEM_COMMANDS_FOR_BUTTONS:
                            linkable_cmds.append(cmd)
                            cmd_options_table.add_row(
                                str(len(linkable_cmds)), f"/{cmd_name}", "System"
                            )
                        elif cmd.get("response") is not None and not isinstance(
                            cmd.get("response"), list
                        ):
                            linkable_cmds.append(cmd)
                            cmd_options_table.add_row(
                                str(len(linkable_cmds)), f"/{cmd_name}", "Custom Text"
                            )

                    if linkable_cmds:
                        console_ref.print(cmd_options_table)
                        console_ref.print(
                            "[yellow]Type 'custom' to enter your own response text.[/yellow]"
                        )
                    else:
                        console_ref.print(
                            "[italic yellow]No linkable commands found. You'll need to enter a custom response.[/italic yellow]"
                        )

                    current_resp_display = old_btn.get("response", "")
                    resp_choice = console_ref.input(
                        f"[magenta]Choose new response (enter number, 'custom', or blank to keep '{current_resp_display}'): [/]"
                    ).strip()

                    new_resp = old_btn.get("response", "")
                    if resp_choice:
                        if resp_choice.lower() == "custom":
                            new_resp = console_ref.input(
                                "[cyan]💬 Enter custom response for button: [/]"
                            ).strip()
                        else:
                            try:
                                resp_idx = int(resp_choice) - 1
                                if 0 <= resp_idx < len(linkable_cmds):
                                    selected_cmd = linkable_cmds[resp_idx]
                                    new_resp = f"/{selected_cmd.get('name')}"
                                else:
                                    console_ref.print(
                                        "[red]❌ Invalid choice. Keeping current response.[/red]"
                                    )
                            except ValueError:
                                new_resp = resp_choice

                    features_ref["main_keyboard"]["buttons"][idx] = {
                        "text": new_text,
                        "response": new_resp,
                    }
                    save_features_func(features_ref)
                    console_ref.print("[green]✅ Button updated.[/green]")
                    action_taken = True
                else:
                    console_ref.print("[red]❌ Invalid button number.[/red]")
            except ValueError:
                console_ref.print("[red]❌ Invalid input. Please enter a number.[/red]")

        elif choice == "3":
            if not features_ref["main_keyboard"]["buttons"]:
                console_ref.print("[red]🤷 No buttons to remove.[/red]")
                time.sleep(1)
                continue
            try:
                idx = (
                    int(
                        console_ref.input(
                            "[cyan]🗑️ Enter number of button to remove: [/]"
                        ).strip()
                    )
                    - 1
                )
                if 0 <= idx < len(features_ref["main_keyboard"]["buttons"]):
                    removed_btn = features_ref["main_keyboard"]["buttons"].pop(idx)
                    save_features_func(features_ref)
                    console_ref.print(
                        f"[green]🗑️ Button '{removed_btn['text']}' removed.[/green]"
                    )
                    action_taken = True
                else:
                    console_ref.print("[red]❌ Invalid button number.[/red]")
            except ValueError:
                console_ref.print("[red]❌ Invalid input. Please enter a number.[/red]")

        elif choice == "4":
            current_resize_val = features_ref["main_keyboard"].get("resize", True)
            features_ref["main_keyboard"]["resize"] = not current_resize_val
            save_features_func(features_ref)
            console_ref.print(
                f"[green]📏 Resize keyboard set to: {'✅ Yes' if features_ref['main_keyboard']['resize'] else '❌ No'}[/green]"
            )
            action_taken = True

        elif choice == "5":
            current_persistent_val = features_ref["main_keyboard"].get(
                "persistent", False
            )
            features_ref["main_keyboard"]["persistent"] = not current_persistent_val
            save_features_func(features_ref)
            console_ref.print(
                f"[green]📌 Persistent keyboard set to: {'✅ Yes' if features_ref['main_keyboard']['persistent'] else '❌ No'}[/green]"
            )
            action_taken = True

        elif choice == "0":
            break
        else:
            console_ref.print("[red]❌ Invalid choice.[/red]")

        if action_taken:
            console_ref.input(
                "[bold yellow]\nPress Enter to continue... ↩️[/bold yellow]"
            )


def _handle_generated_bot_script_run():
    """Attempts to run the generated bot script."""
    script_name = GENERATED_BOT_SCRIPT_FILENAME
    clear_terminal()
    console.print(f"[cyan]🚀 Attempting to run [bold]{script_name}[/bold]...[/cyan]")
    console.print("=" * console.width)
    if os.path.exists(script_name):
        try:
            python_executable = sys.executable
            exit_code = subprocess.run(
                [python_executable, script_name], check=False
            ).returncode
            console.print("=" * console.width)
            if exit_code == 0:
                console.print(
                    f"[green]✅ [bold]{script_name}[/bold] execution finished successfully.[/green]"
                )
            else:
                console.print(
                    f"[yellow]⚠️ [bold]{script_name}[/bold] execution finished with exit code: {exit_code}. Check for errors above. 👆[/yellow]"
                )
        except Exception as e:
            console.print("=" * console.width)
            console.print(
                f"[bold red]❌ An error occurred while trying to run the script: {e}[/bold red]"
            )
    else:
        console.print(
            f"[bold red]❌ Error: Script '[bold]{script_name}[/bold]' not found.[/bold red]"
        )
        console.print(
            f"[bold red]👉 Generate/Export it first using option 7 or the main utility menu.[/bold red]"
        )
        console.print("=" * console.width)


def manage_todo_template_config(
    features_ref,
    console_ref,
    save_features_func,
    recursive_replace_func,
    clear_terminal_func,
):
    """Main function to manage the ToDo bot's configuration."""
    if features_ref.get("template_name") != "ToDo":
        console_ref.print(
            "[bold red]❌ Error: The 'ToDo' template is not currently active or loaded correctly.[/]"
        )
        console_ref.print(
            f"[bold red]‼️ Please ensure '{BOT_CONFIG_FILEPATH}' contains '\"template_name\": \"ToDo\"'.[/bold red]"
        )
        console_ref.input("[bold yellow]Press Enter to continue... ↩️[/]")
        return

    system_commands_to_add = {
        "tasks": {"name": "tasks", "response": "Here are your current tasks..."},
        "add": {"name": "add", "response": "Please enter the task you want to add."},
        "complete": {
            "name": "complete",
            "response": "Enter the task ID to mark as completed.",
        },
        "delete": {"name": "delete", "response": "Enter the task ID to delete."},
    }

    changed_config_flag = False
    current_command_names = {
        cmd.get("name")
        for cmd in features_ref.get("commands", [])
        if isinstance(cmd, dict) and "name" in cmd
    }

    for cmd_name, cmd_data in system_commands_to_add.items():
        if cmd_name not in current_command_names:
            features_ref.setdefault("commands", []).append(cmd_data)
            changed_config_flag = True
            console_ref.print(
                f"[yellow]ℹ️ Added missing system command '/{cmd_name}' to configuration for display.[/yellow]"
            )

    if "main_keyboard" not in features_ref or not isinstance(
        features_ref["main_keyboard"], dict
    ):
        features_ref["main_keyboard"] = {
            "buttons": [],
            "resize": True,
            "persistent": False,
        }
        changed_config_flag = True
        console_ref.print(
            "[yellow]ℹ️ Initialized missing 'main_keyboard' structure.[/yellow]"
        )

    required_todo_buttons = [
        {"text": "📋 View Tasks", "response": "/tasks"},
        {"text": "➕ Add Task", "response": "/add"},
        {"text": "✅ Complete Task", "response": "/complete"},
        {"text": "🗑️ Delete Task", "response": "/delete"},
    ]
    current_button_texts = {
        btn.get("text") for btn in features_ref["main_keyboard"].get("buttons", [])
    }

    for req_btn in required_todo_buttons:
        if req_btn["text"] not in current_button_texts:
            features_ref["main_keyboard"]["buttons"].append(req_btn)
            changed_config_flag = True
            console_ref.print(
                f"[yellow]ℹ️ Added missing default ToDo button '{req_btn['text']}'.[/yellow]"
            )

    if changed_config_flag:
        save_features_func(features_ref)
        console_ref.print(
            "[green]✅ Configuration updated with missing ToDo elements.[/green]"
        )
        console_ref.input("[bold yellow]\nPress Enter to continue... ↩️[/bold yellow]")

    while True:
        clear_terminal_func()
        bot_name = features_ref.get("active_template", "Your ToDo Bot")
        console_ref.print(
            Align.center(
                Panel(
                    f"[bold cyan]ToDo Template Admin: {bot_name}[/]",
                    border_style="cyan",
                    padding=(1, 1),
                )
            )
        )

        todo_admin_menu = Table(
            title="[b]🔧 ToDo Admin Options[/b]",
            box=box.ROUNDED,
            expand=False,
            show_header=False,
            padding=(0, 1),
            width=min(console_ref.width - 4, 70),
        )
        todo_admin_menu.add_column("Opt", style="cyan", width=3)
        todo_admin_menu.add_column("Action", style="yellow")
        todo_admin_menu.add_row("1.", "📝 Change Bot Name")
        todo_admin_menu.add_row("2.", "💬 Edit Start Message Text")
        todo_admin_menu.add_row("3.", "Change Welcome Image URL")
        todo_admin_menu.add_row("4.", "❓ Edit Help Message")
        todo_admin_menu.add_row("5.", "Manage Commands (System & Custom)")
        todo_admin_menu.add_row("6.", "Manage Main Keyboard Buttons")
        todo_admin_menu.add_row("7.", "📤 Export & View Bot Source Code")
        todo_admin_menu.add_row("8.", "⚡ Run Generated ToDo Bot")
        todo_admin_menu.add_row("0.", "🚪 Exit")
        console_ref.print(Align.center(todo_admin_menu))

        choice = console_ref.input(
            "[bold magenta]👉 Select ToDo Config option: [/]"
        ).strip()

        action_occurred_direct = False
        if choice == "1":
            _todo_edit_bot_name(
                features_ref, console_ref, save_features_func, recursive_replace_func
            )
            action_occurred_direct = True
        elif choice == "2":
            _todo_edit_start_text(features_ref, console_ref, save_features_func)
            action_occurred_direct = True
        elif choice == "3":
            _todo_edit_welcome_image(features_ref, console_ref, save_features_func)
            action_occurred_direct = True
        elif choice == "4":
            _todo_edit_help_message(features_ref, console_ref, save_features_func)
            action_occurred_direct = True
        elif choice == "5":
            _todo_manage_commands(
                features_ref, console_ref, save_features_func, clear_terminal_func
            )
        elif choice == "6":
            _todo_manage_keyboard(
                features_ref, console_ref, save_features_func, clear_terminal_func
            )
        elif choice == "7":
            generator = ToDoBotCodeGenerator(features_ref, console_ref)
            generator.save_script()
            console_ref.print(f"\n[bold green]To run your new bot:[/bold green]")
            console_ref.print(
                f"1. Ensure 'python-telegram-bot' is installed: [cyan]pip install python-telegram-bot[/cyan]"
            )
            if generator.actual_bot_token:
                console_ref.print(
                    f"2. ✅ Bot token was read from [cyan]{BOT_TOKEN_FILE}[/cyan] and embedded in the script."
                )
            else:
                console_ref.print(
                    f"2. [yellow]⚠️ Warning:[/yellow] Bot token was [bold red]NOT[/bold] read from [cyan]{BOT_TOKEN_FILE}[/cyan]."
                )
                console_ref.print(
                    f"   👉 Please manually edit [cyan]{GENERATED_BOT_SCRIPT_FILENAME}[/cyan] and replace `YOUR_BOT_TOKEN_HERE_UPDATE_THIS_OR_ENSURE_GENERATOR_CAN_READ_TOKEN_FILE` with your actual bot token."
                )
            console_ref.print(
                f"3. Run the script: [cyan]python {GENERATED_BOT_SCRIPT_FILENAME}[/cyan]"
            )
            action_occurred_direct = True
        elif choice == "8":
            _handle_generated_bot_script_run()
            action_occurred_direct = True
        elif choice == "0":
            break
        else:
            console_ref.print("[bold red]❌ Invalid choice.[/red]")
            time.sleep(1)

        if action_occurred_direct:
            console_ref.input(
                "\n[bold yellow]Press Enter to continue... ↩️[/bold yellow]"
            )


def main():
    """Main entry point for the ToDo Eco Configuration Manager."""
    clear_terminal()
    console.print(
        Panel.fit(
            "[bold green]⚙️ ToDo Template Configuration Manager[/bold green]",
            padding=(0, 2),
        )
    )

    features_data = {}
    try:
        features_data = load_features_from_json(BOT_CONFIG_FILEPATH)
        console.print(
            f"[green]✅ Loaded bot config from '{BOT_CONFIG_FILEPATH}'[/green]\n"
        )
    except (FileNotFoundError, json.JSONDecodeError) as e:
        console.print(f"[red]❌ Error loading '{BOT_CONFIG_FILEPATH}': {e}[/red]")
        console.print(
            "[yellow]Initializing with default ToDo template structure for current session.[/yellow]\n"
        )

        features_data = {
            "template_name": "ToDo",
            "active_template": "My ToDo List Bot",
            "start": {
                "text": "Welcome to **{BOT_NAME}**! Manage your tasks effectively.",
                "image_url": "",
            },
            "help": "Help for {BOT_NAME}: Use /tasks, /add, /complete, /delete.",
            "commands": [
                {"name": "tasks", "response": "Here are your current tasks..."},
                {"name": "add", "response": "Please enter the task you want to add."},
                {
                    "name": "complete",
                    "response": "Enter the task ID to mark as completed.",
                },
                {"name": "delete", "response": "Enter the task ID to delete."},
            ],
            "main_keyboard": {
                "buttons": [
                    {"text": "📋 View Tasks", "response": "/tasks"},
                    {"text": "➕ Add Task", "response": "/add"},
                    {"text": "✅ Complete Task", "response": "/complete"},
                    {"text": "🗑️ Delete Task", "response": "/delete"},
                ],
                "resize": True,
                "persistent": False,
            },
        }

        save_features_to_json(features_data, BOT_CONFIG_FILEPATH)

    manage_todo_template_config(
        features_data,
        console,
        save_features_to_json,
        _recursive_replace,
        clear_terminal,
    )

    console.print("\n[yellow]👋 Exiting ToDo Configurator. Goodbye![/yellow]")


if __name__ == "__main__":
    if not os.path.exists(TODO_TEMPLATE_FILENAME):
        dummy_template_content = {
            "template_name": "ToDo",
            "template_description": "A simple To-Do List Template for Task Management",
            "active_template": "ToDoManager",
            "start": {
                "text": "Welcome to **{BOT_NAME}**! Organize your tasks efficiently.",
                "image_url": "",
            },
            "help": "Help for {BOT_NAME}: Use /tasks, /add, /complete, /delete. You can also tap the keyboard buttons!",
            "commands": [
                {"name": "tasks", "response": "Here are your current tasks..."},
                {"name": "add", "response": "Please enter the task you want to add."},
                {
                    "name": "complete",
                    "response": "Enter the task ID to mark as completed.",
                },
                {"name": "delete", "response": "Enter the task ID to delete."},
            ],
            "main_keyboard": {
                "buttons": [
                    {"text": "📋 View Tasks", "response": "/tasks"},
                    {"text": "➕ Add Task", "response": "/add"},
                    {"text": "✅ Complete Task", "response": "/complete"},
                    {"text": "🗑️ Delete Task", "response": "/delete"},
                ],
                "resize": True,
                "persistent": False,
                "inline": False,
            },
        }
        with open(TODO_TEMPLATE_FILENAME, "w", encoding="utf-8") as f:
            json.dump(dummy_template_content, f, indent=4)
        console.print(f"Created a dummy '{TODO_TEMPLATE_FILENAME}' for demonstration.")

    os.makedirs(os.path.dirname(BOT_TOKEN_FILE), exist_ok=True)
    if not os.path.exists(BOT_TOKEN_FILE):
        with open(BOT_TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write("YOUR_TELEGRAM_BOT_TOKEN_HERE")
        console.print(
            f"Created a dummy '{BOT_TOKEN_FILE}'. Please replace its content with your actual bot token."
        )

    main()
