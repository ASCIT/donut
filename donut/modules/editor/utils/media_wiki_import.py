#!/usr/bin/env python

import argparse
from donut.pymysql_connection import make_db
import re
import xml.etree.ElementTree as ET


def import_file(env, filename):
    # Create reference to DB
    db = make_db(env)
    try:
        db.begin()
        tree = ET.parse(filename)
        root = tree.getroot()
        query = "INSERT INTO webpage_files(title, last_edit_time, content) VALUES( %s, %s, %s)"

        with db.cursor() as cursor:
            for elem in root:
                text = ""
                date = ""
                title = ""
                for ele in elem:
                    if 'title' in ele.tag:
                        if 'Image:' in ele.text:
                            break
                        title = ele.text
                    if 'revision' in ele.tag:
                        for i in ele:
                            if 'timestamp' in i.tag:
                                date = i.text
                            if 'text' in i.tag:
                                text = i.text
                if title != '' and text != '' and text is not None:
                    if date != "":
                        date = date.replace("T", " ")
                        date = date.replace("Z", "")
                    title = title.replace(" ", "_")
                    text = format_text(text)
                    cursor.execute(query, [title, date, text])
        db.commit()
    finally:
        db.close()


def format_text(text):
    # Headings
    matches = re.findall(r"\=+[\+0-9a-zA-Z\(\)\'\* \-\,\?\.]+\=+", text)
    for i in matches:
        text = text.replace(i, i.replace("=", "#"))

    #[[Image:Everyone's the same size.png |500px]]
    # Images use a slightly different url.
    matches = re.findall(r"\[\[Image\:[^\]]*\|?[0-9a-zA-Z.]*[px]?\]\]", text)
    for i in matches:
        link = i.replace("[", "").replace("]", "")
        link = link.replace("Image:", "")
        link_piece = link.split("|")
        if len(link_piece) == 1:
            text = text.replace(i, '![' + link_piece[0] + '](uploaded_file/' +
                                link_piece[0].strip().replace(" ", "_") + ')')
        # The image width is set
        # LOL all the images are gonna be squares this is stupid @showdown
        else:
            size = link_piece[1].strip()[:-2]
            text = text.replace(
                i, '![' + link_piece[0].strip() + '](uploaded_file' +
                link_piece[0].strip().replace(
                    " ", "_") + " =" + size + "x" + size + ')')

    # Find all links and replace them -- purposefully missing @
    text = re.sub(
        r"\[(https?://[\&\~\?\%\+0-9a-zA-Z.\./\-_:\#\=\+;,]*) ([^\|\]]*)\]",
        r"[\2](\1)", text)

    # Donut's internal links
    matches = re.findall(
        r"\[\[[\%\+0-9a-zA-Z.\./\-_:\#\= ]*\|?[0-9a-zA-Z.\./\-_:\# ]*\]\]",
        text)
    file_upload_folder = "uploaded_file/"
    for i in matches:
        link = i.replace("[", "").replace("]", "")
        link_piece = link.split("|")
        file_uploads = ""
        if "Media:" in link_piece[0]:
            file_uploads = file_upload_folder
            link_piece[0] = link_piece[0].replace("Media:", "")
        # Text is same as link title
        if len(link_piece) == 1:
            text = text.replace(
                i, '[' + link_piece[0] + ']' + '(' + file_uploads +
                link_piece[0].strip().replace(" ", "_") + ')')
        # The text is different from the link title.
        else:
            text = text.replace(
                i, '[' + link_piece[1].strip() + ']' + '(' + file_uploads +
                link_piece[0].strip().replace(" ", "_") + ')')

    for i in range(4, 0, -1):
        text = text.replace("*" * i, "\t" * (i - 1) + "* ")

    # Bolded first --> ''' -> **
    text = text.replace("'''", "**")

    # Italics
    text = text.replace("''", "*")

    # Reformat emails
    text = re.sub(r"\[(mailto:[0-9a-zA-Z.\@'\-]*) ([^\]]*)\]", r"[\2](\1)",
                  text)

    # Reformat the tables
    matches = re.findall(
        r"\{\|[\%\+0-9a-zA-Z.\./\-_:\# \n\[\]@\t\|\=\(\)\'\*]*\|\}", text)
    for i in matches:
        table = i.replace("\n", "")
        table = table.replace("|-", "| \n")
        table = table.replace("}", "")
        table = table.replace("{", "")

        setting_matches = re.findall(r"\|width\=[0-9]*", table)
        if len(setting_matches) > 0:
            table = table.replace(setting_matches[0], "")

        divider = ""
        first_row_end = table.find("\n|")
        cols = table[:first_row_end].count("|")
        divider = "\n|" + "|".join(["-" * 5 for i in range(cols - 1)]) + "|"
        table = table[:first_row_end] + divider + table[first_row_end:]

        text = text.replace(i, table)

    # Some people actually typed this out
    text = text.replace("<p>", "")
    text = text.replace("</p>", "")
    # Get rid of table of contents settings
    text = text.replace("__NOTOC__\n", "")

    text = text.encode()

    return text


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser(
        description="Imports a list of students exported by the registrar")
    parser.add_argument(
        "-e", "--env", default="dev", help="Database to update")
    parser.add_argument("file", help="Path to old media wiki xml")
    args = parser.parse_args()

    import_file(args.env, args.file)
