import tkinter as tk
from tkinter import messagebox

# تعریف دیکشنری تبدیل
conversion = {
    '000000': 'A', '000001': 'B', '000011': 'C', '000111': 'D',
    '001111': 'E', '011111': 'F', '111111': 'G', '111110': 'H',
    '111100': 'I', '111000': 'J', '110000': 'K', '100000': 'L',
    '101010': 'M', '010101': 'N', '110011': 'O', '011011': 'P',
    '100100': 'Q', '101000': 'R', '100010': 'S', '200000': 'T',
    '220000': 'U', '222000': 'V', '222200': 'W', '222220': 'X',
    '222222': 'Y', '220222': 'Z',' ':' '
}

# ساخت دیکشنری معکوس برای تبدیل حروف به اعداد
reverse_conversion = {v: k for k, v in conversion.items()}

# تابع برای انجام تبدیل


def convert_input():
    s = entry.get().strip()  # دریافت ورودی کاربر
    answer = []

    # تعیین نوع تبدیل (عدد به حروف یا حروف به عدد)
    if s.isdigit():  # اگر ورودی فقط شامل اعداد باشد
        i = 0
        try:
            while i < len(s):
                if s[i:i+6] in conversion:  # چک کردن بلوک‌های ۶ رقمی
                    answer.append(conversion[s[i:i+6]])
                    i += 6
                else:
                    if s[i] in conversion:  # چک کردن رقم‌های تکی
                        answer.append(conversion[s[i]])
                    else:
                        raise KeyError
                    i += 1

            result = ''.join(answer)
            result_label.config(text=f"Result: {result}")
            print(result)
        except KeyError:
            messagebox.showerror("Error", "Invalid numeric input detected!")
    else:  # اگر ورودی شامل حروف باشد
        try:
            for char in s.upper():  # تبدیل به حروف بزرگ برای مطابقت
                if char in reverse_conversion:
                    answer.append(reverse_conversion[char])
                else:
                    raise KeyError

            result = ''.join(answer)
            result_label.config(text=f"Result: {result}")
            print(result)
        except KeyError:
            messagebox.showerror("Error", "Invalid character input detected!")


# ساخت رابط کاربری
root = tk.Tk()
root.title("String Converter")
root.geometry("400x250")

# فیلد ورودی
entry_label = tk.Label(root, text="Enter your string (letters or numbers):")
entry_label.pack(pady=5)

entry = tk.Entry(root, width=30)
entry.pack(pady=5)

# دکمه تبدیل
convert_button = tk.Button(root, text="Convert", command=convert_input)
convert_button.pack(pady=10)

# برچسب نمایش نتیجه
result_label = tk.Label(root, text="Result: ", font=("Arial", 12))
result_label.pack(pady=10)

# اجرای برنامه
root.mainloop()
