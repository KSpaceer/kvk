import sys
from os.path import join
from pygame.image import load
from pygame import Surface
from pygame.mixer import Sound


def resource_path(folder, *paths):
    if hasattr(sys, '_MEIPASS'):
        path = join(sys._MEIPASS, folder)
    else: 
        path = folder
    for rel_path in paths:
        path = join(path, rel_path)
    return path

def load_image(*paths):
    path = resource_path('images', *paths)
    img: Surface = load(path)
    return img.convert_alpha()

def load_sound(*paths):
    path = resource_path('audio', *paths)
    sound = Sound(path)
    return sound

