import xml.etree.ElementTree as ET


def parser_input_message(input_message):
    root = ET.fromstring(input_message)
    fromusername = ""
    message = ""
    tousername = ""
    for move in root:
        if move.tag == "FromUserName":
            fromusername = move.text
        elif move.tag == "Content":
            message = move.text
        elif move.tag == "ToUserName":
            tousername = move.text
    return fromusername, tousername, message


