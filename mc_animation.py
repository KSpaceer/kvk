import pygame
import time

def going_right_animation(mc, ai_settings):
    '''Анимация ходьбы вправо'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if mc.cur_time.time - mc.timer >= ai_settings.animation_change:
        mc.timer = time.monotonic()
        if mc.is_right_leg:
            mc.is_right_leg = False
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_right(left_leg).png')
        else:
            mc.is_right_leg = True
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_right(right_leg).png')

def going_left_animation(mc, ai_settings):
    '''Анимация ходьбы влево'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if mc.cur_time.time - mc.timer >= ai_settings.animation_change:
        mc.timer = time.monotonic()
        if mc.is_right_leg:
            mc.is_right_leg = False
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_left(left_leg).png')
        else:
            mc.is_right_leg = True
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_left(right_leg).png')

def going_down_animation(mc, ai_settings):
    '''Анимация ходьбы вниз'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if mc.cur_time.time - mc.timer >= ai_settings.animation_change:
        mc.timer = time.monotonic()
        if mc.is_right_leg:
            mc.is_right_leg = False
            mc.image = pygame.image.load(
                    f'images/K{mc.surname}Main/going_down(left_leg).png')
        else:
            mc.is_right_leg = True
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_down(right_leg).png')

def going_up_animation(mc, ai_settings):
    '''Анимация ходьбы вверх'''
    # Сверяет разность времени монотонных часов и атрибута времени с 
    # времени смены анимации
    if mc.cur_time.time - mc.timer >= ai_settings.animation_change:
        mc.timer = time.monotonic()
        if mc.is_right_leg:
            mc.is_right_leg = False
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_up(left_leg).png')
        else:
            mc.is_right_leg = True
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/going_up(right_leg).png')

def standing_animation(mc, ai_settings):
    '''Анимация при отсутствии движения'''
    if mc.cur_time.time - mc.timer >= ai_settings.animation_change*1.5:
        mc.timer = time.monotonic()
        if mc.is_right_leg:
            mc.is_right_leg = False
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/standing.png')
        else:
            mc.is_right_leg = True
            mc.image = pygame.image.load(
                f'images/K{mc.surname}Main/standing2.png')

def stunning_animation(mc, ai_settings, file_endname, move_direction):
    '''Анимация оглушения'''
    if mc.attack_timer == 0:
        mc.image = pygame.image.load(
            f'images/K{mc.surname}Main/stunned_{file_endname}.png')
        mc.attack_timer = time.monotonic()
    elif mc.cur_time.time  - mc.attack_timer <= ai_settings.stun_duration:
        # Откидывание:
        exec(f'mc.centerx {move_direction}= ai_settings.mc_speed_factor/2')
    else:
        mc.is_stunned = False
    
    
