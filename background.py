import pygame

from mediator import Mediator
from base64 import b64decode
from path_handling import load_image, resource_path



class Background:
    '''Класс заднего фона игры'''

    PASTER_EGG_ACTIVE = False
    
    def __init__(self, mediator: Mediator) -> None:
        self.mediator = mediator
        self.image = load_image('backgrounds', 'intro.png')
        
        
    
    def blitme(self) -> None:
        '''Прорисовка заднего фона'''
        self.mediator.blit_surface(self.image, (0, 0))

    def change(self, name: str) -> None:
        '''Смена заднего фона'''
        if not Background.PASTER_EGG_ACTIVE:
            try:
                self.image = load_image('backgrounds', name + '.png')
            except FileNotFoundError:
                with open(resource_path('images', 'backgrounds', name + '.bin'), 'rb') as f:
                    data = f.read()
                    data = b64decode(data)
                with open(resource_path('images', 'backgrounds', name + '.png'), 'wb') as img:
                    img.write(data)
                self.image = self.image = load_image('backgrounds', name + '.png')
        else:
            self.image = load_image('backgrounds', 'sans.png')

    
        
    
     