import os
from adaptors.db import DBConnect
from adaptors.pdf import getPagesText
from io import BytesIO
    

def loadToDb():
    db = DBConnect("wxpdtfrapvwyqy",
                   "dfb747abe69e97535f929ce3522a19335e8fa6ae1d7d0161866c2f1d69e02d62",
                   "ec2-3-89-214-80.compute-1.amazonaws.com",
                   "5432",
                   "d9beuhrts4uk1d"
                   )
    for pdf in os.listdir("./PDF"):
        with open("./PDF/"+pdf,"rb") as f:
            buf = BytesIO(f.read())
            texts = getPagesText(buf)
            if len(texts)>0:
                db.create_doc(pdf,texts)

loadToDb()