#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import os
import subprocess
import sys
from telegram_bot_maker import (
    handle_add_help,
    handle_add_start,
    save_bot_code,
    custom_command,
    create_new_session,
    handle_template,
    handle_explain,
    handle_run_bot,
    
    )





class BotCodeGenerator:
    def __init__(self, features):
        self.features = features

    def generate_code(self):
        return "# This is dummy bot code generated based on features:\n" + str(
            self.features
        )


features = {}
BOT_SCRIPT_FILENAME = "user_source_code.py"


class TelegramBotMakerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Bot Maker")
        self.root.geometry("600x510")

        self.frame = tk.Frame(self.root, padx=10, pady=10)
        self.frame.pack(fill="both", expand=True)

        tk.Label(
            self.frame, text="Telegram Bot Maker", font=("Arial", 16, "bold"), fg="cyan"
        ).pack(pady=10)

        self.menu_items = [
            ("1. /start 🚀", "Edit welcome message.", handle_add_start),
            ("2. /help ❓", "Configure help response.", handle_add_help),
            ("3. /commands 💡", "Manage custom commands.", custom_command),
            ("4. /generate 💾", "Export bot source code.", self.handle_generate),
            (
                "5. /sessions 👥",
                "Manage user sessions (Placeholder).",
                create_new_session,
            ),
            (
                "6. /keyboard 💻",
                "Design custom keyboard.(but first /generate)",
                self.handle_keyboard,
            ),
            ("7. /template 📋", "Apply a pre-built template.", handle_template),
            ("8. /explain 🤖", "AI code explanation.", handle_explain),
            ("9. /gui", "Open experimental GUI.", self.refresh_gui),
            ("11. /run ⚡", "Run the bot.", handle_run_bot),
            ("12. /clear 🗑", "Run the bot.", handle_run_bot),
            ("13. /exit 🚪", "Exit the application.", self.exit_app),
        ]

        for option, desc, func in self.menu_items:
            btn_text = f"{option} - {desc}"
            btn = tk.Button(
                self.frame,
                text=btn_text,
                font=("Arial", 10),
                command=func,
                anchor="w",
                relief="flat",
                bg="#f0f0f0",
                justify="left",
            )
            btn.pack(fill="x", pady=2)

        self.output_text = scrolledtext.ScrolledText(
            self.frame, height=10, font=("Arial", 10)
        )
        self.output_text.pack(fill="both", expand=True, pady=10)

        self.output_text.insert(tk.END, "Welcome to Telegram Bot Maker GUI!\n")

    def handle_generate(self):
        """Generates the bot code and saves it to a file."""
        if not features:
            self.output_text.insert(
                tk.END, "⚠️ No configuration found! Add features before generating.\n"
            )
            return
        generator = BotCodeGenerator(features)
        bot_code = generator.generate_code()
        success, result = save_bot_code(bot_code, BOT_SCRIPT_FILENAME)
        if success:
            self.output_text.insert(tk.END, f"✅ Bot code saved to: {result}\n")
            self.output_text.insert(
                tk.END, f"You can now run the bot using the 'Run the bot' button.\n"
            )
        else:
            self.output_text.insert(tk.END, f"❌ Error saving code: {result}\n")

   

        try:
            self.output_text.insert(
                tk.END, f"🚀 Attempting to start the bot script...\n"
            )
            self.output_text.insert(
                tk.END, "A new terminal window should open to run the bot.\n"
            )

            if sys.platform == "win32":
                subprocess.Popen(
                    ["start", "cmd", "/k", "python", BOT_SCRIPT_FILENAME], shell=True
                )
            elif sys.platform == "darwin":
                subprocess.Popen(
                    ["open", "-a", "Terminal", os.path.abspath(BOT_SCRIPT_FILENAME)]
                )
            else:
                terminals = [
                    "gnome-terminal",
                    "konsole",
                    "xfce4-terminal",
                    "lxterminal",
                    "xterm",
                ]
                cmd = ["python3", os.path.abspath(BOT_SCRIPT_FILENAME)]
                for term in terminals:
                    try:
                        subprocess.Popen([term, "-e"] + cmd)
                        return
                    except FileNotFoundError:
                        continue
                self.output_text.insert(
                    tk.END, f"❌ Could not automatically open a terminal.\n"
                )
                self.output_text.insert(
                    tk.END, f"Please run manually: python3 {BOT_SCRIPT_FILENAME}\n"
                )

        except Exception as e:
            self.output_text.insert(tk.END, f"❌ Failed to run bot script: {e}\n")

    def handle_keyboard(self):
        """A simplified keyboard designer for the GUI."""
        self.output_text.insert(tk.END, "🎮 KEYBOARD DESIGNER\n")
        self.output_text.insert(
            tk.END,
            "NOTE: For this demo, buttons will just reply with their own text.\n",
        )
        buttons = []
        while True:
            btn_text = simpledialog.askstring(
                "Keyboard Designer",
                "Enter button text (or leave empty to finish):",
                parent=self.root,
            )
            if not btn_text:
                if not buttons:
                    self.output_text.insert(tk.END, "⚠️ No buttons were added.\n")
                break
            buttons.append({"text": btn_text, "response": btn_text})
            self.output_text.insert(tk.END, f"✅ Added button: '{btn_text}'\n")

        if buttons:
            features["main_keyboard"] = {
                "buttons": buttons,
                "resize": True,
                "persistent": True,
            }
            self.output_text.insert(tk.END, "✅ Keyboard layout saved successfully!\n")

    def refresh_gui(self):
        """In this context, it just prints a message."""
        self.output_text.insert(tk.END, "🖥️ GUI refreshed! (Experimental GUI opened)\n")

    def exit_app(self):
        """Asks for confirmation and exits the application."""
        if messagebox.askokcancel(
            "Exit", "Are you sure you want to exit the application?"
        ):
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = TelegramBotMakerGUI(root)
    root.mainloop()
