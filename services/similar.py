from adaptors.pdf import getPagesText
from adaptors.similarity import Vectorizer, ProcessDistance
import multiprocessing as mp
import numpy as np
import numpy.linalg as LA
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
        c = lambda a, b : round(np.inner(a, b)/(LA.norm(a)*LA.norm(b)), 3)
        vectors =[]
        metadatas =[]
        docs =[]
        res =[]

        for name in doc_names:
            docPages = self.db.get_doc_texts(name)
            docs.append({"name":name, "pages":docPages})
        all_docs = [*docs, *loaded_docs]
        for doc in all_docs:
            metadata =[[doc["name"], i] for i in range(len(doc["pages"]))]
            vec = self.v.getDocVectors(doc["pages"])
            vectors.extend(vec)
            metadatas.extend(metadata)
        x = 0
        for i in vectors:
            y=0
            for j in vectors:
                
                dist = c(i,j)
                if dist >0.5:
                    res.append({"cosine":dist,"source": metadata[y][1],"source_doc":metadata[y][0],"doc":metadata[x][0], "page":metadata[x][1]})
                y+=1
            i+=1
        return res
        


        