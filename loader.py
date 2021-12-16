import os
from adaptors.db import DBConnect
from adaptors.pdf import getPagesText
from io import BytesIO
    

def loadToDb():
    db = DBConnect("postgres",
                   "Cbvajybz13",
                   "195.2.74.188",
                   "5432",
                   )
    for pdf in os.listdir("./PDF"):
        with open("./PDF/"+pdf,"rb") as f:
            buf = BytesIO(f.read())
            texts = getPagesText(buf)
            if len(texts)>0:
                db.create_doc(pdf,texts)

def loadFilesToDb():
    db = DBConnect("postgres",
                   "Cbvajybz13",
                   "195.2.74.188",
                   "5432",
                   )
    for pdf in os.listdir("./PDF"):
        with open("./PDF/"+pdf,"rb") as f:
            db.create_only_doc_bytes(pdf, f.read())


loadFilesToDb()