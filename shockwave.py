from time import monotonic
import pygame
from pygame.sprite import Sprite, Group
from etimer import Timer
from fist import Fist
from settings import Settings

class Shockwave(Sprite):
    '''Класс ударной волны, вызываемой врагами'''

    direction = {True : 'right', False : 'left'}
    
    def __init__(self, screen: pygame.Surface, cur_time: Timer, 
        en_fist: Fist, ai_settings: Settings, to_right: bool = True) -> None:
        '''Инициализация ударной волны'''
        super().__init__()
        self.ai_settings = ai_settings
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.to_right = to_right
        self.image = pygame.image.load(
            f'images/Shockwave/shockwave1_{Shockwave.direction[to_right]}.png')
        self.rect = self.image.get_rect()
        self.starting_location(en_fist)
        self.cur_time = cur_time
        self.current_image_number = False # потом из bool в int
        self.timer = Timer(monotonic())
        # Действительные значения координаты X центра
        self.centerx = float(self.rect.centerx)
        
        

    
        

    def starting_location(self, en_fist):
        '''Начальное положение волны'''
        self.rect.bottom = en_fist.rect.bottom
        if self.to_right:
            self.rect.left = en_fist.rect.right
        else:
            self.rect.right = en_fist.rect.left

    def blitme(self):
        '''Отображает волну на экране'''
        self.screen.blit(self.image, self.rect)

    def update(self, en_fists: Group, *args) -> None:
        '''Обновляет положение волны'''
        # В какую сторону летит волна
        if self.to_right:
            self.centerx += self.ai_settings.shockwave_speed
        else:
            self.centerx -= self.ai_settings.shockwave_speed
        # Анимация
        if self.cur_time - self.timer >= self.ai_settings.animation_change:
            self.image = pygame.image.load('images/Shockwave/shockwave' + 
                f'{int(self.current_image_number) + 1}_' + 
                f'{Shockwave.direction[self.to_right]}.png')
            self.timer.time = monotonic()
            self.current_image_number = not self.current_image_number
        # Действительные значения в целочисленные
        self.rect.centerx = int(self.centerx)
        # Если волна вышла за пределы экрана, удаляет ее из группы ударных поверхностей врагов
        if not self.screen_rect.colliderect(self.rect):
            en_fists.remove(self)
        
