from time import monotonic
import pygame
from pygame.sprite import Sprite

class Enemy(Sprite):

    '''Класс игровых врагов'''

    deaths = 0 # Кол-во смертей врагов
    c_deaths = 0 # Текущие смерти, нужны для волн и уровней
    summons = 0 # Кол-во призывов врагов

    def __init__(self, screen, ai_settings, mc, st, timer, cur_time):
        '''Инициализирует параметры'''
        super().__init__()
        Enemy.summons += 1
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.ai_settings = ai_settings
        self.mc = mc
        self.st = st
        self.main_timer = timer # Таймер из основного модуля
        self.image = ''
        # Текущее время
        self.cur_time = cur_time
        # Переменные для анимаций
        self.timer = monotonic()
        self.is_right_leg = True
        self.is_dead = False
        # Флаг оглушения после получения урона
        self.is_stunned = False
        # Флаги удара
        self.is_punching = False
        self.right_punch = False
        # Таймер для перезарядки атаки
        self.cooldown_timer = 0

    def __del__(self):
        '''Срабатывает при смерти'''
        Enemy.deaths += 1
        Enemy.c_deaths += 1
        # Если вся волна умерла:
        if Enemy.c_deaths == len(self.ai_settings.waves[self.st.level]
        [self.st.current_wave]):
            # Переход на новый уровень, если волна последняя
            if self.st.current_wave == len(
                self.ai_settings.waves[self.st.level]) - 1 and \
                    self.st.level < self.ai_settings.max_level:
                self.st.level += 1
                self.st.current_wave = 0
            # Либо вызов новой волны
            elif self.st.current_wave < len(
                self.ai_settings.waves[self.st.level]) - 1:
                self.st.current_wave += 1
            # Текущие смерти и призывы обнуляются
            Enemy.c_deaths = 0
            Enemy.summons = 0
            # Таймер тоже
            self.main_timer.time = monotonic()
        
        

    def blitme(self):
        '''Рисует врага в текущей позиции'''
        if not self.is_punching:
            self.screen.blit(self.image, self.rect)
        else:
            self.screen.blit(self.image, self.an_rect)

    def change_rect(self):
        '''Заменяет прямоугольник врага, центр нового находится в центре старого'''
        self.rect = self.image.get_rect()
        self.rect.centerx = int(self.centerx)
        self.rect.centery = int(self.centery)

    def spawning_point(self):
        '''Определяет начальное положение врага'''
        
        self.rect.centery = self.screen_rect.centery
        if self.mc.centerx > self.ai_settings.screen_width/2:
            self.rect.right = 0
        elif self.mc.centerx <= self.ai_settings.screen_width/2:
            self.rect.left = self.ai_settings.screen_width
    
    
        