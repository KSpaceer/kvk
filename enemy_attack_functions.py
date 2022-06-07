
import pygame
from pygame.sprite import Group
from time import monotonic
from shockwave import Shockwave
from path_handling import load_image


def define_attack_vars(enemy):
        '''Определяет значение переменных для метода атаки'''
        # Атака идет вправо или влево?
        if enemy.right_punch:
            file_end_name = 'right' # конец названия файлов кадров
            sign = '+'  # знак для уравнения определения положения первых кадров
            rect_side = 'left' # сторона, относительно которой располагаются
                               # первые кадры
        else:
            file_end_name = 'left'
            sign = '-'
            rect_side = 'right'
        return file_end_name, sign, rect_side



def attack(enemy):
    '''Обработка атаки'''
    file_end_name, sign, rect_side = define_attack_vars(enemy)
    # enemy.frames - количество кадров
    for i in range(enemy.frames):
        # Кадры сменяются по времени:
        if (i+1) * enemy.ats >= enemy.mediator.current_time() - enemy.timer >\
            i * enemy.ats:
            # Кадров (изображений именно) всего половина от общего количества, 
            # в случае нечетного кол-ва - с округлением в большую сторону
            if i in range(int(enemy.frames/2) + 1):
                working_stroke(enemy, file_end_name, sign, rect_side, i)
            else:
                idling(enemy, file_end_name, i)

def idling(enemy, file_end_name: str, i: int):
    '''Холостой ход атаки'''
    en_fists: Group = enemy.mediator.get_collection('en_fists')
    if i == round(enemy.frames/2) + 1 and\
        enemy.fist in en_fists:
        # Удаляем ударную поверхность:
        enemy.fist.change_position(-50, -50)
        en_fists.remove(enemy.fist)
        # Кадры идут в обратном порядке
    enemy.image = load_image(f'K{enemy.surname}Enemies', f'{enemy.name}', 
        f'punching{enemy.frames + 1 - i}_{file_end_name}.png')
    enemy.correlate_rect_image(enemy.right_punch)
    if i == enemy.frames - 1:
        # Атака закончена, начинается перезарядка
        enemy.is_punching = False
        enemy.shockwave_active = False
        enemy.has_played_audio = False
        enemy.cooldown_timer = monotonic()
        if hasattr(enemy, 'is_new_rect_created'):
            enemy.is_new_rect_created = False

def working_stroke(enemy, file_end_name: str, sign: str, rect_side: str, i: int):
    '''Рабочий ход атаки'''
    if i == 0:
        enemy.create_new_rect()
        enemy.mediator.extend_collection('en_fists', enemy.fist)
    enemy.image = load_image(f'K{enemy.surname}Enemies', 
        f'{enemy.name}', f'punching{i + 1}_{file_end_name}.png')                 
    if i <= enemy.noload_fr - 1:
    # Корректирует изображение на "неатакующих" кадрах, если такое предусмотрено
        if enemy.pos_correction != '0':
            enemy.correct_position(sign, rect_side)
        else:
            enemy.correlate_rect_image(enemy.right_punch)
    else:
        enemy.correlate_rect_image(enemy.right_punch)
        # Перемещает ударную поверхность:
        exec('enemy.fist.change_position(' +
            f'enemy.an_rect.{rect_side} {sign}' +
            f'enemy.frl_side[i-{enemy.noload_fr}],' +
            f'enemy.an_rect.top + enemy.frl_top[i-{enemy.noload_fr}])')
        if not enemy.has_played_audio:
            enemy.mediator.call_method(
                'audio', 'play_sound', f'"{enemy.audioname}"')
            enemy.has_played_audio = True
        shockwave_check(enemy, i)

def shockwave_check(enemy, i: int):
    '''Вызывает ударную волну, 
        если такое предусмотрено типом врага и другой волны нет'''
    if enemy.summon_shockwave and not enemy.shockwave_active \
        and i == round(enemy.frames/2):
        # Вызывает ударную волну, если такое предусмотрено типом врага
        enemy.mediator.call_method('audio', 'play_sound', '"launch_shockwave"')
        new_shockwave = Shockwave(enemy.mediator, enemy.right_punch, en_fist=enemy.fist)
        enemy.mediator.extend_collection('en_fists', new_shockwave)
        enemy.shockwave_active = True

def launch(enemy):
    '''Обработка запуска сюрикена'''
    if not enemy.shuriken_active:
        enemy.shuriken_active = True
        file_end_name = enemy.define_attack_vars()[0]
        enemy.image = load_image(f'K{enemy.surname}Enemies', 
            f'{enemy.name}', f'launching_{file_end_name}.png')
        enemy.change_rect()
        from shuriken import Shuriken
        new_shuriken = Shuriken(enemy.mediator, enemy, enemy.right_punch)
        enemy.mediator.extend_collection('en_fists',new_shuriken)
        enemy.mediator.call_method(
            'audio', 'play_sound', '"launch_shuriken"')
    if enemy.mediator.current_time() - enemy.timer >=\
        enemy.mediator.get_value('ai_settings', 'animation_change'):
        enemy.is_launching = False
        enemy.shuriken_active = False
        enemy.launch_cooldown_timer = monotonic()