import pygame

from mediator import Mediator



class Background:
    '''Класс заднего фона игры'''

    PASTER_EGG_ACTIVE = False
    
    def __init__(self, mediator: Mediator) -> None:
        self.mediator = mediator
        self.image = pygame.image.load('images/backgrounds/intro.png').convert()
        
    
    def blitme(self) -> None:
        '''Прорисовка заднего фона'''
        self.mediator.blit_surface(self.image, (0, 0))

    def change(self, name: str) -> None:
        '''Смена заднего фона'''
        if not Background.PASTER_EGG_ACTIVE:
            self.image = pygame.image.load('images/backgrounds/' + name + '.png').convert()
        else:
            self.image = pygame.image.load('images/backgrounds/sans.png').convert()
        
    
     