from nltk.util import pr
import os 
import telebot
from enum import Enum
from services.similar import Processor
from adaptors.db import DBConnect
from io import BytesIO
from heplers import FormatTable

class Stages(Enum):
    LOAD_FILE = 1
    PAGINATE= 2


dbUser = os.environ.get("DB_USER")
dbPassword = os.environ.get("DB_PASSWORD")
dbHost = os.environ.get("DB_PORT")

telegramKey = os.environ.get("TELE_KEY")

bot = telebot.TeleBot(telegramKey, parse_mode="HTML")

db = DBConnect(dbUser, dbPassword, dbHost)

processor = Processor(db)

sessions = {}

@bot.message_handler(commands=["start","menu"])
def createMainMenu(message):
    main_mackup = telebot.types.ReplyKeyboardMarkup()
    main_mackup.row("Загрузить документ")
    main_mackup.row("Все документы", "Сравнить")

    bot.send_message(message.from_user.id, "Выберите действие",reply_markup=main_mackup)

@bot.message_handler(content_types=['text'])
def keyboardActions(message):
    if message.text=="Загрузить документ":
        sessions.update({message.from_user.id:{"stage":Stages.LOAD_FILE}})
        hide = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, "Загрузите документ pdf", reply_markup=hide)
    

@bot.message_handler(content_types=["document"])
def document_action(message):
    session = sessions.get(message.from_user.id)
    if session and session["stage"] == Stages.LOAD_FILE:
        raw = message.document.file_id
        file_info = bot.get_file(raw)
        bot.send_message(message.from_user.id, "Загрузка файла...")
        downloaded_file = bot.download_file(file_info.file_path)
        bot.send_message(message.from_user.id, "Сравнение...")
        buf = BytesIO(downloaded_file)
        sim = processor.GetSimilarDocs(buf)
        if len(sim)>0:
            bot.send_message(message.from_user.id,"Найдено совпадение:")
            mackup = telebot.types.ReplyKeyboardMarkup()
            mackup.row("/menu", "Загрузить документ")
            bot.send_message(message.from_user.id, FormatTable(sim), reply_markup=mackup)

        else:
            bot.send_message(message.from_user.id,"Совпадений не обнаружено")
    else:
         bot.send_message(message.from_user.id, "Я тебя не понял. Начни с главного меню")


bot.infinity_polling()