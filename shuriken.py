
from time import monotonic
import pygame
from pygame.sprite import Sprite, Group
from enemy import Enemy
from etimer import Timer
from mediator import Mediator
from path_handling import load_image
from settings import Settings



class Shuriken(Sprite):
    '''Класс сюрикена, выпускаемого врагами'''
    
    
    def __init__(self, mediator: Mediator, 
        enemy: Enemy, to_right: bool) -> None:
        '''Инициализация сюрикена'''
        super().__init__()
        self.mediator = mediator
        self.to_right = to_right
        self.image = load_image('shuriken1.png')
        self.rect = self.image.get_rect()
        self.starting_location(enemy)
        self.current_image_number = False # потом из bool в int
        self.timer = Timer(monotonic())
        # Действительные значения координаты X центра
        self.centerx = float(self.rect.centerx)
        
        

    def starting_location(self, enemy: Enemy):
        '''Начальное положение сюрикена'''
        self.rect.centery = enemy.rect.top + 19
        if self.to_right:
            self.rect.centerx = enemy.rect.right + int(self.rect.width/2)
        else:
            self.rect.centerx = enemy.rect.left - int(self.rect.width/2)

    def blitme(self):
        '''Отображает сюрикен на экране'''
        self.mediator.blit_surface(self.image, self.rect)
    

    def update(self, *args) -> None:
        '''Обновляет положение сюрикена'''
        # В какую сторону летит сюрикен
        if self.to_right:
            self.centerx += self.mediator.get_value('ai_settings', 'shuriken_speed')
        else:
            self.centerx -= self.mediator.get_value('ai_settings', 'shuriken_speed')
        # Анимация
        if self.mediator.current_time() - self.timer >= self.mediator.get_value(
            'ai_settings', 'animation_change')/2:
            self.image = load_image(f'shuriken{int(self.current_image_number) + 1}.png')
            self.timer.time = monotonic()
            self.current_image_number = not self.current_image_number
        # Действительные значения в целочисленные
        self.rect.centerx = int(self.centerx)
        # Если сюрикен за пределами экрана - удаляет его из группы ударных поверхностей
        if not self.rect.colliderect(self.mediator.get_value('screen_rect')):
            self.kill()
        