from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich import box
from rich.box import ROUNDED, SIMPLE_HEAVY
import sys
import subprocess
from rich.console import Console
import os
import json
from pathlib import Path
from rich.table import Table
from rich import box
import time
import requests
import shutil
from datetime import datetime, timedelta

CONFIG_DIR = Path.home() / ".media_analysis"
CONFIG_FILE = CONFIG_DIR / "config.json"

IDEA_FLOW_ART = """
                            ██╗██╗  ██╗██╗       ██╗       ███████╗ █████╗ ██╗      █████╗ ██████╗ 
                            ██║╚██╗██╔╝██║       ██║       ██╔════╝██╔══██╗██║     ██╔══██╗██╔══██╗
                            ██║ ╚███╔╝ ██║    ████████╗    ███████╗███████║██║     ███████║██████╔╝
                            ██║ ██╔██╗ ██║    ██╔═██╔═╝    ╚════██║██╔══██║██║     ██╔══██║██╔══██╗
                            ██║██╔╝ ██╗██║    ██████║      ███████║██║  ██║███████╗██║  ██║██║  ██║
                            ╚═╝╚═╝  ╚═╝╚═╝    ╚═════╝      ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
"""


def show_telegram_bot_info():
    guide_text = Text()
    guide_text.append("1. ", style="bold green")
    guide_text.append("Open Telegram and search for ")
    guide_text.append("@BotFather\n", style="bold cyan")
    guide_text.append("2. ", style="bold green")
    guide_text.append("Start a chat with BotFather\n")
    guide_text.append("3. ", style="bold green")
    guide_text.append("Send ")
    guide_text.append("'/newbot'", style="bold yellow")
    guide_text.append(" to create a new bot\n")
    guide_text.append("4. ", style="bold green")
    guide_text.append("Follow instructions to choose name & username\n")
    guide_text.append("5. ", style="bold green")
    guide_text.append("You'll receive an API token - copy it for this tool\n")
    panel = Panel(
        Align.center(guide_text),
        title="📘 TELEGRAM BOT CREATION GUIDE",
        title_align="center",
        border_style="cyan",
        box=ROUNDED,
        padding=(1, 2),
        width=60,
    )
    console.print(Align.center(panel))


def center_text(text, color_code=None):
    cols = shutil.get_terminal_size().columns
    centered_lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if color_code:
            stripped = f"{color_code}{stripped}\033[0m"
        padding = (cols - len(stripped)) // 2
        centered = " " * max(0, padding) + stripped
        centered_lines.append(centered)
    return "\n".join(centered_lines)


def print_centered(text, color_code=None):
    print(center_text(text, color_code))


def input_centered(prompt, color_code=None):
    cols = shutil.get_terminal_size().columns
    stripped = prompt.strip()
    if color_code:
        stripped = f"{color_code}{stripped}\033[0m"
    padding = (cols - len(stripped)) // 2
    return input(" " * max(0, padding) + stripped)


def load_config():
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        print_centered(f"⚠️ Error loading config: {str(e)}", "\033[31m")
        return {}


def save_config(config):
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print_centered(f"⚠️ Error saving config: {str(e)}", "\033[31m")
        return False


os.system("clear")
print_centered(IDEA_FLOW_ART, "\t\033[38;5;208m")
console = Console()

YOUTUBE_API_KEY = "AIzaSyAeX11rZka_G36cQGP6np3kA-SHK5pD5o0"
TMDB_API_KEY = "44d09a665d39ee0f40eff386f12496ca"


def main_menu():
    table = Table(
        box=ROUNDED,
        show_edge=True,
        expand=False,
        border_style="cyan",
        show_header=True,
        header_style="bold white",
        padding=(0, 2),
        width=60,
    )
    table.add_column("Option", justify="center", style="bold white", no_wrap=True)
    table.add_column("Description", style="bold cyan", justify="center", no_wrap=False)
    table.add_row("1.", "🤖Create/Modify Telegram Bot")
    table.add_row("2.", "🚪Exit")
    panel = Panel(
        Align.center(table),
        title="🌟 Main Menu",
        title_align="center",
        border_style="bright_blue",
        box=ROUNDED,
        padding=(0, 1),
        width=80,
    )
    console.print(Align.center(panel))


def get_telegram_token():
    os.system("clear")
    print("\n" * 3)
    show_telegram_bot_info()
    config = load_config()
    saved_token = config.get("telegram_token")
    if saved_token:
        response = (
            input_centered(
                "🔑 Found saved Telegram token. Use saved token? (Y/n): ", "\033[33m"
            )
            .strip()
            .lower()
        )
        if response in ("y", ""):
            return saved_token
    new_token = input_centered(
        "🤖 Please enter your Telegram Bot API Token: ", "\033[36m"
    ).strip()
    if new_token:
        config["telegram_token"] = new_token
        if save_config(config):
            print_centered("🔒 Token saved securely!", "\033[32m")
        return new_token


def get_new_bot_name():
    print_centered("✏️ What would you like to name your bot?", "\033[36m")
    print_centered("(This will change how your bot appears in chats)", "\033[3m")
    return input_centered("New bot name: ", "\033[36m").strip()


def change_bot_name(token, new_name):
    url = f"https://api.telegram.org/bot{token}/setMyName"
    params = {"name": new_name}
    try:
        response = requests.post(url, params=params)
        result = response.json()
        if result.get("ok"):
            return True, f"✅ Success! Your bot is now named: {new_name}"
        return (
            False,
            f"⚠️ Failed to change name: {result.get('description', 'Unknown error')}",
        )
    except Exception as e:
        return False, f"⚠️ API Error: {str(e)}"


def create_telegram_bot_maker_file():
    bot_file_path = Path("user_source_code.py")
    token_path = Path("bot_files/telegram_token.txt")
    if not token_path.exists():
        print_centered("🔴 Token file not found in bot_files directory", "\033[31m")
        return False
    try:
        with open(token_path, "r") as f:
            actual_token = f.read().strip()
    except Exception as e:
        print_centered(f"⚠️ Error reading token file: {str(e)}", "\033[31m")
        return False
    bot_code_template = """
from telegram.ext import Updater

TOKEN = "YOUR_TOKEN" 

def main():
    updater = Updater(TOKEN)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    """
    if bot_file_path.exists():
        try:
            with open(bot_file_path, "r") as f:
                existing_code = f.read()
            updated_code = existing_code.replace(
                'TOKEN = "YOUR_TOKEN"', f'TOKEN = "{actual_token}"'
            )
            with open(bot_file_path, "w") as f:
                f.write(updated_code)
            print_centered(f"✅ Updated token in existing: {bot_file_path}", "\033[32m")
            return True
        except Exception as e:
            print_centered(f"⚠️ Error updating existing file: {str(e)}", "\033[31m")
            return False
    else:
        try:
            with open(bot_file_path, "w") as f:
                f.write(bot_code_template.format(token=actual_token))
            print_centered(
                f"✅ Created bot source code at: {bot_file_path}", "\033[32m"
            )
            return True
        except Exception as e:
            print_centered(f"⚠️ Error creating bot file: {str(e)}", "\033[31m")
            return False


def telegram_bot_flow():
    token = get_telegram_token()
    if not token:
        console.print(Align.center(Text("🔴 No token provided", style="bold red")))
        return
    print("\n")
    table = Table(
        title="🤖 Telegram Bot Configuration",
        box=ROUNDED,
        style="cyan",
        title_style="bold magenta",
        width=60,
    )
    table.add_column("Option", justify="center", style="bold white")
    table.add_column("Action", justify="center", style="bold green")
    table.add_row("1", "Update API Token")
    table.add_row("2", "Back to Main Menu")
    table.add_row("3", "Show the API Token")
    table.add_row("4", "--> Create New Bot (Continue) <--")
    panel = Panel(
        Align.center(table),
        title="Choose an Option",
        title_align="center",
        border_style="bright_blue",
        width=70,
    )
    console.print(Align.center(panel))
    console.print()
    choice = input_centered("Choose action (1-4): ", "\033[36m")
    if choice == "1":
        config = load_config()
        config.pop("telegram_token", None)
        if save_config(config):
            print_centered("🔑 Existing token removed.", "\033[32m")
        get_telegram_token()
    elif choice == "2":
        return
    elif choice == "3":
        print_centered("\n🤖 Your Telegram Bot API Token:", "\033[36m")
        print_centered(f"{token}", "\033[1;33m")
        print_centered("\nKeep this token secure!", "\033[33m")
        input_centered("\nPress Enter to continue...", "\033[36m")
    elif choice == "4":
        welcome_panel = Panel.fit(
            "🤖 [bold cyan]Welcome to Telegram Bot Maker[/]",
            box=box.DOUBLE,
            padding=(1, 4),
            border_style="bright_cyan",
        )
        console.print(Align.center(welcome_panel))
        print_centered("\n🚀 Launching Advanced Bot Creation...", "\033[1;35m")
        bot_files_dir = Path("bot_files")
        bot_files_dir.mkdir(exist_ok=True)
        token_file = bot_files_dir / "telegram_token.txt"
        try:
            with open(token_file, "w") as f:
                f.write(token)
            print_centered(f"🔑 Token saved to: {token_file}", "\033[33m")
        except Exception as e:
            print_centered(f"⚠️ Error saving token: {str(e)}", "\033[31m")
            return
        if not create_telegram_bot_maker_file():
            return
        print_centered("\n⚙️ Starting Telegram Bot Maker...", "\033[36m")
        time.sleep(2)
        try:
            os.execv(sys.executable, [sys.executable, "telegram_bot_maker.py"])
        except Exception as e:
            print_centered(f"⚠️ Failed to start Bot Maker: {str(e)}", "\033[31m")
            return
    else:
        print_centered("⚠️ Invalid option", "\033[33m")


def show_token():
    try:
        with open("telegram_token.txt", "r") as f:
            token = f.read()
    except:
        token = None
    return token


def main():
    while True:
        main_menu()
        choice = input_centered("\nEnter option (1-2): ", "\033[36m")
        if choice == "1":
            telegram_bot_flow()
        elif choice == "2":
            print_centered("👋 Thank you for using Media Analysis Pro!", "\033[32m")
            break
        else:
            print_centered("⚠️ Invalid option", "\033[33m")


if __name__ == "__main__":
    main()
