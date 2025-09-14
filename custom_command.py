import json
import os
from common import INPUT_COLOR, RESET_COLOR, OPTION_COLOR, SUCCESS_COLOR, ERROR_COLOR, INFO_COLOR, BOLD

USER_BOT_FILE = "user_bot.json"  
SESSIONS_FILE = "sessions.json"

def load_custom_commands():
    """Load custom commands from user_bot.json"""
    if os.path.exists(USER_BOT_FILE):
        with open(USER_BOT_FILE, "r") as f:
            data = json.load(f)
            return data.get('custom_commands', {}), data
    return {}, {'custom_commands': {}}  

def save_custom_commands(custom_commands, additional_data=None):
    """Save custom commands to user_bot.json"""
    data = {'custom_commands': custom_commands}
    if additional_data:
        data.update(additional_data)
    with open(USER_BOT_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_session_response():
    """Helper function to get session response from sessions.json"""
    session_data = None
    use_session = input(f"{INPUT_COLOR}❓ Use a session for reply? (yes/no): {RESET_COLOR}").strip().lower()
    
    if use_session == "yes":
        if not os.path.exists(SESSIONS_FILE):
            print(f"{ERROR_COLOR}⚠️ No sessions file found!{RESET_COLOR}")
        else:
            with open(SESSIONS_FILE, "r") as f:
                sessions = json.load(f)
            
            if sessions:
                print(f"{OPTION_COLOR}Available sessions:{RESET_COLOR}")
                for idx, sess in enumerate(sessions.keys(), 1):
                    print(f"   {idx}. {sess}")
                
                sess_choice = int(input(f"{INPUT_COLOR}👉 Choose session (1-{len(sessions)}): {RESET_COLOR}"))
                if 1 <= sess_choice <= len(sessions):
                    chosen_session = list(sessions.keys())[sess_choice - 1]
                    session_data = sessions[chosen_session]
                    print(f"{SUCCESS_COLOR}✅ Using session: {chosen_session}{RESET_COLOR}")
                else:
                    print(f"{ERROR_COLOR}⚠️ Invalid selection!{RESET_COLOR}")
            else:
                print(f"{INFO_COLOR}ℹ️ No sessions available{RESET_COLOR}")
    
    return session_data

def custom_command():
    try:
        custom_commands, user_bot_data = load_custom_commands()

        print(f"""{OPTION_COLOR}
                ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                🔧 {BOLD}Custom Command Menu ✏️{RESET_COLOR}
                ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                📌 {BOLD}What you can do here:{RESET_COLOR}

                1️⃣ ➕ Add a new custom command  
                2️⃣ 🛠️ Edit your existing commands  
                3️⃣ 📦 Use a ready-made command (/weather, /time, /date)  
                ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                {RESET_COLOR}""")

        choice_custom = int(input(f"{INPUT_COLOR}👉 Choose an option (1-3): {RESET_COLOR}"))

        if choice_custom == 1:
            print(f"""{OPTION_COLOR}
                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    ➕ {BOLD}Add New Custom Command{RESET_COLOR}
                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    🎯 Types of custom triggers your bot can respond to:

                    1️⃣ Text-based trigger → (User says "hello")  
                    2️⃣ Image trigger → (User says "cat")  
                    3️⃣ Slash command → (User sends /time)
                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    {RESET_COLOR}""")
            cmd_type = int(input(f"{INPUT_COLOR}📌 Select trigger type (1-3): {RESET_COLOR}"))
            
            if cmd_type in [4, 5]:  
                cmd_name = "/start" if cmd_type == 4 else "/help"
                key = cmd_name[1:]  
                
                current_text = user_bot_data.get(key, "")
                print(f"{OPTION_COLOR}Current {cmd_name} message:{RESET_COLOR}")
                print(f"{INFO_COLOR}{current_text}{RESET_COLOR}")
                
                session_data = get_session_response()
                if not session_data:
                    new_text = input(f"{INPUT_COLOR}📝 Enter new {cmd_name} message: {RESET_COLOR}").strip()
                    user_bot_data[key] = new_text
                else:
                    user_bot_data[key] = None
                user_bot_data[f"{key}_session"] = session_data
                print(f"{SUCCESS_COLOR}✅ {cmd_name} message updated!{RESET_COLOR}")
            else:
                session_data = get_session_response()

                if cmd_type == 1:  
                    trigger = input(f"{INPUT_COLOR}💬 Trigger phrase (e.g., hello): {RESET_COLOR}").strip().lower()
                    response = None if session_data else input(f"{INPUT_COLOR}📝 Bot response: {RESET_COLOR}").strip()
                    
                    custom_commands[trigger] = {
                        'type': 'text',
                        'trigger': trigger,
                        'response': response,
                        'session': session_data
                    }
                    print(f"{SUCCESS_COLOR}✅ Added text trigger for '{trigger}'!{RESET_COLOR}")

                elif cmd_type == 3:  
                    cmd_name = input(f"{INPUT_COLOR}⌨️ Command name (without /): {RESET_COLOR}").strip().lower()
                    response = None if session_data else input(f"{INPUT_COLOR}📝 Bot response: {RESET_COLOR}").strip()
                    
                    custom_commands[f"/{cmd_name}"] = {
                        'type': 'command',
                        'trigger': f"/{cmd_name}",
                        'response': response,
                        'description': input(f"{INPUT_COLOR}🖋️ Description: {RESET_COLOR}").strip(),
                        'session': session_data
                    }
                    print(f"{SUCCESS_COLOR}✅ Added /{cmd_name} command!{RESET_COLOR}")

        elif choice_custom == 2:
            all_commands = {}
            
            all_commands.update(custom_commands)
            
            if 'start' in user_bot_data:
                all_commands['/start'] = {
                    'type': 'system',
                    'response': user_bot_data.get('start'),
                    'session': user_bot_data.get('start_session'),
                    'description': 'Welcome message'
                }
            if 'help' in user_bot_data:
                all_commands['/help'] = {
                    'type': 'system',
                    'response': user_bot_data.get('help'),
                    'session': user_bot_data.get('help_session'),
                    'description': 'Help message'
                }

            if not all_commands:
                print(f"{ERROR_COLOR}⚠️ No commands to edit!{RESET_COLOR}")
            else:
                print(f"{OPTION_COLOR}Available Commands:{RESET_COLOR}")
                commands_list = list(all_commands.keys())
                for idx, cmd in enumerate(commands_list, 1):
                    desc = all_commands[cmd].get('description', 'No description')
                    print(f"   {idx}. {cmd} - {desc}")

                cmd_choice = int(input(f"{INPUT_COLOR}👉 Choose a command to edit (1-{len(commands_list)}): {RESET_COLOR}"))
                if 1 <= cmd_choice <= len(commands_list):
                    cmd_name = commands_list[cmd_choice - 1]
                    command_data = all_commands[cmd_name]

                    if cmd_name in ['/start', '/help']:
                        key = cmd_name[1:]  
                        print(f"""{OPTION_COLOR}
                            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                            ✏️ {BOLD}Edit {cmd_name} Message{RESET_COLOR}
                            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                            Current: {user_bot_data.get(key, 'None')}
                            Session: {'Yes' if user_bot_data.get(f'{key}_session') else 'No'}
                            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                            {RESET_COLOR}""")
                        session_data = get_session_response()
                        if not session_data:
                            new_resp = input(f"{INPUT_COLOR}📝 New message for {cmd_name}: {RESET_COLOR}").strip()
                            user_bot_data[key] = new_resp
                        else:
                            user_bot_data[key] = None
                        user_bot_data[f"{key}_session"] = session_data
                        print(f"{SUCCESS_COLOR}✅ Updated {cmd_name} message!{RESET_COLOR}")
                    else:
                        print(f"""{OPTION_COLOR}
                            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                            🔧 {BOLD}Edit Command: {cmd_name}{RESET_COLOR}
                            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                            1️⃣ Edit Response  
                            2️⃣ Edit Description  
                            3️⃣ Remove Command  
                            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                            {RESET_COLOR}""")
                        
                        edit_choice = int(input(f"{INPUT_COLOR}👉 Choose an option (1-3): {RESET_COLOR}"))

                        if edit_choice == 1:  
                            session_data = get_session_response()
                            if not session_data:
                                new_response = input(f"{INPUT_COLOR}📝 New response: {RESET_COLOR}").strip()
                                custom_commands[cmd_name]['response'] = new_response
                            else:
                                custom_commands[cmd_name]['response'] = None
                            custom_commands[cmd_name]['session'] = session_data
                            print(f"{SUCCESS_COLOR}✅ Response updated!{RESET_COLOR}")

                        elif edit_choice == 2:  
                            if cmd_name.startswith('/'):
                                new_description = input(f"{INPUT_COLOR}🖋️ New description: {RESET_COLOR}").strip()
                                custom_commands[cmd_name]['description'] = new_description
                                print(f"{SUCCESS_COLOR}✅ Description updated!{RESET_COLOR}")
                            else:
                                print(f"{ERROR_COLOR}⚠️ Description can only be edited for slash commands!{RESET_COLOR}")

                        elif edit_choice == 3:  
                            confirm_remove = input(f"{INPUT_COLOR}Are you sure you want to delete {cmd_name}? (yes/no): {RESET_COLOR}").strip().lower()
                            if confirm_remove == 'yes':
                                if cmd_name in custom_commands:
                                    del custom_commands[cmd_name]
                                    print(f"{SUCCESS_COLOR}✅ Command {cmd_name} removed!{RESET_COLOR}")
                            else:
                                print(f"{INFO_COLOR}ℹ️ Command removal canceled!{RESET_COLOR}")

                        else:
                            print(f"{ERROR_COLOR}⚠️ Invalid choice!{RESET_COLOR}")
                else:
                    print(f"{ERROR_COLOR}⚠️ Invalid selection!{RESET_COLOR}")

        elif choice_custom == 3:
            while True:
                print(f"""{OPTION_COLOR}
                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    📦 {BOLD}Ready-Made Commands{RESET_COLOR}
                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    1️⃣ /weather   - Shows weather forecast for cities
                    2️⃣ /time      - Displays current time  
                    3️⃣ /date      - Shows today's date (Gregorian/Jalali)
                    4️⃣ /dollar    - Shows USD to IRR exchange rates
                    5️⃣ /gold      - Shows current gold coin prices
                    6️⃣ /crypto    - Shows popular cryptocurrency prices
                    7️⃣ /jokes     - Tells random jokes
                    8️⃣ /calendar  - Shows Persian calendar events
                    9️⃣ exit       - Go back to previous menu
                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    {RESET_COLOR}""")

                choice = int(input(f"{INPUT_COLOR}⏳ Choose (1-9): {RESET_COLOR}"))

                if choice == 9:
                    break  

                commands = {
                    1: ('/weather', None, 'Weather information'),
                    2: ('/time', None, 'Current time'),
                    3: ('/date', None, 'Current date'),
                    4: ('/dollar', None, 'Dollar exchange rate'),
                    5: ('/gold', None, 'Gold prices'),
                    6: ('/crypto', None, 'Crypto prices'),
                    7: ('/jokes', None, 'Tell a joke'),
                    8: ('/calendar', None, 'Calendar events')
                }

                if choice in commands:
                    cmd, _, desc = commands[choice]
                    session_data = get_session_response()

                    custom_commands[cmd] = {
                        'type': 'command',
                        'trigger': cmd,
                        'response': None,
                        'description': desc,
                        'session': session_data
                    }

                    print(f"{SUCCESS_COLOR}✅ Added {cmd} command!{RESET_COLOR}")
                else:
                    print(f"{ERROR_COLOR}❌ Invalid choice! Try again.{RESET_COLOR}")
        
        save_custom_commands(custom_commands, user_bot_data)

    except ValueError:
        print(f"{ERROR_COLOR}⚠️ Please enter a valid number!{RESET_COLOR}")
    except Exception as e:
        print(f"{ERROR_COLOR}❌ Error: {str(e)}{RESET_COLOR}")

    input(f"{INPUT_COLOR}Press Enter to continue...{RESET_COLOR}")
