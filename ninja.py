from enemy import Enemy
import pygame
from mediator import Mediator
from settings import Settings
from MC import MainCharacter
from stats import Stats
from etimer import Timer

class Ninja(Enemy):
    '''Четвертый тип врагов - ниндзя'''

    def __init__(self, mediator: Mediator):
        super().__init__(mediator)
        # Инициализация имени для подстановки в файлы и имена переменных
        self.name = 'ninja'
        # Инициализация здоровья
        self.health = 10 * self.mediator.get_value(
            'ai_settings', 'h_multiplier')
        # Загрузка изображения
        self.image = pygame.image.load(
            f'images/K{self.surname}Enemies/ninja/standing.png').convert_alpha()
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
            'ai_settings', 'ninja_attack_speed')
        self.cooldown = self.mediator.get_value(
            'ai_settings', 'ninja_cooldown')
        # Количество кадров атаки
        self.frames = 7
        # Количество кадров, в которых ударной поверхности нет,
        # а сам кулак или что там еще находится за телом
        self.noload_fr = 0
        # Число для корректировки положения изображения и поверхности
        self.pos_correction = '0'
        # Размеры самого маленького кадра для корректировки анимации атаки
        self.smallest_frame = (pygame.image.load(
            f'images/K{self.surname}Enemies/ninja/punching1_right.png'). \
            get_rect().width, pygame.image.load(
            f'images/K{self.surname}Enemies/ninja/punching1_right.png'). \
            get_rect().height)
        # Список координат верха прямоугольника ударной поверхности
        # относительно верха прямоугольника анимаций для последних кадров
        self.frl_top = [101 for i in range(4)] # frl - fist relative location
        self.frl_side = [180 for i in range(4)]
        # Флаг для начала анимации атаки
        self.is_new_rect_created = False
        # Ниндзя метает сюрикены
        self.launch_shuriken = True
        self.is_launching = False
        self.shuriken_active = False
        self.launch_range = self.mediator.get_value(
            'ai_settings', 'ninja_launch_range')
        self.launch_cooldown = self.mediator.get_value(
            'ai_settings', 'ninja_launch_cooldown')
        

    def death_animation(self):
        '''Анимация смерти'''
        an_change = self.mediator.get_value('ai_settings', 'animation_change')
        if not self.has_played_audio:
            self.mediator.call_method('audio', 'play_sound', '"ninja_death"')
            self.has_played_audio = True
        if self.mediator.current_time() - self.timer < 5.5 * an_change:
            for i in range(11):
                if (i + 1)/2 * an_change > \
                    self.mediator.current_time() -self.timer >= \
                    i/2 * an_change:
                    self.image = pygame.image.load(
                        f'images/K{self.surname}Enemies/ninja/death{i + 1}' + 
                        '.png').convert_alpha()
                    self.change_rect()
        elif self.mediator.current_time() - self.timer >= 10.5 * an_change:
            self.kill()

    def create_new_rect(self):
        '''Создает новый прямоугольник для удобной анимации атаки'''
        if not self.is_new_rect_created:
            pos_dict = {'S': 50, 'Z' : 20}
            # Новый прямоугольник - самый маленький кадр
            fake_rect = pygame.Rect((0,0), self.smallest_frame)
            # Отличие от аналогичного метода класса Enemy - центр нового 
            # прямоугольника находится не в центре старого, а чуть дальше от него
            if self.right_punch:
                fake_rect.centerx = self.rect.centerx + pos_dict[self.surname]
            else:
                fake_rect.centerx = self.rect.centerx - pos_dict[self.surname]
            fake_rect.bottom = self.rect.bottom
            self.rect = fake_rect
            self.is_new_rect_created = True
        
