import psycopg2


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

        con.commit()
        cursor.close()
        con.close()

    def create_doc(self, doc_name, pages):
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
    
    

        
        



