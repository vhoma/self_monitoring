# import everything
from flask import Flask, request
import telegram
from telebot.credentials import bot_token, bot_user_name, URL
import re
import datetime
import logging


TOKEN = bot_token
HOST = '0.0.0.0'
PORT = 443
CERT = '../telebot.pem'
CERT_KEY = '../telebot.key'
LOG_FILE = 'log.txt'

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)
context = (CERT, CERT_KEY)


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    user = update.message.from_user

    # Telegram understands UTF-8, so encode text for unicode compatibility
    print("raw text: {}".format(update.message.text))
    if update.message.text:
        text = update.message.text.encode('utf-8').decode()
    # for debugging purposes only
    print("got text message :", text)
    # the first time you chat with the bot AKA the welcoming message
    if text == "/start":
        # print the welcoming message
        bot_welcome = """
Добро пожаловать в гости.
это БОТ
напиши мне сообщение и я поменяю его до НЕУЗНАВАЕМОСТИ!
"""
        # send the welcoming message
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
    else:
        try:
            # clear the message we got from any non alphabets
            # text = re.sub(r"\W", "_", text)
            # # create the api link for the avatar based on http://avatars.adorable.io/
            # url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
            # # reply with a photo to the name the user sent,
            # # note that you can send photos by url and telegram will fetch it for you
            # bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)

            # save log
            with open(LOG_FILE, 'a') as f:
                user_str = "{} {} {}".format(
                    user['username'],
                    user['last_name'],
                    user['first_name']
                )
                f.write("{} {} {}\n".format(datetime.datetime.now(), user_str, text))

            # send same text with some mark
            bot.sendMessage(chat_id=chat_id, text="**{}**".format(text[::-1]), parse_mode=telegram.ParseMode.MARKDOWN)
        except Exception as ex:
            # if things went wrong
            logging.exception("ERROR!!!")
            bot.sendMessage(
                chat_id=chat_id,
                text="There was a problem in the name you used, please enter different name",
                reply_to_message_id=msg_id
            )
    return 'ok'


@app.route('/')
def index():
    return '.'


def set_webhook():
    bot.setWebhook('https://%s:%s/%s' % (HOST, PORT, TOKEN), certificate=open(CERT, 'rb'))


if __name__ == '__main__':
    set_webhook()
    app.run(threaded=True, host=HOST, port=PORT, ssl_context=context)
