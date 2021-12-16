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
    NOTHING=4
    COMPARING=5



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
            m = "Найдены документы"
            for doc in docs:
                mackup.row(f'** {doc}')
        else:
            m = "Совпадений не обнаружено"
        mackup.row("/menu", "Поиск по названию")
        sessions.update({message.from_user.id:{"stage":Stages.NOTHING}})
        bot.send_message(message.from_user.id, m, reply_markup=mackup)

    elif message.text=="Загрузить документ":
        sessions.update({message.from_user.id:{"stage":Stages.LOAD_FILE, "page":1}})
        hide = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, "Загрузите документ pdf", reply_markup=hide)
    elif message.text =="Все документы" or message.text=="Из списка":
        mackup = telebot.types.ReplyKeyboardMarkup()
        session = sessions.get(message.from_user.id)
        docs = paginator.GetPage(1)
        for doc in docs:
            mackup.row(f'** {doc}')
        if (session and  session.get("page",None) and session.get("page",0)>1):
            mackup.row(">>Следующие 20", "<<Предидущие 20")
        else:
            mackup.row(">>Следующие 20")
            sessions.update({message.from_user.id:{ "stage":session["stage"],"page":1}})
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
            sessions.update({message.from_user.id:{  "stage":session["stage"],"page":page}})
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
            sessions.update({message.from_user.id:{  "stage":session["stage"],"page":page}})
            bot.send_message(message.from_user.id, f"Страница {page}", reply_markup=mackup)
        else:
            mackup.row("/menu", )
            bot.send_message(message.from_user.id, "Что-то пошло не так...", reply_markup=mackup)

    elif message.text == "Поиск по названию":
         sessions.update({message.from_user.id:{"stage":Stages.GET_BY_NAME}})
         hide = telebot.types.ReplyKeyboardRemove()
         bot.send_message(message.from_user.id, "Введите запрос для поиска", reply_markup=hide)
    
    elif message.text.startswith("**"):
        session = sessions.get(message.from_user.id)
        doc = message.text[3:]
        if  session and session["stage"]  == Stages.COMPARING:
            print(session)
            docs = session["doc_names"]
            loaded_docs = session["loaded_docs"]
            docs.append(doc)
            sessions.update({message.from_user.id:{"stage":Stages.COMPARING,'doc_names':docs, 'loaded_docs':loaded_docs }})
            mackup = telebot.types.ReplyKeyboardMarkup()
            mackup.row("Из списка", "Загрузить")
            mackup.row("Выполнить сравнение")
            bot.send_message(message.from_user.id, f"Выбрано ${len(docs)+len(loaded_docs)} документов", reply_markup=mackup)
            return

        doc_bytes = db.doc_by_name(doc)
        session = sessions.get(message.from_user.id)


        hide = telebot.types.ReplyKeyboardRemove()
        if doc_bytes:
            bot.send_message(message.from_user.id, "Загрузка", reply_markup=hide)
            bot.send_document(message.from_user.id, doc_bytes, visible_file_name=doc)
        else:
            bot.send_message(message.from_user.id, "Что-то пошло не так", reply_markup=hide)
        
        mackup = telebot.types.ReplyKeyboardMarkup()
        mackup.row("/menu", "Поиск по названию")
        bot.send_message(message.from_user.id,"Действие:",reply_markup=mackup)
    elif message.text == "Сравнить":
         sessions.update({message.from_user.id:{"stage":Stages.COMPARING, 'doc_names':[], 'loaded_docs':[]}})
         mackup = telebot.types.ReplyKeyboardMarkup()
         mackup.row("Из списка", "Загрузить")
         mackup.row("Выполнить сравнение")
         bot.send_message(message.from_user.id, f"Выбрано 0 документов", reply_markup=mackup)

    elif message.text == "Загрузить":
        hide = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, "Загрузите документ pdf", reply_markup=hide)
    elif message.text == "Выполнить сравнение":
        session = sessions.get(message.from_user.id)
        mackup = telebot.types.ReplyKeyboardMarkup()
        mackup.row("/menu", "Сравнить")
        if session and len(session.get("doc_names",[]))+len(session.get("loaded_docs",[])) >1:
            data = processor.CompareDocs(session.get("doc_names",[]),session.get("loaded_docs",[]) )
            if len(data)>0:
                bot.send_message(message.from_user.id, FormatTable(data), reply_markup=mackup)
            else:
                bot.send_message(message.from_user.id, "Совпадений не обнаружено", reply_markup=mackup)
        else:
            bot.send_message(message.from_user.id, "Выбрано <2 документа", reply_markup=mackup)


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
    elif session and session["stage"] == Stages.COMPARING:
        raw = message.document.file_id
        file_info = bot.get_file(raw)
        bot.send_message(message.from_user.id, "Загрузка файла...")
        downloaded_file = bot.download_file(file_info.file_path)
        docs = session["doc_names"]
        loaded_docs = session["loaded_docs"]
        buf = BytesIO(downloaded_file)
        doc = processor.GetDocPages(buf)
        loaded_docs.append({"name":message.document.file_name, "pages":doc})
        sessions.update({message.from_user.id:{"stage":Stages.COMPARING,'doc_names':docs, 'loaded_docs':loaded_docs }})
        mackup = telebot.types.ReplyKeyboardMarkup()
        mackup.row("Из списка", "Загрузить")
        mackup.row("Выполнить сравнение")
        bot.send_message(message.from_user.id, f"Выбрано ${len(docs)+len(loaded_docs)} документов", reply_markup=mackup)
    else:
         bot.send_message(message.from_user.id, "Я тебя не понял. Начни с главного меню")



bot.infinity_polling()