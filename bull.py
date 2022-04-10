
import pygame
from enemy import Enemy
from fist import Fist



class Bull(Enemy):
    '''Класс первого типа врагов - бугаев'''

    def __init__(self, screen, ai_settings, mc, st, timer, cur_time):
        '''Инициализация параметров, начального положения и изображения'''
        super().__init__(screen, ai_settings, mc, st, timer, cur_time)
        # Инициализация имени для подстановки в файлы и имена переменных
        self.name = 'bull'
        
        # Инициализация здоровья
        self.health = 10 * self.ai_settings.h_multiplier
        
        # Загрузка изображения
        self.image = pygame.image.load('images/KSEnemies/bull/standing.png')
        self.rect = self.image.get_rect()
        # Враг появляется с отдаленной от главного персонажа стороны экрана
        self.spawning_point()
        # Прямоугольник для анимаций
        self.an_rect = self.rect
        # Сохранение координат центра в виде вещественных чисел
        self.centerx = self.rect.centerx
        self.centery = self.rect.centery
        # Сохраняем скорость атаки и время перезарядки из настроек
        self.ats = ai_settings.bull_attack_speed
        self.cooldown = ai_settings.bull_cooldown
        # Создаем ударную поверхность
        self.fist = Fist(screen)
        # Количество кадров атаки
        self.frames = 10
        # Количество кадров, в которых ударной поверхности нет,
        # а сам кулак или что там еще находится за телом
        self.noload_fr = 2
        # Число для корректировки положения изображения и поверхности:
        self.define_pos_correction()
        # Размеры самого маленького кадра для корректировки анимации атаки
        self.smallest_frame = (77, 238)
        # Список координат верха прямоугольника ударной поверхности
        # относительно верха прямоугольника анимаций для 4 последних кадров
        self.frl_top = [16, 15, 12, 15] # frl - fist relative location
        self.frl_side = [63, 87, 104, 114]
        

    def define_pos_correction(self):
        if self.surname == 'S':
            self.pos_correction = '20'
        else:
            self.pos_correction = '40'



        
    
    def death_animation(self, enemies):
        '''Анимация смерти'''
        if self.cur_time.time - self.timer < 6 * self.ai_settings.animation_change:
            for i in range(6):
                # Появление ангельских/дьявольских атрибутов
                if (i+1) * self.ai_settings.animation_change > \
                    self.cur_time.time - self.timer >= \
                        i * self.ai_settings.animation_change:
                    self.image = pygame.image.load(
                        f'images/K{self.surname}Enemies/bull/death{i + 1}.png')
                    self.change_rect()
        else:
            # Полетели вверх, если ангел
            if self.surname == 'S':
                self.rect.centery -= 5
                if self.rect.bottom <= self.screen_rect.top:
                    pygame.sprite.Group.remove(enemies, self)
            # Полетели вниз, если дьявол
            else:
                self.rect.centery += 5
                if self.rect.top >= self.screen_rect.bottom:
                    pygame.sprite.Group.remove(enemies, self)

    