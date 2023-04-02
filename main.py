import json
from dotenv import dotenv_values
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

import gpt


CONFIG = dotenv_values('.env')

TOKEN = CONFIG['TOKEN']


updater = Updater(token=TOKEN)

chat_session = None


def send_message(update, context):
    global chat_session
    chat_id = update.effective_chat.id

    if chat_session is None:
        context.bot.send_message(chat_id=chat_id, text="Нужно начать новую сессию чата")
        return

    user_message = update.message.text

    try:
        gpt_response = chat_session.send_message(user_message)
    except gpt.TokensLimitExceeded as exc:
        chat_session = gpt.ChatSession()

        context.bot.send_message(chat_id=chat_id, text=exc.incomplete_response)

        error_message = (
            'Достигнут лимит сообщений, создана новаяя сессия. '
            'Контекст предыдущей сессии потерян, начните заново'
        )
        context.bot.send_message(chat_id=chat_id, text=error_message)
        return

    context.bot.send_message(chat_id=chat_id, text=gpt_response)


def start_chat(update, context):
    global chat_session

    chat_id = update.effective_chat.id

    chat_session = gpt.ChatSession()

    context.bot.send_message(
        chat_id=chat_id,
        text="Создана новая сессия чата, можно отправлять сообщения"
    )


def check_existing_session():
    with open('current_session.json', 'r') as f:
        messages = json.load(f)
        print(messages, type(messages))

        if messages:
            global chat_session
            chat_session = gpt.ChatSession(messages)


def main():
    global chat_session
    check_existing_session()

    print(chat_session)
    updater.dispatcher.add_handler(CommandHandler('start', start_chat))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, send_message))

    updater.start_polling()
    updater.idle()


# with open('current_session.json', 'r') as f:
#     # data = [
#     #     {"role": "user", "content": "some message1"},
#     #     {"role": "user", "content": "some message2"},
#     # ]
#     # json.dump(data, f)
#     data = json.load(f)
#     print(data)
#     print(type(data))


if __name__ == '__main__':

    main()
