from io import BytesIO
def FormatTable(items):
    buf = ''
    buf+='|        Оригинал        | Исходная исх. | Страница ориг. |\n'
    for item in items:
        if len(item["doc"]) >24:
            doc = item["doc"][:24]
        else:
            doc = item["doc"] + ''.join([' ' for x in range(24-len(item["doc"]))])

        if item["source"]>9:
            source = f'      {item["source"]}       '
        else:
            source = f'       {item["source"]}       '

        if item["page"]>9:
            page = f'      {item["page"]}      '
        else:
            page = f'       {item["page"]}      '
        
        buf+=f'|{doc}|{source}|{page}|\n'
    return buf.encode("utf-8")

def FormatTableDocs(items):
    res = '|        Документ1       |        Документ2       |Стр1|Стр2|\n'
    for item in items:
        if len(item["doc"]) >24:
            doc = item["doc"][:24]
        else:
            doc = item["doc"] + ''.join([' ' for x in range(24-len(item["doc"]))])
        
        if len(item["source_doc"]) >24:
            doc1 = item["source_doc"][:24]
        else:
            doc1 = item["source_doc"] + ''.join([' ' for x in range(24-len(item["source_doc"]))])

        if item["source"]>9:
            source = f' {item["source"]} '
        else:
            source = f' {item["source"]}  '

        if item["page"]>9:
            page = f' {item["page"]} '
        else:
            page = f' {item["page"]}  '
        
        res += f'|{doc}|{doc1}|{source}|{page}|\n'

    return res.encode("utf-8")


        