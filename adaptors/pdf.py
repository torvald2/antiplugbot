from logging import exception
import fitz


def getPagesText(buf):
    texts = []
    try:
        doc = fitz.open("pdf",buf)
        for page in doc:
            
            texts.append(page.get_text())
    except Exception as e:
        print(e)
    return texts

