from typing import final
from telegram import Update
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

token: final = '7061561323:AAEMfdleh097ZizIrIZmlFxnM_RmGXZObZ4 '
bot_username: final = '@Salarbot'
# comment


async def start_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('سلام ستونم من یک ربات ازمایشی هستم و برای سالار کار میکنم و به طور عشقی به وجود امدم ولی فکر کنم سالار روم برنامه های داره بعدا')
    await update.message.reply_text('کاری از دستم ساختس؟')


async def help_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(' کمک خواستی؟بگو')


async def custom_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(' درسته ')
   # responses

    def handle_responses(text: str) -> str:
        processed: str = text.lower()

        if 'سلام' in processed:
            return 'سلام سالار بر تو'

        if 'چه خبر ' in processed:
            return 'سلامتیت کاری داشتی؟'

        if 'چی کار میتونی انجام بدی ' in processed:
            return 'در اینده همه کار ولی الان فعلا معلوم نیست'

        if 'خدافظ' in processed:
            return ' فعلا مراقبت کن'
        


        async def custom_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
            Message_type: str = update.massege.chat.type
            text: str = update.massege.text

            print(f'user({update.message.chat.id}) in {Message_type}: "{text}"')


            if Message_type == 'group':
                if bot_username  in text:
                    new_text: str = text.replace(bot_username, '').strip()
                    responses: str = handle_responses(new_text)
                else:
                    return
            else:
                responses: str = handle_responses(text)

                print('bot',responses)
                await update.message.reply_text(responses)

                async def error(update: Update, context: contextTypes.DEFAULT_TYPE):
                    print(f'update {update} caused error {context.error}')

                    if __name__=='__main__':
                        app = Application.builder().token(token).build()
                        # comment
                        app.add_handler(CommandHandler('start', start_comment))
                        app.add_handler(CommandHandler('help', help_comment))
                        app.add_handler(CommandHandler('custom', custom_comment))

                        # messages
                        app.add_handler(MessageHandler(filters.TEXT , handle_massage))
                        #error
                        app.add_error_handler(error)

                        #polls the bot
                        print('polling...')
                        app.run_polling(poll_interval=3)
                        
