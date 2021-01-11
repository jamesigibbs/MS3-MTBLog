import os

def template_exists(name):
    return os.path.isfile("templates/" + name + ".html")