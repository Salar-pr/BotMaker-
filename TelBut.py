import telebot
from telebot import types

bot = telebot.TeleBot("7061561323:AAEMfdleh097ZizIrIZmlFxnM_RmGXZObZ4")


@bot .message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, "به سالار بات خوش امدید برای عضویت روی /membership ضربه بزن .")


@bot .message_handler(commands=['help'])
def send_help(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("درباره ما")
    item2 = types.KeyboardButton("تماس با ما ")
    item3 = types.KeyboardButton("برگشت")
    markup.add(item1, item2, item3)

    bot.send_message(
        message.chat.id, " یکی از موارد زیر را انتخواب کنید:", reply_markup=markup)


if __name__ == '__main__':
    bot.polling()
