import flask


def create_new_html():
    """
    Creates a blank html page. 
    """
    with open("template.html") as f:
        with open("title.html") as f1:
            for line in f:
                f1.write(line)
    return


def rename_title(oldfilename, newfilename):
    """
    Changes the file name of an html file
    Need to look for paths
    """

    os.rename(oldfilename, newfilename)
    return
