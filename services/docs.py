import math
class DocsPaginator:
    def __init__(self,db) -> None:
        self.db = db
        docCount =  db.get_docs_count()
        self.pages = math.ceil(docCount/30)

    def GetPage(self,page):
        offset = (page-1)*20+1
        return self.db.get_doc_names(20, offset)
    
    def IsLastPage(self,page):
        return self.pages == page

    def FindByName(self, name):
        name = name.lower()
        res = []
        data = self.db.get_doc_names(99999, 0)
        for i in data:
            if i.lower().find(name)!=-1:
                res.append(i)
        return res
