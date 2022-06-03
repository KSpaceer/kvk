


import pygame
from enemy import Enemy
from mediator import Mediator
from settings import Settings
from MC import MainCharacter
from stats import Stats
from etimer import Timer

class Guru(Enemy):
    '''Третий тип врагов (З.) - гуру'''

    def __init__(self, mediator: Mediator):
        super().__init__(mediator)
        # Инициализация имени для подстановки в файлы и имена переменных
        self.name = 'guru'
        # Название звука атаки
        self.audioname = 'ohm'
        # Инициализация здоровья
        self.health = 10 * self.mediator.get_value(
            'ai_settings', 'h_multiplier')
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
        self.ats = self.mediator.get_value(
            'ai_settings', 'guru_attack_speed')
        self.cooldown = self.mediator.get_value(
            'ai_settings', 'guru_cooldown')
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
        speed = self.mediator.get_value(
                'ai_settings', 'guru_speed_factor')
        if self.rect.centery < self.mediator.get_value('mc', 'rect').centery:
            self.centery += speed
            self.centery -= speed

    def horizontal_movement(self):
        '''Перемещение врага по горизонтали'''
        # Отличие от одноименного метода класса Enemy - отсутствие анимации
        mc_rect: pygame.Rect = self.mediator.get_value('mc', 'rect')
        speed = self.mediator.get_value(
                'ai_settings', 'guru_speed_factor')
        if self.rect.left > mc_rect.right:
            self.centerx -= speed
        elif self.rect.right < mc_rect.left:
            self.centerx += speed
        else:
            if self.rect.centerx > mc_rect.centerx:
                self.centerx += speed
            else:
                self.centerx -= speed

    def death_animation(self):
        '''Анимация смерти'''
        an_change = self.mediator.get_value('ai_settings', 'animation_change')
        if not self.has_played_audio:
            self.mediator.call_method('audio', 'play_sound', '"guru_death"')
            self.has_played_audio = True
        if self.mediator.current_time() - self.timer < \
            12 * an_change:
            for i in range(6):
                if 2 * (i + 1) * an_change > \
                    self.mediator.current_time() - self.timer >= \
                    2 * i * an_change:
                    self.image = pygame.image.load(
                        f'images/KZEnemies/guru/death{i + 1}' + 
                        '.png').convert_alpha()
                    self.change_rect()
        elif self.mediator.current_time() - self.timer >= \
            18 * an_change:
            self.kill()
