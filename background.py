import pygame
from os import listdir
from os.path import abspath


class Background:
    '''Класс заднего фона игры'''


    
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.image = pygame.image.load('images/backgrounds/intro.png').convert()

    def blitme(self) -> None:
        '''Прорисовка заднего фона'''
        self.screen.blit(self.image, (0, 0))

    def change(self, name: str) -> None:
        '''Смена заднего фона'''
        self.image = pygame.image.load('images/backgrounds/' + name + '.png').convert()
        
        