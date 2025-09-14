import time
from datetime import datetime
from khayyam import JalaliDatetime
import json
import os
from common import (
    features,
    INPUT_COLOR,
    RESET_COLOR,
    OPTION_COLOR,
    SUCCESS_COLOR,
    ERROR_COLOR,
    INFO_COLOR,
    BOLD,
)


def save_session_to_file(sessions_data, filename="sessions.json"):
    try:
        with open("sessions.json", "w", encoding="utf-8") as json_file:
            json.dump(sessions_data, json_file, indent=4, ensure_ascii=False)
        print(f"{SUCCESS_COLOR}✅ Sessions saved successfully.{RESET_COLOR}")
    except Exception as e:
        print(f"{ERROR_COLOR}❌ Error saving sessions: {str(e)}{RESET_COLOR}")


def create_new_session():
    try:
        if os.path.exists("sessions.json"):
            with open("sessions.json", "r", encoding="utf-8") as f:
                existing_sessions = json.load(f)
            features["sessions"] = existing_sessions
        else:
            features["sessions"] = {}
            with open("sessions.json", "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

        while True:
            print(f"""{OPTION_COLOR}
                        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        🗂️ {BOLD}Create Session Menu{RESET_COLOR}
                        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        Choose an action:
                        1️⃣ ➕ Create New Session
                        2️⃣ ✏️ Edit Existing Session
                        3️⃣ 🗑️ Delete Session
                        4️⃣ 👀 Show JSON Preview
                        5️⃣ 🔙 Return to Main Menu
                        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        {RESET_COLOR}""")

            choice_session = input(
                f"{INPUT_COLOR}👉 Choose an option (1-5): {RESET_COLOR}"
            )
            try:
                choice_session = int(choice_session)
            except ValueError:
                print(
                    f"{ERROR_COLOR}⚠️ Invalid selection. Please choose 1-5.{RESET_COLOR}"
                )
                continue

            if choice_session == 1:
                session_name = input(
                    f"{INPUT_COLOR}Enter a name for the new session: {RESET_COLOR}"
                ).strip()
                if not session_name:
                    print(f"{ERROR_COLOR}⚠️ Session name cannot be empty.{RESET_COLOR}")
                    continue

                if session_name in features["sessions"]:
                    print(
                        f"{ERROR_COLOR}⚠️ Session '{session_name}' already exists.{RESET_COLOR}"
                    )
                    continue

                session_content = features["sessions"].setdefault(session_name, [])
                print(
                    f"{SUCCESS_COLOR}Session '{session_name}' created. Now you can add content.{RESET_COLOR}"
                )

                session_content = []
                while True:
                    if session_content:
                        print(
                            f"{OPTION_COLOR}Current content in session '{session_name}':{RESET_COLOR}"
                        )
                        for idx, item in enumerate(session_content, 1):
                            if item["type"] == "text":
                                button_count = len(item.get("buttons", []))
                                if button_count > 0:
                                    print(
                                        f"{idx}. Text: {item['content']} -- {button_count} button(s)"
                                    )
                                else:
                                    print(f"{idx}. Text: {item['content']}")
                            elif item["type"] == "image":
                                button_count = len(item.get("buttons", []))
                                if button_count > 0:
                                    print(
                                        f"{idx}. Image: {item['url']} -- {button_count} button(s)"
                                    )
                                else:
                                    print(f"{idx}. Image: {item['url']}")
                            elif item["type"] == "file":
                                button_count = len(item.get("buttons", []))
                                if button_count > 0:
                                    print(
                                        f"{idx}. File: {item['path']} -- {button_count} button(s)"
                                    )
                                else:
                                    print(f"{idx}. File: {item['path']}")
                            elif item["type"] == "button":
                                button_count = len(item.get("buttons", []))
                                if button_count > 0:
                                    print(
                                        f"{idx}. Button: {item['text']} (URL: {item['url']}) -- {button_count} button(s)"
                                    )
                                else:
                                    print(
                                        f"{idx}. Button: {item['text']} (URL: {item['url']})"
                                    )
                                if "buttons" in item:
                                    for btn in item["buttons"]:
                                        print(
                                            f"    ⬆️ Inline button: {btn['text']} (URL: {btn['url']})"
                                        )
                            elif item["type"] == "wait_for_response":
                                timeout_info = (
                                    f" (timeout: {item['timeout']}s)"
                                    if item.get("timeout")
                                    else ""
                                )
                                print(
                                    f"{idx}. ⏳ Wait for Response: Will store user input as '{item['variable']}'{timeout_info}"
                                )
                    else:
                        print(f"{OPTION_COLOR}No content in session yet.{RESET_COLOR}")

                    print(f"""{OPTION_COLOR}
                                Add content to the session:
                                1. Add Text
                                2. Add Image
                                3. Add File
                                4. Add Button
                                5. Ready Templates
                                6. Change Position (Indent or Place)
                                7. Delete item from session
                                8. Add Function to Button - - not working yet
                                9. Add Wait for Response
                                0. Done
                    {RESET_COLOR}""")
                    try:
                        choice_content = int(
                            input(
                                f"{INPUT_COLOR}👉 Choose an option (1-0): {RESET_COLOR}"
                            )
                        )
                    except ValueError:
                        print(f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}")
                        continue

                    if choice_content == 1:
                        text = input(
                            f"{INPUT_COLOR}Enter the text content: {RESET_COLOR}"
                        ).strip()
                        if not text:
                            print(
                                f"{ERROR_COLOR}⚠️ Text content cannot be empty.{RESET_COLOR}"
                            )
                            continue
                        session_content.append({"type": "text", "content": text})
                        print(f"{SUCCESS_COLOR}Text added to session.{RESET_COLOR}")
                        features["sessions"][session_name] = session_content
                        save_session_to_file(features["sessions"])
                    elif choice_content == 2:
                        image_url = input(
                            f"{INPUT_COLOR}Enter the image URL: {RESET_COLOR}"
                        ).strip()
                        if not image_url:
                            print(
                                f"{ERROR_COLOR}⚠️ Image URL cannot be empty.{RESET_COLOR}"
                            )
                            continue

                        add_text = (
                            input(
                                f"{INPUT_COLOR}Do you want to add text to this image? (y/n): {RESET_COLOR}"
                            )
                            .strip()
                            .lower()
                        )
                        image_item = {"type": "image", "url": image_url}

                        if add_text == "y":
                            image_text = input(
                                f"{INPUT_COLOR}Enter the text to display with the image: {RESET_COLOR}"
                            ).strip()
                            if image_text:
                                image_item["caption"] = image_text
                                print(
                                    f"{SUCCESS_COLOR}Text added to image.{RESET_COLOR}"
                                )

                            print(f"""{OPTION_COLOR}
                            Choose text position:
                            1️⃣ Above the image
                            2️⃣ Below the image
                            3️⃣ As caption (overlay on image)
                            {RESET_COLOR}""")

                            try:
                                text_position = int(
                                    input(
                                        f"{INPUT_COLOR}👉 Choose text position (1-3): {RESET_COLOR}"
                                    )
                                )
                                if text_position == 1:
                                    image_item["text_position"] = "above"
                                elif text_position == 2:
                                    image_item["text_position"] = "below"
                                elif text_position == 3:
                                    image_item["text_position"] = "overlay"
                                else:
                                    print(
                                        f"{ERROR_COLOR}⚠️ Invalid position. Using default (below).{RESET_COLOR}"
                                    )
                                    image_item["text_position"] = "below"
                            except ValueError:
                                print(
                                    f"{ERROR_COLOR}⚠️ Invalid input. Using default position (below).{RESET_COLOR}"
                                )
                                image_item["text_position"] = "below"

                        # add_buttons = input(f"{INPUT_COLOR}Do you want to add buttons to this image? (y/n): {RESET_COLOR}").strip().lower()
                        # if add_buttons == 'y':
                        #     image_item['buttons'] = []
                        #     while True:
                        #         button_text = input(f"{INPUT_COLOR}Enter button text (or '' to finish): {RESET_COLOR}").strip()
                        #         if button_text.lower() == '':
                        #             break
                        #         button_url = input(f"{INPUT_COLOR}Enter button URL: {RESET_COLOR}").strip()
                        #         if not button_url:
                        #             print(f"{ERROR_COLOR}⚠️ Button URL cannot be empty.{RESET_COLOR}")
                        #             continue
                        #         image_item['buttons'].append({'text': button_text, 'url': button_url})
                        #         print(f"{SUCCESS_COLOR}Button added to image.{RESET_COLOR}")

                        session_content.append(image_item)
                        print(f"{SUCCESS_COLOR}Image added to session.{RESET_COLOR}")
                        features["sessions"][session_name] = session_content
                        save_session_to_file(features["sessions"])

                    elif choice_content == 3:
                        file_path = input(
                            f"{INPUT_COLOR}Enter the file path: {RESET_COLOR}"
                        ).strip()
                        if not file_path:
                            print(
                                f"{ERROR_COLOR}⚠️ File path cannot be empty.{RESET_COLOR}"
                            )
                            continue
                        session_content.append({"type": "file", "path": file_path})
                        print(f"{SUCCESS_COLOR}File added to session.{RESET_COLOR}")
                        features["sessions"][session_name] = session_content
                        save_session_to_file(features["sessions"])
                    elif choice_content == 4:
                        print(f"""{OPTION_COLOR}
                        Choose button type:
                        1️⃣ Inline Button
                        2️⃣ Dock Button (Panel)
                        {RESET_COLOR}""")

                        try:
                            button_choice = int(
                                input(
                                    f"{INPUT_COLOR}👉 Choose button type (1-2): {RESET_COLOR}"
                                )
                            )
                        except ValueError:
                            print(f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}")
                            continue

                        if button_choice == 1:
                            if not session_content:
                                print(
                                    f"{ERROR_COLOR}⚠️ No items available to attach buttons to.{RESET_COLOR}"
                                )
                                continue

                            print(
                                f"{OPTION_COLOR}For the inline button, choose the item to stick the button to:{RESET_COLOR}"
                            )
                            for idx, item in enumerate(session_content, 1):
                                if item["type"] == "text":
                                    print(f"{idx}. Text: {item['content']}")
                                elif item["type"] == "image":
                                    print(f"{idx}. Image: {item['url']}")
                                elif item["type"] == "file":
                                    print(f"{idx}. File: {item['path']}")
                                elif item["type"] == "button":
                                    print(
                                        f"{idx}. Button: {item['text']} (URL: {item['url']})"
                                    )

                            try:
                                button_target = int(
                                    input(
                                        f"{INPUT_COLOR}👉 Choose an item number to attach the button to (1-{len(session_content)}): {RESET_COLOR}"
                                    )
                                )
                            except ValueError:
                                print(
                                    f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}"
                                )
                                continue

                            if 1 <= button_target <= len(session_content):
                                selected_item = session_content[button_target - 1]
                                selected_item["buttons"] = selected_item.get(
                                    "buttons", []
                                )

                                while True:
                                    inline_button_text = input(
                                        f"{INPUT_COLOR}Enter inline button text (enter empty to exit): {RESET_COLOR}"
                                    ).strip()
                                    if (
                                        inline_button_text.lower() == ""
                                        or not inline_button_text
                                    ):
                                        break
                                    inline_button_url = input(
                                        f"{INPUT_COLOR}Enter the URL for the button: {RESET_COLOR}"
                                    ).strip()
                                    if not inline_button_url:
                                        print(
                                            f"{ERROR_COLOR}⚠️ Button URL cannot be empty.{RESET_COLOR}"
                                        )
                                        continue
                                    selected_item["buttons"].append(
                                        {
                                            "text": inline_button_text,
                                            "url": inline_button_url,
                                        }
                                    )
                                    print(
                                        f"{SUCCESS_COLOR}Inline button added to the selected item.{RESET_COLOR}"
                                    )

                                if len(selected_item["buttons"]) > 0:
                                    print(
                                        f"{OPTION_COLOR}\n📏 Configure button layout for {len(selected_item['buttons'])} buttons:{RESET_COLOR}"
                                    )
                                    print(
                                        "How many buttons per row would you like? (e.g. 3 for |,|,| layout)"
                                    )
                                    while True:
                                        try:
                                            per_row = int(
                                                input(
                                                    f"{INPUT_COLOR}👉 Buttons per row (default 1): {RESET_COLOR}"
                                                ).strip()
                                                or 1
                                            )
                                            if per_row < 1:
                                                raise ValueError
                                            selected_item["buttons_per_row"] = min(
                                                per_row, len(selected_item["buttons"])
                                            )
                                            print(
                                                f"{SUCCESS_COLOR}✓ Layout set to {selected_item['buttons_per_row']} buttons per row{RESET_COLOR}"
                                            )
                                            break
                                        except ValueError:
                                            print(
                                                f"{ERROR_COLOR}⚠️ Please enter a positive integer{RESET_COLOR}"
                                            )

                                print(
                                    f"{SUCCESS_COLOR}All buttons have been added to the selected item.{RESET_COLOR}"
                                )
                            else:
                                print(f"{ERROR_COLOR}⚠️ Invalid selection.{RESET_COLOR}")

                        elif button_choice == 2:
                            button_text = input(
                                f"{INPUT_COLOR}Enter the button text: {RESET_COLOR}"
                            ).strip()
                            if not button_text:
                                print(
                                    f"{ERROR_COLOR}⚠️ Button text cannot be empty.{RESET_COLOR}"
                                )
                                continue
                            button_url = input(
                                f"{INPUT_COLOR}Enter the URL for the button: {RESET_COLOR}"
                            ).strip()
                            if not button_url:
                                print(
                                    f"{ERROR_COLOR}⚠️ Button URL cannot be empty.{RESET_COLOR}"
                                )
                                continue

                            print(
                                f"{OPTION_COLOR}Choose dock button layout:{RESET_COLOR}"
                            )
                            print("1. Automatic (buttons in a single row)")
                            print("2. Custom grid layout")
                            layout_choice = input(
                                f"{INPUT_COLOR}👉 Choose layout (1-2): {RESET_COLOR}"
                            ).strip()

                            if layout_choice == "2":
                                while True:
                                    try:
                                        cols = int(
                                            input(
                                                f"{INPUT_COLOR}Enter number of columns per row: {RESET_COLOR}"
                                            )
                                        )
                                        rows = int(
                                            input(
                                                f"{INPUT_COLOR}Enter number of rows: {RESET_COLOR}"
                                            )
                                        )
                                        if cols < 1 or rows < 1:
                                            raise ValueError
                                        break
                                    except ValueError:
                                        print(
                                            f"{ERROR_COLOR}⚠️ Please enter positive integers{RESET_COLOR}"
                                        )
                                layout = {"type": "grid", "columns": cols, "rows": rows}
                            else:
                                layout = {"type": "auto"}

                            session_content.append(
                                {
                                    "type": "button",
                                    "text": button_text,
                                    "url": button_url,
                                    "style": "dock",
                                    "layout": layout,
                                }
                            )
                            print(
                                f"{SUCCESS_COLOR}Dock button added with {layout['type']} layout.{RESET_COLOR}"
                            )
                        else:
                            print(
                                f"{ERROR_COLOR}⚠️ Invalid selection. Please choose 1 or 2.{RESET_COLOR}"
                            )

                        features["sessions"][session_name] = session_content
                        save_session_to_file(features["sessions"])
                    elif choice_content == 5:
                        print(f"""{OPTION_COLOR}
                        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        📋 Ready Templates - Available Variables
                        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        
                        You can use these variables in your text (they will be replaced automatically):
                        $time - Current time (e.g. {datetime.now().strftime("%H:%M:%S")})
                        $date - Today's date (e.g. {datetime.now().strftime("%Y-%m-%d")})
                        $jalali - Jalali date (e.g. {JalaliDatetime.now().strftime("%Y/%m/%d")})
                        $weekday - Weekday name (e.g. {JalaliDatetime.now().weekdayname()})
                        $dollar - Dollar rates
                        $euro - Euro rates
                        $bitcoin - Bitcoin price
                        $gold - Gold price
                        $weather - Weather information
                        
                        Select a template to add:
                        ⏰ [1] Time/Date Template
                        💰 [2] Financial Template
                        🌤 [3] Weather Template
                        [4] Back to Previous Menu
                        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        {RESET_COLOR}""")

                        try:
                            template_choice = int(
                                input(
                                    f"{INPUT_COLOR}👉 Choose template (1-4): {RESET_COLOR}"
                                )
                            )
                        except ValueError:
                            print(f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}")
                            continue

                        if template_choice == 1:
                            template_text = """⏰ Time/Date Information:
                            
                    Current Time: $time
                    Today's Date: $date (Gregorian)
                    Jalali Date: $jalali
                    Weekday: $weekday

                    These variables will update automatically when the message is sent"""
                            session_content.append(
                                {"type": "text", "content": template_text}
                            )
                            print(
                                f"{SUCCESS_COLOR}Added Time/Date template to session.{RESET_COLOR}"
                            )

                        elif template_choice == 2:
                            template_text = """💰 Financial Information:
                            
                    💵 Dollar Rates:
                    Official: $dollar_official
                    Market: $dollar_market

                    💶 Euro Rates:
                    Official: $euro_official
                    Market: $euro_market

                    🪙 Bitcoin: $bitcoin
                    🥇 Gold: $gold

                    These rates update automatically"""
                            session_content.append(
                                {"type": "text", "content": template_text}
                            )
                            print(
                                f"{SUCCESS_COLOR}Added Financial template to session.{RESET_COLOR}"
                            )

                        elif template_choice == 3:
                            template_text = """🌤 Weather Information:
                            
                    $weather_city - Shows weather for specific city
                    Example: 
                    Tehran: $weather_tehran
                    Mashhad: $weather_mashhad

                    Use /weather command to get current conditions"""
                            session_content.append(
                                {"type": "text", "content": template_text}
                            )
                            print(
                                f"{SUCCESS_COLOR}Added Weather template to session.{RESET_COLOR}"
                            )

                        elif template_choice == 4:
                            print(f"{INFO_COLOR}Returning to add menu.{RESET_COLOR}")
                        else:
                            print(
                                f"{ERROR_COLOR}⚠️ Invalid template selection.{RESET_COLOR}"
                            )

                        features["sessions"][session_name] = session_content
                        save_session_to_file(features["sessions"])
                    elif choice_content == 6:
                        if not session_content:
                            print(
                                f"{ERROR_COLOR}⚠️ No items available to move.{RESET_COLOR}"
                            )
                            continue

                        print(
                            f"{OPTION_COLOR}Choose the item you want to move:{RESET_COLOR}"
                        )
                        for idx, item in enumerate(session_content, 1):
                            print(
                                f"{idx}. {item['type'].capitalize()}: {item.get('content', item.get('url', item.get('path', '')))}"
                            )

                        try:
                            move_item_index = int(
                                input(
                                    f"{INPUT_COLOR}👉 Enter the item number you want to move (1-{len(session_content)}): {RESET_COLOR}"
                                )
                            )
                        except ValueError:
                            print(f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}")
                            continue

                        if 1 <= move_item_index <= len(session_content):
                            move_item = session_content.pop(move_item_index - 1)
                            print(
                                f"{SUCCESS_COLOR}You chose to move: {move_item['type'].capitalize()} - {move_item.get('content', move_item.get('url', move_item.get('path', '')))}{RESET_COLOR}"
                            )

                            print(
                                f"{OPTION_COLOR}Where do you want to move this item?{RESET_COLOR}"
                            )
                            print(f"1️⃣ Move to the top of the session")
                            print(f"2️⃣ Move up by one position")
                            print(f"3️⃣ Move down by one position")

                            try:
                                move_position = int(
                                    input(
                                        f"{INPUT_COLOR}👉 Choose a position (1-3): {RESET_COLOR}"
                                    )
                                )
                            except ValueError:
                                print(
                                    f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}"
                                )
                                continue

                            if move_position == 1:
                                session_content.insert(0, move_item)
                                print(
                                    f"{SUCCESS_COLOR}Item moved to the top of the session.{RESET_COLOR}"
                                )
                            elif move_position == 2 and move_item_index > 1:
                                session_content.insert(move_item_index - 2, move_item)
                                print(
                                    f"{SUCCESS_COLOR}Item moved up by one position.{RESET_COLOR}"
                                )
                            elif move_position == 3 and move_item_index < len(
                                session_content
                            ):
                                session_content.insert(move_item_index, move_item)
                                print(
                                    f"{SUCCESS_COLOR}Item moved down by one position.{RESET_COLOR}"
                                )
                            else:
                                print(
                                    f"{ERROR_COLOR}⚠️ Invalid move. No item to move in that direction.{RESET_COLOR}"
                                )

                        else:
                            print(f"{ERROR_COLOR}⚠️ Invalid selection.{RESET_COLOR}")

                        features["sessions"][session_name] = session_content
                        save_session_to_file(features["sessions"])

                    elif choice_content == 7:
                        if not session_content:
                            print(
                                f"{ERROR_COLOR}⚠️ No items to delete. Session is empty.{RESET_COLOR}"
                            )
                            continue

                        print(
                            f"{OPTION_COLOR}Choose the item you want to delete:{RESET_COLOR}"
                        )
                        for idx, item in enumerate(session_content, 1):
                            display_text = ""
                            if item["type"] == "text":
                                display_text = f"📝 Text: {item['content'][:30]}"
                            elif item["type"] == "image":
                                display_text = f" Image URL: {item['url']}"
                            elif item["type"] == "file":
                                display_text = f"📁 File: {item['path']}"
                            elif item["type"] == "button":
                                display_text = f"🔘 Button: {item['text']}"

                            print(f"{idx}. {display_text}")
                        try:
                            delete_index = int(
                                input(
                                    f"{INPUT_COLOR}👉 Enter the number of the item to delete (1-{len(session_content)}): {RESET_COLOR}"
                                )
                            )
                            if 1 <= delete_index <= len(session_content):
                                removed = session_content.pop(delete_index - 1)
                                print(
                                    f"{SUCCESS_COLOR}✅ Item removed from session: {removed['type']}{RESET_COLOR}"
                                )
                                features["sessions"][session_name] = session_content
                                save_session_to_file(features["sessions"])
                            else:
                                print(
                                    f"{ERROR_COLOR}⚠️ Invalid item number.{RESET_COLOR}"
                                )
                        except ValueError:
                            print(
                                f"{ERROR_COLOR}⚠️ Please enter a valid number.{RESET_COLOR}"
                            )

                    elif choice_content == 8:
                        if not session_content:
                            print(
                                f"{ERROR_COLOR}⚠️ No items available to attach functions to.{RESET_COLOR}"
                            )
                            continue

                        button_items = []
                        for idx, item in enumerate(session_content):
                            if item["type"] == "button":
                                button_items.append((idx, item))
                            elif "buttons" in item and item["buttons"]:
                                for btn_idx, btn in enumerate(item["buttons"]):
                                    button_items.append((idx, btn, True))

                        if not button_items:
                            print(
                                f"{ERROR_COLOR}⚠️ No buttons found in the session.{RESET_COLOR}"
                            )
                            continue

                        print(f"{OPTION_COLOR}Available buttons:{RESET_COLOR}")
                        for i, (idx, btn, *is_inline) in enumerate(button_items, 1):
                            btn_type = "Inline" if is_inline else "Regular"
                            print(f"{i}. {btn_type} Button: {btn['text']}")

                        try:
                            btn_choice = int(
                                input(
                                    f"{INPUT_COLOR}👉 Choose a button to add function to (1-{len(button_items)}): {RESET_COLOR}"
                                )
                            )
                        except ValueError:
                            print(f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}")
                            continue

                        if 1 <= btn_choice <= len(button_items):
                            selected = button_items[btn_choice - 1]
                            if len(selected) == 2:
                                btn = selected[1]
                            else:
                                btn = selected[1]

                            print(f"{OPTION_COLOR}Available functions:{RESET_COLOR}")
                            print("1. Send Message")
                            print("2. Open URL")
                            print("3. Run Python Code")
                            print("4. Get User Input")

                            try:
                                func_choice = int(
                                    input(
                                        f"{INPUT_COLOR}👉 Choose function type (1-4): {RESET_COLOR}"
                                    )
                                )
                            except ValueError:
                                print(
                                    f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}"
                                )
                                continue

                            if func_choice == 1:
                                message = input(
                                    f"{INPUT_COLOR}Enter message to send: {RESET_COLOR}"
                                ).strip()
                                btn["action"] = {
                                    "type": "send_message",
                                    "content": message,
                                }
                                print(
                                    f"{SUCCESS_COLOR}Message function added to button.{RESET_COLOR}"
                                )
                            elif func_choice == 2:
                                print(
                                    f"{SUCCESS_COLOR}Button already has URL action.{RESET_COLOR}"
                                )
                            elif func_choice == 3:
                                code = input(
                                    f"{INPUT_COLOR}Enter Python code to execute: {RESET_COLOR}"
                                ).strip()
                                btn["action"] = {"type": "run_code", "code": code}
                                print(
                                    f"{SUCCESS_COLOR}Code execution added to button.{RESET_COLOR}"
                                )
                            elif func_choice == 4:
                                prompt = input(
                                    f"{INPUT_COLOR}Enter prompt for user input: {RESET_COLOR}"
                                ).strip()
                                btn["action"] = {
                                    "type": "get_input",
                                    "prompt": prompt,
                                    "variable": f"user_input_{len(btn.get('actions', []))}",
                                }
                                print(
                                    f"{SUCCESS_COLOR}Input collection added to button.{RESET_COLOR}"
                                )
                            else:
                                print(
                                    f"{ERROR_COLOR}⚠️ Invalid function choice.{RESET_COLOR}"
                                )
                        else:
                            print(
                                f"{ERROR_COLOR}⚠️ Invalid button selection.{RESET_COLOR}"
                            )

                        features["sessions"][session_name] = session_content
                        save_session_to_file(features["sessions"])

                    elif choice_content == 9:
                        wait_position = len(session_content)

                        print(
                            f"{OPTION_COLOR}Select the kind of response you want to capture:{RESET_COLOR}"
                        )
                        print("  1) Text")
                        print("  2) Number")
                        type_choice = input(
                            f"{INPUT_COLOR}Enter choice [1-2] (default 1): {RESET_COLOR}"
                        ).strip()
                        if type_choice == "2":
                            input_type = "number"
                        else:
                            input_type = "text"

                        variable_name = input(
                            f"{INPUT_COLOR}Enter variable name to store response (e.g., 'user_name'): {RESET_COLOR}"
                        ).strip()
                        if not variable_name:
                            print(
                                f"{ERROR_COLOR}⚠️ Variable name cannot be empty.{RESET_COLOR}"
                            )
                            continue

                        prompt_text = input(
                            f"{INPUT_COLOR}Enter prompt text to show while waiting (optional): {RESET_COLOR}"
                        ).strip()

                        follow_up = input(
                            f"{INPUT_COLOR}Enter follow‑up message after user responds (optional): {RESET_COLOR}"
                        ).strip()

                        timeout = input(
                            f"{INPUT_COLOR}Enter timeout in seconds (leave empty for none): {RESET_COLOR}"
                        ).strip()
                        try:
                            timeout = float(timeout) if timeout else None
                        except ValueError:
                            print(
                                f"{ERROR_COLOR}⚠️ Invalid timeout value; ignoring.{RESET_COLOR}"
                            )
                            timeout = None

                        wait_item = {
                            "type": "wait_for_response",
                            "variable": variable_name,
                            "input_type": input_type,
                            "prompt": prompt_text,
                            "follow_up": follow_up or None,
                            "timeout": timeout,
                            "save_to": f"user_responses.{variable_name}",
                            "position": wait_position,
                        }

                        session_content.append(wait_item)
                        print(
                            f"{SUCCESS_COLOR}✔️ Will wait for a {input_type} response after item {wait_position}. Variable: '{variable_name}'.{RESET_COLOR}"
                        )
                        if follow_up:
                            print(
                                f"{INFO_COLOR}Will then send: {follow_up}{RESET_COLOR}"
                            )
                        print(
                            f"{INFO_COLOR}Use it later as: {{user_responses.{variable_name}}}{RESET_COLOR}"
                        )

                        features["sessions"][session_name] = session_content
                        save_session_to_file(features["sessions"])

                    elif choice_content == 0:
                        features["sessions"][session_name] = session_content
                        print(
                            f"{SUCCESS_COLOR}Session '{session_name}' created with {len(session_content)} parts.{RESET_COLOR}"
                        )
                        save_session_to_file(features["sessions"])
                        break
                    else:
                        print(
                            f"{ERROR_COLOR}⚠️ Invalid selection. Please choose 1-0.{RESET_COLOR}"
                        )

            elif choice_session == 2:
                try:
                    with open("sessions.json", "r", encoding="utf-8") as f:
                        sessions = json.load(f)

                    if not sessions:
                        print(
                            f"{INFO_COLOR}No sessions available to edit.{RESET_COLOR}"
                        )
                        continue

                    print(f"{OPTION_COLOR}Available sessions to edit:{RESET_COLOR}")
                    for idx, session_name in enumerate(sessions.keys(), 1):
                        print(f"{idx}. {session_name}")

                    try:
                        session_choice = int(
                            input(
                                f"{INPUT_COLOR}👉 Choose a session to edit (1-{len(sessions)}): {RESET_COLOR}"
                            )
                        )
                    except ValueError:
                        print(f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}")
                        continue

                    if 1 <= session_choice <= len(sessions):
                        session_name = list(sessions.keys())[session_choice - 1]
                        session_content = sessions[session_name]

                        print(
                            f"{SUCCESS_COLOR}Editing session: {session_name}{RESET_COLOR}"
                        )

                        while True:
                            print(
                                f"{OPTION_COLOR}Current content in session '{session_name}':{RESET_COLOR}"
                            )
                            for idx, item in enumerate(session_content, 1):
                                item_desc = ""
                                if item["type"] == "text":
                                    item_desc = f"📝 Text: {item['content'][:30]}"
                                    if "buttons" in item:
                                        item_desc += (
                                            f" [+{len(item['buttons'])} buttons]"
                                        )
                                elif item["type"] == "image":
                                    item_desc = f" Image: {item['url'][:30]}"
                                    if "buttons" in item:
                                        item_desc += (
                                            f" [+{len(item['buttons'])} buttons]"
                                        )
                                elif item["type"] == "file":
                                    item_desc = f"📁 File: {item['path'][:30]}"
                                elif item["type"] == "button":
                                    btn_type = (
                                        "Dock"
                                        if item.get("style") == "dock"
                                        else "Inline"
                                    )
                                    item_desc = f"🔘 {btn_type} Button: {item['text']} ({item['url'][:20]})"
                                elif item["type"] == "wait_for_response":
                                    timeout_info = (
                                        f" (timeout: {item['timeout']}s)"
                                        if item.get("timeout")
                                        else ""
                                    )
                                    item_desc = (
                                        f"⏳ Wait: {item['variable']}{timeout_info}"
                                    )
                                print(f"{idx}. {item_desc}")

                            print(f"""{OPTION_COLOR}
                            Edit options:
                            1️⃣ Edit an item
                            2️⃣ Add new content
                            3️⃣ Delete an item
                            4️⃣ Save changes
                            5️⃣ Add button
                            6️⃣ Cancel editing
                            {RESET_COLOR}""")

                            try:
                                edit_choice = int(
                                    input(
                                        f"{INPUT_COLOR}👉 Choose an option (1-6): {RESET_COLOR}"
                                    )
                                )
                            except ValueError:
                                print(
                                    f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}"
                                )
                                continue

                            if edit_choice == 1:
                                try:
                                    item_index = int(
                                        input(
                                            f"{INPUT_COLOR}👉 Enter the item number to edit (1-{len(session_content)}): {RESET_COLOR}"
                                        )
                                    )
                                except ValueError:
                                    print(
                                        f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}"
                                    )
                                    continue

                                if 1 <= item_index <= len(session_content):
                                    item = session_content[item_index - 1]
                                    print(
                                        f"{SUCCESS_COLOR}Editing item {item_index}: {item['type']}{RESET_COLOR}"
                                    )

                                    if item["type"] == "text":
                                        new_text = input(
                                            f"{INPUT_COLOR}Enter new text (current: {item['content']}): {RESET_COLOR}"
                                        ).strip()
                                        if new_text:
                                            item["content"] = new_text
                                            print(
                                                f"{SUCCESS_COLOR}Text updated.{RESET_COLOR}"
                                            )

                                    elif item["type"] == "wait_for_response":
                                        print(
                                            f"{OPTION_COLOR}Editing wait_for_response item:{RESET_COLOR}"
                                        )
                                        new_var = input(
                                            f"{INPUT_COLOR}Enter new variable name (current: {item['variable']}): {RESET_COLOR}"
                                        ).strip()
                                        if new_var:
                                            item["variable"] = new_var
                                            item["save_to"] = (
                                                f"user_responses.{new_var}"
                                            )

                                        print(
                                            f"{OPTION_COLOR}Current input type: {item['input_type']}{RESET_COLOR}"
                                        )
                                        print("1. Text\n2. Number")
                                        type_choice = input(
                                            f"{INPUT_COLOR}Choose input type (1-2, leave empty to keep current): {RESET_COLOR}"
                                        ).strip()
                                        if type_choice == "1":
                                            item["input_type"] = "text"
                                        elif type_choice == "2":
                                            item["input_type"] = "number"

                                        new_prompt = input(
                                            f"{INPUT_COLOR}Enter new prompt text (current: {item.get('prompt', '')}): {RESET_COLOR}"
                                        ).strip()
                                        if new_prompt:
                                            item["prompt"] = new_prompt

                                        new_follow_up = input(
                                            f"{INPUT_COLOR}Enter new follow-up message (current: {item.get('follow_up', '')}): {RESET_COLOR}"
                                        ).strip()
                                        item["follow_up"] = (
                                            new_follow_up if new_follow_up else None
                                        )

                                        new_timeout = input(
                                            f"{INPUT_COLOR}Enter new timeout in seconds (current: {item.get('timeout', '')}): {RESET_COLOR}"
                                        ).strip()
                                        try:
                                            if new_timeout:
                                                item["timeout"] = float(new_timeout)
                                        except ValueError:
                                            print(
                                                f"{ERROR_COLOR}⚠️ Invalid timeout value, keeping current.{RESET_COLOR}"
                                            )

                                        print(
                                            f"{SUCCESS_COLOR}Wait_for_response item updated.{RESET_COLOR}"
                                        )

                                    elif item["type"] == "button":
                                        print(
                                            f"{OPTION_COLOR}Editing Button:{RESET_COLOR}"
                                        )
                                        new_text = input(
                                            f"{INPUT_COLOR}New button text (current: {item['text']}): {RESET_COLOR}"
                                        ).strip()
                                        if new_text:
                                            item["text"] = new_text

                                        new_url = input(
                                            f"{INPUT_COLOR}New button URL (current: {item['url']}): {RESET_COLOR}"
                                        ).strip()
                                        if new_url:
                                            item["url"] = new_url

                                        print(
                                            f"{SUCCESS_COLOR}Button updated.{RESET_COLOR}"
                                        )

                                    else:
                                        print(
                                            f"{ERROR_COLOR}⚠️ This item type cannot be edited yet.{RESET_COLOR}"
                                        )
                                else:
                                    print(
                                        f"{ERROR_COLOR}⚠️ Invalid item selection.{RESET_COLOR}"
                                    )

                            elif edit_choice == 2:
                                print(f"""{OPTION_COLOR}
                                Add content to the session:
                                1️⃣ Add Text
                                2️⃣ Add Image
                                3️⃣ Add File
                                4️⃣ Add Button
                                5️⃣ Add Wait for Response
                                6️⃣ Back to edit menu
                                {RESET_COLOR}""")

                                try:
                                    add_choice = int(
                                        input(
                                            f"{INPUT_COLOR}👉 Choose an option (1-6): {RESET_COLOR}"
                                        )
                                    )
                                except ValueError:
                                    print(
                                        f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}"
                                    )
                                    continue

                                if add_choice == 4:
                                    print(f"""{OPTION_COLOR}
                                    Choose button type:
                                    1️⃣ Inline Button (attached to existing item)
                                    2️⃣ Dock Button (standalone panel)
                                    {RESET_COLOR}""")

                                    try:
                                        btn_type = int(
                                            input(
                                                f"{INPUT_COLOR}👉 Choose type (1-2): {RESET_COLOR}"
                                            )
                                        )
                                    except ValueError:
                                        print(
                                            f"{ERROR_COLOR}⚠️ Invalid input{RESET_COLOR}"
                                        )
                                        continue

                                    if btn_type == 1:
                                        if not session_content:
                                            print(
                                                f"{ERROR_COLOR}⚠️ No items available to attach buttons to{RESET_COLOR}"
                                            )
                                            continue

                                        print(
                                            f"{OPTION_COLOR}Select item to attach button to:{RESET_COLOR}"
                                        )
                                        for idx, item in enumerate(session_content, 1):
                                            print(f"{idx}. {item['type'].capitalize()}")

                                        try:
                                            target_idx = (
                                                int(
                                                    input(
                                                        f"{INPUT_COLOR}👉 Choose item (1-{len(session_content)}): {RESET_COLOR}"
                                                    )
                                                )
                                                - 1
                                            )
                                            target_item = session_content[target_idx]
                                        except (ValueError, IndexError):
                                            print(
                                                f"{ERROR_COLOR}⚠️ Invalid selection{RESET_COLOR}"
                                            )
                                            continue

                                        while True:
                                            btn_text = input(
                                                f"{INPUT_COLOR}Button text (empty to finish): {RESET_COLOR}"
                                            ).strip()
                                            if not btn_text:
                                                break
                                            btn_url = input(
                                                f"{INPUT_COLOR}Button URL: {RESET_COLOR}"
                                            ).strip()
                                            if not btn_url:
                                                print(
                                                    f"{ERROR_COLOR}⚠️ URL required{RESET_COLOR}"
                                                )
                                                continue

                                            if "buttons" not in target_item:
                                                target_item["buttons"] = []
                                            target_item["buttons"].append(
                                                {"text": btn_text, "url": btn_url}
                                            )
                                            print(
                                                f"{SUCCESS_COLOR}✅ Button added!{RESET_COLOR}"
                                            )

                                    elif btn_type == 2:
                                        btn_text = input(
                                            f"{INPUT_COLOR}Button text: {RESET_COLOR}"
                                        ).strip()
                                        btn_url = input(
                                            f"{INPUT_COLOR}Button URL: {RESET_COLOR}"
                                        ).strip()
                                        if not btn_text or not btn_url:
                                            print(
                                                f"{ERROR_COLOR}⚠️ Both text and URL required{RESET_COLOR}"
                                            )
                                            continue

                                        print(
                                            f"{OPTION_COLOR}Choose button layout:{RESET_COLOR}"
                                        )
                                        print("1. Auto (single row)\n2. Grid layout")
                                        try:
                                            layout_choice = int(
                                                input(
                                                    f"{INPUT_COLOR}👉 Choice (1-2): {RESET_COLOR}"
                                                )
                                            )
                                        except ValueError:
                                            layout_choice = 1

                                        layout = {"type": "auto"}
                                        if layout_choice == 2:
                                            try:
                                                cols = int(
                                                    input(
                                                        f"{INPUT_COLOR}Columns per row: {RESET_COLOR}"
                                                    )
                                                )
                                                rows = int(
                                                    input(
                                                        f"{INPUT_COLOR}Number of rows: {RESET_COLOR}"
                                                    )
                                                )
                                                layout = {
                                                    "type": "grid",
                                                    "columns": cols,
                                                    "rows": rows,
                                                }
                                            except ValueError:
                                                print(
                                                    f"{ERROR_COLOR}⚠️ Using auto layout{RESET_COLOR}"
                                                )

                                        session_content.append(
                                            {
                                                "type": "button",
                                                "text": btn_text,
                                                "url": btn_url,
                                                "style": "dock",
                                                "layout": layout,
                                            }
                                        )
                                        print(
                                            f"{SUCCESS_COLOR}✅ Dock button added!{RESET_COLOR}"
                                        )

                                    else:
                                        print(
                                            f"{ERROR_COLOR}⚠️ Invalid choice{RESET_COLOR}"
                                        )

                                elif add_choice == 5:
                                    print(
                                        f"{OPTION_COLOR}Select response type:{RESET_COLOR}"
                                    )
                                    print("1. Text\n2. Number")
                                    type_choice = (
                                        input(
                                            f"{INPUT_COLOR}Choice (1-2): {RESET_COLOR}"
                                        ).strip()
                                        or "1"
                                    )

                                    variable_name = input(
                                        f"{INPUT_COLOR}Variable name (e.g., user_age): {RESET_COLOR}"
                                    ).strip()
                                    if not variable_name:
                                        print(
                                            f"{ERROR_COLOR}⚠️ Variable name required{RESET_COLOR}"
                                        )
                                        continue

                                    wait_item = {
                                        "type": "wait_for_response",
                                        "variable": variable_name,
                                        "input_type": "number"
                                        if type_choice == "2"
                                        else "text",
                                        "prompt": input(
                                            f"{INPUT_COLOR}Prompt text: {RESET_COLOR}"
                                        ).strip(),
                                        "follow_up": input(
                                            f"{INPUT_COLOR}Follow-up message (optional): {RESET_COLOR}"
                                        ).strip()
                                        or None,
                                        "timeout": None,
                                        "save_to": f"user_responses.{variable_name}",
                                    }

                                    timeout = input(
                                        f"{INPUT_COLOR}Timeout in seconds (optional): {RESET_COLOR}"
                                    ).strip()
                                    if timeout:
                                        try:
                                            wait_item["timeout"] = float(timeout)
                                        except ValueError:
                                            print(
                                                f"{ERROR_COLOR}⚠️ Invalid timeout value{RESET_COLOR}"
                                            )

                                    session_content.append(wait_item)
                                    print(
                                        f"{SUCCESS_COLOR}✅ Wait for response added!{RESET_COLOR}"
                                    )

                                elif add_choice == 6:
                                    print(
                                        f"{SUCCESS_COLOR}Returning to edit menu.{RESET_COLOR}"
                                    )

                            elif edit_choice == 3:
                                try:
                                    item_index = int(
                                        input(
                                            f"{INPUT_COLOR}👉 Enter item number to delete (1-{len(session_content)}): {RESET_COLOR}"
                                        )
                                    )
                                    if 1 <= item_index <= len(session_content):
                                        deleted = session_content.pop(item_index - 1)
                                        print(
                                            f"{SUCCESS_COLOR}✅ Deleted: {deleted['type']}{RESET_COLOR}"
                                        )
                                    else:
                                        print(
                                            f"{ERROR_COLOR}⚠️ Invalid item number{RESET_COLOR}"
                                        )
                                except ValueError:
                                    print(f"{ERROR_COLOR}⚠️ Invalid input{RESET_COLOR}")

                            elif edit_choice == 4:
                                features["sessions"][session_name] = session_content
                                save_session_to_file(features["sessions"])
                                print(
                                    f"{SUCCESS_COLOR}✅ Changes saved to '{session_name}'!{RESET_COLOR}"
                                )
                                break

                            elif edit_choice == 5:
                                print(f"""{OPTION_COLOR}
                                Add Button Type:
                                1️⃣ Inline Button
                                2️⃣ Dock Button
                                {RESET_COLOR}""")

                                try:
                                    btn_type = int(
                                        input(
                                            f"{INPUT_COLOR}👉 Choose type (1-2): {RESET_COLOR}"
                                        )
                                    )
                                except ValueError:
                                    print(f"{ERROR_COLOR}⚠️ Invalid input{RESET_COLOR}")
                                    continue

                                if btn_type == 1:
                                    if not session_content:
                                        print(
                                            f"{ERROR_COLOR}⚠️ No items to attach buttons to{RESET_COLOR}"
                                        )
                                        continue

                                    print(
                                        f"{OPTION_COLOR}Select target item:{RESET_COLOR}"
                                    )
                                    for idx, item in enumerate(session_content, 1):
                                        print(f"{idx}. {item['type'].capitalize()}")

                                    try:
                                        target_idx = (
                                            int(
                                                input(
                                                    f"{INPUT_COLOR}👉 Choose item (1-{len(session_content)}): {RESET_COLOR}"
                                                )
                                            )
                                            - 1
                                        )
                                        target = session_content[target_idx]

                                        btn_text = input(
                                            f"{INPUT_COLOR}Button text: {RESET_COLOR}"
                                        ).strip()
                                        btn_url = input(
                                            f"{INPUT_COLOR}Button URL: {RESET_COLOR}"
                                        ).strip()
                                        if not btn_text or not btn_url:
                                            print(
                                                f"{ERROR_COLOR}⚠️ Both text and URL required{RESET_COLOR}"
                                            )
                                            continue

                                        if "buttons" not in target:
                                            target["buttons"] = []
                                        target["buttons"].append(
                                            {"text": btn_text, "url": btn_url}
                                        )
                                        print(
                                            f"{SUCCESS_COLOR}✅ Inline button added!{RESET_COLOR}"
                                        )

                                    except (ValueError, IndexError):
                                        print(
                                            f"{ERROR_COLOR}⚠️ Invalid selection{RESET_COLOR}"
                                        )

                                elif btn_type == 2:
                                    btn_text = input(
                                        f"{INPUT_COLOR}Button text: {RESET_COLOR}"
                                    ).strip()
                                    btn_url = input(
                                        f"{INPUT_COLOR}Button URL: {RESET_COLOR}"
                                    ).strip()
                                    if not btn_text or not btn_url:
                                        print(
                                            f"{ERROR_COLOR}⚠️ Both text and URL required{RESET_COLOR}"
                                        )
                                        continue

                                    session_content.append(
                                        {
                                            "type": "button",
                                            "text": btn_text,
                                            "url": btn_url,
                                            "style": "dock",
                                            "layout": {"type": "auto"},
                                        }
                                    )
                                    print(
                                        f"{SUCCESS_COLOR}✅ Dock button added!{RESET_COLOR}"
                                    )

                                else:
                                    print(f"{ERROR_COLOR}⚠️ Invalid choice{RESET_COLOR}")

                            elif edit_choice == 6:
                                print(f"{INFO_COLOR}Editing cancelled{RESET_COLOR}")
                                break

                            else:
                                print(f"{ERROR_COLOR}⚠️ Invalid selection{RESET_COLOR}")

                    else:
                        print(f"{ERROR_COLOR}⚠️ Invalid session selection{RESET_COLOR}")
                except Exception as e:
                    print(f"{ERROR_COLOR}💥 Error: {str(e)}{RESET_COLOR}")

            if choice_session == 3:
                try:
                    with open("sessions.json", "r", encoding="utf-8") as f:
                        sessions = json.load(f)

                    if not sessions:
                        print(
                            f"{INFO_COLOR}No sessions available to delete.{RESET_COLOR}"
                        )
                        continue

                    print(f"{OPTION_COLOR}Available sessions to delete:{RESET_COLOR}")
                    session_names = list(sessions.keys())
                    for idx, name in enumerate(session_names, 1):
                        print(f"{idx}. {name}")

                    try:
                        session_choice = int(
                            input(
                                f"{INPUT_COLOR}👉 Choose a session to delete (1-{len(session_names)}): {RESET_COLOR}"
                            )
                        )
                    except ValueError:
                        print(f"{ERROR_COLOR}⚠️ Please enter a number.{RESET_COLOR}")
                        continue

                    if 1 <= session_choice <= len(session_names):
                        session_name = session_names[session_choice - 1]
                        confirm = (
                            input(
                                f"{INPUT_COLOR}⚠️ Are you sure you want to delete session '{session_name}'? (y/n): {RESET_COLOR}"
                            )
                            .strip()
                            .lower()
                        )
                        if confirm == "y":
                            del sessions[session_name]
                            save_session_to_file(sessions)
                            print(
                                f"{SUCCESS_COLOR}Session '{session_name}' deleted.{RESET_COLOR}"
                            )
                        else:
                            print(f"{INFO_COLOR}Deletion cancelled.{RESET_COLOR}")
                    else:
                        print(f"{ERROR_COLOR}⚠️ Invalid session selection.{RESET_COLOR}")
                except FileNotFoundError:
                    print(
                        f"{ERROR_COLOR}⚠️ 'sessions.json' file not found.{RESET_COLOR}"
                    )
                except json.JSONDecodeError:
                    print(
                        f"{ERROR_COLOR}⚠️ Error decoding JSON from 'sessions.json'.{RESET_COLOR}"
                    )
                except Exception as e:
                    print(f"{ERROR_COLOR}💥 Unexpected error: {str(e)}{RESET_COLOR}")

            elif choice_session == 4:
                try:
                    while True:
                        with open("sessions.json", "r") as f:
                            sessions = json.load(f)

                        if not sessions:
                            print(
                                f"{INFO_COLOR}No sessions available to preview.{RESET_COLOR}"
                            )
                        else:
                            print(
                                f"{OPTION_COLOR}Current live sessions JSON preview:{RESET_COLOR}"
                            )
                            print(
                                f"{OPTION_COLOR}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET_COLOR}\n"
                            )

                            print(json.dumps(sessions, indent=4, ensure_ascii=False))

                            print(
                                f"\n{OPTION_COLOR}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET_COLOR}"
                            )

                        print(f"\n{INFO_COLOR}Preview options:{RESET_COLOR}")
                        print(f"1. Refresh preview")
                        print(f"2. Return to main menu")
                        print(f"3. Export to file")
                        print(f"4. Quit")

                        preview_choice = input(
                            f"{INPUT_COLOR}👉 Choose an option (1-4): {RESET_COLOR}"
                        ).strip()

                        if preview_choice == "1":
                            continue
                        elif preview_choice == "2":
                            print(f"{INFO_COLOR}Returning to main menu...{RESET_COLOR}")
                            break
                        elif preview_choice == "3":
                            export_filename = input(
                                f"{INPUT_COLOR}Enter filename to export to (e.g., export.json): {RESET_COLOR}"
                            ).strip()
                            if not export_filename:
                                export_filename = "sessions_export.json"
                            try:
                                with open(export_filename, "w") as export_file:
                                    json.dump(sessions, export_file, indent=4)
                                print(
                                    f"{SUCCESS_COLOR}✅ Sessions successfully exported to {export_filename}{RESET_COLOR}"
                                )
                            except Exception as e:
                                print(
                                    f"{ERROR_COLOR}❌ Error exporting sessions: {str(e)}{RESET_COLOR}"
                                )
                        elif preview_choice == "4":
                            print(f"{INFO_COLOR}Exiting program...{RESET_COLOR}")
                            exit(0)
                        else:
                            print(
                                f"{ERROR_COLOR}⚠️ Invalid option. Please choose 1-4.{RESET_COLOR}"
                            )

                except FileNotFoundError:
                    print(
                        f"{ERROR_COLOR}⚠️ 'sessions.json' file not found.{RESET_COLOR}"
                    )
                except json.JSONDecodeError:
                    print(
                        f"{ERROR_COLOR}⚠️ Error decoding JSON from 'sessions.json'. The file might be corrupted.{RESET_COLOR}"
                    )
                except Exception as e:
                    print(
                        f"{ERROR_COLOR}💥 Unexpected error during preview: {str(e)}{RESET_COLOR}"
                    )

            elif choice_session == 5:
                print(f"{INFO_COLOR}Returning to main menu...{RESET_COLOR}")
                break

            else:
                print(f"{ERROR_COLOR}⚠️ Invalid option. Please choose 1-5.{RESET_COLOR}")

    except KeyboardInterrupt:
        print(f"\n{INFO_COLOR}Operation cancelled by user.{RESET_COLOR}")
    except Exception as e:
        print(
            f"{ERROR_COLOR}💥 Unexpected error in session creation: {str(e)}{RESET_COLOR}"
        )
    finally:
        if "sessions" in features:
            save_session_to_file(features["sessions"])
