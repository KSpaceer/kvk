import pygame

from enemy import Enemy
from mediator import Mediator
from settings import Settings
from MC import MainCharacter
from stats import Stats
from etimer import Timer

class Sumo(Enemy):
    '''Класс второго типа врагов - сумоистов'''

    def __init__(self, mediator: Mediator):
        '''Инициализация параметров, начального положения и изображения'''
        super().__init__(mediator)
        # Инициализация имени для подстановки в файлы и имена переменных
        self.name = 'sumo'
        # Инициализация здоровья
        self.health = 15 * self.mediator.get_value(
            'ai_settings', 'h_multiplier')
        # Загрузка изображения
        self.image = pygame.image.load(
            f'images/K{self.surname}Enemies/sumo/standing.png').convert_alpha()
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
            'ai_settings', 'sumo_attack_speed')
        self.cooldown = self.mediator.get_value(
            'ai_settings', 'sumo_cooldown')
        # Дальность атаки
        self.attack_range = self.mediator.get_value(
            'ai_settings', 'sumo_attack_range')
        # Сумоист во время атаки вызывает ударную волну, причем только одну
        self.summon_shockwave = True
        self.shockwave_active = False
        # Количество кадров атаки
        self.frames = 9
        # Количество кадров, в которых ударной поверхности нет,
        # а сам кулак или что там еще находится за телом
        self.noload_fr = 2
        # Число для корректировки положения изображения и поверхности
        self.pos_correction = '0'
        # Размеры самого маленького кадра для корректировки анимации атаки
        self.smallest_frame = (87, 220)
        # Список координат верха прямоугольника ударной поверхности
        # относительно верха прямоугольника анимаций для последних кадров
        self.frl_top = [94, 109, 119] # frl - fist relative location
        self.frl_side = [31, 83, 123]



    def death_animation(self):
        '''Анимация смерти'''
        an_change = self.mediator.get_value('ai_settings', 'animation_change')
        if not self.has_played_audio:
            self.mediator.call_method('audio', 'play_sound', '"sumo_death"')
            self.has_played_audio = True
        if self.mediator.current_time() - self.timer < 9 * an_change:
            for i in range(9):
                # Путь самурая - смерть
                if (i + 1) * an_change > \
                    self.mediator.current_time() - self.timer >= \
                        i * an_change:
                    self.image = pygame.image.load(
                        f'images/K{self.surname}Enemies/sumo/death{i + 1}' +
                        '.png').convert_alpha()
                    self.change_rect_sumo()
        elif self.mediator.current_time() - self.timer > 18 * an_change:
            self.kill()

    def change_rect_sumo(self):
        '''Заменяет прямоугольник в анимации смерти сумоиста'''
        left = self.rect.left
        bottom = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.bottom = bottom