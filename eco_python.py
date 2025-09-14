import os
import time
import json
import logging
import csv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich import box
import re




TOKEN_FILE_PATH_FOR_GENERATOR = "bot_files/telegram_token.txt"
BOT_CONFIG_FILEPATH = "user_bot.json"
SESSIONS_FILE = "sessions.json"
IDEA_FLOW_ART = """
                            ██╗██╗  ██╗██╗       ██╗       ███████╗ █████╗ ██╗      █████╗ ██████╗ 
                            ██║╚██╗██╔╝██║       ██║       ██╔════╝██╔══██╗██║     ██╔══██╗██╔══██╗
                            ██║ ╚███╔╝ ██║    ████████╗    ███████╗███████║██║     ███████║██████╔╝
                            ██║ ██╔██╗ ██║    ██╔═██╔═╝    ╚════██║██╔══██║██║     ██╔══██║██╔══██╗
                            ██║██╔╝ ██╗██║    ██████║      ███████║██║  ██║███████╗██║  ██║██║  ██║
                            ╚═╝╚═╝  ╚═╝╚═╝    ╚═════╝      ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
"""


def print_centered(text, color_code=None):
    """Print centered text"""
    print(text, color_code)

import pandas as pd

def excel_to_json(file_path):
    excel_file = pd.read_excel(file_path, sheet_name=None)  # Load all sheets
    return {sheet: df.to_dict(orient="records") for sheet, df in excel_file.items()}

def open_file_dialog_with_csv():
    """Opens a file dialog to select Excel or CSV files."""
    try:
        from tkinter import filedialog, Tk

        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select an Excel or CSV file",
            filetypes=(
                ("Supported Files", "*.xlsx *.xls *.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ),
        )
        return file_path
    except (ImportError, RuntimeError):
        return input(
            "Tkinter not available. Please paste the full file path here: "
        ).strip()


def csv_to_json(file_path, console_ref):
    """Converts a CSV file to a JSON-compatible dictionary."""
    data = {}
    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as csv_file:
            sheet_name = os.path.splitext(os.path.basename(file_path))[0]
            csv_reader = csv.DictReader(csv_file)
            product_list = [row for row in csv_reader]
            if not product_list:
                return None
            data[sheet_name] = product_list
    except Exception as e:
        console_ref.print(f"[bold red]❌ Error processing CSV file: {e}[/bold red]")
        return None
    return data


def _get_session_response(console_ref):
    """Helper function to get session response from sessions.json"""
    session_data = None
    use_session = (
        console_ref.input("[magenta]❓ Use a session for reply? (yes/no): [/]")
        .strip()
        .lower()
    )

    if use_session == "yes":
        if not os.path.exists(SESSIONS_FILE):
            console_ref.print(
                f"[red]⚠️ No sessions file found at '{SESSIONS_FILE}'![/red]"
            )
            return None

        try:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                sessions = json.load(f)

            if sessions and isinstance(sessions, dict):
                console_ref.print("[cyan]Available sessions:[/cyan]")
                sessions_list = list(sessions.keys())
                for idx, sess in enumerate(sessions_list, 1):
                    console_ref.print(f"  {idx}. {sess}")

                try:
                    sess_choice_str = console_ref.input(
                        f"[magenta]👉 Choose session (1-{len(sessions_list)}): [/]"
                    )
                    if not sess_choice_str.isdigit():
                        console_ref.print(
                            "[red]⚠️ Invalid input. Please enter a number.[/red]"
                        )
                        return None

                    sess_choice = int(sess_choice_str)
                    if 1 <= sess_choice <= len(sessions_list):
                        chosen_session_name = sessions_list[sess_choice - 1]
                        session_content = sessions[chosen_session_name]
                        session_data = {chosen_session_name: session_content}
                        console_ref.print(
                            f"[green]✅ Using session: {chosen_session_name}[/green]"
                        )
                    else:
                        console_ref.print("[red]⚠️ Invalid selection![/red]")
                except ValueError:
                    console_ref.print(
                        "[red]⚠️ Invalid input. Please enter a number.[/red]"
                    )
            elif not sessions:
                console_ref.print(
                    "[yellow]ℹ️ No sessions available in the sessions file.[/yellow]"
                )
            else:
                console_ref.print(
                    "[red]⚠️ Sessions file is not in the correct format (should be a dictionary).[/red]"
                )

        except (json.JSONDecodeError, IOError) as e:
            console_ref.print(
                f"[red]⚠️ Error reading or parsing sessions file: {e}[/red]"
            )
            return None

    return session_data


def _eco_edit_shop_name(
    features_ref, console_ref, save_features_func, recursive_replace_func
):
    """Handles editing the shop name."""
    current_shop_name = features_ref.get("active_template", "Unknown Shop")
    console_ref.print(
        f"\n[cyan]🏬 Current Shop Name:[/cyan] [yellow]{current_shop_name}[/yellow]"
    )
    new_name = console_ref.input(
        f"[magenta]✏️ Enter new shop name (leave blank to keep '{current_shop_name}'): [/]"
    ).strip()
    if new_name and new_name != current_shop_name:
        if (
            console_ref.input(
                f"[red]🔄 Replace all instances of '{current_shop_name}' with '{new_name}' throughout the configuration? (yes/no): [/]"
            ).lower()
            == "yes"
        ):
            features_copy = json.loads(json.dumps(features_ref))
            features_updated_contents = recursive_replace_func(
                features_copy, current_shop_name, new_name
            )
            features_ref.clear()
            features_ref.update(features_updated_contents)
            features_ref["active_template"] = new_name
            save_features_func(features_ref)
            console_ref.print(
                f"[green]✅ Shop name updated to '{new_name}' and all instances replaced.[/green]"
            )
        else:
            features_ref["active_template"] = new_name
            save_features_func(features_ref)
            console_ref.print(
                f"[green]✅ Shop name updated to '{new_name}'. Other instances of '{current_shop_name}' were not changed.[/green]"
            )
    elif not new_name:
        console_ref.print("[yellow]🤷 No change to shop name.[/yellow]")
    else:
        console_ref.print(
            f"[yellow]🤔 New name is same as current. No change.[/yellow]"
        )


def _eco_edit_start_text(features_ref, console_ref, save_features_func):
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


def _eco_edit_welcome_image(features_ref, console_ref, save_features_func):
    """Handles editing the welcome image URL."""
    start_config = features_ref.get("start", {})
    console_ref.print(
        f"\n[cyan]🖼️  Current Welcome Image URL:[/cyan] [yellow]{start_config.get('image_url', 'Not set')}[/yellow]"
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


def _eco_edit_help_message(features_ref, console_ref, save_features_func):
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


def _eco_manage_commands(
    features_ref, console_ref, save_features_func, clear_terminal_func
):
    """Manages all commands, allowing edits only to custom ones."""
    if "commands" not in features_ref or not isinstance(features_ref["commands"], list):
        features_ref["commands"] = []

    SYSTEM_COMMANDS = ["products", "search"]

    while True:
        clear_terminal_func()
        console_ref.print(
            Align.center(
                Panel.fit(
                    "🔧 [bold]Manage Eco Commands[/bold] 🔧",
                    border_style="green",
                    padding=(1, 1),
                )
            )
        )

        all_commands = features_ref.get("commands", [])
        cmd_table = Table(
            title="⌨️ Current Commands",
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
                "[italic yellow]🤷 No commands configured yet. Add one![/italic yellow]"
            )
        else:
            for i, cmd in enumerate(all_commands):
                cmd_name = cmd.get("name", "N/A")
                response = cmd.get("response")
                session = cmd.get("session")
                response_preview = ""
                cmd_type = "Custom"

                if cmd_name in SYSTEM_COMMANDS:
                    cmd_type = "System"

                if session and isinstance(session, dict):
                    response_preview = f"[Session: {list(session.keys())[0]}]"
                elif isinstance(response, str):
                    response_preview = response[:70] + (
                        "..." if len(response) > 70 else ""
                    )
                elif isinstance(response, list) and cmd_name == "products":
                    product_count = len(response)
                    response_preview = f"[{product_count} product(s) loaded]"
                elif cmd_name == "search":
                    response_preview = "[Auto-handled search]"
                else:  # Catch-all for other types
                    response_preview = f"[Data Type: {type(response).__name__}]"

                cmd_table.add_row(
                    str(i + 1), f"/{cmd_name}", response_preview, cmd_type
                )
            console_ref.print(cmd_table)

        console_ref.print("\n[bold]Options:[/bold]")
        console_ref.print("  [cyan]1.[/cyan] ➕ Add New Command")
        console_ref.print("  [cyan]2.[/cyan] ✏️ Edit a Custom Command")
        console_ref.print("  [cyan]3.[/cyan] 🗑️ Remove a Custom Command")
        console_ref.print("  [cyan]0.[/cyan] 🔙 Back to Eco Config Menu")
        choice = console_ref.input("[magenta]👉 Select: [/]").strip()
        action_taken = False

        if choice == "1":
            cmd_name = console_ref.input(
                "[cyan]⌨️ New command name (e.g., 'status', no slash): [/]"
            ).strip()
            if cmd_name.lower() in SYSTEM_COMMANDS:
                console_ref.print(
                    f"[red]❌ The '/{cmd_name}' command is a system command. Please choose a different name.[/red]"
                )
            elif cmd_name:
                session_data = _get_session_response(console_ref)
                if session_data:
                    cmd_resp = None
                else:
                    cmd_resp = console_ref.input(
                        f"[cyan]💬 Response for '/{cmd_name}' (use \\n for new lines): [/]"
                    ).strip()

                features_ref["commands"].append(
                    {"name": cmd_name, "response": cmd_resp, "session": session_data}
                )
                save_features_func(features_ref)
                console_ref.print(f"[green]✅ Command '/{cmd_name}' added.[/green]")
                action_taken = True
            else:
                console_ref.print("[red]❌ Command name cannot be empty.[/red]")

        elif choice in ["2", "3"]:
            if not all_commands:
                console_ref.print("[red]🤷 No commands to edit or remove.[/red]")
                time.sleep(1)
                continue
            try:
                prompt_action = "edit" if choice == "2" else "remove"
                idx_str = console_ref.input(
                    f"[cyan]✏️ Enter number of command to {prompt_action}: [/]"
                ).strip()
                if not idx_str:
                    continue
                idx = int(idx_str) - 1

                if 0 <= idx < len(all_commands):
                    cmd_to_modify = all_commands[idx]
                    cmd_name = cmd_to_modify.get("name")

                    if cmd_name in SYSTEM_COMMANDS:
                        console_ref.print(
                            f"[red]❌ System command '/{cmd_name}' cannot be modified or removed here.[/red]"
                        )
                    else:
                        if choice == "2":
                            console_ref.print(
                                f"✍️ Editing command: [yellow]/{cmd_name}[/yellow]"
                            )
                            current_resp = cmd_to_modify.get("response", "")
                            new_name = (
                                console_ref.input(
                                    f"[cyan]New name (blank for '/{cmd_name}'): [/]"
                                ).strip()
                                or cmd_name
                            )
                            session_data = _get_session_response(console_ref)
                            if session_data:
                                new_resp = None
                            else:
                                new_resp = (
                                    console_ref.input(
                                        f"[cyan]New response (blank for '{current_resp}'): [/]"
                                    ).strip()
                                    or current_resp
                                )
                            features_ref["commands"][idx] = {
                                "name": new_name,
                                "response": new_resp,
                                "session": session_data,
                            }
                            save_features_func(features_ref)
                            console_ref.print("[green]✅ Command updated.[/green]")
                            action_taken = True
                        elif choice == "3":
                            removed_cmd = features_ref["commands"].pop(idx)
                            save_features_func(features_ref)
                            console_ref.print(
                                f"[green]🗑️ Command '/{removed_cmd['name']}' removed.[/green]"
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


def _eco_manage_keyboard(
    features_ref, console_ref, save_features_func, clear_terminal_func
):
    """Handles editing the main reply keyboard."""
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
    while True:
        clear_terminal_func()
        console_ref.print(
            Align.center(
                Panel.fit(
                    "⌨️ [bold]Manage Eco Keyboard[/bold] ⌨️",
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
        console_ref.print("  [cyan]0.[/cyan] 🔙 Back to Eco Config Menu")
        choice = console_ref.input("[magenta]👉 Select: [/]").strip()
        action_taken = False
        if choice == "1":
            btn_text = console_ref.input("[cyan]➕ New button text: [/]").strip()
            if btn_text:
                console_ref.print("\n[bold]Available Commands:[/bold]")

                available_commands = features_ref.get("commands", [])
                if available_commands:
                    cmd_options_table = Table(box=box.MINIMAL, show_header=False)
                    cmd_options_table.add_column("Num", style="dim")
                    cmd_options_table.add_column("Command", style="cyan")
                    cmd_options_table.add_column("Response (Preview)", style="yellow")
                    for i, cmd in enumerate(available_commands):
                        cmd_name = cmd.get("name", "N/A")
                        response_preview = ""
                        if isinstance(cmd.get("response"), str):
                            response_preview = cmd.get("response")[:50] + (
                                "..." if len(cmd.get("response")) > 50 else ""
                            )
                        elif isinstance(cmd.get("response"), list):
                            response_preview = f"[{len(cmd.get('response'))} item(s)]"
                        cmd_options_table.add_row(
                            str(i + 1), f"/{cmd_name}", response_preview
                        )
                    console_ref.print(cmd_options_table)
                    console_ref.print(
                        "[yellow]Type 'custom' to enter your own response.[/yellow]"
                    )
                else:
                    console_ref.print(
                        "[italic yellow]No commands configured. You'll need to enter a custom response.[/italic yellow]"
                    )

                resp_choice = console_ref.input(
                    "[magenta]Choose response (enter number, or type custom text/URL): [/]"
                ).strip()
                btn_resp = ""
                if resp_choice.lower() == "custom":
                    btn_resp = console_ref.input(
                        "[cyan]💬 Enter custom response for button: [/]"
                    ).strip()
                else:
                    try:
                        resp_idx = int(resp_choice) - 1
                        if 0 <= resp_idx < len(available_commands):
                            selected_cmd = available_commands[resp_idx]

                            if isinstance(selected_cmd.get("response"), list):
                                btn_resp = f"/{selected_cmd.get('name')}"
                            else:
                                btn_resp = (
                                    f"/{selected_cmd.get('name')}"
                                    if selected_cmd.get("name")
                                    else selected_cmd.get("response")
                                )

                            if selected_cmd.get("name") in ["products", "search"]:
                                btn_resp = f"/{selected_cmd.get('name')}"
                            elif isinstance(selected_cmd.get("response"), str):
                                btn_resp = selected_cmd.get("response")

                            if selected_cmd.get("name"):
                                btn_resp = f"/{selected_cmd.get('name')}"

                        else:
                            console_ref.print(
                                "[red]❌ Invalid choice. Using entered text as custom response.[/red]"
                            )
                            btn_resp = resp_choice
                    except ValueError:
                        btn_resp = resp_choice

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

                    console_ref.print("\n[bold]Available Commands:[/bold]")
                    available_commands = features_ref.get("commands", [])
                    if available_commands:
                        cmd_options_table = Table(box=box.MINIMAL, show_header=False)
                        cmd_options_table.add_column("Num", style="dim")
                        cmd_options_table.add_column("Command", style="cyan")
                        cmd_options_table.add_column(
                            "Response (Preview)", style="yellow"
                        )
                        for i, cmd in enumerate(available_commands):
                            cmd_name = cmd.get("name", "N/A")
                            response_preview = ""
                            if isinstance(cmd.get("response"), str):
                                response_preview = cmd.get("response")[:50] + (
                                    "..." if len(cmd.get("response")) > 50 else ""
                                )
                            elif isinstance(cmd.get("response"), list):
                                response_preview = (
                                    f"[{len(cmd.get('response'))} item(s)]"
                                )
                            cmd_options_table.add_row(
                                str(i + 1), f"/{cmd_name}", response_preview
                            )
                        console_ref.print(cmd_options_table)
                        console_ref.print(
                            "[yellow]Type 'custom' to enter your own response.[/yellow]"
                        )
                    else:
                        console_ref.print(
                            "[italic yellow]No commands configured. You'll need to enter a custom response.[/italic yellow]"
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
                                if 0 <= resp_idx < len(available_commands):
                                    selected_cmd = available_commands[resp_idx]
                                    if selected_cmd.get("name"):
                                        new_resp = f"/{selected_cmd.get('name')}"
                                    elif isinstance(selected_cmd.get("response"), str):
                                        new_resp = selected_cmd.get("response")
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
                    console_ref.print("[red]❌ Invalid command number.[/red]")
            except ValueError:
                console_ref.print("[red]❌ Invalid input.[/red]")
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
                    console_ref.print("[red]❌ Invalid command number.[/red]")
            except ValueError:
                console_ref.print("[red]❌ Invalid input.[/red]")
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


def _eco_view_products(features_ref, console_ref, clear_terminal_func):
    """Displays imported products from the main configuration."""
    clear_terminal_func()
    console_ref.print(
        Align.center(
            Panel.fit(
                "📦 [bold]Viewing Imported Products[/bold] 📦",
                border_style="green",
                padding=(1, 1),
            )
        )
    )

    product_cmd = next(
        (
            cmd
            for cmd in features_ref.get("commands", [])
            if cmd.get("name") == "products"
        ),
        None,
    )

    if not product_cmd or not isinstance(product_cmd.get("response"), list):
        console_ref.print(
            "[yellow]🤷 No products have been imported into the '/products' command yet.[/yellow]"
        )
        console_ref.print(
            "[yellow]👉 Use option '8' to import products from a file.[/yellow]"
        )
        return

    product_list = product_cmd["response"]
    if not product_list:
        console_ref.print("[yellow]🤷 The product list is empty.[/yellow]")
        return

    product_table = Table(
        box=box.MINIMAL, expand=False, width=min(console_ref.width - 4, 120)
    )

    if product_list:
        headers = list(product_list[0].keys())
        for header in headers:
            product_table.add_column(header, style="yellow", overflow="fold")

        for product in product_list:
            row_values = [str(product.get(h, "N/A")) for h in headers]
            product_table.add_row(*row_values)

        console_ref.print(product_table)
    else:
        console_ref.print("[yellow]Product list is empty, but command exists.[/yellow]")


def manage_eco_template_config(
    features_ref,
    console_ref,
    save_features_func,
    recursive_replace_func,
    clear_terminal_func,
    handle_bot_code_generation_func,
):
    """Main function to manage the bot's configuration."""
    if features_ref.get("template_name") != "Eco":
        console_ref.print(
            "[bold red]❌ Error: The 'Eco' template is not currently active or loaded correctly.[/]"
        )
        console_ref.print(
            f"[bold red]‼️ Please ensure '{BOT_CONFIG_FILEPATH}' contains '\"template_name\": \"Eco\"'.[/bold red]"
        )
        console_ref.input("[bold yellow]Press Enter to continue... ↩️[/]")
        return

    system_commands_to_add = {
        "products": {"name": "products", "response": []},
        "search": {"name": "search", "response": "[Auto-handled search]"},
    }
    current_command_names = {
        cmd.get("name")
        for cmd in features_ref.get("commands", [])
        if isinstance(cmd, dict) and "name" in cmd
    }

    changes_made_in_config = False
    for cmd_name, cmd_data in system_commands_to_add.items():
        if cmd_name not in current_command_names:
            features_ref.setdefault("commands", []).append(cmd_data)
            changes_made_in_config = True
            console_ref.print(
                f"[yellow]ℹ️ Added missing system command '/{cmd_name}' to configuration for display.[/yellow]"
            )

    if changes_made_in_config:
        save_features_func(features_ref)
        console_ref.print(
            "[green]✅ Configuration updated with missing system commands.[/green]"
        )
        console_ref.input("[bold yellow]\nPress Enter to continue... ↩️[/bold yellow]")

    while True:
        clear_terminal_func()
        shop_name = features_ref.get("active_template", "Your Eco Shop")
        console_ref.print(
            Align.center(
                Panel(
                    f"[bold cyan]Eco Template Admin: {shop_name}[/]",
                    border_style="cyan",
                    padding=(1, 1),
                )
            )
        )

        eco_admin_menu = Table(
            title="[b]🔧 Eco Admin Options[/b]",
            box=box.ROUNDED,
            expand=False,
            show_header=False,
            padding=(0, 1),
            width=min(console_ref.width - 4, 70),
        )
        eco_admin_menu.add_column("Opt", style="cyan", width=3)
        eco_admin_menu.add_column("Action", style="yellow")
        eco_admin_menu.add_row("1.", "🏬 Change Shop Name")
        eco_admin_menu.add_row("2.", "💬 Edit Start Message Text")
        eco_admin_menu.add_row("3.", "Change Welcome Image URL")
        eco_admin_menu.add_row("4.", "❓ Edit Help Message")
        eco_admin_menu.add_row("5.", "Manage Commands (Custom & System)")
        eco_admin_menu.add_row("6.", "🎹 Manage Main Keyboard")
        eco_admin_menu.add_row("7.", "Run Generated Bot Code")
        eco_admin_menu.add_row("8.", "📤 Export Bot Source Code")
        eco_admin_menu.add_row("9.", "📦 Import Products from File (.csv, .xlsx)")
        eco_admin_menu.add_row("10.", "View Imported Products")
        auto_send_status = (
            "✅ Enabled"
            if features_ref.get("auto_send_product_info", False)
            else "❌ Disabled"
        )
        eco_admin_menu.add_row(
            "11.", f"🤖 Toggle Auto-Send Product Info ({auto_send_status})"
        )
        eco_admin_menu.add_row("0.", "🚪 Exit")
        console_ref.print(Align.center(eco_admin_menu))

        choice = console_ref.input(
            "[bold magenta]👉 Select Eco Config option: [/]"
        ).strip()

        action_occurred_direct = False
        if choice == "1":
            _eco_edit_shop_name(
                features_ref, console_ref, save_features_func, recursive_replace_func
            )
            action_occurred_direct = True
        elif choice == "2":
            _eco_edit_start_text(features_ref, console_ref, save_features_func)
            action_occurred_direct = True
        elif choice == "3":
            _eco_edit_welcome_image(features_ref, console_ref, save_features_func)
            action_occurred_direct = True
        elif choice == "4":
            _eco_edit_help_message(features_ref, console_ref, save_features_func)
            action_occurred_direct = True
        elif choice == "5":
            _eco_manage_commands(
                features_ref, console_ref, save_features_func, clear_terminal_func
            )
        elif choice == "6":
            _eco_manage_keyboard(
                features_ref, console_ref, save_features_func, clear_terminal_func
            )
        elif choice == "7":
            script_name = "user_source_code.py"
            clear_terminal_func()
            console_ref.print(
                f"[cyan]🚀 Attempting to run [bold]{script_name}[/bold]...[/cyan]"
            )
            console_ref.print("=" * console_ref.width)
            if os.path.exists(script_name):
                try:
                    python_executable = (
                        "python3"
                        if os.system("python3 -V > /dev/null 2>&1") == 0
                        else "python"
                    )
                    exit_code = os.system(f"{python_executable} {script_name}")
                    console_ref.print("=" * console_ref.width)
                    if exit_code == 0:
                        console_ref.print(
                            f"[green]✅ [bold]{script_name}[/bold] execution finished successfully.[/green]"
                        )
                    else:
                        console_ref.print(
                            f"[yellow]⚠️ [bold]{script_name}[/bold] execution finished with exit code: {exit_code}. Check for errors above. 👆[/yellow]"
                        )
                except Exception as e:
                    console_ref.print("=" * console_ref.width)
                    console_ref.print(
                        f"[bold red]❌ An error occurred while trying to run the script: {e}[/bold red]"
                    )
            else:
                console_ref.print(
                    f"[bold red]❌ Error: Script '[bold]{script_name}[/bold]' not found.[/bold red]"
                )
                console_ref.print(
                    f"[bold red]👉 Generate/Export it first using option 8 or the main utility menu.[/bold red]"
                )
                console_ref.print("=" * console_ref.width)
            action_occurred_direct = True
        elif choice == "8":
            handle_bot_code_generation_func(
                console_ref, clear_terminal_func, action_verb="Exported from Eco Admin"
            )
            action_occurred_direct = True
        elif choice == "9":
            console_ref.input("[yellow]📂 Press enter and select file (.xlsx, .xls, .csv)...[/]")

            file_path = open_file_dialog_with_csv()
            if not file_path:
                console_ref.print("❌[red] No file selected.[/]")
                action_occurred_direct = True
                return

            file_lower = file_path.lower()
            data = None

            if file_lower.endswith(".csv"):
                console_ref.print("[cyan]Processing CSV file...[/cyan]")
                data = csv_to_json(file_path, console_ref)

            elif file_lower.endswith((".xlsx", ".xls")):
                console_ref.print("[cyan]Processing Excel file...[/cyan]")
                try:
                    data = excel_to_json(file_path)
                except Exception as e:
                    console_ref.print(f"❌[red] Error reading Excel file: {e}[/]")

            else:
                console_ref.print("❌[red] Unsupported file type. Please select an Excel or CSV file.[/]")
                action_occurred_direct = True
                return

            if data and isinstance(data, dict):
                product_list = next(iter(data.values()), [])
                if not product_list:
                    console_ref.print("❌[red] No products found in the file.[/]")
                else:
                    # Inject the products into the feature config
                    product_cmd = next(
                        (cmd for cmd in features_ref.get("commands", []) if cmd.get("name") == "products"),
                        None
                    )
                    if product_cmd:
                        product_cmd["response"] = product_list
                    else:
                        features_ref.setdefault("commands", []).append({
                            "name": "products",
                            "response": product_list
                        })

                    save_features_func(features_ref)
                    console_ref.print(
                        f"[bold green]✅ Products imported and integrated into the '/products' command in '{BOT_CONFIG_FILEPATH}'.[/bold green]"
                    )
            else:
                console_ref.print("❌[red] Failed to process the file or the file is empty.[/]")

            action_occurred_direct = True

        elif choice == "10":
            _eco_view_products(features_ref, console_ref, clear_terminal_func)
            action_occurred_direct = True
        elif choice == "11":
            current_val = features_ref.get("auto_send_product_info", False)
            features_ref["auto_send_product_info"] = not current_val
            save_features_func(features_ref)
            new_status = (
                "✅ Enabled"
                if features_ref["auto_send_product_info"]
                else "❌ Disabled"
            )
            console_ref.print(
                f"\n[green]🤖 Auto-Send Product Info is now {new_status}[/green]"
            )
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


class BotCodeGenerator:
    """Generates the Telegram bot script from the configuration data."""

    def __init__(self, config_data):
        self.config = config_data
        self.shop_name = self.config.get("active_template", "My Bot")
        self.logger = logging.getLogger("BotGenerator")
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.actual_bot_token = None

        product_cmd = next(
            (
                cmd
                for cmd in self.config.get("commands", [])
                if cmd.get("name") == "products"
            ),
            None,
        )
        self.products = (
            product_cmd.get("response")
            if product_cmd and isinstance(product_cmd.get("response"), list)
            else None
        )

        if self.products is None:
            self.logger.warning(
                "No product *list* found for '/products' command. Will be treated as a text command if defined."
            )

        try:
            token_dir = os.path.dirname(TOKEN_FILE_PATH_FOR_GENERATOR)
            if token_dir and not os.path.exists(token_dir):
                os.makedirs(token_dir, exist_ok=True)
                self.logger.info(f"Created directory for token file: {token_dir}")

            with open(TOKEN_FILE_PATH_FOR_GENERATOR, "r", encoding="utf-8") as f:
                self.actual_bot_token = f.read().strip()
            if not self.actual_bot_token:
                self.logger.warning(
                    f"Token file '{TOKEN_FILE_PATH_FOR_GENERATOR}' was found but is empty."
                )
                self.actual_bot_token = None
        except FileNotFoundError:
            self.logger.warning(
                f"Token file '{TOKEN_FILE_PATH_FOR_GENERATOR}' not found by generator. Generated script will use a placeholder."
            )
        except Exception as e:
            self.logger.error(
                f"Error reading token from '{TOKEN_FILE_PATH_FOR_GENERATOR}' by generator: {e}. Generated script will use a placeholder."
            )

    def _generate_imports(self):
        return """import logging
import os
import sys
import json
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
"""

    def _generate_bot_init(self):
        token_to_embed = (
            self.actual_bot_token
            if self.actual_bot_token
            else "YOUR_BOT_TOKEN_HERE_UPDATE_THIS_OR_ENSURE_GENERATOR_CAN_READ_TOKEN_FILE"
        )

        product_data_str = "None"
        if self.products is not None:
            product_data_str = json.dumps(self.products, indent=4)

        auto_send_flag = self.config.get("auto_send_product_info", False)
        shop_name_constant = self.shop_name.replace('"', '\\"')
        return f"""
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
BOT_TOKEN = "{token_to_embed}"

# --- Settings from Config ---
AUTO_SEND_PRODUCT_INFO = {auto_send_flag}
SHOP_NAME = "{shop_name_constant}"

# Product data is embedded directly from the configuration
PRODUCT_DATA = {product_data_str}

# State definition for our search conversation
AWAITING_QUERY = 0

if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE_UPDATE_THIS_OR_ENSURE_GENERATOR_CAN_READ_TOKEN_FILE":
    logger.critical(
        "FATAL: Telegram Bot Token is a placeholder. "
        "Please replace it with your actual bot token in this script, "
        "or ensure the generator script can read it from '{TOKEN_FILE_PATH_FOR_GENERATOR}' upon generation."
    )
"""

    def _generate_start_handler(self):
        start_config = self.config.get("start", {})
        image_url = start_config.get("image_url")
        start_text = start_config.get("text", f"Welcome to **{{SHOP_NAME}}**!")

        kb_config = self.config.get("main_keyboard", {})
        buttons_config = kb_config.get("buttons", [])
        keyboard_layout_str = "    keyboard_buttons = [\n"
        if buttons_config:
            row_buttons = []
            for i, btn_data in enumerate(buttons_config):
                btn_text_py = btn_data.get("text", f"Button {i + 1}").replace(
                    '"', '\\"'
                )
                row_buttons.append(f'KeyboardButton("{btn_text_py}")')
                if len(row_buttons) == 2 or i == len(buttons_config) - 1:
                    keyboard_layout_str += f"        [{', '.join(row_buttons)}],\n"
                    row_buttons = []
            if buttons_config and not keyboard_layout_str.strip().endswith("],\n"):
                if row_buttons:
                    keyboard_layout_str += f"        [{', '.join(row_buttons)}],\n"
        else:
            keyboard_layout_str += "    \n"
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
    user = update.effective_user
    start_text = f\"\"\"{start_text}\"\"\"
    image_url = "{image_url}"

{keyboard_layout_str}
    if image_url:
        try:
            await update.message.reply_photo(photo=image_url)
        except Exception as e:
            logger.error(f"Error sending start photo: {{e}}.")

    await update.message.reply_text(start_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
"""
        return handler_code

    def _generate_help_handler(self):
        return f"""
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = f\"\"\"Help for {{SHOP_NAME}}: /products, /search, etc.\"\"\"
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
"""

    def _generate_product_list_handler(self):
        if not self.products:
            return ""

        handler_code = """
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not PRODUCT_DATA:
        await update.message.reply_text("Sorry, no products are available at the moment.")
        return

    response_text = "🛍️ Here are our products:\\n"
    for product in PRODUCT_DATA:
        name = product.get("ProductName", "N/A")
        price = product.get("Price", "N/A")
        desc = product.get("Description", "")
        response_text += f"\\n*- {name}* -${price}\\n"
        if desc:
            response_text += f"  _{desc}_\\n"

    await update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
"""
        return handler_code

    def _generate_search_conversation(self):
        search_command_config = next(
            (
                cmd
                for cmd in self.config.get("commands", [])
                if cmd.get("name") == "search"
            ),
            None,
        )
        search_placeholder = "Please enter the product name or ID to search."
        if search_command_config and isinstance(
            search_command_config.get("response"), str
        ):
            search_placeholder = search_command_config.get("response")

        search_placeholder_py = search_placeholder.replace('"', '\\"')

        search_button_text = None
        kb_config = self.config.get("main_keyboard", {})
        buttons_config = kb_config.get("buttons", [])
        if buttons_config:
            for btn_data in buttons_config:
                if btn_data.get("response") == "/search":
                    search_button_text = btn_data.get("text")
                    break

        entry_points = "[CommandHandler('search', search_start)]"
        if search_button_text:
            regex_str = f"^{re.escape(search_button_text)}$"
            entry_points = f"[CommandHandler('search', search_start), MessageHandler(filters.Regex(r'{regex_str}'), search_start)]"

        handler_code = f"""
# --- Search Conversation Functions ---
async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Starts the search conversation by asking the user for a query.'''
    await update.message.reply_text("{search_placeholder_py}")
    return AWAITING_QUERY

async def search_receive_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Receives the user's search query, performs the search, and ends the conversation.'''
    search_query = update.message.text.lower()
    
    if not PRODUCT_DATA:
        await update.message.reply_text("No products are available to search.")
        return ConversationHandler.END

    found_products = []
    for product in PRODUCT_DATA:
        product_name = str(product.get("ProductName", product.get("name", ""))).lower()
        # Check for multiple possible ID keys: ProductID, id, SKU
        product_id = str(product.get("ProductID", product.get("id", product.get("SKU", "")))).lower()
        
        if search_query in product_name or (product_id and search_query == product_id):
            found_products.append(product)

    if not found_products:
        await update.message.reply_text(f"Sorry, no products found matching '{{search_query}}'.")
    else:
        response_text = f"🔎 Found {{len(found_products)}} matching products:\\n"
        for product in found_products:
            name = product.get("ProductName", "N/A")
            price = product.get("Price", "N/A")
            desc = product.get("Description", "")
            response_text += f"\\n*- {{name}}* -${{price}}\\n"
            if desc:
                response_text += f"  _{{desc}}_\\n"
        await update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)

    return ConversationHandler.END

async def search_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Cancels the search conversation if the user sends /cancel.'''
    await update.message.reply_text("Search has been cancelled.")
    return ConversationHandler.END
"""

        registration_code = f"""# Add ConversationHandler for the search functionality
search_conv_handler = ConversationHandler(
    entry_points={entry_points},
    states={{
        AWAITING_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_receive_query)],
    }},
    fallbacks=[CommandHandler('cancel', search_cancel)],
)
application.add_handler(search_conv_handler)"""
        return handler_code, registration_code

    def _generate_simple_command_handlers(self):
        """
        Generates simple text-response handlers for all commands that are not special cases.
        """
        handlers_code = ""
        registrations = []

        special_commands = ["start", "help", "search"]
        if self.products:
            special_commands.append("products")

        commands_to_generate = [
            cmd
            for cmd in self.config.get("commands", [])
            if cmd.get("name") not in special_commands
        ]

        for cmd_config in commands_to_generate:
            name = cmd_config.get("name")
            if not name:
                continue

            session_data = cmd_config.get("session")
            if session_data and isinstance(session_data, dict):
                session_content = list(session_data.values())[0]
                response_template_py = json.dumps(session_content, indent=4)
            else:
                response_template_py = cmd_config.get("response", "").replace(
                    "\\n", "\n"
                )

            func_name_base = "".join(c if c.isalnum() else "_" for c in name)
            func_name = f"cmd_{func_name_base}"

            handlers_code += f"""
async def {func_name}(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response_text = f\"\"\"{response_template_py}\"\"\"
    await update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
"""
            registrations.append(
                f'application.add_handler(CommandHandler("{name}", {func_name}))'
            )

        return handlers_code, registrations

    def _generate_text_trigger_handler(self):
        """
        Generates a handler that triggers command functions based on exact text matches from keyboard buttons.
        """
        map_str = "KEYBOARD_COMMAND_MAP = {\n"
        kb_config = self.config.get("main_keyboard", {})
        buttons_config = kb_config.get("buttons", [])
        has_mapped_buttons = False

        search_button_text = None
        for btn_data in buttons_config:
            if btn_data.get("response") == "/search":
                search_button_text = btn_data.get("text")
                break

        for btn_data in buttons_config:
            btn_text = btn_data.get("text")
            btn_resp = btn_data.get("response")
            if (
                btn_text
                and btn_resp
                and btn_resp.startswith("/")
                and btn_text != search_button_text
            ):
                command_name = btn_resp[1:]
                btn_text_py = btn_text.replace('"', '\\"')
                map_str += f'    "{btn_text_py}": "{command_name}",\n'
                has_mapped_buttons = True
        map_str += "}\n"

        auto_send_enabled = self.config.get("auto_send_product_info", False)

        if not has_mapped_buttons and not (auto_send_enabled and self.products):
            return "", ""

        handler_code = f"""
{map_str}
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    command_name = KEYBOARD_COMMAND_MAP.get(message_text)

    if command_name and command_name in COMMAND_HANDLERS:
        await COMMAND_HANDLERS[command_name](update, context)
        return

    if AUTO_SEND_PRODUCT_INFO and PRODUCT_DATA:
        message_text_lower = message_text.lower().strip()
        for product in PRODUCT_DATA:
            product_name = str(product.get("ProductName", product.get("name", ""))).lower()
            if message_text_lower == product_name:
                name = product.get("ProductName", "N/A")
                price = product.get("Price", "N/A")
                desc = product.get("Description", "")
                response_text = f"*- {{name}}* -${{price}}\\n"
                if desc:
                    response_text += f"  _{{desc}}_\\n"
                await update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
                return
"""
        registration_code = "# A general text handler for other keyboard buttons and auto-product info\n"
        registration_code += "application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))"
        return handler_code, registration_code

    def generate_full_script(self):
        imports = self._generate_imports()
        bot_init = self._generate_bot_init()

        all_handlers_code = []

        all_handlers_code.append(self._generate_start_handler())
        all_handlers_code.append(self._generate_help_handler())

        product_list_handler = self._generate_product_list_handler()
        if product_list_handler:
            all_handlers_code.append(product_list_handler)

        search_conv_code, search_reg_code_block = self._generate_search_conversation()
        all_handlers_code.append(search_conv_code)

        simple_cmd_code, simple_cmd_reg_list = self._generate_simple_command_handlers()
        all_handlers_code.append(simple_cmd_code)

        text_trigger_code, text_trigger_reg_code = self._generate_text_trigger_handler()
        all_handlers_code.append(text_trigger_code)

        command_map_str = "\n# This map is for simple text-based commands that are not part of a conversation.\n"
        command_map_str += "COMMAND_HANDLERS = {\n"
        for cmd in self.config.get("commands", []):
            cmd_name = cmd.get("name")
            if not cmd_name or cmd_name in ["start", "help", "search"]:
                continue

            if cmd_name == "products" and self.products:
                func_name = "show_products"
            else:
                func_name_base = "".join(c if c.isalnum() else "_" for c in cmd_name)
                func_name = f"cmd_{func_name_base}"
            command_map_str += f'    "{cmd_name}": {func_name},\n'
        command_map_str += "}\n"
        all_handlers_code.append(command_map_str)

        main_body = [
            "    application = Application.builder().token(BOT_TOKEN).build()",
            "\n    # Register basic command handlers",
            '    application.add_handler(CommandHandler("start", start_command))',
            '    application.add_handler(CommandHandler("help", help_command))',
        ]

        if product_list_handler:
            main_body.append("\n    # Register product list handler if it exists")
            main_body.append(
                '    application.add_handler(CommandHandler("products", show_products))'
            )

        if search_reg_code_block:
            main_body.append("")
            for line in search_reg_code_block.strip().split("\n"):
                main_body.append(f"    {line}")

        if simple_cmd_reg_list:
            main_body.append("\n    # Register all other simple command handlers")
            for reg_line in simple_cmd_reg_list:
                main_body.append(f"    {reg_line}")

        if text_trigger_reg_code:
            main_body.append("")
            for line in text_trigger_reg_code.strip().split("\n"):
                main_body.append(f"    {line}")

        main_func = f"""
def main() -> None:
{chr(10).join(main_body)}

    logger.info(f"Bot '{{SHOP_NAME}}' is starting... Polling for updates.")
    application.run_polling()

if __name__ == "__main__":
    main()
"""

        return f"{imports}\n{bot_init}\n{''.join(all_handlers_code)}\n{main_func}"

    def save_script(self, console_ref: Console, filename="user_source_code.py"):
        script_content = self.generate_full_script()
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(script_content)
            console_ref.print(
                f"[green]✅ Bot script '{self.shop_name}' successfully generated and saved to '{filename}'[/green]"
            )
        except IOError as e:
            console_ref.print(f"[red]❌ Error saving script to '{filename}': {e}[/red]")


def _handle_bot_code_generation(
    console_ref: Console, clear_terminal_func, action_verb="Generated"
):
    clear_terminal_func()
    title_verb = "Generate" if action_verb == "Generated" else "Export"
    if "export" in action_verb.lower():
        title_verb = "Export"

    console_ref.print(
        Panel.fit(
            f"[bold green]🤖 Telegram Bot Code {title_verb}r[/bold green]",
            padding=(0, 2),
        )
    )
    generated_script_path = "user_source_code.py"
    console_ref.print(
        f"\n[cyan]⚙️ Attempting to {title_verb.lower()} bot code from: '{BOT_CONFIG_FILEPATH}'[/cyan]"
    )
    console_ref.print(
        f"[cyan]💾 {action_verb} code will be saved to: '{generated_script_path}'[/cyan]\n"
    )
    try:
        with open(BOT_CONFIG_FILEPATH, "r", encoding="utf-8") as f:
            content = f.read()
            if not content:
                raise json.JSONDecodeError("File is empty", content, 0)
            bot_config_data = json.loads(content)

        generator = BotCodeGenerator(bot_config_data)
        generator.save_script(console_ref, generated_script_path)

        console_ref.print("\n[bold green]To run your new bot:[/bold green]")
        console_ref.print(
            "1. Ensure 'python-telegram-bot' is installed: [cyan]pip install python-telegram-bot[/cyan]"
        )
        if generator.actual_bot_token:
            console_ref.print(
                f"2. ✅ Bot token was read from [cyan]{TOKEN_FILE_PATH_FOR_GENERATOR}[/cyan] and embedded in the script."
            )
        else:
            console_ref.print(
                f"2. [yellow]⚠️ Warning:[/yellow] Bot token was [bold red]NOT[/bold] read from [cyan]{TOKEN_FILE_PATH_FOR_GENERATOR}[/cyan]."
            )
            console_ref.print(
                f"   👉 Please manually edit [cyan]{generated_script_path}[/cyan] and set the `BOT_TOKEN` variable."
            )
        console_ref.print(
            f"3. Run the script: [cyan]python {generated_script_path}[/cyan]"
        )

    except (FileNotFoundError, json.JSONDecodeError):
        console_ref.print(
            f"❌ [bold red]Error: Bot configuration file '{BOT_CONFIG_FILEPATH}' not found or is invalid.[/bold red]"
        )
        console_ref.print(
            f"   [yellow]👉 Please run the utility again to create a new configuration file.[/yellow]"
        )
    except Exception as e:
        console_ref.print(
            f"❌ [bold red]An unexpected error occurred during bot code generation: {e}[/bold red]"
        )

    console_ref.print(f"\n[blue]🔙 Returning to the previous menu...[/blue]")
    console_ref.input("[yellow]Press Enter to continue... ↩️[/yellow]")


def main():
    console = Console()

    def clear_terminal_main():
        os.system("cls" if os.name == "nt" else "clear")

    def save_bot_config_main(features_dict, filepath=BOT_CONFIG_FILEPATH):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(features_dict, f, indent=4)
        except IOError as e:
            console.print(f"[red]❌ Error saving features to {filepath}: {e}[/red]")

    def _recursive_replace_main(data_struct, old_val, new_val):
        if isinstance(data_struct, dict):
            return {
                k: _recursive_replace_main(v, old_val, new_val)
                for k, v in data_struct.items()
            }
        elif isinstance(data_struct, list):
            return [
                _recursive_replace_main(item, old_val, new_val) for item in data_struct
            ]
        elif isinstance(data_struct, str):
            return data_struct.replace(old_val, new_val)
        return data_struct

    clear_terminal_main()
    console.print(
        Panel.fit(
            "[bold green]⚙️ Eco Template Configuration Manager[/bold green]",
            padding=(0, 2),
        )
    )
    try:
        with open(BOT_CONFIG_FILEPATH, "r", encoding="utf-8") as f:
            content = f.read()
            if not content:
                raise json.JSONDecodeError("File is empty", content, 0)
            features_data = json.loads(content)
        console.print(
            f"[green]✅ Loaded bot config from '{BOT_CONFIG_FILEPATH}'[/green]\n"
        )
    except (FileNotFoundError, json.JSONDecodeError):
        console.print(f"[yellow]⚠️ Could not load '{BOT_CONFIG_FILEPATH}'.[/yellow]")
        console.print(
            "[yellow]🛠️ Initializing with default Eco template structure.[/yellow]\n"
        )
        features_data = {
            "template_name": "Eco",
            "active_template": "My New Eco Shop",
            "start": {"text": "Welcome to My New Eco Shop!", "image_url": ""},
            "help": "Default help: Use /products, /cart, etc.",
            "commands": [
                {"name": "products", "response": []},
                {
                    "name": "search",
                    "response": "[Auto-handled search]",
                },
            ],
            "main_keyboard": {"buttons": [], "resize": True, "persistent": False},
            "auto_send_product_info": False,
        }
        save_bot_config_main(features_data, BOT_CONFIG_FILEPATH)

    manage_eco_template_config(
        features_data,
        console,
        save_bot_config_main,
        _recursive_replace_main,
        clear_terminal_main,
        _handle_bot_code_generation,
    )

    console.print("\n[yellow]👋 Exiting utility. Goodbye![/yellow]")


if __name__ == "__main__":
    main()
