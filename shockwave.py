from random import randint
from time import monotonic
import pygame
from pygame.sprite import Sprite, Group
from etimer import Timer
from fist import Fist
from mediator import Mediator
from path_handling import load_image
from settings import Settings

class Shockwave(Sprite):
    '''Класс ударной волны, вызываемой врагами'''

    

    direction = {True : 'right', False : 'left'}
    
    
    def __init__(self, mediator: Mediator, to_right: bool = True, 
        *, en_fist: Fist = None, boss = None) -> None:
        '''Инициализация ударной волны'''
        super().__init__()
        self.mediator = mediator
        self.to_right = to_right
        self.image = load_image('Shockwave', 
            f'shockwave1_{Shockwave.direction[to_right]}.png')
        self.rect = self.image.get_rect()
        self.starting_location(en_fist=en_fist, boss=boss)
        self.current_image_number = False # потом из bool в int
        self.timer = monotonic()
        # Действительные значения координаты X центра
        self.centerx = float(self.rect.centerx)
        
        

    
        

    def starting_location(self, en_fist: Fist, boss):
        '''Начальное положение волны'''
        if en_fist:
            self.rect.bottom = en_fist.rect.bottom
            if self.to_right:
                self.rect.left = en_fist.rect.right
            else:
                self.rect.right = en_fist.rect.left
        elif boss:
            exec(f'self.rect.{Shockwave.direction[not self.to_right]}' +
                f'= boss.an_rect.{Shockwave.direction[self.to_right]}')
            self.rect.centery = randint(boss.an_rect.top, boss.an_rect.bottom)
        else:
            raise TypeError
        

    def blitme(self):
        '''Отображает волну на экране'''
        self.mediator.blit_surface(self.image, self.rect)

    def update(self, *args) -> None:
        '''Обновляет положение волны'''
        # В какую сторону летит волна
        if self.to_right:
            self.centerx += self.mediator.get_value(
                'ai_settings', 'shockwave_speed')
        else:
            self.centerx -= self.mediator.get_value(
                'ai_settings', 'shockwave_speed')
        # Анимация
        if self.mediator.current_time() - self.timer >= self.mediator.get_value(
            'ai_settings', 'animation_change'):
            self.image = load_image('Shockwave', 
                f'shockwave{int(self.current_image_number) + 1}' 
                + f'_{Shockwave.direction[self.to_right]}.png')
            self.timer = monotonic()
            self.current_image_number = not self.current_image_number
        # Действительные значения в целочисленные
        self.rect.centerx = int(self.centerx)
        # Если волна вышла за пределы экрана, удаляет ее из группы ударных поверхностей врагов
        if not self.rect.colliderect(self.mediator.get_value('screen_rect')):
            self.kill()

        
