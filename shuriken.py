
from time import monotonic
import pygame
from pygame.sprite import Sprite, Group
from enemy import Enemy
from etimer import Timer
from settings import Settings



class Shuriken(Sprite):
    '''Класс сюрикена, выпускаемого врагами'''
    
    
    def __init__(self, screen: pygame.Surface, cur_time: Timer, 
        enemy: Enemy, ai_settings: Settings, to_right: bool) -> None:
        '''Инициализация сюрикена'''
        super().__init__()
        self.ai_settings = ai_settings
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.to_right = to_right
        self.image = pygame.image.load('images/shuriken1.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.starting_location(enemy)
        self.cur_time = cur_time
        self.current_image_number = False # потом из bool в int
        self.timer = Timer(monotonic())
        # Действительные значения координаты X центра
        self.centerx = float(self.rect.centerx)
        
        

    def starting_location(self, enemy):
        '''Начальное положение сюрикена'''
        self.rect.centery = enemy.rect.top + 19
        if self.to_right:
            self.rect.centerx = enemy.rect.right + int(self.rect.width/2)
        else:
            self.rect.centerx = enemy.rect.left - int(self.rect.width/2)

    def blitme(self):
        '''Отображает сюрикен на экране'''
        self.screen.blit(self.image, self.rect)

    def update(self, en_fists: Group, *args) -> None:
        '''Обновляет положение сюрикена'''
        # В какую сторону летит сюрикен
        if self.to_right:
            self.centerx += self.ai_settings.shuriken_speed
        else:
            self.centerx -= self.ai_settings.shuriken_speed
        # Анимация
        if self.cur_time - self.timer >= self.ai_settings.animation_change/2:
            self.image = pygame.image.load(
                f'images/shuriken{int(self.current_image_number) + 1}' +
                '.png').convert_alpha()
            self.timer.time = monotonic()
            self.current_image_number = not self.current_image_number
        # Действительные значения в целочисленные
        self.rect.centerx = int(self.centerx)
        # Если сюрикен за пределами экрана - удаляет его из группы ударных поверхностей
        if not self.screen_rect.colliderect(self.rect):
            en_fists.remove(self)
        