
import pygame
from enemy import Enemy
from fist import Fist
from random import randint
from enemy_animation import going_left_animation, going_right_animation

class Bull(Enemy):
    '''Класс первого типа врагов - бугаев'''

    def __init__(self, screen, ai_settings, mc, st, timer, cur_time):
        '''Инициализация параметров, начального положения и изображения'''
        super().__init__(screen, ai_settings, mc, st, timer, cur_time)
        # Инициализация имени для подстановки в файлы и имена переменных
        self.name = 'bull'
        
        # Инициализация здоровья
        self.health = 10 * self.ai_settings.h_multiplier
        # Случайное превращение в Диану
        if randint(0, ai_settings.diana_appearance_chance) == \
            ai_settings.diana_appearance_chance:
            self.surname = 'D'
        # Загрузка изображения
        self.image = pygame.image.load(
            f'images/K{self.surname}Enemies/bull/standing.png')
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
        # Уйдет ли Диана налево?
        self.leaving_left = False
        

    def define_pos_correction(self):
        if self.surname == 'S':
            self.pos_correction = '20'
        else:
            self.pos_correction = '40'



        
    
    def death_animation(self, enemies):
        '''Анимация смерти'''
        # Если враг не Диана:
        if self.surname != 'D':
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
        else:
            # Диана уходит
            self.diana_leaving(enemies)

    def diana_leaving(self, enemies):
        '''Анимация ухода Дианы'''
        if self.leaving_left:
            if self.rect.right <= self.screen_rect.left:
                del self.fist
                pygame.sprite.Group.remove(enemies, self)
            else:
                self.centerx -= self.ai_settings.bull_speed_factor
                going_left_animation(self, self.ai_settings)
                self.rect.centerx = self.centerx
        else:
            if self.rect.left >= self.screen_rect.right:
                del self.fist
                pygame.sprite.Group.remove(enemies, self)
            else:
                self.centerx += self.ai_settings.bull_speed_factor
                going_right_animation(self, self.ai_settings)
                self.rect.centerx = self.centerx