import pygame
from pygame.sprite import Sprite

from mediator import Mediator

class Fist(Sprite):
    '''Класс для кулака(хотя это может быть и нога). В общем, 
    ударная поверхность'''

    
    
    def __init__(self, mediator: Mediator):
        '''Инициализация параметров ударной поверхности'''
        super().__init__()
        self.mediator = mediator
        surface = pygame.Surface((15,15))
        self.rect = surface.get_rect()
        # Ударная поверхность появляется за пределами экрана
        self.rect.centerx = -50
        self.rect.centery = -50
        

    def change_position(self, left, top):
        '''Изменяет расположение ударной поверхности'''
        self.rect.left = left
        self.rect.top = top
        
    def blitme(self):
        pass
    