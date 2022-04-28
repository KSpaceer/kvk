import pygame
from time import monotonic



def going_vertical_animation(enemy):
    '''Анимация вертикального перемещения'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if enemy.cur_time - enemy.timer >= \
        enemy.ai_settings.animation_change/2:
        enemy.timer = monotonic()
        if enemy.is_right_leg:
            enemy.is_right_leg = False
            enemy.image = pygame.image.load(
                    f'images/K{enemy.surname}Enemies/{enemy.name}' + 
                    '/going_vertical(left_leg).png').convert_alpha()
            enemy.change_rect()
        else:
            enemy.is_right_leg = True
            enemy.image = pygame.image.load(
                f'images/K{enemy.surname}Enemies/{enemy.name}' +
                '/going_vertical(right_leg).png').convert_alpha()
            enemy.change_rect()

def going_right_animation(enemy):
    '''Анимация ходьбы вправо'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if enemy.cur_time - enemy.timer >= \
        enemy.ai_settings.animation_change:
        enemy.timer = monotonic()
        if enemy.is_right_leg:
            enemy.is_right_leg = False
            enemy.image = pygame.image.load(
                f'images/K{enemy.surname}Enemies/{enemy.name}' +
                '/going_right(left_leg).png').convert_alpha()
            enemy.change_rect()
        else:
            enemy.is_right_leg = True
            enemy.image = pygame.image.load(
                f'images/K{enemy.surname}Enemies/{enemy.name}' +
                '/going_right(right_leg).png').convert_alpha()
            enemy.change_rect()

def going_left_animation(enemy):
    '''Анимация ходьбы влево'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if enemy.cur_time - enemy.timer >= \
        enemy.ai_settings.animation_change:
        enemy.timer = monotonic()
        if enemy.is_right_leg:
            enemy.is_right_leg = False
            enemy.image = pygame.image.load(
                f'images/K{enemy.surname}Enemies/{enemy.name}' +
                '/going_left(left_leg).png').convert_alpha()
            enemy.change_rect()
        else:
            enemy.is_right_leg = True
            enemy.image = pygame.image.load(
                f'images/K{enemy.surname}Enemies/{enemy.name}' +
                '/going_left(right_leg).png').convert_alpha()
            enemy.change_rect()

def stunning_animation(enemy):
    '''Анимация оглушения'''
    for i in range(8):
        if (i+1) * (enemy.ai_settings.animation_change/2) > \
            enemy.cur_time - enemy.timer >= i * (
            enemy.ai_settings.animation_change/2):
            # Происходит шатание:
            if i % 2 == 0:
                enemy.rect.centerx = enemy.centerx - 5
            else:
                enemy.rect.centerx = enemy.centerx + 5
            if i == 7:
                enemy.is_stunned = False # Оглушение закончено