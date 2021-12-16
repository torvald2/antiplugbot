from nltk.util import pr
import os 
import telebot
from enum import Enum
from services.similar import Processor
from adaptors.db import DBConnect
from io import BytesIO
from heplers import FormatTable
from services.docs import  DocsPaginator

class Stages(Enum):
    LOAD_FILE = 1
    PAGINATE= 2
    GET_BY_NAME=3


dbUser = os.environ.get("DB_USER")
dbPassword = os.environ.get("DB_PASSWORD")
dbHost = os.environ.get("DB_HOST")
dbPort = os.environ.get("DB_PORT")

telegramKey = os.environ.get("TELE_KEY")

bot = telebot.TeleBot(telegramKey, parse_mode="HTML")

db = DBConnect(dbUser, dbPassword, dbHost,dbPort)

processor = Processor(db)
paginator  = DocsPaginator(db)

sessions = {}

@bot.message_handler(commands=["start","menu"])
def createMainMenu(message):
    main_mackup = telebot.types.ReplyKeyboardMarkup()
    main_mackup.row("Загрузить документ")
    main_mackup.row("Все документы", "Сравнить")

    bot.send_message(message.from_user.id, "Выберите действие",reply_markup=main_mackup)

@bot.message_handler(content_types=['text'])
def keyboardActions(message):
    session = sessions.get(message.from_user.id)
    if session and session["stage"] == Stages.GET_BY_NAME:
        docs  = paginator.FindByName(message.text)
        mackup = telebot.types.ReplyKeyboardMarkup()
        if len(docs) >0:
            message = "Найдены документы"
            for doc in docs:
                mackup.row(f'** {doc}')
        else:
            message = "Совпадений не обнаружено"
        mackup.row("/menu", "Поиск по названию")
        bot.send_message(message.from_user.id, message, reply_markup=message)

    elif message.text=="Загрузить документ":
        sessions.update({message.from_user.id:{"stage":Stages.LOAD_FILE, "page":1}})
        hide = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, "Загрузите документ pdf", reply_markup=hide)
    elif message.text =="Все документы":
        mackup = telebot.types.ReplyKeyboardMarkup()
        session = sessions.get(message.from_user.id)
        docs = paginator.GetPage(1)
        for doc in docs:
            mackup.row(f'** {doc}')
        if (session and session["page"]>1):
            mackup.row(">>Следующие 20", "<<Предидущие 20")
        else:
            mackup.row(">>Следующие 20")
            sessions.update({message.from_user.id:{"stage":Stages.PAGINATE, "page":1}})
        mackup.row("/menu", "Поиск по названию")

        docs = paginator.GetPage(1)
        bot.send_message(message.from_user.id, "Страница 1", reply_markup=mackup)

    elif message.text ==">>Следующие 20":
        mackup = telebot.types.ReplyKeyboardMarkup()
        session = sessions.get(message.from_user.id)
        if session:
            page = session["page"]+1
            docs = paginator.GetPage(page)
            for doc in docs:
                mackup.row(f'** {doc}')
            if paginator.IsLastPage(session["page"]):
                mackup.row("<<Предидущие 20")
            else:
                mackup.row(">>Следующие 20", "<<Предидущие 20")
            mackup.row("/menu", "Поиск по названию")
            sessions.update({message.from_user.id:{"stage":Stages.PAGINATE, "page":page}})
            bot.send_message(message.from_user.id, f"Страница {page}", reply_markup=mackup)
        else:
            mackup.row("/menu", )
            bot.send_message(message.from_user.id, "Что-то пошло не так...", reply_markup=mackup)
    
    elif message.text =="<<Предидущие 20":
        mackup = telebot.types.ReplyKeyboardMarkup()
        session = sessions.get(message.from_user.id)
        if session:
            page = session["page"]-1
            if page <1:
                 mackup.row("/menu")
                 bot.send_message(message.from_user.id, f"Попытка зайти на страницу <1", reply_markup=mackup)
            docs = paginator.GetPage(page)
            for doc in docs:
                mackup.row(f'** {doc}')
            if paginator.IsLastPage(session["page"]):
                mackup.row("<<Предидущие 20")
            else:
                mackup.row(">>Следующие 20", "<<Предидущие 20")
            mackup.row("/menu", "Поиск по названию")
            sessions.update({message.from_user.id:{"stage":Stages.PAGINATE, "page":page}})
            bot.send_message(message.from_user.id, f"Страница {page}", reply_markup=mackup)
        else:
            mackup.row("/menu", )
            bot.send_message(message.from_user.id, "Что-то пошло не так...", reply_markup=mackup)

    elif message.text == "Поиск по названию":
         sessions.update({message.from_user.id:{"stage":Stages.GET_BY_NAME}})
         hide = telebot.types.ReplyKeyboardRemove()
         bot.send_message(message.from_user.id, "Введите запрос для поиска", reply_markup=hide)
    
    elif message.text.startswith("**")!=-1:
        doc = message.text[3:]
        doc_bytes = db.doc_by_name(doc)

        hide = telebot.types.ReplyKeyboardRemove()
        if doc_bytes:
            bot.send_message(message.from_user.id, "Загрузка", reply_markup=hide)
            bot.send_document(message.from_user.id, doc_bytes)
        else:
            bot.send_message(message.from_user.id, "Что-то пошло не так", reply_markup=hide)
        
        mackup = telebot.types.ReplyKeyboardMarkup()
        mackup.row("/menu", "Поиск по названию")
        bot.send_message(message.from_user.id,"Действие:",reply_markup=mackup)



        


        






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
        sim = processor.GetSimilarDocs(buf,message.document.file_name)
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