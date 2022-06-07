
import pygame
from enemy import Enemy
from random import randint
from enemy_animation import going_left_animation, going_right_animation
from mediator import Mediator
from path_handling import load_image

class Bull(Enemy):
    '''Класс первого типа врагов - бугаев'''

    def __init__(self, mediator: Mediator, is_native: bool = True):
        '''Инициализация параметров, начального положения и изображения'''
        super().__init__(mediator, is_native)
        # Инициализация имени для подстановки в файлы и имена переменных
        self.name = 'bull'
        # Инициализация здоровья
        self.health = 10 * self.mediator.get_value('ai_settings', 'h_multiplier')
        # Случайное превращение в Диану
        diana_appearance_chance = self.mediator.get_value(
            'ai_settings', 'diana_appearance_chance')
        if randint(0, diana_appearance_chance) == diana_appearance_chance:
            self.surname = 'D'
        # Загрузка изображения
        self.image = load_image(f'K{self.surname}Enemies', 'bull', 'standing.png')
        self.rect = self.image.get_rect()
        # Враг появляется с отдаленной от главного персонажа стороны экрана
        self.spawning_point()
        # Прямоугольник для анимаций
        self.an_rect = self.rect
        # Сохранение координат центра в виде вещественных чисел
        self.centerx = self.rect.centerx
        self.centery = self.rect.centery
        # Сохраняем скорость атаки и время перезарядки из настроек
        self.ats = self.mediator.get_value('ai_settings', 'bull_attack_speed')
        self.cooldown = self.mediator.get_value('ai_settings', 'bull_cooldown')
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
        # Уйдет ли Диана в левую сторону?
        self.leaving_left = False
        

    def define_pos_correction(self):
        '''Определяет корректировку положения изображения'''
        if self.surname == 'S':
            self.pos_correction = '20'
        else:
            self.pos_correction = '40'



        
    
    def death_animation(self):
        '''Анимация смерти'''
        screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
        # Если враг не Диана:
        if self.surname != 'D':
            if not self.has_played_audio:
                self.mediator.call_method(
                    'audio', 'play_sound', f'"bull{self.surname}_death"')
                self.has_played_audio = True
            animation_change = self.mediator.get_value('ai_settings', 'animation_change')
            if self.mediator.current_time() - self.timer < 6 * animation_change:
                for i in range(6):
                    # Появление ангельских/дьявольских атрибутов
                    if (i+1) * animation_change > \
                        self.mediator.current_time() - self.timer >= \
                            i * animation_change:
                        self.image = load_image(f'K{self.surname}Enemies', 
                            'bull', f'death{i + 1}.png')
                        self.change_rect()
            else:
                # Полетели вверх, если ангел
                if self.surname == 'S':
                    self.rect.centery -= 5
                    if self.rect.bottom <= screen_rect.top:
                        self.kill()
                # Полетели вниз, если дьявол
                else:
                    self.rect.centery += 5
                    if self.rect.top >= screen_rect.bottom:
                        self.kill()
        else:
            # Диана уходит
            self.diana_leaving(screen_rect)

    def diana_leaving(self, screen_rect: pygame.Rect):
        '''Анимация ухода Дианы'''
        speed = self.mediator.get_value('ai_settings', 'bull_speed_factor')
        if self.leaving_left:
            # Уходит направо
            if self.rect.right <= screen_rect.left:
                del self.fist
                self.kill()
            else:
                self.centerx -= speed
                going_left_animation(self)
                self.rect.centerx = self.centerx
        else:
            # Уходит налево
            if self.rect.left >= screen_rect.right:
                del self.fist
                self.kill()
            else:
                self.centerx += speed
                going_right_animation(self)
                self.rect.centerx = self.centerx