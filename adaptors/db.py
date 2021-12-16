import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class DBConnect:
    def __init__(self, user, password, host,port):
        self.user = user
        self.password = password
        self.host =host
        self.port = port
        self.db = "recognize"
        
        self.__create_db()
        self.__create_tables()
    
 

    def __get_connect(self):
        return psycopg2.connect(user = self.user,
                               password=self.password,
                               host = self.host,
                               port = self.port,
                               database = self.db
                               )
     
    def __create_db(self):
        con = psycopg2.connect(user = self.user,
                               password=self.password,
                               host = self.host,
                               port = self.port,
                               )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()

        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'recognize'")
        exists = cur.fetchone()
        if not exists:
            cur.execute('CREATE DATABASE recognize')
        cur.close()
        con.close()

    
    def __create_tables(self):
        con = self.__get_connect()
        cursor = con.cursor()
        cursor.execute('''
                 CREATE TABLE IF NOT EXISTS pages
                 (
                     id SERIAL,
                     book TEXT NOT NULL,
                     page SMALLINT NOT NULL,
                     text TEXT
                 )
        
        ''')
        cursor.execute('''
                 CREATE TABLE IF NOT EXISTS docs
                 (
                     id SERIAL,
                     doc_name TEXT NOT NULL,
                     data bytea NOT NULL
                 )
        
        ''')


        con.commit()
        cursor.close()
        con.close()

    def create_doc(self, doc_name, pages, docBytes):
        con = self.__get_connect()
        cursor = con.cursor()
        i = 1
        for page in pages:
            cursor.execute(f'''
                 INSERT INTO pages
                 (book, page, text)
                 VALUES (%s, %s, %s)
                 ''', (doc_name,i,page))
            i+=1
        cursor.execute(f'''
            INSERT INTO docs
            (doc_name, data)
            VALUES (%s, %s)
        ''', (doc_name,docBytes))
        con.commit()
        cursor.close()
        con.close()
    
    def get_all_docs(self):
        metadata =[]
        texts = []
        con = self.__get_connect()
        cur = con.cursor()
        cur.execute("SELECT book, page, text FROM pages")

        for doc in cur.fetchall():
            texts.append(doc[2])
            metadata.append([doc[0],doc[1]])
        
        return (texts, metadata)
        
    def create_only_doc_bytes(self, doc_name, docBytes):
        con = self.__get_connect()
        cursor = con.cursor()    
        cursor.execute(f'''
            INSERT INTO docs
            (doc_name, data)
            VALUES (%s, %s)
        ''', (doc_name,psycopg2.Binary(docBytes)))
        con.commit()
        cursor.close()
        con.close()
    
    def get_doc_names(self, limit, offset):
        data = []
        con = self.__get_connect()
        cur = con.cursor()
        cur.execute("SELECT doc_name FROM docs LIMIT %s OFFSET %s",(limit, offset))
        for doc in cur.fetchall():
            data.append(doc[0])
        cur.close()
        con.close()
        return data

    
    def get_docs_count(self):
        con = self.__get_connect()
        cur = con.cursor()
        cur.execute("SELECT count(*) FROM docs")
        data = cur.fetchone()
        return data[0]
        

    def doc_by_name(self, name):
        con = self.__get_connect()
        cur = con.cursor()
        cur.execute(f"SELECT data FROM docs WHERE doc_name='{name}' ",)
        blob = cur.fetchone()
        cur.close()
        con.close()
        return blob[0]




        
        



