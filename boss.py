

from random import randint
from time import monotonic
import pygame
import boss_ultimates as bu
import boss_common_attacks as bac
import enemy_animation as an
from enemy import Enemy
from fist import Fist
from MC import MainCharacter
from mediator import Mediator
from path_handling import load_image
from stats import Stats
from audiosounds import Audio



class Boss(Enemy):
    '''Пятый тип врагов - босс'''

    def __init__(self, mediator: Mediator):
        super().__init__(mediator)
        self.mediator = mediator
        # Повышение скорости главного персонажа
        new_mc_speed = self.mediator.get_value('mc', 'speed') * 2
        self.mediator.set_value('mc', 'speed', f'{new_mc_speed}')
        # Скорость босса
        self.speed = self.mediator.get_value('ai_settings', 'boss_speed_factor')
        # Инициализация имени для подстановки в файлы и имена переменных
        self.name = 'boss'
        # Инициализация здоровья и панели здоровья
        self.health = self.mediator.get_value('ai_settings', 'boss_health')
        from graphic import BossHealth
        self.healthbar = BossHealth(self)
        # Загрузка изображения
        self.image = load_image(f'K{self.surname}Enemies', 'boss', 'standing.png')
        # Руки на картинке не учитываются, поэтому основной прямоугольник
        # задаем сами 
        self.rect = pygame.Rect(-500, -500, 110, 414)
        # Враг появляется сверху
        self.spawning_point()
        # Сохранение координат центра в виде вещественных чисел
        self.centerx = float(self.rect.centerx)
        self.centery = float(self.rect.centery)
        # Сохраняем скорость атаки и время перезарядки из настроек
        self.ats = self.mediator.get_value('ai_settings', 'boss_attack_speed')
        self.cooldown = self.mediator.get_value('ai_settings', 'boss_cooldown')
        self.ultimate_cooldown = self.mediator.get_value(
            'ai_settings', 'boss_ultimate_cooldown')
        # Флаг неуязвимости (босса нельзя оглушить, поэтому он получает неуязвимость на время)
        # Т.к. он может делать другие действия во время неуязвимости, 
        # использовать обычный таймер (Enemy.timer) нельзя - он используется
        # для этих действий. Для отслеживания неуязвимости добавим новый таймер
        self.is_invincible = False
        self.invin_timer = 0
        # Таймер перезарядки для ультимативной атаки
        # (изначально на середине перезарядки)
        self.ultimate_cooldown_timer = monotonic() - self.ultimate_cooldown/2
        # Таймер перезарядки обычной атаки изначально на середине перезарядки
        self.cooldown_timer = monotonic() - self.cooldown/2
        # Номер ультимативной и обычной способности
        self.ultimate_number = None
        self.common_attack_number = None
        # Флаги применения обычной и ультимативной атак
        self.using_common_attack = False
        self.using_ultimate = False
        # Иногда врагу нужно переместиться на позицию, чтобы
        # начать применение способности. Следующий флаг
        # отслеживает то, выбрана ли нужная позиция
        self.position_is_chosen = False
        # Флаг отслеживания того, что враг на позиции
        self.in_position = False
        # Координаты позиции
        self.positionx = None
        self.positiony = None
        # Определяем количество кадров для различных атак
        self.define_attack_frames()
        # Запуск музыки
        self.mediator.set_value('audio', 'current_music', f'"boss{self.surname}"')
        Stats.state_to_audio[Stats.GAMEACTIVE] = f'boss{self.surname}'
        # Определяем то, какие атаки будут у босса
        self.define_attacks()

    def __del__(self):
        audio: Audio = self.mediator.get_value('audio')
        if 'spinning' in audio.sounds.keys():
            audio.sounds.pop('spinning')
        new_mc_speed = self.mediator.get_value('mc', 'speed')
        self.mediator.set_value('mc', 'speed', f'{new_mc_speed}')
        return super().__del__()
    
    def spawning_point(self):
        '''Определяет начальное положение врага'''
        self.rect.centerx = self.mediator.get_value('screen_rect', 'centerx')
        self.rect.centery = -int(self.rect.width/2)
        self.change_rect()

    def define_attack_frames(self):
        '''Определяет количество кадров в атаках'''
        self.ultimate_frames = 6
        if self.surname == 'S':
            self.common_attack_frames = 7
        else:
            self.common_attack_frames = 2

    def define_attacks(self):
        '''Определяет ультимативные и обычные атаки босса'''
        if self.surname == 'S':
            self.first_ultimate = bu.summon_enemies
            self.second_ultimate = bu.launch_lightnings
            self.third_ultimate = bu.blade_runner
            self.first_common_attack = bac.chasing_tornado
            self.second_common_attack = bac.pulling_spin
        else:
            self.first_ultimate = bu.summon_enemies
            self.second_ultimate = bu.launch_spears
            self.third_ultimate = bu.saw_runner
            self.first_common_attack = bac.create_crack
            self.second_common_attack = bac.shockwave_barrage

    @staticmethod
    def lava_blit_decorator(method):
        '''Декоратор для прорисовки лавы во время смерти'''
        def wrapper(self, *args, **kwargs):
            if self.is_dead:
                self.mediator.blit_surface(self.backlava, self.bl_rect)
            method(self, *args, **kwargs)
            if self.is_dead:
                self.mediator.blit_surface(self.frontlava, self.fl_rect)
        return wrapper
    
    @lava_blit_decorator.__func__
    def blitme(self):
        '''Рисует врага в текущей позиции'''
        self.mediator.blit_surface(self.image, self.an_rect)
        self.additional_draw()

    def change_rect(self):
        '''Заменяет прямоугольник анимаций.
        Низ и центр по Х совпадает с соответствующими хар-ками основного
        прямоугольника.'''
        self.an_rect = self.image.get_rect()
        self.an_rect.bottom = self.rect.bottom
        self.an_rect.centerx = self.rect.centerx

    def update(self):
        '''Обновление состояния врага(перемещение, атаки или смерть)'''
        # Если враг жив
        if self.health > 0:
            self.damage_invin_processing()
            if not self.is_punching:
                screen_rect: pygame.Rect = self.mediator.get_value('screen_rect')
                # Функция движения находится в условии, т.к. если
                # босс на нужном месте, то должна проигрываться какая-то анимация;
                # в данном случае это анимация вертикального движения.
                if self.movement(screen_rect.centerx, 
                    screen_rect.centery):
                    an.going_vertical_animation(self)
                
                # Если нет перезарядки, применяет ультимативную атаку
                if self.mediator.current_time() - self.ultimate_cooldown_timer \
                    >= self.ultimate_cooldown:
                    self.initiate_ultimate()
                    return
                # Если нет перезарядки, применяет обычную атаку
                elif self.mediator.current_time() - self.cooldown_timer >= \
                    self.cooldown:
                    self.initiate_common_attack()
                    return
            else:
                if self.using_ultimate:
                    self.ultimate()
                else:
                    self.common_attack()
        else:    
            self.death_animation()
        self.blitme()

        
    def movement(self, x, y, multiplier: int = 1) -> bool:
        '''Перемещение босса. 
        Возвращает bool, соответствующий нахождению босса в нужном месте'''
        where_am_i_x, where_am_i_y = self.check_position(x, y) 
            # Сначала идет перемещение по вертикали
        if not where_am_i_y:
            self.vertical_movement(y)
                # Затем по горизонтали
        elif not where_am_i_x:
            self.horizontal_movement(x, multiplier)
        # Для использования в условии
        return where_am_i_x and where_am_i_y

    @staticmethod
    def zubkov_third_ultimate_decorator(method):
        '''
        Декоратор для функции обработки неуязвимости,
        поскольку во время третьей ультимативной атаки 
        Зубкова неуязвимость не должна
        спадать.
        '''
        def wrapper(self, *args, **kwargs):
            a = bool(self.using_ultimate)
            b = bool(self.ultimate_number == 2)
            c = bool(self.surname == 'Z')
            if not (a and b and c):
                method(self, *args, **kwargs)
            else:
                
                return None
        return wrapper

    
    
    @zubkov_third_ultimate_decorator.__func__
    def damage_invin_processing(self):
        '''Обработка получения урона и неуязвимости'''
        # Если босс не неуязвим и в него попал кулак главного персонажа, он получает урон
        mc_fist: Fist = self.mediator.get_value('mc_fist')
        if not self.is_invincible and self.rect.colliderect(mc_fist.rect):
            self.get_damage()
        # Если босс неуязвим и уже прошло время его неуязвимости, он ее теряет
        elif self.is_invincible and self.mediator.current_time() - self.invin_timer \
                >= self.mediator.get_value(
                'ai_settings', 'boss_invincibility_duration'):
                    self.is_invincible = False
                


    def get_damage(self):
        '''Получение урона'''
        self.health -= self.mediator.get_value('ai_settings', 'mc_damage')
        self.is_invincible = True
        self.mediator.call_method('audio', 'play_sound', '"punch"')
        self.invin_timer = monotonic()

    def check_position(self, x: int, y: int) -> tuple[bool, bool]:
        '''Определяет то, находится ли босс в нужном положении. 
        Возвращает два флага для координат.'''
        where_am_i_x = self.rect.centerx in range(x - 10, x + 10)
        where_am_i_y = self.rect.centery in range(y - 10, y + 10)
        return where_am_i_x, where_am_i_y

    def vertical_movement(self, y: int):
        '''Перемещение босса по вертикали'''
        an.going_vertical_animation(self)
        if self.rect.centery < y:
            self.centery += self.speed
        else:
            self.centery -= self.speed
        # Конвертируем вещественное значение в целочисленное
        self.rect.centery = int(self.centery)

    def horizontal_movement(self, x: int, multiplier: int = 1):
        '''Перемещение босса по горизонтали'''
        if self.rect.centerx > x:
            an.going_left_animation(self)
            self.centerx -= self.speed * multiplier
        else:
            an.going_right_animation(self)
            self.centerx += self.speed * multiplier
        # Конвертируем вещественное значение в целочисленное
        self.rect.centerx = int(self.centerx)

    def initiate_ultimate(self):
        '''Начинает применение ультимативной атаки'''
        self.using_ultimate = True
        self.is_punching = True
        self.ultimate_number = randint(0, 2)

    def initiate_common_attack(self):
        '''Начинает применение обычной атаки'''
        self.using_common_attack = True
        self.is_punching = True
        self.common_attack_number = randint(0, 1)

    def ultimate(self):
        '''Применение ультимативной атаки'''
        if self.ultimate_number == 0:
            self.first_ultimate(self)
        elif self.ultimate_number == 1:
            self.second_ultimate(self)
        else:
            self.third_ultimate(self)

    def common_attack(self):
        '''Применение обычной атаки'''
        # Не перепутать: тут сначала идет номер 1, потом номер 0
        if self.common_attack_number:
            self.first_common_attack(self)
        else:
            self.second_common_attack(self)

    def deal_nonstunning_damage(self, mc: MainCharacter):
        '''Наносит главному персонажу урон, не оглушая его'''
        mc.health -= 1
        mc.invincible = True
        mc.invin_timer = monotonic()
        mc.attack_timer = 0
    

    def additional_draw(self):
        '''Отображение дополнительных элементов на экране'''
        if hasattr(self, 'target_surface'):
            self.mediator.blit_surface(self.target_surface, self.target_rect)
        if hasattr(self, 'healthbar'):
            self.healthbar.blitme()


    def define_position(self, x, y):
        '''Определяет позицию, выбранную для проведения атаки'''
        self.positionx = x
        self.positiony = y
        self.position_is_chosen = True 

    def death_animation(self):
        '''Анимация смерти босса'''
        if not self.is_dead:
            self.mediator.call_method('audio', 'stop_music')
            self.mediator.call_method('audio', 'play_sound', '"boss_death"')
            self.is_dead = True
            self.timer = monotonic()
            self.image = load_image(f'K{self.surname}Enemies', 'boss', 'death.png')
            self.change_rect()
            self.frontlava = load_image('front_lava.png')
            self.backlava = load_image('back_lava.png')
            # fl - frontlava, bl - backlava
            self.fl_rect = self.frontlava.get_rect()
            self.bl_rect = self.backlava.get_rect()
            self.fl_rect.centerx = self.bl_rect.centerx = self.an_rect.centerx
            self.bl_rect.centery = self.an_rect.bottom
            self.fl_rect.bottom = self.bl_rect.bottom
        self.image = self.image.subsurface(
            pygame.Rect(0, 0, self.an_rect.width, self.an_rect.height - 1))
        self.an_rect = self.image.get_rect()
        if not self.an_rect.height:
            self.kill()
            # Необходимо удалить ссылку на панель здоровья, чтобы она и босс не ссылались друг на друга
            # и не было никаких ссылок на босса
            del self.healthbar
            return
        self.an_rect.centerx = self.bl_rect.centerx
        self.an_rect.bottom = self.bl_rect.centery


        
        
            


    

        