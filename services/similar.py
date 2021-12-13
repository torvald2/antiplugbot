from adaptors.pdf import getPagesText
from adaptors.similarity import Vectorizer, ProcessDistance
import multiprocessing as mp
class Processor:
    def __init__(self,db) -> None:
        self.texts, self.metadata = db.get_all_docs()
        self.v = Vectorizer(self.texts)

        
    def GetSimilarDocs(self, doc):
        result = []
        pages = getPagesText(doc)
        pageVec = self.v.getDocVectors(pages)
        i = 1
        for page in pageVec:
            data = ProcessDistance(self.v.vectors, self.metadata, page)
            for k in data:
                k.update({"source":i})
                result.append(k)
            i+=1   
        return result
        


        