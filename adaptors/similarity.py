from psycopg2 import connect
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.corpus import stopwords
import nltk
import numpy as np
import numpy.linalg as LA
from threading import Thread
from queue import Queue



nltk.download('stopwords')

class Vectorizer:
    def __init__(self,data) -> None:
        stopWords = stopwords.words('english')
        self.__vectorizer = CountVectorizer(stop_words = stopWords)
        self.__tfidf = self.__vectorizer.fit_transform(data).toarray()
    
    def getDocVectors(self, corpus):
        return self.__vectorizer.transform(corpus).toarray()

    @property
    def vectors(self):
        return self.__tfidf



def ProcessDistance(tfidf, metadata, page):
    res = []
    c = lambda a, b : round(np.inner(a, b)/(LA.norm(a)*LA.norm(b)), 3)
    i = 0
    for vec in tfidf:
        cosine = c(vec, page)
        if cosine >0.5:
            res.append({"cosine":cosine, "doc":metadata[i][0], "page":metadata[i][1]})
        i+=1
    return res
        
