
import pygame
from background import Background
from mediator import Mediator
from path_handling import load_image

from settings import Settings

class Tarzan():
    '''Для заставки'''

    def __init__(self, mediator: Mediator) -> None:
        '''Инициализирует параметры основные'''
        self.image = load_image('Tarzan.png')
        self.rect = self.image.get_rect()
        self.mediator = mediator
        self.rect.center = self.mediator.get_value('screen_rect', 'center')
        self.direction = False
        

    def update_intro(self):
        '''Обновляет заставку'''
        self.mediator.call_method('bg', 'blitme')
        if not self.direction:
            if self.rect.centery != self.mediator.get_value(
                'screen_rect', 'centery') - 25:
                self.rect.centery -= 1
            else:
                self.direction = True
        else:
            if self.rect.centery != self.mediator.get_value(
                'screen_rect', 'centery') + 25:
                self.rect.centery += 1
            else:
                self.direction = False
            
        self.mediator.blit_surface(self.image, self.rect)
        pygame.display.flip()

    
