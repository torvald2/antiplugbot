import fitz


def getPagesText(pdf):
    texts = []
    try:
        doc = fitz.open("pdf",pdf)
        for page in doc:
            texts.append(page.get_text())
    except:
        print(f"Bad file {pdf}")
    return texts



        