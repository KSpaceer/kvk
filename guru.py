


import pygame
from enemy import Enemy
from settings import Settings
from MC import MainCharacter
from stats import Stats
from etimer import Timer

class Guru(Enemy):
    '''Третий тип врагов (З.) - гуру'''

    def __init__(self, screen: pygame.Surface, ai_settings: Settings, 
        mc: MainCharacter, st: Stats, timer: Timer, cur_time: Timer):
        super().__init__(screen, ai_settings, mc, st, timer, cur_time)
        # Инициализация имени для подстановки в файлы и имена переменных
        self.name = 'guru'
        # Название звука атаки
        self.audioname = 'ohm'
        # Инициализация здоровья
        self.health = 10 * self.ai_settings.h_multiplier
        # Загрузка изображения
        self.image = pygame.image.load(
            'images/KZEnemies/guru/standing.png').convert_alpha()
        self.rect = self.image.get_rect()
        # Враг появляется с отдаленной от главного персонажа стороны экрана
        self.spawning_point()
        # Прямоугольник для анимаций
        self.an_rect = self.rect
        # Сохранение координат центра в виде вещественных чисел
        self.centerx = self.rect.centerx
        self.centery = self.rect.centery
        # Сохраняем скорость атаки и время перезарядки из настроек
        self.ats = self.ai_settings.guru_attack_speed
        self.cooldown = self.ai_settings.guru_cooldown
        # Количество кадров атаки
        self.frames = 9
        # Количество кадров, в которых ударной поверхности нет,
        # а сам кулак или что там еще находится за телом
        self.noload_fr = 4
        # Число для корректировки положения изображения и поверхности
        self.pos_correction = '0'
        # Размеры самого маленького кадра для корректировки анимации атаки
        self.smallest_frame = (138, 140)
        # Список координат верха прямоугольника ударной поверхности
        # относительно верха прямоугольника анимаций для "ударных" кадров
        self.frl_top = [13,] # frl - fist relative location
        self.frl_side = [152,]


    def vertical_movement(self):
        '''Перемещение врага по вертикали'''
       # Отличие от одноименного метода класса Enemy - отсутствие анимации
        self.image = pygame.image.load(
            'images/KZEnemies/guru/standing.png').convert_alpha()
        self.change_rect()
        if self.rect.centery < self.mc.rect.centery:
            self.centery += self.ai_settings.guru_speed_factor
        else:
            self.centery -= self.ai_settings.guru_speed_factor

    def horizontal_movement(self):
        '''Перемещение врага по горизонтали'''
        # Отличие от одноименного метода класса Enemy - отсутствие анимации
        if self.rect.left > self.mc.rect.right:
            self.centerx -= self.ai_settings.guru_speed_factor
        elif self.rect.right < self.mc.rect.left:
            self.centerx += self.ai_settings.guru_speed_factor
        else:
            if self.rect.centerx > self.mc.rect.centerx:
                self.centerx += self.ai_settings.guru_speed_factor
            else:
                self.centerx -= self.ai_settings.guru_speed_factor

    def death_animation(self, enemies: pygame.sprite.Group):
        '''Анимация смерти'''
        if not self.has_played_audio:
            self.audio.play_sound('guru_death')
            self.has_played_audio = True
        if self.cur_time - self.timer < \
            12 * self.ai_settings.animation_change:
            for i in range(6):
                if 2 * (i + 1) * self.ai_settings.animation_change > \
                    self.cur_time - self.timer >= \
                    2 * i * self.ai_settings.animation_change:
                    self.image = pygame.image.load(
                        f'images/KZEnemies/guru/death{i + 1}' + 
                        '.png').convert_alpha()
                    self.change_rect()
        elif self.cur_time - self.timer >= \
            18 * self.ai_settings.animation_change:
            enemies.remove(self)
