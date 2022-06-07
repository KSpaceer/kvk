


from random import randint
from time import monotonic
import pygame
from audiosounds import Audio
from enemy import Enemy
from enemy_animation import (going_left_animation, 
going_right_animation, going_vertical_animation)
from mediator import Mediator
from path_handling import load_image
from settings import Settings
from MC import MainCharacter
from stats import Stats
from etimer import Timer


class Eater(Enemy):
    '''Третий тип врагов (С.) - пожиратель(едок)'''

    def __init__(self, mediator: Mediator):
        '''Инициализация параметров, начального положения и изображения'''
        super().__init__(mediator)
        # Инициализация имени для подстановки в файлы и имена переменных
        self.name = 'eater'
        # Название звука атаки
        self.audioname = 'bite'
        # Инициализация здоровья
        self.health = 10 * self.mediator.get_value('ai_settings', 'h_multiplier')
        # Загрузка изображения
        self.image = load_image('KSEnemies', 'eater', 'standing.png')
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
            'ai_settings', 'eater_attack_speed')
        self.cooldown = self.mediator.get_value(
            'ai_settings', 'eater_cooldown')
        # Количество кадров атаки
        self.frames = 10
        # Количество кадров, в которых ударной поверхности нет,
        # а сам кулак или что там еще находится за телом
        self.noload_fr = 4
        # Число для корректировки положения изображения и поверхности
        self.pos_correction = '0'
        # Размеры самого маленького кадра для корректировки анимации атаки
        self.smallest_frame = (140, 180)
        # Список координат верха прямоугольника ударной поверхности
        # относительно верха прямоугольника анимаций для "ударных" кадров
        self.frl_top = [69, 69] # frl - fist relative location
        self.frl_side = [143, 154]
        # Для смерти
        self.start_dying = True # Флаг для начала смерти
        # Словарь для направлений
        self.dir_dict = {0: ('y', '-'),
                         1: ('y', '+'),
                         2: ('x', '-'),
                         3: ('x', '+')}

   
    
    def death_animation(self):
        '''Анимация смерти'''
        self.initiate_death()
        self.gotta_go_fast()
        exec(f'self.center{self.dir_dict[self.direction][0]}' +
             f'{self.dir_dict[self.direction][1]}=' +
             '5 * self.ai_settings.eater_speed_factor')
        # Если враг за пределами экрана
        if not self.rect.colliderect(self.mediator.get_value('screen_rect')):
            self.kill()

    def initiate_death(self):
        '''Определяет направление движения во время смерти'''
        if self.start_dying:
            self.direction = randint(0, 3)
            self.start_dying = False
            self.image = load_image('KSEnemies', 'eater', 'standing.png')
            self.change_rect()

    def gotta_go_fast(self):
        '''Противник быстро убегает после смерти'''
        # Выражение вида "НЕ 1 ИЛИ НЕ 2" используется
        # вместо "НЕ(1 ИЛИ 2)", т.к. в таком случае, если
        # звук не проигрывался (self.has_played_audio) будет равно False, и тогда
        # выражение под скобками: (0 ИЛИ 2). Из-за этого начнет проверяться 
        # второе выражение, что приведет к ошибке - значения с таким ключом в словаре
        # до первого проигрывания звука нет. В использующемся выражении, если
        # НЕ 1 равно True, то второе выражение проверяться уже не будет.
        audio: Audio = self.mediator.get_value('audio')
        if not self.has_played_audio or not \
            audio.sounds['eater_death'].get_num_channels():
            audio.play_sound('eater_death')
            self.has_played_audio = True
        if self.direction in (0, 1):
            going_vertical_animation(self)
        elif self.direction == 2:
            going_left_animation(self)
        elif self.direction == 3:
            going_right_animation(self)