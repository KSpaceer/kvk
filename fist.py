import pygame
from pygame.sprite import Sprite

class Fist(Sprite):
    '''Класс для кулака(хотя это может быть и нога). В общем, 
    ударная поверхность'''

    
    
    def __init__(self, screen: pygame.Surface):
        '''Инициализация параметров ударной поверхности'''
        super().__init__()
        self.screen = screen
        surface = pygame.Surface((15,15))
        self.rect = surface.get_rect()
        # Ударная поверхность появляется за пределами экрана
        self.rect.centerx = -50
        self.rect.centery = -50
        

    def change_position(self, left, top):
        '''Изменяет расположение ударной поверхности'''
        self.rect.left = left
        self.rect.top = top
        
    