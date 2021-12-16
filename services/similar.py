from adaptors.pdf import getPagesText
from adaptors.similarity import Vectorizer, ProcessDistance
import multiprocessing as mp
class Processor:
    def __init__(self,db) -> None:
        self.texts, self.metadata = db.get_all_docs()
        self.v = Vectorizer(self.texts)
        self.db = db

        
    def GetSimilarDocs(self, doc, doc_name):
        result = []
        pages = getPagesText(doc)
        self.db.create_doc(doc_name, pages, doc.read())
        pageVec = self.v.getDocVectors(pages)
        i = 1
        for page in pageVec:
            data = ProcessDistance(self.v.vectors, self.metadata, page)
            for k in data:
                k.update({"source":i})
                result.append(k)
            i+=1
        self.texts, self.metadata = self.db.get_all_docs()
        self.v = Vectorizer(self.texts)
        return result
    
    def GetDocPages(self,doc):
        return getPagesText(doc)

    def CompareDocs(self, doc_names,loaded_docs):
        return []
        


        