def FormatTable(items):
    res = '<pre>|        Оригинал        | Исходная исх. | Страница ориг. |\n'
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
        
        res += f'|{doc}|{source}|{page}|\n'
    res+= "</pre>"

    return res

def FormatList(items):
    res = '<pre> \n'
    for item in items:
        res += f'* {item}\n'
    res+= "</pre>"
    return res
        
        